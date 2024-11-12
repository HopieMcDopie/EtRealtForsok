import pandas as pd
import matplotlib.pyplot as plt

"""
spot prices gathererd from https://newtransparency.entsoe.eu/market/energyPrices on the 12.11.2024
Note that spot prices are in EUR/MWh, conversion to NOK/kWh by 1 EUR = 11.79 NOK (https://www.norges-bank.no/tema/Statistikk/Valutakurser/?tab=currency&id=EUR on the 12.11.2024)
"""


def SpotPrices():
    monthly_spot_price_data  = {}
    hour = [i for i in range(24)]

    for day in range(1,32):

        if len(str(day)) == 1:
            replace = '0'+ str(day)
            filename = 'SpotPriceData\DA_' + replace + '.01.24.csv'
        else:
            replace = str(day)
            filename = 'SpotPriceData\DA_' + replace + '.01.24.csv'

        single_df = pd.read_csv(filename)
        single_spot_price_data = single_df['Day-ahead (EUR/MWh)']*11.79*1000

        if day == 1: 
            for h in hour:
                monthly_spot_price_data[h] = single_spot_price_data[h]
        else:
            last_hour = len(monthly_spot_price_data)
            for h in hour:
                monthly_spot_price_data[last_hour + h] = single_spot_price_data[h]
    return monthly_spot_price_data

if __name__ == '__main__':
    prices = SpotPrices()

    plt.figure()
    plt.plot(prices.values())
    plt.xlabel('hours')
    plt.ylabel('NOK/kWh')
    plt.title('Day-ahead prices for januaray 2024 for NO3')
    plt.show()
