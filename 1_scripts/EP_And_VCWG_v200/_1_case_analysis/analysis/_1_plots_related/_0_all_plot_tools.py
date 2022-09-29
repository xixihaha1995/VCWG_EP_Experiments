#RMSE function
import numpy as np, pandas as pd, matplotlib.pyplot as plt, os
def RMSE(y_true, y_pred):
    return np.sqrt(np.mean(np.square(y_pred - y_true)))

def ep_time_to_pandas_time(df, start_time):
    '''
    for 0th column, find all the observation with 24:00:00, and change it to 00:00:00, and add one day
    0th column is date related data, however, it has rare format, so it is not easy to convert to pandas time

    extract month, day, hour, minute, second from 0th column
    0th column current format is one string, " MM/DD  HH:MM:SS"
    '''
    index_24 = df[df.iloc[:, 0].str.contains('24:00:00')].index
    # replace 24:00:00 with 00:00:00
    df.iloc[index_24, 0] = df.iloc[index_24, 0].str.replace('24:00:00', '00:00:00')
    # extract month from 0th column
    df['month'] = df.iloc[:, 0].str.extract('(\d{2})/').astype(int)
    # extract day from 0th column
    df['day'] = df.iloc[:, 0].str.extract('/(\d{2})').astype(int)
    # extract hour from 0th column
    df['hour'] = df.iloc[:, 0].str.extract('(\d{2}):').astype(int)
    # extract minute from 0th column
    df['minute'] = df.iloc[:, 0].str.extract(':(\d{2}):').astype(int)
    # extract second from 0th column, second is the last 2 index of 0th column
    df['second'] = df.iloc[:, 0].str[-2:].astype(int)
    # we dont have year, so we use the first 4 char of start_time
    df['year'] = start_time[:4]
    # convert to pandas time
    df['date'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute', 'second']])
    # add one day to index_24
    df.loc[index_24, 'date'] = df.loc[index_24, 'date'] + pd.Timedelta(days=1)
    # update dataframe index
    df.index = df['date']
    # drop 0th column, date related data
    # drop month, day, hour, minute, second, date
    df.drop(['month', 'day', 'hour', 'minute', 'second', 'date','year','Date/Time'], axis=1, inplace=True)
    #  if date is earlier than start_time, increase one year
    df.index = df.index + pd.Timedelta(days=365) * (df.index < start_time)
    return df

def clean_epw(df, start_time):
    '''
    df 0th column is year,
    df 1st column is month,
    df 2nd column is day,
    df 3rd column is hour, range from 1 to 24, make it to 0 to 23
    df 4th column is minute, always 60
    '''
    # convert hour to 0 to 23
    df.iloc[:, 3] = df.iloc[:, 3] - 1
    # convert columns year, month, day, hour, all of them is numpy.int64
    # convert to pandas time
    # combine the 4 columns to one string column, in format of 'year-month-day hour:00:00'
    df['string_combined'] = df.iloc[:, 0].astype(str) + '-' + df.iloc[:, 1].astype(str) + '-' \
                            + df.iloc[:, 2].astype(str) + ' ' + df.iloc[:, 3].astype(str) + ':00:00'
    # convert to pandas time
    df['date'] = pd.to_datetime(df['string_combined'])
    # update dataframe index
    df.index = df['date']
    df.drop(['date', 'string_combined'], axis=1, inplace=True)
    #  overwrite the index year as start_time year
    start_time_year = start_time[:4]
    df.index = df.index.strftime('%Y-%m-%d %H:%M:%S').str.replace('2012', start_time_year)
    return df
def sequence_time_to_pandas_time(dataframe, delta_t,start_time):
    date = pd.date_range(start_time, periods=len(dataframe), freq='{}S'.format(delta_t))
    date = pd.Series(date)
    # update dataframe index
    dataframe.index = date
    return dataframe
def bias_rmse_r2(df1, df2, df2_name):
    '''
    df1 is measurement data, [date, sensible/latent]
    df2 is simulated data, [date, sensible/latent]
    '''
    bias = df1 - df2
    rmse = np.sqrt(np.mean(np.square(bias)))
    cvrmse = rmse / np.mean(df1) * 100
    r2 = 1 - np.sum(np.square(bias)) / np.sum(np.square(df1 - np.mean(df1)))
    mean_bias_percent = np.mean(abs(bias)) / np.mean(df1) * 100

    # bias_mean = np.mean(bias)
    # df2 name
    # return number with 2 decimal places
    return df2_name, round(mean_bias_percent,2), round(cvrmse,2), round(r2,2)

def calculate_cvrmse(df1, df2):
    '''
    df1 is measurement data, [date, sensible/latent]
    df2 is simulated data, [date, sensible/latent]
    '''
    bias = df1 - df2
    rmse = np.sqrt(np.mean(np.square(bias)))
    cvrmse = rmse / np.mean(df1) * 100
    return round(cvrmse, 2)


def read_text_as_csv(file_path, header=None, index_col=0, skiprows=3):
    '''
    df first column is index
    '''
    df = pd.read_csv(file_path, skiprows= skiprows, header= header, index_col=index_col, sep= '[ ^]+', engine='python')
    # set index to first column
    # df.set_index(df.iloc[:,0], inplace=True)
    return df

def clean_bubble_iop(df, start_time='2018-01-01 00:00:00', end_time='2018-12-31 23:59:59',
                     to_hourly = True):
    # current index format is DD.MM.YYYY
    df.index = pd.to_datetime(df.index, format='%d.%m.%Y')
    # index format is YYYY-MM-DD HH:MM:SS
    # replace HH:MM with first 5 char of 0th column, convert to datetime
    df.index = pd.to_datetime(df.index.strftime('%Y-%m-%d') + ' ' + df.iloc[:,0].str[:5])
    # drop the 0th column, according to the index instead of column name
    df.drop(df.columns[0], axis=1, inplace=True)
    # except the last column, all columns are number with comma, convert them to number
    df.iloc[:, :-1] = df.iloc[:, :-1].apply(lambda x: x.str.replace(',', '')).astype(float)
    df = df[start_time:end_time]
    # convert 10 min interval to 1 hour interval
    if to_hourly:
        df = time_interval_convertion(df, original_time_interval_min=10, start_time=start_time)
    return df


def multiple_days_hour_data_to_one_day_hour_data(df):
    '''
    columns are 48 hours based sequence data,
    average them into one day 24 hours data
    '''
    # new df with 24 hours data
    columns = np.arange(24)
    df_new = pd.DataFrame(columns=columns)
    # average 48 hours data into 24 hours data
    for i in range(0,24):
        df_new[i] = df.iloc[:,i::24].mean(axis=1)
    return df_new

def certain_height_one_day(df, height):
    '''
    df index is different heights, resolution is 0.5 m
    '''
    # find the closest height
    height_index = np.argmin(np.abs(df.index - height))
    return df.iloc[height_index,:]

def average_temperature_below_height(df, height):
    '''
    df index is different heights, resolution is 0.5 m
    '''
    # find the closest height
    height_index = np.argmin(np.abs(df.index - height))
    return df.iloc[:height_index,:].mean(axis=0)

def filter_df_with_new_heights(df, heights_arr):
    # new df with heights as index
    df_new = pd.DataFrame(index=heights_arr, columns=df.columns)
    for heigh in heights_arr:
        df_new.loc[heigh] = certain_height_one_day(df, heigh)
    return df_new

def plot_24_hours_comparison_for_multiple_heights(df1, df2, height, all_rmse,case_name):
    '''
    In total, there are len(height) figures
    df index is
    '''
    fig, ax = plt.subplots(figsize=(10,5), nrows = 2, ncols = len(height) // 2, sharex=True, sharey=True)
    for i in range(len(height)):
        ax[i%2,i//2].plot(df1.columns, df1.iloc[i], label='VCWG')
        ax[i%2,i//2].plot(df2.columns,df2.iloc[i], label='Bypass')
        ax[i%2,i//2].legend()
        ax[i%2,i//2].set_title(f'Height:{height[i]}m, RMSE:{RMSE(df1.iloc[i],df2.iloc[i]):.2f}')
        # set y limit
        ax[i%2,i//2].set_ylim(270,320)

    # set x name, y name, and title
    ax[1,0].set_xlabel('Hours')
    ax[0,0].set_ylabel('Temperature (K)')
    fig.suptitle(
        f'RMSE(VCWGv2.0.0 - {case_name}):{np.mean(all_rmse):.2f}')
    plt.show()

def data_cleaning(df):
    '''
    string to number
    Nan to 0
    '''
    df = df.apply(pd.to_numeric, errors='coerce')
    df = df.fillna(0)
    return df

def time_interval_convertion(df, original_time_interval_min = 30, need_date = False,
                             start_time = '2018-01-01 00:00:00'):
    '''
    Original data is 30 mins interval,
    Convert it to hourly data
    Original data has [index, sensible]
    Replace sensible with hourly average
    '''
    original_time_num = 60 // original_time_interval_min
    df_new = pd.DataFrame(columns=df.columns)
    for i in range(0, len(df), original_time_num):
        df_new.loc[df.index[i]] = df.iloc[i:i+original_time_num:,].mean()
        # df_new.iloc[i,0] = df.iloc[i:i+2,0].mean()
    # floor index (YYYY-MM-DD HH:MM:SS) to (YYYY-MM-DD HH:00:00)
    if not need_date:
        df_new.index = df_new.index.floor('H')
    else:
        df_new = add_date_index(df_new, start_time, 3600)
    return df_new

def _5min_to_10min(df):
    '''
    Original data is 5 mins interval,
    Convert it to 10 mins interval
    Original data has [index, sensible]
    Replace sensible with 10 mins average
    '''
    df_new = pd.DataFrame(columns=df.columns)
    for i in range(0, len(df), 2):
        df_new.loc[df.index[i]] = df.iloc[i:i+2,].mean()
    # floor index (YYYY-MM-DD HH:MM:SS) to (YYYY-MM-DD HH:MM:00)
    return df_new

# plot the comparisons between Vancouver Sunset dataset versus simulated (VCWGv2.0.0, VCWG-Bypass)
def plot_comparison_measurement_simulated(df, txt_info):

    figure, ax = plt.subplots(figsize=(10,5))

    ax.plot(df.iloc[:,0], label='Measurement')
    ax.plot(df.iloc[:,1], label= df.columns[1])
    ax.plot(df.iloc[:,2], label= df.columns[2])
    ax.plot(df.iloc[:,3], label= df.columns[3])
    ax.plot(df.iloc[:,4], label= df.columns[4])
    ax.legend()
    # add  to the plot
    # add text below the plot, outside the plot
    # txt = f'Bias Mean(W m-2), RMSE(W m-2), R2(-)\n' \
    #       f'{df.columns[1]}:{txt_info[1]}\n' \
    #       f'{df.columns[2]}:{txt_info[2]}'
    # print(txt)
    # ax.text(0.5, 1, txt, transform=ax.transAxes, fontsize=6,
    #     verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.set_title(txt_info[0][0])
    # set x name, y name, and title
    ax.set_xlabel(txt_info[0][1])
    ax.set_ylabel(txt_info[0][2])

    plt.show()

def general_time_series_comparision(df, txt_info):
    # df has many columns, itearte to plot each column
    figure, ax = plt.subplots(figsize=(10, 5))
    for i in range(0, len(df.columns)):
        if 'Urban' in df.columns[i]:
            ax.plot(df.iloc[:,i], label= df.columns[i], color='black', linestyle='--')
        elif 'Rural' in df.columns[i]:
            ax.plot(df.iloc[:,i], label= df.columns[i], color='black', linestyle=':')
        else:
            ax.plot(df.iloc[:,i], label= df.columns[i])
    # make legend located at the best position
    ax.legend(loc='best')
    # from 1 iteraterat through all columns, make a txt for error info

    txt = 'Maximum Daily UHI effect: 5.2 K'
    txt +='\nVCWGv2.0.0 (Monthly) MeanBiasError: -0.53(K), RMSE: 0.56(K), R2: 0.98(-)'
    txt +='\nUWG Monthly MBE: -0.6(K), RMSE: 0.9(K)'
    txt += f'\nNMBE(%), CV-RMSE(%), R2(-)'

    for i in range(1, len(txt_info)):
        txt += f'\n{txt_info[i]}'
    print(txt)
    ax.text(0.05, 1, txt, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    # lim
    ax.set_ylim(10, 40)
    ax.set_title(txt_info[0][0])
    # set x name, y name, and title
    ax.set_xlabel(txt_info[0][1])
    ax.set_ylabel(txt_info[0][2])
    plt.show()

def add_date_index(df, start_date, time_interval_sec):
    '''
    df is [date, sensible/latent]
    '''
    date = pd.date_range(start_date, periods=len(df), freq='{}S'.format(time_interval_sec))
    date = pd.Series(date)
    # update dataframe index
    df.index = date
    return df

def merge_multiple_df(df_list, column_name):
    '''
    df_list is a list of dataframes
    '''
    df = pd.concat(df_list, axis=1)
    df.columns = column_name
    return df

def save_data_to_csv(saving_data, file_name,case_name, start_time, time_interval_sec, vcwg_ep_saving_path):
    data_arr = np.array(saving_data[file_name])
    df = pd.DataFrame(data_arr)
    if file_name == 'can_Averaged_temp_k_specHum_ratio_press_pa':
        df.columns = ['Temp_K', 'SpecHum_Ratio', 'Press_Pa']
    else:
        df.columns = [f'(m) {file_name}_' + str(0.5 + i) for i in range(len(df.columns))]
    df = add_date_index(df, start_time, time_interval_sec)
    # save to excel, if non-exist, create one
    if not os.path.exists(vcwg_ep_saving_path):
        os.makedirs(vcwg_ep_saving_path)
    df.to_excel(os.path.join(vcwg_ep_saving_path, f'{case_name}_{file_name}.xlsx'))

def excel_to_potential_real_df(filename, results_folder, p0, heights_profile, ue1_heights,compare_start_time,
                               compare_end_time):
    th_profie_5min = pd.read_excel(f'{results_folder}\\{filename}_TempProfile_K.xlsx',
                                                   sheet_name='Sheet1', header=0, index_col=0)
    # ue1_heights is sensor heights, heights_profile is the heights of predictions
    # find the mapped indices in heights_profile
    heights_profile = np.array(heights_profile)
    ue1_heights = np.array(ue1_heights)
    mapped_indices = [np.argmin(np.abs(heights_profile - i)) for i in ue1_heights]
    # sensor_idx = np.argmin(np.abs(np.array(heights_profile) - v200_sensor_height))
    th_sensor_5min = th_profie_5min.iloc[:, mapped_indices]
    th_sensor_5min_K_compare = th_sensor_5min[compare_start_time:compare_end_time]
    th_sensor_5min_K_compare_df = pd.DataFrame(th_sensor_5min_K_compare)
    th_sensor_10min_K_compare = _5min_to_10min(th_sensor_5min_K_compare_df)

    pres_profile_5min = pd.read_excel(f'{results_folder}\\{filename}_PressProfile_Pa.xlsx',
                                                      sheet_name='Sheet1', header=0, index_col=0)
    pres_sensor_5min = pres_profile_5min.iloc[:, mapped_indices]
    pres_sensor_5min_pa_compare = pres_sensor_5min[compare_start_time:compare_end_time]
    pres_sensor_5min_pa_compare_df = pd.DataFrame(pres_sensor_5min_pa_compare)
    pres_sensor_10min_pa_compare = _5min_to_10min(
        pres_sensor_5min_pa_compare_df)
    # real temperature  = th_sensor_10min_c_compare * (pres_sensor_10min_pa_compare/p0)^0.286
    # both pres_sensor_10min_pa_compare and th_sensor_10min_c_compare have 6 columns
    # get real_sensor_10min_c_compare (element wise calculation)
    real_sensor_10min_K_compare_arr = th_sensor_10min_K_compare.values * \
                                      (pres_sensor_10min_pa_compare.values / p0) ** 0.286
    real_sensor_10min_K_compare = pd.DataFrame(real_sensor_10min_K_compare_arr,
                                                  index=th_sensor_10min_K_compare.index,
                                                    columns=th_sensor_10min_K_compare.columns)
    th_sensor_10min_c_compare = th_sensor_10min_K_compare - 273.15
    real_sensor_10min_c_compare = real_sensor_10min_K_compare - 273.15
    return th_sensor_10min_c_compare, real_sensor_10min_c_compare

def stacked_comparison_plot(merged_df, sensor_heights):
    # merged_df has 5 *  len(sensor_heights) + 1 columns
    # sensor_heights is a list of sensor heights
    # the first column is rural measurement
    # following the first len(sensor_heights) columns are urban measurements
    # following the second len(sensor_heights) columns are original predictions
    # following the third len(sensor_heights) columns are ver0 predictions
    # following the fourth len(sensor_heights) columns are ver1 predictions
    # following the fifth len(sensor_heights) columns are ver2 predictions

    # In total, there will be len(sensor_heights) plots
    # each plot has 5 lines
    # the first line is the measurements data, with linestyle='--'

    fig, ax = plt.subplots(len(sensor_heights), 1, figsize=(10, 10))
    for i in range(len(sensor_heights)):
        ax[i].plot(merged_df.iloc[:, 0], linestyle='-.', label='Rural Measurement')
        ax[i].plot(merged_df.iloc[:, 1+i], linestyle='--', label='Urban Measurement')
        ax[i].plot(merged_df.iloc[:, 1+len(sensor_heights)+i], label='Original Prediction')
        ax[i].plot(merged_df.iloc[:, 1+2*len(sensor_heights)+i], label='Ver0 Prediction')
        ax[i].plot(merged_df.iloc[:, 1+3*len(sensor_heights)+i], label='Ver1 Prediction')
        ax[i].plot(merged_df.iloc[:, 1+4*len(sensor_heights)+i], label='Ver2 Prediction')
        ax[i].set_ylabel(f'Height {sensor_heights[i]} m')
        ax[i].legend()
    ax[-1].set_xlabel('Time')
    # set the overall title
    fig.suptitle('Comparison of Potential Temperature Profiles')
    plt.show()