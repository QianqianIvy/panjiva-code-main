# %%
#Packages needed to run code
import pandas as pd
from pathlib import Path
import time
import os
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.seasonal import STL

# **Readme
# This code is for summing the volumeTEU by year, conPanjivaId and shpPanjivaId to get monthly data
# %%

######################################################
# Function to perform seasonal decomposition
# and extract the final adjusted values
######################################################

# Perform seasonal adjustment with detailed output for debugging
def seasonal_adjustment(series, start_year):
    try:
        # Create a time series index with the frequency of 12 (monthly data)
        series.index = pd.date_range(start=f'{start_year}-01-01', periods=len(series), freq='MS')
        
        # Seasonal decomposition using STL
        decomposition = STL(series, seasonal=13).fit()

        # Plot components for visual inspection
        decomposition.plot()
        plt.show()

        # Check the components for debugging
        print("Trend component:")
        print(decomposition.trend.dropna())  # Print non-NaN trend values
        print("Seasonal component:")
        print(decomposition.seasonal.dropna())  # Print non-NaN seasonal values
        print("Residual component:")
        print(decomposition.resid.dropna())  # Print non-NaN residuals

        # Combine trend and residuals to get seasonally adjusted series
        return decomposition.trend + decomposition.resid
    except Exception as e:
        print(f"Error during seasonal adjustment: {e}")
        return None
# %%
#####################################
# Read raw data
#####################################

#set timer
start_time = time.time()
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
    df = pd.read_csv(filepath)
    # keep if conCountry is United Satates and null
    df = df[(df['conCountry']== 'United States') | (df['conCountry'].isnull())]
    # drop non necessary columns for figure 1/2
    df = df.drop(columns=['conName', 'conFullAddress', 'conRoute', 'conCity', 
                            'conStateRegion', 'conPostalCode', 'conPanjivaId',
                            'shpPanjivaId', 'shpmtOrigin', 'shpmtDestination', 'day'])

    #change conPanjivaId, shpPanjivaId, year, month, day to int
    df[['year', 'month']] = df[['year', 'month']].apply(pd.to_numeric, errors='coerce')
    # drop if year month day is na/nan
    df.dropna(subset=['year', 'month'], inplace=True)

    # generate the date column
    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    df = df.drop(columns=['month'])

    # caluclate the sum of volumeTEU and the number of shipments by month
    teu_data_mon = df.groupby(['year', 'date']).agg({'volumeTEU': 'sum'}).reset_index()
    shpt_data_mon = df.groupby(['year','date']).agg({'panjivaRecordId': 'count'}).reset_index()

    # merge the two dataframes
    df = teu_data_mon.merge(shpt_data_mon, on=['date', 'year'], how='left')
                                                                                         
    #Add the file to the list
    fileData.append(df)

# %%
# concatenate all files in files
data_teu_shpt_val = pd.concat(fileData)

# rename volumeTEU to TEU(Panjiva),  panjivaRecordId to Shipments(Panjiva)
data_teu_shpt_val = data_teu_shpt_val.rename(columns={'volumeTEU': 'TEU(Panjiva)', 'panjivaRecordId': 'Shipments(Panjiva)'})
# %%
# Perform seasonal decomposition
teu_data_mon_sea = seasonal_adjustment(data_teu_shpt_val['TEU(Panjiva)'],2015)
shpt_data_mon_sea = seasonal_adjustment(data_teu_shpt_val['Shipments(Panjiva)'], 2015)
# Set the index of teu_data_mon_sea to the 'date' column for alignment
teu_data_mon_sea.index = teu_data_mon_sea.index.to_period('M').to_timestamp()
shpt_data_mon_sea.index = shpt_data_mon_sea.index.to_period('M').to_timestamp()

# %%
# merge teu_data_mon_sea with data_teu_shpt_val
# Ensure 'date' column is of datetime type in data_teu_shpt_val
data_teu_shpt_val['date'] = pd.to_datetime(data_teu_shpt_val['date'])

# Set 'date' as index in data_teu_shpt_val for alignment
data_teu_shpt_val.set_index('date', inplace=True)

# Assign adjusted TEU values from teu_data_mon_sea to data_teu_shpt_val
data_teu_shpt_val['TEU(Panjiva)_Adjusted'] = teu_data_mon_sea.reindex(data_teu_shpt_val.index)
data_teu_shpt_val['Shipments(Panjiva)_Adjusted'] = shpt_data_mon_sea.reindex(data_teu_shpt_val.index)

# Reset index if needed (to return to original structure)
data_teu_shpt_val.reset_index(inplace=True)
data_teu_shpt_val

# %%
# export data_teu_shpt_val to csv file
data_teu_shpt_val.to_csv(f'/Users/qianqiantang/Desktop/panjiva-code-main/Result/data_teu_shpt_val.csv', index=False)
print(data_teu_shpt_val)

# Calculate the time it takes to run the code
print("--- %s seconds ---" % (time.time() - start_time))



# %%
# Draw figure 1 in Flaaen et al. (2023)
# Packages needed to run code
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
import numpy as np

# Caculate the change from 2015-01-01 for TEU(Panjiva)  Shipments(Panjiva)
data_teu_shpt_val = pd.read_csv('/Users/qianqiantang/Desktop/panjiva-code-main/Result/data_teu_shpt_val.csv')

# %%
# caculate the change from 2015-01-01
data_teu_shpt = data_teu_shpt_val.copy()
data_teu_shpt['TEU(Panjiva)'] = data_teu_shpt_val['TEU(Panjiva)_Adjusted'] / data_teu_shpt_val['TEU(Panjiva)_Adjusted'].iloc[0]
data_teu_shpt['Shipments(Panjiva)'] = data_teu_shpt_val['Shipments(Panjiva)_Adjusted'] / data_teu_shpt_val['Shipments(Panjiva)_Adjusted'].iloc[0]
data_teu_shpt
# %%
# plot the figure data_teu_shpt['TEU(Panjiva)'], data_teu_shpt['Shipments(Panjiva)'] , and x axis is date
# label x axis by year
fig, ax = plt.subplots()
ax.plot(data_teu_shpt['date'], data_teu_shpt['TEU(Panjiva)'], label='TEU(Panjiva)', color='blue')
ax.plot(data_teu_shpt['date'], data_teu_shpt['Shipments(Panjiva)'], label='Shipments(Panjiva)', color='red')
ax.set_xlabel('Year')
ax.set_ylabel('Index, 2015-01-01 = 100 (Seasonally Adjusted)')
ax.legend()
plt.show()
fig.savefig('/Users/qianqiantang/Desktop/panjiva-code-main/Result/figure1.png')

# %%
# plot the figure after 2019-01-01
data_teu_shpt_2019 = data_teu_shpt[data_teu_shpt['date'] >= '2019-01-01']
data_teu_shpt_2019['TEU(Panjiva)'] = data_teu_shpt_2019['TEU(Panjiva)_Adjusted'] / data_teu_shpt_2019['TEU(Panjiva)_Adjusted'].iloc[0]
data_teu_shpt_2019['Shipments(Panjiva)'] = data_teu_shpt_2019['Shipments(Panjiva)_Adjusted'] / data_teu_shpt_2019['Shipments(Panjiva)_Adjusted'].iloc[0]


# %%

fig, ax = plt.subplots()
ax.plot(data_teu_shpt_2019['date'], data_teu_shpt_2019['TEU(Panjiva)'], label='TEU(Panjiva)', color='blue')
ax.plot(data_teu_shpt_2019['date'], data_teu_shpt_2019['Shipments(Panjiva)'], label='Shipments(Panjiva)', color='red')
ax.set_xlabel('Year')
ax.set_ylabel('Index, 2019-01-01 = 100 (Seasonally Adjusted)')
ax.legend()
plt.show()
fig.savefig('/Users/qianqiantang/Desktop/panjiva-code-main/Result/figure2.png')

# %%
