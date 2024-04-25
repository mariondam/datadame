'''
Functions to get data on Dutch energy markets.
All functions expect a start_date and end_date as string in the format 'YYYYMMDD'

Functions:
get_afrr_df(start_date, end_date, entsoe_client) : 
    quarterly aFRR dispatch, from entsoe, using entsoe-py client
get_dayahead_df(start_date, end_date, entsoe_client) : 
    hourly EPEX day-ahead prices from entsoe, using entsoe-py client
get_minute_df(start_date, end_date) : 
    imbalance data per minute from Tennet
get_vp_df(start_date, end_date) : 
    quarterly VerrekenPrijzen from Tennet
'''

import pandas as pd
import requests
from datetime import datetime

def _date_tennet_format(input_date):
    date_object = datetime.strptime(input_date, '%Y%m%d')
    formatted_date = date_object.strftime('%d-%m-%Y')
    return formatted_date
    
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


def get_minute_df(start_date, end_date):
    # Fetch data from TenneT
    url = f"http://www.tennet.org/bedrijfsvoering/ExporteerData.aspx"

    datatype = 'balansdeltaIGCC'

    params = {
            'exporttype': datatype,
            'format': 'xml',
            'datefrom': _date_tennet_format(start_date),
            'dateto': _date_tennet_format(end_date),
            'submit': '1'
        }

    response = requests.get(url, params = params)
    minute_df = pd.read_xml(response.content, xpath='//Record')

    # give column names suffix _1m for minute data
    cols = list(minute_df.columns)
    cols = [str.lower(c) + '_1m' for c in cols]
    minute_df.columns = cols

    # make datetime index
    minute_df['datetime'] = pd.to_datetime(minute_df['date_1m'] + ' ' + minute_df['time_1m'], format = '%d-%m-%Y %H:%M')
    minute_df = minute_df.set_index('datetime').tz_localize('Europe/Amsterdam')

    return minute_df


def get_vp_df(start_date, end_date):
    datatype = 'verrekenprijzen'
    params = {
            'exporttype': datatype,
            'format': 'xml',
            'datefrom': _date_tennet_format(start_date),
            'dateto': _date_tennet_format(end_date),
            'submit': '1'
        }

    url = f"http://www.tennet.org/bedrijfsvoering/ExporteerData.aspx"
    response = requests.get(url, params = params)
    vp_df = pd.read_xml(response.content, xpath='//Record')

    # give column names suffix _vp for VerrekenPrijzen (imbalance settlement)
    cols = list(vp_df.columns)
    cols = [str.lower(c) for c in cols]
    vp_df.columns = cols

    # create datetime index
    vp_df['datetime'] = vp_df['date'] + ' ' + vp_df['period_from']
    vp_df['datetime'] = pd.to_datetime(vp_df['datetime'], format = '%d-%m-%Y %H:%M')
    vp_df = vp_df.set_index('datetime').tz_localize('Europe/Amsterdam', ambiguous= 'infer')
    
    return vp_df