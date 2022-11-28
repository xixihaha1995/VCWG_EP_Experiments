
import os, numpy as np, pandas as pd
from threading import Thread
from multiprocessing import Process
import _0_vcwg_ep_coordination as coordination
import _1_ep_time_step_handler as time_step_handlers

def run_ep_api(input_config, experiments_theme, input_value):
    info('main line')
    global epwFileName, idfFileName
    coordination.ini_all(input_config, experiments_theme, input_value)
    idfFileName = coordination.config['Default']['climate_zone'] + '_'+input_value + '.idf'
    epwFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['epwFileName']

    state = coordination.ep_api.state_manager.new_state()
    coordination.psychrometric=coordination.ep_api.functional.psychrometrics(state)
    coordination.ep_api.runtime.callback_begin_zone_timestep_before_set_current_weather(state,
                                                                                        time_step_handlers.overwrite_ep_weather)
    if 'MediumOffice' in input_value:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.MediumOffice_get_ep_results)
    elif 'SmallOffice' in input_value:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.SmallOffice_get_ep_results)
    elif 'LargeOffice' in input_value:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.LargeOffice_get_ep_results)
    else:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.general_get_ep_results)

    coordination.ep_api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Speed", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Direction", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Drybulb Temperature", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Humidity Ratio", "ENVIRONMENT")

    output_path = coordination.ep_trivial_path
    weather_file_path = os.path.join('.\\resources\\epw', epwFileName)
    idfs_path = coordination.config['Default']['idfs_path']
    idfFilePath = os.path.join(f'.\\resources\\idf\\{idfs_path}', idfFileName)
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    coordination.ep_api.runtime.run_energyplus(state, sys_args)
def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

