'''
1. To get the total electricity cooling
'''
import os
import pathlib
import re
import sqlite3


def read_sql(csv_file):
    csv_name = re.search(r'(.*)\.csv', csv_file).group(1)
    current_path = f'./{experiments_folder}'
    sql_path = "foo"
    for folder in os.listdir(current_path):
        if csv_name in folder and 'ep_trivial_outputs' in folder:
            sql_path = os.path.join(current_path, folder, 'eplusout.sql')
            break
    if not os.path.exists(sql_path):
        return None
    abs_sql_path = os.path.abspath(sql_path)
    sql_uri = '{}?mode=ro'.format(pathlib.Path(abs_sql_path).as_uri())
    # Facility:Electricity:Cooling [J] 3151
    ReportDataDictionaryIndex = 3151
    query = f"SELECT * FROM ReportVariableWithTime WHERE ReportDataDictionaryIndex = {ReportDataDictionaryIndex}"
    with sqlite3.connect(sql_uri, uri=True) as con:
        cursor = con.cursor()
        results = cursor.execute(query).fetchall()
        if results:
            pass
        else:
            msg = ("Cannot find the EnergyPlusVersion in the SQL file. "
                   "Please inspect query used:\n{}".format(query))
            raise ValueError(msg)
    regex = r'(\d+\.?\d*)'
    # results is len(results), where each element is a tuple, tuple[4] is the value
    elec_cooling_J_lst = [float(re.search(regex, str(result[4])).group(1)) for result in results]
    return elec_cooling_J_lst

def main():
    global experiments_folder
    experiments_folder = 'CAPITOUl_Whole_Year'
    experiments = []
    for file in os.listdir(experiments_folder):
        if file.endswith('.csv') and '345' in file:
            experiments.append(file)
    experiments = ['CAPITOUL_WithoutShading_WithCooling_345.csv']
    for experiment in experiments:
        read_sql(experiment)

if __name__ == '__main__':
    main()

