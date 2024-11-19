import matplotlib.pyplot as plt
import pandas as pd

"""
Hentet fra https://www.tensio.no/no/kunde/nettleie/nettleiepriser-september-ts den 12.11.2024
"""

# Creating a dictionary for the energy-part of the grid tariff for one month
def GridTariffEnergy():
    energy = {}
    hour = [i for i in range(24)]
    energy_day = 50.18 # øre/kWh (06-22) at daytime
    energy_night = 35.93 # øre/kWh (22-06) at night

    for h in hour: #create dictionary based on night/day for one day
        if h > 5 and h < 22:
            energy[h] = energy_day
        else:
            energy[h] = energy_night

    for day in range(1,31): #create night/day part of tariff for the entire month
        last_hour = len(energy) #correcting the hours over multiple days
        for h in hour:
            energy[last_hour + h] = energy[h]

    return energy

# Creating a dictionary for the power-part of the grid tariff
def GridTariffPower():
    power = {'0-2': 134, # kr/måned
            '2-5': 239,
            '5-10': 408,
            '10-15': 601,
            '15-20': 794,
            '20-25': 989,
            '25-50': 1699,
            '50-75': 2667,
            '75-100': 3635,
            '100-150': 5250,
            '150-200': 7185,
            '200-300': 10411,
            '300-400': 14288,
            '400-500': 18158,
            '500+': 22032 }
    return power

if __name__ == '__main__':
    test = GridTariffEnergy()
    test_df = pd.DataFrame.from_dict(test, orient='index')