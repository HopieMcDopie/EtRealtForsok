import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from SpotPrice import SpotPrices
from ConsumptionData import ReadCSVDemandFile
from EVData import ReadEVData, FindMonthlyChargeEnergy
from GridTariff import GridTariffEnergy, GridTariffPower

"""
Her vil jeg legge inn at man kan skru av og på ting med True or False! Kanskje som en dictionary?

"""
flexible_EV_on = True
battery_on = True
power_grid_tariff_on = True
step_grid_tariff = True # if False the linear model will be included!


# _____________________________________________DATA INPUT_____________________________________________
'''
    Her må vi lese inn en måned med forbruksdata og prisdata. 
    Disse må ha time-oppløsning og være i fomatet pandas dataframe. 
    De burde også operere med samme enhet, NOK og kWh.
'''

SpotPrice = SpotPrices() # Gives the spot prices for NO3 for january 2024, hourly resolution
EnergyTariff = GridTariffEnergy() # Gives the energy part of the grid tariff for NO3, hourly resolution
PowerTariff = GridTariffPower() # Gives the power part of the grid tariff for NO3

Demand = ReadCSVDemandFile('AustinDemand.csv') # Gives the demand for 25 households for a month, hourly resolution
EV_data = ReadEVData(share_of_CP=0.3, no_of_EVs=25) # Gives the available power in the area and the demand for a 
                                                    # given number of EVs for a month, hourly resolution, note that share_of_CP 
                                                    # is the share of private charging points





# _____________________________________________DEFINE CONSTANTS_____________________________________________
'''
Her må vi definerer konstanter som feks batteriparametere etc.
'''

# These constants are linked to the shared community battery
batt_const = {'Battery energy capacity': 80, #kWh
             'Initial State of Charge': 0, #kWh
             'Charge capacity': 80*0.20, #kW
             'Dishcharge capacity': 80*0.20, #kW
             'eta': 0.975}

flex_const = {'Monthly energy' : FindMonthlyChargeEnergy(EV_data), #kWh
                            'Flexible': 0.3} # %



# _____________________________________________MATHEMATICAL FORMULATION_____________________________________________
'''
Her må objektivfunskjonen sammen med alle constraintsene være definert først, så må modellen settes opp
'''
# Objective function
def Obj_without_power_grid_tariff(m):
    #The objective function of the optimization problem, is the sum of the costs of the consumed energy
    return sum((m.C_spot[t] + m.C_grid_energy[t] )*m.y_imp[t] for t in m.T)  

def Obj_with_power_grid_tariff(m):
    #The objective function of the optimization problem, is the sum of the costs of the consumed energy, 
    # in addtion to the cost related to the power consumption decided by the grid tariff
    return sum((m.C_spot[t] + m.C_grid_energy[t] )*m.y_imp[t] for t in m.T)  + m.C_grid_power

#Energy balance constraints
def HouseEnergyBalance(m, t):
    #Ensures that the imported energy to th houses equals the demand and the potential charging or 
    # discharging of the comuunity battery
    return m.y_house[t] == m.D[t] + m.e_cha[t] - m.e_dis[t] 

#Modelling of the flexible EV battery 
def EVEnergyBalance(m, t):
    #The modelling of the flexible EV charging is done through a conseptual battery, the charging of
    # this implies charging moved forwards in time, and teh discharging is demand that already has been
    # met by earlier charging
    return m.y_EV[t] == m.D_EV[t] + m.e_EV_cha[t] - m.e_EV_dis[t]

#Defines grid import
def GridImport(m, t):
    #Ensures that the total imported energy is the sum of what is going to the houses and to the EVs
    return m.y_imp[t] == m.y_house[t] + m.y_EV[t]

#Monthly peak grid tariff constraints
def Peak(m, t):
    #Finds the monthly peak consumption of power as the highest value of the grid import
    return m.peak >= m.y_imp[t]

#Ensure single power tariff price-bracket activation
def SignleSegment(m):
    #Ensures that only one of the price-brackets of the prower grid tariff is activated 
    return sum(m.z[i] for i in m.I) == 1

#couples activated price bracket with price
def Segment(m):
    #Ensures that the measured peak power activates the respective power tariff price-bracket
    return m.peak <= sum(m.z[i] * m.breakpoints[i] for i in m.I)
    
#Relates the active power grid tariff price-breacket to the cost
def TariffCosts(m):
    return m.C_grid_power == sum(m.costs[i]*m.z[i] for i in m.I)


#_____________________________#
# Community battery constraints

#Ensures that the battery's State of Charge is dependent on the amount charged, 
def SoC(m, t):
    # minus the amount discharged and the SoC of the previous hour.
    # Note that the efficiencies of charging and discharging are included, in addition
    # to an initial SoC for hour 0.
    if t == 0:
        return m.b[0] == m.e_cha[0]*m.eta - m.e_dis[0]/m.eta + m.SoC0
    else:
        return m.b[t] == m.e_cha[t]*m.eta - m.e_dis[t]/m.eta + m.b[t-1]
    
def SoCCap(m, t):
    #Ensures that the battery stays within its energy limitations
    return m.b[t] <= m.BatteryCap
    
def ChargeCap(m, t):
    #Ensures that the battery stays within its power limitations
    return m.e_cha[t] <= m.BatteryChargeCap

def DischargeCap(m, t):
    #Ensures that the battery stays within its power limitations
    return m.e_dis[t] <= m.BatteryDischargeCap


#______________________________________#
# Modelling of the flexible EV charging


def SoC_EV(m, t):
    #Models how much flexibility has been activated and when it is moved from
    if t == 0:
        return m.b_EV[0] == m.e_EV_cha[0] - m.e_EV_dis[0] 
    else:
        return m.b_EV[t] == m.e_EV_cha[t] - m.e_EV_dis[t] + m.b_EV[t-1]
    

def SoCCap_EV(m, t):
    # The total amount of potential flexible EV charging
    return m.b_EV[t]  <= 105.1 #kW (average charge in a day)

def Flex(m):
    # Decides how much of the monthly demand could be flexible
    return sum(m.e_EV_cha[t] for t in m.T) <= m.EV_BatteryEnergyCap
    
def ChargeCap_EV(m, t):
    # The amount of EV charingg that can be moved is limited by the amount of 
    # available capacity in the grid at the hour
    return m.e_EV_cha[t] <= m.EV_BatteryPowerCap[t] 

def DischargeCap_EV(m, t):
    #Discharge does not seem to be a limiting factor, as this is in reality 
    # chargign that is not occuring in that hours because of charging in an 
    # earlier hour...  
    return m.e_EV_dis[t] <= m.EV_BatteryPowerCap[t] 

#______________________________________#
# The set up of the optimization problem
def ModelSetUp(SpotPrice, EnergyTariff, PowerTariff, Demand, EV_data, batt_const, flex_const): 
    #Instance
    m = pyo.ConcreteModel()

    #Set
    m.T = pyo.RangeSet(0, len(Demand)-1)      # 24 hours/day * 31 days/month = 744 hours
    m.I = pyo.RangeSet(0, len(PowerTariff)-1) # 15 different price-brackets
    
    #Paramters
    m.C_spot              = pyo.Param(m.T, initialize = SpotPrice)                                      # spot price input for the month [NOK/kWh]
    m.C_grid_energy       = pyo.Param(m.T, initialize = EnergyTariff)                                   # energy part of grid tariff [NOK/kWh]
    m.D                   = pyo.Param(m.T, initialize = Demand)                                         # aggregated household demand [kWh]
    m.D_EV                = pyo.Param(m.T, initialize = EV_data['Charging'])                            # aggregated EV demand [kWh]
    m.SoC0                = pyo.Param(initialize = batt_const['Initial State of Charge'])               # initial state of charge of the battery [kWh]
    if battery_on:
        m.BatteryCap            = pyo.Param(initialize = batt_const['Battery energy capacity'])               # max battery energy capacity [kWh]
    else:
        m.BatteryCap            = pyo.Param(initialize = 0)                                                   # max battery energy capacity [kWh]
    m.BatteryChargeCap    = pyo.Param(initialize = batt_const['Charge capacity'])                       # charging speed/battery power capacity [kW]
    m.BatteryDischargeCap = pyo.Param(initialize = batt_const['Dishcharge capacity'])                   # disharging speed/battery power capacity [kW]
    m.eta                 = pyo.Param(initialize = batt_const['eta'])                                   # efficiency of charge/discharge
    if flexible_EV_on:
        m.EV_BatteryEnergyCap   = pyo.Param(initialize = flex_const['Monthly energy']*flex_const['Flexible']) # amount of flexible EV load
    else:
        m.EV_BatteryEnergyCap   = pyo.Param(initialize = 0)                                               # amount of flexible EV load
    m.EV_BatteryPowerCap        = pyo.Param(m.T, initialize = EV_data['Available'])                           # available capacity in the grid

    #Creating the list of the grid tariff break-points and respective costs
    m.breakpoints = []
    m.costs = []
    for key, value in PowerTariff.items():
        if '++' in key:
            lower = int(key.split('++')[0])
            upper = 10000
        else: 
            lower, upper = map(int, key.split('-'))
        m.breakpoints.append(upper)
        m.costs.append(value)

    #Variables
    m.y_house       = pyo.Var(m.T, within = pyo.NonNegativeReals) # imported energy from the grid to the house [kWh]
    m.y_EV          = pyo.Var(m.T, within = pyo.NonNegativeReals) # imported energy from the grid to the EV [kWh]
    m.y_imp         = pyo.Var(m.T, within = pyo.NonNegativeReals) # imported energy from the grid in total [kWh]
    m.b             = pyo.Var(m.T, within = pyo.NonNegativeReals) # battery SoC [kWh]
    m.e_cha         = pyo.Var(m.T, within = pyo.NonNegativeReals) # energy charged to the battery [kW]
    m.e_dis         = pyo.Var(m.T, within = pyo.NonNegativeReals) # energy disherged from the battery [kW]
    m.b_EV          = pyo.Var(m.T, within = pyo.NonNegativeReals) # EV battery SoC [kWh]
    m.e_EV_cha      = pyo.Var(m.T, within = pyo.NonNegativeReals) # flexibility activated [kW]
    m.e_EV_dis      = pyo.Var(m.T, within = pyo.NonNegativeReals) # result of activated flexibility [kW]
    m.C_grid_power  = pyo.Var(within = pyo.NonNegativeReals)      # cost of power consumption [NOK]

    if step_grid_tariff:
        m.peak          = pyo.Var(within = pyo.NonNegativeReals)      # peak power consumed during th month [kW]
        m.z             = pyo.Var(m.I, within = pyo.Binary)           # binary variable that selects price-backet of power grid tariff
        m.SingleSegment         = pyo.Constraint(rule = SignleSegment)
        m.Segment               = pyo.Constraint(rule = Segment) 
        m.TariffCosts           = pyo.Constraint(rule = TariffCosts)
    else:
        m.peak = pyo.Var(within = pyo.NonNegativeReals, bounds = (m.breakpoints[0], m.breakpoints[-1])) # peak power consumed during th month [kW]
        m.piecewice = pyo.Piecewise(m.C_grid_power, m.peak, pw_pts = m.breakpoints, f_rule = m.costs, pw_repn = 'SOS2', pw_constr_type = 'EQ') #piecewice function

    #Constraints
    m.HouseEnergyBalance    = pyo.Constraint(m.T, rule = HouseEnergyBalance)
    m.EVEnergyBalance       = pyo.Constraint(m.T, rule = EVEnergyBalance)
    m.GridImport            = pyo.Constraint(m.T, rule = GridImport)
    m.Peak                  = pyo.Constraint(m.T,rule = Peak)
    m.SoC                   = pyo.Constraint(m.T, rule = SoC)
    m.SoCCap                = pyo.Constraint(m.T, rule = SoCCap)
    m.ChargeCap             = pyo.Constraint(m.T, rule = ChargeCap) 
    m.DischargeCap          = pyo.Constraint(m.T, rule = DischargeCap)
    m.SoC_EV                = pyo.Constraint(m.T, rule = SoC_EV)
    m.SoCCap_EV             = pyo.Constraint(m.T, rule = SoCCap_EV)
    m.Flex                  = pyo.Constraint(rule= Flex)
    m.ChargeCap_EV          = pyo.Constraint(m.T, rule = ChargeCap_EV) 
    m.DischargeCap_EV       = pyo.Constraint(m.T, rule = DischargeCap_EV)         
    

    #Objective function
    if power_grid_tariff_on:
        m.Obj = pyo.Objective(rule = Obj_with_power_grid_tariff, sense = pyo.minimize)
    else:
        m.Obj = pyo.Objective(rule= Obj_without_power_grid_tariff, sense = pyo.minimize)

    return m


# Solving and presenting the data
'''
Her må vi solve og lagre data, gjerne presentere i gode visuelle grafer
'''
def Solve(m):
    opt = SolverFactory('gurobi')
    return opt.solve(m, load_solutions = True)

def Graphical_results(m):
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

    #plotting the demand and imports
    fig1, ax1 = plt.subplots()
    ax1.plot(hours, y, label='Power import', color='tab:red')
    ax1.plot(hours, demand, color ='tab:orange', linestyle = '--', label='House Demand')
    ax1.plot(hours, EV_demand, color = 'tab:grey', linestyle = '--', label = 'EV demand')
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



m = ModelSetUp(SpotPrice, EnergyTariff, PowerTariff, Demand, EV_data, batt_const, flex_const)
Solve(m)
Graphical_results(m)
print(f'Objective function: {pyo.value(m.Obj):.2f} NOK')
print(f'Peak power imported during the month: {pyo.value(m.peak):.2f} kW')
print(f'Cost of respective grid tariff power price bracket: {pyo.value(m.C_grid_power):.2f} NOK')