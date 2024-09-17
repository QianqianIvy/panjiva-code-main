# %%
#Packages needed to run code
import pandas as pd
from pathlib import Path
import time
import os
# **Readme
# This code is for summing the volumeTEU by year, month, conPanjivaId and shpPanjivaId to get monthly data
# missing value convert to 999, drop rows with non numeric conPanjivaId and shpPanjivaId


#set timer
start_time = time.time()
#read the each csv file in the folder Processed_data/USImport

# check if conName and conPanjivaID are unique in pair
#print(importus[['conName', 'conPanjivaId']].duplicated().any())

#combine all files in files and sum by year and month
#List to store dataframes
directory = "/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/annual/annual_raw_address"

#List to store dataframes
fileData = []
fileData_truncted = []
#For each file in the folder
# List of years you want to read files for
years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

for y in years:
    filename = f'USImport_{y}.csv'  # Assuming the files are in CSV format
    filepath = os.path.join(directory, filename)
    print(filepath)

    df = pd.read_csv(filepath)
    df = df.groupby(['year', 'month', 'conName', 'conPanjivaId', 'shpPanjivaId', 'conCountry', 'shpCountry', 'shpmtDestination']).agg({'volumeTEU': 'sum'}).reset_index()

    #Add the file to the list
    fileData.append(df)

importus = pd.concat(fileData)
print(importus.head(10))

# export importus into csv file
importus.to_csv('/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/monthly/USImport_monthly_2015-2024.csv', index=False)


#calculate the time it takes to run the code
print("--- %s seconds ---" % (time.time() - start_time))

# %%
#Packages needed to run code
import pandas as pd
from pathlib import Path
import time
# for code testing
directory = "/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport"
files = Path(directory).glob('*.csv')
file = next(files)
test =pd.read_csv(file)

# check type of each column
print(test.dtypes)

# give examples of non-numeric values of conPanjivaId
print(test[test['conPanjivaId'].str.isnumeric() == False]['conPanjivaId'].unique())

# how many rows which conPanjivaId is not numeric
print(test[test['conPanjivaId'].str.isnumeric() == False].shape[0])
print(test[test['shpPanjivaId'].str.isnumeric() == False].shape[0])

# how many rows which conPanjivaId and shpPanjivaId is not numeric at the same time
print(test[(test['conPanjivaId'].str.isnumeric() == False) & (test['shpPanjivaId'].str.isnumeric() == False)].shape[0])
#how many rows in test
print(test.shape[0])