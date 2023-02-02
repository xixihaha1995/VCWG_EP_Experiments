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

    cooling_demand_query = f"SELECT * FROM TabularDataWithStrings WHERE ReportName = 'DemandEndUseComponentsSummary'" \
                           f"And RowName = 'Cooling' "
    cooling_demand_query_results = cursor.execute(cooling_demand_query).fetchall()
    cooling_demand = float(re.findall(regex, cooling_demand_query_results[0][1])[0])
    return totalEnergy, cooling_electricity, heating_electricity, cooling_demand
def read_csv_energy(csv_file):
    '''
    Returns:
        ElecTotal[J] coolConsump[J]	heatConsump[J]
        convert to GJ
    '''
    df = pd.read_csv(os.path.join(experiments_folder, csv_file), index_col=0, parse_dates=True)
    #sum over all the desired columns
    elecTotal = df['ElecTotal[J_m2]'].sum()
    gasTotal = df['GasTotal[J_m2]'].sum()
    coolConsump = df['coolConsump[J_m2]'].sum()
    heatConsump = df['heatConsump[J_m2]'].sum()
    total = elecTotal + gasTotal
    return round(total/1e6, 2), round(coolConsump/1e6, 2), round(heatConsump/1e6, 2)

plot_fontsize = 12
experiments_folder = 'Chicago_MedOffice_IDFComplexity'
baseline = 'ByPass_IDFComplexity_Detailed_MedOffice.csv'
footprint_area_m2 = 53628 * 0.09290304 / 3

# experiments_folder = 'Chicago_HighOffice_IDFComplexity'
# baseline = 'ByPass_IDFComplexity_Detailed_HighOffice.csv'
# footprint_area_m2 = 31 * 15

'''
read all csv files, containing OnlyVCWG or PartialVCWG, and create a new excel file with the following sheets:
sheet_names = ['Energy Consumption','CanTempC', 'CanTempComparison']
'''
def sort_by_numbers(s):
    regex = r'(\d+\.?\d*)'
    return [float(x) for x in re.findall(regex, s)]

def excel_letters(idx):
    #idx:0, letter:A
    #idx:1, letter:B
    #idx:25, letter:Z
    #idx:26, letter:AA
    if idx < 26:
        return chr(idx + 65)
    else:
        return excel_letters(idx//26 - 1) + excel_letters(idx%26)

def add_excel_formula(df_excel):
    #for each column, B,C ...
    # The first row is the header, so we start from the second row
    # add three cells(with formula) at the bottom:
    # 1. the average of the column
    # 2. the max of the column
    # 3. the min of the column
    # 4. the standard deviation of the column
    length = df_excel.shape[0] + 1
    for idx, col in enumerate(df_excel.columns):
        idx_letter = excel_letters(idx + 1)
        df_excel.loc['Average', col] = f'=AVERAGE({idx_letter}2:{idx_letter}{length})'
        df_excel.loc['Max', col] = f'=MAX({idx_letter}2:{idx_letter}{length})'
        df_excel.loc['Min', col] = f'=MIN({idx_letter}2:{idx_letter}{length})'
        df_excel.loc['Std', col] = f'=STDEV({idx_letter}2:{idx_letter}{length})'
    return df_excel

all_csv_files = [f for f in os.listdir(experiments_folder)
                 if f.endswith('.csv')]

all_csv_files.sort(key=sort_by_numbers)
sheet_names = ['CanTempComparison_CVRMSE', 'CanTempComparison_NMBE',
               'Total[GJ]', 'Cooling[GJ]', 'Heating[GJ]', 'CanTempC']
'''
Extract indices from the all_csv_files:
1. create a set
2. iterate over all_csv_files, remove the prefix (ByPass_,OnlyVCWG_ or PartialVCWG_)
'''
indices = set()
for csv_file in all_csv_files:
    csv_file = csv_file.replace('ByPass_', '')
    csv_file = csv_file.replace('OnlyVCWG_', '')
    csv_file = csv_file.replace('PartialVCWG_', '')
    indices.add(csv_file)
indices = sorted(indices, key=sort_by_numbers)
indices = [x for x in indices]
all_dfs = {}
for csv_file in all_csv_files:
    df = pd.read_csv(os.path.join(experiments_folder, csv_file), index_col=0, parse_dates=True)
    all_dfs[csv_file] = df

if 'HighOffice' in experiments_folder:
    all_sensitivity = pd.ExcelWriter(os.path.join(experiments_folder, 'HighOffice_IDFComplexity_Framework.xlsx'))
else:
    all_sensitivity = pd.ExcelWriter(os.path.join(experiments_folder, 'MedOffice_IDFComplexity_Framework.xlsx'))

#'CanTempC'
df_canTemp_c_sheet = pd.DataFrame(index=all_dfs[baseline].index)
df_canTemp_c_sheet['Baseline'] = all_dfs[baseline]['canTemp'] - 273.15
for csv_file in all_csv_files:
    if 'canTemp' in all_dfs[csv_file].columns:
        df_canTemp_c_sheet[csv_file] = all_dfs[csv_file]['canTemp'] - 273.15
    else:
        df_canTemp_c_sheet[csv_file] = all_dfs[csv_file]['canTemp_K'] - 273.15

'''
In the CanTempComparison_CVRMSE sheet, the columns are: ByPass, OnlyVCWG/PartialVCWG, and Offline
The index is indices.
'''
def get_col_and_index(csv_file_name):
    if 'ByPass' in csv_file_name:
        return 'ByPass', csv_file_name[7:]
    elif 'OnlyVCWG' in csv_file_name:
        return 'OnlyVCWG', csv_file_name[9:]
# 'CanTempComparison_CVRMSE'
df_canTemp_comparison_sheet = pd.DataFrame(index=indices)
for csv_file in all_csv_files:
    _cvrmse = cvrmse_percentage(df_canTemp_c_sheet['Baseline'], df_canTemp_c_sheet[csv_file])
    _col, _index = get_col_and_index(csv_file)
    df_canTemp_comparison_sheet.loc[_index, _col] = _cvrmse
    if 'ByPass' not in csv_file:
        df_canTemp_comparison_sheet.loc[_index, 'Offline'] = _cvrmse
df_canTemp_comparison_sheet.to_excel(all_sensitivity, sheet_name='CanTempComparison_CVRMSE')

# 'CanTempComparison_NMBE'
df_canTemp_comparison_sheet = pd.DataFrame(index=indices)
for csv_file in all_csv_files:
    _nmb = normalized_mean_bias_error_percentage(df_canTemp_c_sheet['Baseline'], df_canTemp_c_sheet[csv_file])
    _col, _index = get_col_and_index(csv_file)
    df_canTemp_comparison_sheet.loc[_index, _col] = _nmb
    if 'ByPass' not in csv_file:
        df_canTemp_comparison_sheet.loc[_index, 'Offline'] = _nmb
df_canTemp_comparison_sheet.to_excel(all_sensitivity, sheet_name='CanTempComparison_NMBE')

#Cooling[GJ]
df_cooling_sheet = pd.DataFrame(index=indices)
df_heating_sheet = pd.DataFrame(index=indices)
df_total_sheet = pd.DataFrame(index=indices)
df_cooling_baseline_sheet = pd.DataFrame(index=indices)
df_cooling_demand_sheet = pd.DataFrame(index=indices)
df_cooling_demand_percent_sheet = pd.DataFrame(index=indices)
baseline_energy = (read_sql(baseline))
for csv_file in all_csv_files:
    _col, _index = get_col_and_index(csv_file)
    if 'ByPass' in csv_file:
        energy_tuple = (read_sql(csv_file))
        df_cooling_sheet.loc[_index, _col] = energy_tuple[1]
        df_heating_sheet.loc[_index, _col] = energy_tuple[2]
        df_total_sheet.loc[_index, _col] = energy_tuple[0]
        tmp_cooling_per = round((energy_tuple[1] - baseline_energy[1]) / baseline_energy[1] * 100, 2)
        df_cooling_baseline_sheet.loc[_index, _col] = tmp_cooling_per
        df_cooling_demand_sheet.loc[_index, _col] = energy_tuple[3]
        tmp_cooling_demand_per = round((energy_tuple[3] - baseline_energy[3]) / baseline_energy[3] * 100, 2)
        df_cooling_demand_percent_sheet.loc[_index, _col] = tmp_cooling_demand_per
    else:
        energy_tuple = (read_csv_energy(csv_file))
        df_cooling_sheet.loc[_index, _col] = energy_tuple[1]
        df_heating_sheet.loc[_index, _col] = energy_tuple[2]
        df_total_sheet.loc[_index, _col] = energy_tuple[0]
        tmp_cooling_per = round((energy_tuple[1] - baseline_energy[1]) / baseline_energy[1] * 100, 2)
        df_cooling_baseline_sheet.loc[_index, _col] = tmp_cooling_per
        _offline_energy = (read_sql(csv_file))
        df_cooling_sheet.loc[_index, 'Offline'] = _offline_energy[1]
        df_heating_sheet.loc[_index, 'Offline'] = _offline_energy[2]
        df_total_sheet.loc[_index, 'Offline'] = _offline_energy[0]
        tmp_cooling_per = round((_offline_energy[1] - baseline_energy[1]) / baseline_energy[1] * 100, 2)
        df_cooling_baseline_sheet.loc[_index, 'Offline'] = tmp_cooling_per
        df_cooling_demand_sheet.loc[_index, 'Offline'] = _offline_energy[3]
        tmp_cooling_demand_per = round((_offline_energy[3] - baseline_energy[3]) / baseline_energy[3] * 100, 2)
        df_cooling_demand_percent_sheet.loc[_index, 'OnlyVCWG'] = tmp_cooling_demand_per
        df_cooling_demand_percent_sheet.loc[_index, 'Offline'] = tmp_cooling_demand_per

df_cooling_baseline_sheet.to_excel(all_sensitivity, sheet_name='Cooling_Baseline_Percent')
df_cooling_sheet.to_excel(all_sensitivity, sheet_name='Cooling_GJ')
df_heating_sheet.to_excel(all_sensitivity, sheet_name='Heating_GJ')
df_total_sheet.to_excel(all_sensitivity, sheet_name='Total_GJ')
df_canTemp_c_sheet = add_excel_formula(df_canTemp_c_sheet)
df_canTemp_c_sheet.to_excel(all_sensitivity, sheet_name='CanTempC')
df_cooling_demand_sheet.to_excel(all_sensitivity, sheet_name='Cooling_Demand_W')
df_cooling_demand_percent_sheet.to_excel(all_sensitivity, sheet_name='Cooling_Demand_Percent')
all_sensitivity.save()