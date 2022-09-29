import _0_all_plot_tools as plt_tools
import pandas as pd
results_folder = r'..\_2_saved\BUBBLE_VCWG-EP-refine_idf'
IOP_start_time = '2002-06-10 01:00:00'
IOP_end_time = '2002-07-09 22:50:00'

vcwg_output_time_interval_seconds = 3600
v200_start_time = '2002-06-14 00:00:00'
v200_end_time = '2002-06-30 23:00:00'
v132_start_time = '2002-06-15 00:00:00'
v132_end_time = '2002-06-29 23:00:00'

compare_start_time = '2002-06-20 00:00:00'
compare_end_time = '2002-06-27 23:00:00'

v200_sensor_height = 2.6
p0 = 100000

ue1_col_idx = 0
re1_col_idx = 7
# Read air temperature measurements
urban_all_sites_10min_dirty = plt_tools.read_text_as_csv(f'{results_folder}\\BUBBLE_BSPR_AT_PROFILE_IOP.txt',
                                                          header=0, index_col=0, skiprows=16)
# clean the measurements
urban_all_sites_hour = plt_tools.clean_bubble_iop(urban_all_sites_10min_dirty,
                                                  start_time = IOP_start_time, end_time = IOP_end_time)
# select the 0th column as the comparison data
urban_2p6_hour_c = urban_all_sites_hour.iloc[:,ue1_col_idx]
urban_2p6_hour_c_compare = urban_2p6_hour_c[compare_start_time:compare_end_time]

mixed_all_sites_10min_dirty = plt_tools.read_text_as_csv(f'{results_folder}\\BUBBLE_AT_IOP.txt',
                                                            header=0, index_col=0, skiprows=25)
# clean the measurements
mixed_all_sites_hour = plt_tools.clean_bubble_iop(mixed_all_sites_10min_dirty,
                                                    start_time = IOP_start_time, end_time = IOP_end_time)
# Keep original index, only select one column and keep the column name
rural_1p5_hour_c = mixed_all_sites_hour.iloc[:,re1_col_idx]
rural_1p5_hour_c_compare = rural_1p5_hour_c[compare_start_time:compare_end_time]

# Read the VCWG potential temperature
v200_BaselEPW_th_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\th_profiles_v200_BaselEPW_Basel_MOST.txt')
v200_BaselEPW_th_profile_hours_height_spin = plt_tools.certain_height_one_day(
    v200_BaselEPW_th_profile_hours, v200_sensor_height)
v200_BaselEPW_th_profile_hours_height_spin_date = plt_tools.add_date_index(v200_BaselEPW_th_profile_hours_height_spin,
                                                                    v200_start_time,
                                                                    vcwg_output_time_interval_seconds)
v200_BaselEPW_th_profile_hours_height_K = v200_BaselEPW_th_profile_hours_height_spin_date\
    .loc[compare_start_time:compare_end_time]
v200_BaselEPW_th_profile_hours_height_C = v200_BaselEPW_th_profile_hours_height_K - 273.15

v200_BaselEPW_presProf_hour = plt_tools.read_text_as_csv(f'{results_folder}\\presProf_profiles_v200_BaselEPW_Basel_MOST.txt')
v200_BaselEPW_presProf_hour_height_spin = plt_tools.certain_height_one_day(
    v200_BaselEPW_presProf_hour, v200_sensor_height)
v200_BaselEPW_presProf_hour_height_spin_date = plt_tools.add_date_index(v200_BaselEPW_presProf_hour_height_spin,
                                                                    v200_start_time,
                                                                    vcwg_output_time_interval_seconds)
v200_BaselEPW_presProf_hour_height = v200_BaselEPW_presProf_hour_height_spin_date\
    .loc[compare_start_time:compare_end_time]
v200_BaselEPW_real_temp_profile_hours_height_K_arr = v200_BaselEPW_th_profile_hours_height_K\
    .values * (v200_BaselEPW_presProf_hour_height.values / p0) ** 0.286
v200_BaselEPW_real_temp_profile_hours_height_K = pd.DataFrame(v200_BaselEPW_real_temp_profile_hours_height_K_arr,
                                                                index=v200_BaselEPW_th_profile_hours_height_K.index,)
v200_BaselEPW_real_temp_profile_hours_height_K = v200_BaselEPW_real_temp_profile_hours_height_K.squeeze()
v200_BaselEPW_real_temp_profile_hours_height_C = v200_BaselEPW_real_temp_profile_hours_height_K - 273.15

reference_th_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\th_profiles_Reference_Basel_MOST.txt')
reference_th_profile_hours_height_spin = plt_tools.certain_height_one_day(
    reference_th_profile_hours, v200_sensor_height)
reference_th_profile_hours_height_spin_date = plt_tools.add_date_index(reference_th_profile_hours_height_spin,
                                                                    v200_start_time,
                                                                    vcwg_output_time_interval_seconds)
reference_th_profile_hours_height_K = reference_th_profile_hours_height_spin_date\
    .loc[compare_start_time:compare_end_time]
reference_th_profile_hours_height_C = reference_th_profile_hours_height_K - 273.15

reference_presProf_hour = plt_tools.read_text_as_csv(f'{results_folder}\\presProf_profiles_Reference_Basel_MOST.txt')
reference_presProf_hour_height_spin = plt_tools.certain_height_one_day(
    reference_presProf_hour, v200_sensor_height)
reference_presProf_hour_height_spin_date = plt_tools.add_date_index(reference_presProf_hour_height_spin,
                                                                    v200_start_time,
                                                                    vcwg_output_time_interval_seconds)
reference_presProf_hour_height = reference_presProf_hour_height_spin_date\
    .loc[compare_start_time:compare_end_time]
reference_real_temp_profile_hours_height_K_arr = reference_th_profile_hours_height_K\
    .values * (reference_presProf_hour_height.values / p0) ** 0.286
reference_real_temp_profile_hours_height_K = pd.DataFrame(reference_real_temp_profile_hours_height_K_arr,
                                                                index=reference_th_profile_hours_height_K.index,)
reference_real_temp_profile_hours_height_K = reference_real_temp_profile_hours_height_K.squeeze()
reference_real_temp_profile_hours_height_C = reference_real_temp_profile_hours_height_K - 273.15

refining_th_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\th_profiles_Refinement_Basel_MOST.txt')
refining_th_profile_hours_height_spin = plt_tools.certain_height_one_day(
    refining_th_profile_hours, v200_sensor_height)
refining_th_profile_hours_height_spin_date = plt_tools.add_date_index(refining_th_profile_hours_height_spin,
                                                                    v200_start_time,
                                                                    vcwg_output_time_interval_seconds)
refining_th_profile_hours_height_K = refining_th_profile_hours_height_spin_date\
    .loc[compare_start_time:compare_end_time]
refining_th_profile_hours_height_C = refining_th_profile_hours_height_K - 273.15

refining_presProf_hour = plt_tools.read_text_as_csv(f'{results_folder}\\presProf_profiles_Refinement_Basel_MOST.txt')
refining_presProf_hour_height_spin = plt_tools.certain_height_one_day(
    refining_presProf_hour, v200_sensor_height)
refining_presProf_hour_height_spin_date = plt_tools.add_date_index(refining_presProf_hour_height_spin,
                                                                    v200_start_time,
                                                                    vcwg_output_time_interval_seconds)
refining_presProf_hour_height = refining_presProf_hour_height_spin_date\
    .loc[compare_start_time:compare_end_time]
refining_real_temp_profile_hours_height_K_arr = refining_th_profile_hours_height_K\
    .values * (refining_presProf_hour_height.values / p0) ** 0.286
refining_real_temp_profile_hours_height_K = pd.DataFrame(refining_real_temp_profile_hours_height_K_arr,
                                                                index=refining_th_profile_hours_height_K.index,)
refining_real_temp_profile_hours_height_K = refining_real_temp_profile_hours_height_K.squeeze()
refining_real_temp_profile_hours_height_C = refining_real_temp_profile_hours_height_K - 273.15

# convert to diurnal cycle
urban_2p6_hour_c_compare_dc = urban_2p6_hour_c_compare.groupby(urban_2p6_hour_c_compare.index.hour).mean()
rural_1p5_hour_c_compare_dc = rural_1p5_hour_c_compare.groupby(rural_1p5_hour_c_compare.index.hour).mean()
v200_BaselEPW_th_profile_hours_height_C_dc = v200_BaselEPW_th_profile_hours_height_C.groupby(
    v200_BaselEPW_th_profile_hours_height_C.index.hour).mean()
v200_BaselEPW_real_temp_profile_hours_height_C_dc = v200_BaselEPW_real_temp_profile_hours_height_C.groupby(
    v200_BaselEPW_real_temp_profile_hours_height_C.index.hour).mean()
reference_th_profile_hours_height_C_dc = reference_th_profile_hours_height_C.groupby(
    reference_th_profile_hours_height_C.index.hour).mean()
reference_real_temp_profile_hours_height_C_dc = reference_real_temp_profile_hours_height_C.groupby(
    reference_real_temp_profile_hours_height_C.index.hour).mean()
refining_th_profile_hours_height_C_dc = refining_th_profile_hours_height_C.groupby(
    refining_th_profile_hours_height_C.index.hour).mean()
refining_real_temp_profile_hours_height_C_dc = refining_real_temp_profile_hours_height_C.groupby(
    refining_real_temp_profile_hours_height_C.index.hour).mean()
# reshape the data

all_df_dc_lst = [urban_2p6_hour_c_compare_dc, rural_1p5_hour_c_compare_dc,
                 v200_BaselEPW_real_temp_profile_hours_height_C_dc,
                    reference_real_temp_profile_hours_height_C_dc,
                    refining_real_temp_profile_hours_height_C_dc]
all_df_dc_names = ['Urban(2.6 m)', 'Rural (1.5 m)',
                   f'VCWG(v200)-Real Temperature ({v200_sensor_height} m)',
                   f'VCWG(idf-Reference)-Real Temperature ({v200_sensor_height} m)',
                   f'VCWG(idf-Refining)-Real Temperature ({v200_sensor_height} m)']
all_df_dc_in_one = plt_tools.merge_multiple_df(all_df_dc_lst, all_df_dc_names)

mbe_rmse_r2_v200_BaselEPW_th = plt_tools.bias_rmse_r2(urban_2p6_hour_c_compare_dc,
                                                      v200_BaselEPW_th_profile_hours_height_C_dc,
                                                      'VCWG(v200)-Potential Temperature error')
mbe_rmse_r2_v200_BaselEPW_real = plt_tools.bias_rmse_r2(urban_2p6_hour_c_compare_dc,
                                                        v200_BaselEPW_real_temp_profile_hours_height_C_dc,
                                                        'VCWG(v200)-Real Temperature error')
mbe_rmse_r2_reference_th = plt_tools.bias_rmse_r2(urban_2p6_hour_c_compare_dc,
                                                    reference_th_profile_hours_height_C_dc,
                                                    'VCWG(EP-Reference)-Potential Temperature error')
mbe_rmse_r2_reference_real = plt_tools.bias_rmse_r2(urban_2p6_hour_c_compare_dc,
                                                    reference_real_temp_profile_hours_height_C_dc,
                                                    'VCWG(EP-Reference)-Real Temperature error')
mbe_rmse_r2_refining_th = plt_tools.bias_rmse_r2(urban_2p6_hour_c_compare_dc,
                                                    refining_th_profile_hours_height_C_dc,
                                                    'VCWG(EP-Refining)-Potential Temperature error')
mbe_rmse_r2_refining_real = plt_tools.bias_rmse_r2(urban_2p6_hour_c_compare_dc,
                                                    refining_real_temp_profile_hours_height_C_dc,
                                                    'VCWG(EP-Refining)-Real Temperature error')

case_name = (f"{compare_start_time} to {compare_end_time}-averaged diurnal cycle. p0 {p0} pa",
             "Hour of day", "Temperature (C)")
txt_info = [case_name,
            mbe_rmse_r2_v200_BaselEPW_real,
            mbe_rmse_r2_reference_real,
            mbe_rmse_r2_refining_real]
# plot
plt_tools.general_time_series_comparision(all_df_dc_in_one, txt_info)



