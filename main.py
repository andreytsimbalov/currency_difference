import requests
import xmltodict
import os
from flask import Flask, request, jsonify
from constants import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

generate_currency_flag = False
if not os.path.exists(DATABASE):
    generate_currency_flag = True

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE
db = SQLAlchemy(app)


class Currency(db.Model):
    __tablename__ = 'currency'
    currency_id = db.Column(db.String(50), primary_key=True)
    code = db.Column(db.String(50))
    name = db.Column(db.String(50))

    def __init__(self, currency_id, code, name):
        self.currency_id = currency_id
        self.code = code
        self.name = name

    def __repr__(self):
        return "\n<Currency('%s', '%s', '%s'>" % (
            self.currency_id,
            self.code,
            self.name
        )


class Value(db.Model):
    __tablename__ = 'value'
    id = db.Column(db.Integer, db.Sequence('value_id_seq'), primary_key=True)
    currency_id = db.Column(db.String(50),
                            db.ForeignKey("currency.currency_id"))  # , ForeignKey("currency.currency_id")
    date = db.Column(db.DateTime)
    value = db.Column(db.Float)

    def __init__(self, currency_id, date, value):
        self.currency_id = currency_id
        self.date = date
        self.value = value

    def __repr__(self):
        return "\n<Values(%s, '%s', %s, %s>" % (
            self.id,
            self.currency_id,
            self.date,
            self.value
        )


db.create_all()


def generate_currency_table(url=URL_CURRENCIES_LIST):
    response = requests.get(url)
    tree = xmltodict.parse(response.content)
    for item in tree['Valuta']['Item']:
        if item['ISO_Char_Code'] != None:
            currency = Currency(item['@ID'], item['ISO_Char_Code'], item['Name'])
            db.session.add(currency)
    db.session.commit()


def get_currency_code_names():
    currencies = []
    for currency in Currency.query.all():
        currencies.append((currency.code, currency.name))
    return currencies


def add_to_value_table_for_period(
        cur_code,
        date_req1='01/01/2000',
        date_req2=date.today().strftime("%d/%m/%Y"),
        url=URL_CURRENCY_DYNAMIC):
    parameters = {
        'date_req1': date_req1,
        'date_req2': date_req2,
        'VAL_NM_RQ': cur_code,
    }
    response = requests.get(url, params=parameters)
    tree = xmltodict.parse(response.content)
    if 'Record' in tree['ValCurs']:
        for record in tree['ValCurs']['Record']:
            cur_date = datetime.strptime(record['@Date'], '%d.%m.%Y')
            cur_value = record['Value'].replace(',', '.')
            cur_value = float(cur_value)
            value = Value(cur_code, cur_date, cur_value)
            db.session.add(value)
        db.session.commit()
    else:
        print(cur_code, 'has not values for period')


def generate_value_table_for_period(
        date_req1='01/01/2000',
        date_req2=date.today().strftime("%d/%m/%Y"),
        url=URL_CURRENCY_DYNAMIC):
    for currency in Currency.query.all():
        print(currency.currency_id)
        add_to_value_table_for_period(currency.currency_id, date_req1, date_req2, url)


def get_currency_value(currency_id, cur_req, url=URL_CURRENCY_DAILY):
    value = Value.query.filter_by(currency_id=currency_id).filter_by(date=cur_req).first()
    if value == None:
        date_req = cur_req.strftime("%d/%m/%Y")
        parameters = {'date_req': date_req}
        response = requests.get(url, params=parameters)
        tree = xmltodict.parse(response.content)
        valute_value = None
        if 'Valute' in tree['ValCurs']:
            valutes = tree['ValCurs']['Valute']
            for valute in valutes:
                if valute['@ID'] == currency_id:
                    valute_value = valute['Value'].replace(',', '.')
                    valute_value = float(valute_value)

                    value = Value(currency_id, cur_req, valute_value)
                    db.session.add(value)
                    db.session.commit()
                    break
        value = valute_value
    else:
        value = value.value
    return value


def get_currencies_difference(iso_char_code, date_req1, date_req2):
    currency_id = Currency.query.filter_by(code=iso_char_code).first().currency_id
    value1 = get_currency_value(currency_id, date_req1)
    value2 = get_currency_value(currency_id, date_req2)
    if value1 is None or value2 is None:
        value_diff = None
    else:
        value_diff = round(value2 - value1, 4)
    return value1, value2, value_diff


@app.route('/')
def request_manager():
    params_dict = request.args.to_dict()
    if params_dict == {}:
        return jsonify(get_currency_code_names())
    else:
        try:
            date_req1 = datetime.strptime(params_dict['date_req1'], '%Y-%m-%d')
            date_req2 = datetime.strptime(params_dict['date_req2'], '%Y-%m-%d')
        except ValueError:
            return 'Error date format. Use YYYY-MM-DD'
        iso_char_code = params_dict['iso_char_code']
        return jsonify(get_currencies_difference(iso_char_code, date_req1, date_req2))


if __name__ == '__main__':
    if generate_currency_flag:
        generate_currency_table()
        generate_value_table_for_period()
    app.run()
