# %%
#Packages needed to run code
import pandas as pd
from pathlib import Path
import time

#set timer
start_time = time.time()
#read the each csv file in the folder Processed_data/USImport

directory = "/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport"
files = Path(directory).glob('*.csv')

#List to store dataframes
fileData = []
#For each file in the folder
for file in files:
    print(file)
    #Read the file
    df = pd.read_csv(file)

    # drop rows with non numeric conPanjivaId and shpPanjivaId and keep NA/NaN
    df['conPanjivaId'] = df['conPanjivaId'].fillna(999)
    df['shpPanjivaId'] = df['shpPanjivaId'].fillna(999)
    # Ensure the column is of string type
    df['conPanjivaId'] = df['conPanjivaId'].astype(str)
    df['shpPanjivaId'] = df['shpPanjivaId'].astype(str)
    # drop rows with non numeric conPanjivaId and shpPanjivaId
    df = df[df['conPanjivaId'].str.isnumeric()]
    df = df[df['shpPanjivaId'].str.isnumeric()]

    #change conPanjivaId, shpPanjivaId, year, month, day to int
    df['conPanjivaId'] = df['conPanjivaId'].astype(int)
    df['shpPanjivaId'] = df['shpPanjivaId'].astype(int)
    df['year'] = df['year'].fillna(999).astype(int)
    df['month'] = df['month'].fillna(999).astype(int)
    df['day'] = df['day'].fillna(999).astype(int)

    #Add the file to the list
    fileData.append(df)

#concatenate all files in files
importus = pd.concat(fileData)

# drop if year month day is 999
importus = importus[importus['year'] != 999]
importus = importus[importus['month'] != 999]
importus = importus[importus['day'] != 999]

# caculater the days from last shipment
importus['date_str'] = importus['year'].astype(str) + importus['month'].astype(str).str.zfill(2) + importus['day'].astype(str).str.zfill(2)
# Convert the combined string column to datetime
importus['date'] = pd.to_datetime(importus['date_str'], format='%Y%m%d')

# Drop the temporary 'date_str' column
importus = importus.drop(columns=['date_str'])

# Continue with the rest of your code
importus = importus.sort_values(['conPanjivaId', 'shpPanjivaId', 'date'])
importus['days_from_last_shipment'] = importus.groupby(['conPanjivaId', 'shpPanjivaId'])['date'].diff().dt.days

print(importus.head(10))

# # summary statistics of days_from_last_shipment
# print(importus['days_from_last_shipment'].describe())

# # print the number of missing values in days_from_last_shipment
# print(importus['days_from_last_shipment'].isnull().sum())

# drop volumeTEU and PanjivaId columns
importus_try = importus.drop(columns=['panjivaRecordId'])
print(importus_try.shape)
importus_try = importus.drop(columns=['volumeTEU'])
print(importus_try.shape)

# duplicate rows
importus_try = importus_try.drop_duplicates()
print(importus_try.shape)

# drop if shpPanjivaId, conPanjivaId is 999
importus_try = importus_try[importus_try['shpPanjivaId'] != 999]
importus_try = importus_try[importus_try['conPanjivaId'] != 999]

# keep if conCountry is US or null
importus_try = importus_try[(importus_try['conCountry'] == 'US')| (importus_try['conCountry'].isnull())]

# save importus_try into csv file
importus_try.to_csv('/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/delay_days.csv', index=False)

#calculate the time it takes to run the code
print("--- %s seconds ---" % (time.time() - start_time))

# print the number of unique values of conPanjivaId in import_us
print(importus['conPanjivaId'].nunique())
# print the number of unique values of pairs of conPanjivaID, shpPanjivaId in import_us
print(importus.groupby(['conPanjivaId', 'shpPanjivaId']).size().reset_index().shape[0])

#print the number of conPanjivaID is 999 in import_us
print(importus[importus['conPanjivaId'] == 999].shape[0])

# print the number of conName is null in import_us
print(importus[importus['conName'].isnull()].shape[0])
# %%

#Packages needed to run code
import pandas as pd
from pathlib import Path
import time

#set timer
start_time = time.time()
#read the each csv file in the folder Processed_data/USImport/monthly
df = pd.read_csv('/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/PanjivaUSImport2020To2024-2.csv')

# print the number of unique values of conPanjivaId, conName in df
print(df['conPanjivaId'].nunique())
print(df['conName'].nunique())

# print the number of 999 in conPanjivaId in df
print(df[df['conPanjivaId'] == 999].shape[0])

# print the number of null in conName in df
print(df[df['conName'].isnull()].shape[0])

# print the number of unique values of pairs of conPanjivaID, shpPanjivaId in df
print(df.groupby(['conPanjivaId', 'shpPanjivaId']).size().reset_index().shape[0])



# %%
