import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pyomo.environ as pyo
from Formulation import ModelSetUp, Solve
from GridTariff import GridTariffEnergy, GridTariffPower



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

def Graphical_Results(m, what2run): #Function to plot results
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
    adjusted_EV_demand = np.array([(d - e) for d, e in zip(EV_demand, e_EV_dis)]) #each element is the result of subtracting e_EV_dis from demand.

    plt.rc('xtick', labelsize=14)  # X-tick customization
    plt.rc('ytick', labelsize=14)  # Y-tick customization
    plt.rc('font', family='serif') # Change font family globally

    days = [i for i in range(1,32)]
    days_str = []
    for day in days:
        if day < 10:
            days_str.append('0' + str(day) + '.01')
        else:
            days_str.append(str(day) + '.01')

#a plot showcasing where the energy import is coming from
    #Stacked bar plot
    fig, ax1 = plt.subplots(figsize = (12,6))
    ax1.step(hours, y, where = 'post', label='Grid Import', color='magenta', linewidth = 2)
    ax1.bar(hours, adjusted_demand, align='edge', label='Household Demand', color='lightgrey')
    ax1.bar(hours, adjusted_EV_demand, align='edge', bottom = adjusted_demand, label='Regular EV Charging', color='tab:grey')
    if what2run != 'b':
        ax1.bar(hours, e_cha, align ='edge', bottom = adjusted_demand + adjusted_EV_demand, label = 'BESS Charging', color = 'limegreen')
        ax1.bar(hours, e_EV_cha, align= 'edge', bottom = adjusted_demand + adjusted_EV_demand + e_cha, label = 'Additional EV Charging', color = 'darkgreen')
        #ax1.bar(hours, ENS, align = 'edge', color = 'yellow', label = 'ENS')
        ax1.bar(hours, e_dis, align ='edge', bottom = adjusted_demand + adjusted_EV_demand , label = 'BESS Discharging', color = 'orangered')
        ax1.bar(hours, e_EV_dis, align ='edge', bottom = adjusted_demand + adjusted_EV_demand+ e_dis, label = 'Avoided EV Charging', color = 'darkred')
        
    # Format primary y-axis
    major_ticks = [i for i in range(0,744,24)]
    major_labels =[f'{day}' for day in days_str]
    minor_ticks = [i for i in range(0, 744, 6)]
    ax1.set_xticks(major_ticks)
    ax1.set_xticklabels(major_labels, fontsize = 14, fontweight = 'bold')
    ax1.set_xticks(minor_ticks, minor = True)
    ax1.tick_params(axis = 'x', which = 'minor', length=5, color='gray')
    ax1.xaxis.set_tick_params(which='minor', labelsize=14)
    ax1.set_ylabel('Power [kW]',fontsize=16, fontweight='bold')
    ax1.legend(loc='upper left', ncol = 3, prop = {'weight': 'bold', 'family': 'serif', 'size':12})
    ax1.set_xlim(24*27, 24*29)
    #ax1.set_xlim(24*0, 24*2)
    #ax1.set_ylim(0, 95)
    ax1.set_ylim(0,110)
    ax2 = ax1.twinx() # Adding the secondary y-axis for Spotprice
    ax2.step(hours, price, where = 'post', label='Spot Price', color='tab:blue', linewidth = 2, linestyle = '--')
    ax2.set_ylabel('Spot Price [NOK/kWh]', fontsize=16, fontweight='bold')
    ax2.legend(loc='upper right', prop = {'weight': 'bold', 'family': 'serif', 'size':12})
    #ax2.set_ylim([0, 0.3])
    ax2.set_ylim(0.2,1.1)
    # Adding a title and adjusting layout
    plt.title('Grid Import and Allocation', fontsize=18, fontweight='bold')
    fig.tight_layout()



# #a plot showcasing how the battery operates
#     #plotting the community battery
#     fig2, ax1 = plt.subplots(figsize = (12,6))
#     ax1.step(hours, battery, where = 'post', label='State of Charge', color='tab:green')
#     ax1.bar(hours, e_cha, align='edge', label = 'Battery charge', color = 'green')
#     ax1.bar(hours, e_dis, align='edge', label = 'Battery discharge', color='red')  
#     ax1.set_xlabel('Days', fontsize=16, fontweight='bold')
#     ax1.set_xticks([i for i in range(0,744,24)], [f'{day}' for day in days_str])  # Reducing ticks for better readability
#     ax1.set_ylabel('Power [kW]',fontsize=16, fontweight='bold')
#     ax1.legend(loc='upper left', ncol=3, prop = {'weight': 'bold', 'family': 'serif'})
#     ax1.set_xlim(24*27, 24*29)
#     ax1.set_ylim(0,90)
#     ax2 = ax1.twinx() #Creates a second y-axis on the right
#     ax2.step(hours, price, where = 'post', label = 'Spot price', color = 'tab:blue')
#     ax2.set_ylabel('Spot Price [NOK/kWh]',fontsize=16, fontweight='bold')
#     ax2.legend(loc = 'upper right', prop = {'weight': 'bold', 'family': 'serif'})
#     ax2.set_ylim([0, 1])
#     plt.title('The Community Battery', fontsize=18, fontweight='bold')
#     fig2.tight_layout()  # Adjust layout to prevent overlapping


# #a plot showcasing how the EV charging operates
#     #plotting the EV "battery"
#     fig3, ax1 = plt.subplots(figsize = (12,6))
#     ax1.step(hours, EV_battery, where = 'post', label='EV flexibility potential', color='tab:green')
#     ax1.bar(hours, EV_demand, align='edge', label='Regular EV charging', color ='tab:gray')
#     ax1.bar(hours, e_EV_cha, align='edge', bottom = adjusted_EV_demand, label = 'Additional EV charging', color = 'green')
#     ax1.bar(hours, e_EV_dis, align='edge', bottom = adjusted_EV_demand, label = 'Averted EV charging', color='red')  # Subtract discharge
#     ax1.set_xlabel('Days', fontsize=16, fontweight='bold')
#     ax1.set_xticks([i for i in range(0,744,24)], [f'{day}' for day in days_str])  # Reducing ticks for better readability
#     ax1.set_ylabel('Power [kW]', fontsize=16, fontweight='bold')
#     ax1.legend(loc = 'upper left', ncol = 2, prop = {'weight': 'bold', 'family': 'serif'})
#     ax1.set_xlim(24*27, 24*29)
#     ax1.set_ylim(0, 110)
#     ax2 = ax1.twinx() #Creates a second y-axis on the right
#     ax2.step(hours, price, where = 'post', label = 'Spot price', color = 'tab:blue')
#     ax2.set_ylabel('Spot Price [NOK/kWh]', fontsize=16, fontweight='bold')
#     ax2.legend(loc = 'upper right', prop = {'weight': 'bold', 'family': 'serif'})
#     ax2.set_ylim([0, 1])
#     plt.title('Flexible EV charging', fontsize=18, fontweight='bold')
#     fig3.tight_layout()  # Adjust layout to prevent overlapping
    plt.show()

def Comparing_plots(base_case_file, compare_case_file, compare_2_case_file, compare_3_case_file):

    hours = [i for i in range(0,25)]

    base_case = pd.read_excel(base_case_file)
    compare_case = pd.read_excel(compare_case_file)
    compare_2_case = pd.read_excel(compare_2_case_file)
    compare_3_case = pd.read_excel(compare_3_case_file)

    base_daily = [list(base_case['Power Import [kW]'])[i:i+24] for i in range(0, len(base_case['Power Import [kW]']), 24)]
    base_transposed = zip(*base_daily)
    base_hourly = list(base_transposed)
    base_hourly_mean = np.array([sum(base_hourly[i]) for i in range(len(base_hourly))])/len(base_hourly)
    base_hourly_mean = list(base_hourly_mean)
    base_hourly_mean.append(base_hourly_mean[-1])

    case_daily = [list(compare_case['Power Import [kW]'])[i:i+24] for i in range(0, len(compare_case['Power Import [kW]']), 24)]
    case_transposed = zip(*case_daily)
    case_hourly = list(case_transposed)
    case_hourly_mean = np.array([sum(case_hourly[i]) for i in range(len(case_hourly))])/len(case_hourly)
    case_hourly_mean = list(case_hourly_mean)
    case_hourly_mean.append(case_hourly_mean[-1])

    case_2_daily = [list(compare_2_case['Power Import [kW]'])[i:i+24] for i in range(0, len(compare_2_case['Power Import [kW]']), 24)]
    case_2_transposed = zip(*case_2_daily)
    case_2_hourly = list(case_2_transposed)
    case_2_hourly_mean = np.array([sum(case_2_hourly[i]) for i in range(len(case_2_hourly))])/len(case_2_hourly)
    case_2_hourly_mean = list(case_2_hourly_mean)
    case_2_hourly_mean.append(case_2_hourly_mean[-1])

    case_3_daily = [list(compare_3_case['Power Import [kW]'])[i:i+24] for i in range(0, len(compare_3_case['Power Import [kW]']), 24)]
    case_3_transposed = zip(*case_3_daily)
    case_3_hourly = list(case_3_transposed)
    case_3_hourly_mean = np.array([sum(case_3_hourly[i]) for i in range(len(case_3_hourly))])/len(case_3_hourly)
    case_3_hourly_mean = list(case_3_hourly_mean)
    case_3_hourly_mean.append(case_3_hourly_mean[-1])

    price_daily = [list(base_case['Price [NOK/kWh]'])[i:i+24] for i in range(0, len(base_case['Price [NOK/kWh]']), 24)]
    price_transposed = zip(*price_daily)
    price_hourly = list(price_transposed)
    price_hourly_mean = np.array([sum(price_hourly[i]) for i in range(len(price_hourly))])/len(price_hourly)
    price_hourly_mean = list(price_hourly_mean)
    price_hourly_mean.append(price_hourly_mean[-1])

    plt.rc('xtick', labelsize=14)  # X-tick customization
    plt.rc('ytick', labelsize=14)  # Y-tick customization
    plt.rc('font', family='serif') # Change font family globally

    test = list(base_case['Power Import [kW]'])

    print(test.index(max(test)))

    # plt.figure()
    # plt.plot(range(744), compare_case['Power Import [kW]'], compare_2_case['Power Import [kW]'])
    
    fig, ax1 = plt.subplots(figsize = (12,6))
    ax1.step(hours, base_hourly_mean, color = 'tab:red', label = 'Base Case', linewidth = 2, where = 'post')
    ax1.step(hours, case_hourly_mean,  color = 'tab:green', label = 'Case 1', linewidth = 2, where = 'post')
    ax1.step(hours, case_2_hourly_mean,  color = 'tab:orange', label = 'Case 2', linewidth = 2, where = 'post')
    ax1.step(hours, case_3_hourly_mean,  color = 'tab:purple', label = 'Case 3', linewidth = 2, where = 'post')
    ax1.set_xlim(0,23)
    ax1.set_xticks(hours)
    ax1.set_xlabel('Hours', fontsize=16, fontweight='bold', family='serif')
    ax1.set_ylim(40,85)
    ax1.set_ylabel('Power [kW]', fontsize=16, fontweight='bold', family='serif')
    ax1.legend(loc = 'upper left', ncol = 2, prop = {'weight': 'bold', 'family': 'serif', 'size': 14})
    ax2 = ax1.twinx()
    ax2.set_ylabel('Price [NOK/kWh)]', fontsize=16, fontweight='bold', family='serif')
    ax2.step(hours, price_hourly_mean, linestyle = '--', label = 'Spot Price',linewidth = 2, where = 'post')
    ax2.legend(loc = 'upper right', ncol = 1, prop = {'weight': 'bold', 'family': 'serif', 'size': 14})
    plt.title('Average Hourly Grid Import and Spot Price', fontsize=18, fontweight='bold', family='serif')
    fig.tight_layout()
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
    y_EV_split = [list(y_EV)[i:i+24] for i in range(0, len(y), 24)]
    e_cha_split = [list(e_cha)[i:i+24] for i in range(0, len(e_cha), 24)]
    e_dis_split = [list(e_dis)[i:i+24] for i in range(0, len(e_dis), 24)]
    
    #transponerer den slik at vi får 24 lister med 31 verdier
    y_transposed = zip(*y_split)
    y_EV_transposed = zip(*y_EV_split)
    e_cha_transposed = zip(*e_cha_split)
    e_dis_transposed = zip(*e_dis_split)
    y_box = list(y_transposed)
    y_EV_box = list(y_EV_transposed)
    e_cha_box = list(e_cha_transposed)
    e_dis_box = list(e_dis_transposed)

    plt.rc('xtick', labelsize=14) 
    plt.rc('ytick', labelsize=14) 
    plt.rc('font', family='serif') 

    plt.figure(figsize = (12,6))
    box1 = plt.boxplot(y_box, patch_artist=True)
    for median in box1['medians']:
        median.set_color('darkorange')
        median.set_linewidth(2)
    for patch in box1['boxes']:
        patch.set_facecolor('bisque')
    plt.xlabel('Hours', fontsize=16, fontweight='bold', family='serif')
    plt.ylabel('Power [kW]', fontsize=16, fontweight='bold', family='serif')
    plt.ylim(0, 100)
    plt.title('Grid Import', fontsize=18, fontweight='bold', family='serif')
    plt.tight_layout()
    
    plt.figure(figsize = (12,6))
    box2 = plt.boxplot(y_EV_box, patch_artist=True)
    for median in box2['medians']:
        median.set_color('darkblue')
        median.set_linewidth(2)
    for patch in box2['boxes']:
        patch.set_facecolor('lightsteelblue')
    plt.xlabel('Hours', fontsize=16, fontweight='bold', family='serif')
    plt.ylabel('Power [kW]', fontsize=16, fontweight='bold', family='serif')
    plt.ylim(0, 35)
    plt.title('EV Charging', fontsize=18, fontweight='bold', family='serif')
    plt.tight_layout()

    plt.figure(figsize = (12,6))
    box3 = plt.boxplot(e_cha_box, patch_artist=True)
    box4 = plt.boxplot(e_dis_box, patch_artist=True)
    for median in box3['medians']:
        median.set_color('darkgreen')
        median.set_linewidth(2)
    for patch in box3['boxes']:
        patch.set_facecolor('palegreen')
    for patch in box4['boxes']:
        patch.set_facecolor('lightcoral')
    for median in box4['medians']:
        median.set_color('darkred')
        median.set_linewidth(2)
    plt.xlabel('Hours', fontsize=16, fontweight='bold', family='serif')
    plt.ylabel('Power [kW]', fontsize=16, fontweight='bold', family='serif')
    plt.ylim(0, 35)
    plt.title('BESS Charging/Discharging', fontsize=18, fontweight='bold', family='serif')
    plt.plot([], [], color='darkgreen', label='Charge')
    plt.plot([], [], color='darkred', label='Discharge')
    plt.legend(loc='upper left', ncol = 3, prop = {'weight': 'bold', 'family': 'serif', 'size':12})
    plt.tight_layout()
    plt.show()

    return    

def Cost_Of_Flex(SpotPrice, EnergyTariff, PowerTariff, Demand, EV_data, batt_const, flex_const):
    #setter case 3 som standard, setter fast timen for IBDR men ikke begrensingen
    case_dict = {'flexible_EV_on': True,      #flexible EV charge not active
                'battery_on': True,           #community BESS not active
                'power_grid_tariff_on': True,  #grid tariff not active
                'step_grid_tariff': True,      #stepwise grid tariff active
                'IBDR_on': True,              #incentive base demand response not active
                'hour_restricted': 674,
                'power_restricted': 10e6}
    
    #setter hva importen skal begrens til     
    y_lim = np.linspace(0.2, 73.2, 74)
    #y_lim = np.linspace(10.2, 73.2, 64)
    y_lim = y_lim[::-1]

    obj_value = []

    for limit in y_lim:
        case_dict['power_restricted'] = limit
        m = ModelSetUp(SpotPrice, EnergyTariff, PowerTariff, Demand, EV_data, batt_const, flex_const, case_dict)
        Solve(m)
        obj_value.append(pyo.value(m.Obj))

    plt.rc('xtick', labelsize=14) 
    plt.rc('ytick', labelsize=14) 
    plt.rc('font', family='serif') 
    plt.figure(figsize = (12,6))
    plt.axvline(x = 10.2, linestyle = '--', color = 'k')
    plt.step(y_lim, obj_value)
    plt.xlabel('Grid Import Allowed [kW]', fontsize = 14, fontweight='bold')
    plt.xlim(10,73)
    plt.xticks([i for i in range(0,75,5)])
    plt.ylabel('Total Costs [NOK]', fontsize = 16, fontweight='bold')
    plt.title('Cost of Flexibility', fontsize = 18, fontweight='bold')
    plt.tight_layout()

    obj_val_diff = [obj_value[0]]
    for i in range(len(obj_value)-1):
        obj_val_diff.append(obj_value[i+1] - obj_value[i])

    plt.figure(figsize = (12,6))
    plt.axvline(x = 10.2, linestyle = '--', color = 'k')
    plt.step(y_lim, obj_val_diff, linewidth = 2)
    plt.xlabel('Grid Import Allowed [kW]', fontsize = 14, fontweight='bold')
    plt.xticks([i for i in range(10,75,5)])
    plt.xlim(9.9,70.1)
    plt.ylabel('Change in Total Costs [NOK]', fontsize = 16, fontweight='bold')
    plt.ylim(0,0.35)
    plt.title('Marginal Cost of Flexibility', fontsize = 18, fontweight='bold')
    plt.tight_layout()

    plt.show()
    
    # #linear regression
    # x = y_lim
    # y = obj_value
    # log_y = np.log(y)
    # x_reshaped = x.reshape(-1,1)
    # model = LinearRegression()
    # model.fit(x_reshaped, log_y)
    # b = model.coef_[0]
    # log_a = model.intercept_
    # a = np.exp(log_a)
    # print(f"Exponential Model: y = {a:.3f} * e^({b:.3f} * x)")

def Economic_plots(base_case_file, compare_case_file, compare_2_case_file, compare_3_case_file):
    #GRID TARIFF DATA   
    energy = GridTariffEnergy()
    power = GridTariffPower()

    #SPOT PRICE, GRID IMPORT AND ENS DATA
    base = pd.read_excel(base_case_file)
    case1 = pd.read_excel(compare_case_file)
    case2 = pd.read_excel(compare_2_case_file)
    case3 = pd.read_excel(compare_3_case_file)

    #RETRIEVING THE DATA FROM THE FILES
    spot_price = base['Price [NOK/kWh]']
    grid_import = [base['Power Import [kW]'], case1['Power Import [kW]'], case2['Power Import [kW]'], case3['Power Import [kW]']]
    max_grid_import = [max(base['Power Import [kW]']), max(case1['Power Import [kW]']), max(case2['Power Import [kW]']), max(case3['Power Import [kW]'])]
    CENS = [sum(base['CENS']), sum(case1['CENS']), sum(case2['CENS']), sum(case3['CENS'])]

    spot_volumetric_costs = []
    grid_volumetric_costs = []
    monthly_demand_charge = []
    
    for j in range(len(grid_import)):
        spot_volumetric_costs_temp = 0
        grid_volumetric_costs_temp = 0
        #CALCULATING THE VOLUMETRIC COSTS
        for i in range(len(spot_price)):
            spot_volumetric_costs_temp += spot_price[i]*grid_import[j][i]
            grid_volumetric_costs_temp += energy[i]*grid_import[j][i]
        spot_volumetric_costs.append(spot_volumetric_costs_temp)
        grid_volumetric_costs.append(grid_volumetric_costs_temp)

    
        #CALCULATING THE MONTLY DEMAND CHARGE
        for bracket in power.keys():
            if '++' in bracket:
                lower = int(bracket.split('++')[0])
                upper = 10000
            else: 
                lower, upper = map(int, bracket.split('-'))

            if max_grid_import[j] > lower and max_grid_import[j] <= upper:
                monthly_demand_charge.append(power[bracket])
    
    x = ['Base Case', 'Case 1', 'Case 2', 'Case 3']
    spot_volumetric_costs = np.array(spot_volumetric_costs)/1000
    grid_volumetric_costs = np.array(grid_volumetric_costs)/1000
    monthly_demand_charge = np.array(monthly_demand_charge)/1000
    CENS = np.array(CENS)/1000

    plt.rc('xtick', labelsize=14) 
    plt.rc('ytick', labelsize=14) 
    plt.rc('font', family='serif')
    plt.figure(figsize = (12,6))
    plt.bar(x, spot_volumetric_costs, label = 'Electricity Price', color = 'tab:blue', alpha = 0.8)
    plt.bar(x, grid_volumetric_costs, bottom = spot_volumetric_costs, label = 'Volumteric Grid Tariff', color = 'tab:green', alpha = 0.8)
    plt.bar(x, monthly_demand_charge, bottom = spot_volumetric_costs + grid_volumetric_costs, label = 'Monthly Demand Charge', color = 'forestgreen')
    plt.bar(x, CENS, bottom = spot_volumetric_costs + grid_volumetric_costs + monthly_demand_charge, label = 'CENS', color = 'yellow', alpha = 0.8)
    plt.legend(loc='upper left', ncol=2, prop = {'weight': 'bold', 'family': 'serif', 'size': 14})
    plt.ylabel('Price [kNOK]', fontsize = 16, fontweight='bold')
    plt.title('Total Costs', fontsize = 18, fontweight='bold')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':

    Comparing_plots('Base_Case_Results.xlsx', 'Case1_Results.xlsx', 'Case2_Results.xlsx', 'Case3_Results.xlsx')

    #Economic_plots('Base_Case_Results.xlsx', 'Case1_Results.xlsx', 'Case2_Results.xlsx', 'Case3_Results.xlsx')
