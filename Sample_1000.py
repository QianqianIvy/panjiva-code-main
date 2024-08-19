# %%
import pandas as pd
from pathlib import Path
import time
import numpy as np


# Path to panjiva data files directory/folder
directories = [
    '/Users/qianqiantang/Desktop/panjiva-code-main/original_data/PanjivaUSImpGoodsShpd',
    '/Users/qianqiantang/Desktop/panjiva-code-main/original_data/PanjivaUSImpContNum',
    '/Users/qianqiantang/Desktop/panjiva-code-main/original_data/PanjivaUSImpContTOS',
    '/Users/qianqiantang/Desktop/panjiva-code-main/original_data/PanjivaUSImpContTypes',
    '/Users/qianqiantang/Desktop/panjiva-code-main/original_data/PanjivaUSImpDG',
    '/Users/qianqiantang/Desktop/panjiva-code-main/original_data/PanjivaUSImpDividedLCL',
    '/Users/qianqiantang/Desktop/panjiva-code-main/original_data/PanjivaUSImpVolCon',
    '/Users/qianqiantang/Desktop/panjiva-code-main/original_data/PanjivaUSImpContMarks'
]

# To read the first existing files in the folder
for directory in directories:
    start_time = time.time()
    print(f"Checking directory: {directory}")
    files = Path(directory).glob('*.txt')
    # Read the first txt file in the folder
    filepath = next(files, None)
    
    if filepath:
        print(filepath)
        # Recreate the list to store dataframes
        fileData = []
        # Read the first file in the folder
        with filepath.open(encoding='utf-8', errors='ignore') as f:
            # # Read the first 1000 rows of the file
            # for i, line in enumerate(f):
            #     # Split rows by #@#@# and columns by '~'
            #     df = pd.DataFrame([x.split("'~'") for x in line.split('#@#@#')])
            #     print(f"Number of columns in the DataFrame: {df.shape[1]}")
            #     fileData.append(df)
            #     if i + 1 == 1000:
            #         break
            #read the first line of the file
            line = f.readline() 
            # Split rows by #@#@# and columns by '~'
            df = pd.DataFrame([x.split("'~'") for x in line.split('#@#@#')])
            print(f"Number of columns in the DataFrame: {df.shape[1]}")
            fileData.append(df)
        sample = pd.concat(fileData).head(1000)
        # Print the number of rows and columns in the sample
        print(f"Number of rows and columns in the sample: {sample.shape}")

        # Export to Stata file into the directory
        sample.to_stata(f"{directory}/{filepath.stem}.dta", version=118)


        end_time = time.time()
        print(f"Execution time: {end_time - start_time} seconds")
    else:
        print(f"No .txt files found in the directory: {directory}")



# %%
