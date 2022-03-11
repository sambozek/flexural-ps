import pandas as pd
import glob
import os
from sklearn import linear_model
from sklearn.metrics import r2_score
from sql_in import psql_insert_copy
from sqlalchemy import create_engine
import numpy as np


def main():
    flexural_results = pd.DataFrame()
    list_of_flexural_paths = get_list_of_flexural_paths("./green-flexural_BV")
    for path in list_of_flexural_paths:
        dimension, logs = folder_opener(path)
        flex_mod = log_converter(logs, dimension)
        flex_mod['Date'] = path.split('/')[-2]
        flex_mod['Experiment'] = path.split('/')[-1]
        flexural_results = pd.concat(
            [flex_mod, flexural_results], ignore_index=True)
    flexural_results.to_csv('./all_flex_results.csv')


# TODO: Get list of all flexural tests
def get_list_of_flexural_paths(path):
    directoryList = []

    # return nothing if path is a file
    if os.path.isfile(path):
        return []

    # add dir to directorylist if it contains .txt files
    if len([f for f in os.listdir(path) if f.endswith('.txt')]) > 0:
        directoryList.append(path)

    for d in os.listdir(path):
        new_path = os.path.join(path, d)
        if os.path.isdir(new_path):
            directoryList += get_list_of_flexural_paths(new_path)

    return directoryList


def folder_opener(folder):
    '''
    :param folder: The folder containing the .log files and Dimensions.txt
    :return: dataframe of dimensions and logs associated with
     proper dimensional measurements.
    '''
    dimensions = pd.read_csv(folder + '/Dimensions.txt')
    logs = glob.glob(folder + '/*.log')
    try:
        assert len(logs) == len(dimensions)
        return dimensions, sorted(logs)
    except AssertionError:
        print('Number of logs and dimensions do not match')


def load_travel_time(log, dimension):
    '''

    :param log: Tensile .log data from a dogbone pulled on MARK-10
    :param dimension: the dimension of the particular dogbone that was pulled
    :return: converted Load, Travel, and Time for use in the green_model
    '''
    L = 25.4  # span length (mm)
    log = pd.read_csv(log, header=5, sep='\t')
    load_travel = pd.DataFrame()
    load_travel['Load'] = (
        (3 * log.Load * L) / (2 * dimension.Width * (dimension.Depth ** 2))
        )
    load_travel['Travel'] = (-6 * log.Travel * dimension.Depth) / (L ** 2)
    load_travel['Time'] = log.Load / log.Travel
    return load_travel


def green_model(load_travel):
    '''
    :param load_travel: the converted Load, Travel, Time
    from the load_travel_time function
    :return: The green strength and associated coefficent of determination of
    the green strength, using 10% elongation at break.
    '''
    constrained_travel = load_travel[load_travel["Travel"] < 0.03]
    model = linear_model.LinearRegression()
    travel, load = constrained_travel.Travel, constrained_travel.Load
    travel = travel.values.reshape(-1, 1)
    model.fit(travel, load)
    r2 = r2_score(load, model.predict(X=travel))
    return model.coef_[0], r2


def log_converter(logs, dimensions):
    '''

    :param logs: log files
    :param dimensions: dataframe of the dimensions.
    :return: Dataframe of the green strengths in MegaPascal
    '''

    green_strengths = {'flex bar': [],
                       'flex modulus': [],
                       'r2': []}
    for num, log in enumerate(logs):
        load_travel = load_travel_time(log, dimensions.loc[num])
        green_strength, determination_coef = green_model(load_travel)
        green_strengths['flex bar'].append(log[2])
        green_strengths['flex modulus'].append(green_strength)
        green_strengths['r2'].append(determination_coef)

    green_strengths = pd.DataFrame(green_strengths)
    return green_strengths


def avg_and_std(green_strength):
    '''

    :param green_strength: DataFrame of the green strength,
    :return: Green Strength with its absolute and relative stdev, 
    average coefficient of determination and its green strength.
    '''
    avs = green_strength[['flex modulus',
                          'r2']].describe().loc[['mean', 'std']]
    avs = avs.apply(lambda x: round(x, 3))
    avs.loc['rel_std'] = [
        str(
            (
                (avs['flex modulus'].loc['std'] / avs['flex modulus']
                ).loc['mean']) * 100)[:2] + ' %', np.NaN]
    return avs


if __name__ == '__main__':
    main()


df = pd.read_csv('./all_flex_results.csv')
engine = create_engine('postgresql://doadmin:RGUuvzY6n25TQF5E@cor-properties-do-user-3715075-0.b.db.ondigitalocean.com:25060/physical_properties?sslmode=require')
df.to_sql('flexural_data', engine, if_exists='append', method=psql_insert_copy)
