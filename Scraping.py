import json

import requests
from bs4 import BeautifulSoup
import operator
import csv

DATAFILE = "data.json"

#TODO описать класс данных "банк курс"
#TODO динамическая структура на основе списка "ключ"-"описание добычи значения"?

def get_rates_rub():
    page = requests.get("https://rate.am/ru/armenian-dram-exchange-rates/banks/cash?tp=0&rt=0")
    BSPage = BeautifulSoup(page.content, "html.parser")
    trs = BSPage.findAll("tr", id=True) #ищем все строки с id в таблице банков

    banks_list = []

    count = 1
    for tr in trs:
        d = {}
        tdbank = tr.find("td", class_='bank')
        tds = tr.find_all("td")
        #TODO написать функцию заполнения класса "банк курс" из входных данных
        d['Bank ID'] = tr.get("id")
        d['Bank Name'] = tdbank.find("a").get_text()
        d['Bank Link'] = "https://rate.am" + tdbank.find('a', href=True).get('href')
        d['Date'] = tr.find("td", class_="date").get_text()
        d['Rub Buy'] = tds[9].get_text()
        d['Rub Sell'] = tds[10].get_text()
        d['USD Buy'] = tds[5].get_text()
        d['USD Sell'] = tds[6].get_text()
        d['Office Count'] = tds[3].get_text()
        d['Exchange Type'] = 'bank'
        banks_list.append(d)
        count += 1

    return sorted(banks_list, key=operator.itemgetter('Rub Buy'), reverse=True)

def get_rates_exch_pnts():
    page = requests.get("https://rate.am/ru/armenian-dram-exchange-rates/exchange-points/cash")

    BSPage = BeautifulSoup(page.content, "html.parser")
    trs = BSPage.findAll("tr", id=True)  # ищем все строки с id в таблице пунктов обмена

    exch_pnts_list = []

    count = 1
    for tr in trs:
        d = {}
        tdbank = tr.find("td", class_='bank')
        if tdbank is not None:
            d['Bank Name'] = tdbank.find("a").get_text()
            tds = tr.find_all("td")
            d['Bank ID'] = tr.get("id")
            d['Bank Link'] = "https://rate.am" + tdbank.find('a', href=True).get('href')
            d['Date'] = tr.find("td", class_="date").get_text()
            d['Rub Buy'] = tds[9].get_text()
            d['Rub Sell'] = tds[10].get_text()
            d['USD Buy'] = tds[5].get_text()
            d['USD Sell'] = tds[6].get_text()
            d['Office Count'] = tds[3].get_text()
            d['Exchange Type'] = 'exch pnt'
            exch_pnts_list.append(d)
            count += 1
        else:
            print("Дошли до breakline на ", count, " строчке")
            break

    return sorted(exch_pnts_list, key=operator.itemgetter('USD Sell'), reverse=True)

def write_to_csv():
    banks_list = get_rates_rub()
    print(banks_list)
    filename = 'data.csv'
    with open(filename, 'w', newline='') as f:
        w = csv.DictWriter(f, ['Bank Name', 'Bank Link', 'Date', 'Rub Buy'])
        w.writeheader()
        w.writerows(banks_list)

def write_to_json():

    with open(DATAFILE) as f:
        data = json.load(f)
    print("!")
    data["banks_list"] += list(get_rates_rub())
    data["banks_list"] += list(get_rates_exch_pnts())

    with open(DATAFILE, 'w') as f:
        json.dump(data, f)

    #
    # with open(DATAFILE, 'w') as json_file:
    #     data = {"banks_list": get_rates_rub()}
    #     json.dump(data, json_file)
    # print('000')
    # rts = get_rates_exch_pnts()
    # print('111')
    # with open(DATAFILE, 'a') as json_file:
    #     data = {"banks_list": rts}
    #     json.dump(data, json_file)

def read_from_csv():
    write_to_json()
    filename = 'data.csv'
    return open(filename, 'r').read()
