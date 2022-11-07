import os, pandas as pd
import matplotlib.pyplot as plt

# data_dict = {
#     'Albedo(-)': {
#         '0.05': 12.88,
#         '0.25': 11.95,
#         '0.7':10.59,
#     },
#     'WidthRoof(m)': {
#         '4.5': 10.98,
#         '9': 11.49,
#         '18.2':11.96,
#     },
#     'WidthCanyon(m)' : {
#         '8': 11.87,
#         '15': 11.85,
#         '30':11.17,
#     },
#     'fveg_G(-)' : {
#         '0': 12.46,
#         '0.5': 11.93,
#         '1':11.79,
#     },
#     'IDFCooling(-)' : {
#         'With': 11.94,
#         'Without': 10.78,
#     },
#     'theta_canyon(deg)' : {
#         '-56 deg': 11.96,
#         '0 deg': 11.93,
#         '56 deg':11.97,
#     },
# }

def process_one_file(file_path, theme):
    # read sheet 'cvrmse'
    global data_all
    df = pd.read_excel(file_path, sheet_name='cvrmse')
    data_all[theme] = {}
    for i in range(1,len(df)):
        data_all[theme][df.iloc[i, 0]] = df.iloc[i, 1]
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
        x = list(data.keys())
        # The value is fraction, so multiply 100
        y = [i * 100 for i in list(data.values())]
        # group the sensitivity variable values by the sensitivity theme, where second layer keys are on top of each bar
        # this group share the same x-axis, theme
        plt.bar(x, y, label=theme)
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
    plot_one_dict(data_all_1, 'NoCooling', r'sensitivity_saving\CAPITOUL\NoCooling')
    plot_one_dict(data_all_2, 'Cooling', r'sensitivity_saving\CAPITOUL\Cooling')

if __name__ == '__main__':
    main()


