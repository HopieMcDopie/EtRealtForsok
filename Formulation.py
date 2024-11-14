import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from SpotPrice import SpotPrices
from ConsumptionData import ReadCSVDemandFile
from EVData import ReadEVData, FindMonthlyChargeEnergy
from GridTariff import GridTariffEnergy


# Data input
'''
Her må vi lese inn en måned med forbruksdata og en med prisdata. Disse må ha time-oppløsning og være i
fomatet pandas dataframe
'''

SpotPrice = SpotPrices()
EnergyTariff = GridTariffEnergy()

Demand = ReadCSVDemandFile('AustinDemand.csv')
EV_data = ReadEVData(share_of_CP=0.3, no_of_EVs=25)



"""I effekttariff må man ha en liste med de tre høyeste peakene, dette blir en variabel, den må sjekke alle peakene og kaste ut 
   den laveste dersom det er mulig, tilslutt må den bestemme seg for hvile sone den er i og få en kostnad knyttet til dette"""


# Define constants
'''
Her må vi definerer konstanter som feks batteriparametere etc.
'''
EV_battery_energy_cap = FindMonthlyChargeEnergy(EV_data)
EV_battery_power_cap = EV_data['Available']

constants = {'Battery energy capacity': 80, #kWh
             'Initial State of Charge': 0, #kWh
             'Charge capacity': 80*0.20, #kW
             'Dishcharge capacity': 80*0.20, #kW
             'eta': 0.975,
             'EV battery energy capcaity': EV_battery_energy_cap*0.40, #kWh, ganger med andel som anses som fleksiblet
             'EV battery power capacity': EV_battery_power_cap
             }


# Mathematical formulation
'''
Her må objekticfunskjonen sammen med alle constraintsene være definert først, så må modellen settes opp
'''

def Obj(m):
    return sum((m.C_spot[t] + m.C_grid[t] )*m.y[t] for t in m.T)



def HouseEnergyBalance(m, t):
    return m.y_house[t] == m.D[t] + m.e_cha[t] - m.e_dis[t] 

def EVEnergyBalance(m, t):
    return m.y_EV[t] == m.D_EV[t] + m.e_EV_cha[t] - m.e_EV_dis[t]

def GridImport(m, t):
    return m.y[t] == m.y_house[t] + m.y_EV[t]



def SoC(m, t):
    if t == 0:
        return m.b[0] == m.e_cha[0]*m.eta - m.e_dis[0]/m.eta + m.SoC0
    else:
        return m.b[t] == m.e_cha[t]*m.eta - m.e_dis[t]/m.eta + m.b[t-1]
    
def SoCCap(m, t):
    return m.b[t] <= m.BatteryCap
    
def ChargeCap(m, t):
    return m.e_cha[t] <= m.BatteryChargeCap

def DischargeCap(m, t):
    return m.e_dis[t] <= m.BatteryDischargeCap

"""
MÅ LAGE EN B FOR ELBILBATTERIET!! OG FINNE EN INITIAL?
     
"""

def SoC_EV(m, t):
    if t == 0:
        return m.b_EV[0] == m.e_EV_cha[0]*m.eta - m.e_EV_dis[0]/m.eta 
    else:
        return m.b_EV[t] == m.e_EV_cha[t]*m.eta - m.e_EV_dis[t]/m.eta + m.b_EV[t-1]
    
def SoCCap_EV(m, t):
    return m.b_EV[t] <= m.EV_BatteryEnergyCap
    
def ChargeCap_EV(m, t):
    return m.e_EV_cha[t] <= m.EV_BatteryPowerCap[t]

def DischargeCap_EV(m, t):
    return m.e_EV_dis[t] <= m.EV_BatteryPowerCap[t]


def ModelSetUp(SpotPrice, EnergyTariff, Demand, EV_data, constants): #Set up the optimisation model
    #Instance
    m = pyo.ConcreteModel()

    #Set
    m.T = pyo.RangeSet(0, 743) #24 hours/day * 31 days/month = 744 hours
    
    #Paramters
    m.C_spot              = pyo.Param(m.T, initialize = SpotPrice) #spot price input for the month
    m.C_grid              = pyo.Param(m.T, initialize = EnergyTariff) #energy part of grid tariff
    m.D                   = pyo.Param(m.T, initialize = Demand) #aggregated household demand
    m.D_EV                = pyo.Param(m.T, initialize = EV_data['Charging']) #aggregated EV demand
    m.SoC0                = pyo.Param(initialize = constants['Initial State of Charge']) #Initial state of charge of the batter
    m.BatteryCap          = pyo.Param(initialize = constants['Battery energy capacity']) #Max battery energy capacity [kWh]
    m.BatteryChargeCap    = pyo.Param(initialize = constants['Charge capacity']) #Charging speed/battery power capacity [kW]
    m.BatteryDischargeCap = pyo.Param(initialize = constants['Dishcharge capacity']) #Disharging speed/battery power capacity [kW]
    m.eta                 = pyo.Param(initialize = constants['eta']) #efficiency of charge/discharge
    m.EV_BatteryEnergyCap = pyo.Param(initialize = constants['EV battery energy capcaity'])
    m.EV_BatteryPowerCap  = pyo.Param(m.t, initialize = constants['EV battery power capacity'])
    

    #Variables
    m.y_house   = pyo.Var(m.T, within = pyo.NonNegativeReals) # imported energy from the grid to the house [kWh]
    m.y_EV      = pyo.Var(m.T, within = pyo.NonNegativeReals) # imported energy from the grid to the EV [kWh]
    m.y_total   = pyo.Var(m.T, within = pyo.NonNegativeReals) # imported energy from the grid in total [kWh]
    m.b         = pyo.Var(m.T, within = pyo.NonNegativeReals) # battery SoC [kWh]
    m.e_cha     = pyo.Var(m.T, within = pyo.NonNegativeReals) # energy charged to the battery [kWh]
    m.e_dis     = pyo.Var(m.T, within = pyo.NonNegativeReals) # energy disherged from the battery [kWh]
    m.b_EV      = pyo.Var(m.T, within = pyo.NonNegativeReals) # EV battery SoC [kWh]
    m.e_EV_cha  = pyo.Var(m.T, within = pyo.NonNegativeReals) # energy charged to the battery [kWh]
    m.e_EV_dis  = pyo.Var(m.T, within = pyo.NonNegativeReals) # energy disherged from the battery [kWh]

    #Constraints
    m.HouseEnergyBalance    = pyo.Constraint(m.T, rule = HouseEnergyBalance)
    m.EVEnergyBalance       = pyo.Constraint(m.T, rule = EVEnergyBalance)
    m.GridImport            = pyo.Constraint(m.T, rule = GridImport)
    m.SoC                   = pyo.Constraint(m.T, rule = SoC)
    m.SoCCap                = pyo.Constraint(m.T, rule = SoCCap)
    m.ChargeCap             = pyo.Constraint(m.T, rule = ChargeCap) 
    m.DischargeCap          = pyo.Constraint(m.T, rule = DischargeCap)

    #Objective function
    m.Obj = pyo.Objective(rule = Obj, sense = pyo.minimize)

    return m

def Solve(m):
    opt = SolverFactory('gurobi')
    return opt.solve(m, load_solutions = True)

# Solving and presenting the data
'''
Her må vi solve og lagre data, gjerne presentere i gode visuelle grafer
'''

def Graphical_results(m):
    demand = []
    EV_demand = []
    price = []
    battery = []
    y = []
    hours = []

    for t in m.T:
        hours.append(t)
        demand.append(m.D[t])
        EV_demand.append(m.D_EV[t])
        price.append(m.C_spot[t])
        battery.append(m.b[t].value)
        y.append(m.y_total[t].value)


    fig, ax1 = plt.subplots()
    ax1.plot(hours, battery, label='State of Charge', color='tab:green')
    ax1.plot(hours, y, label='Power import', color='tab:red')
    ax1.plot(hours, demand, color ='tab:orange', linestyle = '--', label='Demand')
    ax1.plot(hours, EV_demand, color = 'tab:grey', linestyle = '--', label = 'EV demand')
    ax1.set_xlabel('Hours')
    ax1.set_xticks(hours)
    ax1.set_ylabel('Power [kW]')
    ax1.legend(loc = 'upper left')

    ax2 = ax1.twinx() #Creates a second y-axis on the right
    ax2.plot(hours, price, label = 'Spotprice', color = 'tab:blue')
    ax2.set_ylabel('Spot Price [NOK/kWh]')
    ax2.legend(loc = 'upper right')

    
    fig.tight_layout()  # Adjust layout to prevent overlapping
    plt.title('Results from optimization problem')
    plt.show()

m = ModelSetUp(SpotPrice, EnergyTariff, Demand, EV_data, constants)
Solve(m)
Graphical_results(m)
print(pyo.value(m.Obj))
