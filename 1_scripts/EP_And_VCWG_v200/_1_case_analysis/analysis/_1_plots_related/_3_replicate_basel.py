import _0_all_plot_tools as plt_tools
import pandas as pd
results_folder = r'..\_2_saved\vcwg_potential_real_confirmation'
sensor_height = 2.6
building_height = 15
start_time_with_spin_up = '2002-06-09 00:00:00'
v132_start_timewith_spin_up = '2002-06-15 00:00:00'
start_time = '2002-06-15 00:00:00'
end_time = '2002-06-29 23:00:00'
vcwg_output_time_interval_seconds = 3600

# Read air temperature measurements
measurements_all_sites_10min_dirty = plt_tools.read_text_as_csv(f'{results_folder}\\BUBBLE_BSPR_AT_PROFILE_IOP.txt',
                                                          header=0, index_col=0, skiprows=16)

# clean the measurements
measurements_all_sites_hour = plt_tools.clean_bubble_iop(measurements_all_sites_10min_dirty)
# select the 0th column as the comparison data
measurements_hour_height = measurements_all_sites_hour.iloc[:,0]
# select the time period
measurements_hour_C = measurements_hour_height[start_time:end_time]
# ORIGINAL_th_profilesBasel_MOST
# th_profilesBasel_MOST
# BaselEPW_th_profilesBasel_MOST
potential_temp_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\BaselEPW_th_profilesBasel_MOST.txt')
potential_temp_profile_hours_height_spin = plt_tools.certain_height_one_day(potential_temp_profile_hours, sensor_height)
potential_temp_profile_hours_height_spin_date = plt_tools.add_date_index(potential_temp_profile_hours_height_spin,
                                                                    start_time_with_spin_up,
                                                                    vcwg_output_time_interval_seconds)
potential_temp_profile_hours_height_K = potential_temp_profile_hours_height_spin_date.loc[start_time:end_time]

v132_turban_profile_hours = plt_tools.read_text_as_csv(f'{results_folder}\\v132_Tu_profiles_hourly.txt')
v132_turban_profile_hours_height_spin = plt_tools.certain_height_one_day(v132_turban_profile_hours, sensor_height)
v132_turban_profile_hours_height_spin_date = plt_tools.add_date_index(v132_turban_profile_hours_height_spin,
                                                                    v132_start_timewith_spin_up,
                                                                    vcwg_output_time_interval_seconds)
v132_turban_profile_hours_height_K = v132_turban_profile_hours_height_spin_date.loc[start_time:end_time]


# read the real temperature profile time series from csv
dynamic_p0_real_temp_profile_timestep = pd.read_csv(f'{results_folder}\\th_real_dynamic_p0.csv', header=None, index_col=None)
dynamic_p0_real_temp_profile_hours = plt_tools.time_interval_convertion(dynamic_p0_real_temp_profile_timestep,
                                                             need_date=True,
                                                             original_time_interval_min = 5,
                                                             start_time = start_time_with_spin_up)
#add height index from potential_profile_hours
dynamic_p0_real_temp_profile_hours_all_height = dynamic_p0_real_temp_profile_hours.T
#select height
dynamic_p0_real_temp_profile_hours_height_spin = plt_tools.certain_height_one_day(
    dynamic_p0_real_temp_profile_hours_all_height, sensor_height)
# add date index
dynamic_p0_real_temp_profile_hours_height_spin_date = plt_tools.add_date_index(
    dynamic_p0_real_temp_profile_hours_height_spin,start_time_with_spin_up,vcwg_output_time_interval_seconds)
dynamic_p0_real_temp_profile_hours_height_avg = plt_tools.average_temperature_below_height(
    dynamic_p0_real_temp_profile_hours_all_height,building_height)
dynamic_p0_real_temp_profile_hours_height_avg_date = plt_tools.add_date_index(
    dynamic_p0_real_temp_profile_hours_height_avg,start_time_with_spin_up,vcwg_output_time_interval_seconds)
dynamic_p0_real_temp_profile_hours_height_K = dynamic_p0_real_temp_profile_hours_height_spin_date.loc[start_time:end_time]

constant_p0_real_temp_profile_timestep = pd.read_csv(f'{results_folder}\\BaselEPW_th_real.csv',
                                                     header=None, index_col=None)
constant_p0_real_temp_profile_hours = plt_tools.time_interval_convertion(constant_p0_real_temp_profile_timestep,
                                                                need_date=True,
                                                                original_time_interval_min = 1,
                                                                start_time = start_time_with_spin_up)
#add height index from potential_profile_hours
constant_p0_real_temp_profile_hours_all_height = constant_p0_real_temp_profile_hours.T
#select height
constant_p0_real_temp_profile_hours_height_spin = plt_tools.certain_height_one_day(
    constant_p0_real_temp_profile_hours_all_height, sensor_height)
# add date index
constant_p0_real_temp_profile_hours_height_spin_date = plt_tools.add_date_index(
    constant_p0_real_temp_profile_hours_height_spin,start_time_with_spin_up,vcwg_output_time_interval_seconds)
# select the time period
constant_p0_real_temp_profile_hours_height_K = constant_p0_real_temp_profile_hours_height_spin_date.loc[start_time:end_time]

# K to C
dynamic_p0_real_temp_profile_hours_height_C = dynamic_p0_real_temp_profile_hours_height_K - 273.15
constant_p0_real_temp_profile_hours_height_C = constant_p0_real_temp_profile_hours_height_K - 273.15
potential_temp_profile_hours_height_C = potential_temp_profile_hours_height_K - 273.15
v132_turban_profile_hours_height_C = v132_turban_profile_hours_height_K - 273.15

all_df_names = ['measurements_hour', '(Basel.epw)v200_potential_temp','(Basel.epw)v200_real_temp',
                '(Basel_BUBBLE.epw)v132_potential_temp']
all_df = [measurements_hour_C, potential_temp_profile_hours_height_C, constant_p0_real_temp_profile_hours_height_C,
            v132_turban_profile_hours_height_C]
all_in_one_df = plt_tools.merge_multiple_df(all_df, all_df_names)

# bias_rmse_r2_th_rep = plt_tools.bias_rmse_r2(all_in_one_df['measurements_hour'],
#                                          all_in_one_df['replicate_profile_hours_height'])
# bias_rmse_r2_th_bypass = plt_tools.bias_rmse_r2(all_in_one_df['measurements_hour'],
#                                             all_in_one_df['bypass_profile_hours_height'])
case_txt = (f"Air Temperature at {sensor_height}m\n", "Date", "Temperature (K)")
plt_tools.general_time_series_comparision(all_in_one_df,case_txt)



