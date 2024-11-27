import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""

Note: data is in kW
Data from Kasper, originally from "Analysis of residential EV energy flexibility potential based on real-world charging reports and smart meter data"

"""

#plt.rcParams.update({
    #"text.usetex": False,            # Use LaTeX for text rendering
    #"font.family": "serif",         # Use a serif font
    #"font.serif": ["Computer Modern"],  # Use Computer Modern, the default LaTeX font
    #"axes.labelsize": 14,           # Font size for axis labels
    #"font.size": 14,                # General font size
    #"legend.fontsize": 12,           # Font size for legend
    #"xtick.labelsize": 12,           # Font size for x-tick labels
    #"ytick.labelsize": 12,           # Font size for y-tick labels})


def ReadEVData(share_of_CP = float, no_of_EVs = int): #Read EV data an create useable format
    share_of_SP = 1 - share_of_CP

    #Read the data file
    data = pd.read_excel('EV_load_VERY_IMPORTANT_FILE.xlsx', sheet_name = 'Sheet2')

    #Extract the necessary data
    timestamps = data.iloc[0:24,2] # if needed
    CP_week = {'Available': data.iloc[0:24,3], 'Charging': data.iloc[0:24,4]}
    CP_end = {'Available': data.iloc[0:24,9], 'Charging': data.iloc[0:24,10]}
    SP_week = {'Available': data.iloc[0:24,13], 'Charging': data.iloc[0:24,14]}
    SP_end = {'Available': data.iloc[0:24,17], 'Charging': data.iloc[0:24,18]}

    #Create shared data
    week = {}
    end = {}
    for key in CP_week.keys():
        temp_week = []
        temp_end = []
        for i in range(len(CP_week[key])):
            temp_week.append((share_of_CP*CP_week[key][i] + share_of_SP*SP_week[key][i])*no_of_EVs)
            temp_end.append((share_of_CP*CP_end[key][i] + share_of_SP*SP_end[key][i])*no_of_EVs)
        week[key] = temp_week
        end[key] = temp_end

    #Creating monthly data
    days_in_month = 31

    # Generate the repeating pattern for the month (5 weekdays + 2 weekends)
    pattern = np.array([0] * 5 + [1] * 2)  # 0 for weekdays, 1 for weekends
    pattern = np.tile(pattern, days_in_month // 7 + 1)[:days_in_month]  # Repeat and slice to fit the month

    month = {'Available': [], 'Charging': []}
    for day in pattern: 
        if day == 0:
            month['Available'].extend(week['Available'])
            month['Charging'].extend(week['Charging'])
        else:
            month['Available'].extend(end['Available'])
            month['Charging'].extend(end['Charging'])

    for hour in range(len(month['Available'])):
        month['Available'][hour] = month['Available'][hour] + month['Charging'][hour]

    month_df = pd.DataFrame(month)

    # plt.figure()
    # plt.plot(month_df['Available'][0:24], label = 'Available')
    # plt.plot(month_df['Charging'][0:24], label = 'Charging')
    # plt.legend()
    # plt.xlabel('hours')
    # plt.ylabel('kW')
    # plt.title(f'Available capacity and charging load of {no_of_EVs} EVs')
    # plt.show()

    return month_df

def FindMonthlyChargeEnergy(data = pd.DataFrame): #Amount of energy used in one month for EV charging
    monthly_energy_use = 0
    for i in data['Charging']:
        monthly_energy_use += i
    return monthly_energy_use



if __name__ == '__main__':

    share_of_CP = 0.4
    no_of_EVs = 25 #Number of EVs

    df = ReadEVData(share_of_CP = share_of_CP, no_of_EVs=no_of_EVs)
