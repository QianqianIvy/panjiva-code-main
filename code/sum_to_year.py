# %%
#Packages needed to run code
import pandas as pd
from pathlib import Path
import time

# **Readme
# This code is for summing the volumeTEU by year, conPanjivaId and shpPanjivaId to get monthly data
# missing value convert to 999, drop rows with non numeric conPanjivaId and shpPanjivaId

#####################################
# Read raw data
#####################################

#set timer
start_time = time.time()
#read the each csv file in the folder Processed_data/USImport

directory = "/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport"
files = Path(directory).glob('*address.csv')


#List to store dataframes
fileData = []
#For each file in the folder
for file in files:
    print(file)
    #Read the file
    df = pd.read_csv(file)

    # drop rows with non numeric conPanjivaId and shpPanjivaId
    df['conPanjivaId'] = df['conPanjivaId'].astype(str)
    df['shpPanjivaId'] = df['shpPanjivaId'].astype(str)

    df = df[df['conPanjivaId'].str.isnumeric()]
    df = df[df['shpPanjivaId'].str.isnumeric()]

     #change conPanjivaId, shpPanjivaId, year, month, day to int

    df['conPanjivaId'] = pd.to_numeric(df['conPanjivaId'], errors='coerce').astype('Int64')
    df['shpPanjivaId'] = pd.to_numeric(df['shpPanjivaId'], errors='coerce').astype('Int64')
    
    #change conPanjivaId, shpPanjivaId, year, month, day to int
    df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')
    df['month'] = pd.to_numeric(df['month'], errors='coerce').astype('Int64')
    df['day'] = pd.to_numeric(df['day'], errors='coerce').astype('Int64')

    # drop if year month day is na/nan
    df = df.dropna(subset=['year', 'month', 'day'])

    #Add the file to the list
    fileData.append(df)

# concatenate all files in files
importus = pd.concat(fileData)

#store importus into importus_copy
importus_copy = importus.copy()

#####################################
# calculate days between shipments
#####################################
# caculater the days from last shipment
importus['date_str'] = importus['year'].astype(str) + importus['month'].astype(str).str.zfill(2) + importus['day'].astype(str).str.zfill(2)
# Convert the combined string column to datetime
importus['date'] = pd.to_datetime(importus['date_str'], format='%Y%m%d')

# Drop the temporary 'date_str' column
importus = importus.drop(columns=['date_str'])

# Continue with the rest of your code
importus = importus.sort_values(['conPanjivaId', 'shpPanjivaId', 'date'])
importus['days_from_last_shipment'] = importus.groupby(['conPanjivaId', 'shpPanjivaId'])['date'].diff().dt.days

# caculate the average days_from_last_shipment by year, conPanjivaId, shpPanjivaId
# importus['days_from_last_shipment'] = importus['days_from_last_shipment'].fillna(999)
importus['average_days_from_last_shipment'] = importus.groupby(['year', 'conPanjivaId', 'shpPanjivaId'])['days_from_last_shipment'].transform('mean')

#drop the column days_from_last_shipment
importus = importus.drop(columns=['days_from_last_shipment'])


#####################################
# group by year
#####################################

#sum volumeTEU by year, month, conPanjivaId and shpPanjivaId but also keep other columns
# aggregate the volumeTEU by year, conName, conPanjivaId, shpPanjivaId, conCountry, shpCountry, shpmtDestination, conFullAddress, conRoute, conCity, conStateRegion, conPostalCode
aggregated_df = importus.groupby(['year', 'conName', 'conPanjivaId', 'shpPanjivaId', 'conCountry', 'shpCountry', 'shpmtDestination', 'conFullAddress', 'conRoute', 'conCity', 'conStateRegion', 'conPostalCode']).agg({'volumeTEU': 'sum'}).reset_index()
aggregated_df = aggregated_df.rename(columns={'volumeTEU': 'Total_teu'})
importus = importus.merge(aggregated_df, on=['year', 'conName', 'conPanjivaId', 'shpPanjivaId', 'conCountry', 'shpCountry', 'shpmtDestination', 'conFullAddress', 'conRoute', 'conCity', 'conStateRegion', 'conPostalCode'], how='left')

# duplicate into paris level and year level
importus = importus.drop(columns=['panjivaRecordId', 'date', 'month', 'day', 'volumeteu'])
importus = importus.drop_duplicates()
importus.head()


# calculate the number of distinct shpPanjivaId for each conPanjivaId by year
importus['num_distinct_shpPanjivaId'] = importus.groupby(['year', 'conPanjivaId'])['shpPanjivaId'].transform('nunique')


# change columns names to lower case
importus.columns = importus.columns.str.lower()

# only keep rows if concountry is United States or NaN/Na
importus = importus[(importus['concountry'] == 'United States')| (importus['concountry'].isnull())]

# export importus into csv file
importus.to_csv('/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/monthly/USImport_annual.csv', index=False)


#calculate the time it takes to run the code
print("--- %s seconds ---" % (time.time() - start_time))

# %%