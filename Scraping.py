import requests
from bs4 import BeautifulSoup
import operator

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
        #TODO написать функцию заполнения класса "банк курс" из входных данных
        d['Bank Name'] = tdbank.find("a").get_text()
        d['Bank Link'] = "https://rate.am" + tdbank.find('a', href=True).get('href')
        d['Date'] = tr.find("td", class_="date").get_text()
        d['Rub Buy'] = tr.find_all("td").pop(9).get_text()
        banks_list.append(d)
        count += 1

    return sorted(banks_list, key=operator.itemgetter('Rub Buy'), reverse=True)
