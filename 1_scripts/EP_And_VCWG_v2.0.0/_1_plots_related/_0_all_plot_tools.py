#RMSE function
import numpy as np, pandas as pd, matplotlib.pyplot as plt
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
    df.drop(df.columns[0], axis=1, inplace=True)
    # drop month, day, hour, minute, second, date
    df.drop(['month', 'day', 'hour', 'minute', 'second', 'date'], axis=1, inplace=True)
    #  if date is earlier than start_time, increase one year
    df.index = df.index + pd.Timedelta(days=365) * (df.index < start_time)
    return df
def sequence_time_to_pandas_time(dataframe, delta_t,start_time):
    date = pd.date_range(start_time, periods=len(dataframe), freq='{}S'.format(delta_t))
    date = pd.Series(date)
    # update dataframe index
    dataframe.index = date
    return dataframe
def bias_rmse_r2(df1, df2):
    '''
    df1 is measurement data, [date, sensible/latent]
    df2 is simulated data, [date, sensible/latent]
    '''
    bias = df1 - df2
    rmse = np.sqrt(np.mean(np.square(bias)))
    r2 = 1 - np.sum(np.square(bias)) / np.sum(np.square(df1 - np.mean(df1)))
    bias_mean = np.mean(abs(bias))
    # return number with 2 decimal places
    return round(bias_mean,2), round(rmse,2), round(r2,2)

def read_text_as_csv(file_path, header=None, index_col=0, skiprows=3):
    '''
    df first column is index
    '''
    df = pd.read_csv(file_path, skiprows= skiprows, header= header, index_col=index_col, sep= '[ ^]+', engine='python')
    # set index to first column
    # df.set_index(df.iloc[:,0], inplace=True)
    return df

def clean_bubble_iop(df):
    # current index format is DD.MM.YYYY
    df.index = pd.to_datetime(df.index, format='%d.%m.%Y')
    # index format is YYYY-MM-DD HH:MM:SS
    # replace HH:MM with first 5 char of 0th column, convert to datetime
    df.index = pd.to_datetime(df.index.strftime('%Y-%m-%d') + ' ' + df.iloc[:,0].str[:5])
    # drop the 0th column, according to the index instead of column name
    df.drop(df.columns[0], axis=1, inplace=True)
    # 0 to 5 column is number with comma, convert them to number
    df.iloc[:, 0:5] = df.iloc[:, 0:5].apply(lambda x: x.str.replace(',', '')).astype(float)
    # convert 10 min interval to 1 hour interval
    df = time_interval_convertion(df, original_time_interval_min=10)
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

def time_interval_convertion(df, original_time_interval_min = 30 ):
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
    df_new.index = df_new.index.floor('H')
    return df_new

# plot the comparisons between Vancouver Sunset dataset versus simulated (VCWGv2.0.0, VCWG-Bypass)
def plot_comparison_measurement_simulated(df, txt_info):

    figure, ax = plt.subplots(figsize=(10,5))

    ax.plot(df.iloc[:,0], label='Measurement')
    # ax.plot(df.iloc[:,1], label= df.columns[1])
    # ax.plot(df.iloc[:,2], label= df.columns[2])
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

def add_date_index(df, start_date, time_interval):
    '''
    df is [date, sensible/latent]
    '''
    date = pd.date_range(start_date, periods=len(df), freq='{}S'.format(time_interval))
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
