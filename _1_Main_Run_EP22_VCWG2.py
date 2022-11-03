
import os, numpy as np, pandas as pd
from threading import Thread
import _0_vcwg_ep_coordination as coordination
import _1_ep_time_step_handler as time_step_handlers

def run_ep_api():
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
    output_path = os.path.join('.\\resources\\idf', 'ep_outputs')
    weather_file_path = os.path.join('.\\resources\\epw', epwFileName)
    idfFilePath = os.path.join('.\\resources\\idf', idfFileName)
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    coordination.ep_api.runtime.run_energyplus(state, sys_args)

if __name__ == '__main__':
    prompt = 'Please enter the configuration file name: [Bypass_CAPITOUL_NoCooling.ini]'
    config_file_name = input(prompt) or 'Bypass_CAPITOUL_NoCooling.ini'
    coordination.read_ini(config_file_name)
    epwFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['epwFileName']
    idfFileName = coordination.config['_1_Main_Run_EP22_VCWG2.py']['idfFileName']

    # Lichen: init the synchronization lock related settings: locks, shared variables.
    coordination.init_ep_api()
    coordination.init_semaphore_lock_settings()
    coordination.init_variables_for_vcwg_ep()

    # Lichen: run ep_thread first, wait for EP warm up and ep_thread will call run VCWG_thread
    ep_thread = Thread(target=run_ep_api)
    ep_thread.start()
    # Lichen: wait for ep_thread to finish to post process some accumulated records
    ep_thread.join()


