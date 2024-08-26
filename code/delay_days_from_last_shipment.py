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
    # df['conPanjivaId'] = df['conPanjivaId'].fillna(999)
    # df['shpPanjivaId'] = df['shpPanjivaId'].fillna(999)

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

#concatenate all files in files
importus = pd.concat(fileData)



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

# drop volumeTEU and panjivaRecordId columns
importus_try = importus.drop(columns=['panjivaRecordId', 'volumeTEU'])
print(f"importus_try shape is {importus_try.shape}")
print(f"importus' shape is {importus.shape}")


# duplicate rows
importus_try = importus_try.drop_duplicates()
print(f"importus_try shape is {importus_try.shape}")

# keep if conCountry is US or null
importus_try = importus_try[(importus_try['conCountry'] == 'United States')| (importus_try['conCountry'].isnull())]

# save importus_try into csv file
importus_try.to_csv('/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/delay_days.csv', index=False)

#calculate the time it takes to run the code
print("--- %s seconds ---" % (time.time() - start_time))

# print the number of unique values of conPanjivaId in import_us
print(importus['conPanjivaId'].nunique())
# print the number of unique values of pairs of conPanjivaID, shpPanjivaId in import_us
print(importus.groupby(['conPanjivaId', 'shpPanjivaId']).size().reset_index().shape[0])

#print the number of conPanjivaID is 999 in import_us
print(importus[importus['conPanjivaId'].isnull].shape[0])

# print the number of conName is null in import_us
print(importus[importus['conName'].isnull()].shape[0])

# Assuming 'df' is your DataFrame and 'days_from_last_shipment' is the column of interest
importus_try['days_from_last_shipment'].describe()

# count the number of the missing values in 'days_from_last_shipment'
importus_try['days_from_last_shipment'].isnull().sum()

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
