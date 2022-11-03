import threading, sys, configparser, os
import numpy as np, datetime

save_path_clean = False

sys.path.insert(0,'C:\EnergyPlusV22-1-0')
from pyenergyplus.api import EnergyPlusAPI
def init_ep_api():
    global ep_api, psychrometric
    ep_api=EnergyPlusAPI()
    psychrometric =None

def read_ini(config_file_name):
    global config, project_path, sensor_heights
    config = configparser.ConfigParser()
    # find the project path
    project_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(project_path,'A_prepost_processing', 'configs',config_file_name)
    config.read(config_path)
    sensor_heights = [int(i) for i in config['_0_vcwg_ep_coordination.py']['sensor_height_meter'].split(',')]

def init_semaphore_lock_settings():
    global sem0, sem1, sem2, sem3
    sem0 = threading.Semaphore(1)
    sem1 = threading.Semaphore(0)
    sem2 = threading.Semaphore(0)
    sem3 = threading.Semaphore(0)
    # sem0 VCWG calculates canyon data for EP
    # sem1 EP download canyon data
    # sem2 EP calculates sensHVAC, surface temperature
    # sem3 VCWG download sensHVAC, surface temperature from EP
def init_variables_for_vcwg_ep():
    global vcwg_needed_time_idx_in_seconds,\
        vcwg_canTemp_K, vcwg_canSpecHum_Ratio, vcwg_canPress_Pa, vcwg_wsp_mps, vcwg_wdir_deg,\
        ep_indoorTemp_C, ep_indoorHum_Ratio, ep_sensCoolDemand_w_m2, ep_sensHeatDemand_w_m2, ep_coolConsump_w_m2, ep_heatConsump_w_m2,\
        ep_elecTotal_w_m2_per_floor_area, ep_sensWaste_w_m2_per_floor_area, \
        ep_floor_Text_K, ep_floor_Tint_K, ep_roof_Text_K, ep_roof_Tint_K, \
        ep_wallSun_Text_K, ep_wallSun_Tint_K,ep_wallShade_Text_K, ep_wallShade_Tint_K,\
        midRiseApartmentBld_floor_area_m2, mediumOfficeBld_floor_area_m2, smallOfficeBld_floor_area_m2, time_step_version, ep_files_path,\
        ep_oaTemp_C, overwriting_time_index, overwriten_time_index, count
    count=0
    vcwg_wsp_mps = 0
    vcwg_wdir_deg = 0
    midRiseApartmentBld_floor_area_m2 = 3135
    smallOfficeBld_floor_area_m2 = 511
    mediumOfficeBld_floor_area_m2 = 4982
    vcwg_needed_time_idx_in_seconds = 0
    overwriting_time_index = 0
    overwriten_time_index = 0
    vcwg_canTemp_K = 300
    vcwg_canSpecHum_Ratio = 0
    vcwg_canPress_Pa = 0
    ep_indoorTemp_C = 20
    ep_indoorHum_Ratio = 0.006
    ep_sensCoolDemand_w_m2 = 0
    ep_sensHeatDemand_w_m2 = 0
    ep_coolConsump_w_m2 = 0
    ep_heatConsump_w_m2 = 0
    ep_elecTotal_w_m2_per_floor_area = 0
    ep_sensWaste_w_m2_per_floor_area = 0
    ep_oaTemp_C = 7

    ep_floor_Text_K = 300
    ep_floor_Tint_K = 300
    ep_roof_Text_K = 300
    ep_roof_Tint_K = 300
    ep_wallSun_Text_K = 300
    ep_wallSun_Tint_K = 300
    ep_wallShade_Text_K = 300
    ep_wallShade_Tint_K = 300

def BEMCalc_Element(VerticalProfUrban,BEM, it, simTime, FractionsRoof, Geometry_m, MeteoData):

    global vcwg_needed_time_idx_in_seconds,\
        vcwg_canTemp_K, vcwg_canSpecHum_Ratio, vcwg_canPress_Pa, vcwg_wsp_mps, vcwg_wdir_deg,\
        ep_indoorTemp_C, ep_indoorHum_Ratio, ep_sensCoolDemand_w_m2, ep_sensHeatDemand_w_m2, ep_coolConsump_w_m2, ep_heatConsump_w_m2,\
        ep_elecTotal_w_m2_per_floor_area, ep_sensWaste_w_m2_per_floor_area, ep_floor_fluxMass_w_m2, ep_fluxRoof_w_m2, ep_fluxWall_w_m2, \
        ep_floor_Text_K, ep_floor_Tint_K, ep_roof_Text_K, ep_roof_Tint_K, ep_wall_Text_K, ep_wall_Tint_K, count
    #Wait for the upstream (VCWG download EP results from Parent) to finish
    sem0.acquire()
    vcwg_time_index_in_seconds = (it + 1) * simTime.dt

    TempProf_cur = VerticalProfUrban.th
    HumProf_cur = VerticalProfUrban.qn
    PresProf_cur = VerticalProfUrban.presProf
    vxProf = VerticalProfUrban.vx
    vyProf = VerticalProfUrban.vy
    wind_magnitudeProf = VerticalProfUrban.s
    tkeProf = VerticalProfUrban.tke
    rhoProf = VerticalProfUrban.rho
    HfluxProf = VerticalProfUrban.Hflux
    LEfluxProf = VerticalProfUrban.LEflux

    canTempProf_cur = TempProf_cur[0:Geometry_m.nz_u]
    canSpecHumProf_cur = HumProf_cur[0:Geometry_m.nz_u]
    canPressProf_cur = PresProf_cur[0:Geometry_m.nz_u]
    canWspdProf_cur = wind_magnitudeProf[0:Geometry_m.nz_u]
    # tan(wdir) = vx/vy, wdir unit is degree from 0 to 360, 0 is north, 90 is east, 180 is south, 270 is west
    canWdirProf_cur = np.arctan(vxProf[0:Geometry_m.nz_u] / vyProf[0:Geometry_m.nz_u]) * 180 / np.pi

    canTemp = np.mean(canTempProf_cur)
    canHum = np.mean(canSpecHumProf_cur)
    vcwg_canPress_Pa = np.mean(canPressProf_cur)
    vcwg_wsp_mps = np.mean(canWspdProf_cur)
    vcwg_wdir_deg = np.mean(canWdirProf_cur) + Geometry_m.theta_canyon
    BEM_building = BEM.building
    BEM_building.nFloor = max(Geometry_m.Height_canyon / float(BEM_building.floorHeight), 1)
    vcwg_needed_time_idx_in_seconds = vcwg_time_index_in_seconds
    vcwg_canTemp_K = canTemp
    vcwg_canSpecHum_Ratio = canHum
    # Notify to the downstream (EP download canyon info from Parent) to start
    sem1.release()

    # Waiting for the upstream (EP upload results to Parent) to finish
    sem3.acquire()
    # VCWG download EP results from Parent

    BEM_building.sensWaste = ep_sensWaste_w_m2_per_floor_area * BEM_building.nFloor
    ep_sensWaste_w_m2_per_floor_area = 0

    BEM_building.ElecTotal = ep_elecTotal_w_m2_per_floor_area * BEM_building.nFloor
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

    BEM_building.sensCoolDemand = ep_sensCoolDemand_w_m2
    BEM_building.sensHeatDemand = ep_sensHeatDemand_w_m2
    BEM_building.coolConsump = ep_coolConsump_w_m2
    BEM_building.heatConsump = ep_heatConsump_w_m2
    BEM_building.indoorTemp = ep_indoorTemp_C + 273.15
    BEM_building.indoorHum = ep_indoorHum_Ratio


    BEM_building.indoorRhum = 0.6
    BEM_building.sensWasteCoolHeatDehum = 0.0  # Sensible waste heat per unit building footprint area only including cool, heat, and dehum [W m-2]
    BEM_building.dehumDemand = 0.0  # Latent heat demand for dehumidification of air per unit building footprint area [W m^-2]
    BEM_building.dehumDemand = 0.5
    BEM_building.fluxSolar = 0.5
    BEM_building.fluxWindow = 0.5
    BEM_building.fluxInterior = 0.5
    BEM_building.fluxInfil = 0.5
    BEM_building.fluxVent = 0.5
    BEM_building.QWater = 0.5
    BEM_building.QGas = 0.5
    BEM_building.Qhvac = 0.5
    BEM_building.Qheat = 0.5
    BEM_building.GasTotal = 0.5
    # wall load per unit building footprint area [W m^-2]
    BEM_building.QWall = 0.5
    # other surfaces load per unit building footprint area [W m^-2]
    BEM_building.QMass = 0.5
    # window load due to temperature difference per unit building footprint area [W m^-2]
    BEM_building.QWindow = 0.5
    # ceiling load per unit building footprint area [W m^-2]
    BEM_building.QCeil = 0.5
    # infiltration load per unit building footprint area [W m^-2]
    BEM_building.QInfil = 0.5
    # ventilation load per unit building footprint area [W m^-2]
    BEM_building.QVen = 0.5
    BEM_building.QWindowSolar = 0.5
    BEM_building.elecDomesticDemand = 0.5
    BEM_building.sensWaterHeatDemand = 0.5
    BEM_building.fluxWall = 0
    BEM_building.fluxRoof = 0
    BEM_building.fluxMass = 0
    # Notify to the downstream (VCWG upload canyon info to Parent) to start
    sem0.release()
    TempProf_cur = VerticalProfUrban.th
    PresProf_cur = VerticalProfUrban.presProf
    WallshadeT = BEM.wallShade.Text
    WalllitT = BEM.wallSun.Text
    RoofT = BEM.roofImp.Text
    senWaste = BEM_building.sensWaste
    # with open('tempProfile.csv','a') as f0:
    # fmt0 = "%.3f," * 301 % (simTime.secDay, TempProf_cur, HumProf_cur, PresProf_cur,vxProf, vyProf, HfluxProf) + "\n"
    #    fmt0 = ["%.3f"% i for i in TempProf_cur]
    #    f0.write(str(fmt0)+"\n")
    # with open('VCWG_result_ue1.csv', 'a') as f1:
    '''with open('VCWG_EP_result_ue1.csv', 'a') as f1:
        fmt1 = "%.3f," * 18 % (simTime.secDay, WallshadeT, WalllitT, RoofT, canTemp, senWaste, TempProf_cur[2], TempProf_cur[13], \
        TempProf_cur[17], TempProf_cur[21],TempProf_cur[25], TempProf_cur[31], PresProf_cur[2], PresProf_cur[13], \
        PresProf_cur[17], PresProf_cur[21], PresProf_cur[25], PresProf_cur[31]) + "\n"
        # fmt = "%.3f, %.2f, %.2f, %.2f, %.2f,%.2f\n" % (simTime.secDay,WallshadeT,WalllitT,RoofT,canTemp,senWaste)
        f1.write(fmt1)
    with open('10min_VCWG_EP_result_ue1.csv', 'a') as f2:
        fmt2 = "%.3f," * 18 % (simTime.secDay, WallshadeT, WalllitT, RoofT, canTemp, senWaste, TempProf_cur[2], TempProf_cur[13], \
        TempProf_cur[17], TempProf_cur[21],TempProf_cur[25], TempProf_cur[31], PresProf_cur[2], PresProf_cur[13], \
        PresProf_cur[17], PresProf_cur[21], PresProf_cur[25], PresProf_cur[31]) + "\n"
        # fmt = "%.3f, %.2f, %.2f, %.2f, %.2f,%.2f\n" % (simTime.secDay,WallshadeT,WalllitT,RoofT,canTemp,senWaste)
        count=count+1
        if count%2==0:
            f2.write(fmt2)
    '''
    '''with open('VCWG_0HVAC_result_ue2.csv', 'a') as f1:
        fmt1 = "%.3f," * 16 % (
        simTime.secDay, WallshadeT, WalllitT, RoofT, canTemp, senWaste, TempProf_cur[2], TempProf_cur[15], \
        TempProf_cur[22], TempProf_cur[27], TempProf_cur[32], PresProf_cur[2], \
        PresProf_cur[15], PresProf_cur[22], PresProf_cur[27], PresProf_cur[32]) + "\n"
        # fmt = "%.3f, %.2f, %.2f, %.2f, %.2f,%.2f\n" % (simTime.secDay,WallshadeT,WalllitT,RoofT,canTemp,senWaste)
        f1.write(fmt1)
    with open('10min_VCWG_0HVAC_result_ue2.csv', 'a') as f2:
        fmt2 = "%.3f," * 16 % (simTime.secDay, WallshadeT, WalllitT, RoofT, canTemp, senWaste, TempProf_cur[2], \
                               TempProf_cur[15], TempProf_cur[22], TempProf_cur[27], TempProf_cur[32], PresProf_cur[2],
                               PresProf_cur[15], \
                               PresProf_cur[22], PresProf_cur[27], PresProf_cur[32]) + "\n"
        # fmt = "%.3f, %.2f, %.2f, %.2f, %.2f,%.2f\n" % (simTime.secDay,WallshadeT,WalllitT,RoofT,canTemp,senWaste)
        count = count + 1
        if count % 2 == 0:
            f2.write(fmt2)
    '''
    data_saving_path = os.path.join(project_path, 'A_prepost_processing','sensitivity_saving',
                                    config['_0_vcwg_ep_coordination.py']['site_location'],
                                    config['_0_vcwg_ep_coordination.py']['theme'],
                                    config['_0_vcwg_ep_coordination.py']['choice'] + '.csv')
    global save_path_clean
    if os.path.exists(data_saving_path) and not save_path_clean:
        os.remove(data_saving_path)
        save_path_clean = True
    # start_time + accumulative_seconds
    cur_datetime = datetime.datetime.strptime(config['_0_vcwg_ep_coordination.py']['start_time'], '%Y-%m-%d %H:%M:%S') + \
                      datetime.timedelta(seconds=vcwg_time_index_in_seconds - simTime.dt)
    domain_height = len(TempProf_cur)
    vcwg_heights_profile = np.array([0.5 + i for i in range(domain_height)])
    mapped_indices = [np.argmin(np.abs(vcwg_heights_profile - i)) for i in sensor_heights]

    #if not exist, create the file and write the header
    if not os.path.exists(data_saving_path):
        os.makedirs(os.path.dirname(data_saving_path), exist_ok=True)
        with open(data_saving_path, 'a') as f1:
            # prepare the header string for different sensors
            header_str = 'cur_datetime,WallshadeT,WalllitT,RoofT,canTemp,senWaste,MeteoData.Tatm,MeteoData.Pre,'
            for i in mapped_indices:
                header_str += 'TempProf_cur[%d],' % i + 'PresProf_cur[%d],' % i
            header_str = header_str[:-1] + '\n'
            f1.write(header_str)

    # write the data
    with open(data_saving_path, 'a') as f1:
        fmt1 = "%s," * 1 % (cur_datetime) + \
               "%.3f," * 7 % (WallshadeT, WalllitT, RoofT, canTemp, senWaste, MeteoData.Tatm, MeteoData.Pre) + \
               "%.3f," * 2* len(mapped_indices) % tuple([TempProf_cur[i] for i in mapped_indices] + \
                                                        [PresProf_cur[i] for i in mapped_indices]) + '\n'
        f1.write(fmt1)
    # with open('capitoul.csv', 'a') as f1:
    #     fmt1 = "%.3f," * 8 % (
    #     simTime.secDay, WallshadeT, WalllitT, RoofT, canTemp, senWaste, TempProf_cur[19], PresProf_cur[19]) \
    #      + "\n"
    #     # fmt = "%.3f, %.2f, %.2f, %.2f, %.2f,%.2f\n" % (simTime.secDay,WallshadeT,WalllitT,RoofT,canTemp,senWaste)
    #     f1.write(fmt1)

    '''
    with open('vancouver.csv', 'a') as f1:
        fmt1 = "%.3f," * 10 % (
            simTime.secDay, WallshadeT, WalllitT, RoofT, canTemp, senWaste, TempProf_cur[1],TempProf_cur[19], PresProf_cur[1],PresProf_cur[19]) \
               + "\n"
        # fmt = "%.3f, %.2f, %.2f, %.2f, %.2f,%.2f\n" % (simTime.secDay,WallshadeT,WalllitT,RoofT,canTemp,senWaste)
        f1.write(fmt1)
    with open('30min_vancouver.csv', 'a') as f2:
        fmt2 = "%.3f," * 10 % (simTime.secDay, WallshadeT, WalllitT, RoofT, canTemp, senWaste, TempProf_cur[1], \
                              TempProf_cur[19],PresProf_cur[1],PresProf_cur[19]) + "\n"
        # fmt = "%.3f, %.2f, %.2f, %.2f, %.2f,%.2f\n" % (simTime.secDay,WallshadeT,WalllitT,RoofT,canTemp,senWaste)
        count = count + 1
        if count % 6 == 0:
            f2.write(fmt2)
    '''
    '''with open('guelph.csv', 'a') as f1:
        fmt1 = "%.3f," * 12 % (
            simTime.secDay, WallshadeT, WalllitT, RoofT, canTemp, senWaste, TempProf_cur[2],TempProf_cur[5],TempProf_cur[17], PresProf_cur[2],PresProf_cur[5],PresProf_cur[17]) \
               + "\n"
        # fmt = "%.3f, %.2f, %.2f, %.2f, %.2f,%.2f\n" % (simTime.secDay,WallshadeT,WalllitT,RoofT,canTemp,senWaste)
        f1.write(fmt1)
    with open('30min_guelph.csv', 'a') as f2:
        fmt2 = "%.3f," * 12 % (simTime.secDay, WallshadeT, WalllitT, RoofT, canTemp, senWaste, TempProf_cur[2], TempProf_cur[5], \
                              TempProf_cur[17],PresProf_cur[2],PresProf_cur[5], PresProf_cur[17]) + "\n"
        # fmt = "%.3f, %.2f, %.2f, %.2f, %.2f,%.2f\n" % (simTime.secDay,WallshadeT,WalllitT,RoofT,canTemp,senWaste)
        count = count + 1
        if count % 6 == 0:
            f2.write(fmt2)
    '''
    return BEM