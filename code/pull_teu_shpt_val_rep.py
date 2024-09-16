# %%
#Packages needed to run code
import pandas as pd
from pathlib import Path
import time
import os
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.seasonal import STL
import matplotlib.pyplot as plt
import seaborn as sns

# %%
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
# **Readme
# This code is for summing the volumeTEU by year, conPanjivaId and shpPanjivaId to get monthly data
# missing value convert to 999, drop rows with non numeric conPanjivaId and shpPanjivaId

#####################################
# Read raw data
#####################################

#set timer
start_time = time.time()
#read the each csv file in the folder Processed_data/USImport
directorys = ["/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/2015-2019", "/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/2020-2024"]
fileData = []
for directory in directorys:
    files = Path(directory).glob('*address.csv')
    #List to store dataframes
    #For each file in the folder
    for file in files:
        print(file)
        #Read the file
        df = pd.read_csv(file)
        df = df[['year', 'month', 'panjivaRecordId', 'volumeTEU']]
        df[['year', 'month']] = df[[ 'year', 'month']].apply(pd.to_numeric, errors='coerce')
        # drop if year month day is na/nan
        df.dropna(subset=['year', 'month'], inplace=True)

        #Add the file to the list
        fileData.append(df)

# concatenate all files in files
importus = pd.concat(fileData)

importus['date'] = pd.to_datetime(importus[['year', 'month']].assign(day=1))
importus['volumeTEU'] = pd.to_numeric(importus['volumeTEU'], errors='coerce')

# %%
teu_data_mon = importus.groupby(['year', 'date']).agg({'volumeTEU': 'sum'}).reset_index()
shpt_data_mon = importus.groupby(['year','date']).agg({'panjivaRecordId': 'count'}).reset_index()
data_teu_shpt_val = teu_data_mon.merge(shpt_data_mon, on=['date', 'year'], how='left')

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
data_teu_shpt_val.to_csv(f'/Users/qianqiantang/Desktop/panjiva-code-main/Result/data_teu_shpt_val.csv', index=False)

#calculate the time it takes to run the code
print("--- %s seconds ---" % (time.time() - start_time))

# %%
# caculate the change from 2015-01-01
data_teu_shpt = data_teu_shpt_val.copy()
data_teu_shpt['teu'] = 100 *data_teu_shpt_val['TEU(Panjiva)_Adjusted'] / data_teu_shpt_val['TEU(Panjiva)_Adjusted'].iloc[0]
data_teu_shpt['shp'] = 100 * data_teu_shpt_val['Shipments(Panjiva)_Adjusted'] / data_teu_shpt_val['Shipments(Panjiva)_Adjusted'].iloc[0]
data_teu_shpt

# %%
import seaborn as sns
import matplotlib.dates as mdates
# Define colors
approved_colors = {
    "blue": "#1f77b4",
    "red": "#d62728"
}

colors = {
    "TEUs (Panjiva)": approved_colors["blue"],
    "Shipments (Panjiva)": approved_colors["red"]
}

# Make charts
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(data=data_teu_shpt, x='date', y='teu', ax=ax, label='TEUs (Panjiva)', color=colors["TEUs (Panjiva)"])
sns.lineplot(data=data_teu_shpt, x='date', y='shp', ax=ax, label='Shipments (Panjiva)', color=colors["Shipments (Panjiva)"])

ax.set(xlabel='', ylabel='', title='Index, 2015 = 100')
ax.legend(title='Legend', loc='upper left', bbox_to_anchor=(0.3, 0.8))
ax.set_xlim(pd.Timestamp('2015-01-01'), pd.Timestamp('2024-05-01'))
ax.set_ylim(90, 170)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.yaxis.set_major_locator(plt.MultipleLocator(20))

# Save the chart
plt.savefig("/Users/qianqiantang/Desktop/panjiva-code-main/Result/fig_teu_shpt_val_monthly.png", bbox_inches='tight')

# %%
############################################
######### 2015-01-01-2021-01-01
import seaborn as sns

# Define colors
approved_colors = {
    "blue": "#1f77b4",
    "red": "#d62728"
}

colors = {
    "TEUs (Panjiva)": approved_colors["blue"],
    "Shipments (Panjiva)": approved_colors["red"]
}

# Make charts
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(data=data_teu_shpt, x='date', y='teu', ax=ax, label='TEUs (Panjiva)', color=colors["TEUs (Panjiva)"])
sns.lineplot(data=data_teu_shpt, x='date', y='shp', ax=ax, label='Shipments (Panjiva)', color=colors["Shipments (Panjiva)"])

ax.set(xlabel='', ylabel='', title='Index, 2015 = 100')
ax.legend(title='Legend', loc='upper left', bbox_to_anchor=(0.3, 0.8))
ax.set_xlim(pd.Timestamp('2015-01-01'), pd.Timestamp('2021-9-01'))
ax.set_ylim(90, 160)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.yaxis.set_major_locator(plt.MultipleLocator(20))

# Save the chart
plt.savefig("/Users/qianqiantang/Desktop/panjiva-code-main/Result/fig_teu_shpt_val_monthly_2021.png", bbox_inches='tight')

# %%
######## compute missing values in conPanjivaId and shpPanjivaId
#read the each csv file in the folder Processed_data/USImport
start_time = time.time()

directorys = ["/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/2015-2019", "/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/2020-2024"]
fileData = []
y = 1
for directory in directorys:
    files = Path(directory).glob('*address.csv')
    #List to store dataframes
    #For each file in the folder
    for file in files:
        print(file)
        #Read the file
        df = pd.read_csv(file)
        df = df[['conPanjivaId', 'shpPanjivaId']].astype(str)

        # count non numeric conPanjivaId and shpPanjivaId for this file
        print("non numeric conPanjivaId and shpPanjivaId for this file")
        conpanjivaid_missing = df[~df['conPanjivaId'].str.isnumeric()]['conPanjivaId'].count()
        shppanjivaid_missing = df[~df['shpPanjivaId'].str.isnumeric()]['shpPanjivaId'].count()
        conpanjivaid_total = df['conPanjivaId'].count()
        shppanjivaid_total = df['shpPanjivaId'].count()
        print(conpanjivaid_missing, shppanjivaid_missing)

        # save conpanjivaid_missing, conpanjivaid_total, shppanjivaid_missing, shppanjivaid_total
        fileData.append([y, conpanjivaid_missing, conpanjivaid_total, shppanjivaid_missing, shppanjivaid_total])
        y = y+1
        y
# %%
missing_firm = pd.DataFrame(fileData, columns=['File Order', 'ConPanjivaId_Missing (Non-numeric, Non-NAN)', 'ConPanjivaId_Total (Non-NAN)', 'ShpPanjivaId_Missing (Non-numeric, Non-NAN)', 'ShpPanjivaId_Total  (Non-NAN)'])
missing_firm['Con Missing Share'] = missing_firm['ConPanjivaId_Missing (Non-numeric, Non-NAN)'] / missing_firm['ConPanjivaId_Total (Non-NAN)']
missing_firm['Shp Missing Share'] = missing_firm['ShpPanjivaId_Missing (Non-numeric, Non-NAN)'] / missing_firm['ShpPanjivaId_Total  (Non-NAN)']
missing_firm.to_csv(f'/Users/qianqiantang/Desktop/panjiva-code-main/Result/missing_firm.csv', index=False)
print("--- %s seconds ---" % (time.time() - start_time))

# %%
