import pandas as pd
from entsoe import EntsoePandasClient

entsoe_token = 'TOKEN_HERE'

# Fetch historic EPEX day-ahead prices from ENTSO-E
start = pd.Timestamp('20230101', tz='Europe/Amsterdam')
end = pd.Timestamp('20240101', tz='Europe/Amsterdam')
country_code = 'NL'  

client = EntsoePandasClient(api_key=entsoe_token)
series_day_ahead_prices = client.query_day_ahead_prices(country_code, start = start, end = end)

# To DataFrame
df_day_ahead_prices = pd.Series.to_frame(series_day_ahead_prices).reset_index().rename(columns = {'index': 'date_time', 0: 'price_euro_per_MWh'})
df_day_ahead_prices['price_euro_per_kWh'] = df_day_ahead_prices['price_euro_per_MWh'] / 1000