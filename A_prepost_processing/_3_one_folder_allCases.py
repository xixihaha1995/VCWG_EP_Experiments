import os, csv, numpy as np, pandas as pd, re
import pathlib
import sqlite3
from shutil import copyfile

from matplotlib import pyplot as plt

def cvrmse(measurements, predictions):
    bias = predictions - measurements
    rmse = np.sqrt(np.mean(bias**2))
    cvrmse = rmse / np.mean(abs(measurements))
    return round(cvrmse*100, 2)

def normalized_mean_bias_error(measurements, predictions):
    bias = measurements - predictions
    nmb = np.mean(bias) / np.mean(measurements)
    return round(nmb*100, 2)
def read_text_as_csv(file_path, header=None, index_col=0, skiprows=3):
    '''
    df first column is index
    '''
    df = pd.read_csv(file_path, skiprows= skiprows, header= header, index_col=index_col, sep= '[ ^]+', engine='python')
    df.index = pd.to_datetime(df.index, format='%d.%m.%Y')
    # index format is YYYY-MM-DD HH:MM:SS
    # replace HH:MM with first 5 char of 0th column, convert to datetime
    df.index = pd.to_datetime(df.index.strftime('%Y-%m-%d') + ' ' + df.iloc[:,0].str[:5])
    repeated_index = df.index[df.index.duplicated()]
    df = df.drop(repeated_index)
    target_idx = pd.date_range(start=df.index[0], end=df.index[-1], freq='10min')
    missing_index = target_idx.difference(df.index)
    if len(repeated_index) != 0 or len(missing_index) != 0:
        print('Repeated index:', repeated_index)
        print('Missing index:', missing_index)
        print('---------------------------------------------------')
    # 3. add the missed empty rows, dtype is float
    df = df.reindex(target_idx)
    # drop the 0th column, according to the index instead of column name
    df.drop(df.columns[0], axis=1, inplace=True)
    df.iloc[:, :-1] = df.iloc[:, :-1].apply(lambda x: x.str.replace(',', '')).astype(float)
    # interpolate the missing values
    df = df.interpolate(method='linear')
    return df

def clean_urban(df):
    repeated_index = df.index[df.index.duplicated()]
    df = df.drop(repeated_index)
    target_idx = pd.date_range(start=df.index[0], end=df.index[-1], freq='10min')
    missing_index = target_idx.difference(df.index)
    if len(repeated_index) != 0 or len(missing_index) != 0:
        print('Repeated index:', repeated_index)
        print('Missing index:', missing_index)
        print('---------------------------------------------------')
    # 3. add the missed empty rows, dtype is float
    df = df.reindex(target_idx)
    df = df.interpolate(method='linear')
    return df

def get_BUUBLE_Ue1_measurements():
    file_path  = os.path.join(processed_folder, processed_file)
    if os.path.exists(file_path):
        measurements = pd.read_csv(file_path, index_col=0, parse_dates=True)
        measurements = measurements[compare_start_time:compare_end_time]
        return measurements

    # urban_path = r'measurements/BUBBLE_BSPR_AT_PROFILE_IOP.txt'
    # rural_path = r'measurements/BUBBLE_AT_IOP.txt'
    urban_path = os.path.join(processed_folder, 'BUBBLE_BSPR_AT_PROFILE_IOP.txt')
    rural_path = os.path.join(processed_folder, 'BUBBLE_AT_IOP.txt')

    urban_dirty = read_text_as_csv(urban_path,header=0, index_col=0, skiprows=16)
    urban = clean_urban(urban_dirty)
    urban = urban[compare_start_time:compare_end_time]

    mixed_all_sites_10min = read_text_as_csv(rural_path,header=0, index_col=0, skiprows=25)
    mixed_all_sites_10min = mixed_all_sites_10min[compare_start_time:compare_end_time]

    comparison = pd.DataFrame(index=mixed_all_sites_10min.index,columns = range(6))
    comparison.columns = ['Urban_DBT_C_2.6', 'Urban_DBT_C_13.9',
                          'Urban_DBT_C_17.5', 'Urban_DBT_C_21.5', 'Urban_DBT_C_25.5', 'Urban_DBT_C_31.2']
    comparison['Urban_DBT_C_2.6'] = urban.iloc[:, 0]
    comparison['Urban_DBT_C_13.9'] = urban.iloc[:, 1]
    comparison['Urban_DBT_C_17.5'] = urban.iloc[:, 2]
    comparison['Urban_DBT_C_21.5'] = urban.iloc[:, 3]
    comparison['Urban_DBT_C_25.5'] = urban.iloc[:, 4]
    comparison['Urban_DBT_C_31.2'] = urban.iloc[:, 5]
    comparison['Rural_DBT_C'] = mixed_all_sites_10min.iloc[:, 7]
    comparison.to_csv(file_path)
    return comparison

def get_BUUBLE_Ue2_measurements():
    file_path  = os.path.join(processed_folder, processed_file)
    if os.path.exists(file_path):
        measurements = pd.read_csv(file_path, index_col=0, parse_dates=True)
        measurements = measurements[compare_start_time:compare_end_time]
        return measurements

    urban_path = os.path.join(processed_folder, 'BUBBLE_BSPA_AT_PROFILE_IOP.txt')
    rural_path = os.path.join(processed_folder, 'BUBBLE_AT_IOP.txt')

    urban_dirty = read_text_as_csv(urban_path,header=0, index_col=0, skiprows=17)
    urban = clean_urban(urban_dirty)
    urban = urban[compare_start_time:compare_end_time]

    mixed_all_sites_10min = read_text_as_csv(rural_path,header=0, index_col=0, skiprows=25)
    mixed_all_sites_10min = mixed_all_sites_10min[compare_start_time:compare_end_time]

    comparison = pd.DataFrame(index=mixed_all_sites_10min.index, columns = range(5))

    comparison.columns = ['Urban_DBT_C_3.0', 'Urban_DBT_C_15.8',
                            'Urban_DBT_C_22.9', 'Urban_DBT_C_27.8', 'Urban_DBT_C_32.9']
    comparison['Rural_DBT_C'] = mixed_all_sites_10min.iloc[:, 7]
    comparison['Urban_DBT_C_3.0'] = (urban.iloc[:, 0] + urban.iloc[:, 2]) / 2
    comparison['Urban_DBT_C_15.8'] = (urban.iloc[:, 1] + urban.iloc[:, 3]) / 2
    comparison['Urban_DBT_C_22.9'] = urban.iloc[:, 4]
    comparison['Urban_DBT_C_27.8'] = urban.iloc[:, 5]
    comparison['Urban_DBT_C_32.9'] = urban.iloc[:, 6]
    comparison.to_csv(file_path)
    return comparison
def get_CAPITOUL_measurements():
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

def get_Vancouver_measurements(csv_filename):
    file_path = os.path.join(processed_folder, processed_file)
    if os.path.exists(file_path):
        measurements = pd.read_csv(file_path, index_col=0, parse_dates=True)
        measurements = measurements[compare_start_time:compare_end_time]
        return measurements
    urban_path = os.path.join(processed_folder, 'SSDTA_all_30min.csv')
    urban_hourly = pd.read_csv(urban_path, index_col=0, parse_dates=True)
    urban_hourly = urban_hourly.astype(float)
    urban_30min = urban_hourly.resample('30min').interpolate()
    urban_30min = urban_30min[compare_start_time:compare_end_time]

    comparison = pd.DataFrame(index=urban_30min.index, columns=['Urban_DBT_C', 'Rural_DBT_C'])
    comparison['Urban_DBT_C_1.2'] = urban_30min.iloc[:, 0]
    comparison['Urban_DBT_C_20.0'] = urban_30min.iloc[:, 1]


    if 'TopForcing' in csv_filename:
        rural_path = os.path.join(processed_folder, 'Vancouver_TopForcing_2008_ERA5_Jul.csv')
        rural_hourly = pd.read_csv(rural_path, index_col=0, parse_dates=True, skiprows=1)
    else:
        rural_path = os.path.join(processed_folder, 'Vancouver_Rural_ECCC_BC_1108447_MM-2008_P1H.csv')
        rural_hourly = pd.read_csv(rural_path, index_col=0, parse_dates=True)
    rural_hourly = rural_hourly.astype(float)
    rural_30min = rural_hourly.resample('30min').interpolate()
    rural_30min = rural_30min[compare_start_time:compare_end_time]

    comparison['Rural_DBT_C'] = rural_30min.iloc[:, 0]
    if 'TopForcing' in csv_filename:
        comparison['Rural_Pres_Pa'] = rural_30min.iloc[:, 1] * 100
    else:
        comparison['Rural_Pres_Pa'] = rural_30min.iloc[:, 3] * 1000
    comparison.to_csv(file_path)
    return comparison

def read_sql(csv_file):
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
    number = float(re.findall(regex, results[0][1])[0])
    return number
def find_height_indice(df):
    cols = df.columns
    temp_prof_cols = [col for col in cols if 'TempProf_cur' in col]
    pres_prof_cols = [col for col in cols if 'PresProf_cur' in col]
    return temp_prof_cols, pres_prof_cols


def process_one_theme(csv_filename):
    global processed_folder, processed_file, \
        compare_start_time, compare_end_time
    if "BUBBLE" in csv_filename:
        compare_start_time = '2002-06-10 00:10:00'
        compare_end_time = '2002-07-09 21:50:00'
        processed_folder =  os.path.join('_measurements','BUBBLE')
        if 'UE1' in csv_filename:
            processed_file = 'BUBBLE_UE1_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                                 + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'
        elif 'UE2' in csv_filename:
            processed_file = 'BUBBLE_UE2_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                                 + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'
    elif "CAPITOUL" in csv_filename:
        compare_start_time = '2004-06-01 00:00:00'
        compare_end_time = '2004-06-30 23:55:00'
        processed_folder =  os.path.join('_measurements','CAPITOUL')
        processed_file = r'CAPITOUL_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                                 + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'
    else:
        compare_start_time = '2008-07-01 00:30:00'
        compare_end_time = '2008-07-31 23:00:00'
        processed_folder = os.path.join('_measurements', 'VANCOUVER')
        if 'TopForcing' in csv_filename:
            processed_file = r'Vancouver_TopForcing_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                         + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'
        else:
            processed_file = r'Vancouver_Rural_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                         + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'

    cvrmse_dict = {}
    nmbe_dict = {}
    if "BUBBLE_UE1" in csv_filename:
        comparison = get_BUUBLE_Ue1_measurements()
        cvrmse_dict['Rural_2.6'] = cvrmse(comparison['Urban_DBT_C_2.6'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_13.9'] = cvrmse(comparison['Urban_DBT_C_13.9'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_17.5'] = cvrmse(comparison['Urban_DBT_C_17.5'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_21.5'] = cvrmse(comparison['Urban_DBT_C_21.5'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_25.5'] = cvrmse(comparison['Urban_DBT_C_25.5'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_31.2'] = cvrmse(comparison['Urban_DBT_C_31.2'], comparison['Rural_DBT_C'])
        nmbe_dict['Rural_2.6'] = normalized_mean_bias_error(comparison['Urban_DBT_C_2.6'], comparison['Rural_DBT_C'])
        nmbe_dict['Rural_13.9'] = normalized_mean_bias_error(comparison['Urban_DBT_C_13.9'], comparison['Rural_DBT_C'])
        nmbe_dict['Rural_17.5'] = normalized_mean_bias_error(comparison['Urban_DBT_C_17.5'], comparison['Rural_DBT_C'])
        nmbe_dict['Rural_21.5'] = normalized_mean_bias_error(comparison['Urban_DBT_C_21.5'], comparison['Rural_DBT_C'])
        nmbe_dict['Rural_25.5'] = normalized_mean_bias_error(comparison['Urban_DBT_C_25.5'], comparison['Rural_DBT_C'])
        nmbe_dict['Rural_31.2'] = normalized_mean_bias_error(comparison['Urban_DBT_C_31.2'], comparison['Rural_DBT_C'])

        print(f'cvrmse for Rural_2.6 is {cvrmse_dict["Rural_2.6"]}, nmbe is {nmbe_dict["Rural_2.6"]}')
        print(f'cvrmse for Rural_13.9 is {cvrmse_dict["Rural_13.9"]}, nmbe is {nmbe_dict["Rural_13.9"]}')
        print(f'cvrmse for Rural_17.5 is {cvrmse_dict["Rural_17.5"]}, nmbe is {nmbe_dict["Rural_17.5"]}')
        print(f'cvrmse for Rural_21.5 is {cvrmse_dict["Rural_21.5"]}, nmbe is {nmbe_dict["Rural_21.5"]}')
        print(f'cvrmse for Rural_25.5 is {cvrmse_dict["Rural_25.5"]}, nmbe is {nmbe_dict["Rural_25.5"]}')
        print(f'cvrmse for Rural_31.2 is {cvrmse_dict["Rural_31.2"]}, nmbe is {nmbe_dict["Rural_31.2"]}')

    elif "BUBBLE_UE2" in csv_filename:
        comparison = get_BUUBLE_Ue2_measurements()
        cvrmse_dict['Rural_3.0'] = cvrmse(comparison['Urban_DBT_C_3.0'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_15.8'] = cvrmse(comparison['Urban_DBT_C_15.8'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_22.9'] = cvrmse(comparison['Urban_DBT_C_22.9'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_27.8'] = cvrmse(comparison['Urban_DBT_C_27.8'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_32.9'] = cvrmse(comparison['Urban_DBT_C_32.9'], comparison['Rural_DBT_C'])
        nmbe_dict['Rural_3.0'] = normalized_mean_bias_error(comparison['Urban_DBT_C_3.0'], comparison['Rural_DBT_C'])
        nmbe_dict['Rural_15.8'] = normalized_mean_bias_error(comparison['Urban_DBT_C_15.8'], comparison['Rural_DBT_C'])
        nmbe_dict['Rural_22.9'] = normalized_mean_bias_error(comparison['Urban_DBT_C_22.9'], comparison['Rural_DBT_C'])
        nmbe_dict['Rural_27.8'] = normalized_mean_bias_error(comparison['Urban_DBT_C_27.8'], comparison['Rural_DBT_C'])
        nmbe_dict['Rural_32.9'] = normalized_mean_bias_error(comparison['Urban_DBT_C_32.9'], comparison['Rural_DBT_C'])

        print(f'cvrmse for Rural vs Urban(3.0) is {cvrmse_dict["Rural_3.0"]}, nmbe is {nmbe_dict["Rural_3.0"]}')
        print(f'cvrmse for Rural vs Urban(15.8) is {cvrmse_dict["Rural_15.8"]}, nmbe is {nmbe_dict["Rural_15.8"]}')
        print(f'cvrmse for Rural vs Urban(22.9) is {cvrmse_dict["Rural_22.9"]}, nmbe is {nmbe_dict["Rural_22.9"]}')
        print(f'cvrmse for Rural vs Urban(27.8) is {cvrmse_dict["Rural_27.8"]}, nmbe is {nmbe_dict["Rural_27.8"]}')
        print(f'cvrmse for Rural vs Urban(32.9) is {cvrmse_dict["Rural_32.9"]}, nmbe is {nmbe_dict["Rural_32.9"]}')
    elif 'Vancouver' in csv_filename:
        comparison = get_Vancouver_measurements(csv_filename)
        cvrmse_dict['Rural_1.2'] = cvrmse(comparison['Urban_DBT_C_1.2'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_20.0'] = cvrmse(comparison['Urban_DBT_C_20.0'], comparison['Rural_DBT_C'])
        nmbe_dict['Rural_1.2'] = normalized_mean_bias_error(comparison['Urban_DBT_C_1.2'], comparison['Rural_DBT_C'])
        nmbe_dict['Rural_20.0'] = normalized_mean_bias_error(comparison['Urban_DBT_C_20.0'], comparison['Rural_DBT_C'])
        print(f'cvrmse for Rural vs Urban(1.2) is {cvrmse_dict["Rural_1.2"]}, nmbe is {nmbe_dict["Rural_1.2"]}')
        print(f'cvrmse for Rural vs Urban(20.0) is {cvrmse_dict["Rural_20.0"]}, nmbe is {nmbe_dict["Rural_20.0"]}')
    else:
        comparison = get_CAPITOUL_measurements()
        cvrmse_dict['Rural'] = cvrmse(comparison['Urban_DBT_C'], comparison['Rural_DBT_C'])
        nmbe_dict['Rural'] = normalized_mean_bias_error(comparison['Urban_DBT_C'], comparison['Rural_DBT_C'])
        print(f'cvrmse for Rural is {cvrmse_dict["Rural"]}, nmbe for Rural is {nmbe_dict["Rural"]}')


    sql_dict = {}
    df = pd.read_csv(os.path.join(experiments_folder, csv_filename), index_col=0, parse_dates=True)
    csv_file = csv_filename.split('.')[0]
    df = df[compare_start_time:compare_end_time]
    comparison['MeteoData.Pre'] = df['MeteoData.Pre']
    comparison['sensWaste_' + csv_filename] = df['sensWaste']
    comparison['wallSun_K_' + csv_filename] = df['wallSun_K']
    comparison['wallShade_K_' + csv_filename] = df['wallShade_K']
    comparison['roof_K_' + csv_filename] = df['roof_K']
    comparison['ForcTemp_K_' + csv_filename] = df['ForcTemp_K']
    # #OnlyVCWG
    # df_onlyVCWG = pd.read_csv(os.path.join(experiments_folder, 'OnlyVCWG_' + csv_file[7:] + '.csv'), index_col=0, parse_dates=True)
    # comparison['sensWaste_' + 'OnlyVCWG_'+csv_filename] = df_onlyVCWG['sensWaste']
    # comparison['wallSun_K_' + 'OnlyVCWG_'+csv_filename] = df_onlyVCWG['wallSun_K']
    # comparison['wallShade_K_' + 'OnlyVCWG_'+csv_filename] = df_onlyVCWG['wallShade_K']
    # comparison['roof_K_' + 'OnlyVCWG_'+csv_filename] = df_onlyVCWG['roof_K']

    temp_prof_cols, pres_prof_cols = find_height_indice(df)
    # _onlyVCWG_temp_prof_cols, _onlyVCWG_pres_prof_cols = find_height_indice(df_onlyVCWG)
    for i in range(len(temp_prof_cols)):
        comparison[csv_file + '_'+temp_prof_cols[i]] = df[temp_prof_cols[i]]
        comparison[csv_file + '_'+pres_prof_cols[i]] = df[pres_prof_cols[i]]
        height_idx = re.search(r'(\d+\.?\d*)', temp_prof_cols[i]).group(1)
        comparison[csv_file + '_sensor_idx_' + height_idx] = (comparison[csv_file + '_'+temp_prof_cols[i]]) * \
                                                            (comparison[csv_file + '_'+pres_prof_cols[i]] / comparison['MeteoData.Pre']) \
                                                            ** 0.286 - 273.15
        # comparison['OnlyVCWG_' + csv_file + '_'+temp_prof_cols[i]] = df_onlyVCWG[temp_prof_cols[i]]
        # comparison['OnlyVCWG_' + csv_file + '_'+pres_prof_cols[i]] = df_onlyVCWG[pres_prof_cols[i]]
        # comparison['OnlyVCWG_' + csv_file + '_sensor_idx_' + height_idx] = (comparison['OnlyVCWG_' + csv_file + '_'+temp_prof_cols[i]]) * \
        #                                                     (comparison['OnlyVCWG_' + csv_file + '_'+pres_prof_cols[i]] / comparison['MeteoData.Pre']) \
        #                                                     ** 0.286 - 273.15

        if 'CAPITOUL' in csv_filename \
                or "Improvements" in csv_filename:
            _tmp_col = 'Urban_DBT_C'
        else:
            _tmp_col = 'Urban_DBT_C_' + height_idx
        tempCVRMSE = cvrmse(comparison[_tmp_col],
                                       comparison[csv_file + '_sensor_idx_' + height_idx])
        cvrmse_dict[csv_file + '_sensor_idx_' + height_idx] = tempCVRMSE
        # _onlyVCWG_tempCVRMSE = cvrmse(comparison[_tmp_col],
        #                                 comparison['OnlyVCWG_' + csv_file + '_sensor_idx_' + height_idx])
        # cvrmse_dict['OnlyVCWG_' + csv_file + '_sensor_idx_' + height_idx] = _onlyVCWG_tempCVRMSE
        tempNMBE = normalized_mean_bias_error(comparison[_tmp_col],
                                              comparison[csv_file + '_sensor_idx_' + height_idx])
        nmbe_dict[csv_file + '_sensor_idx_' + height_idx] = tempNMBE
        # _onlyVCWG_tempNMBE = normalized_mean_bias_error(comparison[_tmp_col],
        #                                                 comparison['OnlyVCWG_' + csv_file + '_sensor_idx_' + height_idx])
        # nmbe_dict['OnlyVCWG_' + csv_file + '_sensor_idx_' + height_idx] = _onlyVCWG_tempNMBE
        print(f'cvrmse for {csv_file} at height idx:{height_idx} is {tempCVRMSE}, NMBE is {tempNMBE}')
        # print(f'cvrmse for OnlyVCWG_{csv_file} at height idx:{height_idx} is {_onlyVCWG_tempCVRMSE}, NMBE is {_onlyVCWG_tempNMBE}')

    # sql_dict[csv_file] = read_sql(csv_filename)
    # if os.path.exists(os.path.join(experiments_folder, csv_file + 'comparison.xlsx')):
    #     os.remove(os.path.join(experiments_folder, csv_file + 'comparison.xlsx'))
    # writer = pd.ExcelWriter(os.path.join(experiments_folder, csv_file + 'comparison.xlsx'))
    # comparison.to_excel(writer, 'comparison')
    # cvrmse_df = pd.DataFrame.from_dict(cvrmse_dict, orient='index', columns=['cvrmse'])
    # cvrmse_df.to_excel(writer, 'cvrmse')
    # nmbe_df = pd.DataFrame.from_dict(nmbe_dict, orient='index', columns=['nmbe'])
    # nmbe_df.to_excel(writer, 'nmbe')
    # sql_df = pd.DataFrame.from_dict(sql_dict, orient='index', columns=['total_site_energy'])
    # sql_df.to_excel(writer, 'sql')
    # writer.save()

def iterate_all_cases(experiments_folder):
    csv_files = []
    for file in os.listdir(experiments_folder):
        if file.endswith('.csv') and 'OnlyVCWG' not in file and 'WithoutShading' in file:
            csv_files.append(file)
            process_one_theme(file,)

def main():
    global sql_report_name, sql_table_name, sql_row_name, sql_col_name
    global experiments_folder
    experiments_folder = 'AllCases_Roughness'
    sql_report_name = 'AnnualBuildingUtilityPerformanceSummary'
    sql_table_name = 'Site and Source Energy'
    sql_row_name = 'Total Site Energy'
    sql_col_name = 'Total Energy'
    iterate_all_cases(experiments_folder)
if __name__ == '__main__':
    main()