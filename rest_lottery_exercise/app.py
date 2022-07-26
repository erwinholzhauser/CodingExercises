import datetime
import os
from pprint import pprint
import json

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request

_draws_df = None
app = Flask(__name__)


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

    # pprint(df)

    return df


def _winning_numbers_from_dates(start, end=None, df=_draws_df):
    start = datetime.datetime.strptime(start, '%m-%d-%Y')
    end = datetime.datetime.strptime(
        end, '%m-%d-%Y') if end is not None else start

    return df.loc[(df['date'] >= start) & (df['date'] <= end)]['winning_numbers']


def _draws_from_dates(start, end=None, df=_draws_df):
    start = datetime.datetime.strptime(start, '%m-%d-%Y')
    end = datetime.datetime.strptime(
        end, '%m-%d-%Y') if end is not None else start

    return df.loc[(df['date'] >= start) & (df['date'] <= end)]


def _draws_from_multiplier(mult, df=_draws_df):
    return df.loc[df['multiplier'] == mult]


def _dates_from_winning_numbers(winning_nums, match=6, df=_draws_df):
    return [row['date'] for idx, row in df.iterrows()
            if np.sum(np.array(row['winning_numbers']) == np.array(winning_nums)) == match]


def _max_sum_date_from_dates(start, end, df=_draws_df):
    start = datetime.datetime.strptime(start, '%m-%d-%Y')
    end = datetime.datetime.strptime(end, '%m-%d-%Y')
    df0 = df.loc[(df['date'] >= start) & (df['date'] <= end)]
    max_sum = max([sum(i) for i in df0['winning_numbers']])
    return [row['date'] for idx, row in df0.iterrows()
            if sum(row['winning_numbers']) == max_sum]


def _max_freq_nums_from_dates(start, end, df=_draws_df):
    start = datetime.datetime.strptime(start, '%m-%d-%Y')
    end = datetime.datetime.strptime(end, '%m-%d-%Y')
    df0 = df.loc[(df['date'] >= start) & (df['date'] <= end)]

    num_freq_map = {}
    for idx, row in df0.iterrows():
        for num in row['winning_numbers']:
            if num not in num_freq_map:
                num_freq_map[num] = 0
            num_freq_map[num] += 1

    return sorted([num for num in num_freq_map.keys()],
                  key=lambda x: num_freq_map[x], reverse=True)[:6]


def _avg_multiplier_from_month(month, year, df=_draws_df):
    # Draws without multipliers aren't included in the average.
    start = datetime.datetime(year=year, month=month, day=1)
    end = datetime.datetime(year=year, month=(month + 1), day=1) if month < 12 \
        else datetime.datetime(year=year + 1, month=1, day=1)
    return df.loc[(df['date'] >= start) & (df['date'] < end)]['multiplier'].mean()


@app.route('/winning_number/', methods=['GET'])
def winning_numbers():
    start, end = request.args.get('start_date'), request.args.get('end_date')
    nums = (_draws_from_dates(start, end, _draws_df)
            if start else _draws_df)['winning_numbers'].tolist()
    return jsonify({'data': {'winning_numbers': nums}})


@app.route('/draw/', methods=['GET'])
def draws():
    mult = request.args.get('multiplier')
    return jsonify({'data': (_draws_from_multiplier(float(mult), _draws_df) if mult
                             else _draws_df).to_dict(orient='records')})


@app.route('/date/', methods=['GET'])
def dates_from_winning_numbers():
    nums = [int(i) for i in request.args.get('numbers').split(',')]
    return jsonify({'data': {
        'match_4': _dates_from_winning_numbers(nums, match=4, df=_draws_df),
        'match_5': _dates_from_winning_numbers(nums, match=5, df=_draws_df),
        'match_6': _dates_from_winning_numbers(nums, match=6, df=_draws_df),
    }})


@app.route('/max_winning_numbers_sum/date/', methods=['GET'])
def max_sum_date():
    start, end = request.args.get('start_date'), request.args.get('end_date')
    return jsonify({'data': {'dates': _max_sum_date_from_dates(start, end, _draws_df)}})


@app.route('/max_frequence_numbers/', methods=['GET'])
def max_freq_nums():
    start, end = request.args.get('start_date'), request.args.get('end_date')
    return jsonify({'data': {'numbers': _max_freq_nums_from_dates(start, end, _draws_df)}})


@app.route('/average_multiplier/', methods=['GET'])
def avg_multiplier():
    month, year = int(request.args.get('month')), int(request.args.get('year'))
    return jsonify({'data': {'multiplier': _avg_multiplier_from_month(month, year, _draws_df)}})


if __name__ == '__main__':
    _draws_df = _dataframe_from_file()
    app.run(debug=True)
