import numpy as np
def init_save_arr(_in_vcwg_ep_saving_path = '..\EP_And_VCWG_v2.0.0\_2_saved\BUBBLE_VCWG-EP-detailed'):
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

    vcwg_ep_saving_path = _in_vcwg_ep_saving_path