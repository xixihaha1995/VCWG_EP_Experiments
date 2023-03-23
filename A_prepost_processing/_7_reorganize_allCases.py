'''
./AllCases_Roughness/_allCase_Zoh_for_Heat.txt

cvrmse for Rural_Weather, case name is ByPass_Vancouver_Rural_WithoutShading_WithCooling.csv, height is 20.0, performance is 8.23
nmbe for Rural_Weather, case name is ByPass_Vancouver_Rural_WithoutShading_WithCooling.csv, height is 20.0, performance is -1.89
cvrmse, case name is ByPass_Vancouver_Rural_WithoutShading_WithCooling.csv, height is 1.2, performance is 16.07
nmbe, case name is ByPass_Vancouver_Rural_WithoutShading_WithCooling.csv, height is 1.2, performance is -4.08
cvrmse, case name is OnlyVCWG_Vancouver_Rural_WithoutShading_WithCooling.csv, height is 1.2, performance is 16.38
nmbe, case name is OnlyVCWG_Vancouver_Rural_WithoutShading_WithCooling.csv, height is 1.2, performance is -5.33
'''
import re

'''
I will reorganize the results from the above txt file into a csv file.
Columns:
Rural CVRMSE (%)
OnlyVCWG CVRMSE (%)	
Bypass With Shading CVRMSE (%)	
Bypass Without Shading CVRMSE (%)
Rural NMBE (%)	
OnlyVCWG NMBE (%)	
Bypass With Shading NMBE (%)	
Bypass Without Shading NMBE (%)

Rows:
CAPITOUL With Cooling
CAPITOUL Without Cooling
BUBBLE UE1 2.6
BUBBLE UE1 13.9
BUBBLE UE1 17.5
BUBBLE UE1 21.5
BUBBLE UE1 25.5
BUBBLE UE1 31.2
Vancouver TopForcing- 1.2
Vancouver TopForcing- 20.0
BUBBLE UE2 3.0
BUBBLE UE2 15.8
BUBBLE UE2 22.9
BUBBLE UE2 27.8
BUBBLE UE2 32.9
Vancouver Rural 1.2
Vancouver Rural 20.0
'''

def _generateColumns(line):
    if 'Rural_Weather' in line and 'cvrmse' in line:
        return 'Rural CVRMSE (%)'
    elif 'Rural_Weather' in line and 'nmbe' in line:
        return 'Rural NMBE (%)'
    elif 'OnlyVCWG' in line and 'cvrmse' in line:
        return 'OnlyVCWG CVRMSE (%)'
    elif 'OnlyVCWG' in line and 'nmbe' in line:
        return 'OnlyVCWG NMBE (%)'
    elif 'ByPass' in line and 'cvrmse' in line and 'WithShading' in line:
        return 'Bypass With Shading CVRMSE (%)'
    elif 'ByPass' in line and 'nmbe' in line and 'WithShading' in line:
        return 'Bypass With Shading NMBE (%)'
    elif 'ByPass' in line and 'cvrmse' in line and 'WithoutShading' in line:
        return 'Bypass Without Shading CVRMSE (%)'
    elif 'ByPass' in line and 'nmbe' in line and 'WithoutShading' in line:
        return 'Bypass Without Shading NMBE (%)'

def _getRowsAndValues(line):
    #use regex to extract decimal numbers
    _nbs = re.findall(r"[-+]?\d*\.\d+|\d+", line)

    _height, value = _nbs[-2], _nbs[-1]
    if 'CAPITOUL' in line and 'WithCooling' in line:
        return 'CAPITOUL With Cooling', float(value)
    elif 'CAPITOUL' in line and 'WithoutCooling' in line:
        return 'CAPITOUL Without Cooling', float(value)
    elif 'BUBBLE' in line and 'UE1' in line:
        return 'BUBBLE UE1 ' + _height, float(value)
    elif 'BUBBLE' in line and 'UE2' in line:
        return 'BUBBLE UE2 ' + _height, float(value)
    elif 'Vancouver' in line and 'TopForcing' in line:
        return 'Vancouver TopForcing- ' + _height, float(value)
    elif 'Vancouver_Rural' in line:
        return 'Vancouver Rural ' + _height, float(value)

# Initialize the csv file with columns and rows, default value is 0
columns = ['Rural CVRMSE (%)', 'OnlyVCWG CVRMSE (%)',
           'Bypass With Shading CVRMSE (%)', 'Bypass Without Shading CVRMSE (%)',
           'Rural NMBE (%)', 'OnlyVCWG NMBE (%)',
           'Bypass With Shading NMBE (%)', 'Bypass Without Shading NMBE (%)']
rows = ['CAPITOUL With Cooling', 'CAPITOUL Without Cooling',
        'BUBBLE UE1 2.6', 'BUBBLE UE1 13.9', 'BUBBLE UE1 17.5', 'BUBBLE UE1 21.5', 'BUBBLE UE1 25.5', 'BUBBLE UE1 31.2',
        'Vancouver TopForcing- 1.2', 'Vancouver TopForcing- 20.0',
        'BUBBLE UE2 3.0', 'BUBBLE UE2 15.8', 'BUBBLE UE2 22.9', 'BUBBLE UE2 27.8', 'BUBBLE UE2 32.9',
        'Vancouver Rural 1.2', 'Vancouver Rural 20.0']
_dict = {}
for row in rows:
    _dict[row] = {}
    for column in columns:
        _dict[row][column] = 0
# Open and read the text file line by line
with open('./AllCases_Roughness/_allCase_Zoh_for_Heat.txt', 'r') as f:
    lines = f.readlines()
    # For each line, determine which column and row, then fill the value with performance is [number]
    for line in lines:
        column = _generateColumns(line)
        row, value = _getRowsAndValues(line)
        _dict[row][column] = value
# convert the dictionary to xlsx file
import pandas as pd
df = pd.DataFrame(_dict)
df = df.T
df.to_csv('./AllCases_Roughness/_allCase_Zoh_for_Heat.csv')


