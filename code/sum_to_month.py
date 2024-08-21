# %%
#Packages needed to run code
import pandas as pd
from pathlib import Path
import time

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
    #Add the file to the list
    fileData.append(df)

#sum volumeTEU by year, month, conPanjivaId and shpPanjivaId
importus = pd.concat(fileData)
importus = importus.groupby(['year', 'month', 'conPanjivaId', 'shpPanjivaId']).agg({'volumeTEU': 'sum'}).reset_index()



# %%
