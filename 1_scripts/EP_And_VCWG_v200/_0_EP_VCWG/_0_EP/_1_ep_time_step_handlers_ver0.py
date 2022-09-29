from threading import Thread
from . import _0_vcwg_ep_coordination as coordination
from .._0_Modified_VCWG200.VCWG_Hydrology import VCWG_Hydro
import os

one_time = True
one_time_call_vcwg = True
accu_hvac_heat_rejection_J = 0
zone_time_step_seconds = 0
ep_last_accumulated_time_index_in_seconds = 0
ep_last_call_time_seconds = 0
def api_to_csv(state):
    orig = coordination.ep_api.exchange.list_available_api_data_csv(state)
    newFileByteArray = bytearray(orig)
    api_path = os.path.join(os.path.dirname(__file__), '..','..',coordination.ep_files_path, 'api_data.csv')
    newFile = open(api_path, "wb")
    newFile.write(newFileByteArray)
    newFile.close()
def run_vcwg():
    epwFileName = 'Basel.epw'
    TopForcingFileName = None
    # VCWGParamFileName = 'initialize_Basel_BSPA_MOST.uwg'
    VCWGParamFileName = '_case5_initialize_Basel_BSPR_MOST.uwg'
    # ViewFactorFileName = '_BSPA_ViewFactor_Basel_MOST.txt'
    ViewFactorFileName = '_case5_BSPR_ViewFactor_Basel_MOST.txt'
    # Case name to append output file names with
    # case = '_BSPA_Refinement_M2_Basel_MOST'
    case = '_BSPR_Refinement_M2_Basel_MOST'

    # '''

    # epwFileName = 'TopForcing_year.epw'
    # TopForcingFileName = None
    # # TopForcingFileName = 'Vancouver2008_ERA5.csv'
    # VCWGParamFileName = 'initialize_Vancouver_LCZ1.uwg'
    # ViewFactorFileName = 'ViewFactor_Vancouver_LCZ1.txt'
    # # Case name to append output file names with
    # case = '_bypass_year_Vancouver_LCZ1'

    # Initialize the UWG object and run the simulation
    VCWG = VCWG_Hydro(epwFileName, TopForcingFileName, VCWGParamFileName, ViewFactorFileName, case)
    VCWG.run()

def _nested_ep_then_vcwg(state):
    global one_time,one_time_call_vcwg,\
        odb_actuator_handle, orh_actuator_handle, wsped_mps_actuator_handle, wdir_deg_actuator_handle,\
        zone_indor_temp_sensor_handle, zone_indor_spe_hum_sensor_handle, zone_flr_area_handle,\
        sens_cool_demand_sensor_handle, sens_heat_demand_sensor_handle, \
        cool_consumption_sensor_handle, heat_consumption_sensor_handle, \
        hvac_heat_rejection_sensor_handle, elec_bld_meter_handle,\
        floor_interior_conv_handle, floor_interior_lwr_otr_faces_handle, \
        floor_interior_lwr_intGain_handle, floor_interior_lwr_hvac_handle,\
        floor_interior_swr_lights_handle, floor_interior_swr_solar_handle, \
        wall_interior_conv_handle, wall_interior_lwr_otr_faces_handle, \
        wall_interior_lwr_intGain_handle, wall_interior_lwr_hvac_handle, \
        wall_interior_swr_lights_handle, wall_interior_swr_solar_handle, \
        roof_interior_conv_handle, roof_interior_lwr_otr_faces_handle, \
        roof_interior_lwr_intGain_handle, roof_interior_lwr_hvac_handle, \
        roof_interior_swr_lights_handle, roof_interior_swr_solar_handle,\
        gsw_flr_Text_handle, gnw_flr_Text_handle, gse_office_flr_Text_handle, gne_flr_Text_handle, \
        gn1_flr_Text_handle, gn2_flr_Text_handle, gs1_flr_Text_handle, gs2_flr_Text_handle, \
        tsw_roof_Text_handle, tnw_roof_Text_handle, tse_roof_Text_handle, tne_roof_Text_handle, \
        tn1_roof_Text_handle, tn2_roof_Text_handle, ts1_roof_Text_handle, ts2_roof_Text_handle, \
        t_cor_roof_Text_handle,\
        gsw_flr_Tint_handle, gnw_flr_Tint_handle, gse_office_flr_Tint_handle, gne_flr_Tint_handle, \
        gn1_flr_Tint_handle, gn2_flr_Tint_handle, gs1_flr_Tint_handle, gs2_flr_Tint_handle, \
        tsw_roof_Tint_handle, tnw_roof_Tint_handle, tse_roof_Tint_handle, tne_roof_Tint_handle, \
        tn1_roof_Tint_handle, tn2_roof_Tint_handle, ts1_roof_Tint_handle, ts2_roof_Tint_handle, \
        t_cor_roof_Tint_handle,\
        gsw_wall_Text_handle, gse_office_wall_Text_handle, gs1_wall_Text_handle, gs2_wall_Text_handle,\
        msw_wall_Text_handle, mse_wall_Text_handle, ms1_wall_Text_handle, ms2_wall_Text_handle,\
        tsw_wall_Text_handle, tse_wall_Text_handle, ts1_wall_Text_handle, ts2_wall_Text_handle,\
        gnw_wall_Text_handle, gne_wall_Text_handle, gn1_wall_Text_handle, gn2_wall_Text_handle,\
        mnw_wall_Text_handle, mne_wall_Text_handle, mn1_wall_Text_handle, mn2_wall_Text_handle,\
        tnw_wall_Text_handle, tne_wall_Text_handle, tn1_wall_Text_handle, tn2_wall_Text_handle,\
        gsw_wall_Tint_handle, gse_office_wall_Tint_handle, gs1_wall_Tint_handle, gs2_wall_Tint_handle,\
        msw_wall_Tint_handle, mse_wall_Tint_handle, ms1_wall_Tint_handle, ms2_wall_Tint_handle,\
        tsw_wall_Tint_handle, tse_wall_Tint_handle, ts1_wall_Tint_handle, ts2_wall_Tint_handle,\
        gnw_wall_Tint_handle, gne_wall_Tint_handle, gn1_wall_Tint_handle, gn2_wall_Tint_handle,\
        mnw_wall_Tint_handle, mne_wall_Tint_handle, mn1_wall_Tint_handle, mn2_wall_Tint_handle,\
        tnw_wall_Tint_handle, tne_wall_Tint_handle, tn1_wall_Tint_handle, tn2_wall_Tint_handle,\
        gsw_solar_handle, gse_office_solar_handle, gs1_solar_handle, gs2_solar_handle,\
        msw_solar_handle, mse_solar_handle, ms1_solar_handle, ms2_solar_handle,\
        tsw_solar_handle, tse_solar_handle, ts1_solar_handle, ts2_solar_handle,\
        gnw_solar_handle, gne_solar_handle, gn1_solar_handle, gn2_solar_handle,\
        mnw_solar_handle, mne_solar_handle, mn1_solar_handle, mn2_solar_handle,\
        tnw_solar_handle, tne_solar_handle, tn1_solar_handle, tn2_solar_handle

    if one_time:
        if not coordination.ep_api.exchange.api_data_fully_ready(state):
            return
        one_time = False
        api_to_csv(state)
        odb_actuator_handle = coordination.ep_api.exchange.get_actuator_handle(
            state, "Weather Data", "Outdoor Dry Bulb",
            "Environment")
        orh_actuator_handle = coordination.ep_api.exchange.get_actuator_handle(
            state, "Weather Data", "Outdoor Relative Humidity",
            "Environment")

        wsped_mps_actuator_handle = coordination.ep_api.exchange.get_actuator_handle(
            state, "Weather Data", "Wind Speed", "Environment")
        wdir_deg_actuator_handle = coordination.ep_api.exchange.get_actuator_handle(
            state, "Weather Data", "Wind Direction", "Environment")

        gsw_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                             "g GFloor SWA")
        gnw_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                               "g GFloor NWA")
        gse_office_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                       "g GFloor SEA")
        gne_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                 "g GFloor NEA")
        gn1_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                             "g GFloor N1A")
        gn2_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                             "g GFloor N2A")
        gs1_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                             "g GFloor S1A")
        gs2_flr_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                             "g GFloor S2A")
        tsw_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                              "t Roof SWA")
        tnw_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                              "t Roof NWA")
        tse_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                              "t Roof SEA")
        tne_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                              "t Roof NEA")
        tn1_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                              "t Roof N1A")
        tn2_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                              "t Roof N2A")
        ts1_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                              "t Roof S1A")
        ts2_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                              "t Roof S2A")
        t_cor_roof_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                  "t Roof C")
        gsw_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                               "g GFloor SWA")
        gnw_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                               "g GFloor NWA")
        gse_office_flr_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
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
        tsw_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "t Roof SWA")
        tnw_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "t Roof NWA")
        tse_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "t Roof SEA")
        tne_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "t Roof NEA")
        tn1_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "t Roof N1A")
        tn2_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "t Roof N2A")
        ts1_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "t Roof S1A")
        ts2_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "t Roof S2A")
        t_cor_roof_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                  "t Roof C")

        gsw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "g SWall SWA")
        gse_office_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "g SWall SEA")
        gs1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "g SWall S1A")
        gs2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "g SWall S2A")
        msw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "m SWall SWA")
        mse_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                       "m SWall SEA")
        ms1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "m SWall S1A")
        ms2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "m SWall S2A")
        tsw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "t SWall SWA")
        tse_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                       "t SWall SEA")
        ts1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "t SWall S1A")
        ts2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "t SWall S2A")
        gnw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "g NWall NWA")
        gne_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "g NWall NEA")
        gn1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "g NWall N1A")
        gn2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "g NWall N2A")
        mnw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "m NWall NWA")
        mne_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "m NWall NEA")
        mn1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "m NWall N1A")
        mn2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "m NWall N2A")
        tnw_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "t NWall NWA")
        tne_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "t NWall NEA")
        tn1_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "t NWall N1A")
        tn2_wall_Text_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Temperature",
                                                                                "t NWall N2A")
        gsw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "g SWall SWA")
        gse_office_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "g SWall SEA")
        gs1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "g SWall S1A")
        gs2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "g SWall S2A")
        msw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "m SWall SWA")
        mse_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "m SWall SEA")
        ms1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "m SWall S1A")
        ms2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "m SWall S2A")
        tsw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "t SWall SWA")
        tse_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "t SWall SEA")
        ts1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "t SWall S1A")
        ts2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "t SWall S2A")
        gnw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "g NWall NWA")
        gne_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "g NWall NEA")
        gn1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "g NWall N1A")
        gn2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "g NWall N2A")
        mnw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "m NWall NWA")
        mne_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "m NWall NEA")
        mn1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "m NWall N1A")
        mn2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "m NWall N2A")
        tnw_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "t NWall NWA")
        tne_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "t NWall NEA")
        tn1_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "t NWall N1A")
        tn2_wall_Tint_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Inside Face Temperature",
                                                                                "t NWall N2A")
        gsw_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "g SWall SWA")
        gse_office_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "g SWall SEA")
        gs1_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "g SWall S1A")
        gs2_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "g SWall S2A")
        msw_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "m SWall SWA")
        mse_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "m SWall SEA")
        ms1_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "m SWall S1A")
        ms2_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "m SWall S2A")
        tsw_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "t SWall SWA")
        tse_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "t SWall SEA")
        ts1_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "t SWall S1A")
        ts2_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "t SWall S2A")
        gnw_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "g NWall NWA")
        gne_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "g NWall NEA")
        gn1_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "g NWall N1A")
        gn2_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "g NWall N2A")
        mnw_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "m NWall NWA")
        mne_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "m NWall NEA")
        mn1_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "m NWall N1A")
        mn2_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "m NWall N2A")
        tnw_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "t NWall NWA")
        tne_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "t NWall NEA")
        tn1_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "t NWall N1A")
        tn2_solar_handle = coordination.ep_api.exchange.get_variable_handle(state, "Surface Outside Face Incident Solar Radiation Rate per Area",
                                                                            "t NWall N2A")

        zone_indor_temp_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Zone Air Temperature","T S1 APARTMENT")
        zone_indor_spe_hum_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Zone Air Humidity Ratio","T S1 APARTMENT")
        zone_flr_area_handle =  coordination.ep_api.exchange.get_internal_variable_handle(state, "Zone Floor Area",
                                                                          "T S1 APARTMENT")
        sens_cool_demand_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Zone Air System Sensible Cooling Rate",
                                                                          "T S1 APARTMENT")
        sens_heat_demand_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Zone Air System Sensible Heating Rate",
                                                                            "T S1 APARTMENT")
        cool_consumption_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Cooling Coil Electricity Rate",
                                                                            "SPLITSYSTEMAC:23_UNITARY_PACKAGE_COOLCOIL")
        heat_consumption_sensor_handle = coordination.ep_api.exchange.get_variable_handle(state,"Heating Coil Heating Rate",
                                                                            "SPLITSYSTEMAC:23_UNITARY_PACKAGE_HEATCOIL")
        hvac_heat_rejection_sensor_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "HVAC System Total Heat Rejection Energy",
                                             "SIMHVAC")
        elec_bld_meter_handle = coordination.ep_api.exchange.get_meter_handle(state, "Electricity:Building")

        floor_interior_conv_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "Surface Inside Face Convection Heat Gain Rate per Area",
                                             "t GFloor S1A")
        floor_interior_lwr_otr_faces_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "Surface Inside Face Net Surface Thermal Radiation Heat Gain Rate per Area",
                                             "t GFloor S1A")
        floor_interior_lwr_intGain_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "Surface Inside Face Internal Gains Radiation Heat Gain Rate per Area",
                                             "t GFloor S1A")
        floor_interior_lwr_hvac_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "Surface Inside Face System Radiation Heat Gain Rate per Area",
                                             "t GFloor S1A")
        floor_interior_swr_lights_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "Surface Inside Face Lights Radiation Heat Gain Rate per Area",
                                             "t GFloor S1A")
        floor_interior_swr_solar_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                             "Surface Inside Face Solar Radiation Heat Gain Rate per Area",
                                             "t GFloor S1A")

        wall_interior_conv_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                                "Surface Inside Face Convection Heat Gain Rate per Area",
                                                "t SWall S1A")
        wall_interior_lwr_otr_faces_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Net Surface Thermal Radiation Heat Gain Rate per Area",
                                            "t SWall S1A")
        wall_interior_lwr_intGain_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Internal Gains Radiation Heat Gain Rate per Area",
                                            "t SWall S1A")
        wall_interior_lwr_hvac_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face System Radiation Heat Gain Rate per Area",
                                            "t SWall S1A")
        wall_interior_swr_lights_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Lights Radiation Heat Gain Rate per Area",
                                            "t SWall S1A")
        wall_interior_swr_solar_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Solar Radiation Heat Gain Rate per Area",
                                            "t SWall S1A")

        roof_interior_conv_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Convection Heat Gain Rate per Area",
                                            "t Roof S1A")
        roof_interior_lwr_otr_faces_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Net Surface Thermal Radiation Heat Gain Rate per Area",
                                            "t Roof S1A")
        roof_interior_lwr_intGain_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Internal Gains Radiation Heat Gain Rate per Area",
                                            "t Roof S1A")
        roof_interior_lwr_hvac_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face System Radiation Heat Gain Rate per Area",
                                            "t Roof S1A")
        roof_interior_swr_lights_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Lights Radiation Heat Gain Rate per Area",
                                            "t Roof S1A")
        roof_interior_swr_solar_handle = \
            coordination.ep_api.exchange.get_variable_handle(state,
                                            "Surface Inside Face Solar Radiation Heat Gain Rate per Area",
                                            "t Roof S1A")




    warm_up = coordination.ep_api.exchange.warmup_flag(state)
    if not warm_up:
        # Lichen: After EP warm up, start to call VCWG
        if one_time_call_vcwg:
            global zone_time_step_seconds, zone_floor_area_m2, ep_last_call_time_seconds
            zone_time_step_seconds = 3600 / coordination.ep_api.exchange.num_time_steps_in_hour(state)
            zone_floor_area_m2 = coordination.ep_api.exchange.get_internal_variable_value(state,zone_flr_area_handle)
            one_time_call_vcwg = False
            Thread(target=run_vcwg).start()

        coordination.sem_vcwg.acquire()
        curr_sim_time_in_hours = coordination.ep_api.exchange.current_sim_time(state)
        curr_sim_time_in_seconds = curr_sim_time_in_hours * 3600
        # print("EP: curr_sim_time_in_seconds: ", curr_sim_time_in_seconds)
        # Should always accumulate, since system time always advances
        accumulated_time_in_seconds = curr_sim_time_in_seconds - ep_last_call_time_seconds
        ep_last_call_time_seconds = curr_sim_time_in_seconds
        hvac_heat_rejection_J = coordination.ep_api.exchange.get_variable_value(state, hvac_heat_rejection_sensor_handle)
        hvac_waste_w_m2 = hvac_heat_rejection_J / accumulated_time_in_seconds / coordination.blf_floor_area_m2
        coordination.ep_sensWaste_w_m2_per_floor_area += hvac_waste_w_m2

        time_index_alignment_bool =  1 > abs(curr_sim_time_in_seconds - coordination.vcwg_needed_time_idx_in_seconds)

        if not time_index_alignment_bool:
            # print("EP: curr_sim_time_in_seconds: ", curr_sim_time_in_seconds)
            # print("EP: vcwg_needed_time_idx_in_seconds: ", coordination.vcwg_needed_time_idx_in_seconds)
            coordination.sem_vcwg.release()
            return

        psychrometric = coordination.ep_api.functional.psychrometrics(state)
        rh = psychrometric.relative_humidity_b(state, coordination.vcwg_canTemp_K - 273.15,
                                               coordination.vcwg_canSpecHum_Ratio, coordination.vcwg_canPress_Pa)
        zone_indor_temp_value = coordination.ep_api.exchange.get_variable_value(state, zone_indor_temp_sensor_handle)
        zone_indor_spe_hum_value = coordination.ep_api.exchange.get_variable_value(state, zone_indor_spe_hum_sensor_handle)
        sens_cool_demand_w_value = coordination.ep_api.exchange.get_variable_value(state, sens_cool_demand_sensor_handle)
        sens_cool_demand_w_m2_value = sens_cool_demand_w_value / zone_floor_area_m2
        sens_heat_demand_w_value = coordination.ep_api.exchange.get_variable_value(state, sens_heat_demand_sensor_handle)
        sens_heat_demand_w_m2_value = sens_heat_demand_w_value / zone_floor_area_m2
        cool_consumption_w_value = coordination.ep_api.exchange.get_variable_value(state, cool_consumption_sensor_handle)
        cool_consumption_w_m2_value = cool_consumption_w_value / zone_floor_area_m2
        heat_consumption_w_value = coordination.ep_api.exchange.get_variable_value(state, heat_consumption_sensor_handle)
        heat_consumption_w_m2_value = heat_consumption_w_value / zone_floor_area_m2

        elec_bld_meter_j_hourly = coordination.ep_api.exchange.get_variable_value(state, elec_bld_meter_handle)
        elec_bld_meter_w_m2 = elec_bld_meter_j_hourly / 3600 / coordination.blf_floor_area_m2

        floor_interior_conv = coordination.ep_api.exchange.get_variable_value(state, floor_interior_conv_handle)
        floor_interior_lwr_otr_faces = coordination.ep_api.exchange.get_variable_value(state, floor_interior_lwr_otr_faces_handle)
        floor_interior_lwr_intGain = coordination.ep_api.exchange.get_variable_value(state, floor_interior_lwr_intGain_handle)
        floor_interior_lwr_hvac = coordination.ep_api.exchange.get_variable_value(state, floor_interior_lwr_hvac_handle)
        floor_interior_swr_lights = coordination.ep_api.exchange.get_variable_value(state, floor_interior_swr_lights_handle)
        floor_interior_swr_solar = coordination.ep_api.exchange.get_variable_value(state, floor_interior_swr_solar_handle)
        floor_flux = floor_interior_conv + floor_interior_lwr_otr_faces + floor_interior_lwr_intGain + \
                        floor_interior_lwr_hvac + floor_interior_swr_lights + floor_interior_swr_solar

        wall_interior_conv = coordination.ep_api.exchange.get_variable_value(state, wall_interior_conv_handle)
        wall_interior_lwr_otr_faces = coordination.ep_api.exchange.get_variable_value(state, wall_interior_lwr_otr_faces_handle)
        wall_interior_lwr_intGain = coordination.ep_api.exchange.get_variable_value(state, wall_interior_lwr_intGain_handle)
        wall_interior_lwr_hvac = coordination.ep_api.exchange.get_variable_value(state, wall_interior_lwr_hvac_handle)
        wall_interior_swr_lights = coordination.ep_api.exchange.get_variable_value(state, wall_interior_swr_lights_handle)
        wall_interior_swr_solar = coordination.ep_api.exchange.get_variable_value(state, wall_interior_swr_solar_handle)
        wall_flux = wall_interior_conv + wall_interior_lwr_otr_faces + wall_interior_lwr_intGain + \
                        wall_interior_lwr_hvac + wall_interior_swr_lights + wall_interior_swr_solar
        roof_interior_conv = coordination.ep_api.exchange.get_variable_value(state, roof_interior_conv_handle)
        roof_interior_lwr_otr_faces = coordination.ep_api.exchange.get_variable_value(state, roof_interior_lwr_otr_faces_handle)
        roof_interior_lwr_intGain = coordination.ep_api.exchange.get_variable_value(state, roof_interior_lwr_intGain_handle)
        roof_interior_lwr_hvac = coordination.ep_api.exchange.get_variable_value(state, roof_interior_lwr_hvac_handle)
        roof_interior_swr_lights = coordination.ep_api.exchange.get_variable_value(state, roof_interior_swr_lights_handle)
        roof_interior_swr_solar = coordination.ep_api.exchange.get_variable_value(state, roof_interior_swr_solar_handle)
        roof_flux = roof_interior_conv + roof_interior_lwr_otr_faces + roof_interior_lwr_intGain + \
                        roof_interior_lwr_hvac + roof_interior_swr_lights + roof_interior_swr_solar

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
                        gn1_flr_Text_c + gn2_flr_Text_c + gs1_flr_Text_c + gs2_flr_Text_c)/8
        floor_Tint_C = (gsw_flr_Tint_c + gnw_flr_Tint_c + gse_flr_Tint_c + gne_flr_Tint_c +
                        gn1_flr_Tint_c + gn2_flr_Tint_c + gs1_flr_Tint_c + gs2_flr_Tint_c)/8

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
                        tn1_roof_Text_c + tn2_roof_Text_c + ts1_roof_Text_c + ts2_roof_Text_c + t_cor_roof_Text_c)/9
        roof_Tint_C = (tsw_roof_Tint_c + tnw_roof_Tint_c + tse_roof_Tint_c + tne_roof_Tint_c +
                          tn1_roof_Tint_c + tn2_roof_Tint_c + ts1_roof_Tint_c + ts2_roof_Tint_c + t_cor_roof_Tint_c)/9

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
                            msw_wall_Text_c*2 + mse_wall_Text_c*2 + ms1_wall_Text_c*2 + ms2_wall_Text_c*2 +
                            tsw_wall_Text_c + tse_wall_Text_c + ts1_wall_Text_c + ts2_wall_Text_c)/16
        s_wall_Tint_C = (gsw_wall_Tint_c + gse_wall_Tint_c + gs1_wall_Tint_c + gs2_wall_Tint_c +
                        msw_wall_Tint_c*2 + mse_wall_Tint_c*2 + ms1_wall_Tint_c*2 + ms2_wall_Tint_c*2 +
                        tsw_wall_Tint_c + tse_wall_Tint_c + ts1_wall_Tint_c + ts2_wall_Tint_c)/16

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
                         mnw_wall_Text_c*2 + mne_wall_Text_c*2 + mn1_wall_Text_c*2 + mn2_wall_Text_c*2 +
                         tnw_wall_Text_c + tne_wall_Text_c + tn1_wall_Text_c + tn2_wall_Text_c)/16
        n_wall_Tint_C = (gnw_wall_Tint_c + gne_wall_Tint_c + gn1_wall_Tint_c + gn2_wall_Tint_c +
                         mnw_wall_Tint_c*2 + mne_wall_Tint_c*2 + mn1_wall_Tint_c*2 + mn2_wall_Tint_c*2 +
                         tnw_wall_Tint_c + tne_wall_Tint_c + tn1_wall_Tint_c + tn2_wall_Tint_c)/16

        gsw_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, gsw_solar_handle)
        gse_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, gse_office_solar_handle)
        gs1_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, gs1_solar_handle)
        gs2_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, gs2_solar_handle)
        msw_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, msw_solar_handle)
        mse_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, mse_solar_handle)
        ms1_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, ms1_solar_handle)
        ms2_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, ms2_solar_handle)
        tsw_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, tsw_solar_handle)
        tse_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, tse_solar_handle)
        ts1_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, ts1_solar_handle)
        ts2_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, ts2_solar_handle)

        gnw_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, gnw_solar_handle)
        gne_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, gne_solar_handle)
        gn1_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, gn1_solar_handle)
        gn2_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, gn2_solar_handle)
        mnw_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, mnw_solar_handle)
        mne_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, mne_solar_handle)
        mn1_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, mn1_solar_handle)
        mn2_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, mn2_solar_handle)
        tnw_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, tnw_solar_handle)
        tne_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, tne_solar_handle)
        tn1_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, tn1_solar_handle)
        tn2_solar_w_m2 = coordination.ep_api.exchange.get_variable_value(state, tn2_solar_handle)


        s_wall_solar_w_m2 = (gsw_solar_w_m2 + gse_solar_w_m2 + gs1_solar_w_m2 + gs2_solar_w_m2 +
                             msw_solar_w_m2*2 + mse_solar_w_m2*2 + ms1_solar_w_m2*2 + ms2_solar_w_m2*2 +
                             tsw_solar_w_m2 + tse_solar_w_m2 + ts1_solar_w_m2 + ts2_solar_w_m2)/16

        n_wall_solar_w_m2 = (gnw_solar_w_m2 + gne_solar_w_m2 + gn1_solar_w_m2 + gn2_solar_w_m2 +
                             mnw_solar_w_m2*2 + mne_solar_w_m2*2 + mn1_solar_w_m2*2 + mn2_solar_w_m2*2 +
                             tnw_solar_w_m2 + tne_solar_w_m2 + tn1_solar_w_m2 + tn2_solar_w_m2)/16

        coordination.ep_api.exchange.set_actuator_value(state, odb_actuator_handle, coordination.vcwg_canTemp_K - 273.15)
        coordination.ep_api.exchange.set_actuator_value(state, orh_actuator_handle, rh)

        coordination.ep_floor_Text_K = floor_Text_C + 273.15
        coordination.ep_floor_Tint_K = floor_Tint_C + 273.15

        coordination.ep_roof_Text_K = roof_Text_C + 273.15
        coordination.ep_roof_Tint_K = roof_Tint_C + 273.15

        coordination.ep_wallSun_Text_K = s_wall_Text_C + 273.15
        coordination.ep_wallSun_Tint_K = s_wall_Tint_C + 273.15
        coordination.ep_wallShade_Text_K = s_wall_Text_C + 273.15
        coordination.ep_wallShade_Tint_K = s_wall_Tint_C + 273.15

        coordination.ep_elecTotal_w_m2_per_floor_area = elec_bld_meter_w_m2
        coordination.ep_indoorTemp_C = zone_indor_temp_value
        coordination.ep_indoorHum_Ratio = zone_indor_spe_hum_value
        coordination.ep_sensCoolDemand_w_m2 = sens_cool_demand_w_m2_value
        coordination.ep_sensHeatDemand_w_m2 = sens_heat_demand_w_m2_value
        coordination.ep_coolConsump_w_m2 = cool_consumption_w_m2_value
        coordination.ep_heatConsump_w_m2 = heat_consumption_w_m2_value
        coordination.ep_floor_fluxMass_w_m2 = floor_flux
        coordination.ep_fluxWall_w_m2 = wall_flux
        coordination.ep_fluxRoof_w_m2 = roof_flux

        coordination.sem_energyplus.release()
