# Data sources


## Get EPEX day ahead prices
*entsoe_epex_day_ahead.py*: example to get the Dutch dynamic electricity prices with Python (the prices of Dutch dynamic contracts are based on the Dutch EPEX day ahead prices). 

- [Documentation entsoe-py](https://github.com/EnergieID/entsoe-py) 
- Data source: ENTSO-E ([API documentation](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html), or [view data source online](https://transparency.entsoe.eu/transmission-domain/r2/dayAheadPrices/show?name=&defaultValue=true&viewType=GRAPH&areaType=BZN&atch=false&dateTime.dateTime=04.02.2024+00:00|CET|DAY&biddingZone.values=CTY|10YNL----------L!BZN|10YNL----------L&resolution.values=PT15M&resolution.values=PT30M&resolution.values=PT60M&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2))). API token needed. 

## Get hourly weather data KNMI
- [Documentation KNMI](https://www.knmi.nl/kennis-en-datacentrum/achtergrond/data-ophalen-vanuit-een-script#)
- [Selection page](https://www.daggegevens.knmi.nl/klimatologie/uurgegevens) of variables and KNMI stations


## pvlib: simulate solar panels
- [Documentation pvlib](https://pvlib-python.readthedocs.io/en/stable/)
- Example solar panels in the Netherlands, using KNMI weather data. See [this post](https://www.datadame.nl/data/zonnepanelen-simuleren-met-python/) for explanation (in Dutch).

## Beautiful Soup: getting data from a website
- [Documentation Beautiful Soup](https://pypi.org/project/beautifulsoup4/)