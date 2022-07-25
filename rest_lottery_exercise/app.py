import datetime
import os
from pprint import pprint

import numpy as np
import pandas as pd


def _dataframe_from_file():
    filepath = os.path.join(os.path.dirname(
        __file__), 'input/powerball_winning_numbers.csv')

    df = pd.read_csv(filepath)
    df.columns = ['date', 'winning_numbers', 'multiplier']

    df['date'] = [datetime.datetime.strptime(
        i, '%m/%d/%Y') for i in df['date']]

    df['winning_numbers'] = [[int(j) for j in i.split(' ')]
                             for i in df['winning_numbers']]

    # df['multiplier'].fillna(1.0, inplace=True)

    pprint(df)

    return df


def _winning_numbers_from_dates(df, start, end=None):
    start = datetime.datetime.strptime(start, '%m/%d/%Y')
    end = datetime.datetime.strptime(
        end, '%m/%d/%Y') if end is not None else start

    return df.loc[(df['date'] >= start) & (df['date'] <= end)]['winning_numbers']


def _draws_from_multiplier(df, mult):
    return df.loc[df['multiplier'] == mult]


def _dates_from_winning_numbers(df, winning_nums, match=6):
    return [row['date'] for idx, row in df.iterrows() if np.sum(np.array(row['winning_numbers']) == np.array(winning_nums)) == match]


def _max_sum_date_from_dates(df, start, end):
    start = datetime.datetime.strptime(start, '%m/%d/%Y')
    end = datetime.datetime.strptime(end, '%m/%d/%Y')
    df0 = df.loc[(df['date'] >= start) & (df['date'] <= end)]
    max_sum = max([sum(i) for i in df0['winning_numbers']])
    return [row['date'] for idx, row in df0.iterrows() if sum(row['winning_numbers']) == max_sum]


def _max_freq_nums_from_dates(df, start, end):
    start = datetime.datetime.strptime(start, '%m/%d/%Y')
    end = datetime.datetime.strptime(end, '%m/%d/%Y')
    df0 = df.loc[(df['date'] >= start) & (df['date'] <= end)]

    num_freq_map = {}
    for idx, row in df0.iterrows():
        for num in row['winning_numbers']:
            if num not in num_freq_map:
                num_freq_map[num] = 0
            num_freq_map[num] += 1

    return sorted([num for num in num_freq_map.keys()], key=lambda x: num_freq_map[x], reverse=True)[:6]


if __name__ == '__main__':
    df = _dataframe_from_file()
