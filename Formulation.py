import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from scipy import stats


# Data input
'''
Her må vi lese inn en måned med forbruksdata og en med prisdata. Disse må ha time-oppløsning og være i
fomatet pandas dataframe
'''

# Define constants
'''
Her må vi definerer konstanter som feks batteriparametere etc.
'''


# Mathematical formulation
'''
Her må objekticfunskjonen sammen med alle constraintsene være definert først, så må modellen settes opp
'''

def Obj():
    return




def ModelSetUp(SpotPrice, Demand): #Setup the opt. model
    #Instance
    m = pyo.ConcreteModel()

    #Set
    m.T = pyo.RangeSet(0, 24*31) #24 hours/day * 31 days/month
    
    #Paramters
    m.C    = pyo.Param(m.T, initialize = SpotPrice) #spot price input for the month
    m.D    = pyo.Param(m.T, initialize = Demand) #household demand
    m.SoC0 = pyo.Param(m.T, initialize = 0) #Initial state of charge of the batter
    m.BatteryCap = pyo.Param(initialize = 10) #Max battery energy capacity [kWh]
    m.BatteryChargeCap = pyo.Param(initialize = 2) #Charging speed/battery power capacity [kW]
    m.BatteryDishargeCap = pyo.Param(initialize = 2) #Disharging speed/battery power capacity [kW]
    m.eta = pyo.Param(initialize = 0.975) #efficiency of charge/discharge
    

    #Variables


    #Constraints


    #Objective function

    return m

def Solve(m):
    opt = SolverFactory('gurobi')
    return opt.solve(m, loadsolution = True)

# Solving and presenting the data
'''
Her må vi solve og lagre data, gjerne presentere i gode visuelle grafer
'''


Solve(m)