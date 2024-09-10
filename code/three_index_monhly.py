# %%
#Packages needed to run code
import pandas as pd
from pathlib import Path
import time
import os
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter, YearLocator

# %%

# **Readme
# This code is for monthly number of distinct shippers per consignee, and total TEU per month per consignee
# days from the last shipment

#####################################
# Read raw data
#####################################

#set timer
start_time = time.time()
directory = "/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/annual/annual_raw_address"

#List to store dataframes
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
    # drop days
    df = df.drop(columns=['day','panjivaRecordId', 'date'])
    # drop non necessary columns for figure 8
    df['total_teu_monthly'] = df.groupby(['year', 'month', 'conPanjivaId', 'shpPanjivaId'])['volumeTEU'].transform('sum')
    df = df.drop(columns=['volumeTEU'])
    #drop duplicates
    df = df.drop_duplicates()
    
    num_distinct_shpPanjivaId = df.groupby(['year', 'month', 'conPanjivaId']).size().reset_index(name='num_distinct_shpPanjivaId')
    df = df.merge(num_distinct_shpPanjivaId, on=['year', 'month', 'conPanjivaId'], how='left')

    #change conPanjivaId, shpPanjivaId, year, month, day to int
    df[['year', 'month']] = df[['year', 'month']].apply(pd.to_numeric, errors='coerce')
    # drop if year month day is na/nan
    df.dropna(subset=['year', 'month', 'conPanjivaId', 'shpPanjivaId'], inplace=True)

    # export df_year to csv file
    df.to_csv(f'/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/monthly/USImport_{y}_index.csv', index=False)

# %%
# print the time it takes to run the code
print("--- %s seconds ---" % (time.time() - start_time))
# %%
# calculate the days from the last shipment
years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
fileData = []

for y in years:
    filename = f'USImport_{y}.csv'  # Assuming the files are in CSV format
    filepath = os.path.join(directory, filename)
    df = pd.read_csv(filepath)
    # keep if conCountry is United Satates and null
    df = df[(df['conCountry']== 'United States') | (df['conCountry'].isnull())]
    # drop days
    df = df[['year', 'month', 'conPanjivaId', 'shpPanjivaId', 'date']]
    # drop nan
    df.dropna(subset=['date', 'conPanjivaId', 'shpPanjivaId'], inplace=True)
    df = df.drop_duplicates()
    # export df_year to csv file
    fileData.append(df)

importus_delay_days = pd.concat(fileData)

# %%
importus_delay_days['date'] = pd.to_datetime(importus_delay_days['date'])
# caculate the days from last shipment
importus_delay_days = importus_delay_days.sort_values(['conPanjivaId', 'shpPanjivaId', 'date'])

importus_delay_days['days_from_last_shipment'] = importus_delay_days.groupby(['conPanjivaId', 'shpPanjivaId'])['date'].diff().dt.days

# caculate the average days_from_last_shipment by year, conPanjivaId, shpPanjivaId
# importus['days_from_last_shipment'] = importus['days_from_last_shipment'].fillna(999)
importus_delay_days['average_days_from_last_shipment'] = importus_delay_days.groupby(['year', 'month', 'conPanjivaId', 'shpPanjivaId'])['days_from_last_shipment'].transform('mean')


#drop the column days_from_last_shipment
importus_delay_days = importus_delay_days.drop(columns=['days_from_last_shipment', 'date'])
# duplicate into paris level and year level 
importus_delay_days = importus_delay_days.drop_duplicates()

directory = "/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/monthly"

for y in years:
    filename = f'USImport_{y}_index.csv'  # Assuming the files are in CSV format
    filepath = os.path.join(directory, filename)
    df_year = pd.read_csv(filepath)
    # merge importus_two_index and importus_delay_days by 'year', 'conPanjivaId', 'shpPanjivaId'
    importus = df_year.merge(importus_delay_days, on=['year', 'month', 'conPanjivaId', 'shpPanjivaId'], how='left')
    # save the data into csv file
    importus.to_csv(f'/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/monthly/USImport_{y}_index.csv', index=False)


# read csv file
directory = "/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/monthly"
files = Path(directory).glob('*.csv')

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

# %%
# calculate the median and mean of Total_teu, num_distinct_shpPanjivaId, average_days_from_last_shipment by year
Total_teu = importus.groupby(['year', 'month'])['total_teu_monthly'].agg(['median', 'mean']).reset_index()

num_distinct_shpPanjivaId = importus.groupby(['year', 'month'])['num_distinct_shpPanjivaId'].agg(['median', 'mean']).reset_index()
average_days_from_last_shipment = importus.groupby(['year', 'month'])['average_days_from_last_shipment'].agg(['median', 'mean']).reset_index()

# draw three figures of Total_teu, num_distinct_shpPanjivaId, average_days_from_last_shipment by year with two lines for median and mean

# Create a 'date' column in datetime format by combining year and month
Total_teu['date'] = pd.to_datetime(Total_teu[['year', 'month']].assign(day=1))
num_distinct_shpPanjivaId['date'] = pd.to_datetime(num_distinct_shpPanjivaId[['year', 'month']].assign(day=1))
average_days_from_last_shipment['date'] = pd.to_datetime(average_days_from_last_shipment[['year', 'month']].assign(day=1))

# change from the same month in 2019
Total_teu_median = Total_teu.drop(columns=['mean']) # all 2.0
Total_teu_median = Total_teu_median[Total_teu_median['year']>= 2019]
Total_teu_mean = Total_teu.drop(columns=['median'])
Total_teu_mean = Total_teu_mean[Total_teu_mean['year']>= 2019]
num_distinct_shpPanjivaId_median = num_distinct_shpPanjivaId.drop(columns=['mean'])
num_distinct_shpPanjivaId_median = num_distinct_shpPanjivaId_median[num_distinct_shpPanjivaId_median['year']>= 2019]
num_distinct_shpPanjivaId_mean = num_distinct_shpPanjivaId.drop(columns=['median'])
num_distinct_shpPanjivaId_mean = num_distinct_shpPanjivaId_mean[num_distinct_shpPanjivaId_mean['year']>= 2019]
average_days_from_last_shipment_median = average_days_from_last_shipment.drop(columns=['mean'])
average_days_from_last_shipment_median = average_days_from_last_shipment_median[average_days_from_last_shipment_median['year']>= 2019]
average_days_from_last_shipment_mean = average_days_from_last_shipment.drop(columns=['median'])
average_days_from_last_shipment_mean = average_days_from_last_shipment_mean[average_days_from_last_shipment_mean['year']>= 2019]

# pivot the data 
Total_teu_median = Total_teu_median.pivot(index='month', columns='year', values='median')
Total_teu_mean = Total_teu_mean.pivot(index='month', columns='year', values='mean')
num_distinct_shpPanjivaId_median = num_distinct_shpPanjivaId_median.pivot(index='month', columns='year', values='median')
num_distinct_shpPanjivaId_mean = num_distinct_shpPanjivaId_mean.pivot(index='month', columns='year', values='mean')
average_days_from_last_shipment_median = average_days_from_last_shipment_median.pivot(index='month', columns='year', values='median')
average_days_from_last_shipment_mean = average_days_from_last_shipment_mean.pivot(index='month', columns='year', values='mean')

# List of DataFrames and their corresponding names for value_name in melt
dataframes = [
    ('Total_teu_median', Total_teu_median, 'Total_teu_median_change_rate'),
    ('Total_teu_mean', Total_teu_mean, 'Total_teu_mean_change_rate'),
    ('num_distinct_shpPanjivaId_median', num_distinct_shpPanjivaId_median, 'num_distinct_shpPanjivaId_median_change_rate'),
    ('num_distinct_shpPanjivaId_mean', num_distinct_shpPanjivaId_mean, 'num_distinct_shpPanjivaId_mean_change_rate'),
    ('average_days_from_last_shipment_median', average_days_from_last_shipment_median, 'average_days_from_last_shipment_median_change_rate'),
    ('average_days_from_last_shipment_mean', average_days_from_last_shipment_mean, 'average_days_from_last_shipment_mean_change_rate')
]

for name, df, value_name in dataframes:
    for y in range(2020, 2025):
        df[y] = (df[y] / df[2019] - 1) * 100
    df = df.drop(columns=[2019])
    df = df.reset_index()
    df = df.melt(id_vars='month', var_name='year', value_name=value_name)
    df['year'] = df['year'].astype(int)
    df['month'] = df['month'].astype(int)
    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    print(df)
    # Replace the original DataFrame with the new one
    globals()[name] = df


Total_teu = Total_teu_median.merge(Total_teu_mean, on=['month', 'year', 'date'])
num_distinct_shpPanjivaId = num_distinct_shpPanjivaId_median.merge(num_distinct_shpPanjivaId_mean, on=['month', 'year', 'date'])
average_days_from_last_shipment = average_days_from_last_shipment_median.merge(average_days_from_last_shipment_mean, on=['month', 'year', 'date'])

# plots
fig, ax = plt.subplots(3, 1, figsize=(10, 15))

# Plot Total TEU
ax[0].plot(Total_teu['date'], Total_teu['Total_teu_median_change_rate'], label='Median')
ax[0].plot(Total_teu['date'], Total_teu['Total_teu_mean_change_rate'], label='Mean')
ax[0].set_title('Total Trade Volume by Pairs (TEU)')
ax[0].set_ylabel('Total_teu')
ax[0].set_xlabel("")
ax[0].xaxis.set_major_locator(mdates.MonthLocator(interval=6))  # Every 6 months
ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))  # Format to display month and year
ax[0].tick_params(axis='x', rotation=45)  # Rotate x-axis labels
ax[0].legend()  # Add legend for the first plot

# Plot Number of Shippers
ax[1].plot(num_distinct_shpPanjivaId['date'], num_distinct_shpPanjivaId['num_distinct_shpPanjivaId_median_change_rate'], label='Median')
ax[1].plot(num_distinct_shpPanjivaId['date'], num_distinct_shpPanjivaId['num_distinct_shpPanjivaId_mean_change_rate'], label='Mean')
ax[1].set_title('Number of Shippers for Each Consignee')
ax[1].set_ylabel('Number of Shippers')
ax[1].set_xlabel("")
ax[1].xaxis.set_major_locator(mdates.MonthLocator(interval=6))  # Every 6 months
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))  # Format to display month and year
ax[1].tick_params(axis='x', rotation=45)  # Rotate x-axis labels
ax[1].legend()  # Add legend for the second plot

# Plot Average Days from Last Shipment
ax[2].plot(average_days_from_last_shipment['date'], average_days_from_last_shipment['average_days_from_last_shipment_median_change_rate'], label='Median')
ax[2].plot(average_days_from_last_shipment['date'], average_days_from_last_shipment['average_days_from_last_shipment_mean_change_rate'], label='Mean')
ax[2].set_title('Average Days from Last Shipment')
ax[2].set_ylabel('Days')
ax[2].set_xlabel("")
ax[2].xaxis.set_major_locator(mdates.MonthLocator(interval=6))  # Every 6 months
ax[2].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))  # Format to display month and year
ax[2].tick_params(axis='x', rotation=45)  # Rotate x-axis labels
ax[2].legend()  # Add legend for the third plot

# Adjust layout to prevent overlapping labels
plt.tight_layout()
plt.text(0, -0.15, "Note: Change from the Same Month in 2019", fontsize=8, ha='left', transform=ax.transAxes)

# Show the plot
plt.show()

# %%

# combine and  expot Total_teu, num_distinct_shpPanjivaId, average_days_from_last_shipment into excel file
fig = pd.concat([Total_teu, num_distinct_shpPanjivaId, average_days_from_last_shipment], axis=1)
fig.to_excel('/Users/qianqiantang/Desktop/panjiva-code-main/Result/monthly_three_index.xlsx')

# %%
# plots
fig, ax = plt.subplots(3, 1, figsize=(10, 15))

# Plot Total TEU
ax[0].plot(Total_teu['date'], Total_teu['Total_teu_median_change_rate'], label='Median')
ax[0].plot(Total_teu['date'], Total_teu['Total_teu_mean_change_rate'], label='Mean')
ax[0].set_title('Total Trade Volume by Pairs (TEU)')
ax[0].set_ylabel('Total_teu')
ax[0].set_xlabel("")
ax[0].xaxis.set_major_locator(mdates.MonthLocator(interval=6))  # Every 6 months
ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))  # Format to display month and year
ax[0].tick_params(axis='x', rotation=45)  # Rotate x-axis labels
ax[0].legend()  # Add legend for the first plot

# Plot Number of Shippers
ax[1].plot(num_distinct_shpPanjivaId['date'], num_distinct_shpPanjivaId['num_distinct_shpPanjivaId_median_change_rate'], label='Median')
ax[1].plot(num_distinct_shpPanjivaId['date'], num_distinct_shpPanjivaId['num_distinct_shpPanjivaId_mean_change_rate'], label='Mean')
ax[1].set_title('Number of Shippers for Each Consignee')
ax[1].set_ylabel('Number of Shippers')
ax[1].set_xlabel("")
ax[1].xaxis.set_major_locator(mdates.MonthLocator(interval=6))  # Every 6 months
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))  # Format to display month and year
ax[1].tick_params(axis='x', rotation=45)  # Rotate x-axis labels
ax[1].legend()  # Add legend for the second plot

# Plot Average Days from Last Shipment
ax[2].plot(average_days_from_last_shipment['date'], average_days_from_last_shipment['average_days_from_last_shipment_median_change_rate'], label='Median')
ax[2].plot(average_days_from_last_shipment['date'], average_days_from_last_shipment['average_days_from_last_shipment_mean_change_rate'], label='Mean')
ax[2].set_title('Average Days from Last Shipment')
ax[2].set_ylabel('Days')
ax[2].set_xlabel("")
ax[2].xaxis.set_major_locator(mdates.MonthLocator(interval=6))  # Every 6 months
ax[2].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))  # Format to display month and year
ax[2].tick_params(axis='x', rotation=45)  # Rotate x-axis labels
ax[2].legend()  # Add legend for the third plot

# Adjust layout to prevent overlapping labels
plt.tight_layout()

# Add text at the bottom (relative to the figure)
fig.text(0, -0.02, "Note: Change from the Same Month in 2019", fontsize=8, ha='left')

# Show the plot
plt.show()

# %%
