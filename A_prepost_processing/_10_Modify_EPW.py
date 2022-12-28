'''
1. To get the only VCWG comparison: -> One excel files
2. To generate EPW files -> All CSV corrsponding to the EPW files
3. To run EnergyPlus -> Corresponding SQL files
4. To get the offline comparison -> One excel file
'''
import os
import pathlib
import sqlite3
import sys
import re

import numpy as np

import pandas as pd
def generate_epw():
    # read text based epw file line by line
    epw_template = os.path.join('..','resources','epw','USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw')
    generate_epw_path = os.path.join('..','resources','epw',
                                     'USA_IL_Chicago-OHare.Intl.AP.725300_TMY3_No_Precipitable_Water.epw')
    with open(epw_template, 'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            if i > 7:
                lines[i] = lines[i].split(',')
                print(f'lines[i][33]: {lines[i][33]}, lines[i][34]: {lines[i][34]}')
                lines[i][33] = str(0)
                lines[i][34] = str(0) + '\n'
                lines[i] = ','.join(lines[i])
    with open(generate_epw_path, 'w') as f:
        f.writelines(lines)
def main():
    generate_epw()

if __name__ == '__main__':
    main()