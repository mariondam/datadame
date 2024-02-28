import pandas as pd
import matplotlib.pyplot as plt
import datetime
import requests

from pvlib import pvsystem, modelchain, location, irradiance
from pvlib.solarposition import get_solarposition


# Example: use KNMI weather data to simulate Dutch PV panels

def get_hourly_weather_data_for_pvlib(stations, start_date, end_date, timezone = 'UTC'):
    '''
    Function to get hourly weather variables T (temperature) and
    Q (global radiation) from KNMI 
    
    Args: 
        stations   (str): NMI-stations separated by ':' 
        start_date (str): start date, format yyyymmdd
        end_date   (str): end date (included), format yyyymmdd
        timezone   (str, optional): timezone

    Returns:
        df: DataFrame with DateTime-index, columns T (temp), Q (global radiation) 
    '''

    url = 'https://www.daggegevens.knmi.nl/klimatologie/uurgegevens'

    data = {
        'start': start_date,
        'end': end_date,
        'vars': 'Q:P:T',
        'stns': stations,
        'fmt': 'json'
        }

    response = requests.post(url, data = data)    
    weather_df = pd.DataFrame(response.json())

    # correct units
    weather_df['T'] = weather_df['T'] / 10          # is in 0.1 degrees C, to degrees C
    weather_df['Q'] = weather_df['Q'] * (1 / 0.36)  # is in J/m2, to W / m2
    weather_df['P'] = weather_df['P'] * 10          # is in 0.1 hPa, to Pa
    
    # create date_time index, convert timezone
    weather_df['hour'] = weather_df['hour'] - 1     # is from 1-24, to 0-23
    weather_df['date_time'] = pd.to_datetime(weather_df['date']) +\
                              pd.to_timedelta(weather_df['hour'].astype(int), unit='h')
    weather_df.index = weather_df.date_time
    weather_df = weather_df.drop(['date', 'hour', 'date_time'], axis = 1)
    weather_df.index = weather_df.index.tz_convert(timezone)

    # shift date_time by 30 minutes, 'average time' during that hour
    weather_df.index = weather_df.index.shift(freq="30min")

    return weather_df


start_date = '20230101'
end_date = '20231231'

timezone = 'Europe/Amsterdam'

# De Bilt 
station = '260'
lat = 52.1092717
lon = 5.1809676

weather_df = get_hourly_weather_data_for_pvlib(station, start_date, end_date, timezone)

# Get solar position for date_times
solpos_df = get_solarposition(
    weather_df.index, latitude = lat,
    longitude = lon, altitude = 0,
    temperature = weather_df['T'])
solpos_df.index = weather_df.index

# Use method 'Erbs' to go from GHI to DNI and DHI. There are other methods available.
irradiance_df = irradiance.erbs(weather_df['Q'], solpos_df['zenith'], weather_df.index)
irradiance_df['ghi'] = weather_df['Q']


# Define solar panels
orientation = 180  # Azimuth, 90 is East, 180 is South, 270 is West
tilt = 30         # 0 is flat on the ground, 90 is vertical
Wp_panels = 1000  # total Wp of the solar panels
W_inverter = 1000 # power (W) of the inverter


array = pvsystem.Array(pvsystem.FixedMount(tilt, orientation),
                       module_parameters = dict(pdc0 = Wp_panels, gamma_pdc = -0.004),
                       temperature_model_parameters = {'a': -3.56, 'b': -.0750, 'deltaT': 3})

loc = location.Location(lat, lon, tz = timezone)
system = pvsystem.PVSystem(arrays = [array], inverter_parameters = dict(pdc0 = W_inverter))
mc = modelchain.ModelChain(system, loc, aoi_model = 'physical',
                           spectral_model = 'no_loss')


# Example 1 day
date = datetime.date(2023, 6, 10)
mc.run_model(irradiance_df[irradiance_df.index.date == date])
mc.results.ac.plot()
plt.title(f'pvlib: opwek gesimuleerde zonnepanelen (1 kWp) op {date}', size  = 12)
plt.ylabel('Opwek (W)', size = 12)
plt.xlabel('Tijdstip', size = 12)
plt.show()

# Compute total production in kWh
pvlib_df = mc.results.ac.reset_index()
pvlib_df['kWh'] = pvlib_df['p_mp'] / 1000  
production_kWh = round(pvlib_df['kWh'].sum(),2)
print(f'On {date} the solar panels produced {production_kWh} kWh')


# Example whole year
mc.run_model(irradiance_df)

# Compute total production in kWh
pvlib_df = mc.results.ac.reset_index()
pvlib_df['kWh'] = pvlib_df['p_mp'] / 1000  
production_kWh = round(pvlib_df['kWh'].sum(),2)
print(f'In 2023, the solar panels produced {production_kWh} kWh')