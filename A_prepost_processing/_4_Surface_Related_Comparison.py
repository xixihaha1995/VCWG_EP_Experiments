'''
Themes todo:
1. VCWG_Oct vs EP_Oct
2. VCWG_Dec vs EP_Dec
3. VCWG_Dec vs Bypass_Dec
'''
import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def cvrmse(measurements, predictions):
    bias = predictions - measurements
    rmse = np.sqrt(np.mean(bias**2))
    cvrmse = rmse / np.mean(abs(measurements))
    return cvrmse

def normalized_mean_bias_error(measurements, predictions):
    bias = predictions - measurements
    nmb = np.mean(bias) / np.mean(measurements)
    return nmb

plot_fontsize = 12
experiments_folder = 'CAPITOUL_ByPass_Improvements_Investigation'
experiments_folder = ['AllCases']
all_data_name = "comparison.xlsx"
all_data = pd.read_excel(os.path.join(experiments_folder, all_data_name), sheet_name='comparison', index_col=0)
# comparison['sensWaste_' + csv_file] = df['sensWaste']
# comparison['wallSun_K_' + csv_file] = df['wallSun_K']
# comparison['wallShade_K_' + csv_file] = df['wallShade_K']
# comparison['roof_K_' + csv_file] = df['roof_K']
# comparison['ForcTemp_K_' + csv_file] = df['ForcTemp_K']

# get all the csv file names
# all_csv_files = [f for f in os.listdir(experiments_folder) if f.endswith('.csv')]
all_csv_files = [ 'Oct_Bypass.csv','Bypassing_EPW.csv', 'Bypassing_IDF.csv', 'Dec_Bypass.csv',]
all_csv_files = ['CAPITOUL_WithShading_WithCooling.csv',]
themes = ['sensor_idx_20.0','ForcTemp_K','sensWaste', 'wallSun_K', 'wallShade_K', 'roof_K']
# create new excel files, with the following sheets name:
# 'sensWaste', 'wallSun_K', 'wallShade_K', 'roof_K', 'ForcTemp_K', sensor_idx_20.0
cvrmse_nmb_dict = {}
reorganized_excel = pd.ExcelWriter(os.path.join(experiments_folder, 'CAPITOUL_WithShading_WithCoolingcomparison.xlsx'))
# copy the "cvrmse" sheet from the original excel file
old_cvrmse_sheet = pd.read_excel(os.path.join(experiments_folder, all_data_name), sheet_name='cvrmse', index_col=0)
old_cvrmse_sheet.to_excel(reorganized_excel, sheet_name='cvrmse')
for theme in themes:
    df = pd.DataFrame()
    for csv_file in all_csv_files:
        # from the all_data, find the column name containg 'theme' and 'csv_file'
        # then add the column to the new excel file
        _target_col = [col for col in all_data.columns if theme in col and csv_file in col]
        df[csv_file] = all_data[_target_col]
        df.index = all_data.index
        _target_col_2 = [col for col in all_data.columns if theme in col and 'Dec_Bypass.csv' in col]
        df['Dec_Bypass.csv'] = all_data[_target_col_2]
        _df1 = df['Dec_Bypass.csv']
        _df2 = df[csv_file]
        cvrmse_nmb_dict[theme + '_' + csv_file] = [cvrmse(_df1, _df2), normalized_mean_bias_error(_df1, _df2)]
    df.to_excel(reorganized_excel, sheet_name=theme)

# convert cvrmse_nmb_dict to one sheet
cvrmse_nmb_df = pd.DataFrame.from_dict(cvrmse_nmb_dict, orient='index', columns=['cvrmse', 'nmb'])
cvrmse_nmb_df.to_excel(reorganized_excel, sheet_name='Distance_To_Dec_Bypass.csv')

reorganized_excel.save()

#plot the len(themes) subfigs, share x axis
_fig, _axs = plt.subplots(len(themes), 1, figsize=(10, 10), sharex=True)
_fig.subplots_adjust(right=0.76)
_global_legend = 1
for _i, _theme in enumerate(themes):
    _df = pd.read_excel(os.path.join(experiments_folder, 'reorganized.xlsx'), sheet_name=_theme, index_col=0)
    for _csv_file in all_csv_files:
        if _global_legend == 1:
            _axs[_i].plot(_df[_csv_file], label=_csv_file)
        else:
            _axs[_i].plot(_df[_csv_file], label='_nolegend_')
    _global_legend = 0
    _axs[_i].set_title(_theme)
_fig.legend(loc='center right', bbox_to_anchor=(1, 0.5), borderaxespad=0., fontsize=plot_fontsize)



