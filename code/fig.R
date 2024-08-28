# import package for plots, reading csv files
library(ggplot2)
library(readr)

# read csv file delay_days.csv
delay_days <- read_csv("/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/delay_days.csv") #nolint
# show the first few rows of the data
head(delay_days)
