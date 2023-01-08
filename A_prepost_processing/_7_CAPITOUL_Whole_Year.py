'''
1. To get the total electricity cooling
2. To get monthly electricity cooling, electricity heating, natural gas heating
3. To get the canyon temperature prediction CVRMSE, NMBE
'''
import os
import pathlib
import re
import sqlite3
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

def cvrmse(measurements, predictions):
    bias = predictions - measurements
    rmse = np.sqrt(np.mean(bias**2))
    cvrmse = rmse / np.mean(abs(measurements))
    return round(cvrmse*100, 2)

def normalized_mean_bias_error(measurements, predictions):
    bias = measurements - predictions
    nmb = np.mean(bias) / np.mean(measurements)
    return round(nmb*100, 2)
def read_sql(csv_file, month):
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
    '''
    Facility:Electricity:Cooling [J] 3151
    Facility:Electricity:Heating [J] 2955
    Facility:Gas:Heating [J] 3048
    '''
    ReportDataDictionaryIndex = 3151
    total_elec_cooling = f"SELECT * FROM ReportVariableWithTime WHERE ReportDataDictionaryIndex = {ReportDataDictionaryIndex}"
    with sqlite3.connect(sql_uri, uri=True) as con:
        cursor = con.cursor()
        results = cursor.execute(total_elec_cooling).fetchall()
        if results:
            pass
        else:
            msg = ("Cannot find the EnergyPlusVersion in the SQL file. "
                   "Please inspect query used:\n{}".format(total_elec_cooling))
            raise ValueError(msg)
    regex = r'(\d+\.?\d*)'
    # results is len(results), where each element is a tuple, tuple[4] is the value
    elec_cooling_J_lst = [float(re.search(regex, str(result[4])).group(1)) for result in results]
    monthly_elec_cooling_query = f"SELECT * FROM ReportVariableWithTime " \
                                 f"WHERE ReportDataDictionaryIndex = {ReportDataDictionaryIndex} " \
                                 f"AND Month = {month}"
    result = cursor.execute(monthly_elec_cooling_query).fetchall()
    monthly_elec_cooling_J_lst = [float(re.search(regex, str(result[4])).group(1)) for result in result]
    monthly_elec_heating_query = f"SELECT * FROM ReportVariableWithTime " \
                                    f"WHERE ReportDataDictionaryIndex = 2955 " \
                                    f"AND Month = {month}"
    result = cursor.execute(monthly_elec_heating_query).fetchall()
    monthly_elec_heating_J_lst = [float(re.search(regex, str(result[4])).group(1)) for result in result]
    monthly_gas_heating_query = f"SELECT * FROM ReportVariableWithTime " \
                                    f"WHERE ReportDataDictionaryIndex = 3048 " \
                                    f"AND Month = {month}"
    result = cursor.execute(monthly_gas_heating_query).fetchall()
    monthly_gas_heating_J_lst = [float(re.search(regex, str(result[4])).group(1)) for result in result]
    return monthly_elec_cooling_J_lst, monthly_elec_heating_J_lst, monthly_gas_heating_J_lst

def to_get_start_end_time(month):
    # compare_start_time = '2004-03-01 00:00:00'
    # compare_end_time = '2004-12-31 23:55:00'
    # 3, 5, 7, 8, 10, 12
    _31_month = [1, 3, 5, 7, 8, 10, 12]
    if month in _31_month:
        start_time = f'2004-{month}-01 00:00:00'
        end_time = f'2004-{month}-31 23:55:00'
    elif month == 2:
        start_time = f'2004-{month}-01 00:00:00'
        end_time = f'2004-{month}-28 23:55:00'
    else:
        start_time = f'2004-{month}-01 00:00:00'
        end_time = f'2004-{month}-30 23:55:00'
    return start_time, end_time

def get_CAPITOUL_measurements(processed_folder, processed_file,
                              compare_start_time, compare_end_time):
    file_path = os.path.join(processed_folder, processed_file)
    if os.path.exists(file_path):
        measurements = pd.read_csv(file_path, index_col=0, parse_dates=True)
        measurements = measurements[compare_start_time:compare_end_time]
        return measurements
    urban_path = os.path.join(processed_folder, 'Urban_Pomme_Ori_1_min.csv')
    rural_path = os.path.join(processed_folder, 'Rural_Ori_1_min.csv')
    urban = pd.read_csv(urban_path, index_col=0, parse_dates=True)
    rural = pd.read_csv(rural_path, index_col=0, parse_dates=True)
    urban_5min = urban.resample('5min').mean()
    rural_5min = rural.resample('5min').mean()
    urban_5min = urban_5min[compare_start_time:compare_end_time]
    rural_5min = rural_5min[compare_start_time:compare_end_time]
    #Air_Temperature_C, tpr_air2m_c13_cal_%60'_celsius, pre_air_c13_cal_%60'_hPa
    # initialize the dataframe, with the same index as rural, and 3 columns
    comparison = pd.DataFrame(index=rural_5min.index, columns=['Urban_DBT_C', 'Rural_DBT_C'])
    comparison['Urban_DBT_C'] = urban_5min['Air_Temperature_C']
    comparison['Rural_DBT_C'] = rural_5min['tpr_air2m_c13_cal_%60\'_celsius']
    comparison['Rural_Pres_Pa'] = rural_5min['pre_air_c13_cal_%60\'_hPa'] * 100
    comparison.to_csv(file_path)
    return comparison

def find_height_indice(df):
    cols = df.columns
    temp_prof_cols = [col for col in cols if 'TempProf_cur' in col]
    pres_prof_cols = [col for col in cols if 'PresProf_cur' in col]
    return temp_prof_cols, pres_prof_cols
def canyon_temp_performance(month, csv_filename, cooling_system):
    cvrmse_dict = {}
    nmbe_dict = {}
    compare_start_time, compare_end_time = to_get_start_end_time(month)
    processed_folder = os.path.join('_measurements', 'CAPITOUL')
    processed_file = r'CAPITOUL_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                     + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'
    comparison = get_CAPITOUL_measurements(processed_folder, processed_file,
                                                compare_start_time, compare_end_time)
    cvrmse_dict['Rural'] = cvrmse(comparison['Urban_DBT_C'], comparison['Rural_DBT_C'])
    nmbe_dict['Rural'] = normalized_mean_bias_error(comparison['Urban_DBT_C'], comparison['Rural_DBT_C'])
    print(f'cvrmse for Rural is {cvrmse_dict["Rural"]}, nmbe for Rural is {nmbe_dict["Rural"]}')

    df = pd.read_csv(os.path.join(experiments_folder, csv_filename), index_col=0, parse_dates=True)
    df = df[compare_start_time:compare_end_time]
    comparison['MeteoData.Pre'] = df['MeteoData.Pre']
    temp_prof_cols, pres_prof_cols = find_height_indice(df)
    # _onlyVCWG_temp_prof_cols, _onlyVCWG_pres_prof_cols = find_height_indice(df_onlyVCWG)
    month  = str(month)
    for i in range(len(temp_prof_cols)):
        comparison[month + '_'+temp_prof_cols[i]] = df[temp_prof_cols[i]]
        comparison[month + '_'+pres_prof_cols[i]] = df[pres_prof_cols[i]]
        height_idx = re.search(r'(\d+\.?\d*)', temp_prof_cols[i]).group(1)
        comparison[month + '_sensor_idx_' + height_idx] = (comparison[month + '_'+temp_prof_cols[i]]) * \
                                                            (comparison[month + '_'+pres_prof_cols[i]] / comparison['MeteoData.Pre']) \
                                                            ** 0.286 - 273.15
        if 'CAPITOUL' in csv_filename \
                or "Improvements" in csv_filename:
            _tmp_col = 'Urban_DBT_C'
        else:
            _tmp_col = 'Urban_DBT_C_' + height_idx
        tempCVRMSE = cvrmse(comparison[_tmp_col],
                                       comparison[month + '_sensor_idx_' + height_idx])
        cvrmse_dict[month + '_sensor_idx_' + height_idx] = tempCVRMSE
        tempNMBE = normalized_mean_bias_error(comparison[_tmp_col],
                                              comparison[month + '_sensor_idx_' + height_idx])
        nmbe_dict[month + '_sensor_idx_' + height_idx] = tempNMBE
        print(f'cvrmse for {month} at height idx:{height_idx} is {tempCVRMSE}, NMBE is {tempNMBE}')
    # #plot urban, rural sensor_idx
    # fig, ax = plt.subplots(figsize=(10, 6))
    # ax.plot(comparison['Urban_DBT_C'], label='Urban')
    # ax.plot(comparison['Rural_DBT_C'], label='Rural')
    # ax.plot(comparison[month + '_sensor_idx_' + height_idx], label = 'Predicted')
    # ax.set_xlabel('Time')
    # ax.set_ylabel('Temperature (C)')
    # ax.legend()
    # plt.show()
    comparison.to_csv(os.path.join(experiments_folder, month + '_'+cooling_system+'_time_series.csv'))
    return cvrmse_dict['Rural'], nmbe_dict['Rural'], cvrmse_dict[month + '_sensor_idx_' + height_idx], nmbe_dict[month + '_sensor_idx_' + height_idx]

def main():
    global experiments_folder
    experiments_folder = 'CAPITOUl_Whole_Year'
    experiments = []
    for file in os.listdir(experiments_folder):
        if file.endswith('.csv') and '3_12' in file:
            experiments.append(file)
    months = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    months = [3, 10, 11, 12]
    energy_dict = {}
    prediction_dict = {}
    for experiment in experiments:
        if 'WithCooling' in experiment:
            cooling_system = 'WithCooling'
        else:
            cooling_system = 'WithoutCooling'
        for month in months:
            monthly_elec_cooling_J_lst, monthly_elec_heating_J_lst, monthly_gas_heating_J_lst \
                = read_sql(experiment, month)
            elec_cooling_GJ = sum(monthly_elec_cooling_J_lst) / 1e9
            elec_heating_GJ = sum(monthly_elec_heating_J_lst) / 1e9
            gas_heating_GJ = sum(monthly_gas_heating_J_lst) / 1e9
            energy_dict[str(month) + '_' + cooling_system] = [elec_cooling_GJ, elec_heating_GJ, gas_heating_GJ]
            rural_cvrmse, rural_nmbe, sensor_idx_cvrmse, sensor_idx_nmbe = canyon_temp_performance(month, experiment, cooling_system)
            prediction_dict[str(month) + '_' + cooling_system] = [rural_cvrmse, rural_nmbe, sensor_idx_cvrmse, sensor_idx_nmbe]

    if os.path.exists(os.path.join(experiments_folder, 'Months_comparison.xlsx')):
        os.remove(os.path.join(experiments_folder, 'Months_comparison.xlsx'))
    writer = pd.ExcelWriter(os.path.join(experiments_folder, 'Months_comparison.xlsx'))
    df = pd.DataFrame.from_dict(energy_dict, orient='index', columns=['Elec_cooling_GJ', 'Elec_heating_GJ', 'Gas_heating_GJ'])
    df.to_excel(writer, sheet_name='Energy')
    df = pd.DataFrame.from_dict(prediction_dict, orient='index', columns=['Rural_CVRMSE_Percent', 'Rural_NMBE_Percent',
                                                                          'Sensor_idx_CVRMSE_Percent', 'Sensor_idx_NMBE_Percent'])
    df.to_excel(writer, sheet_name='Prediction')
    writer.save()

if __name__ == '__main__':
    main()

