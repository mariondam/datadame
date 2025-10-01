'''
Functions to get data on Dutch energy markets.
All functions expect a start_date and end_date as string in the format 'YYYYMMDD'

Functions:
get_afrr_df(start_date, end_date, entsoe_client) : 
    quarterly aFRR dispatch, from entsoe, using entsoe-py client
get_dayahead_df(start_date, end_date, entsoe_client) : 
    hourly EPEX day-ahead prices from entsoe, using entsoe-py client
'''

import pandas as pd
import requests
from datetime import datetime

    
def get_afrr_df(start_date, end_date, entsoe_client):
    # Use ENTSOE-py to fetch aFRR data (both amount and prices)
    start = pd.Timestamp(start_date, tz='Europe/Amsterdam')
    end = pd.Timestamp(end_date, tz='Europe/Amsterdam')
    country_code = 'NL'  

    business_type = 'A96' # aFRR

    afrr_df = entsoe_client.query_activated_balancing_energy(country_code, start = start, end = end, business_type = business_type)
    afrr_df.columns = afrr_df.columns.droplevel()

    # Give column names suffix _15m
    cols = list(afrr_df.columns)
    cols = [str.lower(c) + '_MW' for c in cols]
    afrr_df.columns = cols

    # Get aFRR prices
    afrr_price_df = entsoe_client.query_activated_balancing_energy_prices(country_code, start = start, end = end, business_type = business_type)
    afrr_price_df = afrr_price_df.pivot(columns = 'Direction', values = 'Price')
    afrr_price_df.rename(columns = {'Down': 'down_price_euro_per_MWh', 'Up': 'up_price_euro_per_MWh'}, inplace = True)

    # Merge activated balancing energy with prices
    afrr_df = afrr_df.merge(afrr_price_df, left_index = True, right_index = True)

    return afrr_df


def get_dayahead_df(start_date, end_date, entsoe_client):
    start = pd.Timestamp(start_date, tz='Europe/Amsterdam')
    end = pd.Timestamp(end_date, tz='Europe/Amsterdam')
    country_code = 'NL'  

    dayahead_s = entsoe_client.query_day_ahead_prices(country_code, start = start, end = end)
    dayahead_df = pd.Series.to_frame(dayahead_s).reset_index().rename(columns = {'index': 'date_time', 0: 'price_euro_per_MWh'})

    return dayahead_df

