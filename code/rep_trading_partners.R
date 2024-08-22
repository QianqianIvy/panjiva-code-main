library(lubridate)
library(tidyverse)
library(quantmod)

# this is base on monthly data

# set up data directory to the below path
#/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/monthly
setwd("/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/monthly")

# input USImport_monthly.csv as import_us
import_us <- read_csv("USImport_monthly.csv")

# calculate the number of distinct shppanjivaid for each conpanjivaid by year by month
trading_partners <- import_us %>%
  filter(concountry == "United States" | is.null(concountry)) %>%
  #filter if conpanjivaid, shppanjivaid ==999
  filter(conpanjivaid != 999 & shppanjivaid != 999) %>%
  group_by(conpanjivaid, year, month) %>%
  summarise(count = n_distinct(shppanjivaid))
  
# cut the count into categories
trading_partners$categories = cut(trading_partners$count, breaks = c(0, 1,4,9, 24, 49, 200))

# merge the trading_partners with import_us
import_us = merge(x = import_us, y = trading_partners, by = c("conpanjivaid", "year", "month"), all = TRUE)

# filter the NA categories
cat_na <- import_us %>%
  filter(is.na(categories))

# show the first ten rows of import_us
head(import_us)


