'''
Themes todo:
1. VCWG_Oct vs EP_Oct
2. VCWG_Dec vs EP_Dec
3. VCWG_Dec vs Bypass_Dec
'''
import os
import pandas as pd
from matplotlib import pyplot as plt

def plot_one_subfig(sub_title, df1, df2, ax):
    _df1 = df1[sub_title]
    _df2 = df2[sub_title]
    ax.plot(_df1, label='VCWG')
    ax.plot(_df2, label='EP')
    ax.set_title(sub_title)
    ax.legend()

def plot_all_subfigs(sub_tiltes, df1, df2):
    _nbr_subfigs = len(sub_tiltes)
    _fig, _axs = plt.subplots(_nbr_subfigs, 1, figsize=(10, 10))
    _fig.subplots_adjust(right=0.76)
    for _i, _sub_title in enumerate(sub_tiltes):
        plot_one_subfig(_sub_title, df1, df2, _axs[_i])

experiments_folder = 'CAPITOUL_All_Surface_Comparison'
vcwg_oct_name = 'VCWG_October_comparison.xlsx'
ep_oct_name = 'OldEPW_WithoutShading_WithCooling.csv'
compare_start_time = '2004-06-01 00:00:00'
compare_end_time = '2004-06-30 23:55:00'

vcwg_oct = pd.read_excel(os.path.join(experiments_folder, vcwg_oct_name),
                         index_col=0, parse_dates=True, header=0)
vcwg_oct = vcwg_oct[compare_start_time:compare_end_time]
ep_oct = pd.read_csv(os.path.join(experiments_folder, ep_oct_name),
                        index_col=0, parse_dates=True, header=0)
ep_oct = ep_oct[compare_start_time:compare_end_time]
theme1_subtitles = ['wallSun']
plot_all_subfigs(theme1_subtitles, vcwg_oct, ep_oct)