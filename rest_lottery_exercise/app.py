import csv
import datetime
import os
from pprint import pprint

from flask import Flask, jsonify, request

app = Flask(__name__)
_draws_list = []


def _populate_draws_list():
    input_file = os.path.join(os.path.dirname(
        __file__), 'input/powerball_winning_numbers.csv')
    with open(input_file) as csv_file:
        reader = csv.DictReader(csv_file)
        for draw in reader:
            draw['draw_date'] = draw.pop('Draw Date').split('/')
            draw['draw_date'] = datetime.datetime(
                *[int(draw['draw_date'][i]) for i in [2, 0, 1]])

            draw['multiplier'] = draw.pop('Multiplier')
            draw['multiplier'] = 1.0 if draw['multiplier'] == '' else float(
                draw['multiplier'])

            draw['winning_numbers'] = [
                int(i) for i in draw.pop('Winning Numbers').split(' ')]

            # pprint(draw)
            _draws_list.append(draw)


def _get_winning_nums_from_date(start, end=None, draws=_draws_list):
    start_split = start.split('/')
    start_dt = datetime.datetime(*[int(start_split[i]) for i in [2, 0, 1]])

    if end is None:
        end_dt = start_dt
    else:
        end_split = end.split('/')
        end_dt = datetime.datetime(*[int(end_split[i]) for i in [2, 0, 1]])

    return [i['winning_numbers'] for i in draws
            if i['draw_date'] >= start_dt and i['draw_date'] <= end_dt]


def _get_draws_from_multiplier(mult, draws=_draws_list):
    return [i for i in draws if i['multiplier'] == mult]


@app.route('/draw/', methods=['GET'])
def get_draws():
    pass


if __name__ == '__main__':
    _populate_draws_list()
    # pprint(_get_winning_nums_from_date(start='09/26/2020', end='10/03/2020'))
    # pprint(_get_draws_from_multiplier(10))
    # app.run(debug=True)
    pass
