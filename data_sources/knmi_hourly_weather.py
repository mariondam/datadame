import pandas as pd
import requests

# Example: create DataFrame with hourly KNMI weather data
base_url = 'https://www.daggegevens.knmi.nl/klimatologie/'

start_date = f'20230101'
end_date = f'20231231'

# Station 260: De Bilt
# Vars: Q is radiation (J/m2 in that hour), T is average temperature
url = base_url + 'uurgegevens'
data = {
    'start': start_date,
    'end': end_date,
    'vars': 'Q:T',
    'stns': '260',
    'fmt': 'json'
    }

response = requests.post(url, data = data)    
weather_df = pd.DataFrame(response.json())

# correct units
weather_df['T'] = weather_df['T'] / 10  # is in 0.1 degrees C, to degrees C
weather_df['Q'] = weather_df['Q'] * (1 / 0.36) # is in J/m2, to W / m2

# create date_time index, convert to Dutch timezone
weather_df['date_time'] = pd.to_datetime(weather_df['date']) + pd.to_timedelta(weather_df['hour'].astype(int), unit='h')
weather_df.index = weather_df.date_time
weather_df = weather_df.drop(['date', 'hour', 'date_time'], axis = 1)
weather_df.index = weather_df.index.tz_convert('Europe/Amsterdam')

# shift date_time by 30 minutes, 'average time' during that hour
weather_df.index = weather_df.index.shift(freq="30min")