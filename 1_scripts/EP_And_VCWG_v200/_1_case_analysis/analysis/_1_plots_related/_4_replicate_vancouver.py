'''
# Eventually, we need compare the Sensible heat flux and the Latent heat flux.
# Do the sensible heat fluxes first
# Sensile heat fluxes are in W/m2, file is "SSQHB_all_30min.csv"
# Latent heat fluxes are in kg/m2/s, file is "SSQEB_all_30min.csv"
# Original measurements is 30 mins interval, we need to convert to hourly
# Read sensible measurements for May - September 2008 (Ultimate goal is to compare with EP measurements)
Specifically,
measurements are available after 2008-05-07 00:00:00
EP is available after 2008-05-07 00:00:00
VCWG is available after 2008-05-07 00:00:00 (one spin up day)

Start from the simple case:
start_time = '2008-07-01 00:00:00'
end_time = '2008-07-02 23:00:00'
'''

import pandas as pd
import _0_all_plot_tools as plt_tools
results_folder = r'..\\_2_saved\\vancouver'
start_time_with_spin_up = '2008-07-01 00:00:00'
start_time = '2008-07-01 00:00:00'
end_time = '2008-07-09 23:00:00'

profile_height = 5

vcwg_output_time_interval_seconds = 3600

# Read sensible measurements
df_sens_dirty = pd.read_csv(f'{results_folder}\\SSQHB_all_30min.csv', header=0, index_col=0, parse_dates=True)
df_30min_sens_measure_all = plt_tools.data_cleaning(df_sens_dirty)
df_30min_sens_measure = df_30min_sens_measure_all.loc[start_time:end_time]
df_hourly_sens_measure = plt_tools.time_interval_convertion(df_30min_sens_measure)

# read Hlfux from replicated VCWG
vcwg_original_hour_Hlfux = plt_tools.read_text_as_csv(f'{results_folder}'
                                                                          f'\\HfluxesReplicate_Vancouver_LCZ1.txt',
                                                          header=0,skiprows=2)
# select 13th column, which is HlfuxUrban, make a new dataframe
vcwg_original_hour_HfluxUrban_spin = vcwg_original_hour_Hlfux.iloc[:, 12]
vcwg_original_hour_HfluxUrban_date = plt_tools.add_date_index(vcwg_original_hour_HfluxUrban_spin,
                                                            start_time_with_spin_up, vcwg_output_time_interval_seconds)
vcwg_original_hour_HfluxUrban = vcwg_original_hour_HfluxUrban_date.loc[start_time:end_time]

# read HlufxProfiles
vcwg_original_hour_HlufxProfiles = plt_tools.read_text_as_csv(f'{results_folder}'
                                                              f'\\HfluxProf_profilesReplicate_Vancouver_LCZ1.txt')
# select 28.8 m, which is the height of the Sensible Heat Fluxes sensor
vcwg_original_hour_HlufxProfiles_spin = plt_tools.certain_height_one_day(vcwg_original_hour_HlufxProfiles, profile_height)
# sequence based index convert to date
vcwg_original_hour_HlufxProfiles_spin_date = plt_tools.add_date_index(vcwg_original_hour_HlufxProfiles_spin,
                                                                        start_time_with_spin_up,
                                                                        vcwg_output_time_interval_seconds)
# select the time period we need
vcwg_original_hour_HlufxProfiles_height = vcwg_original_hour_HlufxProfiles_spin_date.loc[start_time:end_time]


all_df_list = [df_hourly_sens_measure, vcwg_original_hour_HfluxUrban, vcwg_original_hour_HlufxProfiles_height]
all_df_name = ['Sensible Heat Flux (Best available) (28.80m)', 'VCWG-HfluxUrban',
               f'VCWG-HlufxProfiles ({profile_height}m)']
all_in_one_df = plt_tools.merge_multiple_df(all_df_list, all_df_name)

# all_in_one_df.to_csv(f'{results_folder}\\all_in_one_df_sens.csv')
bias_rmse_r2_hfluxUrban = plt_tools.bias_rmse_r2(all_in_one_df['Sensible Heat Flux (Best available) (28.80m)'],
                                      all_in_one_df['VCWG-HfluxUrban'])
bias_rmse_r2_hfluxProf = plt_tools.bias_rmse_r2(all_in_one_df['Sensible Heat Flux (Best available) (28.80m)'],
                                        all_in_one_df[f'VCWG-HlufxProfiles ({profile_height}m)'])
error_infor = [bias_rmse_r2_hfluxUrban, bias_rmse_r2_hfluxProf]
plt_tools.plot_comparison_measurement_simulated(all_in_one_df, error_infor)

print('Done')