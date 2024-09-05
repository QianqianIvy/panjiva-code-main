#Packages needed to run code
import pandas as pd
from pathlib import Path
from datetime import datetime

# read the first line
def main():
    filedata = []

    #Path to panjiva data files directory/folder
    directory = '/Users/qianqiantang/Desktop/panjiva-code-main/original_data/PanjivaUSImport/Processed_data/test'
    #To read existing files in the folder
    files = Path(directory).glob('*.dta')
    #For each file in the folder
    for file in files:
        print(file)
        #Read the file, name columns
        with file.open(encoding='utf-8', errors='ignore') as f:
            string_data = f.readline()
            #split the last column by ';'
            df = pd.DataFrame([x.split(';') for x in string_data.split('\n')]) 
            
            #append to filedata
            filedata.append(df)
    
        #concatenate all dataframes
        combined_df = pd.concat(filedata)
        # save as dta file
        output_filename = f"/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/{file.stem}.dta"
       
        # Export the combined dataframe to a Stata file
        combined_df.to_stata(output_filename, version=118)
        print(f"Exported {output_filename}")

if __name__ == '__main__':
    main()

# %%

#Packages needed to run code
import pandas as pd
from pathlib import Path

# read the csv file
df = pd.read_csv('/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/2015-2019/PanjivaUSImport2015To2019_address.csv')

df.head()
# %%
df2 = pd.read_csv('/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/annual/USImport_2015.csv')

df2.head()
# %%
