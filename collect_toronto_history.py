# collect_toronto_history.py
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIG ---
API_KEY = "09d9e6f7a88e420297d11300252808"
CITY = "Toronto,CA"
START_DATE = "2025-07-27"  # first day of historical data
END_DATE = "2025-08-27"    # last day of historical data
OUTPUT_CSV = "src/toronto_weather_history.csv"

# --- HELPER FUNCTION TO LOOP OVER DATES ---
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

# --- COLLECT DATA ---
all_rows = []
start_dt = datetime.strptime(START_DATE, "%Y-%m-%d")
end_dt = datetime.strptime(END_DATE, "%Y-%m-%d")

for single_date in daterange(start_dt, end_dt):
    date_str = single_date.strftime("%Y-%m-%d")
    url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={CITY}&dt={date_str}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed for {date_str}: {response.status_code}")
        continue

    data = response.json()
    hours = data['forecast']['forecastday'][0]['hour']

    for h in hours:
        row = {
            'datetime': h['time'],
            'Temp': h['temp_c'],
            'Humidity': h['humidity'],
            'Precip': h['precip_mm'],
            'Weather': h['condition']['text']
        }
        all_rows.append(row)

# --- CONVERT TO DATAFRAME ---
df = pd.DataFrame(all_rows)
df['datetime'] = pd.to_datetime(df['datetime'])
df['date'] = df['datetime'].dt.date

# --- CREATE LABEL: RainTomorrowMorning ---
labels = []
for i, row in df.iterrows():
    next_day = row['date'] + timedelta(days=1)
    # morning hours 6-9 AM next day
    next_morning = df[(df['date'] == next_day) & (df['datetime'].dt.hour.isin([6,7,8,9]))]
    labels.append(1 if next_morning['Precip'].sum() > 0 else 0)

df['RainTomorrowMorning'] = labels

# --- SAVE CSV ---
df.to_csv(OUTPUT_CSV, index=False)
print(f"Historical dataset saved to {OUTPUT_CSV}")
