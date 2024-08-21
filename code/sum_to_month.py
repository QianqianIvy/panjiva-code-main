# %%
#Packages needed to run code
import pandas as pd
from pathlib import Path
import time

# **Readme
# This code is for summing the volumeTEU by year, month, conPanjivaId and shpPanjivaId to get monthly data
# missing value convert to 999, drop rows with non numeric conPanjivaId and shpPanjivaId


#set timer
start_time = time.time()
#read the each csv file in the folder Processed_data/USImport

directory = "/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport"
files = Path(directory).glob('*.csv')

# #read the first file in the folder
# file = next(files)
# #print the first 10 rows in the file
# importus = pd.read_csv(file)
# print(importus.head(10))

# check if conName and conPanjivaID are unique in pair
#print(importus[['conName', 'conPanjivaId']].duplicated().any())

#combine all files in files and sum by year and month
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

#sum volumeTEU by year, month, conPanjivaId and shpPanjivaId but also keep other columns
importus = pd.concat(fileData)
importus = importus.groupby(['year', 'month', 'conName', 'conPanjivaId', 'shpPanjivaId', 'conCountry', 'shpCountry', 'shpmtDestination']).agg({'volumeTEU': 'sum'}).reset_index()
print(importus.head(10))

# change columns names to lower case
importus.columns = importus.columns.str.lower()

# export importus into csv file
importus.to_csv('/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/monthly/USImport_monthly.csv', index=False)


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