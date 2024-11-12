import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyomo.environ as pyo
from pyomo.opt import SolverFactory



# Data input
'''
Her må vi lese inn en måned med forbruksdata og en med prisdata. Disse må ha time-oppløsning og være i
fomatet pandas dataframe
'''

df = pd.DataFrame({
    'Random_Float': np.round(np.random.uniform(0, 100, 744), 2)
})
df.index = range(744)
SpotPrice = df



def ReadCSVDemandFile(data_file):
    inputDayAhead = pd.read_csv(data_file, delimiter = ";")
    data = inputDayAhead.to_dict()
    CSV_Info = data['Total_Consumption']
    return CSV_Info
Demand = ReadCSVDemandFile('AustinDemand.csv')


# Define constants
'''
Her må vi definerer konstanter som feks batteriparametere etc.
'''
constants = {'Battery energy capacity': 10,
             'Initial State of Charge': 0,
             'Charge capacity': 2,
             'Dishcharge capacity': 2,
             'eta': 0.975}


# Mathematical formulation
'''
Her må objekticfunskjonen sammen med alle constraintsene være definert først, så må modellen settes opp
'''

def Obj(m):
    return sum(m.C[t]*m.y[t] for t in m.T)

def EnergyBalance(m, t):
    return m.y[t] == m.D[t] + m.e_cha[t] - m.e_dis[t]

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


def ModelSetUp(SpotPrice, Demand, constants): #Setup the opt. model
    #Instance
    m = pyo.ConcreteModel()

    #Set
    m.T = pyo.RangeSet(0, 24*31-1) #24 hours/day * 31 days/month
    
    #Paramters
    m.C                  = pyo.Param(m.T, initialize = SpotPrice) #spot price input for the month
    m.D                  = pyo.Param(m.T, initialize = Demand) #household demand
    m.SoC0               = pyo.Param(initialize = constants['Initial State of Charge']) #Initial state of charge of the batter
    m.BatteryCap         = pyo.Param(initialize = constants['Battery energy capacity']) #Max battery energy capacity [kWh]
    m.BatteryChargeCap   = pyo.Param(initialize = constants['Charge capacity']) #Charging speed/battery power capacity [kW]
    m.BatteryDischargeCap = pyo.Param(initialize = constants['Dishcharge capacity']) #Disharging speed/battery power capacity [kW]
    m.eta                = pyo.Param(initialize = constants['eta']) #efficiency of charge/discharge
    

    #Variables
    m.b     = pyo.Var(m.T, within = pyo.NonNegativeReals) # battery SoC [kWh]
    m.y     = pyo.Var(m.T, within = pyo.NonNegativeReals) # imported energy from the grid [kWh]
    m.e_cha = pyo.Var(m.T, within = pyo.NonNegativeReals) # energy charged to the battery [kWh]
    m.e_dis = pyo.Var(m.T, within = pyo.NonNegativeReals) # energy disherged from the battery [kWh]

    #Constraints
    m.EnergyBalance = pyo.Constraint(m.T, rule = EnergyBalance)
    m.SoC           = pyo.Constraint(m.T, rule = SoC)
    m.SoCCap        = pyo.Constraint(m.T, rule = SoCCap)
    m.ChargeCap     = pyo.Constraint(m.T, rule = ChargeCap) 
    m.DischargeCap  = pyo.Constraint(m.T, rule = DischargeCap)

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
    price = []
    battery = []
    y = []
    hours = []

    for t in m.T:
        hours.append(t)
        demand.append(m.D[t])
        price.append(m.C[t])
        battery.append(m.b[t].value)
        y.append(m.y[t].value)

    plt.figure()
    plt.plot(hours, price)
    plt.show()

m = ModelSetUp(SpotPrice, Demand, constants)
Solve(m)
Graphical_results(m)
