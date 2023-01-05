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
experiments_folder = 'AllCases'
experiment_csv = 'CAPITOUL_WithShading_WithCooling.csv'
organized_xlsx = 'CAPITOUL_WithShading_WithCoolingcomparison.xlsx'
all_data = pd.read_excel(os.path.join(experiments_folder, organized_xlsx), sheet_name='comparison', index_col=0)
themes = ['sensor_idx_20.0','sensWaste','ForcTemp_K', 'wallSun_K', 'wallShade_K', 'roof_K']

#plot the len(themes) subfigs, share x axis
_fig, _axs = plt.subplots(len(themes), 1, figsize=(10, 10), sharex=True)
_fig.subplots_adjust(right=0.76)
_global_legend = 1
for _i, _theme in enumerate(themes):

    _target_cols = [col for col in all_data.columns if _theme in col]
    if _global_legend == 1:
        _labels = ['VCWG' if 'Only' in col else 'VCWG_EP'  for col in _target_cols]
        _axs[_i].plot(all_data.index, all_data[_target_cols], label=_labels)
        _global_legend = 0
    else:
        _axs[_i].plot(all_data[_target_cols], label='_nolegend_')
    if _theme == 'sensor_idx_20.0':
        _axs[_i].plot(all_data['Urban_DBT_C'], label='Urban_DBT_C')

    _axs[_i].set_ylabel(_theme, fontsize=plot_fontsize)
_fig.legend(loc='center right', bbox_to_anchor=(1, 0.5), borderaxespad=0., fontsize=plot_fontsize)
plt.show()




