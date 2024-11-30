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
        'ENS': [m.ENS[t].value for t in m.T],
        'CENS': [m.CENS.value * m.ENS[t].value for t in m.T]
    })
    
    #Creating an excel sheet for the scenario run
    if what2run == "b":
        file_name = 'Base_Case_Results.xlsx' 
        print('Base_Case_Results.xlsx is created')
    elif what2run == "1":
        file_name = 'Case1_Results.xlsx'
        print('Case1_Results.xlsx is created')
    elif what2run == "2":
        file_name = 'Case2_Results.xlsx'
        print('Case2_Results.xlsx is created')
    elif what2run == "3":
        file_name = 'Case3_Results.xlsx'
        print('Case3_Results.xlsx is created')
    else:
        file_name = 'Base_Case_Results.xlsx' 
        print('Base_Case_Results.xlsx is created')

    results_df.to_excel(file_name, index = False)
    return ()


def Graphical_Results(m): #Function to plot results
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
 
    adjusted_demand = np.array([(d - e) for d, e in zip(demand, e_dis)]) #each element is the result of subtracting e_dis from demand.
    adjusted_EV_demand = np.array([(d - e) for d, e in zip(EV_demand, e_EV_dis)]) #each element is the result of subtracting e_dis from demand.

    print('Actual peak power: ', max(y))
    print('ENS: ', max(ENS))

    plt.rc('xtick', labelsize=10)  # X-tick customization
    plt.rc('ytick', labelsize=10)  # Y-tick customization
    plt.rc('font', family='serif') # Change font family globally

#a plot showcasing where the energy import is coming from
    #Stacked bar plot
    fig, ax1 = plt.subplots(figsize = (10,6))
    ax1.step(hours, y, where = 'post', label='Grid import', color='k', linewidth = 2)
    ax1.bar(hours, adjusted_demand, align='edge', label='Household demand', color='lightgrey')
    ax1.bar(hours, adjusted_EV_demand, align='edge', bottom = adjusted_demand, label='Regular EV charging', color='tab:grey')
    ax1.bar(hours, e_EV_cha, align= 'edge', bottom = adjusted_demand + adjusted_EV_demand , label = 'Additional EV charging', color = 'darkgreen')
    ax1.bar(hours, e_cha, align ='edge', bottom = adjusted_demand + adjusted_EV_demand + e_EV_cha, label = 'BESS charging', color = 'limegreen')
    ax1.bar(hours, ENS, align = 'edge', color = 'yellow', label = 'ENS')
    ax1.bar(hours, e_EV_dis, align ='edge', bottom = adjusted_demand + adjusted_EV_demand, label = 'Avoided EV charging', color = 'darkred')
    ax1.bar(hours, e_dis, align ='edge', bottom = adjusted_demand + adjusted_EV_demand + e_EV_dis, label = 'BESS discharging', color = 'orangered')
    
    

    # Format primary y-axis
    ax1.set_xlabel('Days',fontsize=14, fontweight='bold', family='serif')
    ax1.set_xticks([i for i in range(0,744,24)], [f'{i}' for i in range(1,32)])  # Reducing ticks for better readability
    ax1.set_ylabel('Power [kW]',fontsize=14, fontweight='bold', family='serif')
    ax1.legend(loc='upper left', ncol = 3, prop = {'weight': 'bold', 'family': 'serif'})
    ax1.set_xlim(24*21, 24*22)
    ax1.set_ylim(0, 85)

    # Adding the secondary y-axis for Spotprice
    ax2 = ax1.twinx()
    ax2.step(hours, price, where = 'post', label='Spot price', color='tab:blue', linewidth = 2)
    ax2.set_ylabel('Spot Price [NOK/kWh]', fontsize=14, fontweight='bold', family='serif')
    ax2.legend(loc='upper right', prop = {'weight': 'bold', 'family': 'serif'})
    ax2.set_ylim([0, 0.7])

    # Adding a title and adjusting layout
    plt.title('Grid import and distribution', fontsize=18, fontweight='bold', family='serif')
    fig.tight_layout()



#a plot showcasing how the battery operates
    #plotting the community battery
    fig2, ax1 = plt.subplots(figsize = (10,6))
    ax1.step(hours, battery, where = 'post', label='State of Charge', color='tab:green')
    ax1.bar(hours, e_cha, align='edge', label = 'Battery charge', color = 'green')
    ax1.bar(hours, e_dis, align='edge', label = 'Battery discharge', color='red')  

    ax1.set_xlabel('Days', fontsize=14, fontweight='bold', family='serif')
    ax1.set_xticks([i for i in range(0,744,24)], [f'{i}' for i in range(1,32)])  # Reducing ticks for better readability
    ax1.set_ylabel('Power [kW]',fontsize=14, fontweight='bold', family='serif')
    ax1.legend(loc='upper left', ncol=3, prop = {'weight': 'bold', 'family': 'serif'})
    ax1.set_xlim(24*21, 24*28)

    ax2 = ax1.twinx() #Creates a second y-axis on the right
    ax2.step(hours, price, where = 'post', label = 'Spot price', color = 'tab:blue')
    ax2.set_ylabel('Spot Price [NOK/kWh]',fontsize=14, fontweight='bold', family='serif')
    ax2.legend(loc = 'upper right', prop = {'weight': 'bold', 'family': 'serif'})
    ax2.set_ylim([0, 7])

    plt.title('The Community Battery', fontsize=18, fontweight='bold', family='serif')
    fig2.tight_layout()  # Adjust layout to prevent overlapping


#a plot showcasing how the EV charging operates
    #plotting the EV "battery"
    fig3, ax1 = plt.subplots(figsize = (10,6))
    ax1.step(hours, EV_battery, where = 'post', label='EV flexibility potential', color='tab:green')
    ax1.bar(hours, EV_demand, align='edge', color ='tab:gray', label='Regular EV charging')
    ax1.bar(hours, e_EV_cha, align='edge', bottom = adjusted_EV_demand, label = 'Additional EV charging', color = 'green')
    ax1.bar(hours, e_EV_dis, align='edge', bottom = adjusted_EV_demand, label = 'Averted EV charging', color='red')  # Subtract discharge
    
    ax1.set_xlabel('Days', fontsize=14, fontweight='bold', family='serif')
    ax1.set_xticks([i for i in range(0,744,24)], [f'{i}' for i in range(1,32)])  # Reducing ticks for better readability
    ax1.set_ylabel('Power [kW]', fontsize=14, fontweight='bold', family='serif')
    ax1.legend(loc = 'upper left', ncol = 2, prop = {'weight': 'bold', 'family': 'serif'})
    ax1.set_xlim(24*21, 24*28)
    ax1.set_ylim(0,10)

    ax2 = ax1.twinx() #Creates a second y-axis on the right
    ax2.step(hours, price, where = 'post', label = 'Spot price', color = 'tab:blue')
    ax2.set_ylabel('Spot Price [NOK/kWh]', fontsize=14, fontweight='bold', family='serif')
    ax2.legend(loc = 'upper right', prop = {'weight': 'bold', 'family': 'serif'})
    ax2.set_ylim([0, 7])
    
    plt.title('Flexible EV charging', fontsize=18, fontweight='bold', family='serif')
    fig3.tight_layout()  # Adjust layout to prevent overlapping
    plt.show()

def Comparing_plots(base_case_file, compare_case_file):

    base_case = pd.read_excel(base_case_file)
    compare_case = pd.read_excel(compare_case_file)
    
    

    fig, ax1 = plt.subplots()
    ax1.plot(base_case['Power Import [kW]'], color = 'tab:red', linestyle = '--')
    ax1.plot(compare_case['Power Import [kW]'],  color = 'tab:red')
    ax1.set_xlim(24*21, 24*22)
    ax1.set_ylim(15,80)
    ax2 = ax1.twinx()
    ax2.plot(base_case['Price [NOK/kWh]'], linestyle = '--')
    ax2.set_ylim(0,0.6)
    
    plt.show()

    return


def Box_Plots(m):
    """Se hvordan import flyttes med flexibilitet 
    
    Et histgram på power import gjennom dagen, på timesbasis og døgnsbasis?
    Et histogram på når Elbilen lades, lager en som legger på e_EV_cha og trekker fra e_EV_dis

    https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.boxplot.html
    """
    #lager arrays med all data fra optimeringmodellen, 1x744
    hours = list(m.T)
    y = np.array([m.y_imp[t].value for t in m.T])
    y_house = np.array([m.y_house[t].value for t in m.T])
    y_EV = np.array([m.y_EV[t].value for t in m.T])

    demand = np.array([m.D[t] for t in m.T])
    EV_demand = np.array([m.D_EV[t] for t in m.T])

    battery = np.array([m.b[t].value for t in m.T])
    e_cha = np.array([m.e_cha[t].value for t in m.T])
    e_dis = np.array([m.e_dis[t].value for t in m.T])

    EV_battery = np.array([m.b_EV[t].value for t in m.T])
    e_EV_cha = np.array([m.e_EV_cha[t].value for t in m.T])
    e_EV_dis = np.array([m.e_EV_dis[t].value for t in m.T])

    ENS = np.array([m.ENS[t].value for t in m.T])

    #lager 31 lister med 24 verdier
    y_split = [list(y)[i:i+24] for i in range(0, len(y), 24)]
    
    #transponerer den slik at vi får 24 lister med 31 verdier
    y_transposed = zip(*y_split)
    y_box = list(y_transposed)

    plt.figure(figsize = (10,6))
    plt.boxplot(y_box)
    plt.xlabel('Hours', fontsize=14, fontweight='bold', family='serif')
    plt.ylabel('Power [kW]', fontsize=14, fontweight='bold', family='serif')
    plt.ylim(0, 100)
    plt.title('Grid import', fontsize=18, fontweight='bold', family='serif')
    plt.tight_layout()
    plt.show()

    return    


if __name__ == '__main__':

    Comparing_plots('Base_Case_Results.xlsx', 'Case1_Results.xlsx')
