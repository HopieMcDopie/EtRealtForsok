import pyomo.environ as pyo
import matplotlib .pyplot as plt
from Formulation import Solve, ModelSetUp, Initialize_Case
from OutputData import Graphical_Results, Store_Results_In_File, Box_Plots, Cost_Of_Flex, Test
from SpotPrice import SpotPrices
from GridTariff import GridTariffEnergy, GridTariffPower
from EVData import ReadEVData, FindMonthlyChargeEnergy
from ConsumptionData import ReadCSVDemandFile

"""
________________________________________________
#### THE OPTIMISATION MODEL IS RUN FROM HERE###
¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨
"""
if __name__ == "__main__":

    normal_run = True #Set to false if you want to print marginal cost of flexibility curve



    if normal_run == True:
    ###User imput to define the scenarios    
        what2run = input('\n\nDefine the case to be run: \n     Base Case: write "b" \n     Case 1: write "1"\n     Case 2: write "2"\n     Case 3: write "3"\nAnswer: ')
        case_dict = Initialize_Case(what2run) #decides what case to be run
    ###Gather input values to be used in "ModelSetUp" function:
    SpotPrice = SpotPrices() # Gives the spot prices for NO3 for january 2024, hourly resolution
    EnergyTariff = GridTariffEnergy() # Gives the energy part of the grid tariff for NO3, hourly resolution
    PowerTariff = GridTariffPower() # Gives the power part of the grid tariff for NO3
    Demand = ReadCSVDemandFile('AustinDemand.csv') # Gives the demand for 25 households for a month, hourly resolution
    EV_data = ReadEVData(share_of_CP=0.3, no_of_EVs=25) # Gives the available power in the area and the demand for a 
                                                    # given number of EVs for a month, hourly resolution, note that share_of_CP 
                                                    # is the share of private charging points

    ###These constants are linked to the shared community battery
    batt_const = {'Battery energy capacity': 80, #kWh
                  'Initial State of Charge': 0, #kWh
                  'Charge capacity': 80*0.20, #kW
                  'Dishcharge capacity': 80*0.20, #kW
                  'eta_cha': 0.85, #BESS charging capacity
                  'eta_dis': 0.95} #BESS discharging capacity

    ###Determening how flexibility for EV-charging is modelled
    flex_const = {'Monthly energy' : FindMonthlyChargeEnergy(EV_data), #kWh
                  'Flexible': 0.3} # %

    if normal_run == True:
        ###Setting up and solving the model
        m = ModelSetUp(SpotPrice, EnergyTariff, PowerTariff, Demand, EV_data, batt_const, flex_const, case_dict) #Setting up the optimization model
        Solve(m) #Solvign the optimisation problem

        ###Getting data for the hour of IBDR
        # print(pyo.value(m.D[674]))
        # print(pyo.value(m.e_cha[674]))
        # print(pyo.value(m.D_EV[674]))
        # print(pyo.value(m.e_EV_cha[674]))
        # print(pyo.value(m.y_imp[674]))

        ###Support functions to store and present data
        #Store_Results_In_File(m, what2run) #Storing output values in an excel sheet
        Graphical_Results(m, what2run) #Printing graphical results of values from optimisation values
        #Box_Plots(m)

        ###Prints
        print(f'Objective function: {pyo.value(m.Obj):.2f} NOK')
        y_peak = [m.y_imp[t].value for t in m.T]
        print(f'Peak power imported during the month: {max(y_peak):.2f} kW')
        print(f'Cost of respective grid tariff power price bracket: {pyo.value(m.C_grid_power):.2f} NOK')
        ENS = [m.ENS[t].value for t in m.T]
        if any(value != 0 for value in ENS):
            print(f'!! There is {max(ENS):.5f} kWh energy not supplied in the model!!')
    
    else:
        #Cost_Of_Flex(SpotPrice, EnergyTariff, PowerTariff, Demand, EV_data, batt_const, flex_const)
        Test(SpotPrice, EnergyTariff, PowerTariff, Demand, EV_data, batt_const, flex_const)


