import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz
import config

API_KEY = config.API_KEY

def get_current_weather(city):
    """
    Fetch current weather for the specified city.
    Returns: temp (°C), humidity (%), precip (mm), condition (str)
    """
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    temp = data['current']['temp_c']
    humidity = data['current']['humidity']
    precip = data['current']['precip_mm']
    condition = data['current']['condition']['text']
    return temp, humidity, precip, condition


def get_hourly_history(city, hours=24):
    """
    Fetch last `hours` of hourly historical data for the specified city.
    Returns a DataFrame with datetime (Toronto local), Temp, Humidity, Precip
    """
    df = pd.DataFrame()
    now = datetime.utcnow()
    tz = pytz.timezone("America/Toronto")  # Toronto timezone

    for i in range(hours // 24 + 1):
        date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={city}&dt={date}"
        response = requests.get(url)
        if response.status_code != 200:
            continue
        data = response.json()
        for h in data['forecast']['forecastday'][0]['hour']:
            # Convert API time string to datetime
            dt = pd.to_datetime(h['time'])
            # Convert UTC to Toronto local time
            dt = dt.tz_localize('UTC').tz_convert(tz)
            df = pd.concat([df, pd.DataFrame([{
                'datetime': dt,
                'Temp': h['temp_c'],
                'Humidity': h['humidity'],
                'Precip': h['precip_mm']
            }])], ignore_index=True)

    df = df.sort_values('datetime').tail(hours)
    return df
