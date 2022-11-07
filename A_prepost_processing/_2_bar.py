import os, pandas as pd
import matplotlib.pyplot as plt

def process_one_file(file_path, theme):
    # read sheet 'cvrmse'
    global data_all
    df = pd.read_excel(file_path, sheet_name='cvrmse')
    data_all[theme] = {}
    for i in range(len(df)):
        # format the value to 4 decimal places
        data_all[theme][df.iloc[i, 0]] = round(df.iloc[i, 1]* 100, 3)
def process_one_theme(theme, theme_path):
    global data_all
    '''
    data_all, first level is theme, second level is variable, third level is value
    '''
    data_all[theme] = {}
    files = os.listdir(theme_path)
    # open xlsx file, with '_sensitivity_analysis.xlsx' in the name
    for file in files:
        if '_sensitivity_analysis.xlsx' in file:
            file_path = theme_path + '\\' + file
            process_one_file(file_path, theme)
def process_all_themes():
    global data_all
    data_all = {}
    all_themes_path = r'sensitivity_saving\CAPITOUL'
    all_themes = os.listdir(all_themes_path)
    for theme in all_themes:
        process_one_theme(theme, all_themes_path + '\\' + theme)
    return data_all

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
    data_all_1, data_all_2 = split_data(data_all)
    plot_one_dict(data_all_1, 'IDF Without Cooling', r'sensitivity_saving\CAPITOUL\NoCooling')
    plot_one_dict(data_all_2, 'IDF With Cooling', r'sensitivity_saving\CAPITOUL\Cooling')

if __name__ == '__main__':
    main()


