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
# This code is for the trade pattern

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
    # drop non necessary columns for figure 8
    df = df.drop(columns=['panjivaRecordId', 'conName', 'conFullAddress', 'conRoute', 'conCity', 
                            'conStateRegion', 'conPostalCode', 'shpmtDestination',
                            'volumeTEU', 'conCountry', 'shpCountry'])

    #change conPanjivaId, shpPanjivaId, year, month, day to int
    df[['year', 'month', 'day']] = df[['year', 'month', 'day']].apply(pd.to_numeric, errors='coerce')
    # drop if year month day is na/nan
    df.dropna(subset=['year', 'month', 'day'], inplace=True)
    
    # calculate the number of distinct shipments by date and shpmtOrigin
    df = df.groupby(['year', 'month', 'day', 'shpmtOrigin']).size().reset_index(name='num_of_ship')

    # generate the date column
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])

    #Add the file to the list
    fileData.append(df)

# %%
# print the time it takes to run the code
print("--- %s seconds ---" % (time.time() - start_time))

# %%
# concatenate all files in files
shpmtorigin_daily = pd.concat(fileData)

# %% 
# 7-days moving average by shpmtOrigin
# sort shpmtOrigin and dates
shpmtorigin_daily = shpmtorigin_daily.sort_values(by=['shpmtOrigin', 'date'])

shpmtorigin_daily['daily_shpt_wma'] = shpmtorigin_daily.groupby('shpmtOrigin')['num_of_ship'].transform(lambda x: x.rolling(window=7, min_periods=1).mean())


# calculate the portion of each shpmtOrigin in the total number of shipments
shpmtorigin_daily['total_shpmt'] = shpmtorigin_daily.groupby('date')['num_of_ship'].transform('sum')
shpmtorigin_daily['percentage_origin'] = shpmtorigin_daily['num_of_ship'] / shpmtorigin_daily['total_shpmt']
shpmtorigin_daily

# summarize the statitics of percentage_origin
shpmtorigin_daily['percentage_origin'].describe()
# %%
# China counts over 30% of the total daily shipments 
china_daily = shpmtorigin_daily[shpmtorigin_daily['shpmtOrigin'] == 'China'].sort_values(by='date')

# change of daily_shpt_wma from 2015-01-01
china_daily['change_of_daily_shpt_wma_2015'] = (china_daily['daily_shpt_wma']/china_daily['daily_shpt_wma'].iloc[0] -1) * 100

# china_daily['change_of_daily_shpt_wma_2015'].iloc[0] = 0
china_daily['date'] = pd.to_datetime(china_daily['date'])
# %%
# change of total_shpmt from 2015-01-01
china_daily['total_shpmt_wma'] = china_daily['total_shpmt'].rolling(window=7, min_periods=1).mean()

china_daily['change_of_total_shpmt_2015'] = (china_daily['total_shpmt_wma']/china_daily['total_shpmt_wma'].iloc[0] -1) * 100
# china_daily['change_of_total_shpmt_2015'].iloc[0] = 0
# %%


# Assuming data_in_export and data_us_import are DataFrames
# Define colors
colors = {"U.S. imports from China": "#1f77b4", "U.S. imports from the World": "#ff7f0e"}

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Add the lines
sns.lineplot(data=china_daily, x='date', y='change_of_daily_shpt_wma_2015', color=colors["U.S. imports from China"], linewidth=0.8, label="U.S. imports from China", ax=ax)
sns.lineplot(data=china_daily, x='date', y='change_of_total_shpmt_2015', color=colors["U.S. imports from the World"], linewidth=0.5, label="U.S. imports from the World", ax=ax)

# Add the vertical line
ax.axvline(pd.to_datetime("2020-03-01"), linestyle='dotted', color='black')

# Customize the labels, legend, and themes
ax.set_xlabel("")
ax.set_ylabel("")
ax.set_title("US-China Shipments (2015-2024)", fontsize=12)
ax.legend(title="Legend")
# Tilt x-axis labels
plt.xticks(rotation=45)
# Set the x and y axis scales
ax.set_xlim(pd.to_datetime("2015-01-01"), pd.to_datetime("2024-06-18"))
ax.xaxis.set_major_locator(YearLocator())
ax.xaxis.set_major_formatter(DateFormatter("%Y"))
ax.set_ylim(-30, 500)
ax.set_yticks(range(-30, 500, 20))

# Customize the legend position and size
ax.legend(loc='lower right', bbox_to_anchor=(0.6, 0.8), ncol=1, fontsize='small', title="Legend", title_fontsize='small')
plt.text(0, -0.15, "Note: Index, 2015-01-01 = 100", fontsize=8, ha='left', transform=ax.transAxes)

# Show the plot
plt.show()
fig.savefig('/Users/qianqiantang/Desktop/panjiva-code-main/Result/figure9_China_2015-2024.png')

# %%
# Assuming data_in_export and data_us_import are DataFrames
# Define colors
colors = {"U.S. imports from China": "#1f77b4", "U.S. imports from the World": "#ff7f0e"}

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Add the lines
sns.lineplot(data=china_daily, x='date', y='change_of_daily_shpt_wma_2015', color=colors["U.S. imports from China"], linewidth=0.8, label="U.S. imports from China", ax=ax)
sns.lineplot(data=china_daily, x='date', y='change_of_total_shpmt_2015', color=colors["U.S. imports from the World"], linewidth=0.5, label="U.S. imports from the World", ax=ax)

# Add the vertical line
#ax.axvline(pd.to_datetime("2020-01-01"), linestyle='dotted', color='black')

# Customize the labels, legend, and themes
ax.set_xlabel("")
ax.set_ylabel("")
ax.set_title("US-China Daily Shippments in 2020", fontsize=12)
ax.legend(title="Legend")
# Tilt x-axis labels
plt.xticks(rotation=45)
# Set the x and y axis scales
ax.set_xlim(pd.to_datetime("2020-01-01"), pd.to_datetime("2020-12-31"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(DateFormatter("%b"))
ax.set_ylim(-30, 400)
ax.set_yticks(range(-30, 400, 20))

# Customize the legend position and size
ax.legend(loc='lower right', bbox_to_anchor=(0.6, 0.8), ncol=1, fontsize='small', title="Legend", title_fontsize='small')
# add note at the bottom left under the x axis label
plt.text(0, -0.15, "Note: Index, Mar. 1, 2015-01-01 = 100", fontsize=8, ha='left', transform=ax.transAxes)

# Show the plot
plt.show()
fig.savefig('/Users/qianqiantang/Desktop/panjiva-code-main/Result/figure9_China_2020.png')


# %%
# Assuming data_in_export and data_us_import are DataFrames
# Define colors
colors = {"U.S. imports from China": "#1f77b4", "U.S. imports from the World": "#ff7f0e"}

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Add the lines
sns.lineplot(data=china_daily, x='date', y='change_of_daily_shpt_wma_2015', color=colors["U.S. imports from China"], linewidth=0.8, label="U.S. imports from China", ax=ax)
sns.lineplot(data=china_daily, x='date', y='change_of_total_shpmt_2015', color=colors["U.S. imports from the World"], linewidth=0.5, label="U.S. imports from the World", ax=ax)

# Add the vertical line
#ax.axvline(pd.to_datetime("2015-01-01"), linestyle='dotted', color='black')

# Customize the labels, legend, and themes
ax.set_xlabel("")
ax.set_ylabel("")
ax.set_title("US-China Daily Shippments in 2021", fontsize=12)
ax.legend(title="Legend")
# Tilt x-axis labels
plt.xticks(rotation=45)
# Set the x and y axis scales
ax.set_xlim(pd.to_datetime("2021-01-01"), pd.to_datetime("2021-12-31"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(DateFormatter("%b"))
ax.set_ylim(100, 500)
ax.set_yticks(range(100, 500, 20))

# Customize the legend position and size
ax.legend(loc='lower right', bbox_to_anchor=(0.6, 0.8), ncol=1, fontsize='small', title="Legend", title_fontsize='small')
# add note at the bottom left under the x axis label
plt.text(0, -0.15, "Note: Index, 2015-01-01 = 100", fontsize=8, ha='left', transform=ax.transAxes)

# Show the plot
plt.show()
fig.savefig('/Users/qianqiantang/Desktop/panjiva-code-main/Result/figure9_China_2021.png')

# %%
# Assuming data_in_export and data_us_import are DataFrames
# Define colors
colors = {"U.S. imports from China": "#1f77b4", "U.S. imports from the World": "#ff7f0e"}

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Add the lines
sns.lineplot(data=china_daily, x='date', y='change_of_daily_shpt_wma_2015', color=colors["U.S. imports from China"], linewidth=0.8, label="U.S. imports from China", ax=ax)
sns.lineplot(data=china_daily, x='date', y='change_of_total_shpmt_2015', color=colors["U.S. imports from the World"], linewidth=0.5, label="U.S. imports from the World", ax=ax)

# Add the vertical line
#ax.axvline(pd.to_datetime("2015-01-01"), linestyle='dotted', color='black')

# Customize the labels, legend, and themes
ax.set_xlabel("")
ax.set_ylabel("")
ax.set_title("US-China Daily Shippments in 2022", fontsize=12)
ax.legend(title="Legend")
# Tilt x-axis labels
plt.xticks(rotation=45)
# Set the x and y axis scales
ax.set_xlim(pd.to_datetime("2022-01-01"), pd.to_datetime("2022-12-31"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(DateFormatter("%b"))
ax.set_ylim(50, 500)
ax.set_yticks(range(50, 500, 20))

# Customize the legend position and size
ax.legend(loc='lower right', bbox_to_anchor=(0.6, 0.8), ncol=1, fontsize='small', title="Legend", title_fontsize='small')
# add note at the bottom left under the x axis label
plt.text(0, -0.15, "Note: Index, 2015-01-01 = 100", fontsize=8, ha='left', transform=ax.transAxes)

# Show the plot
plt.show()
fig.savefig('/Users/qianqiantang/Desktop/panjiva-code-main/Result/figure9_China_2022.png')


# %%
# Assuming data_in_export and data_us_import are DataFrames
# Define colors
colors = {"U.S. imports from China": "#1f77b4", "U.S. imports from the World": "#ff7f0e"}

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Add the lines
sns.lineplot(data=china_daily, x='date', y='change_of_daily_shpt_wma_2015', color=colors["U.S. imports from China"], linewidth=0.8, label="U.S. imports from China", ax=ax)
sns.lineplot(data=china_daily, x='date', y='change_of_total_shpmt_2015', color=colors["U.S. imports from the World"], linewidth=0.5, label="U.S. imports from the World", ax=ax)

# Add the vertical line
#ax.axvline(pd.to_datetime("2015-01-01"), linestyle='dotted', color='black')

# Customize the labels, legend, and themes
ax.set_xlabel("")
ax.set_ylabel("")
ax.set_title("US-China Daily Shippments in 2023", fontsize=12)
ax.legend(title="Legend")
# Tilt x-axis labels
plt.xticks(rotation=45)
# Set the x and y axis scales
ax.set_xlim(pd.to_datetime("2023-01-01"), pd.to_datetime("2023-12-31"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(DateFormatter("%b"))
ax.set_ylim(50, 500)
ax.set_yticks(range(50, 500, 20))

# Customize the legend position and size
ax.legend(loc='lower right', bbox_to_anchor=(0.6, 0.8), ncol=1, fontsize='small', title="Legend", title_fontsize='small')
# add note at the bottom left under the x axis label
plt.text(0, -0.15, "Note: Index, 2015-01-01 = 100", fontsize=8, ha='left', transform=ax.transAxes)

# Show the plot
plt.show()
fig.savefig('/Users/qianqiantang/Desktop/panjiva-code-main/Result/figure9_China_2023.png')
# %%
# Define colors
colors = {"U.S. imports from China": "#1f77b4", "U.S. imports from the World": "#ff7f0e"}

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Add the lines
sns.lineplot(data=china_daily, x='date', y='change_of_daily_shpt_wma_2015', color=colors["U.S. imports from China"], linewidth=0.8, label="U.S. imports from China", ax=ax)
sns.lineplot(data=china_daily, x='date', y='change_of_total_shpmt_2015', color=colors["U.S. imports from the World"], linewidth=0.5, label="U.S. imports from the World", ax=ax)

# Add the vertical line
#ax.axvline(pd.to_datetime("2015-01-01"), linestyle='dotted', color='black')

# Customize the labels, legend, and themes
ax.set_xlabel("")
ax.set_ylabel("")
ax.set_title("US-China Daily Shippments in 2024", fontsize=12)
ax.legend(title="Legend")
# Tilt x-axis labels
plt.xticks(rotation=45)
# Set the x and y axis scales
ax.set_xlim(pd.to_datetime("2024-01-01"), pd.to_datetime("2024-06-18"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(DateFormatter("%b"))
ax.set_ylim(0, 500)
ax.set_yticks(range(0, 500, 20))

# Customize the legend position and size
ax.legend(loc='lower right', bbox_to_anchor=(0.6, 0.8), ncol=1, fontsize='small', title="Legend", title_fontsize='small')
# add note at the bottom left under the x axis label
plt.text(0, -0.15, "Note: Index, 2015-01-01 = 100", fontsize=8, ha='left', transform=ax.transAxes)

# Show the plot
plt.show()
fig.savefig('/Users/qianqiantang/Desktop/panjiva-code-main/Result/figure9_China_2024.png')
# %%
#####################################
#Packages needed to run code
import pandas as pd
from pathlib import Path
import time
import os
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter, YearLocator

# monthly data

shpmtorigin_daily = pd.read_csv('/Users/qianqiantang/Desktop/panjiva-code-main/Result/shpmtorigin_daily.csv')
shpmtorigin_monthly = shpmtorigin_daily.groupby(['year', 'month', 'shpmtOrigin'])['num_of_ship'].sum().reset_index()
shpmtorigin_monthly['total_monthly_shpmt'] = shpmtorigin_monthly.groupby(['year', 'month'])['num_of_ship'].transform('sum')
shpmtorigin_monthly['percentage_origin'] = shpmtorigin_monthly['num_of_ship'] / shpmtorigin_monthly['total_monthly_shpmt']
# %%
# high frequency trade partners ['percentage_origin']>=0.05
china_monthly = shpmtorigin_monthly[shpmtorigin_monthly['shpmtOrigin'] == 'China'].sort_values(by=['year', 'month'])
southkorea_monthly = shpmtorigin_monthly[shpmtorigin_monthly['shpmtOrigin'] == 'South Korea'].sort_values(by=['year', 'month'])
hk_monthly = shpmtorigin_monthly[shpmtorigin_monthly['shpmtOrigin'] == 'Hong Kong'].sort_values(by=['year', 'month'])
india_monthly = shpmtorigin_monthly[shpmtorigin_monthly['shpmtOrigin'] == 'India'].sort_values(by=['year', 'month'])
taiwan_monthly = shpmtorigin_monthly[shpmtorigin_monthly['shpmtOrigin'] == 'Taiwan'].sort_values(by=['year', 'month'])
germany_monthly = shpmtorigin_monthly[shpmtorigin_monthly['shpmtOrigin'] == 'Germany'].sort_values(by=['year', 'month'])
italy_monthly = shpmtorigin_monthly[shpmtorigin_monthly['shpmtOrigin'] == 'Italy'].sort_values(by=['year', 'month'])
vietnam_monthly = shpmtorigin_monthly[shpmtorigin_monthly['shpmtOrigin'] == 'Vietnam'].sort_values(by=['year', 'month'])
world_monthly = shpmtorigin_monthly[['year', 'month', 'total_monthly_shpmt']].drop_duplicates().sort_values(by=['year', 'month'])

# rename world_monthly['total_monthly_shpmt'] to 'num_of_ship'
world_monthly = world_monthly.rename(columns={'total_monthly_shpmt': 'num_of_ship'})
# %%
# List of trade partners' monthly dataframes and their corresponding names
trade_partners = {
    'world': world_monthly, 'china': china_monthly, 'southkorea': southkorea_monthly,
    'hk': hk_monthly, 'india': india_monthly, 'taiwan': taiwan_monthly,
    'germany': germany_monthly, 'italy': italy_monthly, 'vietnam': vietnam_monthly
}

# List of years to consider for COVID impact
covid_years = [2019, 2020, 2021, 2022, 2023, 2024]

# Initialize a list to collect data for each trade partner
partnerData = []

# Loop through each partner and calculate YoY growth
for partner_name, partner_df in trade_partners.items():
    # Pivot the DataFrame to have months as rows and years as columns
    partner_pivot = partner_df.pivot(index='month', columns='year', values='num_of_ship')
    
    # Keep only years from 2019 onwards
    partner_pivot = partner_pivot.loc[:, partner_pivot.columns >= 2019]

    # Calculate YoY growth for each year relative to 2019
    for year in range(2020, 2025):
        partner_pivot[year] = (partner_pivot[year] / partner_pivot[2019] - 1) * 100
    partner_pivot = partner_pivot.drop(columns=2019)



    # Reset the index to have 'month' as a column again
    partner_pivot = partner_pivot.reset_index()

    # Melt the pivot table back to long format
    partner_melted = partner_pivot.melt(id_vars='month', var_name='year', value_name='yoy_growth_rate_num_of_ship')
    partner_melted['shpmtOrigin'] = partner_name

    # Add this trade partner's data to the list
    partnerData.append(partner_melted)

# Concatenate all the partners' data into one DataFrame
trading_partners_shp_frequency = pd.concat(partnerData, ignore_index=True)
# set date
trading_partners_shp_frequency['date'] = pd.to_datetime(trading_partners_shp_frequency[['year', 'month']].assign(day=1))


# Inspect the final dataframe
print(trading_partners_shp_frequency.head())


# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Assume df is your DataFrame with 'country', 'year', 'month', and 'num_ship' columns

# Create the plot
plt.figure(figsize=(15, 10))

# Use seaborn's lineplot to draw multiple lines, one for each country
sns.lineplot(data=trading_partners_shp_frequency, x='date', y='yoy_growth_rate_num_of_ship', hue='shpmtOrigin', marker='o')

# Customize the labels, legend, and themes
# NO NEED TO SET X AND Y LABELS
plt.xlabel("")
plt.ylabel("")
plt.title("Shipments by Country", fontsize=16)
plt.legend(title="shpmtOrigin", title_fontsize='large', fontsize='large')
plt.xticks(rotation=45)


# Tilt x-axis labels
plt.xticks(rotation=45)
# Set the x and y axis scales
ax.set_xlim(pd.to_datetime("2020-01-01"), pd.to_datetime("2024-05-01"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.xaxis.set_major_formatter(DateFormatter("%b"))
ax.set_ylim(50, 500)
ax.set_yticks(range(50, 500, 20))

# Customize the legend position and size
ax.legend(loc='lower right', bbox_to_anchor=(0.6, 0.8), ncol=1, fontsize='small', title="Legend", title_fontsize='small')
# add note at the bottom left under the x axis label
plt.text(0, -0.1, "Note: Percent change from same month in 2019", fontsize=8, ha='left', transform=ax.transAxes)

# Show the plot
plt.show()
fig.savefig('/Users/qianqiantang/Desktop/panjiva-code-main/Result/trading_partner.png')

# %%
# only world, china, hk, southkorea, taiwan
# List of trade partners' monthly dataframes and their corresponding names
trade_partners_main = trading_partners_shp_frequency[trading_partners_shp_frequency['shpmtOrigin'].isin(['world', 'china', 'vietnam'])]
# %%
# Create the plot
plt.figure(figsize=(15, 10))

# Use seaborn's lineplot to draw multiple lines, one for each country
sns.lineplot(data=trade_partners_main, x='date', y='yoy_growth_rate_num_of_ship', hue='shpmtOrigin', marker='o')

# Customize the labels, legend, and themes
# NO NEED TO SET X AND Y LABELS
plt.xlabel("")
plt.ylabel("")
plt.title("Shipments by Country", fontsize=16)
plt.legend(title="shpmtOrigin", title_fontsize='large', fontsize='large')
plt.xticks(rotation=45)


# Tilt x-axis labels
plt.xticks(rotation=45)
# Set the x and y axis scales
ax.set_xlim(pd.to_datetime("2020-01-01"), pd.to_datetime("2024-05-01"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.xaxis.set_major_formatter(DateFormatter("%b"))
ax.set_ylim(50, 500)
ax.set_yticks(range(50, 500, 20))

# Customize the legend position and size
ax.legend(loc='lower right', bbox_to_anchor=(0.6, 0.8), ncol=1, fontsize='small', title="Legend", title_fontsize='small')
# add note at the bottom left under the x axis label
plt.text(0, -0.1, "Note: Percent change from same month in 2019", fontsize=8, ha='left', transform=ax.transAxes)

# Show the plot
plt.show()
fig.savefig('/Users/qianqiantang/Desktop/panjiva-code-main/Result/trading_partner_china_vietnam.png')
# %%
