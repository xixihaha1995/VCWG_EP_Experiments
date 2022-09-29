# read csv, then plot
import pandas as pd, matplotlib.pyplot as plt, _0_all_plot_tools as plt_tools



results_folder = r'..\\_2_saved\\accumulated_confirmation'
start_time = '2002-June-09 00:05:00'

df_ep_only = pd.read_csv(results_folder + r'\\RefBldgMidriseApartmentPost1980_v1.4_7.2_4C_USA_WA_SEATTLE_year.csv')
df_nested_ep_only = pd.read_csv(results_folder + r'\\records_df_year.csv')

df_ep_only_timed = plt_tools.ep_time_to_pandas_time(df_ep_only,start_time)
df_nested_ep_only_timed = plt_tools.sequence_time_to_pandas_time(df_nested_ep_only, 300, start_time)

# according to the index of df_nested_ep_only_timed, select all the corresponding observations from df_ep_only_timed
df_ep_only_timed_aligned = df_ep_only_timed.loc[df_nested_ep_only_timed.index]

bias_rmse_r2 = plt_tools.bias_rmse_r2(df_ep_only_timed_aligned['SimHVAC:HVAC System Total Heat Rejection Energy [J](TimeStep) '],
                                      df_nested_ep_only_timed['coordination.ep_accumulated_waste_heat'])

# plot
fig, ax = plt.subplots()
ax.plot(df_nested_ep_only_timed.index, df_ep_only_timed_aligned['SimHVAC:HVAC System Total Heat Rejection Energy [J](TimeStep) '],
        label='5 min TimeStep (EP Software)')
ax.plot(df_nested_ep_only_timed.index, df_nested_ep_only_timed['coordination.ep_accumulated_waste_heat'],
        label='5 min Accumulated (EP Python-API)')
ax.set(xlabel='Time [h]', ylabel='HVAC System Total Heat Rejection Energy [J]',
         title='Accumulated Waste Heat in different software (EP only, EP+VCWG)')
ax.legend()
plt.title(f'Bias, RMSE, R2: {bias_rmse_r2}')
plt.show()



