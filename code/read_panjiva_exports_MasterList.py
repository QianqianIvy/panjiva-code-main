#Packages needed to run code
import pandas as pd
from pathlib import Path
#****READ ME****
#This Python file reads a Panjiva US Import data file (in text format) and creates an excel spreadsheet with this information
#Numbers are changed to numeric type if they are not used as identifiers
#Column names were also added to the dataframe
#Dataframe is saved as an excel spreadsheet
#Make sure to change data path and saving path before running as the default paths are not universal - Yuritzy Ramos
def main():
    #List to store dataframes
    fileData = []
    #Path to panjiva data files directory/folder
    directory = '/home/atl/f1ysr01/Documents/PycharmProjects/Panjiva/panjivaExportFiles/'
    #To read existing files in the folder
    files = Path(directory).glob('*')
    #For each file in the folder
    for file in files:
        #Read the file, name columns, and append to the masterList
        with file.open() as f:
            string_data = f.readline()
            #Split rows by #@#@# and columns by '~'
            df = pd.DataFrame([x.split("'~'") for x in string_data.split('#@#@#')])
            #Add column names to the dataframe
            df.columns = ['panjivaRecordId','billOfLadingNumber','shpmtDate', 'shpName', 'shpFullAddress', 'shpRoute',
                          'shpCity', 'shpStateRegion', 'shpPostalCode', 'shpCountry', 'shpPanjivaId',
                          'shpOriginalFormat', 'carrier', 'shpmtDestination', 'portOfLading', 'portOfLadingRegion',
                          'portOfLadingCountry', 'portOfUnlading', 'portOfUnladingRegion', 'portOfUnladingCountry',
                          'placeOfReceipt', 'vessel', 'vesselCountry', 'transportFlightCode', 'isContainerized',
                          'volumeTEU', 'itemQuantity', 'weightKg', 'weightT', 'weightOriginalFormat', 'valueOfGoodsUSD',
                          'equipmentType', 'equipmentDimensions', 'dividedLCL', 'fileDate']
            #Drop columns that are unnecessary for matching
            df.drop(columns=['panjivaRecordId','billOfLadingNumber','shpmtDate','carrier','shpmtDestination','portOfLading', 'portOfLadingRegion',
                            'portOfLadingCountry','portOfUnlading','portOfUnladingRegion', 'portOfUnladingCountry', 'carrier', 'placeOfReceipt','vessel','vesselCountry',
                             'transportFlightCode', 'isContainerized','volumeTEU','itemQuantity', 'weightKg', 'weightT', 'weightOriginalFormat', 'valueOfGoodsUSD',
                             'equipmentType', 'equipmentDimensions', 'dividedLCL', 'fileDate'], inplace=True)
            fileData.append(df)
    masterList = pd.concat(fileData)
    masterList["exporter"] = [1]*len(masterList)
    masterList.drop_duplicates(inplace=True)
    #Save masterList as excel file
    #masterList.to_excel('~/Documents/PycharmProjects/Panjiva/PanjivaUSExportsMasterList.xlsx')
    #Save masterList as Stata data file
    masterList.to_stata('~/Documents/PycharmProjects/Panjiva/PanjivaUSExportsMasterList.dta',version=118)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()