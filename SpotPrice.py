import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

"""
spot prices gathererd from https://newtransparency.entsoe.eu/market/energyPrices on the 12.11.2024
Note that spot prices are in EUR/MWh, conversion to NOK/kWh by 1 EUR = 11.79 NOK (https://www.norges-bank.no/tema/Statistikk/Valutakurser/?tab=currency&id=EUR on the 12.11.2024)
"""


def SpotPrices(): #create dictionary of spot prices in usable format
    monthly_spot_price_data  = {}
    hour = [i for i in range(24)]

    for day in range(1,32):
        if len(str(day)) == 1:
            replace = '0'+ str(day) #Create unified filename format 
            filename = 'SpotPriceData\DA_' + replace + '.01.24.csv'
        else:
            replace = str(day)
            filename = 'SpotPriceData\DA_' + replace + '.01.24.csv'#Create unified filename format 

        single_df = pd.read_csv(filename)
        single_spot_price_data = single_df['Day-ahead (EUR/MWh)']*11.79/1000  #NOK/kWh

        if day == 1: 
            for h in hour: #Go through all hours on day 1
                monthly_spot_price_data[h] = single_spot_price_data[h]
        else:
            last_hour = len(monthly_spot_price_data) #adjust hour numbering based on days iterated already
            for h in hour:
                monthly_spot_price_data[last_hour + h] = single_spot_price_data[h]
    return monthly_spot_price_data

if __name__ == '__main__':
    prices = SpotPrices()

    plt.figure()
    plt.step(range(744), prices.values())
    plt.xticks([i for i in range(0,744,24)], [f'{i}' for i in range(1,32)])
    plt.xlabel('Days', fontsize=12, fontweight='bold', family='serif')
    plt.ylabel('Price [NOK/kWh]', fontsize=12, fontweight='bold', family='serif')
    plt.title('Day-Ahead Prices for January 2024 for NO3', fontsize=18, fontweight='bold', family='serif')
    plt.xlim(0,743)
    plt.tight_layout()
    plt.grid('on')
    

    prices_list = list(prices.values())
    print(max(prices_list))
    daily_prices = [prices_list[i:i+24] for i in range(0, len(prices_list), 24)]
    daily_prices.pop(4)
    hourly_prices = zip(*daily_prices)
    hourly_prices = list(hourly_prices)
    mean_prices = np.array([sum(hourly_prices[i]) for i in range(len(hourly_prices))])/len(hourly_prices)
    std_prices = np.array([stats.tstd(hourly_prices[i]) for i in range(len(hourly_prices))])

    top = mean_prices + std_prices
    bottom = mean_prices - std_prices

    plt.figure()
    plt.step(range(24), mean_prices, linewidth = 2)
    plt.fill_between(range(24), top, bottom, step = 'pre', alpha = 0.2)
    plt.xlabel('Hours', fontsize=12, fontweight='bold', family='serif')
    plt.ylabel('Price [NOK/kWh]', fontsize=12, fontweight='bold', family='serif')
    plt.title('Average hourly prices with standard deviation for January 2024 for NO3', fontsize=18, fontweight='bold', family='serif')
    plt.xticks(range(24))
    plt.xlim(0,23)
    plt.tight_layout()
    plt.grid('on')
    plt.show()
