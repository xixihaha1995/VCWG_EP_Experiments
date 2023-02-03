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
    if "SmallOffice" in coordination.bld_type:
        global Attic_roof_west_hConv_actuator_handle, Attic_roof_east_hConv_actuator_handle, \
            Attic_roof_north_hConv_actuator_handle, Attic_roof_south_hConv_actuator_handle
    elif "MediumOffice" in coordination.bld_type or \
            'MedOffice' in coordination.bld_type:
        global roof_hConv_actuator_handle
    elif "MidriseApartment" in coordination.bld_type:
        global tRoofSWA_hConv_actuator_handle, tRoofNWA_hConv_actuator_handle, tRoofSEA_hConv_actuator_handle, \
            tRoofNEA_hConv_actuator_handle, tRoofN1A_hConv_actuator_handle, tRoofN2A_hConv_actuator_handle, \
            tRoofS1A_hConv_actuator_handle, tRoofS2A_hConv_actuator_handle, tRoofC_hConv_actuator_handle

    if not overwrite_ep_weather_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        overwrite_ep_weather_inited_handle = True
        odb_actuator_handle = coordination.ep_api.exchange.\
            get_actuator_handle(state, "Weather Data", "Outdoor Dry Bulb", "Environment")
        orh_actuator_handle = coordination.ep_api.exchange.\
            get_actuator_handle(state, "Weather Data", "Outdoor Relative Humidity", "Environment")
        if "SmallOffice" in coordination.bld_type:
            Attic_roof_west_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient",
                                    "Attic_roof_west")
            Attic_roof_east_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient",
                                    "Attic_roof_east")
            Attic_roof_north_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient",
                                    "Attic_roof_north")
            Attic_roof_south_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient",
                                    "Attic_roof_south")
        elif "MediumOffice" in coordination.bld_type or 'Detailed_MedOffice' in coordination.bld_type:
            roof_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "BUILDING_ROOF")
        elif "ShoeBox_MedOffice" in coordination.bld_type:
            roof_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "roof")
        elif 'Simplified_MedOffice' in coordination.bld_type:
            roof_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "Surface 14")
        elif "MidriseApartment" in coordination.bld_type:
            # global tRoofSWA_hConv_actuator_handle, tRoofNWA_hConv_actuator_handle, tRoofSEA_hConv_actuator_handle, \
            #     tRoofNEA_hConv_actuator_handle, tRoofN1A_hConv_actuator_handle, tRoofN2A_hConv_actuator_handle, \
            #     tRoofS1A_hConv_actuator_handle, tRoofS2A_hConv_actuator_handle, tRoofC_hConv_actuator_handle
            tRoofSWA_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "t Roof SWA")
            tRoofNWA_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "t Roof NWA")
            tRoofSEA_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "t Roof SEA")
            tRoofNEA_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "t Roof NEA")
            tRoofN1A_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "t Roof N1A")
            tRoofN2A_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "t Roof N2A")
            tRoofS1A_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "t Roof S1A")
            tRoofS2A_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "t Roof S2A")
            tRoofC_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "t Roof C")

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

        if "SmallOffice" in coordination.bld_type:
            if Attic_roof_west_hConv_actuator_handle < 0 or Attic_roof_east_hConv_actuator_handle < 0 or \
                Attic_roof_north_hConv_actuator_handle < 0 or Attic_roof_south_hConv_actuator_handle < 0:
                print('ovewrite_ep_weather():  SmallOffice, some roofhConv handle not available')
                os.getpid()
                os.kill(os.getpid(), signal.SIGTERM)
        elif "MediumOffice" in coordination.bld_type or 'MedOffice' in coordination.bld_type:
            if roof_hConv_actuator_handle < 0:
                print('ovewrite_ep_weather():  MediumOffice, some roofhConv handle not available')
                os.getpid()
                os.kill(os.getpid(), signal.SIGTERM)
        elif "MidriseApartment" in coordination.bld_type:
            if tRoofSWA_hConv_actuator_handle < 0 or tRoofNWA_hConv_actuator_handle < 0 or \
                tRoofSEA_hConv_actuator_handle < 0 or tRoofNEA_hConv_actuator_handle < 0 or \
                tRoofN1A_hConv_actuator_handle < 0 or tRoofN2A_hConv_actuator_handle < 0 or \
                tRoofS1A_hConv_actuator_handle < 0 or tRoofS2A_hConv_actuator_handle < 0 or \
                tRoofC_hConv_actuator_handle < 0:
                print('ovewrite_ep_weather():  MidriseApartment, some roofhConv handle not available')
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
        if "SmallOffice" in coordination.bld_type:
            coordination.ep_api.exchange.set_actuator_value(state, Attic_roof_west_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, Attic_roof_east_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, Attic_roof_north_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, Attic_roof_south_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
        elif "MediumOffice" in coordination.bld_type or 'MedOffice' in coordination.bld_type:
            coordination.ep_api.exchange.set_actuator_value(state, roof_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
        elif "MidriseApartment" in coordination.bld_type:
            coordination.ep_api.exchange.set_actuator_value(state, tRoofSWA_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, tRoofNWA_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, tRoofSEA_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, tRoofNEA_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, tRoofN1A_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, tRoofN2A_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, tRoofS1A_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, tRoofS2A_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, tRoofC_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
        elif 'ShoeBox_HighOffice' in coordination.bld_type:
            coordination.ep_api.exchange.set_actuator_value(state, Surface_3_roof_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
        elif "HighOffice" in coordination.bld_type and "ShoeBox" not in coordination.bld_type:
            coordination.ep_api.exchange.set_actuator_value(state, Surface_576_roof_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, Surface_582_roof_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, Surface_588_roof_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, Surface_594_roof_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
            coordination.ep_api.exchange.set_actuator_value(state, Surface_600_roof_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)

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
                                                                                "floor")
        roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",\
                                                                            "roof")
        s_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                              "Surface Outside Face Temperature",\
                                                                              "south")
        n_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,\
                                                                                    "Surface Outside Face Temperature",\
                                                                                    "north")
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

        _EP_wall_temperatures_K_dict, south_wall_Text_c, north_wall_Text_c, roof_Text_c, floor_Text_c \
            =batch_get_20_stories_temperatures(state, wall_handles_dict)

        coordination.ep_floor_Text_K = floor_Text_c + 273.15
        coordination.ep_roof_Text_K = roof_Text_c + 273.15

        coordination.ep_wallSun_Text_K = south_wall_Text_c + 273.15
        coordination.ep_wallShade_Text_K = north_wall_Text_c + 273.15

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

def MidriseApartment_get_ep_results(state):
    global get_ep_results_inited_handle, \
        hvac_heat_rejection_sensor_handle, zone_indor_temp_sensor_handle, zone_indor_spe_hum_sensor_handle, \
        gsw_flr_Text_handle, gnw_flr_Text_handle, gse_office_flr_Text_handle, gne_flr_Text_handle, \
        gn1_flr_Text_handle, gn2_flr_Text_handle, gs1_flr_Text_handle, gs2_flr_Text_handle, \
        tsw_roof_Text_handle, tnw_roof_Text_handle, tse_roof_Text_handle, tne_roof_Text_handle, \
        tn1_roof_Text_handle, tn2_roof_Text_handle, ts1_roof_Text_handle, ts2_roof_Text_handle, \
        t_cor_roof_Text_handle, \
        gsw_flr_Tint_handle, gnw_flr_Tint_handle, gse_office_flr_Tint_handle, gne_flr_Tint_handle, \
        gn1_flr_Tint_handle, gn2_flr_Tint_handle, gs1_flr_Tint_handle, gs2_flr_Tint_handle, \
        tsw_roof_Tint_handle, tnw_roof_Tint_handle, tse_roof_Tint_handle, tne_roof_Tint_handle, \
        tn1_roof_Tint_handle, tn2_roof_Tint_handle, ts1_roof_Tint_handle, ts2_roof_Tint_handle, \
        t_cor_roof_Tint_handle, \
        gsw_wall_Text_handle, gse_office_wall_Text_handle, gs1_wall_Text_handle, gs2_wall_Text_handle, \
        msw_wall_Text_handle, mse_wall_Text_handle, ms1_wall_Text_handle, ms2_wall_Text_handle, \
        tsw_wall_Text_handle, tse_wall_Text_handle, ts1_wall_Text_handle, ts2_wall_Text_handle, \
        gnw_wall_Text_handle, gne_wall_Text_handle, gn1_wall_Text_handle, gn2_wall_Text_handle, \
        mnw_wall_Text_handle, mne_wall_Text_handle, mn1_wall_Text_handle, mn2_wall_Text_handle, \
        tnw_wall_Text_handle, tne_wall_Text_handle, tn1_wall_Text_handle, tn2_wall_Text_handle, \
        gsw_wall_Tint_handle, gse_office_wall_Tint_handle, gs1_wall_Tint_handle, gs2_wall_Tint_handle, \
        msw_wall_Tint_handle, mse_wall_Tint_handle, ms1_wall_Tint_handle, ms2_wall_Tint_handle, \
        tsw_wall_Tint_handle, tse_wall_Tint_handle, ts1_wall_Tint_handle, ts2_wall_Tint_handle, \
        gnw_wall_Tint_handle, gne_wall_Tint_handle, gn1_wall_Tint_handle, gn2_wall_Tint_handle, \
        mnw_wall_Tint_handle, mne_wall_Tint_handle, mn1_wall_Tint_handle, mn2_wall_Tint_handle, \
        tnw_wall_Tint_handle, tne_wall_Tint_handle, tn1_wall_Tint_handle, tn2_wall_Tint_handle

    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        get_ep_results_inited_handle = True
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,\
                                                             "HVAC System Total Heat Rejection Energy",\
                                                             "SIMHVAC")
        gsw_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                               "Surface Outside Face Temperature",
                                                                               "g GFloor SWA")
        gnw_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                               "Surface Outside Face Temperature",
                                                                               "g GFloor NWA")
        gse_office_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                      "Surface Outside Face Temperature",
                                                                                      "g GFloor SEA")
        gne_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                               "Surface Outside Face Temperature",
                                                                               "g GFloor NEA")
        gn1_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                               "Surface Outside Face Temperature",
                                                                               "g GFloor N1A")
        gn2_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                               "Surface Outside Face Temperature",
                                                                               "g GFloor N2A")
        gs1_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                               "Surface Outside Face Temperature",
                                                                               "g GFloor S1A")
        gs2_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                               "Surface Outside Face Temperature",
                                                                               "g GFloor S2A")
        tsw_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t Roof SWA")
        tnw_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t Roof NWA")
        tse_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t Roof SEA")
        tne_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t Roof NEA")
        tn1_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t Roof N1A")
        tn2_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t Roof N2A")
        ts1_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t Roof S1A")
        ts2_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t Roof S2A")
        t_cor_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                  "Surface Outside Face Temperature",
                                                                                  "t Roof C")
        gsw_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                               "g GFloor SWA")
        gnw_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                               "g GFloor NWA")
        gse_office_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                      "Surface Inside Face Temperature",
                                                                                      "g GFloor SEA")
        gne_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                               "g GFloor NEA")
        gn1_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                               "g GFloor N1A")
        gn2_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                               "g GFloor N2A")
        gs1_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                               "g GFloor S1A")
        gs2_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                               "g GFloor S2A")
        tsw_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "t Roof SWA")
        tnw_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "t Roof NWA")
        tse_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "t Roof SEA")
        tne_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "t Roof NEA")
        tn1_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "t Roof N1A")
        tn2_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "t Roof N2A")
        ts1_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "t Roof S1A")
        ts2_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "t Roof S2A")
        t_cor_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                  "Surface Inside Face Temperature",
                                                                                  "t Roof C")

        gsw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "g SWall SWA")
        gse_office_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                       "Surface Outside Face Temperature",
                                                                                       "g SWall SEA")
        gs1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "g SWall S1A")
        gs2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "g SWall S2A")
        msw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "m SWall SWA")
        mse_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "m SWall SEA")
        ms1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "m SWall S1A")
        ms2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "m SWall S2A")
        tsw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t SWall SWA")
        tse_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t SWall SEA")
        ts1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t SWall S1A")
        ts2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t SWall S2A")
        gnw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "g NWall NWA")
        gne_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "g NWall NEA")
        gn1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "g NWall N1A")
        gn2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "g NWall N2A")
        mnw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "m NWall NWA")
        mne_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "m NWall NEA")
        mn1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "m NWall N1A")
        mn2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "m NWall N2A")
        tnw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t NWall NWA")
        tne_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t NWall NEA")
        tn1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t NWall N1A")
        tn2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Outside Face Temperature",
                                                                                "t NWall N2A")
        gsw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "g SWall SWA")
        gse_office_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                       "Surface Inside Face Temperature",
                                                                                       "g SWall SEA")
        gs1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "g SWall S1A")
        gs2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "g SWall S2A")
        msw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "m SWall SWA")
        mse_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "m SWall SEA")
        ms1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "m SWall S1A")
        ms2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "m SWall S2A")
        tsw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "t SWall SWA")
        tse_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "t SWall SEA")
        ts1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "t SWall S1A")
        ts2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "t SWall S2A")
        gnw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "g NWall NWA")
        gne_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "g NWall NEA")
        gn1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "g NWall N1A")
        gn2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "g NWall N2A")
        mnw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "m NWall NWA")
        mne_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "m NWall NEA")
        mn1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "m NWall N1A")
        mn2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "m NWall N2A")
        tnw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "t NWall NWA")
        tne_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "t NWall NEA")
        tn1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "t NWall N1A")
        tn2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                                "Surface Inside Face Temperature",
                                                                                "t NWall N2A")
        if (hvac_heat_rejection_sensor_handle == -1 or
                gsw_flr_Text_handle == -1 or gnw_flr_Text_handle == -1 or gse_office_flr_Text_handle == -1 or gne_flr_Text_handle == -1 or \
                gn1_flr_Text_handle == -1 or gn2_flr_Text_handle == -1 or gs1_flr_Text_handle == -1 or gs2_flr_Text_handle == -1 or \
                tsw_roof_Text_handle == -1 or tnw_roof_Text_handle == -1 or tse_roof_Text_handle == -1 or tne_roof_Text_handle == -1 or \
                tn1_roof_Text_handle == -1 or tn2_roof_Text_handle == -1 or ts1_roof_Text_handle == -1 or ts2_roof_Text_handle == -1 or \
                t_cor_roof_Text_handle == -1 or \
                gsw_flr_Tint_handle == -1 or gnw_flr_Tint_handle == -1 or gse_office_flr_Tint_handle == -1 or gne_flr_Tint_handle == -1 or \
                gn1_flr_Tint_handle == -1 or gn2_flr_Tint_handle == -1 or gs1_flr_Tint_handle == -1 or gs2_flr_Tint_handle == -1 or \
                tsw_roof_Tint_handle == -1 or tnw_roof_Tint_handle == -1 or tse_roof_Tint_handle == -1 or tne_roof_Tint_handle == -1 or \
                tn1_roof_Tint_handle == -1 or tn2_roof_Tint_handle == -1 or ts1_roof_Tint_handle == -1 or ts2_roof_Tint_handle == -1 or \
                t_cor_roof_Tint_handle == -1 or \
                gsw_wall_Text_handle == -1 or gse_office_wall_Text_handle == -1 or gs1_wall_Text_handle == -1 or gs2_wall_Text_handle == -1 or \
                msw_wall_Text_handle == -1 or mse_wall_Text_handle == -1 or ms1_wall_Text_handle == -1 or ms2_wall_Text_handle == -1 or \
                tsw_wall_Text_handle == -1 or tse_wall_Text_handle == -1 or ts1_wall_Text_handle == -1 or ts2_wall_Text_handle == -1 or \
                gnw_wall_Text_handle == -1 or gne_wall_Text_handle == -1 or gn1_wall_Text_handle == -1 or gn2_wall_Text_handle == -1 or \
                mnw_wall_Text_handle == -1 or mne_wall_Text_handle == -1 or mn1_wall_Text_handle == -1 or mn2_wall_Text_handle == -1 or \
                tnw_wall_Text_handle == -1 or tne_wall_Text_handle == -1 or tn1_wall_Text_handle == -1 or tn2_wall_Text_handle == -1 or \
                gsw_wall_Tint_handle == -1 or gse_office_wall_Tint_handle == -1 or gs1_wall_Tint_handle == -1 or gs2_wall_Tint_handle == -1 or \
                msw_wall_Tint_handle == -1 or mse_wall_Tint_handle == -1 or ms1_wall_Tint_handle == -1 or ms2_wall_Tint_handle == -1 or \
                tsw_wall_Tint_handle == -1 or tse_wall_Tint_handle == -1 or ts1_wall_Tint_handle == -1 or ts2_wall_Tint_handle == -1 or \
                gnw_wall_Tint_handle == -1 or gne_wall_Tint_handle == -1 or gn1_wall_Tint_handle == -1 or gn2_wall_Tint_handle == -1 or \
                mnw_wall_Tint_handle == -1 or mne_wall_Tint_handle == -1 or mn1_wall_Tint_handle == -1 or mn2_wall_Tint_handle == -1 or \
                tnw_wall_Tint_handle == -1 or tne_wall_Tint_handle == -1 or tn1_wall_Tint_handle == -1 or tn2_wall_Tint_handle == -1):
            print('MidriseApartment_get_ep_results(): some handle not available')
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

        gsw_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, gsw_flr_Text_handle)
        gnw_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, gnw_flr_Text_handle)
        gse_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, gse_office_flr_Text_handle)
        gne_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, gne_flr_Text_handle)
        gn1_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, gn1_flr_Text_handle)
        gn2_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, gn2_flr_Text_handle)
        gs1_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, gs1_flr_Text_handle)
        gs2_flr_Text_c = coordination.ep_api.exchange.get_variable_value(state, gs2_flr_Text_handle)

        gsw_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gsw_flr_Tint_handle)
        gnw_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gnw_flr_Tint_handle)
        gse_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gse_office_flr_Tint_handle)
        gne_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gne_flr_Tint_handle)
        gn1_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gn1_flr_Tint_handle)
        gn2_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gn2_flr_Tint_handle)
        gs1_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gs1_flr_Tint_handle)
        gs2_flr_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gs2_flr_Tint_handle)

        floor_Text_C = (gsw_flr_Text_c + gnw_flr_Text_c + gse_flr_Text_c + gne_flr_Text_c +
                        gn1_flr_Text_c + gn2_flr_Text_c + gs1_flr_Text_c + gs2_flr_Text_c) / 8
        floor_Tint_C = (gsw_flr_Tint_c + gnw_flr_Tint_c + gse_flr_Tint_c + gne_flr_Tint_c +
                        gn1_flr_Tint_c + gn2_flr_Tint_c + gs1_flr_Tint_c + gs2_flr_Tint_c) / 8

        tsw_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tsw_roof_Text_handle)
        tnw_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tnw_roof_Text_handle)
        tse_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tse_roof_Text_handle)
        tne_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tne_roof_Text_handle)
        tn1_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tn1_roof_Text_handle)
        tn2_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, tn2_roof_Text_handle)
        ts1_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, ts1_roof_Text_handle)
        ts2_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, ts2_roof_Text_handle)
        t_cor_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state, t_cor_roof_Text_handle)

        tsw_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tsw_roof_Tint_handle)
        tnw_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tnw_roof_Tint_handle)
        tse_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tse_roof_Tint_handle)
        tne_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tne_roof_Tint_handle)
        tn1_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tn1_roof_Tint_handle)
        tn2_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tn2_roof_Tint_handle)
        ts1_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, ts1_roof_Tint_handle)
        ts2_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, ts2_roof_Tint_handle)
        t_cor_roof_Tint_c = coordination.ep_api.exchange.get_variable_value(state, t_cor_roof_Tint_handle)

        roof_Text_C = (tsw_roof_Text_c + tnw_roof_Text_c + tse_roof_Text_c + tne_roof_Text_c +
                       tn1_roof_Text_c + tn2_roof_Text_c + ts1_roof_Text_c + ts2_roof_Text_c + t_cor_roof_Text_c) / 9
        roof_Tint_C = (tsw_roof_Tint_c + tnw_roof_Tint_c + tse_roof_Tint_c + tne_roof_Tint_c +
                       tn1_roof_Tint_c + tn2_roof_Tint_c + ts1_roof_Tint_c + ts2_roof_Tint_c + t_cor_roof_Tint_c) / 9

        gsw_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, gsw_wall_Text_handle)
        gse_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, gse_office_wall_Text_handle)
        gs1_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, gs1_wall_Text_handle)
        gs2_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, gs2_wall_Text_handle)
        msw_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, msw_wall_Text_handle)
        mse_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, mse_wall_Text_handle)
        ms1_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, ms1_wall_Text_handle)
        ms2_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, ms2_wall_Text_handle)
        tsw_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, tsw_wall_Text_handle)
        tse_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, tse_wall_Text_handle)
        ts1_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, ts1_wall_Text_handle)
        ts2_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, ts2_wall_Text_handle)

        gsw_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gsw_wall_Tint_handle)
        gse_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gse_office_wall_Tint_handle)
        gs1_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gs1_wall_Tint_handle)
        gs2_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gs2_wall_Tint_handle)
        msw_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, msw_wall_Tint_handle)
        mse_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, mse_wall_Tint_handle)
        ms1_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, ms1_wall_Tint_handle)
        ms2_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, ms2_wall_Tint_handle)
        tsw_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tsw_wall_Tint_handle)
        tse_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tse_wall_Tint_handle)
        ts1_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, ts1_wall_Tint_handle)
        ts2_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, ts2_wall_Tint_handle)

        s_wall_Text_C = (gsw_wall_Text_c + gse_wall_Text_c + gs1_wall_Text_c + gs2_wall_Text_c +
                         msw_wall_Text_c * 2 + mse_wall_Text_c * 2 + ms1_wall_Text_c * 2 + ms2_wall_Text_c * 2 +
                         tsw_wall_Text_c + tse_wall_Text_c + ts1_wall_Text_c + ts2_wall_Text_c) / 16
        s_wall_Tint_C = (gsw_wall_Tint_c + gse_wall_Tint_c + gs1_wall_Tint_c + gs2_wall_Tint_c +
                         msw_wall_Tint_c * 2 + mse_wall_Tint_c * 2 + ms1_wall_Tint_c * 2 + ms2_wall_Tint_c * 2 +
                         tsw_wall_Tint_c + tse_wall_Tint_c + ts1_wall_Tint_c + ts2_wall_Tint_c) / 16

        gnw_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, gnw_wall_Text_handle)
        gne_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, gne_wall_Text_handle)
        gn1_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, gn1_wall_Text_handle)
        gn2_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, gn2_wall_Text_handle)
        mnw_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, mnw_wall_Text_handle)
        mne_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, mne_wall_Text_handle)
        mn1_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, mn1_wall_Text_handle)
        mn2_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, mn2_wall_Text_handle)
        tnw_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, tnw_wall_Text_handle)
        tne_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, tne_wall_Text_handle)
        tn1_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, tn1_wall_Text_handle)
        tn2_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state, tn2_wall_Text_handle)

        gnw_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gnw_wall_Tint_handle)
        gne_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gne_wall_Tint_handle)
        gn1_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gn1_wall_Tint_handle)
        gn2_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, gn2_wall_Tint_handle)
        mnw_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, mnw_wall_Tint_handle)
        mne_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, mne_wall_Tint_handle)
        mn1_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, mn1_wall_Tint_handle)
        mn2_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, mn2_wall_Tint_handle)
        tnw_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tnw_wall_Tint_handle)
        tne_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tne_wall_Tint_handle)
        tn1_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tn1_wall_Tint_handle)
        tn2_wall_Tint_c = coordination.ep_api.exchange.get_variable_value(state, tn2_wall_Tint_handle)

        n_wall_Text_C = (gnw_wall_Text_c + gne_wall_Text_c + gn1_wall_Text_c + gn2_wall_Text_c +
                         mnw_wall_Text_c * 2 + mne_wall_Text_c * 2 + mn1_wall_Text_c * 2 + mn2_wall_Text_c * 2 +
                         tnw_wall_Text_c + tne_wall_Text_c + tn1_wall_Text_c + tn2_wall_Text_c) / 16
        n_wall_Tint_C = (gnw_wall_Tint_c + gne_wall_Tint_c + gn1_wall_Tint_c + gn2_wall_Tint_c +
                         mnw_wall_Tint_c * 2 + mne_wall_Tint_c * 2 + mn1_wall_Tint_c * 2 + mn2_wall_Tint_c * 2 +
                         tnw_wall_Tint_c + tne_wall_Tint_c + tn1_wall_Tint_c + tn2_wall_Tint_c) / 16

        coordination.ep_floor_Text_K = floor_Text_C + 273.15
        coordination.ep_floor_Tint_K = floor_Tint_C + 273.15

        coordination.ep_roof_Text_K = roof_Text_C + 273.15
        coordination.ep_roof_Tint_K = roof_Tint_C + 273.15

        coordination.ep_wallSun_Text_K = s_wall_Text_C + 273.15
        coordination.ep_wallSun_Tint_K = s_wall_Tint_C + 273.15
        coordination.ep_wallShade_Text_K = n_wall_Text_C + 273.15
        coordination.ep_wallShade_Tint_K = n_wall_Tint_C + 273.15

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