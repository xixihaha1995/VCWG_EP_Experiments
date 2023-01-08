# TODO
# 1. Total electricity:cooling = 247.05 GJ
# 2. Hourly CVRMSE, NMBE, Elec:cooling, Elec:heating, Natural gas:heating
# 3. Monthly CVRMSE, NMBE, Elec:cooling, Elec:heating, Natural gas:heating
# 4. Seasonly CVRMSE, NMBE, Elec:cooling, Elec:heating, Natural gas:heating
import os
import pathlib
import re


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
    query = f"SELECT * FROM TabularDataWithStrings WHERE ReportName = '{sql_report_name}' AND TableName = '{sql_table_name}'" \
            f" AND RowName = '{sql_row_name}' AND ColumnName = '{sql_col_name}'"
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
    number = float(re.findall(regex, results[0][1])[0])
    return number