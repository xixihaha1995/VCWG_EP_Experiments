'''
for each subfolder (which is a theme) under: sensitivity_saving\CAPITOUL:
    do a theme based sensitivity analysis:
    specifically:
        sheet 1:
        date-time, urban, rural, meteodata.pres,
        (all other TempProf[SensorIdx] in each csv file)
        (all other RealTempProf[SensorIdx] in each csv file)
        sheet 2:
        CVRMSE for each RealTempProf[SensorIdx] in each csv file
'''
import os, csv, numpy as np, pandas as pd


def cvrmse(measurements, predictions):
    bias = predictions - measurements
    rmse = np.sqrt(np.mean(bias**2))
    cvrmse = rmse / np.mean(abs(measurements))
    return cvrmse

def get_measurements():
    if os.path.exists('measurements\\' + processed_measurements):
        return pd.read_csv('measurements\\' + processed_measurements, index_col=0, parse_dates=True)
    urban_path = r'measurements\Urban_Pomme_Ori_1_min.csv'
    rural_path = r'measurements\Rural_Ori_1_min.csv'
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

    comparison.to_csv('measurements\\' + processed_measurements)
    return comparison

def process_one_theme(theme, path):
    #find all csv files in the path, which does not contain 'save'
    csv_files = []
    for file in os.listdir(path):
        if file.endswith('.csv') and 'save' not in file:
            csv_files.append(file)
    #process each csv file
    comparison = get_measurements()
    cvrmse_dict = {}
    for csv_file in csv_files:
        df = pd.read_csv(path + '\\' + csv_file, index_col=0, parse_dates=True)
        df = df[compare_start_time:compare_end_time]
        comparison['Rural_Pres_Pa'] = df['MeteoData.Pre']
        comparison['TempProf_' + csv_file] = df['TempProf_cur[19]']
        comparison['PresProf_' + csv_file] = df['PresProf_cur[19]']
        comparison['RealTempProf_' + csv_file] = (df['TempProf_cur[19]'] - 273.15)* \
                                                 (df['PresProf_cur[19]'] / comparison['Rural_Pres_Pa']) ** 0.286
        cvrmse_dict[csv_file] = cvrmse(comparison['Urban_DBT_C'], comparison['RealTempProf_' + csv_file])
    # create new Excel file, where the first sheet is the comparison, and the second sheet is the cvrmse
    if os.path.exists('sensitivity_saving\\' + theme + '\\comparison.xlsx'):
        os.remove('sensitivity_saving\\' + theme + '\\comparison.xlsx')
    writer = pd.ExcelWriter(path + '\\' + theme + '_sensitivity_analysis.xlsx')
    if os.path.exists('sensitivity_saving\\' + theme + '\\comparison.xlsx'):
        os.remove('sensitivity_saving\\' + theme + '\\comparison.xlsx')
    comparison.to_excel(writer, 'comparison')
    # For the cvrmse, the index is the csv file name, and the column is the cvrmse
    cvrmse_df = pd.DataFrame.from_dict(cvrmse_dict, orient='index', columns=['cvrmse'])
    cvrmse_df.to_excel(writer, 'cvrmse')
    writer.save()

def process_all_themes():
    all_themes_path = r'sensitivity_saving\CAPITOUL'
    all_themes = os.listdir(all_themes_path)
    for theme in all_themes:
        process_one_theme(theme, all_themes_path + '\\' + theme)
    pass

def main():
    global processed_measurements, compare_start_time, compare_end_time
    compare_start_time = '2004-06-01 00:05:00'
    compare_end_time = '2004-06-30 22:55:00'
    processed_measurements = 'CAPITOUL_measurements_' + pd.to_datetime(compare_start_time).strftime('%Y-%m-%d') \
                             + '_to_' + pd.to_datetime(compare_end_time).strftime('%Y-%m-%d') + '.csv'
    process_all_themes()
if __name__ == '__main__':
    main()
