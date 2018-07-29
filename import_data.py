# This module will import hourly elspot price data for 2013-2018 in EUR from
# https://www.nordpoolgroup.com/historical-market-data/ and clean the data for
# data anlaysis.



import pandas as pd
import glob

df_list = []
filenames = glob.glob("datasets/elspot-prices/elspot*.csv")

print(filenames)

## Read in and clean all files.

for filename in filenames:
    ## Read CSV-file
    elspot_df = pd.read_csv(filename, delimiter=";", header=2, encoding="utf-8")


    ## Change column names
    column_names = elspot_df.columns.values
    column_names[0] = "Date_temp" # will remove this after merging the columns
    column_names[1] = "Hours_temp" # will remove this after the columns
    column_names[10] = "NO1" # From Oslo
    column_names[11] = "NO2" # From Kr.sand
    column_names[12] = "NO5" # From Bergen
    column_names[14] = "NO3" # From Trondheim - same as Molde.
    column_names[15] = "NO4" # From Tromsø
    elspot_df.columns = column_names
    print(elspot_df.columns.values)


    ## Merge date and hours
    elspot_df["Hours_temp"] = elspot_df["Hours_temp"].apply(lambda x: x[0:2])
    elspot_df["Date"] = elspot_df["Date_temp"] + " " + elspot_df["Hours_temp"]


    ## Change Date-column to datetime

    elspot_df["Date"] = pd.to_datetime(elspot_df["Date"], format="%d-%m-%Y %H")
    elspot_df = elspot_df.set_index(["Date"])
    elspot_df = elspot_df.drop(["Date_temp", "Hours_temp", "Molde"], axis=1) # Molde is equal to Trondheim = NO3
    column_names = elspot_df.columns.values


    ## Convert decimal point from comma to point
    elspot_df = elspot_df.apply(lambda x: x.str.replace(",", "."))


    ## Cast numbers as float
    elspot_df = elspot_df.apply(lambda x: pd.to_numeric(x))

    df_list.append(elspot_df)



## Concatenate all dataframes

elspot_df_total = df_list.pop(0)

for df in df_list:
        elspot_df_total = pd.concat([elspot_df_total, df], sort=True)


# Dropping FRE column that only shows with values for certain years.
elspot_df_total = elspot_df_total.drop("FRE", axis=1)

# Adding data from the old bidding area ELE to the bidding area LV from 01-01-2013 to 02-06-2013,
# and dropping the ELE-column.

elspot_df_total["LV"].loc["2013-01-01":"2013-06-02"] = elspot_df_total["ELE"].loc["2013-01-01":"2013-06-02"]
elspot_df_total = elspot_df_total.drop("ELE", axis=1)
print(elspot_df_total.info())

elspot_df_total.to_csv("datasets/elspot-prices/total-elspot-prices_2013-2018.csv")
