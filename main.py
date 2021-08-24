import requests
import xmltodict
from flask import Flask, request, jsonify
from constants import *

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


def get_currencies_dict(url=URL_CURRENCIES_LIST):
    response = requests.get(url)
    tree = xmltodict.parse(response.content)
    currencies_dict = {}
    for item in tree['Valuta']['Item']:
        currency = {'id': item['@ID'], 'name': item['Name']}
        currencies_dict[item['ISO_Char_Code']] = currency
    return currencies_dict


@app.route('/')
def request_manager():
    params_dict = request.args.to_dict()
    if params_dict == {}:
        return get_currencies_code_name()
    else:
        date_req1 = params_dict['date_req1']
        date_req2 = params_dict['date_req2']
        iso_char_code = params_dict['iso_char_code']
        return get_currencies_difference(date_req1, date_req2, iso_char_code)


def get_currencies_code_name():
    global currencies
    currencies_code_name = []
    for currency_item in currencies.items():
        currencies_code_name.append((currency_item[0], currency_item[1]['name']))
    return jsonify(currencies_code_name, )


def get_currency_value(date, currency_id, url=URL_CURRENCY_DAILY):
    date_split = date.split('-')
    date_req = date_split[2] + '/' + date_split[1] + '/' + date_split[0]
    parameters = {'date_req': date_req}
    response = requests.get(url, params=parameters)
    tree = xmltodict.parse(response.content)
    valutes = tree['ValCurs']['Valute']
    valute_value = None
    for valute in valutes:
        if valute['@ID'] == currency_id:
            valute_value = valute['Value'].replace(',', '.')
            valute_value = float(valute_value)
            break
    return valute_value


def get_currencies_difference(date_req1, date_req2, iso_char_code):
    global currencies
    value1 = get_currency_value(date_req1, currencies[iso_char_code]['id'])
    value2 = get_currency_value(date_req2, currencies[iso_char_code]['id'])
    if value1 is None or value2 is None:
        value_diff = None
    else:
        value_diff = round(value2 - value1, 4)
    return jsonify(value1, value2, value_diff)


currencies = get_currencies_dict()

if __name__ == '__main__':
    app.run()
