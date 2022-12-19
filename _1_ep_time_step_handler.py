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

def api_to_csv(state):
    orig = coordination.ep_api.exchange.list_available_api_data_csv(state)
    newFileByteArray = bytearray(orig)
    api_path = os.path.join(coordination.data_saving_path,'..', f'{coordination.value}_api_data.csv')
    newFile = open(api_path, "wb")
    newFile.write(newFileByteArray)
    newFile.close()

def run_vcwg():
    if 'None' in coordination.config['Bypass']['TopForcingFileName']:
        TopForcingFileName = None
        epwFileName = coordination.config['Bypass']['epwFileName']
    else:
        epwFileName = None
        TopForcingFileName = coordination.config['Bypass']['TopForcingFileName']
    VCWGParamFileName = coordination.config['Bypass']['VCWGParamFileName']
    ViewFactorFileName = f'{coordination.value}_ViewFactor.txt'
    # Case name to append output file names with
    case = f'{coordination.value}'
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
'''
        :param state: An active EnergyPlus "state" that is returned from a call to `api.state_manager.new_state()`.
        :param dry_bulb_temp: Psychrometric dry bulb temperature, in C
        :param humidity_ratio: Humidity ratio, in kgWater/kgDryAir
        :param barometric_pressure: Barometric pressure, in Pa
'''
def to_get_wet_bulb(state, dry_bulb_temp_C, humidity_ratio, barometric_pressure_Pa):
    _wetbulb = coordination.psychrometric.wet_bulb(state, dry_bulb_temp_C, humidity_ratio, barometric_pressure_Pa)
    return _wetbulb
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
        #Actuator	Schedule:Compact	Schedule Value	OUTDOORAIRNODE:BOTDRYBULB;
        if 'MediumOffice' in coordination.bld_type:
            global odb_bot_actuator_handle, owb_bot_actuator_handle, odb_mid_actuator_handle, owb_mid_actuator_handle, \
        odb_top_actuator_handle, owb_top_actuator_handle, roof_hConv_actuator_handle
            roof_hConv_actuator_handle = coordination.ep_api.exchange. \
                get_actuator_handle(state, "Surface", "Exterior Surface Convection Heat Transfer Coefficient", \
                                    "BUILDING_ROOF")
            odb_bot_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:BOTDRYBULB")
            owb_bot_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:BOTWETBULB")
            odb_mid_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:MIDDRYBULB")
            owb_mid_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:MIDWETBULB")
            odb_top_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:TOPDRYBULB")
            owb_top_actuator_handle = coordination.ep_api.exchange.\
                get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "OUTDOORAIRNODE:TOPWETBULB")
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
            if roof_hConv_actuator_handle < 0 or \
                odb_bot_actuator_handle < 0 or owb_bot_actuator_handle < 0 or odb_mid_actuator_handle < 0 or \
                owb_mid_actuator_handle < 0 or odb_top_actuator_handle < 0 or owb_top_actuator_handle < 0:
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
                coordination.ep_api.exchange.set_actuator_value(state, odb_bot_actuator_handle, odb_c_list[0])
                coordination.ep_api.exchange.set_actuator_value(state, owb_bot_actuator_handle, owb_c_list[0])
                coordination.ep_api.exchange.set_actuator_value(state, odb_mid_actuator_handle, odb_c_list[1])
                coordination.ep_api.exchange.set_actuator_value(state, owb_mid_actuator_handle, owb_c_list[1])
                coordination.ep_api.exchange.set_actuator_value(state, odb_top_actuator_handle, odb_c_list[2])
                coordination.ep_api.exchange.set_actuator_value(state, owb_top_actuator_handle, owb_c_list[2])
            elif "20Stories" in coordination.bld_type or "SimplifiedHighBld" in coordination.bld_type:
                odb_c_list = [i - 273.15 for i in coordination.vcwg_canTemp_K_list]
                owb_c_list = [to_get_wet_bulb(state, i, coordination.vcwg_canSpecHum_Ratio_list[odb_c_list.index(i)],
                                              coordination.vcwg_canPress_Pa_list[odb_c_list.index(i)]) for i in odb_c_list]
                if '20Stories' in coordination.bld_type:
                    oat_temp_c = coordination.ep_api.exchange.get_variable_value(state, oat_sensor_handle)
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

def _20Stories_get_ep_results(state):
    global get_ep_results_inited_handle, \
        hvac_heat_rejection_sensor_handle,\
        surface576_roof_Text_c_handle, surface582_roof_Text_c_handle, surface588_roof_Text_c_handle, \
        surface594_roof_Text_c_handle, surface600_roof_Text_c_handle, surface1_floor_Text_c_handle, \
        surface7_floor_Text_c_handle, surface13_floor_Text_c_handle, surface19_floor_Text_c_handle, \
        surface25_floor_Text_c_handle, \
        surface2_south_wall_Text_c_handle, surface32_south_wall_Text_c_handle, surface62_south_wall_Text_c_handle, \
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

    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        get_ep_results_inited_handle = True
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,\
                                                             "HVAC System Total Heat Rejection Energy",\
                                                             "SIMHVAC")
        surface576_roof_Text_c_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                                            "Surface 576")
        surface582_roof_Text_c_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                                            "Surface 582")
        surface588_roof_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 588")
        surface594_roof_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 594")
        surface600_roof_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 600")
        surface1_floor_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 1")
        surface7_floor_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 7")
        surface13_floor_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 13")
        surface19_floor_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 19")
        surface25_floor_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 25")
        surface2_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 2")
        surface32_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 32")
        surface62_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 62")
        surface92_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 92")
        surface122_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 122")
        surface152_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 152")
        surface182_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 182")
        surface212_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 212")
        surface242_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 242")
        surface272_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 272")
        surface302_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 302")
        surface332_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 332")
        surface362_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 362")
        surface392_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 392")
        surface422_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 422")
        surface452_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 452")
        surface482_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 482")
        surface512_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 512")
        surface542_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 542")
        surface572_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 572")
        surface26_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 26")
        surface56_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 56")
        surface86_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 86")
        surface116_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 116")
        surface146_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 146")
        surface176_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 176")
        surface206_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 206")
        surface236_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 236")
        surface266_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 266")
        surface296_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 296")
        surface326_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 326")
        surface356_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 356")
        surface386_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 386")
        surface416_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 416")
        surface446_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 446")
        surface476_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 476")
        surface506_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 506")
        surface536_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 536")
        surface566_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 566")
        surface596_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 596")
        surface14_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 14")
        surface44_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 44")
        surface74_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 74")
        surface104_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 104")
        surface134_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 134")
        surface164_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 164")
        surface194_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 194")
        surface224_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 224")
        surface254_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 254")
        surface284_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 284")
        surface314_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 314")
        surface344_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 344")
        surface374_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 374")
        surface404_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 404")
        surface434_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 434")
        surface464_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 464")
        surface494_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 494")
        surface524_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 524")
        surface554_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 554")
        surface584_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 584")
        surface10_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 10")
        surface40_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 40")
        surface70_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 70")
        surface100_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 100")
        surface130_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 130")
        surface160_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 160")
        surface190_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 190")
        surface220_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 220")
        surface250_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 250")
        surface280_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 280")
        surface310_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 310")
        surface340_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 340")
        surface370_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 370")
        surface400_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 400")
        surface430_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 430")
        surface460_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 460")
        surface490_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 490")
        surface520_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 520")
        surface550_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 550")
        surface580_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 580")

        if (hvac_heat_rejection_sensor_handle == -1 or \
                surface576_roof_Text_c_handle == -1 or surface582_roof_Text_c_handle == -1 or \
                surface588_roof_Text_c_handle == -1 or surface594_roof_Text_c_handle == -1 or \
                surface600_roof_Text_c_handle == -1 or surface1_floor_Text_c_handle == -1 or \
                surface7_floor_Text_c_handle == -1 or surface13_floor_Text_c_handle == -1 or \
                surface19_floor_Text_c_handle == -1 or surface25_floor_Text_c_handle == -1 or \
            surface2_south_wall_Text_c_handle == -1 or surface32_south_wall_Text_c_handle == -1 or \
            surface62_south_wall_Text_c_handle == -1 or surface92_south_wall_Text_c_handle == -1 or \
            surface122_south_wall_Text_c_handle == -1 or surface152_south_wall_Text_c_handle == -1 or \
            surface182_south_wall_Text_c_handle == -1 or surface212_south_wall_Text_c_handle == -1 or \
            surface242_south_wall_Text_c_handle == -1 or surface272_south_wall_Text_c_handle == -1 or \
            surface302_south_wall_Text_c_handle == -1 or surface332_south_wall_Text_c_handle == -1 or \
            surface362_south_wall_Text_c_handle == -1 or surface392_south_wall_Text_c_handle == -1 or \
            surface422_south_wall_Text_c_handle == -1 or surface452_south_wall_Text_c_handle == -1 or \
            surface482_south_wall_Text_c_handle == -1 or surface512_south_wall_Text_c_handle == -1 or \
            surface542_south_wall_Text_c_handle == -1 or surface572_south_wall_Text_c_handle == -1 or \
            surface26_north_wall_Text_c_handle == -1 or surface56_north_wall_Text_c_handle == -1 or \
            surface86_north_wall_Text_c_handle == -1 or surface116_north_wall_Text_c_handle == -1 or \
            surface146_north_wall_Text_c_handle == -1 or surface176_north_wall_Text_c_handle == -1 or \
            surface206_north_wall_Text_c_handle == -1 or surface236_north_wall_Text_c_handle == -1 or \
            surface266_north_wall_Text_c_handle == -1 or surface296_north_wall_Text_c_handle == -1 or \
            surface326_north_wall_Text_c_handle == -1 or surface356_north_wall_Text_c_handle == -1 or \
            surface386_north_wall_Text_c_handle == -1 or surface416_north_wall_Text_c_handle == -1 or \
            surface446_north_wall_Text_c_handle == -1 or surface476_north_wall_Text_c_handle == -1 or \
            surface506_north_wall_Text_c_handle == -1 or surface536_north_wall_Text_c_handle == -1 or \
            surface566_north_wall_Text_c_handle == -1 or surface596_north_wall_Text_c_handle == -1 or \
            surface14_east_wall_Text_c_handle == -1 or surface44_east_wall_Text_c_handle == -1 or \
            surface74_east_wall_Text_c_handle == -1 or surface104_east_wall_Text_c_handle == -1 or \
            surface134_east_wall_Text_c_handle == -1 or surface164_east_wall_Text_c_handle == -1 or \
            surface194_east_wall_Text_c_handle == -1 or surface224_east_wall_Text_c_handle == -1 or \
            surface254_east_wall_Text_c_handle == -1 or surface284_east_wall_Text_c_handle == -1 or \
            surface314_east_wall_Text_c_handle == -1 or surface344_east_wall_Text_c_handle == -1 or \
            surface374_east_wall_Text_c_handle == -1 or surface404_east_wall_Text_c_handle == -1 or \
            surface434_east_wall_Text_c_handle == -1 or surface464_east_wall_Text_c_handle == -1 or \
            surface494_east_wall_Text_c_handle == -1 or surface524_east_wall_Text_c_handle == -1 or \
            surface554_east_wall_Text_c_handle == -1 or surface584_east_wall_Text_c_handle == -1 or \
            surface10_west_wall_Text_c_handle == -1 or surface40_west_wall_Text_c_handle == -1 or \
            surface70_west_wall_Text_c_handle == -1 or surface100_west_wall_Text_c_handle == -1 or \
            surface130_west_wall_Text_c_handle == -1 or surface160_west_wall_Text_c_handle == -1 or \
            surface190_west_wall_Text_c_handle == -1 or surface220_west_wall_Text_c_handle == -1 or \
            surface250_west_wall_Text_c_handle == -1 or surface280_west_wall_Text_c_handle == -1 or \
            surface310_west_wall_Text_c_handle == -1 or surface340_west_wall_Text_c_handle == -1 or \
            surface370_west_wall_Text_c_handle == -1 or surface400_west_wall_Text_c_handle == -1 or \
            surface430_west_wall_Text_c_handle == -1 or surface460_west_wall_Text_c_handle == -1 or \
            surface490_west_wall_Text_c_handle == -1 or surface520_west_wall_Text_c_handle == -1 or \
            surface550_west_wall_Text_c_handle == -1 or surface580_west_wall_Text_c_handle == -1):

            print('20Stories_get_ep_results(): some handle not available')
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
        surface576_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface576_roof_Text_c_handle)
        surface582_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface582_roof_Text_c_handle)
        surface588_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface588_roof_Text_c_handle)
        surface594_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface594_roof_Text_c_handle)
        surface600_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface600_roof_Text_c_handle)

        roof_Text_c = (surface576_roof_Text_c + surface582_roof_Text_c + surface588_roof_Text_c + surface594_roof_Text_c + surface600_roof_Text_c) / 5

        surface1_floor_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface1_floor_Text_c_handle)
        surface7_floor_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface7_floor_Text_c_handle)
        surface13_floor_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface13_floor_Text_c_handle)
        surface19_floor_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface19_floor_Text_c_handle)
        surface25_floor_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface25_floor_Text_c_handle)

        floor_Text_c = (surface1_floor_Text_c + surface7_floor_Text_c + surface13_floor_Text_c + surface19_floor_Text_c + surface25_floor_Text_c) / 5

        surface2_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface2_south_wall_Text_c_handle)
        surface32_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface32_south_wall_Text_c_handle)
        surface62_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface62_south_wall_Text_c_handle)
        surface92_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface92_south_wall_Text_c_handle)
        surface122_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface122_south_wall_Text_c_handle)
        surface152_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface152_south_wall_Text_c_handle)
        surface182_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface182_south_wall_Text_c_handle)
        surface212_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface212_south_wall_Text_c_handle)
        surface242_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface242_south_wall_Text_c_handle)
        surface272_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface272_south_wall_Text_c_handle)
        surface302_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface302_south_wall_Text_c_handle)
        surface332_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface332_south_wall_Text_c_handle)
        surface362_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface362_south_wall_Text_c_handle)
        surface392_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface392_south_wall_Text_c_handle)
        surface422_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface422_south_wall_Text_c_handle)
        surface452_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface452_south_wall_Text_c_handle)
        surface482_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface482_south_wall_Text_c_handle)
        surface512_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface512_south_wall_Text_c_handle)
        surface542_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface542_south_wall_Text_c_handle)
        surface572_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface572_south_wall_Text_c_handle)

        south_wall_Text_c = (surface2_south_wall_Text_c + surface32_south_wall_Text_c + surface62_south_wall_Text_c + surface92_south_wall_Text_c + surface122_south_wall_Text_c + surface152_south_wall_Text_c + surface182_south_wall_Text_c + surface212_south_wall_Text_c + surface242_south_wall_Text_c + surface272_south_wall_Text_c + surface302_south_wall_Text_c + surface332_south_wall_Text_c + surface362_south_wall_Text_c + surface392_south_wall_Text_c + surface422_south_wall_Text_c + surface452_south_wall_Text_c + surface482_south_wall_Text_c + surface512_south_wall_Text_c + surface542_south_wall_Text_c + surface572_south_wall_Text_c) / 20

        surface26_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface26_north_wall_Text_c_handle)
        surface56_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface56_north_wall_Text_c_handle)
        surface86_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface86_north_wall_Text_c_handle)
        surface116_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface116_north_wall_Text_c_handle)
        surface146_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface146_north_wall_Text_c_handle)
        surface176_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface176_north_wall_Text_c_handle)
        surface206_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface206_north_wall_Text_c_handle)
        surface236_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface236_north_wall_Text_c_handle)
        surface266_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface266_north_wall_Text_c_handle)
        surface296_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface296_north_wall_Text_c_handle)
        surface326_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface326_north_wall_Text_c_handle)
        surface356_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface356_north_wall_Text_c_handle)
        surface386_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface386_north_wall_Text_c_handle)
        surface416_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface416_north_wall_Text_c_handle)
        surface446_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface446_north_wall_Text_c_handle)
        surface476_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface476_north_wall_Text_c_handle)
        surface506_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface506_north_wall_Text_c_handle)
        surface536_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface536_north_wall_Text_c_handle)
        surface566_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface566_north_wall_Text_c_handle)
        surface596_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface596_north_wall_Text_c_handle)

        north_wall_Text_c = (surface26_north_wall_Text_c + surface56_north_wall_Text_c + surface86_north_wall_Text_c + surface116_north_wall_Text_c + surface146_north_wall_Text_c + surface176_north_wall_Text_c + surface206_north_wall_Text_c + surface236_north_wall_Text_c + surface266_north_wall_Text_c + surface296_north_wall_Text_c + surface326_north_wall_Text_c + surface356_north_wall_Text_c + surface386_north_wall_Text_c + surface416_north_wall_Text_c + surface446_north_wall_Text_c + surface476_north_wall_Text_c + surface506_north_wall_Text_c + surface536_north_wall_Text_c + surface566_north_wall_Text_c + surface596_north_wall_Text_c) / 20

        coordination.ep_floor_Text_K = floor_Text_c + 273.15
        coordination.ep_roof_Text_K = roof_Text_c + 273.15

        coordination.ep_wallSun_Text_K = south_wall_Text_c + 273.15
        coordination.ep_wallShade_Text_K = north_wall_Text_c + 273.15

        coordination.sem3.release()

def Simplified_20Stories_get_ep_results(state):
    global get_ep_results_inited_handle, \
        hvac_heat_rejection_sensor_handle,\
        surface576_roof_Text_c_handle, surface582_roof_Text_c_handle, surface588_roof_Text_c_handle, \
        surface594_roof_Text_c_handle, surface600_roof_Text_c_handle, surface1_floor_Text_c_handle, \
        surface7_floor_Text_c_handle, surface13_floor_Text_c_handle, surface19_floor_Text_c_handle, \
        surface25_floor_Text_c_handle, \
        surface2_south_wall_Text_c_handle, surface302_south_wall_Text_c_handle, surface572_south_wall_Text_c_handle,\
    surface26_north_wall_Text_c_handle,surface326_north_wall_Text_c_handle, surface596_north_wall_Text_c_handle,\
    surface14_east_wall_Text_c_handle, surface314_east_wall_Text_c_handle, surface584_east_wall_Text_c_handle,\
    surface10_west_wall_Text_c_handle,surface310_west_wall_Text_c_handle, surface580_west_wall_Text_c_handle

    if not get_ep_results_inited_handle:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        get_ep_results_inited_handle = True
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,\
                                                             "HVAC System Total Heat Rejection Energy",\
                                                             "SIMHVAC")
        surface576_roof_Text_c_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                                            "Surface 576")
        surface582_roof_Text_c_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature", \
                                                                                            "Surface 582")
        surface588_roof_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 588")
        surface594_roof_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 594")
        surface600_roof_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 600")
        surface1_floor_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 1")
        surface7_floor_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 7")
        surface13_floor_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 13")
        surface19_floor_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 19")
        surface25_floor_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", \
                                "Surface 25")
        surface2_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 2")
        surface302_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 302")
        surface572_south_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 572")
        surface26_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 26")
        surface326_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 326")
        surface596_north_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 596")
        surface14_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 14")
        surface314_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 314")
        surface584_east_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 584")
        surface10_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 10")
        surface310_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 310")
        surface580_west_wall_Text_c_handle = coordination.ep_api.exchange.\
            get_variable_handle(state, "Surface Outside Face Temperature", "Surface 580")

        if (hvac_heat_rejection_sensor_handle == -1 or \
                surface576_roof_Text_c_handle == -1 or surface582_roof_Text_c_handle == -1 or \
                surface588_roof_Text_c_handle == -1 or surface594_roof_Text_c_handle == -1 or \
                surface600_roof_Text_c_handle == -1 or surface1_floor_Text_c_handle == -1 or \
                surface7_floor_Text_c_handle == -1 or surface13_floor_Text_c_handle == -1 or \
                surface19_floor_Text_c_handle == -1 or surface25_floor_Text_c_handle == -1 or \
            surface2_south_wall_Text_c_handle == -1 or surface302_south_wall_Text_c_handle == -1 or surface572_south_wall_Text_c_handle == -1 or \
            surface26_north_wall_Text_c_handle == -1 or surface326_north_wall_Text_c_handle == -1 or surface596_north_wall_Text_c_handle == -1 or \
            surface14_east_wall_Text_c_handle == -1 or surface314_east_wall_Text_c_handle == -1 or surface584_east_wall_Text_c_handle == -1 or \
            surface10_west_wall_Text_c_handle == -1 or surface310_west_wall_Text_c_handle == -1 or surface580_west_wall_Text_c_handle == -1):

            print('Simplified_20Stories_get_ep_results(): some handle not available')
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
        surface576_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface576_roof_Text_c_handle)
        surface582_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface582_roof_Text_c_handle)
        surface588_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface588_roof_Text_c_handle)
        surface594_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface594_roof_Text_c_handle)
        surface600_roof_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface600_roof_Text_c_handle)

        roof_Text_c = (surface576_roof_Text_c + surface582_roof_Text_c + surface588_roof_Text_c + surface594_roof_Text_c + surface600_roof_Text_c) / 5

        surface1_floor_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface1_floor_Text_c_handle)
        surface7_floor_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface7_floor_Text_c_handle)
        surface13_floor_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface13_floor_Text_c_handle)
        surface19_floor_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface19_floor_Text_c_handle)
        surface25_floor_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface25_floor_Text_c_handle)

        floor_Text_c = (surface1_floor_Text_c + surface7_floor_Text_c + surface13_floor_Text_c + surface19_floor_Text_c + surface25_floor_Text_c) / 5

        surface2_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface2_south_wall_Text_c_handle)
        surface302_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface302_south_wall_Text_c_handle)
        surface572_south_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface572_south_wall_Text_c_handle)

        south_wall_Text_c = (surface2_south_wall_Text_c + surface302_south_wall_Text_c * 18 + surface572_south_wall_Text_c) / 20

        surface26_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface26_north_wall_Text_c_handle)
        surface326_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface326_north_wall_Text_c_handle)
        surface596_north_wall_Text_c = coordination.ep_api.exchange.get_variable_value(state,surface596_north_wall_Text_c_handle)

        north_wall_Text_c = (surface26_north_wall_Text_c + surface326_north_wall_Text_c * 18 + surface596_north_wall_Text_c) / 20

        coordination.ep_floor_Text_K = floor_Text_c + 273.15
        coordination.ep_roof_Text_K = roof_Text_c + 273.15

        coordination.ep_wallSun_Text_K = south_wall_Text_c + 273.15
        coordination.ep_wallShade_Text_K = north_wall_Text_c + 273.15

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