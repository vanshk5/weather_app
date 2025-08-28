# fetch_weather.py
import requests

# Your WeatherAPI.com key
API_KEY = "09d9e6f7a88e420297d11300252808"
CITY = "Toronto,CA"

def get_current_weather():
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={CITY}"
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to fetch weather data:", response.status_code)
        return None

    data = response.json()
    current = data['current']
    
    temp = current['temp_c']
    humidity = current['humidity']
    condition = current['condition']['text']  # e.g., Partly cloudy, Rain
    precip = current['precip_mm']  # Precipitation in mm

    return temp, humidity, precip, condition

if __name__ == "__main__":
    weather = get_current_weather()
    if weather:
        temp, humidity, precip, condition = weather
        print(f"Temp: {temp}°C, Humidity: {humidity}%, Precip: {precip}mm, Condition: {condition}")
