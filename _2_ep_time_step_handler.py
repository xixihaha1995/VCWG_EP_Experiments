from threading import Thread
import _1_vcwg_ep_coordination as coordination
from VCWG_Hydrology import VCWG_Hydro
import os, signal

get_ep_results_inited_handle = False
overwrite_ep_weather_inited_handle = False
called_vcwg_bool = False

accu_hvac_heat_rejection_J = 0
zone_floor_area_m2 = 0
ep_last_accumulated_time_index_in_seconds = 0
ep_last_call_time_seconds = 0

def run_vcwg():
    if 'None' in coordination.config['Bypass']['TopForcingFileName']:
        TopForcingFileName = None
        epwFileName = coordination.config['Bypass']['epwFileName']
    else:
        epwFileName = None
        TopForcingFileName = coordination.config['Bypass']['TopForcingFileName']
    VCWGParamFileName = coordination.config['Bypass']['VCWGParamFileName']
    ViewFactorFileName = f'{coordination.csv_file_name}_ViewFactor.txt'
    # Case name to append output file names with
    case = f'{coordination.csv_file_name}'
    # Initialize the UWG object and run the simulation
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()

def overwrite_ep_weather(state):
    global overwrite_ep_weather_inited_handle, odb_actuator_handle, orh_actuator_handle, \
        wsped_mps_actuator_handle, wdir_deg_actuator_handle,zone_flr_area_handle,\
        called_vcwg_bool

    if not overwrite_ep_weather_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        overwrite_ep_weather_inited_handle = True
        odb_actuator_handle = coordination.ep_api.exchange.\
            get_actuator_handle(state, "Weather Data", "Outdoor Dry Bulb", "Environment")
        orh_actuator_handle = coordination.ep_api.exchange.\
            get_actuator_handle(state, "Weather Data", "Outdoor Relative Humidity", "Environment")
        if "MediumOffice" in coordination.bld_type or 'Detailed_MedOffice' in coordination.bld_type:
            global roof_hConv_actuator_handle
            roof_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "BUILDING_ROOF")
        elif "ShoeBox_MedOffice" in coordination.bld_type:
            roof_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "Surface 2")
        elif 'Simplified_MedOffice' in coordination.bld_type:
            roof_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "Surface 14")
        if 'ShoeBox_HighOffice' in coordination.bld_type:
            global Surface_3_roof_hConv_actuator_handle
            Surface_3_roof_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "Surface 3")
        if "HighOffice" in coordination.bld_type and 'ShoeBox_HighOffice' not in coordination.bld_type:
            global Surface_576_roof_hConv_actuator_handle, \
                Surface_582_roof_hConv_actuator_handle, Surface_588_roof_hConv_actuator_handle, \
                Surface_594_roof_hConv_actuator_handle, Surface_600_roof_hConv_actuator_handle

            Surface_576_roof_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "Surface 576")
            Surface_582_roof_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "Surface 582")
            Surface_588_roof_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "Surface 588")
            Surface_594_roof_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "Surface 594")
            Surface_600_roof_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "Surface 600")
        if odb_actuator_handle < 0 or orh_actuator_handle < 0:
            print('ovewrite_ep_weather(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)
        elif "MediumOffice" in coordination.bld_type or 'MedOffice' in coordination.bld_type:
            if roof_hConv_actuator_handle < 0:
                print('ovewrite_ep_weather():  MediumOffice, some roofhConv handle not available')
                os.getpid()
                os.kill(os.getpid(), signal.SIGTERM)
        elif "HighOffice" in coordination.bld_type:
            if 'ShoeBox_HighOffice' in coordination.bld_type:
                if Surface_3_roof_hConv_actuator_handle < 0:
                    print('ovewrite_ep_weather(): ShoeBox HighOffice,some handle not available')
                    os.getpid()
                    os.kill(os.getpid(), signal.SIGTERM)
            elif Surface_576_roof_hConv_actuator_handle < 0 or \
                    Surface_582_roof_hConv_actuator_handle < 0 or Surface_588_roof_hConv_actuator_handle < 0 or \
                    Surface_594_roof_hConv_actuator_handle < 0 or Surface_600_roof_hConv_actuator_handle < 0:
                print('ovewrite_ep_weather(): HighOffice,some handle not available')
                os.getpid()
                os.kill(os.getpid(), signal.SIGTERM)

    warm_up = coordination.ep_api.exchange.warmup_flag(state)
    if not warm_up:
        if not called_vcwg_bool:
            global zone_floor_area_m2
            called_vcwg_bool = True
            Thread(target=run_vcwg).start()
        coordination.sem1.acquire()
        rh = 100*coordination.psychrometric.relative_humidity_b(state, coordination.vcwg_canTemp_K - 273.15,
                                               coordination.vcwg_canSpecHum_Ratio, coordination.vcwg_canPress_Pa)
        coordination.ep_api.exchange.set_actuator_value(state, odb_actuator_handle, coordination.vcwg_canTemp_K - 273.15)
        coordination.ep_api.exchange.set_actuator_value(state, orh_actuator_handle, rh)
        if "MediumOffice" in coordination.bld_type or 'MedOffice' in coordination.bld_type:
            coordination.ep_api.exchange.set_actuator_value(state, roof_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
        elif 'ShoeBox_HighOffice' in coordination.bld_type:
            coordination.ep_api.exchange.set_actuator_value(state, Surface_3_roof_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
        elif "HighOffice" in coordination.bld_type and "ShoeBox" not in coordination.bld_type:
            coordination.ep_api.exchange.set_actuator_value(state, Surface_576_roof_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, Surface_582_roof_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, Surface_588_roof_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, Surface_594_roof_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, Surface_600_roof_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
        coordination.sem2.release()#

def medium_get_handles(state):
    handles_dict = {}
    hvac_heat_rejection_sensor_handle = \
        coordination.ep_api.exchange.get_variable_handle(state, \
                                                         "HVAC System Total Heat Rejection Energy", \
                                                         "SIMHVAC")
    roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                        "Building_Roof")
    if hvac_heat_rejection_sensor_handle * roof_Text_handle < 0:
        print("MediumOffice_get_handles: hvac_heat_rejection_sensor_handle * roof_Text_handle < 0")
        os.getpid()
        os.kill(os.getpid(), signal.SIGTERM)
    handles_dict['simhvac'] = hvac_heat_rejection_sensor_handle
    handles_dict['roof_Text'] = roof_Text_handle

    handles_dict['floor_Text'] = []
    flr_surfaces = ['Perimeter_bot_ZN_1_Floor', 'Perimeter_bot_ZN_2_Floor', 'Perimeter_bot_ZN_3_Floor',
                    'Perimeter_bot_ZN_4_Floor', 'Core_bot_ZN_5_Floor']
    for surface in flr_surfaces:
        _tmp = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                                 surface)
        if _tmp < 0:
            print("MediumOffice_get_handles: _tmp < 0")
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)
        handles_dict['floor_Text'].append(_tmp)

    handles_dict['s_wall_Text'] = []
    handles_dict['s_wall_Solar'] = []
    handles_dict['n_wall_Text'] = []
    handles_dict['n_wall_Solar'] = []
    _levels = ['bot', 'mid', 'top']
    for level in _levels:
        _tmp_SText = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                        "Perimeter_" + level + "_ZN_1_Wall_South")
        _tmp_SSolar = coordination.ep_api.exchange.get_variable_handle(state, \
                                                                        "Surface Outside Face Incident Solar Radiation Rate per Area", \
                                                                        "Perimeter_" + level + "_ZN_1_Wall_South")
        _tmp_NText = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                        "Perimeter_" + level + "_ZN_3_Wall_North")
        _tmp_NSolar = coordination.ep_api.exchange.get_variable_handle(state, \
                                                                        "Surface Outside Face Incident Solar Radiation Rate per Area", \
                                                                        "Perimeter_" + level + "_ZN_3_Wall_North")
        if _tmp_SText * _tmp_SSolar * _tmp_NText * _tmp_NSolar < 0:
            print("MediumOffice_get_handles: _tmp_SText * _tmp_SSolar * _tmp_NText * _tmp_NSolar < 0")
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)
        handles_dict['s_wall_Text'].append(_tmp_SText)
        handles_dict['s_wall_Solar'].append(_tmp_SSolar)
        handles_dict['n_wall_Text'].append(_tmp_NText)
        handles_dict['n_wall_Solar'].append(_tmp_NSolar)
    return handles_dict

def medium_get_sensor_values(state, handleDict):
    _roof_Text_c = 0
    _floor_Text_c = 0
    _s_wall_Text_c = 0
    _s_wall_Solar_w_m2 = 0
    _n_wall_Text_c = 0
    _n_wall_Solar_w_m2 = 0

    _roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, handleDict['roof_Text'])
    for i in range(len(handleDict['floor_Text'])):
        _floor_Text_c += coordination.ep_api.exchange.get_variable_value(state, handleDict['floor_Text'][i])
    _floor_Text_c /= len(handleDict['floor_Text'])
    for i in range(len(handleDict['s_wall_Text'])):
        _s_wall_Text_c += coordination.ep_api.exchange.get_variable_value(state, handleDict['s_wall_Text'][i])
        _s_wall_Solar_w_m2 += coordination.ep_api.exchange.get_variable_value(state, handleDict['s_wall_Solar'][i])
        _n_wall_Text_c += coordination.ep_api.exchange.get_variable_value(state, handleDict['n_wall_Text'][i])
        _n_wall_Solar_w_m2 += coordination.ep_api.exchange.get_variable_value(state, handleDict['n_wall_Solar'][i])
    _s_wall_Text_c /= len(handleDict['s_wall_Text'])
    _s_wall_Solar_w_m2 /= len(handleDict['s_wall_Solar'])
    _n_wall_Text_c /= len(handleDict['n_wall_Text'])
    _n_wall_Solar_w_m2 /= len(handleDict['n_wall_Solar'])
    return _roof_Text_c, _floor_Text_c, _s_wall_Text_c, _s_wall_Solar_w_m2, _n_wall_Text_c, _n_wall_Solar_w_m2
def MediumOffice_get_ep_results(state):
    global get_ep_results_inited_handle,\
        hvac_heat_rejection_sensor_handle,medHanldesDict


    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        get_ep_results_inited_handle = True
        medHanldesDict = medium_get_handles(state)

    if called_vcwg_bool:
        global ep_last_call_time_seconds

        coordination.sem2.acquire()
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600  # Should always accumulate, since system time always advances
        accumulated_time_in_seconds = curr_sim_time_in_seconds - ep_last_call_time_seconds
        ep_last_call_time_seconds = curr_sim_time_in_seconds
        hvac_heat_rejection_J = coordination.ep_api.exchange.get_variable_value(state,medHanldesDict['simhvac'])
        hvac_waste_w_m2 = hvac_heat_rejection_J / accumulated_time_in_seconds / coordination.footprint_area_m2
        coordination.ep_sensWaste_w_m2_per_footprint_area += hvac_waste_w_m2

        time_index_alignment_bool = 1 > abs(curr_sim_time_in_seconds - coordination.vcwg_needed_time_idx_in_seconds)

        if not time_index_alignment_bool:
            coordination.sem2.release()
            return

        roof_Text_C, floor_Text_C, s_wall_Text_c, s_wall_Solar_w_m2, n_wall_Text_c, n_wall_Solar_w_m2 \
            = medium_get_sensor_values(state, medHanldesDict)

        coordination.ep_floor_Text_K = floor_Text_C + 273.15
        coordination.ep_roof_Text_K = roof_Text_C + 273.15
        if s_wall_Solar_w_m2 > n_wall_Solar_w_m2:
            coordination.ep_wallSun_Text_K = s_wall_Text_c + 273.15
            coordination.ep_wallShade_Text_K = n_wall_Text_c + 273.15
        else:
            coordination.ep_wallSun_Text_K = n_wall_Text_c + 273.15
            coordination.ep_wallShade_Text_K = s_wall_Text_c + 273.15
        coordination.sem3.release()

def ShoeBox_MedOffice_get_ep_results(state):
    global get_ep_results_inited_handle,\
        hvac_heat_rejection_sensor_handle, \
        flr_Text_handle, roof_Text_handle, \
        s_wall_Text_handle, n_wall_Text_handle

    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        get_ep_results_inited_handle = True
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,\
                                                             "HVAC System Total Heat Rejection Energy",\
                                                             "SIMHVAC")
        flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Surface 1")
        roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                            "Surface 2")
        s_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Outside Face Temperature",\
                                                                              "Surface 6")
        n_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Surface 3")
        if (hvac_heat_rejection_sensor_handle == -1 or flr_Text_handle == -1 or roof_Text_handle == -1 or \
            s_wall_Text_handle == -1 or n_wall_Text_handle == -1):
            print('ShoeBoxMedOffi_get_ep_results(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)

    # get EP results, upload to coordination
    if called_vcwg_bool:
        global ep_last_call_time_seconds

        coordination.sem2.acquire()
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600  # Should always accumulate, since system time always advances
        accumulated_time_in_seconds = curr_sim_time_in_seconds - ep_last_call_time_seconds
        ep_last_call_time_seconds = curr_sim_time_in_seconds
        hvac_heat_rejection_J = coordination.ep_api.exchange.get_variable_value(state,hvac_heat_rejection_sensor_handle)
        hvac_waste_w_m2 = hvac_heat_rejection_J / accumulated_time_in_seconds / coordination.footprint_area_m2
        coordination.ep_sensWaste_w_m2_per_footprint_area += hvac_waste_w_m2

        time_index_alignment_bool = 1 > abs(curr_sim_time_in_seconds - coordination.vcwg_needed_time_idx_in_seconds)

        if not time_index_alignment_bool:
            coordination.sem2.release()
            return

        floor_Text_C = coordination.ep_api.exchange.get_variable_value(state, flr_Text_handle)
        roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_Text_handle)
        s_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_Text_handle)
        n_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_Text_handle)

        coordination.ep_floor_Text_K = floor_Text_C + 273.15
        coordination.ep_roof_Text_K = roof_Text_c + 273.15
        coordination.ep_wallSun_Text_K = s_wall_Text_c + 273.15
        coordination.ep_wallShade_Text_K = n_wall_Text_c + 273.15

        coordination.sem3.release()


def Simplified_MedOffice_get_ep_results(state):
    global get_ep_results_inited_handle, \
        hvac_heat_rejection_sensor_handle, \
        flr_Text_handle, roof_Text_handle, \
        s_wall_1_Text_handle, n_wall_1_Text_handle, \
        s_wall_2_Text_handle, n_wall_2_Text_handle, \
        s_wall_3_Text_handle, n_wall_3_Text_handle

    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        get_ep_results_inited_handle = True
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state, \
                                                             "HVAC System Total Heat Rejection Energy", \
                                                             "SIMHVAC")
        flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                           "Surface Outside Face Temperature",
                                                                           "Surface 1")
        roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                            "Surface Outside Face Temperature",
                                                                            "Surface 14")
        s_wall_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                              "Surface Outside Face Temperature",
                                                                              "Surface 6")
        s_wall_2_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "Surface 10")
        s_wall_3_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "Surface 16")
        n_wall_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                              "Surface Outside Face Temperature",
                                                                              "Surface 3")
        n_wall_2_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "Surface 12")
        n_wall_3_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "Surface 18")
        if (hvac_heat_rejection_sensor_handle == -1 or \
                flr_Text_handle == -1 or roof_Text_handle == -1 or
                s_wall_1_Text_handle == -1 or n_wall_1_Text_handle == -1 or
        s_wall_2_Text_handle == -1 or n_wall_2_Text_handle == -1 or
        s_wall_3_Text_handle == -1 or n_wall_3_Text_handle == -1):
            print('Simplified_MedOffice_get_ep_results(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)
    # get EP results, upload to coordination
    if called_vcwg_bool:
        global ep_last_call_time_seconds
        coordination.sem2.acquire()
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600  # Should always accumulate, since system time always advances
        accumulated_time_in_seconds = curr_sim_time_in_seconds - ep_last_call_time_seconds
        ep_last_call_time_seconds = curr_sim_time_in_seconds
        hvac_heat_rejection_J = coordination.ep_api.exchange.get_variable_value(state,
                                                                                hvac_heat_rejection_sensor_handle)
        hvac_waste_w_m2 = hvac_heat_rejection_J / accumulated_time_in_seconds / coordination.footprint_area_m2
        coordination.ep_sensWaste_w_m2_per_footprint_area += hvac_waste_w_m2

        time_index_alignment_bool = 1 > abs(curr_sim_time_in_seconds - coordination.vcwg_needed_time_idx_in_seconds)

        if not time_index_alignment_bool:
            coordination.sem2.release()
            return

        flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, flr_Text_handle)
        roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_Text_handle)
        s_wall_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_1_Text_handle)
        n_wall_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_1_Text_handle)
        s_wall_2_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_2_Text_handle)
        n_wall_2_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_2_Text_handle)
        s_wall_3_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_3_Text_handle)
        n_wall_3_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_3_Text_handle)
        s_wall_Text_c = (s_wall_1_Text_c + s_wall_2_Text_c + s_wall_3_Text_c) / 3
        n_wall_Text_c = (n_wall_1_Text_c + n_wall_2_Text_c + n_wall_3_Text_c) / 3

        coordination.ep_floor_Text_K = flr_Text_c + 273.15
        coordination.ep_roof_Text_K = roof_Text_c + 273.15
        coordination.ep_wallSun_Text_K = s_wall_Text_c + 273.15
        coordination.ep_wallShade_Text_K = n_wall_Text_c + 273.15

        coordination.sem3.release()

def batch_HighOffice_wall_handles(state):
    wall_handles_dict = {}
    wall_handles_dict['south'] = []
    wall_handles_dict['north'] = []
    wall_handles_dict['east'] = []
    wall_handles_dict['west'] = []
    if 'Detailed_HighOffice' in coordination.bld_type:
        for i in range(1, 21):
            tmp_south = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                                                    "Surface " + str(2 + (i - 1) * 30))
            tmp_north = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                                                    "Surface " + str(26 + (i - 1) * 30))
            tmp_east = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                                                    "Surface " + str(14 + (i - 1) * 30))
            tmp_west = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                                                    "Surface " + str(10 + (i - 1) * 30))
            wall_handles_dict['south'].append(tmp_south)
            wall_handles_dict['north'].append(tmp_north)
            wall_handles_dict['east'].append(tmp_east)
            wall_handles_dict['west'].append(tmp_west)
    elif 'Simplified_HighOffice' in coordination.bld_type:
        # surface2_south_wall_Text_c_handle, surface302_south_wall_Text_c_handle, surface572_south_wall_Text_c_handle, \
        #     surface26_north_wall_Text_c_handle, surface326_north_wall_Text_c_handle, surface596_north_wall_Text_c_handle, \
        #     surface14_east_wall_Text_c_handle, surface314_east_wall_Text_c_handle, surface584_east_wall_Text_c_handle, \
        #     surface10_west_wall_Text_c_handle, surface310_west_wall_Text_c_handle, surface580_west_wall_Text_c_handle
        wall_handles_dict['south'].append(coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "Surface 2"))
        wall_handles_dict['south'].append(coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "Surface 302"))
        wall_handles_dict['south'].append(coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "Surface 572"))
        wall_handles_dict['north'].append(coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "Surface 26"))
        wall_handles_dict['north'].append(coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "Surface 326"))
        wall_handles_dict['north'].append(coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "Surface 596"))
        wall_handles_dict['east'].append(coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "Surface 14"))
        wall_handles_dict['east'].append(coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "Surface 314"))
        wall_handles_dict['east'].append(coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "Surface 584"))
        wall_handles_dict['west'].append(coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "Surface 10"))
        wall_handles_dict['west'].append(coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "Surface 310"))
        wall_handles_dict['west'].append(coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "Surface 580"))
    elif 'ShoeBox' in coordination.bld_type:
        wall_handles_dict['south'].append(coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "Surface 5"))
        wall_handles_dict['north'].append(coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "Surface 2"))
        wall_handles_dict['east'].append(coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "Surface 4"))
        wall_handles_dict['west'].append(coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", "Surface 6"))

    return wall_handles_dict

def batch_check_wall_handles(wall_handles_dict):
    for key in wall_handles_dict.keys():
        for i in range(len(wall_handles_dict[key])):
            if wall_handles_dict[key][i] == -1:
                print('batch_check_wall_handles(): some wall handles not available')
                os.getpid()
                os.kill(os.getpid(), signal.SIGTERM)

def batch_get_20_stories_temperatures(state, wall_handles_dict, roof_floors_handles_dict):
    #coordination.ep_api.exchange.get_variable_value(state, surface576_roof_Text_c_handle)
    wall_temperatures_dict = {}
    wall_temperatures_dict['south'] = []
    wall_temperatures_dict['north'] = []
    wall_temperatures_dict['east'] = []
    wall_temperatures_dict['west'] = []

    roof_floors_temperatures_dict = {}
    roof_floors_temperatures_dict['roof'] = []
    roof_floors_temperatures_dict['floor'] = []

    for key in wall_handles_dict.keys():
        for i in range(len(wall_handles_dict[key])):
            tmp = coordination.ep_api.exchange.get_variable_value(state, wall_handles_dict[key][i]) + 273.15
            wall_temperatures_dict[key].append(tmp)
    for key in roof_floors_handles_dict.keys():
        for i in range(len(roof_floors_handles_dict[key])):
            tmp = coordination.ep_api.exchange.get_variable_value(state, roof_floors_handles_dict[key][i]) + 273.15
            roof_floors_temperatures_dict[key].append(tmp)

    south_wall_Text_K = 0
    north_wall_Text_K = 0
    for i in range(len(wall_temperatures_dict['south'])):
        south_wall_Text_K += wall_temperatures_dict['south'][i]
        north_wall_Text_K += wall_temperatures_dict['north'][i]
    south_wall_Text_K /= len(wall_temperatures_dict['south'])
    north_wall_Text_K /= len(wall_temperatures_dict['north'])

    roof_Text_K = 0
    floor_Text_K = 0
    for i in range(len(roof_floors_temperatures_dict['roof'])):
        roof_Text_K += roof_floors_temperatures_dict['roof'][i]
        floor_Text_K += roof_floors_temperatures_dict['floor'][i]
    roof_Text_K /= len(roof_floors_temperatures_dict['roof'])
    floor_Text_K /= len(roof_floors_temperatures_dict['floor'])

    return wall_temperatures_dict, south_wall_Text_K - 273.15, north_wall_Text_K - 273.15, \
        roof_Text_K - 273.15, floor_Text_K - 273.15

def batch_highoffice_roof_floor_handels(state):
    roof_flr_dict = {}
    roof_flr_dict['roof'] = []
    roof_flr_dict['floor'] = []
    global surface1_floor_Text_c_handle
    if "ShoeBox_HighOffice" not in coordination.bld_type:
        global  surface576_roof_Text_c_handle, surface582_roof_Text_c_handle, surface588_roof_Text_c_handle, \
        surface594_roof_Text_c_handle, surface600_roof_Text_c_handle, \
        surface7_floor_Text_c_handle, surface13_floor_Text_c_handle, surface19_floor_Text_c_handle, \
        surface25_floor_Text_c_handle

        surface576_roof_Text_c_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                         "Surface Outside Face Temperature", \
                                                                                         "Surface 576")
        surface582_roof_Text_c_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                         "Surface Outside Face Temperature", \
                                                                                         "Surface 582")
        surface588_roof_Text_c_handle = coordination.ep_api.exchange. \
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 588")
        surface594_roof_Text_c_handle = coordination.ep_api.exchange. \
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 594")
        surface600_roof_Text_c_handle = coordination.ep_api.exchange. \
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 600")
        surface1_floor_Text_c_handle = coordination.ep_api.exchange. \
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 1")
        surface7_floor_Text_c_handle = coordination.ep_api.exchange. \
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 7")
        surface13_floor_Text_c_handle = coordination.ep_api.exchange. \
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 13")
        surface19_floor_Text_c_handle = coordination.ep_api.exchange. \
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 19")
        surface25_floor_Text_c_handle = coordination.ep_api.exchange. \
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 25")

        if (surface576_roof_Text_c_handle == -1 or surface582_roof_Text_c_handle == -1 or \
                surface588_roof_Text_c_handle == -1 or surface594_roof_Text_c_handle == -1 or \
                surface600_roof_Text_c_handle == -1 or surface1_floor_Text_c_handle == -1 or \
                surface7_floor_Text_c_handle == -1 or surface13_floor_Text_c_handle == -1 or \
                surface19_floor_Text_c_handle == -1 or surface25_floor_Text_c_handle == -1):
            print('20Stories_get_ep_results(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)
        roof_flr_dict['roof'].append(surface576_roof_Text_c_handle)
        roof_flr_dict['roof'].append(surface582_roof_Text_c_handle)
        roof_flr_dict['roof'].append(surface588_roof_Text_c_handle)
        roof_flr_dict['roof'].append(surface594_roof_Text_c_handle)
        roof_flr_dict['roof'].append(surface600_roof_Text_c_handle)
        roof_flr_dict['floor'].append(surface1_floor_Text_c_handle)
        roof_flr_dict['floor'].append(surface7_floor_Text_c_handle)
        roof_flr_dict['floor'].append(surface13_floor_Text_c_handle)
        roof_flr_dict['floor'].append(surface19_floor_Text_c_handle)
        roof_flr_dict['floor'].append(surface25_floor_Text_c_handle)
    else:
        global surface3_roof_Text_c_handle
        surface3_roof_Text_c_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                        "Surface Outside Face Temperature", \
                                                                                        "Surface 3")
        surface1_floor_Text_c_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                        "Surface Outside Face Temperature", \
                                                                                        "Surface 1")
        if (surface3_roof_Text_c_handle == -1 or surface1_floor_Text_c_handle == -1):
            print('20Stories_get_ep_results(): some shoebox flr roof handles not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)
        roof_flr_dict['roof'].append(surface3_roof_Text_c_handle)
        roof_flr_dict['floor'].append(surface1_floor_Text_c_handle)
    return roof_flr_dict

def _20Stories_get_ep_results(state):
    global get_ep_results_inited_handle, \
        hvac_heat_rejection_sensor_handle,wall_handles_dict,roof_floor_handles

    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        get_ep_results_inited_handle = True
        roof_floor_handles = batch_highoffice_roof_floor_handels(state)
        wall_handles_dict = batch_HighOffice_wall_handles(state)
        batch_check_wall_handles(wall_handles_dict)
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,\
                                                             "HVAC System Total Heat Rejection Energy",\
                                                             "SIMHVAC")
        if hvac_heat_rejection_sensor_handle == -1:
            print('20Stories_get_ep_results(): hvac_heat_rejection_sensor_handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)

    # get EP results, upload to coordination
    warm_up = coordination.ep_api.exchange.warmup_flag(state)
    if not warm_up and called_vcwg_bool:
        global ep_last_call_time_seconds
        coordination.sem2.acquire()
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600  # Should always accumulate, since system time always advances
        accumulated_time_in_seconds = curr_sim_time_in_seconds - ep_last_call_time_seconds
        ep_last_call_time_seconds = curr_sim_time_in_seconds
        hvac_heat_rejection_J = coordination.ep_api.exchange.get_variable_value(state,hvac_heat_rejection_sensor_handle)
        hvac_waste_w_m2 = hvac_heat_rejection_J / accumulated_time_in_seconds / coordination.footprint_area_m2
        coordination.ep_sensWaste_w_m2_per_footprint_area += hvac_waste_w_m2
        time_index_alignment_bool = 1 > abs(curr_sim_time_in_seconds - coordination.vcwg_needed_time_idx_in_seconds)
        if not time_index_alignment_bool:
            coordination.sem2.release()
            return
        print('20 Stores en_sensWaste_w_m2_per_footprint_area: ', coordination.ep_sensWaste_w_m2_per_footprint_area)
        _EP_wall_temperatures_K_dict, south_wall_Text_c, north_wall_Text_c, roof_Text_c, floor_Text_c \
            =batch_get_20_stories_temperatures(state, wall_handles_dict, roof_floor_handles)

        coordination.ep_floor_Text_K = floor_Text_c + 273.15
        coordination.ep_roof_Text_K = roof_Text_c + 273.15

        coordination.ep_wallSun_Text_K = south_wall_Text_c + 273.15
        coordination.ep_wallShade_Text_K = north_wall_Text_c + 273.15

        coordination.sem3.release()
