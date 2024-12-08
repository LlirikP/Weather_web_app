import requests

API_KEY = "5XtNvQ9ULF0zEKrstTCmxmgOZKq3VoGI"


def get_weather(latitude, longitude, location_key = None):
    """
    :param latitude: широта
    :param longitude: долгота
    :return: словарь, содержащий все погодные данные о следующем дне для заданных координат
    """
    location_url = f"http://dataservice.accuweather.com/locations/v1/cities/geoposition/search"
    location_params = {
        "apikey": API_KEY,
        "q": f"{latitude},{longitude}"
    }
    location_response = requests.get(location_url, params=location_params)
    location_data = location_response.json()
    location_key = location_data["Key"]
    weather_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}"
    weather_params = {"apikey": API_KEY, "details": "true", "metric": "true"}
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
        "rain probability": rain_probability
    }


def check_bad_weather(min_temperature, max_temperature, wind_speed, snow_probability, rain_probability):
    if min_temperature < 0 or max_temperature > 35:
        return "bad"
    if wind_speed > 50:
        return "bad"
    if rain_probability > 70:
        return "bad"
    if snow_probability > 70:
        return "bad"
    return "good"


def get_coordinates_from_city(city_name):
    """
    Получает координаты и ключ локации для города через AccuWeather API.
    :param city_name: Название города
    :return: Кортеж (latitude, longitude, location_key)
    """
    params = {
        "apikey": API_KEY,
        "q": city_name,
        "language": "en",
    }
    response = requests.get("http://dataservice.accuweather.com/locations/v1/cities/search", params=params)
    if response.status_code != 200:
        raise Exception(f"Ошибка запроса к AccuWeather API: {response.status_code}, {response.text}")
    data = response.json()
    if not data:
        raise ValueError(f"Город {city_name} не найден.")
    location = data[0]
    latitude = location["GeoPosition"]["Latitude"]
    longitude = location["GeoPosition"]["Longitude"]
    location_key = location["Key"]
    return latitude, longitude, location_key
