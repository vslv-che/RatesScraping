import json

import requests
from bs4 import BeautifulSoup
import operator
import datetime
import shutil
import os.path

DATAFILE = "data.json"
url_banks = "https://rate.am/ru/armenian-dram-exchange-rates/banks/cash?tp=0&rt=0"
url_exchpts = "https://rate.am/ru/armenian-dram-exchange-rates/exchange-points/cash"

#TODO описать класс данных "банк курс"
#TODO динамическая структура на основе списка "ключ"-"описание добычи значения"?

def get_proper_datetime(date_time): # конвертация временного штампа из формата сайта
    ru_to_eng_months = {'Янв': '01', 'Фев': '02', 'Мар': '03', 'Апр': '04', 'Май': '05',
                        'Июн': '06', 'Июл': '07', 'Авг': '08', 'Сен': '09', 'Окт': '10',
                        'Ноя': '11', 'Дек': '12'}
    for i, j in ru_to_eng_months.items():
        date_time = date_time.replace(i, j)
    try:
        prop_datetime = datetime.datetime.strptime(date_time, "%d %m, %H:%M")
        prop_datetime = prop_datetime.replace(year = datetime.date.today().year)
    except:
        prop_datetime = datetime.datetime.strptime("01/01/1999", "%d/%m/%Y")
        print("Не смогли определить формат временного штампа: ", date_time)

    #time.ctime(seconds) - для вывода datetime
    return prop_datetime.timestamp()

def get_last_rate(data, bank_id): # возвращает последний спарсенный курс по ID банка
    try:
        for rate in reversed(data['rates_list']):
            #print(rate['Bank ID'], ' Date: ', rate['Date'])
            #TODO: Проверить что сравнение идёт в оптимальной последовательности (с конца)
            if bank_id == rate['Bank ID']:
                #print('НАШЛИ! ', rate['Date'])
                return rate
    except:
        pass
    return None

#Сравнивает список курсов с дампом ранее спарсенных курсов и возвращает только новые
def get_only_new_rates(data, rates, time_delta = datetime.timedelta(minutes=30)): # дамп всех курсов из файла, курсы подлежащие отсеиванию, минимальное время с предыдущего парсинга
    new_rates = []
    for rate in rates:
        last_rate = get_last_rate(data, rate['Bank ID'])
        #TODO: Если last_rate == None то вывалится в ошибку
        if last_rate is None:
            print("Нашли курс для нового банка: ", rate['Date'], ". Bank ID: ", rate['Bank ID'])
            new_rates.append(rate)
        elif last_rate['Date'] != rate['Date']:
            if rate['Date']-last_rate['Date'] > time_delta.total_seconds(): # предыдущий курс старше, чем требуется
                print("Нашли новый курс, время: ", rate['Date'], ". Bank ID: ", rate['Bank ID'])
                new_rates.append(rate)
            else:
                print("Предыдущий курс старше всего на ", datetime.timedelta(seconds=(rate['Date']-last_rate['Date'])), ". Bank ID: ", rate['Bank ID'])
        else:
            print("Такой курс уже был, время: ", rate['Date'], ". Bank ID: ", rate['Bank ID'])
    return new_rates

# Парсит курсы с заданных страниц сайта и присваевает им указанный тип организации
def get_rates(url, org_type):
    page = requests.get(url)
    bspage = BeautifulSoup(page.content, "html.parser")
    trs = bspage.findAll("tr", id=True)  # ищем все строки с id в таблице банков
    rates_list = []
    count = 1

    for tr in trs:
        d = {}
        tdbank = tr.find("td", class_='bank')
        if tdbank is not None:
            d['Bank Name'] = tdbank.find("a").get_text()
            tds = tr.find_all("td")
            d['Bank ID'] = tr.get("id")
            d['Bank Link'] = "https://rate.am" + tdbank.find('a', href=True).get('href')
            d['Date'] = get_proper_datetime(tr.find("td", class_="date").get_text())
            d['Rub Buy'] = tds[9].get_text()
            d['Rub Sell'] = tds[10].get_text()
            d['USD Buy'] = tds[5].get_text()
            d['USD Sell'] = tds[6].get_text()
            d['Office Count'] = tds[3].get_text()
            d['Organization Type'] = org_type
            rates_list.append(d)
            count += 1
        else:
            print("Дошли до breakline на ", count, " строчке")
            break

    return sorted(rates_list, key=operator.itemgetter('Date'))

# Загружает json-файл курсов. Создаёт новый файл, если возникают проблемы с интерпретацией, при этом переименовывает старый файл
def load_data_file():
    try:
        with open(DATAFILE) as f:
            data = json.load(f)
        testrate = data['rates_list'][0]
        testBN = testrate['Bank Name']
        #TODO: дополнительные проверки при загрузке файла
    except:
        data = json.loads('{"rates_list": []}')
        if os.path.exists(DATAFILE):
            shutil.copyfile(DATAFILE, "copy_" + DATAFILE)
            print("Файл данных имеет неверный формат. Будет пересохранен как copy_", DATAFILE)
        else:
            print("Файл данных отсутствует. Будет создан новый.")
    return data

def scrap_site():
    data = load_data_file()
    all_bank_rates = get_rates(url_banks, "bank")
    new_bank_rates = get_only_new_rates(data, all_bank_rates)
    print("Спарсили ", len(all_bank_rates), " курсов банков, из них новых: ", len(new_bank_rates))
    data["rates_list"] += new_bank_rates
    all_exch_rates = get_rates(url_exchpts, "exch_pt")
    new_exch_rates = get_only_new_rates(data, all_exch_rates)
    print("Спарсили ", len(all_exch_rates), " курсов обменников, из них новых: ", len(new_exch_rates))
    print(new_exch_rates)
    data["rates_list"] += new_exch_rates

    with open(DATAFILE, 'w') as f:
        json.dump(data, f)



