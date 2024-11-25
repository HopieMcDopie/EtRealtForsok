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
    if what2run == "1":
        file_name = 'Base_Case_Results.xlsx' 

    elif what2run == "2":
        file_name = 'Spot_Price_Results.xlsx'

    elif what2run == "3":
        file_name = 'Spot_Grid_Price_Results.xlsx'

    results_df.to_excel(file_name, index = False)
    return ()


def Graphical_Results(m):
    hours = list(m.T)
    price = np.array([m.C_spot[t] for t in m.T])
    y = np.array([m.y_imp[t].value for t in m.T])
    y_house = np.array([m.y_house[t].value for t in m.T])
    demand = np.array([m.D[t] for t in m.T])
    EV_demand = np.array([m.D_EV[t] for t in m.T])
    battery = np.array([m.b[t].value for t in m.T])
    e_cha = np.array([m.e_cha[t].value for t in m.T])
    e_dis = np.array([m.e_dis[t].value for t in m.T])
    EV_battery = np.array([m.b_EV[t].value for t in m.T])
    e_EV_cha = np.array([m.e_EV_cha[t].value for t in m.T])
    e_EV_dis = np.array([m.e_EV_dis[t].value for t in m.T])
    ENS = np.array([m.ENS[t].value for t in m.T])
    """
#THE FIRST PLOT
    #plotting the demand and imports
    fig1, ax1 = plt.subplots()
    ax1.plot(hours, y, label='Power import', color='tab:red')
    ax1.plot(hours, demand, color ='tab:orange', linestyle = '--', label='Household demand')
    ax1.plot(hours, EV_demand, color = 'tab:grey', linestyle = '--', label = 'EV demand')
    #ax1.plot(hours, ENS, color = 'y', label = 'ENS')
    ax1.axhline(y=0, color= 'k', linestyle = '--')
    ax1.set_xlabel('Hours')
    ax1.set_xticks(hours[::3])  # Reducing ticks for better readability
    ax1.set_ylabel('Power [kW]')
    ax1.legend(loc = 'upper left')
    ax1.set_xlim(0,47)
    ax2 = ax1.twinx() #Creates a second y-axis on the right
    ax2.plot(hours, price, label = 'Spotprice', color = 'tab:blue')
    ax2.set_ylabel('Spot Price [NOK/kWh]')
    ax2.legend(loc = 'upper right')
    ax2.set_ylim([0,3])
    fig1.tight_layout()  # Adjust layout to prevent overlapping
    plt.title('Demand and Imports')
    #plt.show()


#THE SECOND PLOT
    #plotting the community battery
    fig2, ax1 = plt.subplots()
    ax1.plot(hours, battery, label='State of Charge', color='tab:green')
    ax1.plot(hours, y, label='Power import', color='tab:red')
    ax1.plot(hours, demand, color ='tab:orange', linestyle = '--', label='Household demand')
    ax1.bar(hours, e_cha, color = 'green')
    ax1.bar(hours, e_dis, color = 'red')
    ax1.axhline(y=0, color= 'k', linestyle = '--')
    ax1.set_xlabel('Hours')
    ax1.set_xticks(hours[::3])  # Reducing ticks for better readability
    ax1.set_ylabel('Power [kW]')
    ax1.legend(loc = 'upper left')
    ax1.set_xlim(0,47)
    ax2 = ax1.twinx() #Creates a second y-axis on the right
    ax2.plot(hours, price, label = 'Spotprice', color = 'tab:blue')
    ax2.set_ylabel('Spot Price [NOK/kWh]')
    ax2.legend(loc = 'upper right')
    ax2.set_ylim([0,1.2])
    fig2.tight_layout()  # Adjust layout to prevent overlapping
    plt.title('The Community Battery')
    #plt.show()

#THE THIRD PLOT
    #plotting the EV "battery"
    fig3, ax1 = plt.subplots()
    ax1.plot(hours, EV_battery, label='EV "SoC"', color='tab:green')
    ax1.plot(hours, y, label='Power import', color='tab:red')
    ax1.plot(hours, EV_demand, color ='tab:gray', linestyle = '--', label='EV Demand')
    ax1.bar(hours, e_EV_cha, color = 'green')
    ax1.bar(hours, e_EV_dis, color = 'red')
    ax1.axhline(y=0, color= 'k', linestyle = '--')
    ax1.set_xlabel('Hours')
    ax1.set_xticks(hours[::3])  # Reducing ticks for better readability
    ax1.set_ylabel('Power [kW]')
    ax1.legend(loc = 'upper left')
    ax1.set_xlim(0,47)
    ax2 = ax1.twinx() #Creates a second y-axis on the right
    ax2.plot(hours, price, label = 'Spotprice', color = 'tab:blue')
    ax2.set_ylabel('Spot Price [NOK/kWh]')
    ax2.legend(loc = 'upper right')
    ax2.set_ylim([0,3])
    fig3.tight_layout()  # Adjust layout to prevent overlapping
    plt.title('Flexible EV charging')
    #plt.show()
    

#THE FOURTH PLOT, SAME AS NUMBER ONE BUT STACKED BAR
    #Stacked bar plot
    fig, ax1 = plt.subplots()
    ax1.step(hours, y, where = 'post', label='Power import', color='tab:red')
    ax1.bar(hours, demand, align='edge', label='Household demand', color='tab:orange')
    ax1.bar(hours, EV_demand, align='edge', bottom = demand, label='Regular EV charging', color='tab:grey')

    # Format primary y-axis
    ax1.set_xlabel('Hours')
    ax1.set_xticks(hours[::3])  # Reducing ticks for better readability
    ax1.set_ylabel('Power [kW]')
    ax1.legend(loc='upper left', ncol = 3)
    ax1.set_xlim(0, 47)

    # Adding the secondary y-axis for Spotprice
    ax2 = ax1.twinx()
    ax2.step(hours, price, where = 'post', label='Spotprice', color='tab:blue')
    ax2.set_ylabel('Spot Price [NOK/kWh]')
    ax2.legend(loc='upper right')
    ax2.set_ylim([0, 3])

    # Adding a title and adjusting layout
    plt.title('Demand and Imports same as the first figure as stacked bar')
    fig.tight_layout()
    """

    adjusted_demand = np.array([(d - e) for d, e in zip(demand, e_dis)]) #each element is the result of subtracting e_dis from demand.
    adjusted_EV_demand = np.array([(d - e) for d, e in zip(EV_demand, e_EV_dis)]) #each element is the result of subtracting e_dis from demand.

#a four and a half plot, showcasing where the energy import is coming from
    #Stacked bar plot
    fig, ax1 = plt.subplots()
    ax1.step(hours, y, where = 'post', label='Power import', color='k', linewidth = 2)
    ax1.bar(hours, adjusted_demand, align='edge', label='Household demand', color='lightgrey')
    ax1.bar(hours, adjusted_EV_demand, align='edge', bottom = adjusted_demand, label='Regular EV charging', color='tab:grey')
    ax1.bar(hours, e_EV_cha, align= 'edge', bottom = adjusted_demand + adjusted_EV_demand , label = 'additional EV charging', color = 'green')
    ax1.bar(hours, e_cha, align ='edge', bottom = adjusted_demand + adjusted_EV_demand + e_EV_cha, label = 'BESS charging', color = 'tab:green')
    ax1.bar(hours, e_dis, align ='edge', bottom = adjusted_demand + adjusted_EV_demand + e_EV_cha + e_cha, label = 'BESS discharging', color = 'tab:red')
    ax1.bar(hours, e_EV_dis, align ='edge', bottom = adjusted_demand + adjusted_EV_demand + e_EV_cha + e_cha + e_dis, label = 'avoided EV charging', color = 'red')

    # Format primary y-axis
    ax1.set_xlabel('Hours')
    ax1.set_xticks(hours[::3])  # Reducing ticks for better readability
    ax1.set_ylabel('Power [kW]')
    ax1.legend(loc='upper left', ncol = 3)
    ax1.set_xlim(0, 743)

    # Adding the secondary y-axis for Spotprice
    ax2 = ax1.twinx()
    ax2.step(hours, price, where = 'post', label='Spotprice', color='tab:blue', linewidth = 2)
    ax2.set_ylabel('Spot Price [NOK/kWh]')
    ax2.legend(loc='upper right')
    ax2.set_ylim([0, 7])

    # Adding a title and adjusting layout
    plt.title('Power import and what it goes to')
    fig.tight_layout()

    """
#THE Fifth plot, same as SECOND PLOT
    #plotting the community battery
    fig, ax1 = plt.subplots()
    ax1.step(hours, battery, where = 'post', label='State of Charge', color='tab:green')
    ax1.bar(hours, demand, align='edge', label='Household demand', color ='tab:orange')

    ax1.bar(hours, e_cha, align='edge', bottom = adjusted_demand, label = 'Battery charge', color = 'green')
    ax1.bar(hours, e_dis, align='edge', bottom = adjusted_demand, label = 'Battery discharge', color='red')  # Subtract discharge

    ax1.axhline(y=0, color= 'k', linestyle = '--')
    ax1.set_xlabel('Hours')
    ax1.set_xticks(hours[::3])  # Reducing ticks for better readability
    ax1.set_ylabel('Power [kW]')
    ax1.legend(loc='upper left', ncol=2)
    ax1.set_xlim(0,47)
    ax2 = ax1.twinx() #Creates a second y-axis on the right
    ax2.step(hours, price, where = 'post', label = 'Spotprice', color = 'tab:blue')
    ax2.set_ylabel('Spot Price [NOK/kWh]')
    ax2.legend(loc = 'upper right')
    ax2.set_ylim([0, 1.2])
    fig.tight_layout()  # Adjust layout to prevent overlapping
    plt.title('The Community Battery')
    plt.show()
    """
    #a fifth and a half plot, showcasing how the battery operates
    #plotting the community battery
    fig, ax1 = plt.subplots()
    ax1.step(hours, battery, where = 'post', label='State of Charge', color='tab:green')
    ax1.bar(hours, e_cha, align='edge', label = 'Battery charge', color = 'green')
    ax1.bar(hours, e_dis, align='edge', label = 'Battery discharge', color='red')  

    ax1.set_xlabel('Hours')
    ax1.set_xticks(hours[::3])  # Reducing ticks for better readability
    ax1.set_ylabel('Power [kW]')
    ax1.legend(loc='upper left', ncol=2)
    ax1.set_xlim(0,743)

    ax2 = ax1.twinx() #Creates a second y-axis on the right
    ax2.step(hours, price, where = 'post', label = 'Spotprice', color = 'tab:blue')
    ax2.set_ylabel('Spot Price [NOK/kWh]')
    ax2.legend(loc = 'upper right')
    ax2.set_ylim([0, 7])
    fig.tight_layout()  # Adjust layout to prevent overlapping
    plt.title('The Community Battery')


#THE SIXTH PLOTS, SAME AS THE THIRD PLOT
    #plotting the EV "battery"
    fig3, ax1 = plt.subplots()
    ax1.step(hours, EV_battery, where = 'post', label='EV flexibility potential', color='tab:green')
    ax1.bar(hours, EV_demand, align='edge', color ='tab:gray', label='Regular EV charging')
    ax1.bar(hours, e_EV_cha, align='edge', bottom = adjusted_EV_demand, label = 'Additional EV charging', color = 'green')
    ax1.bar(hours, e_EV_dis, align='edge', bottom = adjusted_EV_demand, label = 'Averted EV charging', color='red')  # Subtract discharge
    
    ax1.set_xlabel('Hours', fontsize=14, fontweight='bold', family='serif')
    ax1.set_xticks(hours[::3])  # Reducing ticks for better readability
    ax1.set_ylabel('Power [kW]', fontsize=14, fontweight='bold', family='serif')
    ax1.legend(loc = 'upper left', ncol = 2, prop = {'weight': 'bold', 'family': 'serif'})
    ax1.set_xlim(0,743)

    ax2 = ax1.twinx() #Creates a second y-axis on the right
    ax2.step(hours, price, where = 'post', label = 'Spotprice', color = 'tab:blue')
    ax2.set_ylabel('Spot Price [NOK/kWh]', fontsize=12, fontweight='bold', family='serif')
    ax2.legend(loc = 'upper right', prop = {'weight': 'bold', 'family': 'serif'})
    ax2.set_ylim([0, 7])
    fig3.tight_layout()  # Adjust layout to prevent overlapping
    plt.title('Flexible EV charging', fontsize=18, fontweight='bold', family='serif')
    plt.show()