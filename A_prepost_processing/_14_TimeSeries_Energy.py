import os
import pathlib
import re
import sqlite3

import numpy as np
from matplotlib import pyplot as plt


def read_sql(sql_path):
    sql_report_name = 'AnnualBuildingUtilityPerformanceSummary'
    sql_table_name = 'Site and Source Energy'
    sql_row_name = 'Total Site Energy'
    sql_col_name = 'Total Energy'

    abs_sql_path = os.path.abspath(sql_path)
    sql_uri = '{}?mode=ro'.format(pathlib.Path(abs_sql_path).as_uri())
    query = f"SELECT * FROM TabularDataWithStrings WHERE ReportName = '{sql_report_name}' AND TableName = '{sql_table_name}'" \
            f" AND RowName = '{sql_row_name}' AND ColumnName = '{sql_col_name}'"
    with sqlite3.connect(sql_uri, uri=True) as con:
        cursor = con.cursor()
    #Zone Packaged Terminal Heat Pump Total Heating Energy
    time_series_cooling_q = f"SELECT * FROM ReportVariableWithTime " \
                            f"WHERE Name = 'Zone Packaged Terminal Heat Pump Total Heating Energy'"
    time_series_results = cursor.execute(time_series_cooling_q).fetchall()
    # # time_series_results is a list of tuples, to sum over the tuple[4]
    # cooling_sum_J = sum([_tuple[4] for _tuple in time_series_results])

    # time_series_electricity_q = f"SELECT * FROM ReportVariableWithTime " \
    #                         f"WHERE Name = 'Zone Packaged Terminal Heat Pump Electricity Energy'"
    # time_series_results = cursor.execute(time_series_electricity_q).fetchall()
    # time_series_results is a list of tuples, to sum over the tuple[4]
    elec_lst = [(_tuple[4]) for _tuple in time_series_results]
    zone_oat_hourly_q = f"SELECT * FROM ReportVariableWithTime " \
                        f"WHERE Name = 'Zone Outdoor Air Drybulb Temperature'"
    time_series_results = cursor.execute(zone_oat_hourly_q).fetchall()
    zone_oat_hourly = [(_tuple[4]) for _tuple in time_series_results]
    return elec_lst, zone_oat_hourly
    electricity_sum_J = sum([_tuple[4] for _tuple in time_series_results])
    electricity_sum_GJ = electricity_sum_J / 1000000000

def plot_elec(scalar_lst, vector_lst, tilte):
    pass
    # The each 100 values is for one timestep
    scalar_lst = [sum(scalar_lst[i:i + 100])/100 for i in range(0, len(scalar_lst), 100)]
    vector_lst = [sum(vector_lst[i:i + 100])/100 for i in range(0, len(vector_lst), 100)]
    # for plotting purposes, convert lst to np array
    scalar_lst = np.array(scalar_lst)
    vector_lst = np.array(vector_lst)


    #plot both scalar and vector for comparison
    fig, ax = plt.subplots()
    ax.plot(scalar_lst, label='Scalar')
    ax.plot(vector_lst, label='Vector')

    plt.title(tilte)
    plt.legend()
    plt.show()


def main():
    global experiments_folder
    # C:\Users\wulic\Desktop\IDF_Vector\Vector_Cooling_Debug
    _base = 'C:\\Users\\wulic\\Desktop\\IDF_Vector\\Vector_Cooling_Debug'
    _sub_folder = 'Scalar'
    # _sub_folder = 'Vector_Mod_Cmu'
    experiments_folder = os.path.join(_base, _sub_folder,'eplusout.sql')
    scalar_elec_lst, scalar_oat_lst = read_sql(experiments_folder)
    _sub_folder = 'Vector_Mod_Cmu'
    experiments_folder = os.path.join(_base, _sub_folder, 'eplusout.sql')
    vector_elec_lst, vector_oat_lst = read_sql(experiments_folder)
    plot_elec(scalar_oat_lst, vector_oat_lst, 'Zone Outdoor Air Drybulb Temperature (100 Zone, Avg, C, Hourly)')
    plot_elec(scalar_elec_lst, vector_elec_lst, 'Zone PTHP Cooling Energy (100 Zone, Sum, J, 5 min)')

if __name__ == '__main__':
    main()