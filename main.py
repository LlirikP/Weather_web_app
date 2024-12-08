import requests
from flask import Flask, request, render_template

API_KEY = "1uEOrBKxMZkgT7AbHJvWRXGhIvAhLOr1"
BASE_URL = "http://dataservice.accuweather.com/forecasts/v1/daily/1day"

def get_weather(latitude, longitude):
    """
    :param latitude: широта
    :param longitude: долгота
    :return: все погодные данные о следующем дне для заданных координат
    """
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

def get_weather_data(weather_data):
    """
    Функция возвращает погодные условия в таком формате:
        Минимальная температура
        Максимальная температура
        Скорость ветра
        Вероятность снега
        Вероятность дождя
    """
    daily_forecast = weather_data["DailyForecasts"][0]
    min_temperature = daily_forecast["Temperature"]["Minimum"]["Value"]
    max_temperature = daily_forecast["Temperature"]["Maximum"]["Value"]
    snow_probability = daily_forecast["Day"]["RainProbability"]
    wind_speed = daily_forecast["Day"]["Wind"]["Speed"]["Value"]
    rain_probability = daily_forecast["Day"]["RainProbability"]
    return {
        "min temperature": min_temperature,
        "max temperature": max_temperature,
        "wind speed": wind_speed,
        "snow probability": snow_probability,
        "rain_probability": rain_probability
    }
