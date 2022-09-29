import threading, sys, pandas as pd
import numpy as np, time
sys.path.insert(0, 'C:\EnergyPlusV22-1-0')
from pyenergyplus.api import EnergyPlusAPI
def init_ep_api():
    global ep_api
    ep_api = EnergyPlusAPI()
def init_semaphore_lock_settings():
    global sem_vcwg, sem_energyplus
    sem_vcwg = threading.Semaphore(0)
    sem_energyplus = threading.Semaphore(1)

def init_variables_for_vcwg_ep(_in_ep_files_path, _in_ver):
    global vcwg_needed_time_idx_in_seconds,\
        vcwg_canTemp_K, vcwg_canSpecHum_Ratio, vcwg_canPress_Pa, vcwg_wsp_mps, vcwg_wdir_deg,\
        ep_indoorTemp_C, ep_indoorHum_Ratio, ep_sensCoolDemand_w_m2, ep_sensHeatDemand_w_m2, ep_coolConsump_w_m2, ep_heatConsump_w_m2,\
        ep_elecTotal_w_m2_per_floor_area, ep_sensWaste_w_m2_per_floor_area, ep_floor_fluxMass_w_m2, ep_fluxRoof_w_m2, ep_fluxWall_w_m2, \
        ep_floor_Text_K, ep_floor_Tint_K, ep_roof_Text_K, ep_roof_Tint_K, \
        ep_wallSun_Text_K, ep_wallSun_Tint_K,ep_wallShade_Text_K, ep_wallShade_Tint_K,\
        blf_floor_area_m2, time_step_version, ep_files_path

    vcwg_wsp_mps = 0
    vcwg_wdir_deg = 0
    ep_files_path = _in_ep_files_path
    time_step_version = _in_ver

    if time_step_version == 2:
        global ep_wsp_mps, ep_wdir_deg
        ep_wsp_mps = 0
        ep_wdir_deg = 0
    blf_floor_area_m2 = 3135
    vcwg_needed_time_idx_in_seconds = 0
    vcwg_canTemp_K = 0
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
    ep_floor_fluxMass_w_m2 = 0
    ep_fluxRoof_w_m2 = 0
    ep_fluxWall_w_m2 = 0
    ep_floor_Text_K = 300
    ep_floor_Tint_K = 300
    ep_roof_Text_K = 300
    ep_roof_Tint_K = 300
    ep_wallSun_Text_K = 300
    ep_wallSun_Tint_K = 300
    ep_wallShade_Text_K = 300
    ep_wallShade_Tint_K = 300

def init_saving_data(_in_vcwg_ep_saving_path = '_2_saved\BUBBLE_VCWG-EP-detailed'):
    global saving_data, vcwg_ep_saving_path
    saving_data = {}
    saving_data['TempProfile_K'] = []
    saving_data['SpecHumProfile_Ratio'] = []
    saving_data['PressProfile_Pa'] = []
    saving_data['wind_vxProfile_mps'] = []
    saving_data['wind_vyProfile_mps'] = []
    saving_data['wind_SpeedProfile_mps'] = []
    saving_data['turbulence_tkeProfile_m2s2'] = []
    saving_data['air_densityProfile_kgm3'] = []
    saving_data['sensible_heat_fluxProfile_Wm2'] = []
    saving_data['latent_heat_fluxProfile_Wm2'] = []

    saving_data['can_Averaged_temp_k_specHum_ratio_press_pa'] = []
    saving_data['s_wall_Text_K_n_wall_Text_K'] = []
    saving_data['vcwg_wsp_mps_wdir_deg_ep_wsp_mps_wdir_deg'] = []

    vcwg_ep_saving_path = _in_vcwg_ep_saving_path

def BEMCalc_Element(VerticalProfUrban,BEM, it, simTime, FractionsRoof, Geometry_m):
    """
    type(self.BEM[i])
    <class 'BEMDef.BEMDef'>

    type(self.BEM[i].building)
    <class 'BuildingEnergy.Building'>
    """
    global vcwg_needed_time_idx_in_seconds,\
        vcwg_canTemp_K, vcwg_canSpecHum_Ratio, vcwg_canPress_Pa, vcwg_wsp_mps, vcwg_wdir_deg,\
        ep_indoorTemp_C, ep_indoorHum_Ratio, ep_sensCoolDemand_w_m2, ep_sensHeatDemand_w_m2, ep_coolConsump_w_m2, ep_heatConsump_w_m2,\
        ep_elecTotal_w_m2_per_floor_area, ep_sensWaste_w_m2_per_floor_area, ep_floor_fluxMass_w_m2, ep_fluxRoof_w_m2, ep_fluxWall_w_m2, \
        ep_floor_Text_K, ep_floor_Tint_K, ep_roof_Text_K, ep_roof_Tint_K, ep_wall_Text_K, ep_wall_Tint_K

    sem_energyplus.acquire()
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

    saving_data['TempProfile_K'].append(TempProf_cur)
    saving_data['SpecHumProfile_Ratio'].append(HumProf_cur)
    saving_data['PressProfile_Pa'].append(PresProf_cur)
    saving_data['wind_vxProfile_mps'].append(vxProf)
    saving_data['wind_vyProfile_mps'].append(vyProf)
    saving_data['wind_SpeedProfile_mps'].append(wind_magnitudeProf)
    saving_data['turbulence_tkeProfile_m2s2'].append(tkeProf)
    saving_data['air_densityProfile_kgm3'].append(rhoProf)
    saving_data['sensible_heat_fluxProfile_Wm2'].append(HfluxProf)
    saving_data['latent_heat_fluxProfile_Wm2'].append(LEfluxProf)


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


    saving_data['can_Averaged_temp_k_specHum_ratio_press_pa'].append([canTemp, canHum, vcwg_canPress_Pa])

    BEM_building = BEM.building
    BEM_building.nFloor = max(Geometry_m.Height_canyon / float(BEM_building.floorHeight), 1)
    # print(f'VCWG: Update needed time index[accumulated seconds]: {vcwg_time_index_in_seconds}\n')
    vcwg_needed_time_idx_in_seconds = vcwg_time_index_in_seconds
    vcwg_canTemp_K = canTemp
    vcwg_canSpecHum_Ratio = canHum

    BEM_building.sensWaste = ep_sensWaste_w_m2_per_floor_area * BEM_building.nFloor
    # transfer accumulated seconds to Day, Hour, Minute, Second
    day_hour_min_sec = time.strftime("%dd-%HH:%MM:%SS", time.gmtime(vcwg_time_index_in_seconds))

    print(f"Handler ver{time_step_version}, {day_hour_min_sec}, "
          f"sensWaste (Currently only HVAC Rejection):{BEM_building.sensWaste} watts/ unit footprint area")

    ep_sensWaste_w_m2_per_floor_area = 0

    BEM_building.ElecTotal = ep_elecTotal_w_m2_per_floor_area * BEM_building.nFloor

    BEM.mass.Text = ep_floor_Text_K
    BEM.mass.Tint = ep_floor_Tint_K
    BEM.wallSun.Text = ep_wallSun_Text_K
    BEM.wallSun.Tint = ep_wallSun_Tint_K
    BEM.wallShade.Text = ep_wallShade_Text_K
    BEM.wallShade.Tint = ep_wallShade_Tint_K

    saving_data['s_wall_Text_K_n_wall_Text_K'].append([BEM.wallSun.Text, BEM.wallShade.Text])
    if time_step_version == 2:
        saving_data['vcwg_wsp_mps_wdir_deg_ep_wsp_mps_wdir_deg'].append([vcwg_wsp_mps, vcwg_wdir_deg, ep_wsp_mps, ep_wdir_deg])
    # floor mass, wallSun, wallShade, roofImp, roofVeg
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
    BEM_building.fluxWall = ep_fluxWall_w_m2
    BEM_building.fluxRoof = ep_fluxRoof_w_m2
    BEM_building.fluxMass = ep_floor_fluxMass_w_m2

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

    sem_vcwg.release()

    return BEM
