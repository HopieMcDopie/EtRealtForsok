import pyomo.environ as pyo
from Formulation import Solve, ModelSetUp, Initialize_Case
from OutputData import Graphical_Results, Store_Results_In_File
from SpotPrice import SpotPrices
from GridTariff import GridTariffEnergy, GridTariffPower
from EVData import ReadEVData, FindMonthlyChargeEnergy
from ConsumptionData import ReadCSVDemandFile

"""
__________________________________________
#### THE OPTIMISATION MODEL IS RUN HERE###
¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨
"""
if __name__ == "__main__":
    #User imput to define the scenarios
    what2run = input('Define the case? \n    If base case with no flexibility, write "base" \n    If flexibility only considering spot prices, write "spot"\n    If flexibility both spot and grid tariff prices, write "spot and grid"\nAnswer: ')

    #Gather input values to be used in "ModelSetUp" function:
    flexible_EV_on, battery_on, power_grid_tariff_on, step_grid_tariff = Initialize_Case(what2run)
    SpotPrice = SpotPrices() # Gives the spot prices for NO3 for january 2024, hourly resolution
    EnergyTariff = GridTariffEnergy() # Gives the energy part of the grid tariff for NO3, hourly resolution
    PowerTariff = GridTariffPower() # Gives the power part of the grid tariff for NO3
    Demand = ReadCSVDemandFile('AustinDemand.csv') # Gives the demand for 25 households for a month, hourly resolution
    EV_data = ReadEVData(share_of_CP=0.3, no_of_EVs=25) # Gives the available power in the area and the demand for a 
                                                    # given number of EVs for a month, hourly resolution, note that share_of_CP 
                                                    # is the share of private charging points

    # These constants are linked to the shared community battery
    batt_const = {'Battery energy capacity': 80, #kWh
                  'Initial State of Charge': 0, #kWh
                  'Charge capacity': 80*0.20, #kW
                  'Dishcharge capacity': 80*0.20, #kW
                  'eta': 0.975}

    #Determening how flexibility for EV-charging is modelled
    flex_const = {'Monthly energy' : FindMonthlyChargeEnergy(EV_data), #kWh
                  'Flexible': 0.3} # %

    m = ModelSetUp(SpotPrice, EnergyTariff, PowerTariff, Demand, EV_data, batt_const, flex_const, flexible_EV_on, battery_on, power_grid_tariff_on, step_grid_tariff)
    Solve(m) #Solvign the optimisation problem
    Store_Results_In_File(m, what2run) #Storing output values in an excel sheet
    Graphical_Results(m) #Printing graphical results of values from optimisation values
    print(f'Objective function: {pyo.value(m.Obj):.2f} NOK')
    print(f'Peak power imported during the month: {pyo.value(m.peak):.2f} kW')
    print(f'Cost of respective grid tariff power price bracket: {pyo.value(m.C_grid_power):.2f} NOK')
