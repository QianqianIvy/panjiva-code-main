# %%
# read me 
# This code is used to replicate figure 6 in Flaaen et al. (2023)
# necassary packages
import pandas as pd
from pathlib import Path
import time
import os
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.seasonal import STL
import numpy as np

# read 2019 data for replicating figure 6 and 7 in Flaaen et al. (2023)
df_2019 = pd.read_csv('/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/annual/annual_raw_address/USImport_2019.csv')
#   filter(concountry == "United States" | is.null(concountry)) %>%
df_2019 = df_2019[(df_2019['conCountry'] == 'United States') | (df_2019['conCountry'].isnull())]
df_2019 = df_2019.drop(columns=['panjivaRecordId', 'conName', 'conFullAddress', 'conRoute', 'conCity',
                                'conStateRegion', 'conPostalCode', 'conCountry', 'shpCountry', 'shpmtOrigin', 'shpmtDestination',
                                'month', 'day', 'date'])

# %%
# drop nan in conPanjivaId	shpPanjivaId	volumeTEU
df_2019 = df_2019.dropna(subset=['conPanjivaId', 'shpPanjivaId', 'volumeTEU'])
df_2019['conPanjivaId'] = df_2019['conPanjivaId'].astype(int)
df_2019['shpPanjivaId'] = df_2019['shpPanjivaId'].astype(int)

# calculate the number of distinct shpPanjivaId for each conPanjivaId
df_2019['shippers'] = df_2019.groupby('conPanjivaId')['shpPanjivaId'].transform('nunique')
df_2019['shippers_volume'] = df_2019.groupby('conPanjivaId')['volumeTEU'].transform('sum')

# calculate the number of distinct conPanjivaId for each shpPanjivaId
df_2019['consignees'] = df_2019.groupby('shpPanjivaId')['conPanjivaId'].transform('nunique')
df_2019['consignees_volume'] = df_2019.groupby('shpPanjivaId')['volumeTEU'].transform('sum')

print(df_2019.head())

# %%
# drop duplicates
df_2019 = df_2019.drop(columns=[ 'volumeTEU'])
df_2019 = df_2019.drop_duplicates()

# %%
# define the bins
df_2019['bin_shippers'] = np.select(
    [
        df_2019['shippers'] == 1,
        (df_2019['shippers'] > 1) & (df_2019['shippers'] <= 4),
        (df_2019['shippers'] > 4) & (df_2019['shippers'] <= 9),
        (df_2019['shippers'] > 9) & (df_2019['shippers'] <= 24),
        df_2019['shippers'] > 24
    ],
    [
        '1',
        '2',
        '3',
        '4',
        '5'
    ],
    default='NaN'
)

df_2019['bin_consignees'] = np.select(
    [
        df_2019['consignees'] == 1,
        (df_2019['consignees'] > 1) & (df_2019['consignees'] <= 4),
        (df_2019['consignees'] > 4) & (df_2019['consignees'] <= 9),
        (df_2019['consignees'] > 9) & (df_2019['consignees'] <= 24),
        df_2019['consignees'] > 24
    ],
    [
        '1',
        '2',
        '3',
        '4',
        '5'
    ],
    default='NaN'
)

# %%
# group by bins
data_consignees_teu = df_2019.drop(columns=['conPanjivaId', 'shippers_volume', 'bin_shippers', 'shippers']).drop_duplicates()
data_shippers_teu = df_2019.drop(columns=['shpPanjivaId', 'consignees_volume', 'bin_consignees', 'consignees']).drop_duplicates()
print(data_consignees_teu.head())
print(data_shippers_teu.head())
# %%
# figure 6-left: the percentage of conPanjivaId who owns a certain number of shippers
total_teu= data_shippers_teu['shippers_volume'].sum()

# group by bin_shippers summarize the shippers_volume and devide by the total_teu
teu_by_bin = data_shippers_teu.groupby('bin_shippers')['shippers_volume'].sum().reset_index() 
teu_by_bin['percentage_teu'] = 100 * teu_by_bin['shippers_volume']/total_teu

conPanjivaId_by_bin = data_shippers_teu.groupby('bin_shippers')['conPanjivaId'].nunique().reset_index()
conPanjivaId_by_bin['percentage_consignees'] = 100 * conPanjivaId_by_bin['conPanjivaId']/conPanjivaId_by_bin['conPanjivaId'].sum()

# merge teu_by_bin and conPanjivaId_by_bin by bin_shippers
bar_data_shp = pd.merge(teu_by_bin, conPanjivaId_by_bin, on='bin_shippers')
bar_data_shp

# %%
# figure 6-right: the percentage of shpPanjivaId who owns a certain number of consignees
total_teu_con= data_consignees_teu['consignees_volume'].sum()
teu_by_bin_con = data_consignees_teu.groupby('bin_consignees')['consignees_volume'].sum().reset_index()
teu_by_bin_con['percentage_teu'] =  100 * teu_by_bin_con['consignees_volume']/total_teu_con

shpPanjivaId_by_bin = data_consignees_teu.groupby('bin_consignees')['shpPanjivaId'].nunique().reset_index()
shpPanjivaId_by_bin['percentage_shippers'] =  100 * shpPanjivaId_by_bin['shpPanjivaId']/shpPanjivaId_by_bin['shpPanjivaId'].sum()

bar_data_con = pd.merge(teu_by_bin_con, shpPanjivaId_by_bin, on='bin_consignees')
bar_data_con

# %% 
# export data for figure 6
bar_data_shp.to_csv('/Users/qianqiantang/Desktop/panjiva-code-main/Result/data_weighted_hist_shp_con.csv', index=False)
bar_data_con.to_csv('/Users/qianqiantang/Desktop/panjiva-code-main/Result/data_weighted_hist_con_shp.csv', index=False)


# %%
# figure 6
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Pivot the DataFrame to create the 'type' column
bar_data_shp_long = bar_data_shp.melt(
    id_vars=['bin_shippers'],
    value_vars=['percentage_teu', 'percentage_consignees'],
    var_name='type',
    value_name='percent'
)

# Rename the 'type' values for better readability
bar_data_shp_long['type'] = bar_data_shp_long['type'].replace({
    'percentage_teu': 'Percent of total TEU',
    'percentage_consignees': 'Percent of total U.S. consignees'
})

# Set the order of the categories in the 'type' column
bar_data_shp_long['type'] = pd.Categorical(
    bar_data_shp_long['type'],
    categories=['Percent of total U.S. consignees', 'Percent of total TEU'],
    ordered=True
)

# Pivot the DataFrame to create the 'type' column
bar_data_con_long = bar_data_con.melt(
    id_vars=['bin_consignees'],
    value_vars=['percentage_teu', 'percentage_shippers'],
    var_name='type',
    value_name='percent'
)

# Rename the 'type' values for better readability
bar_data_con_long['type'] = bar_data_con_long['type'].replace({
    'percentage_teu': 'Percent of total TEU',
    'percentage_shippers': 'Percent of total U.S. shippers'
})

# Set the order of the categories in the 'type' column
bar_data_con_long['type'] = pd.Categorical(
    bar_data_con_long['type'],
    categories=['Percent of total U.S. shippers', 'Percent of total TEU'],
    ordered=True
)

# Assuming bar_data_shp is a pandas DataFrame
# Example DataFrame creation (replace with actual data loading)
# bar_data_shp = pd.read_csv('/path/to/data_weighted_hist_con_shp.csv')

# %%
# Define approved colors
approved_colors = {
    "lightblue": "#ADD8E6",
    "blue": "#0000FF"
}

# figure 6 left
# Create the plot
plt.figure(figsize=(10, 6))
hist_weighted_shp_1 = sns.barplot(
    data=bar_data_shp_long,
    x='bin_shippers',
    y='percent',
    hue='type',
    palette={
        "Percent of total U.S. consignees": approved_colors["blue"],
        "Percent of total TEU": approved_colors["lightblue"]
    },
    dodge=True
)

# Customize the x-axis labels
hist_weighted_shp_1.set_xticklabels(["1", "2-4", "5-9", "10-24", "25+"])

# Set labels and title
hist_weighted_shp_1.set_xlabel("Number of foreign shippers")
hist_weighted_shp_1.set_ylabel("")
hist_weighted_shp_1.set_title("")
hist_weighted_shp_1.set_title("Percent", loc='center', pad=20)

# Customize the legend
legend = hist_weighted_shp_1.legend(loc='upper left', bbox_to_anchor=(0.6, 0.8), fontsize=8)
legend.set_title("")
for handle in legend.legendHandles:
    handle.set_sizes([0.5])

# Customize the y-axis limits
hist_weighted_shp_1.set_ylim(0, 80)

# Apply additional theme settings if needed
# Example: plt.style.use('seaborn-darkgrid')

# Show the plot
plt.show()

# save the plot
hist_weighted_shp_1.figure.savefig('/Users/qianqiantang/Desktop/panjiva-code-main/Result/figure6_left.png')
# %%
# figure 6 right
# Create the plot
plt.figure(figsize=(10, 6))
hist_weighted_con_1 = sns.barplot(
    data=bar_data_con_long,
    x='bin_consignees',
    y='percent',
    hue='type',
    palette={
        "Percent of total U.S. shippers": approved_colors["blue"],
        "Percent of total TEU": approved_colors["lightblue"]
    },
    dodge=True
)

# Customize the x-axis labels
hist_weighted_con_1.set_xticklabels(["1", "2-4", "5-9", "10-24", "25+"])

# Set labels and title
hist_weighted_con_1.set_xlabel("Number of foreign consignees")
hist_weighted_con_1.set_ylabel("")
hist_weighted_con_1.set_title("")
hist_weighted_con_1.set_title("Percent", loc='center', pad=20)

# Customize the legend
legend = hist_weighted_con_1.legend(loc='upper left', bbox_to_anchor=(0.6, 0.8), fontsize=8)
legend.set_title("")
for handle in legend.legendHandles:
    handle.set_sizes([0.5])

# Customize the y-axis limits
hist_weighted_con_1.set_ylim(0, 80)

# Apply additional theme settings if needed
# Example: plt.style.use('seaborn-darkgrid')

# Show the plot
plt.show()

# save the plot
hist_weighted_con_1.figure.savefig('/Users/qianqiantang/Desktop/panjiva-code-main/Result/figure6_right.png')
# %%
