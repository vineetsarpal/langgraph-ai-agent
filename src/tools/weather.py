import os
import requests

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

def get_weather(city: str, country_code: str = None) -> str:
    """
    Fetches the current weather for a given city (and optional country code).
    Returns a string summary of the weather.
    """
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    q = city if not country_code else f"{city},{country_code}"
    params = {
        "q": q,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return f"Error: {response.json().get('message', 'Failed to fetch weather')}"
    data = response.json()
    weather = data["weather"][0]["description"].capitalize()
    temp = data["main"]["temp"]
    city_name = data["name"]
    country = data["sys"]["country"]
    return f"The weather in {city_name}, {country} is {weather} with a temperature of {temp}°C."
