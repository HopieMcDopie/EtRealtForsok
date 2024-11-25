import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

#__________________________________#
##### DATA PROCESSING FUNCTION #####
#¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨#

def check_nan(temp_df): # create a function to check for NaN values in df columns: grid, solar, solar2

    #checking nan values in grid column
    check_nan = temp_df['grid'].isna().any()
    #print(check_nan)

    #fill the nan values in grid column using ffill method
    temp_df['grid'] = temp_df['grid'].ffill()
    
    # check again to make sure the above method worked
    check_nan = temp_df['grid'].isna().any()
    #print(check_nan)

    # check nan in solar column
    check_nan = temp_df['solar'].isna().any()
    #print(check_nan)
    # replace the nan values  with zero in solar column
    temp_df.fillna({'solar': 0}, inplace = True)
    # check again
    check_nan = temp_df['solar'].isna().any()
    #print(check_nan)

    # check nan in solar2
    check_nan = temp_df['solar2'].isna().any()
    #print(check_nan)
    # replace the nan values  with zero in solar2 column
    temp_df.fillna({'solar2': 0}, inplace = True)
    # check again
    check_nan = temp_df['solar2'].isna().any()
    #print(check_nan)   
    return temp_df

def check_timestamp(temp_df):# check for missing timestamp by sorting the dataframe in ascending order with column localminute using sort_values function
    temp_df= temp_df.sort_values(by='localminute', ascending=True)
    temp_df=temp_df.set_index('localminute')  

    # use reindex function to introduce missing timestamps and use ffill to fill values in those       
    temp_df= temp_df.reindex(pd.date_range(start=temp_df.index.min(), end=temp_df.index.max(), freq='min'))
    temp_df.index.name = "localminute"        
    return temp_df

def sum_data(temp_df):# sum the values of grid, solar and solar 2 row wise and assign it to the column total consumption.
    total= temp_df[['grid', 'solar', 'solar2']].sum(axis=1)
    temp_df['total_consumption']=total    
    return temp_df

def check_negative_consumption(temp_df): # check if there are any negative values in total_consumption column
    negative_rows= temp_df[temp_df[('total_consumption')] < 0]
    
def resample_data(temp_df): # resample the data to 60 minute frequency using resample function and use mean method    
    temp_df= temp_df.resample('60min').mean()       
    return temp_df

def extract_time_features(wat): # use datetime index function to extract following features/values from localminute column 
    wat=wat.reset_index()
    wat['day']= wat['localminute'].dt.day
    wat['month']= wat['localminute'].dt.month
    wat['day_of_week']= wat['localminute'].dt.dayofweek
    wat['hour']= wat['localminute'].dt.hour
    wat['weekend']=(wat['day_of_week'] > 4).astype(float)
    wat.set_index('localminute')  
    return wat

def extract_cons_features(temp_df): # extract previous three consumption to the current timestep and assign it to c-1,c-2,c-3 (tip:check shift function and fill unavailable values with zero) 
    temp_df['c-1']= temp_df['total_consumption'].shift(1)
    temp_df['c-2']= temp_df['total_consumption'].shift(2)
    temp_df['c-3']= temp_df['total_consumption'].shift(3)
    temp_df=temp_df.fillna(0)
    return temp_df

def check_outliers(temp_df): # fill the appropriate z-score value to replace outlier values with nan in the next two lines   
    temp_df['total_consumption']=temp_df['total_consumption'].mask(np.abs(stats.zscore(temp_df['total_consumption'])) > 3,np.nan)
    temp_df['solar']=temp_df['solar'].mask(np.abs(stats.zscore(temp_df['solar'])) > 3,np.nan)
    temp_df['total_consumption']=temp_df['total_consumption'].ffill()
    temp_df['solar']=temp_df['solar'].ffill()  
    return temp_df


#_________________________________#
##### DATA ANALYSIS FUNCTIONS #####
#¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨#
def monthly_consumption(temp_df): # finding the montly consumption and plotting a bar graph
    consumption=list()
    solar_consumption=list()
    month=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']    
    for j in range(12): 
        val=temp_df.loc[j+1] #use loc function to get dataframe with only single month data.
        t_cons=val['total_consumption'].sum() # find monthly total consumption 
        sol_cons=val['solar'].sum() # find monthly solar contribution
        consumption.append(t_cons)
        solar_consumption.append(sol_cons)
    
    plt.bar(month, consumption)
    plt.title('monthly consumption')
    plt.bar(month, solar_consumption, color='y')
    plt.show()

def daily_consumption(temp_df, day=int): # finding the daily consumption and plotting it 
    consumption=list()
    hour=[i for i in range(1,25)]  
    if day == 1:
        h  = 1
    if day == 2:
        h = 24
    for j in range(h,h+24): 
        consumption.append(temp_df.loc[j,'total_consumption']*25)
    
    plt.figure()
    plt.grid(True, which='both', axis='y', linestyle='--', zorder=0)
    plt.bar(hour, consumption, color = 'tab:red')
    plt.title(f'Daily consumption, day {day}')
    plt.xlabel('Hour [h]')
    plt.xticks(hour)
    plt.ylabel('Consumption [kWh]')
    current_yticks = plt.yticks()[0]
    new_yticks = np.linspace(min(current_yticks), max(current_yticks), len(current_yticks) * 2 - 1)
    plt.yticks(new_yticks)
    plt.show()
    

#___________________________________________________________#
##### SPECIAL FUNCTION TO PREPARE FOR CONSUMPLTION DATA #####
#¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨#

def ReadAustinFile(data_file): # Read the data from the Austin file
    # load the excel file
    temp_df = pd.read_csv(data_file, delimiter = ';')

    # get dataid, localminute, grid and solar and solar2 
    keep =('dataid', 'localminute', 'grid', 'solar', 'solar2')
    df = temp_df.loc[:,keep] 

    #convert localminute datatype into datetime
    df['localminute']= pd.to_datetime(df['localminute'], format='%d.%m.%Y %H:%M', errors='coerce')

    # print unique values in dataid
    data_id = pd.unique(df['dataid'])

    #count how many houses' consumption data are in dataframe using data_id.
    num_houses = len(data_id) 

    #seaprate the data based on dataid and store it in a separate dataframe.
    client_data=list()

    for j in range(num_houses):
        #find the house numbers
        name=df.loc[df['dataid']==data_id[j]]
        name=name.drop(['dataid'], axis=1)    
        client_data.append(name) 
      
        #process the data using the functions
        client_data[j]=check_nan(client_data[j]) 
        client_data[j]=check_timestamp(client_data[j])  
        client_data[j]=sum_data(client_data[j])
        client_data[j]=resample_data(client_data[j])
        client_data[j]=extract_time_features(client_data[j])
        client_data[j]=extract_cons_features(client_data[j])
        check_negative_consumption(client_data[j])
        client_data[j]=check_outliers(client_data[j])  

    #create a dictionary for all the hours in the month
    daily_client_data = {hour: 0 for hour in range(24 * 31)}

    #save the aggregated data in the dictionary
    for hour in range(0,24*31):
        for cl_num in range(num_houses):
            daily_client_data[hour] += client_data[cl_num].loc[hour+1,'total_consumption']*25 # to fit better with norwegian values

        df1 = pd.DataFrame(list(daily_client_data.items()), columns = ['Hour', 'Total_Consumption'])

        '''
        
        this next code line has to be commented in to save the processed data in its own file!!
        
        '''
        #df1.to_csv('AustinDemand.csv', index = False, sep = ';')

    #plotting the data for visual representation
    plt.figure()
    plt.plot(df1['Total_Consumption']) # add [0:24] if one wants to only see day 1
    plt.show()

    return daily_client_data


def ReadCSVDemandFile(data_file):
    inputDayAhead = pd.read_csv(data_file, delimiter = ";")
    data = inputDayAhead.to_dict()
    CSV_Info = data['Total_Consumption']
    return CSV_Info

    
if __name__ == '__main__':
    # ________________TEST OF CODE_____________________
    # # load the excel file
    # temp_df = pd.read_csv('15minute_data_austin.csv', sep = ";") 

    # #prints column names
    # print('\n\nColumn names before:\n',list(temp_df.columns))

    # # get dataid, localminute, grid and solar and solar1 
    # keep =('dataid', 'localminute', 'grid', 'solar', 'solar2')
    # df = temp_df.loc[:,keep] 

    # #print all column names
    # print('\n\nColumn names after:\n',list(df.columns))

    # #convert localminute datatype into datetime
    # df['localminute']= pd.to_datetime(df['localminute'], format='%d.%m.%Y %H:%M', errors='coerce')
    # #print(df.dtypes) 

    # # print unique values in dataid
    # data_id = pd.unique(df['dataid'])
    # print('\n\nData IDs:\n',data_id)

    # #count how many houses' consumption data are in dataframe using data_id.
    # num_houses = len(data_id) 
    # print('\n\nNumber of houses:\n',num_houses)

    # #seaprate the data based on dataid and store it in a separate dataframe.
    # client_data=list()

    # for j in range(num_houses):
    #     #name=str(client_names[j])
    #     name=df.loc[df['dataid']==data_id[j]]
    #     name=name.drop(['dataid'], axis=1)    
    #     client_data.append(name)

    # #house number
    # cl_num=8
        
    # # data handeling     
    # client_data[cl_num]=check_nan(client_data[cl_num]) 
    # client_data[cl_num]=check_timestamp(client_data[cl_num])  
    # client_data[cl_num]=sum_data(client_data[cl_num])
    # client_data[cl_num]=resample_data(client_data[cl_num])
    # client_data[cl_num]=extract_time_features(client_data[cl_num])
    # client_data[cl_num]=extract_cons_features(client_data[cl_num])
    # check_negative_consumption(client_data[cl_num])
    # client_data[cl_num]=check_outliers(client_data[cl_num])

    # # printing restults
    # monthly_consumption(client_data[cl_num])
    # daily_consumption(client_data[cl_num], 1)




    # _______DATA PROCESSING FROM LARGE TO SMALLER FILE___________
    """
    Remember to uncomment/comment out line in ReadAustinFile-function if you want to store updated values!!
    """
    #HouseDemand = ReadAustinFile('15minute_data_austin.csv')
    #df = pd.DataFrame.from_dict(HouseDemand, orient='index', columns=['Total_Consumption'])

    # _________DATA PROCESSING OF SMALL FILE________
    demand = ReadCSVDemandFile('AustinDemand.csv')

    plt.figure()
    plt.plot(demand.values())
    plt.xlabel('hours')
    plt.ylabel('kW')
    plt.title('Aggregated demand of 25 households')
    plt.show()
    