import os, pandas as pd
import matplotlib.pyplot as plt
def find_the_cvrmse_row_number(df, variable):
    # iterate through df.iloc[:, 0], find the row number of df_cvrmse that contains the value of df.iloc[i, 0]
    # return the row number
    meteo_row_number = 0
    rural_row_number = 0
    for i in range(len(df.iloc[:, 0])):
        if str(variable) in df.iloc[i, 0] and 'MeteoData' in df.iloc[i, 0]:
            meteo_row_number = i
        if str(variable) in df.iloc[i, 0] and 'Rural_Pres' in df.iloc[i, 0]:
            rural_row_number = i
    return meteo_row_number, rural_row_number

def process_one_file(file_path, theme, framework):
    global data_all
    # for each candidate variable, get one tuple (MeteoData_CVRMSE, Rural_Pres_CVRMSE, TotalSiteEnergy)
    df_sql = pd.read_excel(file_path, sheet_name='sql')
    df_cvrmse = pd.read_excel(file_path, sheet_name='cvrmse')
    data_all[framework][theme] = {}
    for i in range(len(df_sql)):
        # format the value to 4 decimal places
        # create one new
        cur_sql_value = df_sql.iloc[i, 1]
        meteo_num, rural_num = find_the_cvrmse_row_number(df_cvrmse, df_sql.iloc[i, 0])
        cur_meteo_value = round(df_cvrmse.iloc[meteo_num, 1] * 100, 3)
        cur_rural_value = round(df_cvrmse.iloc[rural_num, 1] * 100, 3)
        data_all[framework][theme][str( df_sql.iloc[i, 0])] = [cur_meteo_value, cur_rural_value,cur_sql_value]
def process_one_theme(theme, theme_path, framework):
    global data_all
    '''
    data_all, first level is theme, second level is variable, third level is value
    '''

    files = os.listdir(theme_path)
    # open xlsx file, with '_sensitivity_analysis.xlsx' in the name
    for file in files:
        if '_sensitivity_analysis.xlsx' in file:
            file_path = theme_path + '\\' + file
            process_one_file(file_path, theme, framework)
def process_all_themes():
    global data_all
    data_all = {}
    data_all['online'] = {}
    # first layer keys: framework (online-bypass, offline-bypass)
    # second layer keys: theme (albedo, noCoolingAlbedo, etc.)
    # third layer: variable (MeteoData_CVRMSE, Rural_Pres_CVRMSE, TotalSiteEnergy)
    online_themes_path = r'sensitivity_saving\CAPITOUL'
    online_themes = os.listdir(online_themes_path)
    for theme in online_themes:
        process_one_theme(theme, online_themes_path + '\\' + theme, 'online')

    data_all['offline'] = {}
    offline_themes_path = r'offline_saving\CAPITOUL'
    offline_themes = os.listdir(offline_themes_path)
    for theme in offline_themes:
        process_one_theme(theme, offline_themes_path + '\\' + theme, 'offline')
    return data_all

def save_all_data(data_all):
    #save into excel, where rows are the second layer keys + third layer keys
    # columns are online_meteo_cvrmse, online_rural_cvrmse, online_total_site_energy,
    # offline_meteo_cvrmse, offline_rural_cvrmse, offline_total_site_energy
    df = pd.DataFrame()
    for framework, data in data_all.items():
        for theme, data in data.items():
            for variable, data in data.items():
                df.loc[f'{theme}, {variable}', f'{framework},meteo,cvrmse'] = data[0]
                df.loc[f'{theme}, {variable}', f'{framework},rural,cvrmse'] = data[1]
                df.loc[f'{theme}, {variable}', f'{framework},total_site_energy'] = data[2]
    df.to_excel(r'all_data.xlsx')

def split_data(data_all):
    data_all_1 = {}
    data_all_2 = {}
    for key in data_all.keys():
        if 'NoCooling' in key:
            data_all_1[key] = data_all[key]
        else:
            data_all_2[key] = data_all[key]
    return data_all_1, data_all_2

def plot_one_dict(data_all, title, save_path):
    fix, ax = plt.subplots(figsize=(10, 6))
    x, y = [], []
    for theme, data in data_all.items():
        # make all key to string
        x = list(data.keys())
        x = [str(i) for i in x]
        # The value is fraction, so multiply 100
        y = list(data.values())
        max_variation = max(y) - min(y)
        # group the sensitivity variable values by the sensitivity theme, where second layer keys are on top of each bar
        # this group share the same x-axis, theme
        # denote the y value on top of each bar
        for i, v in enumerate(y):
            ax.text(x[i], v + 0.1, str(v), ha='center', fontsize=8)
        ax.bar(x, y, label=theme + ' [max variation: ' + str(round(max_variation, 3)) + '%]')
            # set the x-axis label
    plt.xlabel('Sensitivity variable value')
    # set the y-axis label
    plt.ylabel('CVRMSE (%)')
    # set the limit of the y-axis
    plt.ylim(min(y)-2, max(y)+2)
    # set the title
    plt.title(title)

    plt.legend()
    plt.show()


def main():
    data_all = process_all_themes()
    save_all_data(data_all)
    # data_all_1, data_all_2 = split_data(data_all)
    # plot_one_dict(data_all_1, 'IDF Without Cooling', r'sensitivity_saving\CAPITOUL\NoCooling')
    # plot_one_dict(data_all_2, 'IDF With Cooling', r'sensitivity_saving\CAPITOUL\Cooling')

if __name__ == '__main__':
    main()


