import configparser
import datetime
import threading, sys, os

import numpy


def ini_all(sensitivity_file_name,_config_file = None, _value = None):
    global value, config, project_path, save_path_clean, sensor_heights,ep_trivial_path, data_saving_path, bld_type,\
        ep_api, psychrometric,\
        sem0, sem1, sem2, sem3, \
        vcwg_needed_time_idx_in_seconds, \
        vcwg_canTemp_K, vcwg_canSpecHum_Ratio, vcwg_canPress_Pa, vcwg_wsp_mps, vcwg_wdir_deg, \
        vcwg_canTemp_K_list, vcwg_canSpecHum_Ratio_list, vcwg_canPress_Pa_list, \
    ep_indoorTemp_C, ep_sensWaste_w_m2_per_footprint_area, \
        ep_floor_Text_K, ep_floor_Tint_K, ep_roof_Text_K, ep_roof_Tint_K, \
        ep_wallSun_Text_K, ep_wallSun_Tint_K, ep_wallShade_Text_K, ep_wallShade_Tint_K, \
        mediumOfficeBld_footprint_area_m2, smallOfficeBld_footprint_area_m2,\
        footprint_area_m2, ForcTemp_K, vcwg_hConv_w_m2_per_K, EP_nFloor
    # find the project path
    value = _value
    ForcTemp_K = 293.15
    vcwg_hConv_w_m2_per_K = 10
    project_path = os.path.dirname(os.path.abspath(__file__))
    if _config_file is None:
        config = configparser.ConfigParser()
        config_path = os.path.join(project_path, 'A_prepost_processing','configs','bypass', sensitivity_file_name)
        config.read(config_path)
        csv_file_name = config['Bypass']['csv_file_name']
    else:
        config = _config_file
        csv_file_name = _value
    bld_type = config['Bypass']['bld_type']
    experiments_theme = config['Bypass']['experiments_theme']
    save_path_clean = False
    sensor_heights = [float(i) for i in config['Bypass']['sensor_height_meter'].split(',')]
    data_saving_path = os.path.join(project_path, 'A_prepost_processing',
                                    experiments_theme,f'{csv_file_name}.csv')
    ep_trivial_path = os.path.join(project_path, 'A_prepost_processing',
                                   experiments_theme, f"{csv_file_name}_ep_trivial_outputs")
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

    if "SmallOffice" in bld_type:
        footprint_area_m2 = 5500 * 0.09290304 / 1
    elif "MediumOffice" in bld_type:
        EP_nFloor = 3
        footprint_area_m2 = 53628 * 0.09290304 / 3
    elif "LargeOffice" in bld_type:
        footprint_area_m2 = 498588 * 0.09290304 / 12
    elif "MidriseApartment" in bld_type:
        footprint_area_m2 = 33740 * 0.09290304 / 4
    elif "StandAloneRetail" in bld_type:
        footprint_area_m2 = 24962 * 0.09290304 /1
    elif "StripMall" in bld_type:
        footprint_area_m2 = 22500 * 0.09290304 / 1
    elif "SuperMarket" in bld_type:
        footprint_area_m2 = 45000 * 0.09290304 / 1

    vcwg_canTemp_K_list = [ 300 for i in range(EP_nFloor)]
    vcwg_canSpecHum_Ratio_list = [ 0 for i in range(EP_nFloor)]
    vcwg_canPress_Pa_list = [ 0 for i in range(EP_nFloor)]

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
    
def BEMCalc_Element(BEM, it, simTime, VerticalProfUrban, Geometry_m,MeteoData,
                    FractionsRoof):
    global ep_sensWaste_w_m2_per_footprint_area,save_path_clean,vcwg_needed_time_idx_in_seconds, \
        vcwg_canTemp_K, vcwg_canSpecHum_Ratio, vcwg_canPress_Pa, \
        vcwg_canTemp_K_list, vcwg_canSpecHum_Ratio_list,vcwg_canPress_Pa_list

    sem0.acquire()
    vcwg_needed_time_idx_in_seconds = (it + 1) * simTime.dt

    TempProf_cur = VerticalProfUrban.th
    HumProf_cur = VerticalProfUrban.qn
    PresProf_cur = VerticalProfUrban.presProf

    canTempProf_cur = TempProf_cur[0:Geometry_m.nz_u]
    canSpecHumProf_cur = HumProf_cur[0:Geometry_m.nz_u]
    canPressProf_cur = PresProf_cur[0:Geometry_m.nz_u]

    vcwg_canTemp_K = numpy.mean(canTempProf_cur)
    vcwg_canSpecHum_Ratio = numpy.mean(canSpecHumProf_cur)
    vcwg_canPress_Pa = numpy.mean(canPressProf_cur)
    '''
    Instead vcwg_canTemp_K (use one scalar value to represent all grid points within the canopy, Geometry_m.nz_u)
    To split the canopy into EP_nFloor layers:
    The first layer is the floor,..., the last layer is for the highest floor    
    '''
    for i in range(EP_nFloor):
        vcwg_canTemp_K_list[i] =numpy.mean(
            canTempProf_cur[int(i * Geometry_m.nz_u / EP_nFloor):int((i + 1) * Geometry_m.nz_u / EP_nFloor)])
        vcwg_canSpecHum_Ratio_list[i] =numpy.mean(
            canSpecHumProf_cur[int(i * Geometry_m.nz_u / EP_nFloor):int((i + 1) * Geometry_m.nz_u / EP_nFloor)])
        vcwg_canPress_Pa_list[i] =numpy.mean(
            canPressProf_cur[int(i * Geometry_m.nz_u / EP_nFloor):int((i + 1) * Geometry_m.nz_u / EP_nFloor)])
    pass
    sem1.release()
    
    sem3.acquire()
    BEM_Building = BEM.building
    BEM_Building.ElecTotal = 0
    BEM_Building.sensWaste = ep_sensWaste_w_m2_per_footprint_area
    ep_sensWaste_w_m2_per_footprint_area = 0

    BEM.mass.Text = ep_floor_Text_K
    BEM.mass.Tint = ep_floor_Tint_K
    BEM.wallSun.Text = ep_wallSun_Text_K
    BEM.wallSun.Tint = ep_wallSun_Tint_K
    BEM.wallShade.Text = ep_wallShade_Text_K
    BEM.wallShade.Tint = ep_wallShade_Tint_K

    if FractionsRoof.fimp > 0:
        BEM.roofImp.Text = ep_roof_Text_K
        BEM.roofImp.Tint = ep_roof_Tint_K
    if FractionsRoof.fveg > 0:
        BEM.roofVeg.Text = ep_roof_Text_K
        BEM.roofVeg.Tint = ep_roof_Tint_K

    if os.path.exists(data_saving_path) and not save_path_clean:
        os.remove(data_saving_path)
        save_path_clean = True

    TempProf_cur = VerticalProfUrban.th
    PresProf_cur = VerticalProfUrban.presProf
    vcwg_needed_time_idx_in_seconds = it * simTime.dt
    cur_datetime = datetime.datetime.strptime(config['__main__']['start_time'],
                                              '%Y-%m-%d %H:%M:%S') + \
                   datetime.timedelta(seconds=vcwg_needed_time_idx_in_seconds)
    print('current time: ', cur_datetime)
    domain_height = len(TempProf_cur)
    vcwg_heights_profile = numpy.array([0.5 + i for i in range(domain_height)])
    mapped_indices = [numpy.argmin(numpy.abs(vcwg_heights_profile - i)) for i in sensor_heights]

    wallSun_K = BEM.wallSun.Text
    wallShade_K = BEM.wallShade.Text
    roof_K = (FractionsRoof.fimp * BEM.roofImp.Text + FractionsRoof.fveg * BEM.roofVeg.Text)

    # dummy values overriding
    BEM_Building.sensCoolDemand = 0
    BEM_Building.sensHeatDemand = 0
    BEM_Building.dehumDemand = 0
    BEM_Building.Qhvac = 0
    BEM_Building.coolConsump = 0
    BEM_Building.heatConsump = 0
    BEM_Building.QWater = 0.5
    BEM_Building.QGas = 0.5
    BEM_Building.Qheat = 0.5
    BEM_Building.GasTotal = 0.5
    # wall load per unit building footprint area [W m^-2]
    BEM_Building.QWall = 0.5
    # other surfaces load per unit building footprint area [W m^-2]
    BEM_Building.QMass = 0.5
    # window load due to temperature difference per unit building footprint area [W m^-2]
    BEM_Building.QWindow = 0.5
    # ceiling load per unit building footprint area [W m^-2]
    BEM_Building.QCeil = 0.5
    # infiltration load per unit building footprint area [W m^-2]
    BEM_Building.QInfil = 0.5
    # ventilation load per unit building footprint area [W m^-2]
    BEM_Building.QVen = 0.5
    BEM_Building.QWindowSolar = 0.5
    BEM_Building.elecDomesticDemand = 0.5
    BEM_Building.sensWaterHeatDemand = 0.5
    BEM_Building.sensWasteCoolHeatDehum = 0.5
    BEM_Building.indoorRhum = 0.6
    BEM_Building.fluxSolar = 0.5
    BEM_Building.fluxWindow = 0.5
    BEM_Building.fluxInterior = 0.5
    BEM_Building.fluxInfil = 0.5
    BEM_Building.fluxVent = 0.5
    BEM_Building.fluxWall = 0
    BEM_Building.fluxRoof = 0
    BEM_Building.fluxMass = 0

    if not os.path.exists(data_saving_path):
        os.makedirs(os.path.dirname(data_saving_path), exist_ok=True)
        with open(data_saving_path, 'a') as f1:
            # prepare the header string for different sensors
            header_str = 'cur_datetime,canTemp,ForcTemp_K,sensWaste,wallSun_K,wallShade_K,roof_K,' \
                         'MeteoData.Tatm,MeteoData.Pre,'
            for i in range(len(mapped_indices)):
                _temp_height = sensor_heights[i]
                header_str += f'TempProf_cur[{_temp_height}],'
            for i in range(len(mapped_indices)):
                _temp_height = sensor_heights[i]
                header_str += f'PresProf_cur[{_temp_height}],'
            header_str += '\n'
            f1.write(header_str)
        # write the data
    with open(data_saving_path, 'a') as f1:
        fmt1 = "%s," * 1 % (cur_datetime) + \
               "%.3f," * 8 % (vcwg_canTemp_K,ForcTemp_K,BEM_Building.sensWaste,
                              wallSun_K,wallShade_K,roof_K,MeteoData.Tatm, MeteoData.Pre) + \
               "%.3f," * 2 * len(mapped_indices) % tuple([TempProf_cur[i] for i in mapped_indices] + \
                                                         [PresProf_cur[i] for i in mapped_indices]) + '\n'
        f1.write(fmt1)

    sem0.release()

    return BEM