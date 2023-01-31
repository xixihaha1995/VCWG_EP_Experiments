'''
1. To get the only VCWG comparison: -> One excel files
2. To generate EPW files -> All CSV corrsponding to the EPW files
3. To run EnergyPlus -> Corresponding SQL files
4. To get the offline comparison -> One excel file
'''
import os
import pathlib
import sqlite3
import sys
import re

import numpy as np

sys.path.insert(0, 'C:/EnergyPlusV22-1-0')
sys.path.insert(0, '/usr/local/EnergyPlus-22-1-0/')
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

def date_time_to_epw_ith_row_in_normal_year(date_time):
    # 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
    hours_in_normal_year = [744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744]
    month = date_time.month
    day = date_time.day
    hour = date_time.hour
    ith_hour = sum(hours_in_normal_year[:month - 1]) + (day - 1) * 24 + hour
    # ith_hour to ith_row
    ith_row = ith_hour + 8
    return ith_row
def generate_epw(experiment):
    state = ep_api.state_manager.new_state()
    psychrometric = ep_api.functional.psychrometrics(state)
    vcwg_outputs = pd.read_csv(os.path.join(experiments_folder,experiment), header=0, index_col=0, parse_dates=True)
    vcwg_outputs_hourly = vcwg_outputs.resample('H').mean()
    '''
    VCWG hour is 0-23, while epw hour is 1-24
    '''
    # read text based epw file line by line
    with open(epw_template, 'r') as f:
        lines = f.readlines()
        # iterate through vcwg_outpouts_hourly.index
        for i, date_time in enumerate(vcwg_outputs_hourly.index):
            ith_row = date_time_to_epw_ith_row_in_normal_year(date_time)
            lines[ith_row] = lines[ith_row].split(',')
            vcwg_prediction = vcwg_outputs_hourly.iloc[i]
            dry_bulb_c = vcwg_prediction['canTemp_K'] - 273.15
            humidity_ratio = vcwg_prediction['canHum_Ratio']
            press_pa = vcwg_prediction['canPres_Pa']
            relative_humidity_percentage = 100*psychrometric.relative_humidity_b(state,
                                                                             dry_bulb_c,humidity_ratio,press_pa)
            dew_point_c = psychrometric.dew_point(state, humidity_ratio, press_pa)
            lines[ith_row][6] = str(dry_bulb_c)
            lines[ith_row][7] = str(dew_point_c)
            lines[ith_row][8] = str(relative_humidity_percentage)
            lines[ith_row][9] = str(press_pa)
            lines[ith_row] = ','.join(lines[ith_row])

    generate_epw_name = experiment.replace('.csv', '.epw')
    generate_epw_path = os.path.join(experiments_folder, generate_epw_name)
    with open(generate_epw_path, 'w') as f:
        f.writelines(lines)
def run_energyplus(experiment):
    #/home/xiaoai/VCWG_EP_Experiments/resources/idf/Chicago/MediumOffice/RefBldgMediumOfficeNew2004_v1.4_7.2_5A_USA_IL_CHICAGO-OHARE_Ori0.idf
    'remove OnlyVCWG_IDFComplexity_'
    idf_template_name = experiment.replace('OnlyVCWG_IDFComplexity_', '')[:-4] + '.idf'

    output_path = os.path.join(experiments_folder,
                               f'{experiment[:-4]}_ep_trivial_outputs')
    project_path = os.path.dirname(os.path.abspath(__file__))
    idfFilePath = os.path.join(project_path,'..','resources','idf','Chicago',idfFolder,idf_template_name)
    sys_args = '-d', output_path, '-w', os.path.join(experiments_folder,experiment.replace('.csv', '.epw')), idfFilePath
    state = ep_api.state_manager.new_state()
    ep_api.runtime.run_energyplus(state, sys_args)

def sort_by_numbers(s):
    regex = r'(\d+\.?\d*)'
    return [float(x) for x in re.findall(regex, s)]
def get_offline_comparison(experiments):
    experiments.sort(key=sort_by_numbers)
    baseline = 'OnlyVCWG_Width_canyon_33.3_fveg_G_0_building_orientation_0.csv'
    sheet_names = ['Energy Consumption', 'CanTempC', 'CanTempComparison']

    all_dfs = {}
    for csv_file in experiments:
        df = pd.read_csv(os.path.join(experiments_folder, csv_file), index_col=0, parse_dates=True)
        all_dfs[csv_file] = df
    all_sensitivity = pd.ExcelWriter(os.path.join(experiments_folder, 'onlyVCWG_sensitivity.xlsx'))

    energy_sql_dict = {}
    energy_sql_dict['Baseline'] = read_sql(baseline)
    for csv_file in experiments:
        energy_sql_dict[csv_file] = (read_sql(csv_file))

    df_energy = pd.DataFrame.from_dict(energy_sql_dict, orient='index', columns=['Total Site Energy[GJ]',
                                                                                 'Cooling Electricity[GJ]',
                                                                                 'Heating Electricity[GJ]'])
    df_energy.to_excel(all_sensitivity, sheet_name=sheet_names[0])

    df_canTemp_c_sheet = pd.DataFrame(index=all_dfs[baseline].index)
    df_canTemp_c_sheet['Baseline'] = all_dfs[baseline]['canTemp_K'] - 273.15
    for csv_file in experiments:
        df_canTemp_c_sheet[csv_file] = all_dfs[csv_file]['canTemp_K'] - 273.15
    df_canTemp_c_sheet.to_excel(all_sensitivity, sheet_name=sheet_names[1])

    '''
    In the CanTempComparison sheet, the first column is the CVRMSE, the second column is the NMBE
    The index is all_csv_files.
    For each row, to compare the baseline with the sensitivity experiment
    '''
    df_canTemp_comparison_sheet = pd.DataFrame(index=experiments)
    df_canTemp_comparison_sheet['CVRMSE(%)'] = 0
    df_canTemp_comparison_sheet['NMBE(%)'] = 0
    for csv_file in experiments:
        df_canTemp_comparison_sheet.loc[csv_file, 'CVRMSE(%)'] = cvrmse_percentage(df_canTemp_c_sheet['Baseline'],
                                                                                   df_canTemp_c_sheet[csv_file])
        df_canTemp_comparison_sheet.loc[csv_file, 'NMBE(%)'] = normalized_mean_bias_error_percentage(
            df_canTemp_c_sheet['Baseline'], df_canTemp_c_sheet[csv_file])
    # insert the baseline row
    df_canTemp_comparison_sheet.loc['Baseline', 'CVRMSE(%)'] = 0
    df_canTemp_comparison_sheet.loc['Baseline', 'NMBE(%)'] = 0
    df_canTemp_comparison_sheet.to_excel(all_sensitivity, sheet_name=sheet_names[2])
    all_sensitivity.save()
def main():
    global experiments_folder, epw_template,ep_api, idfFolder
    from pyenergyplus.api import EnergyPlusAPI
    ep_api = EnergyPlusAPI()
    epw_template = os.path.join('..','resources','epw','USA_IL_Chicago-OHare.Intl.AP.725300_TMY3_No_Precipitable_Water.epw')

    experiments_folder = 'Chicago_MedOffice_IDFComplexity'
    idfFolder = 'MediumOffice'

    experiments_folder = 'Chicago_HighOffice_IDFComplexity'
    idfFolder = 'HighBuilding'

    experiments = []
    for experiment in os.listdir(experiments_folder):
        if experiment.endswith('.csv') and 'OnlyVCWG' in experiment:
            experiments.append(experiment)
    for experiment in experiments:
        generate_epw(experiment)
        # run_energyplus(experiment)

    # get_offline_comparison(experiments)

if __name__ == '__main__':
    main()