import requests
from flask import Flask, request, render_template

API_KEY = "1uEOrBKxMZkgT7AbHJvWRXGhIvAhLOr1"
BASE_URL = "http://dataservice.accuweather.com/forecasts/v1/daily/1day"

def get_weather(latitude, longitude):
    location_url = f"http://dataservice.accuweather.com/locations/v1/cities/geoposition/search"
    location_params = {
        "apikey": API_KEY,
        "q": f"{latitude},{longitude}"
    }
    location_response = requests.get(location_url, params=location_params)
    location_data = location_response.json()
    location_key = location_data["Key"]
    weather_url = f"{BASE_URL}/{location_key}"
    weather_params = {"apikey": API_KEY, "metric": "true"}
    weather_response = requests.get(weather_url, params=weather_params)
    weather_data = weather_response.json()
    return weather_data

