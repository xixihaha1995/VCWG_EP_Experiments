import _0_all_plot_tools as plt_tools
import pandas as pd
# print current interpreter path


results_folder = r'..\\_2_saved\\orientation_confirmation'

start_time = '2002-June-09 00:05:00'
# read xlsx, "orientation_comparision.xlsx" from the results folder

all_degs = pd.read_csv(results_folder + r'\\orientation_comparision.csv')
all_degs_timed = plt_tools.ep_time_to_pandas_time(all_degs,start_time)
plt_txt =("Rejected Heat From HVAC [J]","Date", "[J]")
plt_tools.general_time_series_comparision(all_degs_timed, plt_txt)
