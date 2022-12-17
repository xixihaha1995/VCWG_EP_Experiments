
import os, numpy as np, pandas as pd
from threading import Thread
from multiprocessing import Process
import _0_vcwg_ep_coordination as coordination
import _1_ep_time_step_handler as time_step_handlers
from VCWG_Hydrology import VCWG_Hydro
# sensitivity_file_name,config, ctl_viriable_1, value
def run_ep_api(sensitivity_file_name, config, ctl_viriable_1, value_1,
               ctl_viriable_2=None, value_2=None, ctl_viriable_3=None, value_3=None):

    coordination.ini_all(sensitivity_file_name, config, ctl_viriable_1, value_1,
                         ctl_viriable_2, value_2, ctl_viriable_3, value_3)
    state = coordination.ep_api.state_manager.new_state()
    coordination.psychrometric=coordination.ep_api.functional.psychrometrics(state)
    coordination.ep_api.runtime.callback_begin_zone_timestep_before_set_current_weather(state,
                                                                                        time_step_handlers.overwrite_ep_weather)
    if 'MediumOffice' in coordination.bld_type:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.MediumOffice_get_ep_results)
    elif 'ShoeBoxMedOffi' in coordination.bld_type:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.ShoeBoxMedOffi_get_ep_results)
    elif 'SmallOffice' in coordination.bld_type:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.SmallOffice_get_ep_results)
    elif 'LargeOffice' in coordination.bld_type:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.LargeOffice_get_ep_results)
    elif 'MidriseApartment' in coordination.bld_type:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.MidriseApartment_get_ep_results)
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
    idfFilePath = os.path.join(f'.\\resources\\idf\\Chicago\\MediumOffice', idfFileName)
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    coordination.ep_api.runtime.run_energyplus(state, sys_args)

def run_vcwg(sensitivity_file_name):
    coordination.ini_all(sensitivity_file_name)
    state = coordination.ep_api.state_manager.new_state()
    coordination.psychrometric=coordination.ep_api.functional.psychrometrics(state)
    if 'None' in coordination.config['Bypass']['TopForcingFileName']:
        TopForcingFileName = None
        epwFileName = coordination.config['Bypass']['epwFileName']
    else:
        epwFileName = None
        TopForcingFileName = coordination.config['Bypass']['TopForcingFileName']
    VCWGParamFileName = coordination.config['Bypass']['VCWGParamFileName']
    csv = coordination.config['Bypass']['csv_file_name']
    ViewFactorFileName = f'{csv}_ViewFactor.txt'
    # Initialize the UWG object and run the simulation
    case = f'{csv}'
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()
