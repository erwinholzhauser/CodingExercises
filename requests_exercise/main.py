# Start solution here

import requests
from pprint import pprint
import os
import pandas as pd
import time
import numpy as np

_BASE_DIR = os.path.dirname(__file__)


def get_currency_name(currency_code):
    data = requests.get(
        url="https://api.coinbase.com/v2/currencies"
    ).json()['data']

    for currency in data:
        if currency['id'] == currency_code:
            return (currency['name'], currency['id'])

    return (None, currency['id'])


def currency_exchange_data_to_file(base_currency_code):
    base_currency_code = base_currency_code.upper()
    currencies_data = requests.get(
        url="https://api.coinbase.com/v2/currencies").json()['data']

    currency_name_map = {}
    for currency_record in currencies_data:
        currency_name_map[currency_record['id']] = currency_record['name']

    # As of 7/23/2022, it appears that the currencies endpoint only includes
    # fiat currencies. (Even though the custom currency code ‘BTC’ is mentioned
    # in its documentation, no record with ‘id’=’BTC’ is returned.) However, the
    # exchanges endpoint does respond as expected to cryptocurrency codes. So,
    # we’ll set the base currency name as its currency code if the exchanges
    # endpoint responds to the currency code but its name isn't found from the
    # currencies endpoint.

    base_currency_name = currency_name_map[base_currency_code] \
        if base_currency_code in currency_name_map else base_currency_code

    exchanges_data = requests.get(
        url="https://api.coinbase.com/v2/exchange-rates",
        params={'currency': base_currency_code}
    ).json()

    if 'errors' in exchanges_data:
        raise ValueError(exchanges_data['errors'][0]['message'])

    rates, records = exchanges_data['data']['rates'], []
    for currency_code in rates:
        currency_name = currency_name_map[currency_code] \
            if currency_code in currency_name_map else currency_code
        records.append({
            'base_currency_code': base_currency_code,
            'base_currency': base_currency_name,
            'currency_code': currency_code,
            'currency': currency_name,
            'exchange_rate': float(rates[currency_code])
        })

    df = pd.DataFrame.from_records(records)

    filename = f'{base_currency_name}-exchange_output.{time.time()}.csv'
    df.to_csv(path_or_buf=os.path.join(_BASE_DIR, filename), index=False)


if __name__ == "__main__":
    pass
