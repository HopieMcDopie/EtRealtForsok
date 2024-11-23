import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



def Store_Results_In_File(m, what2run): #Storing model output values to an excel sheet
    hours = []
    demand = []
    EV_demand = []
    price = []
    battery = []
    e_cha = []
    e_dis = []
    EV_battery = []
    e_EV_cha = []
    e_EV_dis = []
    y = []
    y_house = []
    y_EV = []
    ENS = []

    for t in m.T:
        hours.append(t)
        price.append(m.C_spot[t])
        demand.append(m.D[t])
        EV_demand.append(m.D_EV[t])
        battery.append(m.b[t].value)
        e_cha.append(m.e_cha[t].value)
        e_dis.append(m.e_dis[t].value)
        EV_battery.append(m.b_EV[t].value)
        e_EV_cha.append(m.e_EV_cha[t].value)
        e_EV_dis.append(m.e_EV_dis[t].value)
        y.append(m.y_imp[t].value)
        y_house.append(m.y_house[t].value)
        y_EV.append(m.y_EV[t].value)
        ENS.append(m.ENS[t].value)
    
    #Naming excel-sheet variable based on the scenario
    if what2run == "base": 
        base_results_file = pd.concat([], axis=1)    

    elif what2run == "spot":
        spot_results_file = pd.concat([], axis=1)

    elif what2run == "spot and grid":
        spot_and_grid_results_file = pd.concat([], axis=1)

    #Collecting the various sheets into one file
    with pd.ExcelWriter('output.xlsx', engine='xlsxwriter') as writer: # Write to Excel with multiple sheets
        base_results_file.to_excel(writer, sheet_name = 'Base') 
        spot_results_file.to_excel(writer, sheet_name = 'Spot')
        spot_and_grid_results_file.to_excel(writer, sheet_name = 'Spot & Grid')
    return ()


def Graphical_Results(m):
    hours = []
    demand = []
    EV_demand = []
    price = []
    battery = []
    e_cha = []
    e_dis = []
    EV_battery = []
    e_EV_cha = []
    e_EV_dis = []
    y = []
    y_house = []
    y_EV = []
    ENS = []

    for t in m.T:
        hours.append(t)
        price.append(m.C_spot[t])
        demand.append(m.D[t])
        EV_demand.append(m.D_EV[t])
        battery.append(m.b[t].value)
        e_cha.append(m.e_cha[t].value)
        e_dis.append(m.e_dis[t].value)
        EV_battery.append(m.b_EV[t].value)
        e_EV_cha.append(m.e_EV_cha[t].value)
        e_EV_dis.append(m.e_EV_dis[t].value)
        y.append(m.y_imp[t].value)
        y_house.append(m.y_house[t].value)
        y_EV.append(m.y_EV[t].value)
        ENS.append(m.ENS[t].value)

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


