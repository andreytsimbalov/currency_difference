from sqlalchemy import create_engine, Sequence, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
import sqlalchemy
import datetime as dt
from datetime import datetime, date

import requests
import xmltodict
from constants import *
import os

# if os.path.exists(DATABASE):
#     os.remove(DATABASE)
engine = create_engine('sqlite:///' + DATABASE, echo=True)
Base = declarative_base()


class Currency(Base):
    __tablename__ = 'currency'
    currency_id = Column(String(50), primary_key=True)
    code = Column(String(50))
    name = Column(String(50))

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


class Value(Base):
    __tablename__ = 'value'
    id = Column(Integer, Sequence('value_id_seq'), primary_key=True)
    currency_id = Column(String(50), ForeignKey("currency.currency_id"))  # , ForeignKey("currency.currency_id")
    date = Column(DateTime)
    value = Column(Float)

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


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()
session.commit()


def generate_currency_table(url=URL_CURRENCIES_LIST):
    response = requests.get(url)
    tree = xmltodict.parse(response.content)
    for item in tree['Valuta']['Item']:
        if item['ISO_Char_Code'] != None:
            currency = Currency(item['@ID'], item['ISO_Char_Code'], item['Name'])
            session.add(currency)

    session.commit()


# generate_currency_table()
print(session.query(Currency).all())


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
            session.add(value)
        session.commit()
    else:
        print(cur_code, 'has not values for period')


# add_to_value_table_for_period(currency.currency_id)
# add_to_value_table_for_period('R01510A')


# print(session.query(Value).all()[:5])

def generate_value_table_for_period(
        date_req1='01/01/2000',
        date_req2=date.today().strftime("%d/%m/%Y"),
        url=URL_CURRENCY_DYNAMIC):
    for currency in session.query(Currency).all():
        print(currency.currency_id)
        add_to_value_table_for_period(currency.currency_id, date_req1, date_req2, url)


# generate_value_table_for_period()
# print(len(session.query(Value).all()))
# print(session.query(Value).all()[:10])

# <Values(1, 'R01010', 2000-01-01 00:00:00, 17.63>,
# <Values(1, 'R01010', 2000-01-06 00:00:00, 17.63>,


def get_currency_value(currency_id, cur_req, url=URL_CURRENCY_DAILY):
    value = session.query(Value).filter(Value.currency_id == currency_id).filter(Value.date == cur_req).all()
    if value==[]:
        print('==find internet')
        date_req = cur_req.strftime("%d/%m/%Y")
        parameters = {'date_req': date_req}
        response = requests.get(url, params=parameters)
        tree = xmltodict.parse(response.content)
        valutes = tree['ValCurs']['Valute']
        valute_value = None
        for valute in valutes:
            if valute['@ID'] == currency_id:
                valute_value = valute['Value'].replace(',', '.')
                valute_value = float(valute_value)

                value = Value(currency_id, cur_req, valute_value)
                session.add(value)
                session.commit()
                break
        value = valute_value
    else:
        value = value[0].value
    return value

qwe = get_currency_value('R01010', datetime(2000,1,3))

print(date(2000,1,1))
qwe = session.query(Value).filter(Value.currency_id == 'R01010').filter(Value.date <= datetime(2000,1,6)).all()
print(qwe)



# currency = Currency('3', 'ddd', '123')
# session.add(currency)
# session.commit()
#
# # print(session.query(Currency).all())
# # print(session.query(Value).all())
#
# date_string = "2012-12-12 10:10:10"
# date_string = "2012-12-20"
# dt = datetime.fromisoformat(date_string)
# print(dt)
#
# currency = Value('21', dt, 4.5)
# session.add(currency)
# session.commit()
#
# print('______')
# print(session.query(Currency).all())
# print(session.query(Value).all())
