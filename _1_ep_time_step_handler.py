from threading import Thread
import _0_vcwg_ep_coordination as coordination
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
    csv = coordination.config['Bypass']['csv_file_name']
    ViewFactorFileName = f'{csv}_ViewFactor.txt'
    # Case name to append output file names with
    case = f'{csv}'
    '''
    epwFileName = None
    TopForcingFileName = 'Vancouver2008_ERA5_Jul.csv'
    VCWGParamFileName = 'initialize_Vancouver_LCZ1_2.uwg'
    ViewFactorFileName = 'viewfactor_Vancouver.txt'
    # Case name to append output file names with
    case = 'Vancouver_LCZ1'
    '''
    '''
    epwFileName = 'Guelph_2018.epw'
    TopForcingFileName = None
    VCWGParamFileName = 'initialize_Guelph.uwg'
    ViewFactorFileName = 'viewfactor_Guelph.txt'
    # Case name to append output file names with
    case = 'Guelph_2018'
    '''
    # Initialize the UWG object and run the simulation
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()

def overwrite_ep_weather(state):
    global overwrite_ep_weather_inited_handle, odb_actuator_handle, orh_actuator_handle, \
        wsped_mps_actuator_handle, wdir_deg_actuator_handle,zone_flr_area_handle,\
        called_vcwg_bool, roof_hConv_actuator_handle


    if not overwrite_ep_weather_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        overwrite_ep_weather_inited_handle = True
        odb_actuator_handle = coordination.ep_api.exchange.\
            get_actuator_handle(state, "Weather Data", "Outdoor Dry Bulb", "Environment")
        orh_actuator_handle = coordination.ep_api.exchange.\
            get_actuator_handle(state, "Weather Data", "Outdoor Relative Humidity", "Environment")
        roof_hConv_actuator_handle = coordination.ep_api.exchange. \
            get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                "BUILDING_ROOF")
        oat_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state, "Site Outdoor Air Drybulb Temperature", "Environment")
        orh_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state, "Site Outdoor Air Humidity Ratio","Environment")
    # zone_flr_area_handle =  coordination.ep_api.exchange.get_internal_variable_handle(state, "Zone Floor Area", "CORE_ZN")
        #if one of the above handles is less than 0, then the actuator is not available
        # the entire program (multithread cooperation) should be terminated here, system exit with print messagePYTHO
        #if odb_actuator_handle < 0 or orh_actuator_handle < 0 or zone_flr_area_handle < 0:
        if odb_actuator_handle < 0 or orh_actuator_handle < 0 or roof_hConv_actuator_handle < 0:
            print('ovewrite_ep_weather(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)

    warm_up = coordination.ep_api.exchange.warmup_flag(state)
    if not warm_up:
        if not called_vcwg_bool:
            global zone_floor_area_m2
            #zone_floor_area_m2 = coordination.ep_api.exchange.get_internal_variable_value(state, zone_flr_area_handle)
            called_vcwg_bool = True
            Thread(target=run_vcwg).start()
        # Wait for the upstream (VCWG upload canyon info to Parent) to finish
        coordination.sem1.acquire()
        # EP download the canyon info from Parent
        #psychrometric = coordination.ep_api.functional.psychrometrics(state)
        rh = 100*coordination.psychrometric.relative_humidity_b(state, coordination.vcwg_canTemp_K - 273.15,
                                               coordination.vcwg_canSpecHum_Ratio, coordination.vcwg_canPress_Pa)
        coordination.ep_api.exchange.set_actuator_value(state, odb_actuator_handle, coordination.vcwg_canTemp_K - 273.15)
        coordination.ep_api.exchange.set_actuator_value(state, orh_actuator_handle, rh)
        coordination.ep_api.exchange.set_actuator_value(state, roof_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
        coordination.sem2.release()#

def SmallOffice_get_ep_results(state):
    global get_ep_results_inited_handle, oat_sensor_handle, \
        hvac_heat_rejection_sensor_handle, elec_bld_meter_handle, \
        zone_flr_area_handle,zone_indor_temp_sensor_handle, zone_indor_spe_hum_sensor_handle, \
        sens_cool_demand_sensor_handle, sens_heat_demand_sensor_handle, \
        cool_consumption_sensor_handle, heat_consumption_sensor_handle, \
        core_flr_Text_handle, pre1_flr_Text_handle, pre2_flr_Text_handle, \
        pre3_flr_Text_handle, pre4_flr_Text_handle, \
        core_flr_Tint_handle, pre1_flr_Tint_handle, pre2_flr_Tint_handle, \
        pre3_flr_Tint_handle, pre4_flr_Tint_handle, \
        roof_west_Text_handle, roof_east_Text_handle, roof_north_Text_handle, roof_south_Text_handle,\
        roof_west_Tint_handle, roof_east_Tint_handle, roof_north_Tint_handle, roof_south_Tint_handle,\
        s_wall_Text_handle, n_wall_Text_handle, \
        s_wall_Tint_handle, n_wall_Tint_handle, \
        s_wall_Solar_handle, n_wall_Solar_handle

    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        get_ep_results_inited_handle = True

        oat_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                             "Site Outdoor Air Drybulb Temperature",\
                                                                             "Environment")
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,\
                                                             "HVAC System Total Heat Rejection Energy",\
                                                             "SIMHVAC")
        elec_bld_meter_handle = coordination.ep_api.exchange.get_meter_handle(state, "Electricity:Building")
        zone_flr_area_handle =  coordination.ep_api.exchange.get_internal_variable_handle(state, "Zone Floor Area",\
                                                                          "CORE_ZN")
        zone_indor_temp_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state, "Zone Air Temperature",\
                                                                                         "CORE_ZN")
        zone_indor_spe_hum_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                            "Zone Air Humidity Ratio",\
                                                                                            "CORE_ZN")
        sens_cool_demand_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                          "Zone Air System Sensible Cooling Rate",\
                                                                                          "CORE_ZN")
        sens_heat_demand_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                          "Zone Air System Sensible Heating Rate",\
                                                                                          "CORE_ZN")
        cool_consumption_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                          "Cooling Coil Electricity Rate",\
                                                                                          "PSZ-AC:1_COOLC DXCOIL")
        heat_consumption_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                          "Heating Coil Heating Rate",\
                                                                                          "PSZ-AC:1_HEATC")
        core_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Core_ZN_floor")
        pre1_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Perimeter_ZN_1_floor")
        pre2_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Perimeter_ZN_2_floor")
        pre3_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Perimeter_ZN_3_floor")
        pre4_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Perimeter_ZN_4_floor")
        roof_west_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                 "Surface Outside Face Temperature",\
                                                                                 "Attic_roof_west")
        roof_east_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                 "Surface Outside Face Temperature",\
                                                                                 "Attic_roof_east")
        roof_north_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                  "Surface Outside Face Temperature",\
                                                                                  "Attic_roof_north")
        roof_south_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                  "Surface Outside Face Temperature",\
                                                                                  "Attic_roof_south")
        s_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Outside Face Temperature",\
                                                                              "Perimeter_ZN_1_wall_south")
        n_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Outside Face Temperature",\
                                                                              "Perimeter_ZN_3_wall_north")
        s_wall_Solar_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                "Surface Outside Face Incident Solar Radiation Rate per Area",\
                                                                                "Perimeter_ZN_1_wall_south")
        n_wall_Solar_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                            "Surface Outside Face Incident Solar Radiation Rate per Area",\
                                                                            "Perimeter_ZN_3_wall_north")
        core_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Core_ZN_floor")
        pre1_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_ZN_1_floor")
        pre2_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_ZN_2_floor")
        pre3_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_ZN_3_floor")
        pre4_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_ZN_4_floor")
        roof_west_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                 "Surface Inside Face Temperature",\
                                                                                 "Attic_roof_west")
        roof_east_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                 "Surface Inside Face Temperature",\
                                                                                 "Attic_roof_east")
        roof_north_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                "Surface Inside Face Temperature",\
                                                                                "Attic_roof_north")
        roof_south_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                "Surface Inside Face Temperature",\
                                                                                "Attic_roof_south")
        s_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Inside Face Temperature",\
                                                                              "Perimeter_ZN_1_wall_south")
        n_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Inside Face Temperature",\
                                                                              "Perimeter_ZN_3_wall_north")
        core_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Core_ZN_floor")
        pre1_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_ZN_1_floor")
        pre2_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_ZN_2_floor")
        pre3_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_ZN_3_floor")
        pre4_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_ZN_4_floor")
        roof_west_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                 "Surface Inside Face Temperature",\
                                                                                 "Attic_roof_west")
        roof_east_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                 "Surface Inside Face Temperature",\
                                                                                 "Attic_roof_east")
        roof_north_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                "Surface Inside Face Temperature",\
                                                                                "Attic_roof_north")
        roof_south_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                "Surface Inside Face Temperature",\
                                                                                "Attic_roof_south")
        s_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Inside Face Temperature",\
                                                                              "Perimeter_ZN_1_wall_south")
        n_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Inside Face Temperature",\
                                                                              "Perimeter_ZN_3_wall_north")
        if (oat_sensor_handle == -1 or hvac_heat_rejection_sensor_handle == -1 or\
                elec_bld_meter_handle == -1 or zone_indor_temp_sensor_handle == -1 or\
                zone_indor_spe_hum_sensor_handle == -1 or\
                sens_cool_demand_sensor_handle == -1 or sens_heat_demand_sensor_handle == -1 or\
                cool_consumption_sensor_handle == -1 or heat_consumption_sensor_handle == -1 or\
                core_flr_Text_handle == -1 or pre1_flr_Text_handle == -1 or pre2_flr_Text_handle == -1 or\
                pre3_flr_Text_handle == -1 or pre4_flr_Text_handle == -1 or roof_west_Text_handle == -1 or\
                roof_east_Text_handle == -1 or roof_north_Text_handle == -1 or roof_south_Text_handle == -1 or\
                s_wall_Text_handle == -1 or n_wall_Text_handle == -1 or s_wall_Solar_handle == -1 or\
                n_wall_Solar_handle == -1 or core_flr_Tint_handle == -1 or pre1_flr_Tint_handle == -1 or\
                pre2_flr_Tint_handle == -1 or pre3_flr_Tint_handle == -1 or pre4_flr_Tint_handle == -1 or\
                roof_west_Tint_handle == -1 or roof_east_Tint_handle == -1 or roof_north_Tint_handle == -1 or\
                roof_south_Tint_handle == -1 or s_wall_Tint_handle == -1 or n_wall_Tint_handle == -1 or\
                s_wall_Solar_handle == -1 or n_wall_Solar_handle == -1):
            print('smallOffice_get_ep_results(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)

    # get EP results, upload to coordination
    if called_vcwg_bool:
        global ep_last_call_time_seconds, zone_floor_area_m2
        zone_floor_area_m2 = coordination.ep_api.exchange.get_internal_variable_value(state, zone_flr_area_handle)
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

        zone_indor_temp_value = coordination.ep_api.exchange.get_variable_value(state, zone_indor_temp_sensor_handle)
        zone_indor_spe_hum_value = coordination.ep_api.exchange.get_variable_value(state,\
                                                                                   zone_indor_spe_hum_sensor_handle)
        sens_cool_demand_w_value = coordination.ep_api.exchange.get_variable_value(state,\
                                                                                   sens_cool_demand_sensor_handle)
        sens_cool_demand_w_m2_value = sens_cool_demand_w_value / zone_floor_area_m2
        sens_heat_demand_w_value = coordination.ep_api.exchange.get_variable_value(state,\
                                                                                   sens_heat_demand_sensor_handle)
        sens_heat_demand_w_m2_value = sens_heat_demand_w_value / zone_floor_area_m2
        cool_consumption_w_value = coordination.ep_api.exchange.get_variable_value(state,\
                                                                                   cool_consumption_sensor_handle)
        cool_consumption_w_m2_value = cool_consumption_w_value / zone_floor_area_m2
        heat_consumption_w_value = coordination.ep_api.exchange.get_variable_value(state,\
                                                                                   heat_consumption_sensor_handle)
        heat_consumption_w_m2_value = heat_consumption_w_value / zone_floor_area_m2

        elec_bld_meter_j_hourly = coordination.ep_api.exchange.get_variable_value(state, elec_bld_meter_handle)
        elec_bld_meter_w_m2 = elec_bld_meter_j_hourly / 3600 / coordination.footprint_area_m2

        core_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, core_flr_Text_handle)
        pre1_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, pre1_flr_Text_handle)
        pre2_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, pre2_flr_Text_handle)
        pre3_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, pre3_flr_Text_handle)
        pre4_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, pre4_flr_Text_handle)

        roof_west_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_west_Text_handle)
        roof_east_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_east_Text_handle)
        roof_north_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_north_Text_handle)
        roof_south_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_south_Text_handle)

        s_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_Text_handle)
        n_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_Text_handle)

        core_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, core_flr_Tint_handle)
        pre1_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, pre1_flr_Tint_handle)
        pre2_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, pre2_flr_Tint_handle)
        pre3_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, pre3_flr_Tint_handle)
        pre4_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, pre4_flr_Tint_handle)

        roof_west_Tint_c = coordination.ep_api.exchange.get_variable_value(state, roof_west_Tint_handle)
        roof_east_Tint_c = coordination.ep_api.exchange.get_variable_value(state, roof_east_Tint_handle)
        roof_north_Tint_c = coordination.ep_api.exchange.get_variable_value(state, roof_north_Tint_handle)
        roof_south_Tint_c = coordination.ep_api.exchange.get_variable_value(state, roof_south_Tint_handle)

        s_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_Tint_handle)
        n_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_Tint_handle)

        s_wall_Solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, s_wall_Solar_handle)
        n_wall_Solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, n_wall_Solar_handle)

        coordination.ep_elecTotal_w_m2_per_floor_area = elec_bld_meter_w_m2
        coordination.ep_indoorTemp_C = zone_indor_temp_value
        coordination.ep_indoorHum_Ratio = zone_indor_spe_hum_value
        coordination.ep_sensCoolDemand_w_m2 = sens_cool_demand_w_m2_value
        coordination.ep_sensHeatDemand_w_m2 = sens_heat_demand_w_m2_value
        coordination.ep_coolConsump_w_m2 = cool_consumption_w_m2_value
        coordination.ep_heatConsump_w_m2 = heat_consumption_w_m2_value

        oat_temp_c = coordination.ep_api.exchange.get_variable_value(state, oat_sensor_handle)
        coordination.overwriten_time_index = curr_sim_time_in_seconds
        coordination.ep_oaTemp_C = oat_temp_c

        floor_Text_C =(core_flr_Text_c + pre1_flr_Text_c + pre2_flr_Text_c + pre3_flr_Text_c + pre4_flr_Text_c) / 5
        roof_Text_C = (roof_west_Text_c + roof_east_Text_c + roof_north_Text_c + roof_south_Text_c) / 4
        floor_Tint_C = (core_flr_Tint_c + pre1_flr_Tint_c + pre2_flr_Tint_c + pre3_flr_Tint_c + pre4_flr_Tint_c) / 5
        roof_Tint_C = (roof_west_Tint_c + roof_east_Tint_c + roof_north_Tint_c + roof_south_Tint_c) / 4

        coordination.ep_floor_Text_K = floor_Text_C + 273.15
        coordination.ep_floor_Tint_K = floor_Tint_C + 273.15

        coordination.ep_roof_Text_K = roof_Text_C + 273.15
        coordination.ep_roof_Tint_K = roof_Tint_C + 273.15

        if s_wall_Solar_w_m2 > n_wall_Solar_w_m2:
            coordination.ep_wallSun_Text_K = s_wall_Text_c + 273.15
            coordination.ep_wallSun_Tint_K = s_wall_Tint_c + 273.15
            coordination.ep_wallShade_Text_K = n_wall_Text_c + 273.15
            coordination.ep_wallShade_Tint_K = n_wall_Tint_c + 273.15
        else:
            coordination.ep_wallSun_Text_K = n_wall_Text_c + 273.15
            coordination.ep_wallSun_Tint_K = n_wall_Tint_c + 273.15
            coordination.ep_wallShade_Text_K = s_wall_Text_c + 273.15
            coordination.ep_wallShade_Tint_K = s_wall_Tint_c + 273.15

        coordination.sem3.release()

def MediumOffice_get_ep_results(state):
    global get_ep_results_inited_handle, oat_sensor_handle, \
        hvac_heat_rejection_sensor_handle, elec_bld_meter_handle, zone_flr_area_handle, \
        zone_indor_temp_sensor_handle, zone_indor_spe_hum_sensor_handle, \
        sens_cool_demand_sensor_handle, sens_heat_demand_sensor_handle, \
        cool_consumption_sensor_handle, heat_consumption_sensor_handle, \
        flr_pre1_Text_handle, flr_pre2_Text_handle, flr_pre3_Text_handle, flr_pre4_Text_handle, \
        flr_core_Text_handle, \
        roof_Text_handle, \
        s_wall_bot_1_Text_handle, s_wall_mid_1_Text_handle, s_wall_top_1_Text_handle, \
        n_wall_bot_1_Text_handle, n_wall_mid_1_Text_handle, n_wall_top_1_Text_handle, \
        s_wall_bot_1_Solar_handle, s_wall_mid_1_Solar_handle, s_wall_top_1_Solar_handle, \
        n_wall_bot_1_Solar_handle, n_wall_mid_1_Solar_handle, n_wall_top_1_Solar_handle, \
        flr_pre1_Tint_handle, flr_pre2_Tint_handle, flr_pre3_Tint_handle, flr_pre4_Tint_handle, \
        flr_core_Tint_handle, \
        roof_Tint_handle, \
        s_wall_bot_1_Tint_handle, s_wall_mid_1_Tint_handle, s_wall_top_1_Tint_handle, \
        n_wall_bot_1_Tint_handle, n_wall_mid_1_Tint_handle, n_wall_top_1_Tint_handle

    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        get_ep_results_inited_handle = True
        oat_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                             "Site Outdoor Air Drybulb Temperature",\
                                                                             "Environment")
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,\
                                                             "HVAC System Total Heat Rejection Energy",\
                                                             "SIMHVAC")
        elec_bld_meter_handle = coordination.ep_api.exchange.get_meter_handle(state, "Electricity:Building")
        zone_flr_area_handle =  coordination.ep_api.exchange.get_internal_variable_handle(state, "Zone Floor Area",\
                                                                          "CORE_MID")
        zone_indor_temp_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state, "Zone Air Temperature",\
                                                                                         "CORE_MID")
        zone_indor_spe_hum_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                            "Zone Air Humidity Ratio",\
                                                                                            "CORE_MID")
        sens_cool_demand_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                          "Zone Air System Sensible Cooling Rate",\
                                                                                          "CORE_MID")
        sens_heat_demand_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                          "Zone Air System Sensible Heating Rate",\
                                                                                          "CORE_MID")
        cool_consumption_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                          "Cooling Coil Electricity Rate",\
                                                                                          "VAV_2_COOLC DXCOIL")
        heat_consumption_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                          "Heating Coil Heating Rate",\
                                                                                          "CORE_MID VAV BOX REHEAT COIL")
        flr_pre1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Perimeter_bot_ZN_1_Floor")
        flr_pre2_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Perimeter_bot_ZN_2_Floor")
        flr_pre3_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Perimeter_bot_ZN_3_Floor")
        flr_pre4_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Perimeter_bot_ZN_4_Floor")
        flr_core_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                                "Core_bot_ZN_5_Floor")
        roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                            "Building_Roof")
        s_wall_bot_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Outside Face Temperature",\
                                                                              "Perimeter_bot_ZN_1_Wall_South")
        s_wall_mid_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Perimeter_mid_ZN_1_Wall_South")
        s_wall_top_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Perimeter_top_ZN_1_Wall_South")
        n_wall_bot_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Perimeter_bot_ZN_3_Wall_North")
        n_wall_mid_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Perimeter_mid_ZN_3_Wall_North")
        n_wall_top_1_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "Perimeter_top_ZN_3_Wall_North")
        s_wall_bot_1_Solar_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                     "Surface Outside Face Incident Solar Radiation Rate per Area",\
                                                                                     "Perimeter_bot_ZN_1_Wall_South")
        s_wall_mid_1_Solar_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                     "Surface Outside Face Incident Solar Radiation Rate per Area",\
                                                                                     "Perimeter_mid_ZN_1_Wall_South")
        s_wall_top_1_Solar_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                     "Surface Outside Face Incident Solar Radiation Rate per Area",\
                                                                                     "Perimeter_top_ZN_1_Wall_South")
        n_wall_bot_1_Solar_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                     "Surface Outside Face Incident Solar Radiation Rate per Area",\
                                                                                     "Perimeter_bot_ZN_3_Wall_North")
        n_wall_mid_1_Solar_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                     "Surface Outside Face Incident Solar Radiation Rate per Area",\
                                                                                     "Perimeter_mid_ZN_3_Wall_North")
        n_wall_top_1_Solar_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                     "Surface Outside Face Incident Solar Radiation Rate per Area",\
                                                                                     "Perimeter_top_ZN_3_Wall_North")
        flr_pre1_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_bot_ZN_1_Floor")
        flr_pre2_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_bot_ZN_2_Floor")
        flr_pre3_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_bot_ZN_3_Floor")
        flr_pre4_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Perimeter_bot_ZN_4_Floor")
        flr_core_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                                "Core_bot_ZN_5_Floor")
        roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",\
                                                                            "Building_Roof")
        s_wall_bot_1_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Inside Face Temperature",\
                                                                                    "Perimeter_bot_ZN_1_Wall_South")
        s_wall_mid_1_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Inside Face Temperature",\
                                                                                    "Perimeter_mid_ZN_1_Wall_South")
        s_wall_top_1_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Inside Face Temperature",\
                                                                                    "Perimeter_top_ZN_1_Wall_South")
        n_wall_bot_1_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Inside Face Temperature",\
                                                                                    "Perimeter_bot_ZN_3_Wall_North")
        n_wall_mid_1_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Inside Face Temperature",\
                                                                                    "Perimeter_mid_ZN_3_Wall_North")
        n_wall_top_1_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Inside Face Temperature",\
                                                                                    "Perimeter_top_ZN_3_Wall_North")
        if (oat_sensor_handle == -1 or hvac_heat_rejection_sensor_handle == -1 or zone_flr_area_handle == -1 or\
                elec_bld_meter_handle == -1 or zone_indor_temp_sensor_handle == -1 or\
                zone_indor_spe_hum_sensor_handle == -1 or\
                sens_cool_demand_sensor_handle == -1 or sens_heat_demand_sensor_handle == -1 or\
                cool_consumption_sensor_handle == -1 or heat_consumption_sensor_handle == -1 or\
                flr_pre1_Text_handle == -1 or flr_pre2_Text_handle == -1 or flr_pre3_Text_handle == -1 or\
                flr_pre4_Text_handle == -1 or flr_core_Text_handle == -1 or roof_Text_handle == -1 or\
                s_wall_bot_1_Text_handle == -1 or s_wall_mid_1_Text_handle == -1 or s_wall_top_1_Text_handle == -1 or\
                n_wall_bot_1_Text_handle == -1 or n_wall_mid_1_Text_handle == -1 or n_wall_top_1_Text_handle == -1 or\
                s_wall_bot_1_Solar_handle == -1 or s_wall_mid_1_Solar_handle == -1 or s_wall_top_1_Solar_handle == -1 or\
                n_wall_bot_1_Solar_handle == -1 or n_wall_mid_1_Solar_handle == -1 or n_wall_top_1_Solar_handle == -1 or\
                flr_pre1_Tint_handle == -1 or flr_pre2_Tint_handle == -1 or flr_pre3_Tint_handle == -1 or\
                flr_pre4_Tint_handle == -1 or flr_core_Tint_handle == -1 or roof_Tint_handle == -1 or\
                s_wall_bot_1_Tint_handle == -1 or s_wall_mid_1_Tint_handle == -1 or s_wall_top_1_Tint_handle == -1 or\
                n_wall_bot_1_Tint_handle == -1 or n_wall_mid_1_Tint_handle == -1 or n_wall_top_1_Tint_handle == -1):
            print('mediumOffice_get_ep_results(): some handle not available')
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

        coordination.ep_indoorTemp_C = coordination.ep_api.exchange.get_variable_value(state, zone_indor_temp_sensor_handle)
        coordination.ep_indoorHum_Ratio = coordination.ep_api.exchange.get_variable_value(state,
                                                                                   zone_indor_spe_hum_sensor_handle)

        flr_core_Text_c = coordination.ep_api.exchange.get_variable_value(state, flr_core_Text_handle)
        flr_pre1_Text_c = coordination.ep_api.exchange.get_variable_value(state, flr_pre1_Text_handle)
        flr_pre2_Text_c = coordination.ep_api.exchange.get_variable_value(state, flr_pre2_Text_handle)
        flr_pre3_Text_c = coordination.ep_api.exchange.get_variable_value(state, flr_pre3_Text_handle)
        flr_pre4_Text_c = coordination.ep_api.exchange.get_variable_value(state, flr_pre4_Text_handle)
        roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, roof_Text_handle)

        s_wall_bot_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_bot_1_Text_handle)
        s_wall_mid_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_mid_1_Text_handle)
        s_wall_top_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_top_1_Text_handle)
        n_wall_bot_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_bot_1_Text_handle)
        n_wall_mid_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_mid_1_Text_handle)
        n_wall_top_1_Text_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_top_1_Text_handle)


        flr_core_Tint_c = coordination.ep_api.exchange.get_variable_value(state, flr_core_Tint_handle)
        flr_pre1_Tint_c = coordination.ep_api.exchange.get_variable_value(state, flr_pre1_Tint_handle)
        flr_pre2_Tint_c = coordination.ep_api.exchange.get_variable_value(state, flr_pre2_Tint_handle)
        flr_pre3_Tint_c = coordination.ep_api.exchange.get_variable_value(state, flr_pre3_Tint_handle)
        flr_pre4_Tint_c = coordination.ep_api.exchange.get_variable_value(state, flr_pre4_Tint_handle)
        roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, roof_Tint_handle)

        s_wall_bot_1_Tint_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_bot_1_Tint_handle)
        s_wall_mid_1_Tint_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_mid_1_Tint_handle)
        s_wall_top_1_Tint_c = coordination.ep_api.exchange.get_variable_value(state, s_wall_top_1_Tint_handle)
        n_wall_bot_1_Tint_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_bot_1_Tint_handle)
        n_wall_mid_1_Tint_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_mid_1_Tint_handle)
        n_wall_top_1_Tint_c = coordination.ep_api.exchange.get_variable_value(state, n_wall_top_1_Tint_handle)

        s_wall_bot_1_Solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, s_wall_bot_1_Solar_handle)
        s_wall_mid_1_Solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, s_wall_mid_1_Solar_handle)
        s_wall_top_1_Solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, s_wall_top_1_Solar_handle)
        n_wall_bot_1_Solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, n_wall_bot_1_Solar_handle)
        n_wall_mid_1_Solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, n_wall_mid_1_Solar_handle)
        n_wall_top_1_Solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, n_wall_top_1_Solar_handle)

        floor_Text_C = (flr_core_Text_c + flr_pre1_Text_c + flr_pre2_Text_c + flr_pre3_Text_c + flr_pre4_Text_c )/5
        floor_Tint_C = (flr_core_Tint_c + flr_pre1_Tint_c + flr_pre2_Tint_c + flr_pre3_Tint_c + flr_pre4_Tint_c )/5

        coordination.ep_floor_Text_K = floor_Text_C + 273.15
        coordination.ep_floor_Tint_K = floor_Tint_C + 273.15

        coordination.ep_roof_Text_K = roof_Text_c + 273.15
        coordination.ep_roof_Tint_K = roof_Tint_c + 273.15

        s_wall_Solar_w_m2 = (s_wall_bot_1_Solar_w_m2 + s_wall_mid_1_Solar_w_m2 + s_wall_top_1_Solar_w_m2)/3
        n_wall_Solar_w_m2 = (n_wall_bot_1_Solar_w_m2 + n_wall_mid_1_Solar_w_m2 + n_wall_top_1_Solar_w_m2)/3

        s_wall_Text_c = (s_wall_bot_1_Text_c + s_wall_mid_1_Text_c + s_wall_top_1_Text_c)/3
        s_wall_Tint_c = (s_wall_bot_1_Tint_c + s_wall_mid_1_Tint_c + s_wall_top_1_Tint_c)/3
        n_wall_Text_c = (n_wall_bot_1_Text_c + n_wall_mid_1_Text_c + n_wall_top_1_Text_c)/3
        n_wall_Tint_c = (n_wall_bot_1_Tint_c + n_wall_mid_1_Tint_c + n_wall_top_1_Tint_c)/3

        if s_wall_Solar_w_m2 > n_wall_Solar_w_m2:
            coordination.ep_wallSun_Text_K = s_wall_Text_c + 273.15
            coordination.ep_wallSun_Tint_K = s_wall_Tint_c + 273.15
            coordination.ep_wallShade_Text_K = n_wall_Text_c + 273.15
            coordination.ep_wallShade_Tint_K = n_wall_Tint_c + 273.15
        else:
            coordination.ep_wallSun_Text_K = n_wall_Text_c + 273.15
            coordination.ep_wallSun_Tint_K = n_wall_Tint_c + 273.15
            coordination.ep_wallShade_Text_K = s_wall_Text_c + 273.15
            coordination.ep_wallShade_Tint_K = s_wall_Tint_c + 273.15

        coordination.sem3.release()

def LargeOffice_get_ep_results(state):
    global get_ep_results_inited_handle, \
        hvac_heat_rejection_sensor_handle, zone_indor_temp_sensor_handle, zone_indor_spe_hum_sensor_handle, \
        sens_cool_demand_sensor_handle, sens_heat_demand_sensor_handle, \
        cool_consumption_sensor_handle, heat_consumption_sensor_handle, \
        flr_pre1_Text_handle, flr_pre2_Text_handle, flr_pre3_Text_handle, flr_pre4_Text_handle, \
        flr_core_Text_handle, \
        roof_Text_handle, \
        s_wall_bot_1_Text_handle, s_wall_mid_1_Text_handle, s_wall_top_1_Text_handle, \
        n_wall_bot_1_Text_handle, n_wall_mid_1_Text_handle, n_wall_top_1_Text_handle, \
        s_wall_bot_1_Solar_handle, s_wall_mid_1_Solar_handle, s_wall_top_1_Solar_handle, \
        n_wall_bot_1_Solar_handle, n_wall_mid_1_Solar_handle, n_wall_top_1_Solar_handle, \
        flr_pre1_Tint_handle, flr_pre2_Tint_handle, flr_pre3_Tint_handle, flr_pre4_Tint_handle, \
        flr_core_Tint_handle, \
        roof_Tint_handle, \
        s_wall_bot_1_Tint_handle, s_wall_mid_1_Tint_handle, s_wall_top_1_Tint_handle, \
        n_wall_bot_1_Tint_handle, n_wall_mid_1_Tint_handle, n_wall_top_1_Tint_handle

    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        get_ep_results_inited_handle = True
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,\
                                                             "HVAC System Total Heat Rejection Energy",\
                                                             "SIMHVAC")
        zone_indor_temp_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state, "Zone Air Temperature", \
                                                                                         "CORE_MID")
        zone_indor_spe_hum_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state, \
                                                                                            "Zone Air Humidity Ratio", \
                                                                                            "CORE_MID")

        if (hvac_heat_rejection_sensor_handle == -1 or \
                zone_indor_temp_sensor_handle == -1 or\
                zone_indor_spe_hum_sensor_handle == -1):
            print('LargeOffice_get_ep_results(): some handle not available')
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

        coordination.ep_indoorTemp_C = coordination.ep_api.exchange.get_variable_value(state, zone_indor_temp_sensor_handle)
        coordination.ep_indoorHum_Ratio = coordination.ep_api.exchange.get_variable_value(state,
                                                                                   zone_indor_spe_hum_sensor_handle)
        coordination.sem3.release()

def general_get_ep_results(state):
    global get_ep_results_inited_handle, \
        hvac_heat_rejection_sensor_handle, zone_indor_temp_sensor_handle, zone_indor_spe_hum_sensor_handle

    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        get_ep_results_inited_handle = True
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,\
                                                             "HVAC System Total Heat Rejection Energy",\
                                                             "SIMHVAC")
        if (hvac_heat_rejection_sensor_handle == -1 ):
            print('general_get_ep_results(): some handle not available')
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
        coordination.sem3.release()