
import os, numpy as np, pandas as pd
from threading import Thread
from multiprocessing import Process
import _0_vcwg_ep_coordination as coordination
import _1_ep_time_step_handler as time_step_handlers

def run_ep_api(input_config, input_uwgVariable, input_value):
    info('main line')
    global epwFileName, idfFileName
    coordination.read_ini(input_config, input_uwgVariable, input_value)
    if coordination.config['sensitivity']['uwgVariable'] == 'theta_canyon':
        if input_value == -56:
            idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName'][:-4] + '_Ori+34.idf'
        elif input_value == 0:
            idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName'][:-4] + '_Ori0.idf'
        elif input_value == 56:
            idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName'][:-4] + '_Ori-34.idf'
    elif coordination.config['sensitivity']['uwgVariable'] == 'albedo':
        if input_value == 0.05:
            idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName'][:-4] + '_Albedo0.05.idf'
        elif input_value == 0.25:
            idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName'][:-4] + '_Albedo0.25.idf'
        elif input_value == 0.7:
            idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName'][:-4] + '_Albedo0.7.idf'
    else:
        idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName']

    epwFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['epwFileName']
    coordination.init_ep_api()
    coordination.init_semaphore_lock_settings()
    coordination.init_variables_for_vcwg_ep()
    state = coordination.ep_api.state_manager.new_state()
    coordination.psychrometric=coordination.ep_api.functional.psychrometrics(state)
    coordination.ep_api.runtime.callback_begin_zone_timestep_before_set_current_weather(state,
                                                                                        time_step_handlers.overwrite_ep_weather)
    #coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state, time_step_handlers_1.get_ep_results)
    if 'mediumOffice' in coordination.config['_1_Main_Run_EP22_VCWG2.py']['time_step_handlers']:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.mediumOffice_get_ep_results)
    #coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,time_step_handlers_1.smallOffice_get_ep_results)
    coordination.ep_api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Speed", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Direction", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Drybulb Temperature", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Humidity Ratio", "ENVIRONMENT")

    output_path = os.path.join('.\\resources\\idf', f'{coordination.uwgVariable}{str(coordination.uwgVariableValue)}ep_outputs')
    weather_file_path = os.path.join('.\\resources\\epw', epwFileName)
    idfFilePath = os.path.join('.\\resources\\idf', idfFileName)
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    coordination.ep_api.runtime.run_energyplus(state, sys_args)
def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())


