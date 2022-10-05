import Scraping
import csv

banks_list = Scraping.get_rates_rub()
print(banks_list)
filename = 'data.csv'
with open(filename, 'w', newline='') as f:
    w = csv.DictWriter(f, ['Bank Name', 'Bank Link', 'Date', 'Rub Buy'])
    w.writeheader()
    w.writerows(banks_list)
