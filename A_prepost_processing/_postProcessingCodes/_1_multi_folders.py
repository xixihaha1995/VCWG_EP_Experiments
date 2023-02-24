
import os, csv, numpy as np, pandas as pd, re
import pathlib
import sqlite3


def cvrmse(measurements, predictions):
    bias = predictions - measurements
    rmse = np.sqrt(np.mean(bias**2))
    cvrmse = rmse / np.mean(abs(measurements))
    return cvrmse

def get_measurements():
    if os.path.exists('_measurements\\' + processed_measurements):
        return pd.read_csv('_measurements\\' + processed_measurements, index_col=0, parse_dates=True)
    urban_path = r'_measurements\Urban_Pomme_Ori_1_min.csv'
    rural_path = r'_measurements\Rural_Ori_1_min.csv'
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

    comparison.to_csv('_measurements\\' + processed_measurements)
    return comparison

def read_sql(theme,csv_file, report_name, table_name, row_name, col_name, offline_bool):
    if not offline_bool:
        if "heta_canyon" in theme:
            ep_folder_name = theme + 'theta_canyon' + re.search(r'(.*)\.csv', csv_file).group(1)
        else:
            ep_folder_name = theme + re.search(r'(.*)\.csv', csv_file).group(1)
        sql_path = os.path.join('..\\resources\\idf', ep_folder_name+'ep_outputs', 'eplusout.sql')
    else:
        csv_name = re.search(r'(.*)\.csv', csv_file).group(1)
        current_path = os.path.join('.\\offline_saving\\CAPITOUL', theme)
        # from all the folders in the current path, find the one that contains the csv file
        for folder in os.listdir(current_path):
            if csv_name in folder and 'ep_outputs' in folder:
                sql_path = os.path.join(current_path, folder, 'eplusout.sql')
                break
    if not os.path.exists(sql_path):
        return None
    abs_sql_path = os.path.abspath(sql_path)
    sql_uri = '{}?mode=ro'.format(pathlib.Path(abs_sql_path).as_uri())
    query = f"SELECT * FROM TabularDataWithStrings WHERE ReportName = '{report_name}' AND TableName = '{table_name}'" \
            f" AND RowName = '{row_name}' AND ColumnName = '{col_name}'"
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
def process_one_theme(theme, path, offline_bool = False):
    #find all csv files in the path, which does not contain 'save'
    csv_files = []
    for file in os.listdir(path):
        if file.endswith('.csv') and 'save' not in file:
            csv_files.append(file)
    #process each csv file
    comparison = get_measurements()
    cvrmse_dict = {}
    sql_dict = {}
    for csv_file in csv_files:
        df = pd.read_csv(path + '\\' + csv_file, index_col=0, parse_dates=True)
        df = df[compare_start_time:compare_end_time]
        comparison['MeteoData.Pre'] = df['MeteoData.Pre']
        comparison['TempProf_' + csv_file] = df['TempProf_cur[19]']
        comparison['PresProf_' + csv_file] = df['PresProf_cur[19]']
        comparison['MeteoData.Pre_RealTempProf_' + csv_file] = (df['TempProf_cur[19]'])* \
                                                 (df['PresProf_cur[19]'] / comparison['MeteoData.Pre']) ** 0.286 - 273.15
        comparison['Rural_Pres_Pa_RealTempProf_' + csv_file] = (df['TempProf_cur[19]'])* \
                                                    (df['PresProf_cur[19]'] / comparison['Rural_Pres_Pa']) ** 0.286 - 273.15
        # from string csv_file extract float number based on regex
        if theme == "cooling":
            if "NoCooling" in csv_file:
                key_name = "Without"
            else:
                key_name = "With"
        else:
            regex = r'(\d+\.?\d*)'
            number = float(re.findall(regex, csv_file)[0])
            if "positive" in csv_file:
                number = "+" + str(number)
            if "negative" in csv_file:
                number = "-" + str(number)
            if "theta" in csv_file:
                if number == 0:
                    key_name = "Ori_0"
                else: key_name = str(number)
            elif "NoIDF" in theme:
                key_name = str(number) + "(NI)"
            else:
                key_name = str(number)
        cvrmse_dict['MeteoData.Pre_'+key_name] = cvrmse(comparison['Urban_DBT_C'], comparison['MeteoData.Pre_RealTempProf_' + csv_file])
        cvrmse_dict['Rural_Pres_Pa_'+key_name] = cvrmse(comparison['Urban_DBT_C'], comparison['Rural_Pres_Pa_RealTempProf_' + csv_file])

        sql_dict[key_name] = read_sql(theme,csv_file, sql_report_name, sql_table_name, sql_row_name, sql_col_name, offline_bool)
    # create new Excel file, where the first sheet is the comparison, and the second sheet is the cvrmse
    # third sheet is sql data
    if not offline_bool:
        if os.path.exists('sensitivity_saving\\' + theme + '\\comparison.xlsx'):
            os.remove('sensitivity_saving\\' + theme + '\\comparison.xlsx')
        writer = pd.ExcelWriter(path + '\\' + theme + '_sensitivity_analysis.xlsx')
        if os.path.exists('sensitivity_saving\\' + theme + '\\comparison.xlsx'):
            os.remove('sensitivity_saving\\' + theme + '\\comparison.xlsx')
    else:
        if os.path.exists('offline_saving\\' + theme + '\\comparison.xlsx'):
            os.remove('offline_saving\\' + theme + '\\comparison.xlsx')
        writer = pd.ExcelWriter(path + '\\' + theme + '_sensitivity_analysis.xlsx')
        if os.path.exists('offline_saving\\' + theme + '\\comparison.xlsx'):
            os.remove('offline_saving\\' + theme + '\\comparison.xlsx')

    comparison.to_excel(writer, 'comparison')
    # For the cvrmse, the index is the csv file name, and the column is the cvrmse
    cvrmse_df = pd.DataFrame.from_dict(cvrmse_dict, orient='index', columns=['cvrmse'])
    cvrmse_df.to_excel(writer, 'cvrmse')
    sql_df = pd.DataFrame.from_dict(sql_dict, orient='index', columns=['total_site_energy'])
    sql_df.to_excel(writer, 'sql')
    writer.save()

def process_all_themes():
    online_themes_path = r'sensitivity_saving\CAPITOUL'
    online_themes = os.listdir(online_themes_path)
    for online_theme in online_themes:
        process_one_theme(online_theme, online_themes_path + '\\' + online_theme)

    offline_themes_path = r'offline_saving\CAPITOUL'
    offline_themes = os.listdir(offline_themes_path)
    for offline_theme in offline_themes:
        process_one_theme(offline_theme, offline_themes_path + '\\' + offline_theme, offline_bool = True)

def main():
    global processed_measurements, compare_start_time, compare_end_time, sql_report_name, sql_table_name, sql_row_name, sql_col_name
    sql_report_name = 'AnnualBuildingUtilityPerformanceSummary'
    sql_table_name = 'Site and Source Energy'
    sql_row_name = 'Total Site Energy'
    sql_col_name = 'Total Energy'
    compare_start_time = '2004-06-01 00:05:00'
    compare_end_time = '2004-06-30 22:55:00'
    processed_measurements = 'CAPITOUL_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                             + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'
    process_all_themes()
if __name__ == '__main__':
    main()
