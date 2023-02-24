import os
import pathlib
import re
import sqlite3
import numpy as np
import pandas as pd
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

    return zone_pthp_dict

def read_sql(sql_path):
    abs_sql_path = os.path.abspath(sql_path)
    sql_uri = '{}?mode=ro'.format(pathlib.Path(abs_sql_path).as_uri())
    with sqlite3.connect(sql_uri, uri=True) as con:
        cursor = con.cursor()
    time_series_electricity_q = f"SELECT * FROM ReportVariableWithTime " \
                            f"WHERE Name = 'Zone Packaged Terminal Heat Pump Electricity Energy'"
    time_series_results_elec = cursor.execute(time_series_electricity_q).fetchall()
    elec_lst = [(time_series_results_elec[i][4])
                for i in range(len(time_series_results_elec))]
    zone_oat_hourly_q = f"SELECT * FROM ReportVariableWithTime " \
                        f"WHERE Name = 'Zone Outdoor Air Drybulb Temperature'"
    time_series_results_oat = cursor.execute(zone_oat_hourly_q).fetchall()
    zone_oat_hourly = [(_tuple[4]) for _tuple in time_series_results_oat]
    cursor.close()
    return time_series_results_elec, time_series_results_oat
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

def find_zone_index(zone_number, step):
    '''
    there are 100 zones
    '''
    if step == 100:
        zone_lst = [1,10,100,11,12,13,14,15,16,17,18,19,
                    2,20,21,22,23,24,25,26,27,28,29,
                    3,30,31,32,33,34,35,36,37,38,39,
                    4,40,41,42,43,44,45,46,47,48,49,
                    5,50,51,52,53,54,55,56,57,58,59,
                    6,60,61,62,63,64,65,66,67,68,69,
                    7,70,71,72,73,74,75,76,77,78,79,
                    8,80,81,82,83,84,85,86,87,88,89,
                    9,90,91,92,93,94,95,96,97,98,99]
    else:
        zone_lst = [1,100,2,3,4,5,
                    51,52,53,54,55,
                    96,97,98,99]
    return zone_lst.index(zone_number)

def find_correct_zone(all_zone_elec, all_zone_oat,zone_number, step):
    # find the zone that has the most energy consumption
    pass
    cur_zone_idx = find_zone_index(zone_number, step)
    zone_elec = [all_zone_elec[i][4] for i in range(cur_zone_idx, len(all_zone_elec), step)]
    zone_oat = [all_zone_oat[i][4] for i in range(cur_zone_idx, len(all_zone_oat), step)]
    return zone_elec, zone_oat

def floor_whole_year(sql_path,_sub_folder):
    flr_canyon_energy = {}
    footprint_area = 31 * 15
    if 'Simplified' in _sub_folder:
        step = 15
        flr_lst = [1,11,20]
    else:
        step = 100
        flr_lst = [i for i in range(1,21)]
    for flr in flr_lst:
        flr_canyon_avg_C = 0
        flr_canyon_max_C = 0
        flr_canyon_min_C = 0
        flr_elec_MJ_m2 = 0
        for zne in [1, 2, 3, 4, 5]:
            _tmp_zne_nbr = (flr - 1) * 5 + zne
            # _tmp_zne_nbr = (flr - 1) * 5 + 4
            _tmp_zne_elec, _tmp_zne_oat = find_correct_zone(all_zone_elec, all_zone_oat, _tmp_zne_nbr, step)
            flr_canyon_avg_C += sum(_tmp_zne_oat) / len(_tmp_zne_oat)
            flr_canyon_max_C += max(_tmp_zne_oat)
            flr_canyon_min_C += min(_tmp_zne_oat)
            flr_elec_MJ_m2 += sum(_tmp_zne_elec) / 1000000
        flr_canyon_avg_C /= 5
        flr_canyon_max_C /= 5
        flr_canyon_min_C /= 5
        flr_elec_MJ_m2 /= footprint_area
        flr_canyon_energy[flr] = (round(flr_canyon_avg_C,2), round(flr_canyon_max_C,2),
                                  round(flr_canyon_min_C,2), round(flr_elec_MJ_m2,2))

    # Convert flr_canyon_energy to xlsx, wheree each row is a floor, and each column is avg, max, min, elec
    xls_path = os.path.join(os.path.dirname(sql_path), f'{_sub_folder}_floor_canyon_energy.xlsx')
    writer = pd.ExcelWriter(xls_path, engine='xlsxwriter')
    df = pd.DataFrame.from_dict(flr_canyon_energy, orient='index',
                                columns=[f'Avg_C_{_sub_folder}', f'Max_C_{_sub_folder}',
                                         f'Min_C_{_sub_folder}', f'Elec_MJ_m2_{_sub_folder}'])
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
def main():
    global sql_path, zone_to_pthp, all_zone_elec, all_zone_oat
    _base = 'C:\\Users\\wulic\\Desktop\\IDF_Vector\\Vector_Cooling_Debug_New'
    zone_to_pthp = get_zone_to_pthp_dict()
    sub_folders = [ 'Scalar', 'Vector_Default_Cmu', 'Vector_Mod_Cmu']
    sub_folders = ['Vector_Simplified']
    for _sub_folder in sub_folders:
        sql_path = os.path.join(_base, _sub_folder, 'eplusout.sql')
        all_zone_elec, all_zone_oat = read_sql(sql_path)
        floor_whole_year(sql_path,_sub_folder)

if __name__ == '__main__':
    main()


'''
Execut SQL in DB Browser for SQLite.

1. SELECT * FROM ReportVariableWithTime WHERE KeyValue = 'SimHVAC'
2. Sum over the 'Value' column

The SIMHVAC SQL query is:
SELECT SUM(Value) FROM ReportVariableWithTime WHERE KeyValue = 'SimHVAC'


CORE_BOTTOM VAV BOX REHEAT COIL:Heating Coil Electricity Energy
CORE_MID VAV BOX REHEAT COIL:Heating Coil Electricity Energy
CORE_TOP VAV BOX REHEAT COIL:Heating Coil Electricity Energy
PERIMETER_BOT_ZN_1 VAV BOX REHEAT COIL:Heating Coil Electricity Energy
PERIMETER_BOT_ZN_2 VAV BOX REHEAT COIL:Heating Coil Electricity Energy
PERIMETER_BOT_ZN_3 VAV BOX REHEAT COIL:Heating Coil Electricity Energy
PERIMETER_BOT_ZN_4 VAV BOX REHEAT COIL:Heating Coil Electricity Energy
PERIMETER_MID_ZN_1 VAV BOX REHEAT COIL:Heating Coil Electricity Energy
PERIMETER_MID_ZN_2 VAV BOX REHEAT COIL:Heating Coil Electricity Energy
PERIMETER_MID_ZN_3 VAV BOX REHEAT COIL:Heating Coil Electricity Energy
PERIMETER_MID_ZN_4 VAV BOX REHEAT COIL:Heating Coil Electricity Energy
PERIMETER_TOP_ZN_1 VAV BOX REHEAT COIL:Heating Coil Electricity Energy
PERIMETER_TOP_ZN_2 VAV BOX REHEAT COIL:Heating Coil Electricity Energy
PERIMETER_TOP_ZN_3 VAV BOX REHEAT COIL:Heating Coil Electricity Energy
PERIMETER_TOP_ZN_4 VAV BOX REHEAT COIL:Heating Coil Electricity Energy
VAV_1_HEATC:Heating Coil Electricity Energy
VAV_2_HEATC:Heating Coil Electricity Energy
VAV_3_HEATC:Heating Coil Electricity Energy
VAV_1_FAN:Fan Electricity Energy
VAV_2_FAN:Fan Electricity Energy
VAV_3_FAN:Fan Electricity Energy
VAV_1_COOLC DXCOIL:Cooling Coil Electricity Energy
VAV_2_COOLC DXCOIL:Cooling Coil Electricity Energy
VAV_3_COOLC DXCOIL:Cooling Coil Electricity Energy


1. For keyvalue, it can be:
CORE_BOTTOM VAV BOX REHEAT COIL, CORE_MID VAV BOX REHEAT COIL, CORE_TOP VAV BOX REHEAT COIL, 
PERIMETER_BOT_ZN_1 VAV BOX REHEAT COIL, PERIMETER_BOT_ZN_2 VAV BOX REHEAT COIL, 
PERIMETER_BOT_ZN_3 VAV BOX REHEAT COIL, PERIMETER_BOT_ZN_4 VAV BOX REHEAT COIL, 
PERIMETER_MID_ZN_1 VAV BOX REHEAT COIL, PERIMETER_MID_ZN_2 VAV BOX REHEAT COIL, 
PERIMETER_MID_ZN_3 VAV BOX REHEAT COIL, PERIMETER_MID_ZN_4 VAV BOX REHEAT COIL, 
PERIMETER_TOP_ZN_1 VAV BOX REHEAT COIL, PERIMETER_TOP_ZN_2 VAV BOX REHEAT COIL, 
PERIMETER_TOP_ZN_3 VAV BOX REHEAT COIL, PERIMETER_TOP_ZN_4 VAV BOX REHEAT COIL, 

VAV_1_FAN, VAV_2_FAN, VAV_3_FAN, VAV_1_COOLC DXCOIL, VAV_2_COOLC DXCOIL, VAV_3_COOLC DXCOIL

Help me write one SQL query to get the sum of all the above variables.
The VAV SQL query is:
SELECT SUM(Value) FROM ReportVariableWithTime WHERE KeyValue 
IN ('CORE_BOTTOM VAV BOX REHEAT COIL', 'CORE_MID VAV BOX REHEAT COIL', 
'CORE_TOP VAV BOX REHEAT COIL', 'PERIMETER_BOT_ZN_1 VAV BOX REHEAT COIL', 
'PERIMETER_BOT_ZN_2 VAV BOX REHEAT COIL', 'PERIMETER_BOT_ZN_3 VAV BOX REHEAT COIL', 
'PERIMETER_BOT_ZN_4 VAV BOX REHEAT COIL', 'PERIMETER_MID_ZN_1 VAV BOX REHEAT COIL', 
'PERIMETER_MID_ZN_2 VAV BOX REHEAT COIL', 'PERIMETER_MID_ZN_3 VAV BOX REHEAT COIL', 
'PERIMETER_MID_ZN_4 VAV BOX REHEAT COIL', 'PERIMETER_TOP_ZN_1 VAV BOX REHEAT COIL', 
'PERIMETER_TOP_ZN_2 VAV BOX REHEAT COIL', 'PERIMETER_TOP_ZN_3 VAV BOX REHEAT COIL', 
'PERIMETER_TOP_ZN_4 VAV BOX REHEAT COIL', 'VAV_1_FAN', 'VAV_2_FAN', 'VAV_3_FAN', 
'VAV_1_COOLC DXCOIL', 'VAV_2_COOLC DXCOIL', 'VAV_3_COOLC DXCOIL')

Generate one combined SQL query to get the SIMHVAC and VAV, display the results in one table, 
where the first column is SIMHVAC and the second column is VAV.
The combined SQL query is:
SELECT SUM(Value) FROM ReportVariableWithTime WHERE KeyValue
IN ('CORE_BOTTOM VAV BOX REHEAT COIL', 'CORE_MID VAV BOX REHEAT COIL',
'CORE_TOP VAV BOX REHEAT COIL', 'PERIMETER_BOT_ZN_1 VAV BOX REHEAT COIL',
'PERIMETER_BOT_ZN_2 VAV BOX REHEAT COIL', 'PERIMETER_BOT_ZN_3 VAV BOX REHEAT COIL',
'PERIMETER_BOT_ZN_4 VAV BOX REHEAT COIL', 'PERIMETER_MID_ZN_1 VAV BOX REHEAT COIL',
'PERIMETER_MID_ZN_2 VAV BOX REHEAT COIL', 'PERIMETER_MID_ZN_3 VAV BOX REHEAT COIL',
'PERIMETER_MID_ZN_4 VAV BOX REHEAT COIL', 'PERIMETER_TOP_ZN_1 VAV BOX REHEAT COIL',
'PERIMETER_TOP_ZN_2 VAV BOX REHEAT COIL', 'PERIMETER_TOP_ZN_3 VAV BOX REHEAT COIL',
'PERIMETER_TOP_ZN_4 VAV BOX REHEAT COIL', 'VAV_1_FAN', 'VAV_2_FAN', 'VAV_3_FAN',
'VAV_1_COOLC DXCOIL', 'VAV_2_COOLC DXCOIL', 'VAV_3_COOLC DXCOIL')
UNION
SELECT SUM(Value) FROM ReportVariableWithTime WHERE KeyValue = 'SIMHVAC'

Please generate the following table:


The table query is:
SELECT SUM(Value) FROM ReportVariableWithTime WHERE KeyValue = 'SIMHVAC'
UNION
SELECT SUM(Value) FROM ReportVariableWithTime WHERE KeyValue
IN ('CORE_BOTTOM VAV BOX REHEAT COIL', 'CORE_MID VAV BOX REHEAT COIL',
'CORE_TOP VAV BOX REHEAT COIL', 'PERIMETER_BOT_ZN_1 VAV BOX REHEAT COIL',


SELECT (SELECT SUM(Value) FROM ReportVariableWithTime WHERE KeyValue = 'SimHVAC') /1E9 AS SIMHVAC_GJ,
       (SELECT SUM(Value) FROM ReportVariableWithTime WHERE KeyValue 
       IN ('CORE_BOTTOM VAV BOX REHEAT COIL', 'CORE_MID VAV BOX REHEAT COIL', 
       'CORE_TOP VAV BOX REHEAT COIL', 'PERIMETER_BOT_ZN_1 VAV BOX REHEAT COIL', 
       'PERIMETER_BOT_ZN_2 VAV BOX REHEAT COIL', 'PERIMETER_BOT_ZN_3 VAV BOX REHEAT COIL', 
       'PERIMETER_BOT_ZN_4 VAV BOX REHEAT COIL', 'PERIMETER_MID_ZN_1 VAV BOX REHEAT COIL', 
       'PERIMETER_MID_ZN_2 VAV BOX REHEAT COIL', 'PERIMETER_MID_ZN_3 VAV BOX REHEAT COIL', 
       'PERIMETER_MID_ZN_4 VAV BOX REHEAT COIL', 'PERIMETER_TOP_ZN_1 VAV BOX REHEAT COIL', 
       'PERIMETER_TOP_ZN_2 VAV BOX REHEAT COIL', 'PERIMETER_TOP_ZN_3 VAV BOX REHEAT COIL', 
       'PERIMETER_TOP_ZN_4 VAV BOX REHEAT COIL', 'VAV_1_FAN', 'VAV_2_FAN', 'VAV_3_FAN', 
       'VAV_1_COOLC DXCOIL', 'VAV_2_COOLC DXCOIL', 'VAV_3_COOLC DXCOIL')) /1E9 AS VAV_GJ;
'''