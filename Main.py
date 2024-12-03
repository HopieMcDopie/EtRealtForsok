import pyomo.environ as pyo
import matplotlib .pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from Formulation import Solve, ModelSetUp, Initialize_Case
from OutputData import Graphical_Results, Store_Results_In_File, Box_Plots
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
    what2run = input('\n\nDefine the case to be run: \n     Base Case: write "b" \n     Case 1: write "1"\n     Case 2: write "2"\n     Case 3: write "3"\nAnswer: ')

    #Gather input values to be used in "ModelSetUp" function:
    case_dict = Initialize_Case(what2run) #decides what case to be run
    # case_dict = {'flexible_EV_on': True,      #flexible EV charge not active
    #             'battery_on': True,           #community BESS not active
    #             'power_grid_tariff_on': True,  #grid tariff not active
    #             'step_grid_tariff': True,      #stepwise grid tariff active
    #             'IBDR_on': True,              #incentive base demand response not active
    #             'hour_restricted': 674,
    #             'power_restricted': 0}
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
                  'eta_cha': 0.85, #BESS charging capacity
                  'eta_dis': 0.95} #BESS discharging capacity

    #Determening how flexibility for EV-charging is modelled
    flex_const = {'Monthly energy' : FindMonthlyChargeEnergy(EV_data), #kWh
                  'Flexible': 0.3} # %

    m = ModelSetUp(SpotPrice, EnergyTariff, PowerTariff, Demand, EV_data, batt_const, flex_const, case_dict)
    Solve(m) #Solvign the optimisation problem
    #Store_Results_In_File(m, what2run) #Storing output values in an excel sheet
    Graphical_Results(m) #Printing graphical results of values from optimisation values
    print(f'Objective function: {pyo.value(m.Obj):.2f} NOK')
    print(f'Peak power imported during the month: {pyo.value(m.peak):.2f} kW')
    print(f'Cost of respective grid tariff power price bracket: {pyo.value(m.C_grid_power):.2f} NOK')
    ENS = [m.ENS[t].value for t in m.T]
    if any(value != 0 for value in ENS):
        print('!! There is energy not supplied in the model!!')
    Box_Plots(m)

    # y_lim = np.linspace(9, 80, 30)
    # obj_value = []

    # for limit in y_lim:
    #     case_dict['power_restricted'] = limit

    #     m = ModelSetUp(SpotPrice, EnergyTariff, PowerTariff, Demand, EV_data, batt_const, flex_const, case_dict)
    #     Solve(m)

    #     obj_value.append(pyo.value(m.Obj))

    # plt.step(y_lim, obj_value)
    # plt.show()
    
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

    # print(obj_value)
    # obj_value_reversed = obj_value[::-1]
    # print(obj_value_reversed)
    # delta_obj_value = [0]
    # for i in range(1, len(obj_value_reversed)):
    #     delta_obj_value.append(obj_value_reversed[i]-obj_value_reversed[i-1])
    # print(delta_obj_value)

    # y_lim_reversed = y_lim[::-1]
    # plt.step(y_lim_reversed, delta_obj_value)
    # plt.show()


