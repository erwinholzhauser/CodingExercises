# Start solution here

import os

import pandas as pd

_BASE_DIR = os.path.dirname(__file__)
_INPUT_DIR = os.path.join(_BASE_DIR, 'Input/')
_OUTPUT_DIR = os.path.join(_BASE_DIR, 'Output/')


class DataSource:
    def __init__(self, id, dir_name):
        self.id = id
        self.dir = os.path.join(_INPUT_DIR, dir_name + '/')


class InputFile:
    def __init__(self, filename, data_source, sep=','):
        self.data_source = data_source
        self.path = os.path.join(data_source.dir, filename)
        self.sep = sep


def consolidate_data(input_files, output_filename):
    input_dfs = []
    for input_file in input_files:
        input_dfs.append(pd.read_csv(
            filepath_or_buffer=input_file.path, sep=input_file.sep))
        input_dfs[-1]['data_source'] = [input_file.data_source.id] * \
            input_dfs[-1].shape[0]

    if not os.path.exists(_OUTPUT_DIR):
        os.makedirs(_OUTPUT_DIR)

    pd.concat(input_dfs).to_csv(path_or_buf=os.path.join(
        _OUTPUT_DIR, output_filename), index=False)


if __name__ == "__main__":

    data_source_1 = DataSource(id=1, dir_name='data_source_1')
    data_source_2 = DataSource(id=2, dir_name='data_source_2')

    input_files = [
        InputFile(filename='sample_data.1.csv', data_source=data_source_1),
        InputFile(filename='sample_data.2.dat',
                  data_source=data_source_1, sep='|'),
        InputFile(filename='sample_data.3.dat', data_source=data_source_2)
    ]

    consolidate_data(input_files=input_files,
                     output_filename='consolidated_output.1.csv')
