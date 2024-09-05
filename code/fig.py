# %%
# import necessary pacakages
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import pandas as pd


# read csv file
directory = "/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/annual"
files = Path(directory).glob('*three_index.csv')

#List to store dataframes
fileData = []

# Combine all the files in the folder
for file in files:
    print(file)
    #Read the file
    df = pd.read_csv(file)

    #Add the file to the list
    fileData.append(df)

importus = pd.concat(fileData)

# calculate the median and mean of Total_teu, num_distinct_shpPanjivaId, average_days_from_last_shipment by year
Total_teu = importus.groupby('year')['Total_teu'].agg(['median', 'mean'])

num_distinct_shpPanjivaId = importus.groupby('year')['num_distinct_shpPanjivaId'].agg(['median', 'mean'])
average_days_from_last_shipment = importus.groupby('year')['average_days_from_last_shipment'].agg(['median', 'mean'])

# %%
# draw three figures of Total_teu, num_distinct_shpPanjivaId, average_days_from_last_shipment by year with two lines for median and mean
fig, ax = plt.subplots(3, 1, figsize=(10, 15))
Total_teu.plot(ax=ax[0], title='Total Tade Volume by pairs (TEU)', ylabel='Total_teu', xlabel='year')
num_distinct_shpPanjivaId.plot(ax=ax[1], title='Number of Shippers for Each Consignee', ylabel='num_distinct_shpPanjivaId', xlabel='year')
average_days_from_last_shipment.plot(ax=ax[2], title='Average Days from Last Shippment', ylabel='average_days_from_last_shipment', xlabel='year')
plt.show()

# %%

# combine and  expot Total_teu, num_distinct_shpPanjivaId, average_days_from_last_shipment into excel file
fig = pd.concat([Total_teu, num_distinct_shpPanjivaId, average_days_from_last_shipment], axis=1)
fig.to_excel('/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/annual/annual_three_index.xlsx')

# %%
