import pandas as pd, numpy as np, gif, matplotlib.pyplot as plt

def read_text_as_csv(file_path):
    '''
    df first column is index
    '''
    df = pd.read_csv(file_path, skiprows=3, header= None, sep= '[ ^]+', engine='python')
    # set index to first column
    df.set_index(df.iloc[:,0], inplace=True)
    return df

def plot_all_columns_in_one_figure_with_separation(df):
    '''
    plot all columns in one figure with separation
    '''
    fig, ax = plt.subplots(figsize=(10,5))
    for i in range(1, df.shape[1]):
        ax.plot(df.index, df.iloc[:,i], label=df.columns[i])
    ax.legend()
    plt.show()

@gif.frame
def helper_plot_1(df,i, building_name):
    '''
    plot index and ith column
    '''
    plt.plot(df.iloc[:,i],df.index)
    plt.xlim(285,320)
    plt.xlabel('Temperature (K)')
    plt.ylabel('Heights (m)')

    day = i//24
    hour = i%24
    plt.title(f'{building_name},Day:{day +1}, Hour:{hour}')
    return plt.gcf()

building = 'Normal_Building'

df = read_text_as_csv(f'{building}.csv')
# df max across all elements
frames = []
for i in range(df.shape[1]):
    frames.append(helper_plot_1(df,i,building))
gif.save(frames, f'{building}.gif',
         duration=500)