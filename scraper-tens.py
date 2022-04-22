import pandas as pd
import os
import glob
from datetime import datetime
import numpy as np
from sql_in import psql_insert_copy
from sqlalchemy import create_engine


def creation_date(path_to_file):
    stat = os.stat(path_to_file)
    try:
        creation_time = datetime.fromtimestamp(stat.st_birthtime)
        creation_time_formated = creation_time.strftime('%Y-%m-%d')
        return creation_time_formated
    except AttributeError:
        return stat.st_mtime


def tensile_data(file):
    data = pd.read_csv(file, skiprows=[0, 4])
    data = data.iloc[[1], 1:]
    data['Date'] = creation_date(file)
    data['FileName'] = file.split('/')[-1].replace('.csv', '')
    data['gen_formulation'] = file.split('/')[-3].split('_')[0]
    return data


files = []
start_dir = '/Users/Sam/Tresors/INSTRON TEST DATA/Tensile/2022'
pattern = "*.is_tens_Exports/*_1.csv"


for dirs, _, _ in os.walk(start_dir):
    files.extend(
        glob.glob(os.path.join(dirs, pattern)))

df = pd.DataFrame()
for file in files:
    df = pd.concat([df, tensile_data(file)], ignore_index=True, axis=0)
df.replace('-----', np.nan, inplace=True)
df.iloc[:, [0, 1, 2, 3]] = df.iloc[:, [0, 1, 2, 3]].apply(pd.to_numeric)
df = df[[
    "Modulus (Young's Tensile stress 0 % - 3 %)", 'Maximum Tensile stress',
    'Tensile strain (Strain 1) at Yield (Zero slope)',
    'Tensile strain (Strain 1) at Break (Automatic force drop)',
    'Thickness', 'Width', 'Specimen note 1', 'Date', 'FileName',
    'gen_formulation']
    ]
df.columns = [
    'Modulus', 'UTS', 'Yield_Strain', 'Break_Strain',
    'Thickness', 'Width', 'Specimen note 1',
    'Date', 'FileName', 'gen_formulation']


engine = create_engine('postgresql://doadmin:RGUuvzY6n25TQF5E@cor-properties-do-user-3715075-0.b.db.ondigitalocean.com:25060/physical_properties?sslmode=require')
df.to_sql('tensile_data', engine, if_exists='append', method=psql_insert_copy)
