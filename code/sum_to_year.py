# %%
#Packages needed to run code
import pandas as pd
from pathlib import Path
import time
# %%
# **Readme
# This code is for summing the volumeTEU by year, conPanjivaId and shpPanjivaId to get monthly data
# missing value convert to 999, drop rows with non numeric conPanjivaId and shpPanjivaId

#####################################
# Read raw data
#####################################

#set timer
start_time = time.time()
#read the each csv file in the folder Processed_data/USImport
directorys = ["/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/2015-2019", "/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/2020-2024"]
for directory in directorys:
    files = Path(directory).glob('*address.csv')
    #List to store dataframes
    fileData = []
    #For each file in the folder
    for file in files:
        print(file)
        #Read the file
        df = pd.read_csv(file)

        # drop rows with non numeric conPanjivaId and shpPanjivaId
        #### Important!!! this code also delets NAN values in conPanjivaId and shpPanjivaId
        df = df[df['conPanjivaId'].astype(str).str.isnumeric() & df['shpPanjivaId'].astype(str).str.isnumeric()]


        #change conPanjivaId, shpPanjivaId, year, month, day to int

        # df['conPanjivaId'] = pd.to_numeric(df['conPanjivaId'], errors='coerce').astype('Int64')
        # df['shpPanjivaId'] = pd.to_numeric(df['shpPanjivaId'], errors='coerce').astype('Int64')
        
        #change conPanjivaId, shpPanjivaId, year, month, day to int
        # df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')
        # df['month'] = pd.to_numeric(df['month'], errors='coerce').astype('Int64')
        # df['day'] = pd.to_numeric(df['day'], errors='coerce').astype('Int64')

        df[['conPanjivaId', 'shpPanjivaId', 'year', 'month', 'day']] = df[['conPanjivaId', 'shpPanjivaId', 'year', 'month', 'day']].apply(pd.to_numeric, errors='coerce')
        # drop if year month day is na/nan
        df.dropna(subset=['year', 'month', 'day'], inplace=True)

        #Add the file to the list
        fileData.append(df)

    # concatenate all files in files
    importus = pd.concat(fileData)


    #####################################
    # calculate days between shipments
    #####################################
    # caculater the days from last shipment
    importus['date_str'] = importus['year'].astype(str) + importus['month'].astype(str).str.zfill(2) + importus['day'].astype(str).str.zfill(2)
    # Convert the combined string column to datetime
    importus['date'] = pd.to_datetime(importus['date_str'], format='%Y%m%d')

    # Drop the temporary 'date_str' column
    importus = importus.drop(columns=['date_str'])

    # save every year data into csv file separately
    for year in importus['year'].unique():
        importus_year = importus[importus['year'] == year]
        importus_year.to_csv(f'/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/annual/USImport_{year}.csv', index=False)

#calculate the time it takes to run the code
print("--- %s seconds ---" % (time.time() - start_time))


# %%
#Packages needed to run code
import pandas as pd
from pathlib import Path
import time
import os
# **Readme
# This code is for summing the volumeTEU by year, conPanjivaId and shpPanjivaId to get monthly data

#####################################
# Read raw data
#####################################

#set timer
start_time = time.time()
#read the each csv file in the folder Processed_data/USImport

directory = "/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/annual"
#files = Path(directory).glob('USImport_*.csv')

#List to store dataframes
fileData = []
fileData_truncted = []
#For each file in the folder
# List of years you want to read files for
years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

for y in years:
    filename = f'USImport_{y}.csv'  # Assuming the files are in CSV format
    filepath = os.path.join(directory, filename)
    df_year = pd.read_csv(filepath)
    #sum volumeTEU by year, month, conPanjivaId and shpPanjivaId but also keep other columns
    # aggregate the volumeTEU by year, conName, conPanjivaId, shpPanjivaId, conCountry, shpCountry, shpmtDestination, conFullAddress, conRoute, conCity, conStateRegion, conPostalCode
    aggregated_df_year = df_year.groupby(['conName', 'conPanjivaId', 'shpPanjivaId', 
                                          'conCountry', 'shpCountry', 'shpmtDestination', 
                                          'conFullAddress', 'conRoute', 'conCity', 'conStateRegion', 
                                          'conPostalCode']).agg({'volumeTEU': 'sum'}).reset_index()
    aggregated_df_year = aggregated_df_year.rename(columns={'volumeTEU': 'Total_teu'})
    df_year = df_year.merge(aggregated_df_year, on=['conName', 'conPanjivaId', 'shpPanjivaId', 'conCountry', 'shpCountry', 'shpmtDestination', 'conFullAddress', 'conRoute', 'conCity', 'conStateRegion', 'conPostalCode'], how='left')

    # calculate the number of distinct shpPanjivaId for each conPanjivaId by year
    df_year['num_distinct_shpPanjivaId'] = df_year.groupby(['conPanjivaId'])['shpPanjivaId'].transform('nunique')

    # only keep conPanjivaId and shpPanjivaId and date
    df_year_truncted = df_year[['conPanjivaId', 'shpPanjivaId', 'date', 'year']]
    # ******** need to mention: duplicated rows are dropped ******
    df_year_truncted = df_year_truncted.drop_duplicates()
    fileData_truncted.append(df_year_truncted)

    # duplicate into paris level and year level
    df_year = df_year.drop(columns=['panjivaRecordId', 'date', 'month', 'day', 'volumeTEU'])
    df_year = df_year.drop_duplicates()
    df_year.head()

    # export df_year to csv file
    df_year.to_csv(f'/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/annual/USImport_{y}_index.csv', index=False)


# concatenate all files in files
importus_delay_days = pd.concat(fileData_truncted)

# # in case the laptop cannot handle the data, save the data into csv file
# importus_delay_days.to_csv('/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/annual/USImport_delay_days.csv', index=False)


# # read csv file
# importus_delay_days = pd.read_csv('/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/annual/USImport_delay_days.csv')

importus_delay_days['date'] = pd.to_datetime(importus_delay_days['date'])
# caculate the days from last shipment
importus_delay_days = importus_delay_days.sort_values(['conPanjivaId', 'shpPanjivaId', 'date'])

importus_delay_days['days_from_last_shipment'] = importus_delay_days.groupby(['conPanjivaId', 'shpPanjivaId'])['date'].diff().dt.days

# caculate the average days_from_last_shipment by year, conPanjivaId, shpPanjivaId
# importus['days_from_last_shipment'] = importus['days_from_last_shipment'].fillna(999)
importus_delay_days['average_days_from_last_shipment'] = importus_delay_days.groupby(['year', 'conPanjivaId', 'shpPanjivaId'])['days_from_last_shipment'].transform('mean')

#drop the column days_from_last_shipment
importus_delay_days = importus_delay_days.drop(columns=['days_from_last_shipment'])
# duplicate into paris level and year level 
importus_delay_days = importus_delay_days.drop_duplicates()

for y in years:
    filename = f'USImport_{y}_index.csv'  # Assuming the files are in CSV format
    filepath = os.path.join(directory, filename)
    df_year = pd.read_csv(filepath)
    # merge importus_two_index and importus_delay_days by 'year', 'conPanjivaId', 'shpPanjivaId'
    importus = df_year.merge(importus_delay_days, on=['year', 'conPanjivaId', 'shpPanjivaId'], how='left')
    # save the data into csv file
    importus.to_csv(f'/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/annual/USImport_{y}_three_index.csv', index=False)

#calculate the time it takes to run the code
print("--- %s seconds ---" % (time.time() - start_time))

# %% 

