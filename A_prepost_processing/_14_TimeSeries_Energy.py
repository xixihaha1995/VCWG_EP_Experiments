import os
import pathlib
import re
import sqlite3

import numpy as np
from matplotlib import pyplot as plt

def get_zone_to_pthp_dict():
    zone_pthp_dict = {}
    zone_pthp_dict[1] = 56
    zone_pthp_dict[10] = 65
    zone_pthp_dict[100] = 6
    zone_pthp_dict[11] = 66
    zone_pthp_dict[12] = 67
    zone_pthp_dict[13] = 68
    zone_pthp_dict[14] = 69
    zone_pthp_dict[15] = 70
    zone_pthp_dict[16] = 71
    zone_pthp_dict[17] = 72
    zone_pthp_dict[18] = 73
    zone_pthp_dict[19] = 74
    zone_pthp_dict[2] = 57
    zone_pthp_dict[20] = 75
    zone_pthp_dict[21] = 76
    zone_pthp_dict[22] = 77
    zone_pthp_dict[23] = 78
    zone_pthp_dict[24] = 79
    zone_pthp_dict[25] = 80
    zone_pthp_dict[26] = 81
    zone_pthp_dict[27] = 82
    zone_pthp_dict[28] = 83
    zone_pthp_dict[29] = 84
    zone_pthp_dict[3] = 58
    zone_pthp_dict[30] = 85
    zone_pthp_dict[31] = 86
    zone_pthp_dict[32] = 87
    zone_pthp_dict[33] = 88
    zone_pthp_dict[34] = 89
    zone_pthp_dict[35] = 90
    zone_pthp_dict[36] = 91
    zone_pthp_dict[37] = 92
    zone_pthp_dict[38] = 93
    zone_pthp_dict[39] = 94
    zone_pthp_dict[4] = 59
    zone_pthp_dict[40] = 95
    zone_pthp_dict[41] = 96
    zone_pthp_dict[42] = 97
    zone_pthp_dict[43] = 98
    zone_pthp_dict[44] = 99
    zone_pthp_dict[45] = 100
    zone_pthp_dict[46] = 38
    zone_pthp_dict[47] = 39
    zone_pthp_dict[48] = 40
    zone_pthp_dict[49] = 41
    zone_pthp_dict[5] = 60
    zone_pthp_dict[50] = 42
    zone_pthp_dict[51] = 43
    zone_pthp_dict[52] = 44
    zone_pthp_dict[53] = 45
    zone_pthp_dict[54] = 46
    zone_pthp_dict[55] = 47
    zone_pthp_dict[56] = 48
    zone_pthp_dict[57] = 49
    zone_pthp_dict[58] = 50
    zone_pthp_dict[59] = 51
    zone_pthp_dict[6] = 61
    zone_pthp_dict[60] = 52
    zone_pthp_dict[61] = 53
    zone_pthp_dict[62] = 54
    zone_pthp_dict[63] = 55
    zone_pthp_dict[64] = 36
    zone_pthp_dict[65] = 37
    zone_pthp_dict[66] = 34
    zone_pthp_dict[67] = 35
    zone_pthp_dict[68] = 25
    zone_pthp_dict[69] = 26
    zone_pthp_dict[7] = 62
    zone_pthp_dict[70] = 27
    zone_pthp_dict[71] = 28
    zone_pthp_dict[72] = 29
    zone_pthp_dict[73] = 30
    zone_pthp_dict[74] = 31
    zone_pthp_dict[75] = 32
    zone_pthp_dict[76] = 33
    zone_pthp_dict[77] = 23
    zone_pthp_dict[78] = 24
    zone_pthp_dict[79] = 18
    zone_pthp_dict[8] = 63
    zone_pthp_dict[80] = 19
    zone_pthp_dict[81] = 20
    zone_pthp_dict[82] = 21
    zone_pthp_dict[83] = 22
    zone_pthp_dict[84] = 16
    zone_pthp_dict[85] = 17
    zone_pthp_dict[86] = 14
    zone_pthp_dict[87] = 15
    zone_pthp_dict[88] = 12
    zone_pthp_dict[89] = 13
    zone_pthp_dict[9] = 64
    zone_pthp_dict[90] = 11
    zone_pthp_dict[91] = 7
    zone_pthp_dict[92] = 8
    zone_pthp_dict[93] = 9
    zone_pthp_dict[94] = 10
    zone_pthp_dict[95] = 1
    zone_pthp_dict[96] = 2
    zone_pthp_dict[97] = 3
    zone_pthp_dict[98] = 4
    zone_pthp_dict[99] = 5

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
                            f"WHERE Name = 'Zone Packaged Terminal Heat Pump Total Cooling Energy'"\
                            f"And KeyValue = 'PTHP 5'"
    time_series_results_cooling = cursor.execute(time_series_cooling_q).fetchall()
    # # time_series_results is a list of tuples, to sum over the tuple[4]
    # cooling_sum_J = sum([_tuple[4] for _tuple in time_series_results])

    time_series_electricity_q = f"SELECT * FROM ReportVariableWithTime " \
                            f"WHERE Name = 'Zone Packaged Terminal Heat Pump Electricity Energy'"\
                            f"And KeyValue = 'PTHP 2'"
    time_series_results_elec = cursor.execute(time_series_electricity_q).fetchall()
    # time_series_results is a list of tuples, to sum over the tuple[4]
    elec_lst = [(time_series_results_elec[i][4])
                for i in range(len(time_series_results_elec))]
    zone_oat_hourly_q = f"SELECT * FROM ReportVariableWithTime " \
                        f"WHERE Name = 'Zone Outdoor Air Drybulb Temperature'"\
                        f"And KeyValue = 'THERMAL ZONE 96'"
    time_series_results = cursor.execute(zone_oat_hourly_q).fetchall()
    zone_oat_hourly = [(_tuple[4]) for _tuple in time_series_results]
    return elec_lst, zone_oat_hourly
    electricity_sum_J = sum([_tuple[4] for _tuple in time_series_results])
    electricity_sum_GJ = electricity_sum_J / 1000000000

def plot_elec(scalar_lst, vector_lst, tilte):
    pass
    # # The each 100 values is for one timestep
    # scalar_lst = [sum(scalar_lst[i:i + 100])/100 for i in range(0, len(scalar_lst), 100)]
    # vector_lst = [sum(vector_lst[i:i + 100])/100 for i in range(0, len(vector_lst), 100)]
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
    # _sub_folder = 'Vector_Default_Cmu'
    _sub_folder = 'Vector_Default_Cmu_Core'
    experiments_folder = os.path.join(_base, _sub_folder, 'eplusout.sql')
    vector_elec_lst, vector_oat_lst = read_sql(experiments_folder)
    plot_elec(scalar_oat_lst, vector_oat_lst, 'Zone Outdoor Air Drybulb Temperature (Zone 1, C, Hourly)')
    plot_elec(scalar_elec_lst, vector_elec_lst, 'Zone PTHP Elec Energy (Zone 1, 5 min)\n'
                                                f'Scalar {round(sum(scalar_elec_lst)/1E9, 2)} GJ, '
                                                f'Vector {round(sum(vector_elec_lst)/1E9, 2)} GJ')

if __name__ == '__main__':
    main()