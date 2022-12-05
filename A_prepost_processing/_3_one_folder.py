import os, csv, numpy as np, pandas as pd, re
import pathlib
import sqlite3
from shutil import copyfile

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

def get_Vancouver_measurements():
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
    comparison['Urban_DBT_C'] = urban_30min.iloc[:, 0]


    if 'TopForcing' in experiments_folder:
        rural_path = os.path.join(processed_folder, 'Vancouver_TopForcing_2008_ERA5_Jul.csv')
        rural_hourly = pd.read_csv(rural_path, index_col=0, parse_dates=True, skiprows=1)
    else:
        rural_path = os.path.join(processed_folder, 'Vancouver_Rural_ECCC_BC_1108447_MM-2008_P1H.csv')
        rural_hourly = pd.read_csv(rural_path, index_col=0, parse_dates=True)
    rural_hourly = rural_hourly.astype(float)
    rural_30min = rural_hourly.resample('30min').interpolate()
    rural_30min = rural_30min[compare_start_time:compare_end_time]

    comparison['Rural_DBT_C'] = rural_30min.iloc[:, 0]
    if 'TopForcing' in experiments_folder:
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


def process_one_theme(path):
    #find all csv files in the path, which does not contain 'save'
    csv_files = []
    for file in os.listdir(path):
        if file.endswith('.csv'):
            csv_files.append(file)
    cvrmse_dict = {}
    nmbe_dict = {}
    if "BUBBLE_Ue1" in experiments_folder:
        comparison = get_BUUBLE_Ue1_measurements()
        cvrmse_dict['Rural_2.6'] = cvrmse(comparison['Urban_DBT_C_2.6'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_13.9'] = cvrmse(comparison['Urban_DBT_C_13.9'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_17.5'] = cvrmse(comparison['Urban_DBT_C_17.5'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_21.5'] = cvrmse(comparison['Urban_DBT_C_21.5'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_25.5'] = cvrmse(comparison['Urban_DBT_C_25.5'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_31.2'] = cvrmse(comparison['Urban_DBT_C_31.2'], comparison['Rural_DBT_C'])
        print(f'cvrmse for Rural vs Urban is {cvrmse_dict}')
    elif "BUBBLE_Ue2" in experiments_folder:
        comparison = get_BUUBLE_Ue2_measurements()
        cvrmse_dict['Rural_3.0'] = cvrmse(comparison['Urban_DBT_C_3.0'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_15.8'] = cvrmse(comparison['Urban_DBT_C_15.8'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_22.9'] = cvrmse(comparison['Urban_DBT_C_22.9'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_27.8'] = cvrmse(comparison['Urban_DBT_C_27.8'], comparison['Rural_DBT_C'])
        cvrmse_dict['Rural_32.9'] = cvrmse(comparison['Urban_DBT_C_32.9'], comparison['Rural_DBT_C'])
        print(f'cvrmse for Rural vs Urban(3.0) is {cvrmse_dict["Rural_3.0"]}')
        print(f'cvrmse for Rural vs Urban(15.8) is {cvrmse_dict["Rural_15.8"]}')
        print(f'cvrmse for Rural vs Urban(22.9) is {cvrmse_dict["Rural_22.9"]}')
        print(f'cvrmse for Rural vs Urban(27.8) is {cvrmse_dict["Rural_27.8"]}')
        print(f'cvrmse for Rural vs Urban(32.9) is {cvrmse_dict["Rural_32.9"]}')
    else:
        if "CAPITOUL" in experiments_folder:
            comparison = get_CAPITOUL_measurements()
        else:
            comparison = get_Vancouver_measurements()
        cvrmse_dict['Rural'] = cvrmse(comparison['Urban_DBT_C'], comparison['Rural_DBT_C'])
        nmbe_dict['Rural'] = normalized_mean_bias_error(comparison['Urban_DBT_C'], comparison['Rural_DBT_C'])
        print(f'cvrmse for Rural is {cvrmse_dict["Rural"]}, nmbe for Rural is {nmbe_dict["Rural"]}')

    sql_dict = {}
    for csv_file in csv_files:
        df = pd.read_csv(path + '/' + csv_file, index_col=0, parse_dates=True)
        df = df[compare_start_time:compare_end_time]
        comparison['MeteoData.Pre'] = df['MeteoData.Pre']
        comparison['sensWaste_' + csv_file] = df['sensWaste']
        comparison['wallSun_K_' + csv_file] = df['wallSun_K']
        comparison['wallShade_K_' + csv_file] = df['wallShade_K']
        comparison['roof_K_' + csv_file] = df['roof_K']
        comparison['ForcTemp_K_' + csv_file] = df['ForcTemp_K']

        temp_prof_cols, pres_prof_cols = find_height_indice(df)
        for i in range(len(temp_prof_cols)):
            comparison[csv_file + '_'+temp_prof_cols[i]] = df[temp_prof_cols[i]]
            comparison[csv_file + '_'+pres_prof_cols[i]] = df[pres_prof_cols[i]]
            height_idx = re.search(r'(\d+\.?\d*)', temp_prof_cols[i]).group(1)
            comparison[csv_file + '_sensor_idx_' + height_idx] = (comparison[csv_file + '_'+temp_prof_cols[i]]) * \
                                                                (comparison[csv_file + '_'+pres_prof_cols[i]] / comparison['MeteoData.Pre']) \
                                                                ** 0.286 - 273.15
            if 'CAPITOUL' in experiments_folder or 'Vancouver' in experiments_folder \
                    or "Improvements" in experiments_folder:
                _tmp_col = 'Urban_DBT_C'
            else:
                _tmp_col = 'Urban_DBT_C_' + height_idx
            tempCVRMSE = cvrmse(comparison[_tmp_col],
                                           comparison[csv_file + '_sensor_idx_' + height_idx])
            cvrmse_dict[csv_file + '_sensor_idx_' + height_idx] = tempCVRMSE
            tempNMBE = normalized_mean_bias_error(comparison[_tmp_col],
                                                  comparison[csv_file + '_sensor_idx_' + height_idx])
            nmbe_dict[csv_file + '_sensor_idx_' + height_idx] = tempNMBE
            print(f'cvrmse for {csv_file} at height idx:{height_idx} is {tempCVRMSE}, NMBE is {tempNMBE}')

        sql_dict[csv_file] = read_sql(csv_file)
    if os.path.exists(f'{experiments_folder}/comparison.xlsx'):
        os.remove(f'{experiments_folder}/comparison.xlsx')
    writer = pd.ExcelWriter(f'{experiments_folder}/comparison.xlsx')
    comparison.to_excel(writer, 'comparison')
    cvrmse_df = pd.DataFrame.from_dict(cvrmse_dict, orient='index', columns=['cvrmse'])
    cvrmse_df.to_excel(writer, 'cvrmse')
    nmbe_df = pd.DataFrame.from_dict(nmbe_dict, orient='index', columns=['nmbe'])
    nmbe_df.to_excel(writer, 'nmbe')
    sql_df = pd.DataFrame.from_dict(sql_dict, orient='index', columns=['total_site_energy'])
    sql_df.to_excel(writer, 'sql')
    writer.save()

def plot_one_subfigure(fig, df, ax, category, compare_cols):
    pass
    global legend_bool
    x = pd.to_datetime(df.index)
    ax.set_title(category)
    if category == 'sensWaste':
        ax.set_ylabel('W/m2')
    else:
        ax.set_ylabel(' Temperature (C)')
    col_name_fix = category + '_'
    if legend_bool > 0:
        for col in compare_cols:
            if col == "Rural_DBT_C":
                ax.plot(x, df[col], label=col, color='orange', linestyle='--')
            elif col == "Urban_DBT_C":
                ax.plot(x, df[col], label=col, color='red', linestyle=':')
            elif col == 'Urban_DBT_C_2.6':
                ax.plot(x, df[col], label=col, color='red', linestyle=':')
            elif col == 'Urban_DBT_C_13.9':
                ax.plot(x, df[col], label=col, color='purple', linestyle='-.')
            else:
                ax.plot(x, df[col_name_fix+col +'.csv'], label=col)
        legend_bool -= 1
        if legend_bool == 0:
            fig.legend(loc='center right', bbox_to_anchor=(1, 0.5+ legend_bool * 0.2), borderaxespad=0., fontsize=plot_fontsize)
    else:
        for col in compare_cols:
            ax.plot(x, df[col_name_fix+col+'.csv'])

def plots():
    #Measurements: Rural, Urban
    #Predictions: VCWG, Bypass-Default, Bypass-Shading, Bypass-ViewFactor, Bypass-Shading_ViewFactor
    # All_subfigures: Canyon, Wallshade, Walllit, Roof, Wastez
    global plot_fontsize, legend_bool

    data = pd.read_excel(f'{experiments_folder}/comparison.xlsx', sheet_name='comparison', index_col=0, parse_dates=True)
    plot_fontsize = 8
    if "BUBBLE" in experiments_folder:
        measurements_cols = ['Rural_DBT_C', 'Urban_DBT_C_2.6', 'Urban_DBT_C_13.9']
        legend_bool = 2
    else:
        measurements_cols = ['Rural_DBT_C','Urban_DBT_C']
        legend_bool = 1

    predictions_cols = []
    for file in os.listdir(f'./{experiments_folder}'):
        if file.endswith('.csv'):
            #remove the '.csv' in the file name
            predictions_cols.append(file.replace('.csv', ''))
    if "BUBBLE" in experiments_folder:
        all_subfigures_cols = ['RealTempProf_13.9', 'RealTempProf_2.6', 'sensWaste']
        fig, axes = plt.subplots(3, 1, figsize=(12, 4), sharex=True)
    else:
        all_subfigures_cols = ['RealTempProf','sensWaste']
        fig, axes = plt.subplots(2, 1, figsize=(12, 4), sharex=True)
    fig.subplots_adjust(right=0.76)
    for ax in axes:
        ax.tick_params(axis='x', labelsize=plot_fontsize)
    for i, sub_fig in enumerate(all_subfigures_cols):
        if  'RealTempProf_13.9' in sub_fig:
            compare_cols = ['Rural_DBT_C','Urban_DBT_C_13.9'] + predictions_cols
        elif 'RealTempProf_2.6' in sub_fig:
            compare_cols = ['Rural_DBT_C','Urban_DBT_C_2.6'] + predictions_cols
        else:
            compare_cols = predictions_cols
        plot_one_subfigure(fig, data, axes[i],sub_fig, compare_cols)
    plt.show()

def main():
    global processed_folder,processed_file,\
        compare_start_time, compare_end_time, sql_report_name, sql_table_name, sql_row_name, sql_col_name
    global experiments_folder
    # experiments_folder = 'BUBBLE_debug'


    experiments_folder = 'BUBBLE_Ue1_Bypass'
    experiments_folder = 'CAPITOUL_WithoutCooling_Bypass'
    # experiments_folder = 'CAPITOUL_WithCooling_Bypass'
    # experiments_folder = 'October_CAPITOUL_WithCooling_Bypass'
    # experiments_folder = 'October_CAPITOUL_WithoutCooling_Bypass'
    # experiments_folder = 'BUBBLE_Ue2_Bypass'
    # experiments_folder = 'Vancouver_TopForcing_Bypass'
    # experiments_folder = 'Vancouver_Rural_Bypass'
    experiments_folder = "CAPITOUL_ByPass_Improvements_Investigation"
    sql_report_name = 'AnnualBuildingUtilityPerformanceSummary'
    sql_table_name = 'Site and Source Energy'
    sql_row_name = 'Total Site Energy'
    sql_col_name = 'Total Energy'
    if "BUBBLE" in experiments_folder:
        compare_start_time = '2002-06-10 00:10:00'
        compare_end_time = '2002-07-09 21:50:00'
        processed_folder =  os.path.join('_measurements','BUBBLE')
        if 'Ue1' in experiments_folder:
            processed_file = 'BUBBLE_UE1_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                                 + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'
        elif 'Ue2' in experiments_folder:
            processed_file = 'BUBBLE_UE2_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                                 + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'
    elif "CAPITOUL" in experiments_folder:
        compare_start_time = '2004-06-01 00:00:00'
        compare_end_time = '2004-06-30 23:55:00'
        processed_folder =  os.path.join('_measurements','CAPITOUL')
        processed_file = r'CAPITOUL_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                                 + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'
    else:
        compare_start_time = '2008-07-01 00:30:00'
        compare_end_time = '2008-07-31 23:00:00'
        processed_folder = os.path.join('_measurements', 'VANCOUVER')
        if 'TopForcing' in experiments_folder:
            processed_file = r'Vancouver_TopForcing_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                         + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'
        else:
            processed_file = r'Vancouver_Rural_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                         + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'

    # process_one_theme(experiments_folder)
    plots()
if __name__ == '__main__':
    main()