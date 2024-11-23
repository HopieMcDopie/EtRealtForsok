import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pyomo.environ as pyo



def Store_Results_In_File(m, what2run): #Storing model output values to an excel sheet
    #Creating dataframes from pyomo solution to be used in excel
    results_df = pd.DataFrame({
        'Hour': list(m.T),
        'Price [NOK/kWh]': [m.C_spot[t] for t in m.T],
        'Demand [kW]': [m.D[t] for t in m.T],
        'EV Demand [kW]': [m.D_EV[t] for t in m.T],
        'Battery SOC [kWh]': [m.b[t].value for t in m.T],
        'Charge Power [kW]': [m.e_cha[t].value for t in m.T],
        'Discharge Power [kW]': [m.e_dis[t].value for t in m.T],
        'EV SOC [kWh]': [m.b_EV[t].value for t in m.T],
        'EV Charge Power [kW]': [m.e_EV_cha[t].value for t in m.T],
        'EV Discharge Power [kW]': [m.e_EV_dis[t].value for t in m.T],
        'Power Import [kW]': [m.y_imp[t].value for t in m.T],
        'ENS': [m.ENS[t].value for t in m.T]
    })
    
    
    #Creating an excel sheet for the scenario run
    if what2run == "base":
        file_name = 'Base_Case_Results.xlsx' 

    elif what2run == "spot":
        file_name = 'Spot_Price_Results.xlsx'

    elif what2run == "spot and grid":
        file_name = 'Spot_Grid_Price_Results.xlsx'

    results_df.to_excel(file_name, index = False)
    return ()


def Graphical_Results(m):
    hours = list(m.T)
    price = [m.C_spot[t] for t in m.T]
    demand = [m.D[t] for t in m.T]
    EV_demand = [m.D_EV[t] for t in m.T]
    battery = [m.b[t].value for t in m.T]
    e_cha = [m.e_cha[t].value for t in m.T]
    e_dis = [m.e_dis[t].value for t in m.T]
    EV_battery = [m.b_EV[t].value for t in m.T]
    e_EV_cha = [m.e_EV_cha[t].value for t in m.T]
    e_EV_dis = [m.e_EV_dis[t].value for t in m.T]
    y = [m.y_imp[t].value for t in m.T]
    ENS = [m.ENS[t].value for t in m.T]

    #plotting the demand and imports
    fig1, ax1 = plt.subplots()
    ax1.plot(hours, y, label='Power import', color='tab:red')
    ax1.plot(hours, demand, color ='tab:orange', linestyle = '--', label='House Demand')
    ax1.plot(hours, EV_demand, color = 'tab:grey', linestyle = '--', label = 'EV demand')
    #ax1.plot(hours, ENS, color = 'y', label = 'ENS')
    ax1.axhline(y=0, color= 'k', linestyle = '--')
    ax1.set_xlabel('Hours')
    ax1.set_xticks(hours)
    ax1.set_ylabel('Power [kW]')
    ax1.legend(loc = 'upper left')
    ax1.set_xlim(0,47)
    ax2 = ax1.twinx() #Creates a second y-axis on the right
    ax2.plot(hours, price, label = 'Spotprice', color = 'tab:blue')
    ax2.set_ylabel('Spot Price [NOK/kWh]')
    ax2.legend(loc = 'upper right')
    ax2.set_ylim([0,3])
    fig1.tight_layout()  # Adjust layout to prevent overlapping
    plt.title('Results from Optimization Problem')
    plt.show()


    #plotting the house battery
    fig2, ax1 = plt.subplots()
    ax1.plot(hours, battery, label='State of Charge', color='tab:green')
    ax1.plot(hours, y, label='Power import', color='tab:red')
    ax1.plot(hours, demand, color ='tab:orange', linestyle = '--', label='Demand')
    ax1.bar(hours, e_cha, color = 'green')
    ax1.bar(hours, e_dis, color = 'red')
    ax1.axhline(y=0, color= 'k', linestyle = '--')
    ax1.set_xlabel('Hours')
    ax1.set_xticks(hours)
    ax1.set_ylabel('Power [kW]')
    ax1.legend(loc = 'upper left')
    ax1.set_xlim(0,47)
    ax2 = ax1.twinx() #Creates a second y-axis on the right
    ax2.plot(hours, price, label = 'Spotprice', color = 'tab:blue')
    ax2.set_ylabel('Spot Price [NOK/kWh]')
    ax2.legend(loc = 'upper right')
    ax2.set_ylim([0,3])
    fig2.tight_layout()  # Adjust layout to prevent overlapping
    plt.title('Results from Optimization Problem')
    plt.show()


    #plotting the EV "battery"
    fig3, ax1 = plt.subplots()
    ax1.plot(hours, EV_battery, label='EV "State of Charge"', color='tab:green')
    ax1.plot(hours, y, label='Power import', color='tab:red')
    ax1.plot(hours, EV_demand, color ='tab:orange', linestyle = '--', label='EV Demand')
    ax1.bar(hours, e_EV_cha, color = 'green')
    ax1.bar(hours, e_EV_dis, color = 'red')
    ax1.axhline(y=0, color= 'k', linestyle = '--')
    ax1.set_xlabel('Hours')
    ax1.set_xticks(hours)
    ax1.set_ylabel('Power [kW]')
    ax1.legend(loc = 'upper left')
    ax1.set_xlim(0,743)
    ax2 = ax1.twinx() #Creates a second y-axis on the right
    ax2.plot(hours, price, label = 'Spotprice', color = 'tab:blue')
    ax2.set_ylabel('Spot Price [NOK/kWh]')
    ax2.legend(loc = 'upper right')
    ax2.set_ylim([0,3])
    fig3.tight_layout()  # Adjust layout to prevent overlapping
    plt.title('Results from Optimization Problem')
    plt.show()


