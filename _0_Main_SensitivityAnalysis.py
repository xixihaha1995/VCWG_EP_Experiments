import os, configparser
import _1_vcwg_ep_coordination as coordination
import _2_ep_time_step_handler as time_step_handlers
from VCWG_Hydrology import VCWG_Hydro
from multiprocessing import Process

def run_ep_api(sensitivity_file_name, config, ctl_viriable_1, value_1,
               ctl_viriable_2=None, value_2=None, ctl_viriable_3=None, value_3=None):

    coordination.ini_all(sensitivity_file_name, config, ctl_viriable_1, value_1,
                         ctl_viriable_2, value_2, ctl_viriable_3, value_3)
    state = coordination.ep_api.state_manager.new_state()
    coordination.psychrometric=coordination.ep_api.functional.psychrometrics(state)
    coordination.ep_api.runtime.callback_begin_zone_timestep_before_set_current_weather(state,
                                                                                        time_step_handlers.overwrite_ep_weather)
    if 'MediumOffice' in coordination.bld_type or 'Detailed_MedOffice' in coordination.bld_type:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.MediumOffice_get_ep_results)
    elif 'ShoeBox_MedOffice' in coordination.bld_type:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.ShoeBox_MedOffice_get_ep_results)
    elif 'Simplified_MedOffice' in coordination.bld_type:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.Simplified_MedOffice_get_ep_results)
    elif 'HighOffice' in coordination.bld_type:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers._20Stories_get_ep_results)

    coordination.ep_api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Speed", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Direction", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Drybulb Temperature", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Humidity Ratio", "ENVIRONMENT")

    idfFileName = str(value_1) + '_' + coordination.config['Bypass']['idfFileName']
    epwFileName = coordination.config['Bypass']['epwFileName']
    output_path = coordination.ep_trivial_path
    weather_file_path = os.path.join('.\\resources\\epw', epwFileName)
    idffolder = coordination.config['Bypass']['idfFolder']
    idfFilePath = os.path.join(f'.\\resources\\idf{idffolder}', idfFileName)
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    coordination.ep_api.runtime.run_energyplus(state, sys_args)

def run_vcwg(sensitivity_file_name,config, ctl_viriable_1, value_1,
               ctl_viriable_2=None, value_2=None, ctl_viriable_3=None, value_3=None):
    coordination.ini_all(sensitivity_file_name, config, ctl_viriable_1, value_1,
                         ctl_viriable_2, value_2, ctl_viriable_3, value_3)
    state = coordination.ep_api.state_manager.new_state()
    coordination.psychrometric=coordination.ep_api.functional.psychrometrics(state)
    if 'None' in coordination.config['Bypass']['TopForcingFileName']:
        TopForcingFileName = None
        epwFileName = coordination.config['Bypass']['epwFileName']
    else:
        epwFileName = None
        TopForcingFileName = coordination.config['Bypass']['TopForcingFileName']
    VCWGParamFileName = coordination.config['Bypass']['VCWGParamFileName']
    ViewFactorFileName = f'{coordination.csv_file_name}_ViewFactor.txt'
    # Initialize the UWG object and run the simulation
    case = f'{coordination.csv_file_name}'
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()


def read_ini(config_file_name):
    global config
    config = configparser.ConfigParser()
    project_path = os.path.dirname(os.path.abspath(__file__))
    if 'MedOffice' in config_file_name:
        config_path = os.path.join(project_path, 'A_prepost_processing','_configs','MedOffice',config_file_name)
    elif 'HighOffice' in config_file_name:
        config_path = os.path.join(project_path, 'A_prepost_processing','_configs','HighOffice',config_file_name)
    # config_path = os.path.join(project_path, 'A_prepost_processing','_configs','Only_VCWG',config_file_name)
    config.read(config_path)

def one_control_variable(sensitivity_file_name):
    ctl_viriable_1 = config['Bypass']['control_variable_1']
    ctl_values_1 = [i for i in config['Bypass']['control_values_1'].split(',')]
    framework = config['Bypass']['framework']
    this_ini_process = []
    nbr_of_parallel = 3
    batch_value_list = [ctl_values_1[i:i + nbr_of_parallel] for i in range(0, len(ctl_values_1), nbr_of_parallel)]
    for batch_nbr, batch_value in enumerate(batch_value_list):
        for value in batch_value:
            if 'OnlyVCWG' in framework:
                this_ini_process.append(
                    Process(target=run_vcwg, args=(sensitivity_file_name, config, ctl_viriable_1, value)))
            else:
                # ByPass.run_ep_api(sensitivity_file_name,config, ctl_viriable_1, value)
                this_ini_process.append(
                    Process(target=run_ep_api, args=(sensitivity_file_name, config, ctl_viriable_1, value)))
    for p in this_ini_process:
        p.start()
    for p in this_ini_process:
        p.join()

def one_ini(sensitivity_file_name):
    read_ini(sensitivity_file_name)
    one_control_variable(sensitivity_file_name)


if __name__ == '__main__':
    # one_ini('Chicago_MedOffice_MixedVariable.ini')
    # one_ini('Chicago_MedOffice_MixedVariable_OnlyVCWG.ini')
    # one_ini('Chicago_MedOffice_IDFComplexity.ini')
    # one_ini('Chicago_MedOffice_IDFComplexity_OnlyVCWG.ini')
    todo_jobs = [
        'Chicago_MedOffice_IDFComplexity.ini',
        # 'Chicago_HighOffice_IDFComplexity.ini',
    ]
    for job in todo_jobs:
        one_ini(job)