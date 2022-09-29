import os, numpy as np, pandas as pd
from threading import Thread
import _0_EP_VCWG._0_EP._0_vcwg_ep_coordination as coordination
from _1_case_analysis.analysis._1_plots_related import _0_all_plot_tools as plot_tools



def run_ep_api():
    state = api.state_manager.new_state()
    # api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
    #                                                               _01_ep_time_step_handlers._nested_ep_then_vcwg)
    if coordination.time_step_version == 0:
        import _0_EP_VCWG._0_EP._1_ep_time_step_handlers_ver0 as time_step_handlers_0
        api.runtime.callback_end_system_timestep_after_hvac_reporting(state, time_step_handlers_0._nested_ep_then_vcwg)
    elif coordination.time_step_version == 1:
        import _0_EP_VCWG._0_EP._1_ep_time_step_handlers_ver1 as time_step_handlers_1
        api.runtime.callback_end_system_timestep_after_hvac_reporting(state, time_step_handlers_1._nested_ep_then_vcwg)
    elif coordination.time_step_version == 2:
        import _0_EP_VCWG._0_EP._1_ep_time_step_handlers_ver2 as time_step_handlers_2
        api.runtime.callback_end_system_timestep_after_hvac_reporting(state, time_step_handlers_2._nested_ep_then_vcwg)
    # api.runtime.callback_end_zone_timestep_before_zone_reporting(state,
    #                                                               _01_ep_time_step_handlers._nested_ep_only)
    api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
    api.exchange.request_variable(state, "Site Wind Speed", "ENVIRONMENT")
    api.exchange.request_variable(state, "Site Wind Direction", "ENVIRONMENT")

    output_path = os.path.join(ep_files_path, 'ep_outputs')
    weather_file_path = os.path.join(ep_files_path,'..', epwFileName)
    idfFilePath = os.path.join(ep_files_path, idfFileName)
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    api.runtime.run_energyplus(state, sys_args)

if __name__ == '__main__':
    time_step_handler_ver = 2
    ep_files_path = '_1_case_analysis\\cases\\_05_Basel_BSPR_ue1\\refining_M2'
    epwFileName = 'Basel.epw'
    idfFileName = 'RefBldgMidriseApartmentPost1980_v1.4_7.2_4C_USA_WA_SEATTLE-M2.idf'

    # Lichen: init the synchronization lock related settings: locks, shared variables.
    coordination.init_saving_data()
    coordination.init_ep_api()
    api = coordination.ep_api
    coordination.init_semaphore_lock_settings()
    coordination.init_variables_for_vcwg_ep(ep_files_path, time_step_handler_ver)

    # Lichen: run ep_thread first, wait for EP warm up and ep_thread will call run VCWG_thread
    ep_thread = Thread(target=run_ep_api)
    ep_thread.start()
    # Lichen: wait for ep_thread to finish to post process some accumulated records
    ep_thread.join()

    case_name = '_BSPR_bypass_refining_M2'
    vcwg_ep_saving_path = ep_files_path + f'\\vcwg_ep_saving\\ver{time_step_handler_ver}'

    start_time = '2002-06-10 00:00:00'
    time_interval_sec = 300
    # Lichen: post process, such as [timestamp, waste heat] * time_steps_num
    data_name_lst = ['TempProfile_K', 'SpecHumProfile_Ratio', 'PressProfile_Pa', 'wind_vxProfile_mps',
                     'wind_vyProfile_mps', 'wind_SpeedProfile_mps', 'turbulence_tkeProfile_m2s2',
                     'air_densityProfile_kgm3', 'sensible_heat_fluxProfile_Wm2', 'latent_heat_fluxProfile_Wm2',
                     'can_Averaged_temp_k_specHum_ratio_press_pa','s_wall_Text_K_n_wall_Text_K']
    if coordination.time_step_version == 2:
        data_name_lst.append('vcwg_wsp_mps_wdir_deg_ep_wsp_mps_wdir_deg')
    for data_name in data_name_lst:
        plot_tools.save_data_to_csv(coordination.saving_data, data_name,case_name,
                                    start_time, time_interval_sec, vcwg_ep_saving_path)