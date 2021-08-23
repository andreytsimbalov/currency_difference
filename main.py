# currency_difference

# 1)Курс валют брать с http://www.cbr.ru/development/sxml/
# 2)Микросервис должен содержать два метода
# A) получение списка валют, который должен возвращать все валюты, которые можно использовать
# (символьный код (RUB, EUR), название).
# Список можно взять здесь http://www.cbr.ru/scripts/XML_valFull.asp
# B)Получение разницы курса относительно рубля между двумя датами за выбранную дату,
# метод должен принимать символьный код валюты, и две даты. Возвращать метод должен курс за первую дату,
# курс за вторую дату и разницу между ними.
# 3)Даты должны передаваться в следующем формате YYYY-MM-DD
# 4)Технологии для решения задачи можно выбрать на свой вкус.
# 5)Задание расположить в удалённом репозитории и отправить ссылку на него.
# В репозитории должен быть файл readme.md в котором должно быть описание проделанной работы, в котором указать,
# какие технологии использовались и с какой целью, и примеры вызовов методов.


import requests
import xmltodict
import numpy as np
import xml.etree.ElementTree as ElementTree

URL_CURRENCIES_LIST = "http://www.cbr.ru/scripts/XML_valFull.asp"

URL_CURRENCY_DYNAMIC = 'https://www.cbr.ru/scripts/XML_dynamic.asp'

# https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=02/03/2001&date_req2=02/03/2001&VAL_NM_RQ=R01235
# http://www.cbr.ru/scripts/XML_daily.asp?date_req=02/03/2002

# url_list_of_currencies = "https://www.cbr.ru/scripts/XML_daily.asp?date_req=21/08/2021"
# url_list_of_currencies = "https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=02/03/2001&date_req2=02/03/2001&VAL_NM_RQ=R01235"
url_list_of_currencies = 'https://www.cbr.ru/scripts/XML_dynamic.asp'


def get_currencies(url=URL_CURRENCIES_LIST):
    response = requests.get(url)
    tree = xmltodict.parse(response.content)
    currencies_dict = {}
    for item in tree['Valuta']['Item']:
        currency = {'id': item['@ID'], 'name': item['Name']}
        currencies_dict[item['ISO_Char_Code']] = currency
    return currencies_dict


currencies = get_currencies()


def get_currency_value(date, currency_id, url=URL_CURRENCY_DYNAMIC):
    date_split = date.split('-')
    date_req = date_split[2] + '/' + date_split[1] + '/' + date_split[0]
    parameters = {
        'date_req1': date_req,
        'date_req2': date_req,
        'VAL_NM_RQ': currency_id
    }
    response = requests.get(url, params=parameters)
    tree = xmltodict.parse(response.content)
    value_str = tree['ValCurs']['Record']['Value'].replace(',', '.')
    return float(value_str)


def get_currencies_difference(date_req1, date_req2, iso_char_code):
    global currencies
    val1 = get_currency_value(date_req1, currencies[iso_char_code]['id'])
    val2 = get_currency_value(date_req2, currencies[iso_char_code]['id'])
    return val2 - val1


# print(currencies['AUD']['Name'])
# print(currencies)

date1 = '2002-04-02'
date2 = '2002-03-02'
id = 'R01235'

# val = get_currency_value(date, id)
# print(val)

val = get_currencies_difference(date1, date2, list(currencies.keys())[0])
print(val)

# print(currencies)


# if __name__ == '__main__':
#     main()
