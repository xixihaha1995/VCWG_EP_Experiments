import numpy as np
import pandas as pd, os
from VCWG_Hydrology import VCWG_Hydro
import _0_global_save
def add_date_index(df, start_date, time_interval_sec):
    '''
    df is [date, sensible/latent]
    '''
    date = pd.date_range(start_date, periods=len(df), freq='{}S'.format(time_interval_sec))
    date = pd.Series(date)
    # update dataframe index
    df.index = date
    return df
def save_data_to_csv(df, file_name, case_name):
    data_arr = np.array(_0_global_save.saving_data[file_name])
    df = pd.DataFrame(data_arr)
    if file_name == 'can_Averaged_temp_k_specHum_ratio_press_pa':
        df.columns = ['Temp_K', 'SpecHum_Ratio', 'Press_Pa']
    else:
        df.columns = [f'(m) {file_name}_' + str(0.5 + i) for i in range(len(df.columns))]
    df = add_date_index(df, start_time, time_interval_sec)
    # save to excel
    df.to_excel(os.path.join(_0_global_save.vcwg_ep_saving_path, f'{case_name}_{file_name}.xlsx'))

"""
Specify file and case names
Developed by Mohsen Moradi and Amir A. Aliabadi
Atmospheric Innovations Research (AIR) Laboratory, University of Guelph, Guelph, Canada
Last update: December 2020
"""
#Basel
# '''
epwFileName = 'Basel.epw'
TopForcingFileName = None
VCWGParamFileName = 'initialize_Basel_MOST.uwg'
ViewFactorFileName = '_BSPA_ViewFactor_Basel_MOST.txt'
# Case name to append output file names with
case = 'Basel_MOST'
# '''

# epwFileName = 'ERA5_Basel.epw'
# TopForcingFileName = None
# VCWGParamFileName = 'replicate_Basel_MOST.uwg'
# ViewFactorFileName = 'ViewFactor_Basel_MOST.txt'
# # Case name to append output file names with
# case = 'replicate_Basel_MOST'

#Vancouver
'''
epwFileName = 'TopForcing_year.epw'
TopForcingFileName = None
# TopForcingFileName = 'Vancouver2008_ERA5.csv'
VCWGParamFileName = 'replicate_Vancouver_LCZ1.uwg'
ViewFactorFileName = 'ViewFactor_Vancouver_LCZ1.txt'
# Case name to append output file names with
case = 'Replicate_Vancouver_LCZ1'
'''
_0_global_save.init_save_arr(_in_vcwg_ep_saving_path=
                             '..\EP_And_VCWG_v2.0.0\_2_saved\_1_BUBBLE_BSPA_detailed')
# Initialize the UWG object and run the simulation
VCWG = VCWG_Hydro(epwFileName,TopForcingFileName,VCWGParamFileName,ViewFactorFileName,case)
VCWG.run()

# Lichen: post process, such as [timestamp, waste heat] * time_steps_num

start_time = '2002-06-10 00:00:00'
time_interval_sec = 300
case_name = "_BSPA_"
data_name_lst = ['TempProfile_K', 'SpecHumProfile_Ratio', 'PressProfile_Pa', 'wind_vxProfile_mps',
                 'wind_vyProfile_mps', 'wind_SpeedProfile_mps', 'turbulence_tkeProfile_m2s2',
                 'air_densityProfile_kgm3', 'sensible_heat_fluxProfile_Wm2', 'latent_heat_fluxProfile_Wm2',
                 'can_Averaged_temp_k_specHum_ratio_press_pa']
for data_name in data_name_lst:
    save_data_to_csv(_0_global_save.saving_data[data_name], data_name, case_name)


