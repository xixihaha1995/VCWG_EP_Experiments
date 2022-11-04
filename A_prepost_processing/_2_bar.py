import matplotlib.pyplot as plt


data_dict = {
    'Albedo(-)': {
        '0.05': 12.88,
        '0.25': 11.95,
        '0.7':10.59,
    },
    'WidthRoof(m)': {
        '4.5': 10.98,
        '9': 11.49,
        '18.2':11.96,
    },
    'WidthCanyon(m)' : {
        '8': 11.87,
        '15': 11.85,
        '30':11.17,
    },
    'fveg_G(-)' : {
        '0': 12.46,
        '0.5': 11.93,
        '1':11.79,
    },
    'IDFCooling(-)' : {
        'With': 11.94,
        'Without': 10.78,
    },
    'theta_canyon(deg)' : {
        '-56 deg': 11.96,
        '0 deg': 11.93,
        '56 deg':11.97,
    },
}
#set the figure size
fix, ax = plt.subplots(figsize=(10, 6))

labels = list(data_dict.keys())



x, y = [], []
for theme, data in data_dict.items():
    x = list(data.keys())
    y = list(data.values())
    # group the sensitivity variable values by the sensitivity theme, where second layer keys are on top of each bar
    # this group share the same x-axis, theme
    plt.bar(x, y, label=theme)
# set the x-axis label
plt.xlabel('Sensitivity variable value')
# set the y-axis label
plt.ylabel('CVRMSE (%)')
# set the limit of the y-axis
plt.ylim(min(y)-2, max(y)+2)
plt.legend()
plt.show()


