import _0_all_plot_tools as plt_tools
import pandas as pd
results_folder = r'..\_2_saved\BUBBLE_which_epw'
start_time = '2002-06-10 01:00:00'
IOP_end_time = '2002-07-09 22:50:00'
end_time = '2002-07-09 22:00:00'
ue1_col_idx = 0
re1_col_idx = 7
# Read air temperature measurements
urban_all_sites_10min_dirty = plt_tools.read_text_as_csv(f'{results_folder}\\BUBBLE_BSPR_AT_PROFILE_IOP.txt',
                                                          header=0, index_col=0, skiprows=16)
# clean the measurements
urban_all_sites_hour = plt_tools.clean_bubble_iop(urban_all_sites_10min_dirty,
                                                  start_time = start_time, end_time = IOP_end_time)
# select the 0th column as the comparison data
urban_2p6_hour_c = urban_all_sites_hour.iloc[:,ue1_col_idx]

mixed_all_sites_10min_dirty = plt_tools.read_text_as_csv(f'{results_folder}\\BUBBLE_AT_IOP.txt',
                                                            header=0, index_col=0, skiprows=25)
# clean the measurements
mixed_all_sites_hour = plt_tools.clean_bubble_iop(mixed_all_sites_10min_dirty,
                                                    start_time = start_time, end_time = IOP_end_time)
# Keep original index, only select one column and keep the column name
rural_1p5_hour_c = mixed_all_sites_hour.iloc[:,re1_col_idx]

#read general txt based file as dataframe
v200_Basel_epw_all_dirty = pd.read_csv( f'{results_folder}\\v200_Basel.epw',
                                 skiprows= 8, header= None, index_col=None,)
v200_Basel_epw_all_clean = plt_tools.clean_epw(v200_Basel_epw_all_dirty,
                                               start_time = start_time)
v200_Basel_epw_air_temp_all = v200_Basel_epw_all_clean.iloc[:,6]
v200_Basel_epw_air_temp = v200_Basel_epw_air_temp_all[start_time:end_time]

v200_ERA5_Basel_epw_all_dirty = pd.read_csv( f'{results_folder}\\v200_ERA5_Basel.epw',
                                    skiprows= 8, header= None, index_col=None,)
v200_ERA5_Basel_epw_all_clean = plt_tools.clean_epw(v200_ERA5_Basel_epw_all_dirty,
                                                    start_time = start_time)
v200_ERA5_Basel_epw_air_temp_all = v200_ERA5_Basel_epw_all_clean.iloc[:,6]
v200_ERA5_Basel_epw_air_temp = v200_ERA5_Basel_epw_air_temp_all[start_time:end_time]

v132_Basel_BUBBLE_epw_all_dirty = pd.read_csv( f'{results_folder}\\v132_Basel_BUBBLE.epw',
                                    skiprows= 8, header= None, index_col=None,)
v132_Basel_BUBBLE_epw_all_clean = plt_tools.clean_epw(v132_Basel_BUBBLE_epw_all_dirty,
                                                    start_time = start_time)
v132_Basel_BUBBLE_epw_air_temp_all = v132_Basel_BUBBLE_epw_all_clean.iloc[:,6]
v132_Basel_BUBBLE_epw_air_temp = v132_Basel_BUBBLE_epw_air_temp_all[start_time:end_time]


#column name is original column name
v200_Basel_epw_air_temp.index = pd.to_datetime(v200_Basel_epw_air_temp.index)
all_df_names = ['urban_2p6_hour_c', 'rural_1p5_hour_c', 'v200_Basel_epw_air_temp',]
all_df_lst = [urban_2p6_hour_c, rural_1p5_hour_c, v200_Basel_epw_air_temp]
all_in_one_df = plt_tools.merge_multiple_df(all_df_lst,all_df_names)

all_in_one_df.to_excel(f'{results_folder}\\epw_all_in_one.xlsx')

cast_txt = ("Hourly air temperature for Urban Canyon (2.6m) and Rural Site (1.5m)", "Date", "Temperature (C)")
txt_info = [cast_txt]
plt_tools.general_time_series_comparision(all_in_one_df, txt_info)



