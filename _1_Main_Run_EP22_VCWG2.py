
import os, numpy as np, pandas as pd
from threading import Thread
import _0_vcwg_ep_coordination as coordination
import _1_ep_time_step_handler as time_step_handlers_1

def run_ep_api():
    state = coordination.ep_api.state_manager.new_state()
    coordination.psychrometric=coordination.ep_api.functional.psychrometrics(state)
    coordination.ep_api.runtime.callback_begin_zone_timestep_before_set_current_weather(state, time_step_handlers_1.overwrite_ep_weather)
    #coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state, time_step_handlers_1.get_ep_results)
    coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,time_step_handlers_1.mediumOffice_get_ep_results)
    #coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,time_step_handlers_1.smallOffice_get_ep_results)
    coordination.ep_api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Speed", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Wind Direction", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Drybulb Temperature", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Humidity Ratio", "ENVIRONMENT")
    output_path = os.path.join(ep_files_path, 'ep_outputs')
    weather_file_path = os.path.join(epw_files_path, epwFileName)
    idfFilePath = os.path.join(ep_files_path, idfFileName)
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    coordination.ep_api.runtime.run_energyplus(state, sys_args)

if __name__ == '__main__':

    ep_files_path = '.\\resources\\idf'
    epw_files_path='.\\resources\\epw'
    # ep_files_path = '_2_cases_input_outputs\\_05_Basel_BSPR_ue1\\refining_M3ing'
    #ep_files_path = '_2_cases_input_outputs\\_07_vancouver\\DOE_REF_SMALL_OFFICE'
    # case_name = '_BSPA_bypass_refining_M3ing'
    # case_name = '_BSPR_bypass_refining_M3ing'
    #case_name = '_Vancouver_bypass'
    #epwFileName = 'Basel.epw'
    epwFileName = 'Capitoul.epw'
    #epwFileName = 'VancouverTopForcing.epw'
    #epwFileName = 'Guelph_2018.epw'
    idfFileName = 'CAPTIOUL_mediumOffice4B.idf'#'CAPITOUL.idf'
    #idfFileName = 'Vancouver_smallOffice.idf'
    #idfFileName = 'Guelph_Chicago_MediumOffice.idf'
    # idfFileName = 'RefBldgMidriseApartmentPost1980_v1.4_7.2_4C_USA_WA_SEATTLE-M3ing.idf'
    #idfFileName = 'RefBldgSmallOfficePost1980_v1.4_7.2_4C_USA_WA_SEATTLE.idf'
    #idfFileName = 'ue2_RefBldgMidriseApartmentPost1980_v1.4_7.2_4C_USA_WA_SEATTLE.idf'
    #vcwg_ep_saving_path = ep_files_path + f'\\vcwg_ep_saving\\ver{time_step_handler_ver}'

    # Lichen: init the synchronization lock related settings: locks, shared variables.
    #coordination.init_saving_data()
    coordination.init_ep_api()
    #api = coordination.ep_api
    coordination.init_semaphore_lock_settings()
    coordination.init_variables_for_vcwg_ep()

    # Lichen: run ep_thread first, wait for EP warm up and ep_thread will call run VCWG_thread
    ep_thread = Thread(target=run_ep_api)
    ep_thread.start()
    # Lichen: wait for ep_thread to finish to post process some accumulated records
    ep_thread.join()


