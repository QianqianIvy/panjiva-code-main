library(lubridate)
library(tidyverse)
library(quantmod)

# this is base on monthly data

# set up data directory to the below path
#/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/monthly
setwd("/Users/qianqiantang/Desktop/panjiva-code-main/Processed_data/USImport/monthly") #nolint

# input USImport_monthly.csv as import_us
import_us <- read_csv("USImport_monthly.csv")

# calculate the number of distinct shppanjivaid for each conpanjivaid by year by month #nolint
trading_partners <- import_us %>%
  filter(concountry == "United States" | is.null(concountry)) %>%
  #filter if conpanjivaid, shppanjivaid ==999
  filter(conpanjivaid != 999 & shppanjivaid != 999) %>%
  group_by(conpanjivaid, year, month) %>%
  summarise(count = n_distinct(shppanjivaid))

# cut the count into categories
trading_partners$categories = cut(trading_partners$count, breaks = c(0, 1,4,9, 24, 49, 200)) #nolint

# merge the trading_partners with import_us
import_us = merge(x = import_us, y = trading_partners, by = c("conpanjivaid", "year", "month"), all = TRUE) #nolint

# show the last 10 rows of import_us
# tail(import_us) # nolint

# save import_us as import_us.csv
write.csv(import_us, "import_us_monthly.csv")

###############################################################################
# this is base on annual data

# summarize volumeteu by conpanjivaid, year, shppanjivaid. 
# keep all of other columns and save as import_us_annual
import_us_annual <- import_us %>%
  group_by(conpanjivaid, year, shppanjivaid, shpmtdestination, concountry, shpcountry, conname) %>% #nolint
  summarise(volumeteu_annual = sum(volumeteu))

# calculate the number of distinct shppanjivaid for each conpanjivaid by year
trading_partners_annual <- import_us %>%
  filter(concountry == "United States" | is.null(concountry)) %>%
  #filter if conpanjivaid, shppanjivaid ==999
  filter(conpanjivaid != 999 & shppanjivaid != 999) %>%
  group_by(conpanjivaid, year) %>%
  summarise(count_annual = n_distinct(shppanjivaid))

# cut the count into categories
trading_partners_annual$categories_annual = cut(trading_partners_annual$count_annual, breaks = c(0, 1,4,9, 24, 49, 200)) #nolint

# merge the trading_partners with import_us
import_us_annual = merge(x = import_us_annual, y = trading_partners_annual, by = c("conpanjivaid", "year"), all = TRUE) #nolint

# save import_us_annual as import_us_annual.csv
write.csv(import_us_annual, "import_us_annual.csv")


############################################################################################################ nolint
# this is base on quater data

# create a date column
import_us$Date <- make_date(import_us$year, import_us$month, 1)

#create a quater column
import_us$quarter <- quarter(import_us$Date)

# drop Date column
import_us$Date <- NULL
tail(import_us) # nolint

# summarize volumeteu by conpanjivaid, year, quater shppanjivaid
import_us_quarter <- import_us %>%
  group_by(conpanjivaid, year, quarter, shppanjivaid, shpmtdestination, concountry, shpcountry, conname) %>% #nolint
  summarise(volumeteu_quarter = sum(volumeteu))

tail(import_us_quarter) # nolint

# calculate the number of distinct shppanjivaid for each conpanjivaid by year by quater
trading_partners_quarter <- import_us %>%
  filter(concountry == "United States" | is.null(concountry)) %>%
  #filter if conpanjivaid, shppanjivaid ==999
  filter(conpanjivaid != 999 & shppanjivaid != 999) %>%
  group_by(conpanjivaid, year, quarter) %>%
  summarise(count_quarter = n_distinct(shppanjivaid))

# cut the count into categories
trading_partners_quarter$categories_quarter = cut(trading_partners_quarter$count_quarter, breaks = c(0, 1,4,9, 24, 49, 200)) #nolint

# merge the trading_partners with import_us
import_us_quarter = merge(x = import_us_quarter, y = trading_partners_quarter, by = c("conpanjivaid", "year", "quarter"), all = TRUE) #nolint

tail(import_us_quater) # nolint

# save import_us_quater as import_us_quater.csv
write.csv(import_us_quater, "import_us_quarter.csv")
