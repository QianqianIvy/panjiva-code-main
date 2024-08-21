# %%
#Packages needed to run code
#from importlib.resources.readers import remove_duplicates
import pandas as pd
from pathlib import Path
import time
import numpy as np
#****READ ME****
#This Python file reads a Panjiva US Import data file (in text format) and creates an csv spreadsheet with this information
#Numbers are changed to numeric type if they are not used as identifiers
#Column names were also added to the dataframe
#Dataframe is saved as an excel spreadsheet
#Qianqian(Ivy) Tang
#function for removing repeated values in one blank of hsCode, they contribute to strange long hsCode
def remove_duplicates(input_string):
    elements = input_string.split(';')
    seen = set()
    unique_elements = []
    for element in elements:
        element = element.strip()
        if element not in seen:
            seen.add(element)
            unique_elements.append(element)
    return '; '.join(unique_elements)

# define the funtion to process chunk
def process_chunk(chunk):
    #split the rows by β and columns by '~'
    rows = chunk.iloc[:,0].str.split("β", expand=True)
    print(f"Number of columns in the DataFrame: {rows.shape[1]}")

    #Add column names to the dataframe
    rows.columns = ['hsCodeId', 'panjivaRecordId', 'hsCode']

    #clean the hdCode column by replacing the rows that do not contain 'Classified' or 'Parsed' with NaN
    rows.loc[~rows['hsCode'].str.contains('Classified|Parsed', na=False), 'hsCode'] = np.nan

    # reomve duplicates in the hsCode column
    rows['hsCode'] = rows['hsCode'].apply(lambda x: remove_duplicates(x) if pd.notna(x) else x)

    # ensure all columns are strings
    rows = rows.astype(str)

    return rows

def main():
    #set a timer
    start_time = time.time()

    #Path to panjiva data files directory/folder
    directory = '/Users/qianqiantang/Desktop/panjiva-code-main/original_data/PanjivaUSImpHSCode'
    #To read existing files in the folder
    files = Path(directory).glob('*.csv')
    #For each file in the folder
    for file in files:
        print(f"Processing file: {file}")

        #Read the file, name columns, and append to the masterList
        chunk_iter = pd.read_csv(file, chunksize=10000, encoding='utf-8', on_bad_lines='skip')
        fileData = []

        for i, chunk in enumerate(chunk_iter):
            print(f"Processing chunk {i} of file {file}")
            try:
                rows = process_chunk(chunk)
                fileData.append(rows)
            except Exception as e:
                print(f"Error in chunk {i}: {e}")
                break
        
        if fileData:
            # Concatenate all dataframes for the current file
            combined_df = pd.concat(fileData, ignore_index=True)
            
            # Generate output filename based on the input filename
            output_filename = f"/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/{file.stem}.dta"
            
            # Export the combined dataframe to a Stata file
            combined_df.to_stata(output_filename, version=118)
            print(f"Exported {output_filename}")
        else:
            print(f"No data to concatenate for file {file}")


        end_time = time.time()
        print(f"Execution time: {end_time - start_time} seconds")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# # %%
# import pandas as pd
# from pathlib import Path
# import time
# import numpy as np
# def remove_duplicates(input_string):
#     elements = input_string.split(';')
#     seen = set()
#     unique_elements = []
#     for element in elements:
#         element = element.strip()
#         if element not in seen:
#             seen.add(element)
#             unique_elements.append(element)
#     return '; '.join(unique_elements)

# fileData = []
# #Path to panjiva data files directory/folder
# directory = '/Users/qianqiantang/Desktop/panjiva-code-main/original_data/PanjivaUSImpHSCode'
# #To read existing files in the folder
# files = Path(directory).glob('*.csv')

# # get the filename of the first file and save it as filepath
# filepath = next(files)

# # load the first ten rows of the filepath
# df = pd.read_csv(filepath, nrows=100, encoding='utf-8', on_bad_lines='skip')
# df = df.iloc[:,0].str.split("β", expand=True)
# df.columns = ['hsCodeId', 'panjivaRecordId', 'hsCode']
# print(df)

# # replace the row that has no keywords in hsCode with NaN.
# # The keywords are Classified, Parsed
# # Add the dropped rows to a new dataframe
# df.loc[~df['hsCode'].str.contains('Classified|Parsed', na=False), 'hsCode'] = np.nan

# # Apply the remove_duplicates function to the hsCode column
# df['hsCode'] = df['hsCode'].apply(lambda x: remove_duplicates(x) if pd.notna(x) else x)


# print('df')
# print(df)

# hsCode_split = df['hsCode'].str.split(r'\s*;\s*', expand=True)
# hsCode_split.columns = [f'hsCode_{i+1}' for i in range(hsCode_split.shape[1])]
# df = pd.concat([df.drop(columns=['hsCode']), hsCode_split], axis=1)
# print(f"Number of columns in the DataFrame: {df.shape[1]}")

# # split the semi-colon separated values in the hsCode column
# # hsCode_split = df['hsCode'].str.split(r'\s*;\s*', expand=True)
# # hsCode_split.columns = [f'hsCode_{i+1}' for i in range(hsCode_split.shape[1])]
# # hsCode_split

# # %%


