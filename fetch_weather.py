import requests
import pandas as pd
from datetime import datetime, timedelta
import config

API_KEY = config.API_KEY
CITY = "Toronto,CA"

def get_hourly_history(hours=24):
    """
    Fetch the last `hours` of hourly weather data from WeatherAPI.
    Returns a DataFrame with columns: datetime, Temp, Humidity, Precip
    """
    df = pd.DataFrame()
    now = datetime.utcnow()
    
    # Loop over required past dates (WeatherAPI returns data by date)
    for i in range(hours//24 + 1):
        date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={CITY}&dt={date}"
        response = requests.get(url)
        if response.status_code != 200:
            continue
        data = response.json()
        for h in data['forecast']['forecastday'][0]['hour']:
            df = pd.concat([df, pd.DataFrame([{
                'datetime': pd.to_datetime(h['time']),
                'Temp': h['temp_c'],
                'Humidity': h['humidity'],
                'Precip': h['precip_mm']
            }])], ignore_index=True)
    
    # Keep only the last `hours`
    df = df.sort_values('datetime').tail(hours)
    return df
