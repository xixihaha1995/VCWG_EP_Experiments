from threading import Thread
import _2_vcwg_ep_coordination as coordination
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
    ViewFactorFileName = f'{coordination.bld_type }_{coordination.value}_ViewFactor.txt'
    # Case name to append output file names with
    case = f'{coordination.value}'
    # Initialize the UWG object and run the simulation
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()

def to_get_wet_bulb(state, dry_bulb_temp_C, humidity_ratio, barometric_pressure_Pa):
    _wetbulb = coordination.psychrometric.wet_bulb(state, dry_bulb_temp_C, humidity_ratio, barometric_pressure_Pa)
    return _wetbulb

def medOfficeGetAirNodeHandles(state):
    flrs = ['BOT', 'MID', 'TOP']
    handles = {}
    handles['odb'] = []
    handles['owb'] = []
    for flr in flrs:
        tmp_odb_handle = coordination.ep_api.exchange. \
            get_actuator_handle(state, "Schedule:Compact", "Schedule Value", f"OUTDOORAIRNODE:{flr}DRYBULB")
        tmp_owb_handle = coordination.ep_api.exchange. \
            get_actuator_handle(state, "Schedule:Compact", "Schedule Value", f"OUTDOORAIRNODE:{flr}WETBULB")
        if tmp_odb_handle * tmp_owb_handle < 0:
            print('ovewrite_ep_weather(): MediumOffice,some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)

        handles['odb'].append(tmp_odb_handle)
        handles['owb'].append(tmp_owb_handle)
    return handles
def overwrite_ep_weather(state):
    global overwrite_ep_weather_inited_handle, oat_sensor_handle,\
        wsped_mps_actuator_handle, wdir_deg_actuator_handle,zone_flr_area_handle,\
        called_vcwg_bool, odb_actuator_handle, orh_actuator_handle

    if not overwrite_ep_weather_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        overwrite_ep_weather_inited_handle = True
        oat_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,
                                                                             "Site Outdoor Air Drybulb Temperature",
                                                                             "Environment")
        odb_actuator_handle = coordination.ep_api.exchange.\
            get_actuator_handle(state, "Weather Data", "Outdoor Dry Bulb", "Environment")
        orh_actuator_handle = coordination.ep_api.exchange.\
            get_actuator_handle(state, "Weather Data", "Outdoor Relative Humidity", "Environment")
        if 'MediumOffice' in coordination.bld_type:
            global roof_hConv_actuator_handle, medOdbOwbHandles
            roof_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "BUILDING_ROOF")
            medOdbOwbHandles = medOfficeGetAirNodeHandles(state)

        if "20Stories" in coordination.bld_type or 'SimplifiedHighBld' in coordination.bld_type:
            global Surface_576_roof_hConv_actuator_handle, \
            Surface_582_roof_hConv_actuator_handle, Surface_588_roof_hConv_actuator_handle, \
            Surface_594_roof_hConv_actuator_handle, Surface_600_roof_hConv_actuator_handle, \
                odb_floor1_actuator_handle, owb_floor1_actuator_handle, odb_floor11_actuator_handle, owb_floor11_actuator_handle,\
                odb_floor20_actuator_handle, owb_floor20_actuator_handle

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
            odb_floor1_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_1DryBulb")
            owb_floor1_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_1WetBulb")
            odb_floor11_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_11DryBulb")
            owb_floor11_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_11WetBulb")
            odb_floor20_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_20DryBulb")
            owb_floor20_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_20WetBulb")

        if "20Stories" in coordination.bld_type:
            global  odb_floor2_actuator_handle, owb_floor2_actuator_handle, \
            odb_floor3_actuator_handle, owb_floor3_actuator_handle, odb_floor4_actuator_handle, owb_floor4_actuator_handle, \
            odb_floor5_actuator_handle, owb_floor5_actuator_handle, odb_floor6_actuator_handle, owb_floor6_actuator_handle, \
            odb_floor7_actuator_handle, owb_floor7_actuator_handle, odb_floor8_actuator_handle, owb_floor8_actuator_handle, \
            odb_floor9_actuator_handle, owb_floor9_actuator_handle, odb_floor10_actuator_handle, owb_floor10_actuator_handle, \
             odb_floor12_actuator_handle, owb_floor12_actuator_handle, \
            odb_floor13_actuator_handle, owb_floor13_actuator_handle, odb_floor14_actuator_handle, owb_floor14_actuator_handle, \
            odb_floor15_actuator_handle, owb_floor15_actuator_handle, odb_floor16_actuator_handle, owb_floor16_actuator_handle, \
            odb_floor17_actuator_handle, owb_floor17_actuator_handle, odb_floor18_actuator_handle, owb_floor18_actuator_handle, \
            odb_floor19_actuator_handle, owb_floor19_actuator_handle

            odb_floor2_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_2DryBulb")
            owb_floor2_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_2WetBulb")
            odb_floor3_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_3DryBulb")
            owb_floor3_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_3WetBulb")
            odb_floor4_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_4DryBulb")
            owb_floor4_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_4WetBulb")
            odb_floor5_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_5DryBulb")
            owb_floor5_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_5WetBulb")
            odb_floor6_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_6DryBulb")
            owb_floor6_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_6WetBulb")
            odb_floor7_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_7DryBulb")
            owb_floor7_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_7WetBulb")
            odb_floor8_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_8DryBulb")
            owb_floor8_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_8WetBulb")
            odb_floor9_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_9DryBulb")
            owb_floor9_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_9WetBulb")
            odb_floor10_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_10DryBulb")
            owb_floor10_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_10WetBulb")
            odb_floor12_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_12DryBulb")
            owb_floor12_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_12WetBulb")
            odb_floor13_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_13DryBulb")
            owb_floor13_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_13WetBulb")
            odb_floor14_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_14DryBulb")
            owb_floor14_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_14WetBulb")
            odb_floor15_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_15DryBulb")
            owb_floor15_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_15WetBulb")
            odb_floor16_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_16DryBulb")
            owb_floor16_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_16WetBulb")
            odb_floor17_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_17DryBulb")
            owb_floor17_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_17WetBulb")
            odb_floor18_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_18DryBulb")
            owb_floor18_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_18WetBulb")
            odb_floor19_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_19DryBulb")
            owb_floor19_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:Floor_19WetBulb")

        if odb_actuator_handle < 0 or orh_actuator_handle < 0:
            print('ovewrite_ep_weather(): some handle not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)
        if "MediumOffice" in coordination.bld_type:
            if roof_hConv_actuator_handle < 0:
                print('ovewrite_ep_weather(): MediumOffice,some handle not available')
                os.getpid()
                os.kill(os.getpid(), signal.SIGTERM)

        if "20Stories" in coordination.bld_type:
            if Surface_576_roof_hConv_actuator_handle < 0 or \
                Surface_582_roof_hConv_actuator_handle < 0 or Surface_588_roof_hConv_actuator_handle < 0 or \
                Surface_594_roof_hConv_actuator_handle < 0 or Surface_600_roof_hConv_actuator_handle < 0 or \
                odb_floor1_actuator_handle < 0 or owb_floor1_actuator_handle < 0 or odb_floor2_actuator_handle < 0 or \
                owb_floor2_actuator_handle < 0 or odb_floor3_actuator_handle < 0 or owb_floor3_actuator_handle < 0 or \
                odb_floor4_actuator_handle < 0 or owb_floor4_actuator_handle < 0 or odb_floor5_actuator_handle < 0 or \
                owb_floor5_actuator_handle < 0 or odb_floor6_actuator_handle < 0 or owb_floor6_actuator_handle < 0 or \
                odb_floor7_actuator_handle < 0 or owb_floor7_actuator_handle < 0 or odb_floor8_actuator_handle < 0 or \
                owb_floor8_actuator_handle < 0 or odb_floor9_actuator_handle < 0 or owb_floor9_actuator_handle < 0 or \
                odb_floor10_actuator_handle < 0 or owb_floor10_actuator_handle < 0 or odb_floor11_actuator_handle < 0 or \
                owb_floor11_actuator_handle < 0 or odb_floor12_actuator_handle < 0 or owb_floor12_actuator_handle < 0 or \
                odb_floor13_actuator_handle < 0 or owb_floor13_actuator_handle < 0 or odb_floor14_actuator_handle < 0 or \
                owb_floor14_actuator_handle < 0 or odb_floor15_actuator_handle < 0 or owb_floor15_actuator_handle < 0 or \
                odb_floor16_actuator_handle < 0 or owb_floor16_actuator_handle < 0 or odb_floor17_actuator_handle < 0 or \
                owb_floor17_actuator_handle < 0 or odb_floor18_actuator_handle < 0 or owb_floor18_actuator_handle < 0 or \
                odb_floor19_actuator_handle < 0 or owb_floor19_actuator_handle < 0 or odb_floor20_actuator_handle < 0 or \
                owb_floor20_actuator_handle < 0:
                print('ovewrite_ep_weather(): 20Stories,some handle not available')
                os.getpid()
                os.kill(os.getpid(), signal.SIGTERM)
        if 'SimplifiedHighBld' in coordination.bld_type:
            if Surface_576_roof_hConv_actuator_handle < 0 or \
                Surface_582_roof_hConv_actuator_handle < 0 or Surface_588_roof_hConv_actuator_handle < 0 or \
                Surface_594_roof_hConv_actuator_handle < 0 or Surface_600_roof_hConv_actuator_handle < 0 or \
                odb_floor1_actuator_handle < 0 or owb_floor1_actuator_handle < 0 or odb_floor11_actuator_handle < 0 or \
                owb_floor11_actuator_handle < 0 or odb_floor20_actuator_handle < 0 or owb_floor20_actuator_handle < 0:
                print('ovewrite_ep_weather(): SimplifiedHighBld,some handle not available')
                os.getpid()
                os.kill(os.getpid(), signal.SIGTERM)

    warm_up = coordination.ep_api.exchange.warmup_flag(state)
    if not warm_up:
        # api_to_csv(state)
        if not called_vcwg_bool:
            global zone_floor_area_m2
            #zone_floor_area_m2 = coordination.ep_api.exchange.get_internal_variable_value(state, zone_flr_area_handle)
            called_vcwg_bool = True
            Thread(target=run_vcwg).start()
        # Wait for the upstream (VCWG upload canyon info to Parent) to finish
        coordination.sem1.acquire()
        if 'vector' in coordination.value:
            if "MediumOffice" in coordination.bld_type:
                odb_c_list = [i - 273.15 for i in coordination.vcwg_canTemp_K_list]
                owb_c_list = [to_get_wet_bulb(state, i, coordination.vcwg_canSpecHum_Ratio_list[odb_c_list.index(i)],
                                              coordination.vcwg_canPress_Pa_list[odb_c_list.index(i)]) for i in odb_c_list]
                for idx in range(len(odb_c_list)):
                    coordination.ep_api.exchange.set_actuator_value(state, medOdbOwbHandles['odb'][idx], odb_c_list[idx])
                    coordination.ep_api.exchange.set_actuator_value(state, medOdbOwbHandles['owb'][idx], owb_c_list[idx])

            elif "20Stories" in coordination.bld_type or "SimplifiedHighBld" in coordination.bld_type:
                odb_c_list = [i - 273.15 for i in coordination.vcwg_canTemp_K_list]
                owb_c_list = [to_get_wet_bulb(state, i, coordination.vcwg_canSpecHum_Ratio_list[odb_c_list.index(i)],
                                              coordination.vcwg_canPress_Pa_list[odb_c_list.index(i)]) for i in odb_c_list]
                print(f'20Stories, odb_c_list: {odb_c_list}, owb_c_list: {owb_c_list}')
                coordination.vcwg_canTempWet_K_list = [i + 273 for i in owb_c_list]
                oat_temp_c = coordination.ep_api.exchange.get_variable_value(state, oat_sensor_handle)
                if '20Stories' in coordination.bld_type:
                    print(f'20Stories, oat_temp_c: {oat_temp_c}, odb_c_list: {odb_c_list}')
                    all_odb_actuator_handle_list = [odb_floor1_actuator_handle, odb_floor2_actuator_handle,
                                                    odb_floor3_actuator_handle, odb_floor4_actuator_handle,
                                                    odb_floor5_actuator_handle, odb_floor6_actuator_handle,
                                                    odb_floor7_actuator_handle, odb_floor8_actuator_handle,
                                                    odb_floor9_actuator_handle, odb_floor10_actuator_handle,
                                                    odb_floor11_actuator_handle, odb_floor12_actuator_handle,
                                                    odb_floor13_actuator_handle, odb_floor14_actuator_handle,
                                                    odb_floor15_actuator_handle, odb_floor16_actuator_handle,
                                                    odb_floor17_actuator_handle, odb_floor18_actuator_handle,
                                                    odb_floor19_actuator_handle, odb_floor20_actuator_handle]
                    all_owb_actuator_handle_list = [owb_floor1_actuator_handle, owb_floor2_actuator_handle,
                                                    owb_floor3_actuator_handle, owb_floor4_actuator_handle,
                                                    owb_floor5_actuator_handle, owb_floor6_actuator_handle,
                                                    owb_floor7_actuator_handle, owb_floor8_actuator_handle,
                                                    owb_floor9_actuator_handle, owb_floor10_actuator_handle,
                                                    owb_floor11_actuator_handle, owb_floor12_actuator_handle,
                                                    owb_floor13_actuator_handle, owb_floor14_actuator_handle,
                                                    owb_floor15_actuator_handle, owb_floor16_actuator_handle,
                                                    owb_floor17_actuator_handle, owb_floor18_actuator_handle,
                                                    owb_floor19_actuator_handle, owb_floor20_actuator_handle]
                elif 'SimplifiedHighBld' in coordination.bld_type:
                    print(f'20StoriesSimplified, oat_temp_c: {oat_temp_c}, odb_c_list: {odb_c_list}')
                    all_odb_actuator_handle_list = [odb_floor1_actuator_handle, odb_floor11_actuator_handle, odb_floor20_actuator_handle]
                    all_owb_actuator_handle_list = [owb_floor1_actuator_handle, owb_floor11_actuator_handle, owb_floor20_actuator_handle]

                for i in range(len(all_odb_actuator_handle_list)):
                    coordination.ep_api.exchange.set_actuator_value(state, all_odb_actuator_handle_list[i], odb_c_list[i])
                    coordination.ep_api.exchange.set_actuator_value(state, all_owb_actuator_handle_list[i], owb_c_list[i])

        else:
            rh = 100*coordination.psychrometric.relative_humidity_b(state, coordination.vcwg_canTemp_K - 273.15,
                                               coordination.vcwg_canSpecHum_Ratio, coordination.vcwg_canPress_Pa)
            coordination.ep_api.exchange.set_actuator_value(state, odb_actuator_handle, coordination.vcwg_canTemp_K - 273.15)
            coordination.ep_api.exchange.set_actuator_value(state, orh_actuator_handle, rh)

        if "MediumOffice" in coordination.bld_type:
            coordination.ep_api.exchange.set_actuator_value(state, roof_hConv_actuator_handle, coordination.vcwg_hConv_w_m2_per_K)
        elif "20Stories" in coordination.bld_type or "SimplifiedHighBld" in coordination.bld_type:
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
def medOfficeGetFloorHandles(state, flrNum):
    _handlsDict = {}

    _flrToName = {'1': ['BOTTOM','BOT'], '2': ['MID','MID'], '3': ['TOP','TOP']}

    _handlsDict['fan'] = None
    _handlsDict['cooling'] = None
    _handlsDict['heating'] = None
    _handlsDict['reheating'] = []

    _tmpFan = coordination.ep_api.exchange.get_variable_handle(state, "Fan Electricity Energy", \
                                                               f"VAV_{flrNum}_FAN")
    _tmpClCoil = coordination.ep_api.exchange.get_variable_handle(state, "Cooling Coil Electricity Energy", \
                                                                    f"VAV_{flrNum}_COOLC DXCOIL")
    _tmpHtCoil = coordination.ep_api.exchange.get_variable_handle(state, "Heating Coil Electricity Energy", \
                                                                    f"VAV_{flrNum}_HEATC")
    _tmpHtCoilCore = coordination.ep_api.exchange.get_variable_handle(state, "Heating Coil Electricity Energy", \
                                                                        f"CORE_{_flrToName[flrNum][0]} VAV BOX REHEAT COIL")
    _tmpHtCoilPeri1 = coordination.ep_api.exchange.get_variable_handle(state, "Heating Coil Electricity Energy", \
                                                                          f"PERIMETER_{_flrToName[flrNum][1]}_ZN_1 VAV BOX REHEAT COIL")
    _tmpHtCoilPeri2 = coordination.ep_api.exchange.get_variable_handle(state, "Heating Coil Electricity Energy", \
                                                                            f"PERIMETER_{_flrToName[flrNum][1]}_ZN_2 VAV BOX REHEAT COIL")
    _tmpHtCoilPeri3 = coordination.ep_api.exchange.get_variable_handle(state, "Heating Coil Electricity Energy", \
                                                                            f"PERIMETER_{_flrToName[flrNum][1]}_ZN_3 VAV BOX REHEAT COIL")
    _tmpHtCoilPeri4 = coordination.ep_api.exchange.get_variable_handle(state, "Heating Coil Electricity Energy", \
                                                                            f"PERIMETER_{_flrToName[flrNum][1]}_ZN_4 VAV BOX REHEAT COIL")
    if _tmpFan * _tmpClCoil * _tmpHtCoil * _tmpHtCoilCore * _tmpHtCoilPeri1 * _tmpHtCoilPeri2 * _tmpHtCoilPeri3 * _tmpHtCoilPeri4  < 0:
        print(f'mediumOfficeGetSensor(): floor {flrNum} handles not available')
        os.getpid()
        os.kill(os.getpid(), signal.SIGTERM)

    _handlsDict['fan'] = _tmpFan
    _handlsDict['cooling'] = _tmpClCoil
    _handlsDict['heating'] = _tmpHtCoil
    _handlsDict['reheating'].append(_tmpHtCoilCore)
    _handlsDict['reheating'].append(_tmpHtCoilPeri1)
    _handlsDict['reheating'].append(_tmpHtCoilPeri2)
    _handlsDict['reheating'].append(_tmpHtCoilPeri3)
    _handlsDict['reheating'].append(_tmpHtCoilPeri4)

    return _handlsDict


def medOfficeGetSensorHandles(state):
    sesHandls = {}
    sesHandls['roof'] = []
    sesHandls['floor'] = []
    sesHandls['wall_south'] = []
    sesHandls['wall_north'] = []
    sesHandls['simhvac'] = None

    sesHandls['floor_energy'] = {}
    for _flr in range(1,4):
        sesHandls['floor_energy'][str(_flr)] = medOfficeGetFloorHandles(state, str(_flr))


    _hvac = \
            coordination.ep_api.exchange.get_variable_handle(state,\
                                                             "HVAC System Total Heat Rejection Energy",\
                                                             "SIMHVAC")
    sesHandls['simhvac'] = _hvac

    _roof = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                        "Building_Roof")
    if _roof < 0:
        print('mediumOfficeGetSensor(): roof handles not available')
        os.getpid()
        os.kill(os.getpid(), signal.SIGTERM)

    sesHandls['roof'].append(_roof)

    _flrSurface = ["Perimeter_bot_ZN_1_Floor", "Perimeter_bot_ZN_2_Floor", "Perimeter_bot_ZN_3_Floor", \
                   "Perimeter_bot_ZN_4_Floor", "Core_bot_ZN_5_Floor"]
    for _flr in _flrSurface:
        _flrHandle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                        _flr)
        if _flrHandle < 0:
            print('mediumOfficeGetSensor(): floor handles not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)
        sesHandls['floor'].append(_flrHandle)

    flrs = ['bot', 'mid', 'top']
    for _flr in flrs:
        _tmpSouth = coordination.ep_api.exchange.get_variable_handle(state, \
                                                                        "Surface Outside Face Temperature", \
                                                                        "Perimeter_" + _flr + "_ZN_1_Wall_South")
        _tmpNorth = coordination.ep_api.exchange.get_variable_handle(state, \
                                                                        "Surface Outside Face Temperature", \
                                                                        "Perimeter_" + _flr + "_ZN_3_Wall_North")
        if _tmpSouth < 0 or _tmpNorth < 0:
            print('mediumOfficeGetSensor(): wall handles not available')
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)
        sesHandls['wall_south'].append(_tmpSouth)
        sesHandls['wall_north'].append(_tmpNorth)

    return sesHandls

def medOfficeGetFloorValues(state, handleDict):
    # _handlsDict['fan'] = _tmpFan
    # _handlsDict['cooling'] = _tmpClCoil
    # _handlsDict['reheating'].append(_tmpHtCoilCore)
    # _handlsDict['reheating'].append(_tmpHtCoilPeri1)
    # _handlsDict['reheating'].append(_tmpHtCoilPeri2)
    # _handlsDict['reheating'].append(_tmpHtCoilPeri3)
    # _handlsDict['reheating'].append(_tmpHtCoilPeri4)
    # coordination.ep_api.exchange.get_variable_value(state, medOfficeSensorHandles['simhvac'])
    flrEnergy_J = 0
    flrEnergy_J += coordination.ep_api.exchange.get_variable_value(state, handleDict['fan'])
    flrEnergy_J += coordination.ep_api.exchange.get_variable_value(state, handleDict['cooling'])
    # _tmpHeating = coordination.ep_api.exchange.get_variable_value(state, handleDict['heating'])
    # print(f"floor coil heating: {_tmpHeating}")
    for _reheat in handleDict['reheating']:
        flrEnergy_J += coordination.ep_api.exchange.get_variable_value(state, _reheat)
    return flrEnergy_J
def medOfficeGetSensorValues(state, handles):
    wall_temperatures_dict = {}
    wall_temperatures_dict['south'] = []
    wall_temperatures_dict['north'] = []

    roofTextK = coordination.ep_api.exchange.get_variable_value(state, handles['roof'][0]) + 273.15
    flrTextK = 0
    for _flr in handles['floor']:
        _flrTextK = coordination.ep_api.exchange.get_variable_value(state, _flr) + 273.15
        flrTextK += _flrTextK
    flrTextK /= len(handles['floor'])

    south_K = 0
    north_K = 0

    for idx in range(0, len(handles['wall_south'])):
        _south_K = coordination.ep_api.exchange.get_variable_value(state, handles['wall_south'][idx]) + 273.15
        _north_K = coordination.ep_api.exchange.get_variable_value(state, handles['wall_north'][idx]) + 273.15
        south_K += _south_K
        north_K += _north_K
        wall_temperatures_dict['south'].append(_south_K)
        wall_temperatures_dict['north'].append(_north_K)
    south_K /= len(handles['wall_south'])
    north_K /= len(handles['wall_north'])

    return wall_temperatures_dict, roofTextK, flrTextK, south_K, north_K
def MediumOffice_get_ep_results(state):
    global get_ep_results_inited_handle, medOfficeSensorHandles

    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        get_ep_results_inited_handle = True

        medOfficeSensorHandles = medOfficeGetSensorHandles(state)

    # get EP results, upload to coordination
    if called_vcwg_bool:
        global ep_last_call_time_seconds

        coordination.sem2.acquire()
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600  # Should always accumulate, since system time always advances
        accumulated_time_in_seconds = curr_sim_time_in_seconds - ep_last_call_time_seconds
        ep_last_call_time_seconds = curr_sim_time_in_seconds
        hvac_heat_rejection_J = coordination.ep_api.exchange.get_variable_value(state, medOfficeSensorHandles['simhvac'])
        hvac_waste_w_m2 = hvac_heat_rejection_J / accumulated_time_in_seconds / coordination.footprint_area_m2
        for flr in range(coordination.EP_nFloor):
            _tmpFlrJ = medOfficeGetFloorValues(state, medOfficeSensorHandles['floor_energy'][str(1 + flr)])
            _tmpFlgW_m2 = _tmpFlrJ / accumulated_time_in_seconds/ coordination.footprint_area_m2
            if 'CoolElec' in coordination.value:
                coordination.EP_floor_energy_lst[flr] += _tmpFlgW_m2
            else:
                coordination.EP_floor_energy_lst[flr] += hvac_waste_w_m2 / coordination.EP_nFloor

        coordination.ep_sensWaste_w_m2_per_footprint_area += hvac_waste_w_m2

        print("Old waste", coordination.ep_sensWaste_w_m2_per_footprint_area)
        print("New waste", coordination.EP_floor_energy_lst)

        time_index_alignment_bool = 1 > abs(curr_sim_time_in_seconds - coordination.vcwg_needed_time_idx_in_seconds)

        if not time_index_alignment_bool:
            coordination.sem2.release()
            return

        coordination.EP_wall_temperatures_K_dict, roof_Text_K, floor_Text_K, south_wall_Text_K, north_wall_Text_K  \
            = medOfficeGetSensorValues(state, medOfficeSensorHandles)

        coordination.ep_floor_Text_K = floor_Text_K
        coordination.ep_roof_Text_K = roof_Text_K
        coordination.ep_wallSun_Text_K = south_wall_Text_K
        coordination.ep_wallShade_Text_K = north_wall_Text_K


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

def _20Stories_get_zone_to_pthp_dict():
    global zone_pthp_dict
    zone_pthp_dict = {}
    zone_pthp_dict[1] = 56
    zone_pthp_dict[10] = 65
    zone_pthp_dict[100] = 6
    zone_pthp_dict[11] = 66
    zone_pthp_dict[12] = 67
    zone_pthp_dict[13] = 68
    zone_pthp_dict[14] = 69
    zone_pthp_dict[15] = 70
    zone_pthp_dict[16] = 71
    zone_pthp_dict[17] = 72
    zone_pthp_dict[18] = 73
    zone_pthp_dict[19] = 74
    zone_pthp_dict[2] = 57
    zone_pthp_dict[20] = 75
    zone_pthp_dict[21] = 76
    zone_pthp_dict[22] = 77
    zone_pthp_dict[23] = 78
    zone_pthp_dict[24] = 79
    zone_pthp_dict[25] = 80
    zone_pthp_dict[26] = 81
    zone_pthp_dict[27] = 82
    zone_pthp_dict[28] = 83
    zone_pthp_dict[29] = 84
    zone_pthp_dict[3] = 58
    zone_pthp_dict[30] = 85
    zone_pthp_dict[31] = 86
    zone_pthp_dict[32] = 87
    zone_pthp_dict[33] = 88
    zone_pthp_dict[34] = 89
    zone_pthp_dict[35] = 90
    zone_pthp_dict[36] = 91
    zone_pthp_dict[37] = 92
    zone_pthp_dict[38] = 93
    zone_pthp_dict[39] = 94
    zone_pthp_dict[4] = 59
    zone_pthp_dict[40] = 95
    zone_pthp_dict[41] = 96
    zone_pthp_dict[42] = 97
    zone_pthp_dict[43] = 98
    zone_pthp_dict[44] = 99
    zone_pthp_dict[45] = 100
    zone_pthp_dict[46] = 38
    zone_pthp_dict[47] = 39
    zone_pthp_dict[48] = 40
    zone_pthp_dict[49] = 41
    zone_pthp_dict[5] = 60
    zone_pthp_dict[50] = 42
    zone_pthp_dict[51] = 43
    zone_pthp_dict[52] = 44
    zone_pthp_dict[53] = 45
    zone_pthp_dict[54] = 46
    zone_pthp_dict[55] = 47
    zone_pthp_dict[56] = 48
    zone_pthp_dict[57] = 49
    zone_pthp_dict[58] = 50
    zone_pthp_dict[59] = 51
    zone_pthp_dict[6] = 61
    zone_pthp_dict[60] = 52
    zone_pthp_dict[61] = 53
    zone_pthp_dict[62] = 54
    zone_pthp_dict[63] = 55
    zone_pthp_dict[64] = 36
    zone_pthp_dict[65] = 37
    zone_pthp_dict[66] = 34
    zone_pthp_dict[67] = 35
    zone_pthp_dict[68] = 25
    zone_pthp_dict[69] = 26
    zone_pthp_dict[7] = 62
    zone_pthp_dict[70] = 27
    zone_pthp_dict[71] = 28
    zone_pthp_dict[72] = 29
    zone_pthp_dict[73] = 30
    zone_pthp_dict[74] = 31
    zone_pthp_dict[75] = 32
    zone_pthp_dict[76] = 33
    zone_pthp_dict[77] = 23
    zone_pthp_dict[78] = 24
    zone_pthp_dict[79] = 18
    zone_pthp_dict[8] = 63
    zone_pthp_dict[80] = 19
    zone_pthp_dict[81] = 20
    zone_pthp_dict[82] = 21
    zone_pthp_dict[83] = 22
    zone_pthp_dict[84] = 16
    zone_pthp_dict[85] = 17
    zone_pthp_dict[86] = 14
    zone_pthp_dict[87] = 15
    zone_pthp_dict[88] = 12
    zone_pthp_dict[89] = 13
    zone_pthp_dict[9] = 64
    zone_pthp_dict[90] = 11
    zone_pthp_dict[91] = 7
    zone_pthp_dict[92] = 8
    zone_pthp_dict[93] = 9
    zone_pthp_dict[94] = 10
    zone_pthp_dict[95] = 1
    zone_pthp_dict[96] = 2
    zone_pthp_dict[97] = 3
    zone_pthp_dict[98] = 4
    zone_pthp_dict[99] = 5


def _20Stories_batch_get_energy_results(state, dict, accumulated_time_in_seconds):
    '''
    Zone Packaged Terminal Heat Pump Total Heating Energy
    Zone Packaged Terminal Heat Pump Total Cooling Energy
    Zone Packaged Terminal Heat Pump Electricity Energy
    'PTHP 1' ... 'PTHP 100'
    '''

    if 'SimplifiedHighBld' in coordination.bld_type:
        flr_nbrs = [1,11,20]
    else:
        flr_nbrs = [ i for i in range(1,21)]
    zone_nbrs = [(i - 1) * 5 + j for i in flr_nbrs for j in range(1, 6)]

    energy_dict = {}
    heating_total = 0
    cooling_total = 0
    electricity_total = 0
    for tmp_zone_nbr in zone_nbrs:
        i = zone_pthp_dict[tmp_zone_nbr]
        energy_dict['PTHP ' + str(i)] = []
        tmp_heating = coordination.ep_api.exchange.get_variable_value(state, dict['PTHP ' + str(i)][0])
        tmp_cooling = coordination.ep_api.exchange.get_variable_value(state, dict['PTHP ' + str(i)][1])
        tmp_electricity = coordination.ep_api.exchange.get_variable_value(state, dict['PTHP ' + str(i)][2])
        energy_dict['PTHP ' + str(i)].append(tmp_heating)
        energy_dict['PTHP ' + str(i)].append(tmp_cooling)
        energy_dict['PTHP ' + str(i)].append(tmp_electricity)
        heating_total += tmp_heating
        cooling_total += tmp_cooling
        electricity_total += tmp_electricity

    for idx, i in enumerate(flr_nbrs):
        for j in range(1, 6):
            tmp_zone = zone_pthp_dict[(i - 1) * 5 + j]
            # coordination.EP_floor_energy_lst[i-1] += energy_dict['PTHP ' + str(tmp_zone)][0]
            coordination.EP_floor_energy_lst[idx] += energy_dict['PTHP ' + str(tmp_zone)][1]
            coordination.EP_floor_energy_lst[idx] += energy_dict['PTHP ' + str(tmp_zone)][2]
        coordination.EP_floor_energy_lst[idx] /= coordination.footprint_area_m2
        coordination.EP_floor_energy_lst[idx] /= accumulated_time_in_seconds
    return energy_dict, heating_total, cooling_total, electricity_total

def _20Stories_batch_handles(state):
    '''
        surface576_roof_Text_c_handle, surface582_roof_Text_c_handle, surface588_roof_Text_c_handle, \
        surface594_roof_Text_c_handle, surface600_roof_Text_c_handle, surface1_floor_Text_c_handle, \
        surface7_floor_Text_c_handle, surface13_floor_Text_c_handle, surface19_floor_Text_c_handle, \
        surface25_floor_Text_c_handle

        surface92_south_wall_Text_c_handle, surface122_south_wall_Text_c_handle, surface152_south_wall_Text_c_handle, \
        surface182_south_wall_Text_c_handle, surface212_south_wall_Text_c_handle, surface242_south_wall_Text_c_handle, \
        surface272_south_wall_Text_c_handle, surface302_south_wall_Text_c_handle, surface332_south_wall_Text_c_handle, \
        surface362_south_wall_Text_c_handle, surface392_south_wall_Text_c_handle, surface422_south_wall_Text_c_handle, \
        surface452_south_wall_Text_c_handle, surface482_south_wall_Text_c_handle, surface512_south_wall_Text_c_handle, \
        surface542_south_wall_Text_c_handle, surface572_south_wall_Text_c_handle,\
        surface26_north_wall_Text_c_handle, surface56_north_wall_Text_c_handle, surface86_north_wall_Text_c_handle, \
        surface116_north_wall_Text_c_handle, surface146_north_wall_Text_c_handle, surface176_north_wall_Text_c_handle, \
        surface206_north_wall_Text_c_handle, surface236_north_wall_Text_c_handle, surface266_north_wall_Text_c_handle, \
        surface296_north_wall_Text_c_handle, surface326_north_wall_Text_c_handle, surface356_north_wall_Text_c_handle, \
        surface386_north_wall_Text_c_handle, surface416_north_wall_Text_c_handle, surface446_north_wall_Text_c_handle, \
        surface476_north_wall_Text_c_handle, surface506_north_wall_Text_c_handle, surface536_north_wall_Text_c_handle, \
        surface566_north_wall_Text_c_handle, surface596_north_wall_Text_c_handle,\
        surface14_east_wall_Text_c_handle, surface44_east_wall_Text_c_handle, surface74_east_wall_Text_c_handle, \
        surface104_east_wall_Text_c_handle, surface134_east_wall_Text_c_handle, surface164_east_wall_Text_c_handle, \
        surface194_east_wall_Text_c_handle, surface224_east_wall_Text_c_handle, surface254_east_wall_Text_c_handle, \
        surface284_east_wall_Text_c_handle, surface314_east_wall_Text_c_handle, surface344_east_wall_Text_c_handle, \
        surface374_east_wall_Text_c_handle, surface404_east_wall_Text_c_handle, surface434_east_wall_Text_c_handle, \
        surface464_east_wall_Text_c_handle, surface494_east_wall_Text_c_handle, surface524_east_wall_Text_c_handle, \
        surface554_east_wall_Text_c_handle, surface584_east_wall_Text_c_handle,\
        surface10_west_wall_Text_c_handle, surface40_west_wall_Text_c_handle, surface70_west_wall_Text_c_handle, \
        surface100_west_wall_Text_c_handle, surface130_west_wall_Text_c_handle, surface160_west_wall_Text_c_handle, \
        surface190_west_wall_Text_c_handle, surface220_west_wall_Text_c_handle, surface250_west_wall_Text_c_handle, \
        surface280_west_wall_Text_c_handle, surface310_west_wall_Text_c_handle, surface340_west_wall_Text_c_handle, \
        surface370_west_wall_Text_c_handle, surface400_west_wall_Text_c_handle, surface430_west_wall_Text_c_handle, \
        surface460_west_wall_Text_c_handle, surface490_west_wall_Text_c_handle, surface520_west_wall_Text_c_handle, \
        surface550_west_wall_Text_c_handle, surface580_west_wall_Text_c_handle
    '''
    roof_floor_handles_dict = {}
    roof_floor_handles_dict['roof'] = []
    roof_floor_handles_dict['floor'] = []
    for i in range(1, 6):
        tmp_roof = coordination.ep_api.exchange.get_variable_handle(state,
                                                                    "Surface Outside Face Temperature",
                                                                    "Surface " + str(576 + (i - 1) * 6))
        tmp_floor = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                     "Surface " + str(1 + (i - 1) * 6))
        if tmp_roof * tmp_floor < 0:
            print("20 Stories roof or floor surface handle error!")
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)

        roof_floor_handles_dict['roof'].append(tmp_roof)
        roof_floor_handles_dict['floor'].append(tmp_floor)

    wall_handles_dict = {}
    wall_handles_dict['south'] = []
    wall_handles_dict['north'] = []
    wall_handles_dict['east'] = []
    wall_handles_dict['west'] = []

    if 'SimplifiedHighBld' in coordination.bld_type:
        flr_nbrs = [1,11,20]
    else:
        flr_nbrs = [ i for i in range(1,21)]
    zone_nbrs = [(i - 1) * 5 + j for i in flr_nbrs for j in range(1, 6)]

    for i in flr_nbrs:
        tmp_south = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                                                "Surface " + str(2 + (i - 1) * 30))
        tmp_north = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                                                "Surface " + str(26 + (i - 1) * 30))
        tmp_east = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                                                "Surface " + str(14 + (i - 1) * 30))
        tmp_west = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                                                "Surface " + str(10 + (i - 1) * 30))
        if tmp_south * tmp_west * tmp_east * tmp_north < 0:
            print("20 Stories wall surface handle error!")
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)

        wall_handles_dict['south'].append(tmp_south)
        wall_handles_dict['north'].append(tmp_north)
        wall_handles_dict['east'].append(tmp_east)
        wall_handles_dict['west'].append(tmp_west)

    pthp_dict = {}
    for tmp_zone in zone_nbrs:
        i = zone_pthp_dict[tmp_zone]
        pthp_dict['PTHP ' + str(i)] = []

        _tmpHeating = coordination.ep_api.exchange.get_variable_handle(state,
                                                             "Zone Packaged Terminal Heat Pump Total Heating Energy",
                                                             'PTHP ' + str(i))
        _tmpCooling = coordination.ep_api.exchange.get_variable_handle(state,
                                                             "Zone Packaged Terminal Heat Pump Total Cooling Energy",
                                                             'PTHP ' + str(i))
        _tmpElectricity = coordination.ep_api.exchange.get_variable_handle(state,
                                                           "Zone Packaged Terminal Heat Pump Electricity Energy",
                                                             'PTHP ' + str(i))
        if _tmpHeating * _tmpCooling * _tmpElectricity < 0:
            print("PTHP energy handle error!")
            os.getpid()
            os.kill(os.getpid(), signal.SIGTERM)
        pthp_dict['PTHP ' + str(i)].append(_tmpHeating)
        pthp_dict['PTHP ' + str(i)].append(_tmpCooling)
        pthp_dict['PTHP ' + str(i)].append(_tmpElectricity)
    return wall_handles_dict, roof_floor_handles_dict, pthp_dict



def _20_Stories_batch_get_surface_temperatures(state, wall_handles_dict, roof_floor_handles_dict):
    #coordination.ep_api.exchange.get_variable_value(state, surface576_roof_Text_c_handle)
    wall_temperatures_dict = {}
    wall_temperatures_dict['south'] = []
    wall_temperatures_dict['north'] = []

    for key in ['south', 'north']:
        for i in range(len(wall_handles_dict[key])):
            tmp = coordination.ep_api.exchange.get_variable_value(state, wall_handles_dict[key][i]) + 273.15
            wall_temperatures_dict[key].append(tmp)
    south_wall_Text_K = 0
    north_wall_Text_K = 0
    for i in range(len(wall_temperatures_dict['south'])):
        south_wall_Text_K += wall_temperatures_dict['south'][i]
        north_wall_Text_K += wall_temperatures_dict['north'][i]
    south_wall_Text_K /= len(wall_temperatures_dict['south'])
    north_wall_Text_K /= len(wall_temperatures_dict['north'])

    roof_Text_K = 0
    floor_Text_K = 0
    for i in range(len(roof_floor_handles_dict['roof'])):
        roof_Text_K += coordination.ep_api.exchange.get_variable_value(state, roof_floor_handles_dict['roof'][i]) + 273.15
        floor_Text_K += coordination.ep_api.exchange.get_variable_value(state, roof_floor_handles_dict['floor'][i]) + 273.15
    roof_Text_K /= len(roof_floor_handles_dict['roof'])
    floor_Text_K /= len(roof_floor_handles_dict['floor'])

    return wall_temperatures_dict, roof_Text_K, floor_Text_K, south_wall_Text_K, north_wall_Text_K
def _20Stories_get_ep_results(state):
    global get_ep_results_inited_handle, \
        hvac_heat_rejection_sensor_handle,\
        wall_handles_dict, roof_floor_handles_dict, pthp_energy_handles_dict
    _20Stories_get_zone_to_pthp_dict()
    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        get_ep_results_inited_handle = True
        wall_handles_dict,roof_floor_handles_dict, pthp_energy_handles_dict = _20Stories_batch_handles(state)
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,\
                                                             "HVAC System Total Heat Rejection Energy",\
                                                             "SIMHVAC")
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
        pthp_energy_dict, pthp_heating_total, pthp_cooling_total, pthp_electricity_total =\
            _20Stories_batch_get_energy_results(state, pthp_energy_handles_dict, accumulated_time_in_seconds)

        time_index_alignment_bool = 1 > abs(curr_sim_time_in_seconds - coordination.vcwg_needed_time_idx_in_seconds)
        if not time_index_alignment_bool:
            coordination.sem2.release()
            return

        print(f'coordination.ep_sensWaste_w_m2_per_footprint_area = {coordination.ep_sensWaste_w_m2_per_footprint_area},'
              f'coordination.EP_floor_energy_lst = {sum(coordination.EP_floor_energy_lst)}')
        print("coordination.EP_floor_energy_lst = ", coordination.EP_floor_energy_lst)

        coordination.EP_wall_temperatures_K_dict,roof_Text_K, floor_Text_K, south_wall_Text_K, north_wall_Text_K \
            = _20_Stories_batch_get_surface_temperatures(state, wall_handles_dict, roof_floor_handles_dict)

        coordination.ep_floor_Text_K = floor_Text_K
        coordination.ep_roof_Text_K = roof_Text_K
        coordination.ep_wallSun_Text_K = south_wall_Text_K
        coordination.ep_wallShade_Text_K = north_wall_Text_K

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