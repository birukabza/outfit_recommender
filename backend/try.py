import requests
import os
from dotenv import load_dotenv
load_dotenv()
def get_weather_by_coords(latitude: float, longitude: float) -> dict:
    """
    Fetches current weather data from OpenWeatherMap using coordinates.
    
    Returns a dictionary like:
    {
        "description": "clear sky",
        "temperature": 28.53,
        "feels_like": 29.2,
        "weather_main": "Clear",
    }
    """
    OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
    if not OPENWEATHERMAP_API_KEY:
        raise ValueError("⚠️ OpenWeatherMap API key is not set in the environment.")

    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"lat={latitude}&lon={longitude}&units=metric&appid={OPENWEATHERMAP_API_KEY}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        weather = {
            "description": data["weather"][0]["description"],
            "weather_main": data["weather"][0]["main"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
        }

        return weather
    except requests.RequestException as e:
        print("❌ Failed to fetch weather data:", e)
        return {"error": "Unable to fetch weather data"}

print(get_weather_by_coords( 9.0079232,  38.74816))