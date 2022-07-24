# Start solution here

import os
import time
from pprint import pprint

import numpy as np
import pandas as pd
import requests

_BASE_DIR = os.path.dirname(__file__)


def get_currency_name(currency_code):
    data = requests.get(
        url="https://api.coinbase.com/v2/currencies"
    ).json()['data']

    for currency in data:
        if currency['id'] == currency_code:
            return (currency['name'], currency['id'])

    return (None, currency_code)


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
    return filename


def get_btc_trade_price(currency_code, trade_type):
    currency_code, trade_type = currency_code.upper(), trade_type.lower()
    if trade_type not in {'buy', 'sell', 'spot'}:
        raise ValueError('The trade type must be "buy", "sell", or "spot".')

    price_data = requests.get(
        f'https://api.coinbase.com/v2/prices/BTC-{currency_code}/{trade_type}').json()

    if 'errors' in price_data:
        raise ValueError(price_data['errors'][0]['message'])

    return float(price_data['data']['amount'])


if __name__ == "__main__":

    command = -1
    while command != 0:

        print("MENU\n"
              "1) Get currency name from currency code.\n"
              "2) Generate CSV of exchange rates relative to a specified currency.\n"
              "3) Get bitcoin buy, sell, or spot price.\n"
              "0) Exit.")
        command = float(input("Choose an option: "))

        if command == 1:
            currency_code = input("\nEnter a currency code (e.g. USD): ")
            currency_name, currency_code = get_currency_name(currency_code)
            if currency_name is not None:
                print(
                    f"The currency name for {currency_code} is {currency_name}.\n")
            else:
                print(f"Sorry, the currency code {currency_code} is either invalid, "
                      "or we can't find a name for it.\n")

        elif command == 2:
            base_currency_code = input(
                "\nEnter a base currency code (e.g. BTC): ")
            filename = currency_exchange_data_to_file(base_currency_code)
            print(f"The currency exchange rates relative to {base_currency_code} "
                  f"have been output to {filename}.\n")

        elif command == 3:
            currency_code = input(
                "\nEnter the target currency code (e.g. USD): ").upper()

            trade_type, trade_type_map = -1, {1: "buy", 2: "sell", 3: "spot"}
            while trade_type not in trade_type_map:
                print("\n1) Buy\n2) Sell\n3) Spot")
                trade_type = float(input("Choose an option: "))
            trade_type = trade_type_map[trade_type]

            print(f"\nThe {trade_type} price of 1 BTC is "
                  f"{get_btc_trade_price(currency_code, trade_type)} "
                  f"{currency_code}.\n")

        elif command == 0:
            break

        else:
            print("\nInvalid option.\n")
