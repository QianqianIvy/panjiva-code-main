library(lubridate)
library(tidyverse)
library(DBI)
library(seasonal)
library(rstudioapi)
library(data.table) # for fread opening big data files

dir <- dirname(rstudioapi::getSourceEditorContext()$path)
setwd(dir)

#import the first part of data
file_path <- '/Users/qianqiantang/Desktop/panjiva-code-main/data_for_paper/PanjivaUSImport2020To2024.txt'

# Check if the file exists
if (!file.exists(file_path)) {
  stop("File not found: ", file_path)
}

data <- fread(file_path)

# check the first few rows of the data
head(data)
