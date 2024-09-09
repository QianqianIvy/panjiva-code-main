# %%
#Packages needed to run code
import pandas as pd
from pathlib import Path
import time
import os
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates


# **Readme
# This code is for counting the distinct shpPanjivaId by year, conPanjivaId and month

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
years = [2019, 2020, 2021, 2022, 2023, 2024]

for y in years:
    filename = f'USImport_{y}.csv'  # Assuming the files are in CSV format
    filepath = os.path.join(directory, filename)
    df = pd.read_csv(filepath)
    # keep if conCountry is United Satates and null
    df = df[(df['conCountry']== 'United States') | (df['conCountry'].isnull())]
    # drop non necessary columns for figure 8
    df = df.drop(columns=['panjivaRecordId', 'conName', 'conFullAddress', 'conRoute', 'conCity', 
                            'conStateRegion', 'conPostalCode', 'shpmtOrigin', 'shpmtDestination',
                            'day', 'volumeTEU', 'shpCountry', 'conCountry'])

    #change conPanjivaId, shpPanjivaId, year, month, day to int
    df[['year', 'month']] = df[['year', 'month']].apply(pd.to_numeric, errors='coerce')
    # drop if year month day is na/nan
    df.dropna(subset=['year', 'month'], inplace=True)
    # drop if conPanjivaId, shpPanjivaId is na/nan
    df.dropna(subset=['conPanjivaId', 'shpPanjivaId'], inplace=True)
    df = df.drop_duplicates()

    # generate the date column
    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))

    # caluclate the number of distinct shipments by month
    df = df.groupby(['date', 'conPanjivaId']).size().reset_index(name='num_of_ship')
    
    df = df.groupby('date')['num_of_ship'].mean().reset_index(name='ave_num_distinct_shpPanjivaId')

    #Add the file to the list
    fileData.append(df)

# %%
# concatenate all files in files
data_shp_per_con = pd.concat(fileData)
data_shp_per_con['date'] = pd.to_datetime(data_shp_per_con['date'])

# ave_num_distinct_shpPanjivaId_adjusted = seasonal_adjustment(data_shp_per_con['ave_num_distinct_shpPanjivaId'],2019)
# ave_num_distinct_shpPanjivaId_adjusted.index = ave_num_distinct_shpPanjivaId_adjusted.index.to_period('M').to_timestamp()
# # Ensure 'date' column is of datetime type in data_teu_shpt_val

# # Set 'date' as index in data_teu_shpt_val for alignment
# data_shp_per_con.set_index('date', inplace=True)
# data_shp_per_con['ave_num_distinct_shpPanjivaId'] = ave_num_distinct_shpPanjivaId_adjusted.reindex(data_shp_per_con.index)
# data_shp_per_con

# %%
# change from the same month in 2019
data_shp_per_con['year'] = data_shp_per_con['date'].dt.year
data_shp_per_con['month'] = data_shp_per_con['date'].dt.month
data_shp_per_con_pivot = data_shp_per_con.pivot(index='month', columns='year', values='ave_num_distinct_shpPanjivaId')

# calculate the year over year growth rate from year 2019
for y in range(2020, 2025):
    data_shp_per_con_pivot[y] = (data_shp_per_con_pivot[y] / data_shp_per_con_pivot[2019] - 1) * 100
print(data_shp_per_con_pivot)
data_shp_per_con_pivot = data_shp_per_con_pivot.drop(columns=[2019])

#calculate the time it takes to run the code
print("--- %s seconds ---" % (time.time() - start_time))

# %%
# pivot data_shp_per_con_pivot into long format
data_shp_per_con_pivot = data_shp_per_con_pivot.reset_index()
data_shp_per_con_pivot = data_shp_per_con_pivot.melt(id_vars='month', var_name='year', value_name='yoy_growth_rate')
data_shp_per_con_pivot['year'] = data_shp_per_con_pivot['year'].astype(int)
data_shp_per_con_pivot['month'] = data_shp_per_con_pivot['month'].astype(int)
data_shp_per_con_pivot['date'] = pd.to_datetime(data_shp_per_con_pivot[['year', 'month']].assign(day=1))
data_shp_per_con_pivot = data_shp_per_con_pivot.dropna(subset=['yoy_growth_rate'])
data_shp_per_con.to_csv('monthly_ave_shp_per_con.csv')
data_shp_per_con_pivot.to_csv('yoy_shp_per_con.csv')
# %%
# figure 8
# Assuming data_shp_per_con_chart is a DataFrame
# Define approved colors and lines
approved_colors = {'blue': '#1f77b4'}
approved_lines = {'blue': 1.5}

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Horizontal line at y=0
ax.axhline(y=0, color='black', linewidth=0.3)

# Line plot
sns.lineplot(data=data_shp_per_con_pivot, x='date', y='yoy_growth_rate', color=approved_colors.get('blue', 'b'), linewidth=approved_lines.get('blue', 1.5), ax=ax)

# Customizing the x-axis
ax.set_xlim(pd.to_datetime("2020-01-01"), pd.to_datetime("2024-06-01"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))  # Every 6 months
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b. %Y'))

# Customizing the y-axis
ax.set_ylim(-40, 10)
ax.set_yticks(range(-30, 11, 10)) 

# Labels and title
ax.set_xlabel("")
ax.set_ylabel("")
ax.set_title("Percent change from same month in 2019", fontsize=12)

# Show the plot
plt.show()
fig.savefig('/Users/qianqiantang/Desktop/panjiva-code-main/Result/figure8_2020-2024.png')

# %%
# %%
# figure 8
# Assuming data_shp_per_con_chart is a DataFrame
# Define approved colors and lines
approved_colors = {'blue': '#1f77b4'}
approved_lines = {'blue': 1.5}

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Horizontal line at y=0
ax.axhline(y=0, color='black', linewidth=0.3)

# Line plot
sns.lineplot(data=data_shp_per_con_pivot, x='date', y='yoy_growth_rate', color=approved_colors.get('blue', 'b'), linewidth=approved_lines.get('blue', 1.5), ax=ax)

# Customizing the x-axis
ax.set_xlim(pd.to_datetime("2020-01-01"), pd.to_datetime("2021-09-01"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))  # Every 6 months
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b. %Y'))

# Customizing the y-axis
ax.set_ylim(-40, 10)
ax.set_yticks(range(-30, 11, 10)) 


# Labels and title
ax.set_xlabel("")
ax.set_ylabel("")
ax.set_title("Percent change from same month in 2019", fontsize=12)

# Show the plot
plt.show()
fig.savefig('/Users/qianqiantang/Desktop/panjiva-code-main/Result/figure8_2020-2021.png')

# %%
# %%
# figure 8
# Assuming data_shp_per_con_chart is a DataFrame
# Define approved colors and lines
approved_colors = {'blue': '#1f77b4'}
approved_lines = {'blue': 1.5}

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Horizontal line at y=0
ax.axhline(y=0, color='black', linewidth=0.3)

# Line plot
sns.lineplot(data=data_shp_per_con_pivot, x='date', y='yoy_growth_rate', color=approved_colors.get('blue', 'b'), linewidth=approved_lines.get('blue', 1.5), ax=ax)

# Customizing the x-axis
ax.set_xlim(pd.to_datetime("2020-01-01"), pd.to_datetime("2023-12-01"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))  # Every 6 months
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b. %Y'))

# Customizing the y-axis
ax.set_ylim(-40, 10)
ax.set_yticks(range(-30, 11, 10)) 

# Labels and title
ax.set_xlabel("")
ax.set_ylabel("")
ax.set_title("Percent change from same month in 2019", fontsize=12)

# Show the plot
plt.show()
fig.savefig('/Users/qianqiantang/Desktop/panjiva-code-main/Result/figure8_2020-2023.png')
# %%
# Define approved colors and lines
approved_colors = {'blue': '#1f77b4'}
approved_lines = {'blue': 1.5}

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Horizontal line at y=0
ax.axhline(y=0, color='black', linewidth=0.3)

# Line plot
sns.lineplot(data=data_shp_per_con_pivot, x='date', y='yoy_growth_rate', color=approved_colors.get('blue', 'b'), linewidth=approved_lines.get('blue', 1.5), ax=ax)

# Customizing the x-axis
ax.set_xlim(pd.to_datetime("2023-01-01"), pd.to_datetime("2024-06-01"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))  # Every 6 months
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b. %Y'))

# Customizing the y-axis
ax.set_ylim(-40, 10)
ax.set_yticks(range(-30, 11, 10)) 

# Labels and title
ax.set_xlabel("")
ax.set_ylabel("")
ax.set_title("Percent change from same month in 2019", fontsize=12)

# Show the plot
plt.show()
# %%
