from multiprocessing import Process
import os, configparser, \
    _1_vcwg_ep_coordination as coordination, \
    _2_ep_time_step_handler as time_step_handlers

def read_ini(config_file_name):
    global config
    config = configparser.ConfigParser()
    project_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(project_path, 'A_prepost_processing', '_configs', config_file_name)
    config.read(config_path)

def run_ep_api(sensitivity_file_name,_config=None, _value=None):
    coordination.ini_all(sensitivity_file_name,_config, _value)
    state = coordination.ep_api.state_manager.new_state()
    coordination.psychrometric=coordination.ep_api.functional.psychrometrics(state)
    coordination.ep_api.runtime.callback_begin_zone_timestep_before_set_current_weather(state,
                                                                                        time_step_handlers.overwrite_ep_weather)
    if 'MediumOffice' in coordination.bld_type:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.MediumOffice_get_ep_results)
    elif '20Stories' in coordination.bld_type or 'SimplifiedHighBld' in coordination.bld_type:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers._20Stories_get_ep_results)
    else:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.general_get_ep_results)

    coordination.ep_api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Speed", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Direction", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Drybulb Temperature", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Humidity Ratio", "ENVIRONMENT")

    idfFileName = coordination.config['Bypass']['idfFileName']
    epwFileName = coordination.config['Bypass']['epwFileName']
    output_path = coordination.ep_trivial_path
    weather_file_path = os.path.join('.\\resources\\epw', epwFileName)
    idffolder = coordination.config['Bypass']['idfFolder']
    idfFilePath = os.path.join(f'.\\resources\\idf{idffolder}', idfFileName)
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    coordination.ep_api.runtime.run_energyplus(state, sys_args)

def one_ini(sensitivity_file_name):
    read_ini(sensitivity_file_name)
    value_list = [i for i in config['Bypass']['value_list'].split(',')]
    this_ini_process = []
    nbr_of_parallel = 2
    batch_value_list = [value_list[i:i + nbr_of_parallel] for i in range(0, len(value_list), nbr_of_parallel)]
    for batch_nbr, batch_value in enumerate(batch_value_list):
        for value in batch_value:
            # ByPass.run_ep_api(sensitivity_file_name,config, value)
            this_ini_process.append(Process(target=run_ep_api, args=(sensitivity_file_name,config, value)))
    for i in range(0, len(this_ini_process), nbr_of_parallel):
        for process in this_ini_process[i:i + nbr_of_parallel]:
            process.start()
        for process in this_ini_process[i:i + nbr_of_parallel]:
            process.join()


if __name__ == '__main__':

    jobs = [
        "Chicago_HighOffice_Vector_Detailed.ini",
        # "Chicago_HighOffice_Vector_Simplified.ini",
        # "Chicago_MedOffice_Vector_Detailed.ini",
    ]
    for job in jobs:
        one_ini(job)