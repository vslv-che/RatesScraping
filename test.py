import Scraping


#Scraping.write_to_json()
rates = Scraping.scrap_site()
#Scraping.get_proper_datetime("11 Окт, 20:00")
#print("!")


#рисуем график
#import pandas
#pandas.Series([offer["Price Info"]["USD"] for offer in offers]).plot() #или .hist()