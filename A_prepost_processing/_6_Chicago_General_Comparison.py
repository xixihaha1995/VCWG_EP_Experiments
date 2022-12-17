import os
import pathlib
import re
import sqlite3

import pandas as pd

def read_sql(csv_file):
    sql_report_name = 'AnnualBuildingUtilityPerformanceSummary'
    sql_table_name = 'Site and Source Energy'
    sql_row_name = 'Total Site Energy'
    sql_col_name = 'Total Energy'
    csv_name = re.search(r'(.*)\.csv', csv_file).group(1)
    current_path = f'./{experiments_folder}'
    sql_path = "foo"
    for folder in os.listdir(current_path):
        if csv_name in folder and 'ep_trivial_outputs' in folder:
            sql_path = os.path.join(current_path, folder, 'eplusout.sql')
            break
    if not os.path.exists(sql_path):
        return None
    abs_sql_path = os.path.abspath(sql_path)
    sql_uri = '{}?mode=ro'.format(pathlib.Path(abs_sql_path).as_uri())
    query = f"SELECT * FROM TabularDataWithStrings WHERE ReportName = '{sql_report_name}' AND TableName = '{sql_table_name}'" \
            f" AND RowName = '{sql_row_name}' AND ColumnName = '{sql_col_name}'"
    with sqlite3.connect(sql_uri, uri=True) as con:
        cursor = con.cursor()
        results = cursor.execute(query).fetchall()
        if results:
            pass
        else:
            msg = ("Cannot find the EnergyPlusVersion in the SQL file. "
                   "Please inspect query used:\n{}".format(query))
            raise ValueError(msg)
    regex = r'(\d+\.?\d*)'
    totalEnergy = float(re.findall(regex, results[0][1])[0])

    hvac_electricity_query = f"SELECT * FROM TabularDataWithStrings " \
                             f"WHERE ReportName = '{sql_report_name}'" \
                             f"AND TableName = 'Utility Use Per Total Floor Area' And RowName = 'HVAC' " \
                             f"AND ColumnName = 'Electricity Intensity'"
    hvac_electricity_query_results = cursor.execute(hvac_electricity_query).fetchall()
    hvac_electricity = float(re.findall(regex, hvac_electricity_query_results[0][1])[0])
    hvac_gas_query = f"SELECT * FROM TabularDataWithStrings " \
                     f"WHERE ReportName = '{sql_report_name}'" \
                     f"AND TableName = 'Utility Use Per Total Floor Area' And RowName = 'HVAC' " \
                     f"AND ColumnName = 'Natural Gas Intensity'"
    hvac_gas_query_results = cursor.execute(hvac_gas_query).fetchall()
    hvac_gas = float(re.findall(regex, hvac_gas_query_results[0][1])[0])
    return totalEnergy, hvac_electricity, hvac_gas

plot_fontsize = 12
experiments_folder = 'Chicago_MedOffice'

'''
read all csv files, and create a new excel file with the following sheets:
canTemp_c, energy (Total Site Energy, HVAC Electricity, HVAC Gas)
'''
all_csv_files = [f for f in os.listdir(experiments_folder) if f.endswith('.csv')]
sheet_names = ['canTemp_c', 'sensWaste','wallSun_c','wallShade_c','roof_c','energy']

all_dfs = []
for csv_file in all_csv_files:
    df = pd.read_csv(os.path.join(experiments_folder, csv_file), index_col=0)
    all_dfs.append(df)

comparison_excel = pd.ExcelWriter(os.path.join(experiments_folder, 'comparison.xlsx'))
df_canTemp_c = pd.concat([df['canTemp'] - 273.15 for df in all_dfs], axis=1)
df_canTemp_c.columns = all_csv_files
df_canTemp_c.index = pd.to_datetime(df_canTemp_c.index)
df_canTemp_c.to_excel(comparison_excel, sheet_name=sheet_names[0])

df_sensWaste = pd.concat([df['sensWaste'] for df in all_dfs], axis=1)
df_sensWaste.columns = all_csv_files
df_sensWaste.index = pd.to_datetime(df_sensWaste.index)
df_sensWaste.to_excel(comparison_excel, sheet_name=sheet_names[1])

df_wallSun_K = pd.concat([df['wallSun_K']- 273.15 for df in all_dfs], axis=1)
df_wallSun_K.columns = all_csv_files
df_wallSun_K.index = pd.to_datetime(df_wallSun_K.index)
df_wallSun_K.to_excel(comparison_excel, sheet_name=sheet_names[2])

df_wallShade_K = pd.concat([df['wallShade_K']- 273.15 for df in all_dfs], axis=1)
df_wallShade_K.columns = all_csv_files
df_wallShade_K.index = pd.to_datetime(df_wallShade_K.index)
df_wallShade_K.to_excel(comparison_excel, sheet_name=sheet_names[3])

df_roof_K = pd.concat([df['roof_K']- 273.15 for df in all_dfs], axis=1)
df_roof_K.columns = all_csv_files
df_roof_K.index = pd.to_datetime(df_roof_K.index)
df_roof_K.to_excel(comparison_excel, sheet_name=sheet_names[4])


energy_sql_dict = {}
for csv_file in all_csv_files:
    energy_sql_dict[csv_file] = (read_sql(csv_file))

df_energy = pd.DataFrame.from_dict(energy_sql_dict, orient='index', columns=['Total Site Energy[GJ]',
                                                                       'HVAC Electricity Intensity [MJ/m2]',
                                                                       'HVAC Natural Gas Intensity [MJ/m2]'])
df_energy.to_excel(comparison_excel, sheet_name=sheet_names[5])
comparison_excel.save()

# plot the canTemp_c, sensWaste, wallSun_c, wallShade_c, roof_c (sharedx)
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(5, 1, sharex=True, figsize=(10, 10))
fig.subplots_adjust(right=0.76)
for i, df in enumerate([df_canTemp_c, df_sensWaste, df_wallSun_K, df_wallShade_K, df_roof_K]):
    df.plot(ax=ax[i], legend=False)
    ax[i].set_ylabel(df.columns[0].split('_')[0], fontsize=plot_fontsize)
    ax[i].tick_params(labelsize=plot_fontsize)
    ax[i].set_xlabel('')
    ax[i].set_xlim([df.index[0], df.index[-1]])
    ax[i].set_ylim([df.min().min(), df.max().max()])
    ax[i].grid()
    ax[i].set_title(sheet_names[i], fontsize=plot_fontsize)

fig.legend(df.columns, loc='center right', fontsize=plot_fontsize)
plt.show()
