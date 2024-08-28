# %%
#Packages needed to run code
import pandas as pd
from pathlib import Path
import time
#****READ ME****
#This Python file reads a Panjiva US Import data file (in text format) and creates an excel spreadsheet with this information
#Numbers are changed to numeric type if they are not used as identifiers
#Column names were also added to the dataframe
#Dataframe is saved as an excel spreadsheet
#Make sure to change data path and saving path before running as the default paths are not universal - Yuritzy Ramos
def main():
    start_time = time.time()

    #Path to panjiva data files directory/folder
    directory = '/Users/qianqiantang/Desktop/panjiva-code-main/original_data/PanjivaUSImport'
    #To read existing files in the folder
    files = Path(directory).glob('*.txt')
    #For each file in the folder
    for file in files:
        print(file)
        
        #List to store dataframes
        fileData = []
        #Read the file, name columns, and append to the masterList
        with file.open(encoding='utf-8', errors='ignore') as f:
            for line in f:

            #Split rows by #@#@# and columns by '~'
                df = pd.DataFrame([x.split("'~'") for x in line.split('#@#@#')])
                print(f"Number of columns in the DataFrame: {df.shape[1]}")

                #check if the number of columns is 53, if not drop the line
                expected_columns = 53
                if df.shape[1] != expected_columns:
                    print(f"Number of columns in the DataFrame: {df.shape[1]}")
                    df.drop(df.index, inplace=True)
                    continue

                #Add column names to the dataframe
                df.columns = ['panjivaRecordId', 'billOfLadingNumber', 'arrivalDate', 'conName', 'conFullAddress', 'conRoute', 'conCity', 'conStateRegion', 'conPostalCode',
                          'conCountry', 'conPanjivaId', 'conOriginalFormat', 'shpName', 'shpFullAddress', 'shpRoute', 'shpCity', 'shpStateRegion', 'shpPostalCode', 'shpCountry',
                          'shpPanjivaId', 'shpOriginalFormat',
                          'carrier', 'notifyParty', 'notifyPartySCAC', 'billOfLadingType', 'masterBillOfLadingNumber', 'shpmtOrigin', 'shpmtDestination', 'shpmtDestinationRegion',
                          'portOfUnlading', 'portOfUnladingRegion', 'portOfLading', 'portOfLadingRegion', 'portOfLadingCountry',
                          'placeOfReceipt', 'transportMethod', 'vessel', 'vesselVoyageId', 'vesselIMO','isContainerized', 'volumeTEU', 'quantity', 'measurement', 'weightKg', 'weightT',
                          'weightOriginalFormat', 'valueOfGoodsUSD', 'FROB', 'manifestNumber', 'inbondCode', 'numberOfContainers', 'hasLCL', 'fileDate']
            #Drop columns that won't be necessary
                df.drop(columns= ['billOfLadingNumber', 'conOriginalFormat', 'shpName', 'shpFullAddress', 'shpRoute', 'shpCity', 'shpStateRegion', 'shpPostalCode', 'shpOriginalFormat',
                          'carrier', 'notifyParty', 'notifyPartySCAC', 'billOfLadingType', 'masterBillOfLadingNumber', 'shpmtDestinationRegion',
                          'portOfUnlading', 'portOfUnladingRegion', 'portOfLading', 'portOfLadingRegion', 'portOfLadingCountry',
                          'placeOfReceipt', 'transportMethod', 'vessel', 'vesselVoyageId', 'vesselIMO','isContainerized', 'quantity', 'measurement', 'weightKg', 'weightT',
                          'weightOriginalFormat', 'valueOfGoodsUSD', 'FROB', 'manifestNumber', 'inbondCode', 'numberOfContainers', 'hasLCL', 'fileDate'], inplace=True)
             # Convert arrivalDate to datetime  
                df['arrivalDate'] = pd.to_datetime(df['arrivalDate'], format="%Y-%m-%d %H:%M:%S", errors='coerce')

            # Extract year, month, and day
                df['year'] = df['arrivalDate'].dt.year
                df['month'] = df['arrivalDate'].dt.month
                df['day'] = df['arrivalDate'].dt.day
            
                df.drop(columns= ['arrivalDate'], inplace=True)
                fileData.append(df)
        importus = pd.concat(fileData)
        #Save importus as csv file
        importus.to_csv(f"/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/{file.stem}_address.csv", index=False)
        # #sample's first 10000 rows
        # sample = importus.head(10000)
        # sample.to_csv(f"/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport_sample/{file.stem}_sample.csv", index=False)


    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")
    
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
    
# %%
