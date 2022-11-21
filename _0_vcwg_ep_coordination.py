import threading, sys, os
import numpy as np, datetime




def ini_all(input_config, experiments_theme, _controlValue):
    global config, project_path, save_path_clean, sensor_heights,ep_trivial_path, data_saving_path, controlValue, \
        ep_api, psychrometric,\
        sem0, sem1, sem2, sem3, \
        vcwg_needed_time_idx_in_seconds, \
        vcwg_canTemp_K, vcwg_canSpecHum_Ratio, vcwg_canPress_Pa, vcwg_wsp_mps, vcwg_wdir_deg, \
        ep_indoorTemp_C, ep_sensWaste_w_m2_per_footprint_area, \
        ep_floor_Text_K, ep_floor_Tint_K, ep_roof_Text_K, ep_roof_Tint_K, \
        ep_wallSun_Text_K, ep_wallSun_Tint_K, ep_wallShade_Text_K, ep_wallShade_Tint_K, \
        midRiseApartmentBld_floor_area_m2, mediumOfficeBld_footprint_area_m2, smallOfficeBld_footprint_area_m2
    # find the project path
    config = input_config
    controlValue = _controlValue
    project_path = os.path.dirname(os.path.abspath(__file__))
    save_path_clean = False
    sensor_heights = [int(i) for i in config['_0_vcwg_ep_coordination.py']['sensor_height_meter'].split(',')]
    data_saving_path = os.path.join(project_path, 'A_prepost_processing',
                                    experiments_theme,f'{controlValue}.csv')
    ep_trivial_path = os.path.join(project_path, 'A_prepost_processing', experiments_theme, f"{controlValue}ep_trivial_outputs")
    if config['Default']['operating_system'] == 'windows':
        sys.path.insert(0, 'C:/EnergyPlusV22-1-0')
    else:
        sys.path.insert(0, '/usr/local/EnergyPlus-22-1-0/'),
    from pyenergyplus.api import EnergyPlusAPI
    ep_api = EnergyPlusAPI()
    psychrometric = None

    sem0 = threading.Semaphore(1)
    sem1 = threading.Semaphore(0)
    sem2 = threading.Semaphore(0)
    sem3 = threading.Semaphore(0)

    vcwg_needed_time_idx_in_seconds = 0
    vcwg_canTemp_K = 300
    vcwg_canSpecHum_Ratio = 0
    vcwg_canPress_Pa = 0
    vcwg_wsp_mps = 0
    vcwg_wdir_deg = 0

    midRiseApartmentBld_floor_area_m2 = 3135
    smallOfficeBld_footprint_area_m2 = 511
    mediumOfficeBld_footprint_area_m2 = 4982 / 3

    ep_indoorTemp_C = 20
    ep_sensWaste_w_m2_per_footprint_area = 0
    ep_floor_Text_K = 300
    ep_floor_Tint_K = 300
    ep_roof_Text_K = 300
    ep_roof_Tint_K = 300
    ep_wallSun_Text_K = 300
    ep_wallSun_Tint_K = 300
    ep_wallShade_Text_K = 300
    ep_wallShade_Tint_K = 300