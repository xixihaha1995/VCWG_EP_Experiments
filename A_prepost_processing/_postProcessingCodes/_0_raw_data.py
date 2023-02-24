
import numpy as np
import pandas as pd, os, matplotlib.pyplot as plt



def pomme_columns_name():
    '''
    date, format JJ/MM/AAAA
    time, format HHMMSS.SSS
    air pressure: hPa; sensor: Vaisala PTB200.
    air temperature: Celsius; sensor MP233 VAISALA.
    relative humidity: %; sensor HMP233 VAISALA.
    Incoming short wave radiation: watts/m2; CM3 sensor of Kipp & Zonen CNR1.
    Outgoing short wave radiation: watts/m2; CM3 sensor of Kipp & Zonen CNR1.
    Incoming long wave-Red radiation: watts/m2; CG1 sensor of Kipp & Zonen CNR1.
    Outgoing long wave radiation: watts/m2; CG1 sensor of Kipp & Zonen CNR1.
    rain rate: mm/h; sensor: Optical Rain Gauge
    rate rate: mm/h; sensor: tipping bucket rain gauge
    wind direction: degree; sensor: GILL sonic anemoter, top of tower
    wind speed: m/s; sensor: GILL sonic anemoter, top of tower
    wind direction: degree; sensor: GILL sonic anemoter, intermediate level
    wind speed: m/s; sensor: GILL sonic anemoter, intermediate level
    CO2 concentration: g/m3; sensor: LICOR 7500
    Tower position
    = full extension                (height above ground: 48.05 m)
    = intermediate extension  (height above ground: 38.98 m)
    = intermediate extension  (height above ground: 38.23 m)
    = down                             (height above ground: 26.93 m)
    '''
    column_names = ['Date', 'Time', 'Air_Pressure_hPa', 'Air_Temperature_C', 'Relative_Humidity_%',
                    'Incoming_Short_Wave_Radiation_watts/m2', 'Outgoing_Short_Wave_Radiation_watts/m2',
                    'Incoming_Long_Wave-Red_Radiation_watts/m2', 'Outgoing_Long_Wave_Radiation_watts/m2',
                    'Rain_Rate_mm/h', 'Rate_Rate_mm/h', 'Wind_Direction_degree',
                    'Wind_Speed_m/s', 'Wind_Direction_degree', 'Wind_Speed_m/s', 'CO2_Concentration_g/m3', 'Tower_Position']
    return column_names
def pomme_read_one_file(file_path):
    # 3. read the rest lines, which are the data
    # separators is tab, read the first two columns as string, the rest columns as float
    data = pd.read_csv(file_path, sep='\s+', header=None, index_col= False, dtype ={0:str, 1:str})
    # drop the 3rd column, since it is always 9999
    # data.drop([2], axis=1, inplace=True)
    # DD/MM/YYYY; HHMMSS.SSS
    # 4. convert the date and time to datetime format
    data['Date'] = pd.to_datetime(data.iloc[:, 0] + data.iloc[:, 1], format='%d/%m/%Y%H%M%S.%f')
    # print all columns data types
    # print(data.dtypes)
    data.index = data['Date']
    data.drop(['Date'], axis=1, inplace=True)
    repeated_index = data.index[data.index.duplicated()]
    # drop the repeated index
    data = data.drop(repeated_index)
    target_idx = pd.date_range(start=data.index[0], end=data.index[-1], freq='1min')
    missing_index = target_idx.difference(data.index)
    if len(repeated_index) != 0 or len(missing_index) != 0:
        print('Repeated index:', repeated_index)
        print('Missing index:', missing_index)
        print('File path:', file_path)
        print('---------------------------------------------------')
    # 3. add the missed empty rows, dtype is float
    data = data.reindex(target_idx)
    #except the 2nd column, replace 9999 with NaN
    data.iloc[:, 3:] = data.iloc[:, 3:].replace(9999, np.nan)
    # interpolate the missing values
    data = data.interpolate(method='linear')
    return data

def pomme_read_all_files():
    # '_4_measurements/CAPITOUL/CAPITOUL_including_City(Tower)'
    measure_pomme_folder = '_measurements\\CAPITOUL_including_City(Tower)'
    df = pd.DataFrame()
    file_name_str = 'TaYYYYMM_MAT_%60.asc' # where MM stands for the month
    #There are 11+2 files, from 200402 to 200502
    file_yyyymm = ['200402', '200403', '200404', '200405', '200406', '200407', '200408',
                   '200409', '200410', '200411', '200412', '200501', '200502']
    for yyyymm in file_yyyymm:
        file_name = file_name_str.replace('YYYYMM', yyyymm)
        file_name = os.path.join(measure_pomme_folder, file_name)
        df_month = pomme_read_one_file(file_name)
        df = pd.concat([df, df_month])
    column_names = pomme_columns_name()
    # drop the 3rd column name
    # column_names.pop(2)
    df.columns =column_names
    return df

def rural_make_columns_name(_first_month_name):
    # make the column names
    # # 1.2. The 10th line is the column names, in total 14 columns
    # # 1.3. The 11th line is the unit of each column, in total 14 columns
    # combine the 10th and 11th lines as the column names
    with open(_first_month_name, 'r') as f:
        lines = f.readlines()
        # For each column name, its surrounded by two single quotes, 'column_name'; between two column names, there is a space.
        # for string between two single quotes, extract them as column names
        _10th_line = lines[9].strip().split(' ')
        # remove string only containing single quote
        _10th_line = [i for i in _10th_line if i != "'"]
        _11th_line = lines[10].strip().split("' '")
        column_name = []
        for i in range(len(_10th_line)):
            column_name.append(_10th_line[i] + '_' + _11th_line[i])
    return column_name

def rural_get_one_file_data(file_path):
    # read one file, read the second column as string
    df = pd.read_csv(file_path, skiprows=15, header=None, sep='\t', dtype={1: str})
    #
    # convert the date and time to datetime format
    '''
    1. first column is data, format DD/MM/AAAA
    2. second column is time, format HHMNSS.SSS, fill the missing 0
    '''
    # Fix the timestamp first
    df[0] = df[0].apply(lambda x: x.replace('/', '-'))
    df[1] = df[1].apply(lambda x: x.zfill(8))
    df['date_time'] = df.iloc[:, 0] + ' ' + df.iloc[:, 1]
    df['date_time'] = pd.to_datetime(df['date_time'], format='%d-%m-%Y %H%M%S.%f')
    # set the date_time as index
    df = df.set_index('date_time')

    repeated_index = df.index[df.index.duplicated()]
    # drop the repeated index
    df = df.drop(repeated_index)

    target_idx = pd.date_range(start=df.index[0], end=df.index[-1], freq='1min')
    missing_index = target_idx.difference(df.index)
    if len(repeated_index) != 0 or len(missing_index) != 0:
        print('Repeated index:', repeated_index)
        print('Missing index:', missing_index)
        print('File path:', file_path)
        print('---------------------------------------------------')
    # 3. add the missed empty rows, dtype is float
    df = df.reindex(target_idx)

    #get one subset df by dropping the last two columns
    df = df.iloc[:, :-2]
    # find the index (row, col) of element is 9999
    # index = df[df == 9999].stack().index.tolist()
    # [(6523, 10), (7873, 10), (7874, 10), (7878, 10), (13664, 10), (23771, 10), (23772, 10), (26583, 10), (26646, 10),
    #  (26687, 10), (26688, 10), (26703, 10), (26709, 10)]
    # iterate the index, fill it with nan
    # for i in index:
    #     df.iloc[i[0], i[1]] = np.nan
    df[2] = df[2].apply(lambda x: np.nan if x > 69 or x < -69 else x)
    df[3] = df[3].apply(lambda x: np.nan if x > 1200 or x < 310 else x)
    df[4] = df[4].apply(lambda x: np.nan if x > 109 or x < 0 else x)
    df = df.replace(9999, pd.np.nan)
    # interpolate the nan with linear method
    df = df.interpolate(method='linear')
    return df

def get_all_rural_files_data():
    # get the file path
    file_path = r'_measurements\CAPITOUL_including_Rural(Mondouzil)\Mo_BDD\Mo_BDD'
    # get the data from all the files
    df = pd.DataFrame()
    file_name_str = 'Mo_BDD_MM-2004.asc' # where MM stands for the month
    for month in range(1, 13):
        file_name = file_name_str.replace('MM', str(month).zfill(2))
        file_name = os.path.join(file_path, file_name)
        df_month = rural_get_one_file_data(file_name)
        df = pd.concat([df, df_month])
    #get 01 month file name by file_name_str.replace('MM', '01')
    _first_month_name = file_name_str.replace('MM', '01')
    column_name = rural_make_columns_name(os.path.join(file_path, _first_month_name))
    # change the column name
    df.columns = column_name[:-2]
    return df


def main():
    # df_zone7 = zone7_read_all_files()
    # df_zone7.to_csv('..\\_4_measurements\\CAPITOUL\\Mini_Zone7_Ori_12_min.csv')
    # df_pomme = pomme_read_all_files()
    # df_pomme.to_csv('_measurements\\Urban_Pomme_Ori_1_min.csv')

    df_rural = get_all_rural_files_data()
    df_rural.to_csv('_measurements\\Rural_Ori_1_min.csv')
    df_rural.iloc[:, 2:] = df_rural.iloc[:, 2:].astype(float)
    df_rural_hourly = df_rural.resample('H').mean()
    df_rural_hourly.to_csv('_measurements\\Rural_Ori_1_hour.csv')
if __name__ == '__main__':
    main()