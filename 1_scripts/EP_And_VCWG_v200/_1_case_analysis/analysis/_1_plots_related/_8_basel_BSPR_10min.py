import _0_all_plot_tools as plt_tools
import pandas as pd, numpy as np
measure_results_folder = r'..\..\cases\_0_measurements\BUBBLE'
original_prediction_results_folder = r'..\..\cases\_05_Basel_BSPR_ue1\ep_saving'
bypass_predict_results_folder = r'..\..\cases\_05_Basel_BSPR_ue1\refining_M2\vcwg_ep_saving'
all_in_one_saving_path = r'..\..\cases\_05_Basel_BSPR_ue1\refining_M2'
IOP_start_time = '2002-06-10 01:00:00'
IOP_end_time = '2002-07-09 22:50:00'

vcwg_output_time_interval_seconds = 3600
v200_start_time = '2002-06-10 00:00:00'
v200_end_time = '2002-07-09 23:55:00'
compare_start_time = '2002-06-10 01:00:00'
compare_end_time = '2002-07-09 22:00:00'

bypass_filename = '_BSPR_bypass_refining_M2'
original_filename = 'vcwg'

# v200_sensor_height = 2.6
heights_profile = [0.5 + i for i in range(50)]
p0 = 100000
ue1_heights = [2.6, 13.9, 17.5, 21.5, 25.5, 31.2]
re1_col_idx = 7

# Read air temperature measurements
urban_all_sites_10min_dirty = plt_tools.read_text_as_csv(f'{measure_results_folder}\\BUBBLE_BSPR_AT_PROFILE_IOP.txt',
                                                          header=0, index_col=0, skiprows=16)
# clean the measurements
urban_all_sites_10min_clean = plt_tools.clean_bubble_iop(urban_all_sites_10min_dirty,
                                                  start_time = IOP_start_time, end_time = IOP_end_time,
                                                  to_hourly= False)
# select the 0th column as the comparison data
urban_2p6_10min_c_compare = urban_all_sites_10min_clean[compare_start_time:compare_end_time]

mixed_all_sites_10min_dirty = plt_tools.read_text_as_csv(f'{measure_results_folder}\\BUBBLE_AT_IOP.txt',
                                                            header=0, index_col=0, skiprows=25)
# clean the measurements
mixed_all_sites_10min_clean = plt_tools.clean_bubble_iop(mixed_all_sites_10min_dirty,
                                                    start_time = IOP_start_time, end_time = IOP_end_time,
                                                    to_hourly= False)
rural_1p5_10min_c_compare = mixed_all_sites_10min_clean.iloc[:,re1_col_idx][compare_start_time:compare_end_time]

original_potential_10min_c_compare, original_real_10min_c_compare = \
    plt_tools.excel_to_potential_real_df(original_filename, original_prediction_results_folder, p0,
                                         heights_profile, ue1_heights,compare_start_time,compare_end_time)
bypass_ver0_path = f'{bypass_predict_results_folder}\\ver0'
bypass_potential_10min_c_compare_ver0, bypass_real_10min_c_compare_ver0 = \
    plt_tools.excel_to_potential_real_df(bypass_filename, bypass_ver0_path, p0, heights_profile, ue1_heights,
                                         compare_start_time,compare_end_time)
bypass_ver1_path = f'{bypass_predict_results_folder}\\ver1'
bypass_potential_10min_c_compare_ver1, bypass_real_10min_c_compare_ver1 = \
    plt_tools.excel_to_potential_real_df(bypass_filename, bypass_ver1_path, p0, heights_profile, ue1_heights,
                                            compare_start_time,compare_end_time)
bypass_ver2_path = f'{bypass_predict_results_folder}\\ver2'
bypass_potential_10min_c_compare_ver2, bypass_real_10min_c_compare_ver2 = \
    plt_tools.excel_to_potential_real_df(bypass_filename, bypass_ver2_path, p0, heights_profile, ue1_heights,
                                            compare_start_time,compare_end_time)
# urban_2p6_10min_c_compare are the measurements, column length is 6, which is for 6 heights
# original_real_sensor_10min_c_compare are the associated original predictions, column length is 6
# bypass_refining_real_sensor_10min_c_compare are the associated bypass predictions, column length is 6

# for each height, calculate the RMSE
original_potential_10min_c_compare_cvrmse = []
bypass_potential_10min_c_compare_ver0_cvrmse = []
bypass_potential_10min_c_compare_ver1_cvrmse = []
bypass_potential_10min_c_compare_ver2_cvrmse = []
for i in range(len(ue1_heights)):
    original_potential_10min_c_compare_cvrmse.append(plt_tools.calculate_cvrmse(
        urban_2p6_10min_c_compare.iloc[:,i], original_potential_10min_c_compare.iloc[:,i]))
    bypass_potential_10min_c_compare_ver0_cvrmse.append(plt_tools.calculate_cvrmse(
        urban_2p6_10min_c_compare.iloc[:,i], bypass_potential_10min_c_compare_ver0.iloc[:,i]))
    bypass_potential_10min_c_compare_ver1_cvrmse.append(plt_tools.calculate_cvrmse(
        urban_2p6_10min_c_compare.iloc[:,i], bypass_potential_10min_c_compare_ver1.iloc[:,i]))
    bypass_potential_10min_c_compare_ver2_cvrmse.append(plt_tools.calculate_cvrmse(
        urban_2p6_10min_c_compare.iloc[:,i], bypass_potential_10min_c_compare_ver2.iloc[:,i]))

# print the results
print(f"BSPR CVRMSE:{compare_start_time} to {compare_end_time}-10min Canyon Temperature. p0 {p0} pa")
for i in range(len(ue1_heights)):
    print(f'Height {ue1_heights[i]}m. Original: {original_potential_10min_c_compare_cvrmse[i]:.2f}'
            f' Bypass ver0: {bypass_potential_10min_c_compare_ver0_cvrmse[i]:.2f}'
            f' Bypass ver1: {bypass_potential_10min_c_compare_ver1_cvrmse[i]:.2f}'
            f' Bypass ver2: {bypass_potential_10min_c_compare_ver2_cvrmse[i]:.2f}')

# # merge them together
merged_df = pd.concat([rural_1p5_10min_c_compare,urban_2p6_10min_c_compare,
                       original_potential_10min_c_compare, bypass_potential_10min_c_compare_ver0,
                          bypass_potential_10min_c_compare_ver1, bypass_potential_10min_c_compare_ver2],
                        axis=1)
# rename the above columns
# get ue1_heights length
heights_length = len(ue1_heights)
# first column is rural_1p5_10min_c_compare, no change
# following the first heights_length columns are urban_2p6_10min_c_compare, no change
# following the second heights_length columns are original_potential_10min_c_compare, add 'original' prefix
# following the third heights_length columns are bypass_potential_10min_c_compare_ver0, add 'bypass_ver0' prefix
# following the fourth heights_length columns are bypass_potential_10min_c_compare_ver1, add 'bypass_ver1' prefix
# following the fifth heights_length columns are bypass_potential_10min_c_compare_ver2, add 'bypass_ver2' prefix

# rename the columns
merged_df.columns = ['rural_1p5_10min_c_compare'] + \
                    [f'urban_2p6_10min_c_compare_{i}' for i in range(heights_length)] + \
                    [f'original_potential_10min_c_compare_{i}' for i in range(heights_length)] + \
                    [f'bypass_potential_10min_c_compare_ver0_{i}' for i in range(heights_length)] + \
                    [f'bypass_potential_10min_c_compare_ver1_{i}' for i in range(heights_length)] + \
                    [f'bypass_potential_10min_c_compare_ver2_{i}' for i in range(heights_length)]
# save the merged_df to an Excel file
merged_df.to_excel(f'{all_in_one_saving_path}\\{bypass_filename}_10min_C_compare.xlsx')
plt_tools.stacked_comparison_plot(merged_df, ue1_heights)
