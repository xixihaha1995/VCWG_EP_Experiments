import os
import pathlib
import re
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def cvrmse_percentage(measurements, predictions):
    bias = predictions - measurements
    rmse = np.sqrt(np.mean(bias**2))
    cvrmse = rmse / np.mean(abs(measurements))
    return round(cvrmse * 100, 2)

def normalized_mean_bias_error_percentage(measurements, predictions):
    bias = measurements - predictions
    nmb = np.mean(bias) / np.mean(measurements)
    return round(nmb * 100, 2)

def read_sql(csv_file):
    print(csv_file)
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
            print(sql_path)
            return 0,0,0
            msg = ("Cannot find the EnergyPlusVersion in the SQL file. "
                   "Please inspect query used:\n{}".format(query))
            raise ValueError(msg)
    regex = r'(\d+\.?\d*)'
    totalEnergy = float(re.findall(regex, results[0][1])[0])

    hvac_electricity_query = f"SELECT * FROM TabularDataWithStrings " \
                             f"WHERE ReportName = '{sql_report_name}'" \
                             f"AND TableName = 'Utility Use Per Total Floor Area' And RowName = 'HVAC' " \
                             f"AND ColumnName = 'Electricity Intensity'"
    cooling_query = f"SELECT * FROM TabularDataWithStrings " \
                             f"WHERE ReportName = '{sql_report_name}'" \
                             f"AND TableName = 'End Uses' And RowName = 'Cooling' " \
                             f"AND ColumnName = 'Electricity'"
    cooling_query_results = cursor.execute(cooling_query).fetchall()
    cooling_electricity = float(re.findall(regex, cooling_query_results[0][1])[0])
    hvac_gas_query = f"SELECT * FROM TabularDataWithStrings " \
                     f"WHERE ReportName = '{sql_report_name}'" \
                     f"AND TableName = 'Utility Use Per Total Floor Area' And RowName = 'HVAC' " \
                     f"AND ColumnName = 'Natural Gas Intensity'"
    heating_query = f"SELECT * FROM TabularDataWithStrings " \
                    f"WHERE ReportName = '{sql_report_name}'" \
                    f"AND TableName = 'End Uses' And RowName = 'Heating' " \
                    f"AND ColumnName = 'Electricity'"
    heating_query_results = cursor.execute(heating_query).fetchall()
    heating_electricity = float(re.findall(regex, heating_query_results[0][1])[0])
    return totalEnergy, cooling_electricity, heating_electricity

def read_csv_energy(csv_file):
    '''
    Returns:
        ElecTotal[J] coolConsump[J]	heatConsump[J]
        convert to GJ
    '''
    df = pd.read_csv(os.path.join(experiments_folder, csv_file), index_col=0, parse_dates=True)
    #sum over all the desired columns
    elecTotal = df['ElecTotal[J]'].sum()
    coolConsump = df['coolConsump[J]'].sum()
    heatConsump = df['heatConsump[J]'].sum()
    return round(elecTotal/1e9, 2), round(coolConsump/1e9, 2), round(heatConsump/1e9, 2)

plot_fontsize = 12
experiments_folder = 'Chicago_MedOffice_Sensitivity'
'''
read all csv files, containing OnlyVCWG or PartialVCWG, and create a new excel file with the following sheets:
sheet_names = ['Energy Consumption','CanTempC', 'CanTempComparison']
'''
def sort_by_numbers(s):
    regex = r'(\d+\.?\d*)'
    return [float(x) for x in re.findall(regex, s)]

all_csv_files = [f for f in os.listdir(experiments_folder)
                 if f.endswith('.csv') and ('OnlyVCWG' in f or 'PartialVCWG' in f)]
baseline = 'ByPass_Width_canyon_33.3_fveg_G_0_building_orientation_0.csv'
# insert front
all_csv_files.sort(key=sort_by_numbers)
all_csv_files.insert(0, baseline)
sheet_names = ['Energy Consumption','CanTempC', 'CanTempComparison']

all_dfs = {}
for csv_file in all_csv_files:
    df = pd.read_csv(os.path.join(experiments_folder, csv_file), index_col=0, parse_dates=True)
    all_dfs[csv_file] = df
all_sensitivity = pd.ExcelWriter(os.path.join(experiments_folder, 'only_partial_VCWG.xlsx'))

energy_sql_dict = {}
energy_sql_dict['Baseline'] = read_sql(baseline)
for csv_file in all_csv_files:
    if csv_file == baseline:
        continue
    else:
        energy_sql_dict[csv_file] = (read_csv_energy(csv_file))
# ElecTotal[J] coolConsump[J]	heatConsump[J]
df_energy = pd.DataFrame.from_dict(energy_sql_dict, orient='index', columns=['ElecTotal [GJ]',
                                                                       'coolConsump[GJ]',
                                                                          'heatConsump[GJ]'])
df_energy.to_excel(all_sensitivity, sheet_name=sheet_names[0])

df_canTemp_c_sheet = pd.DataFrame(index=all_dfs[baseline].index)
df_canTemp_c_sheet['Baseline'] = all_dfs[baseline]['canTemp'] - 273.15
for csv_file in all_csv_files:
    # check if 'canTemp' is in the csv file
    if csv_file == baseline:
        continue
    if 'canTemp' in all_dfs[csv_file].columns:
        df_canTemp_c_sheet[csv_file] = all_dfs[csv_file]['canTemp'] - 273.15
    else:
        df_canTemp_c_sheet[csv_file] = all_dfs[csv_file]['canTemp_K'] - 273.15
df_canTemp_c_sheet.to_excel(all_sensitivity, sheet_name=sheet_names[1])

'''
In the CanTempComparison sheet, the first column is the CVRMSE, the second column is the NMBE
The index is all_csv_files.
For each row, to compare the baseline with the sensitivity experiment
'''
df_canTemp_comparison_sheet = pd.DataFrame(index=all_csv_files)
df_canTemp_comparison_sheet['CVRMSE(%)'] = 0
df_canTemp_comparison_sheet['NMBE(%)'] = 0
# insert index 0: 'Baseline', CVRMSE and NMBE are 0
df_canTemp_comparison_sheet.loc['Baseline', 'CVRMSE(%)'] = 0
df_canTemp_comparison_sheet.loc['Baseline', 'NMBE(%)'] = 0
# move the 'Baseline' to the first row
df_canTemp_comparison_sheet = df_canTemp_comparison_sheet.reindex(['Baseline'] + all_csv_files[1:])
for csv_file in all_csv_files:
    if csv_file == baseline:
        continue
    df_canTemp_comparison_sheet.loc[csv_file, 'CVRMSE(%)'] = cvrmse_percentage(df_canTemp_c_sheet['Baseline'], df_canTemp_c_sheet[csv_file])
    df_canTemp_comparison_sheet.loc[csv_file, 'NMBE(%)'] = normalized_mean_bias_error_percentage(df_canTemp_c_sheet['Baseline'], df_canTemp_c_sheet[csv_file])

df_canTemp_comparison_sheet.to_excel(all_sensitivity, sheet_name=sheet_names[2])
all_sensitivity.save()