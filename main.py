import requests

API_KEY = "1bEE7WceTPRNRMMA97cD4kuYXAImgFaB"


def get_weather(latitude, longitude, location_key=None, days_count=1):
    """
    :param latitude: широта
    :param longitude: долгота
    :return: словарь, содержащий все погодные данные о следующем дне для заданных координат
    """
    try:
        location_url = f"http://dataservice.accuweather.com/locations/v1/cities/geoposition/search"
        location_params = {
            "apikey": API_KEY,
            "q": f"{latitude},{longitude}"
        }
        location_response = requests.get(location_url, params=location_params)
        location_data = location_response.json()
        location_key = location_data["Key"]
        if days_count >= 1:
            weather_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/{days_count}day/{location_key}"
        else:
            weather_url = f"http://dataservice.accuweather.com/forecasts/v1/hourly/1hour/{location_key}"
        weather_params = {"apikey": API_KEY, "details": "true", "metric": "true"}
        weather_response = requests.get(weather_url, params=weather_params)
        weather_data = weather_response.json()
        return weather_data
    except requests.exceptions.RequestException as e:
        return "Ошибка подключения к серверу."


def get_weather_data(weather_data, i=0):
    """
    Функция возвращает погодные условия в таком формате:
        Минимальная температура
        Максимальная температура
        Скорость ветра
        Вероятность снега
        Вероятность дождя
    """
    try:
        if isinstance(weather_data, list):
            hourly_data = weather_data[i]
            temperature = hourly_data.get("Temperature", {}).get("Value", None)
            real_feel_temperature = hourly_data.get("RealFeelTemperature", {}).get("Value", None)
            snow_probability = hourly_data.get("SnowProbability", 0)
            wind_speed = hourly_data.get("Wind", {}).get("Speed", {}).get("Value", None)
            rain_probability = hourly_data.get("RainProbability", 0)
            return {
                "temperature": temperature,
                "real feel temperature": real_feel_temperature,
                "wind speed": wind_speed,
                "snow probability": snow_probability,
                "rain probability": rain_probability
            }
        elif "DailyForecasts" in weather_data:
            daily_forecast = weather_data["DailyForecasts"][i]
            min_temperature = daily_forecast.get("Temperature", {}).get("Minimum", {}).get("Value", None)
            max_temperature = daily_forecast.get("Temperature", {}).get("Maximum", {}).get("Value", None)
            snow_probability = daily_forecast.get("Day", {}).get("SnowProbability", 0)
            wind_speed = daily_forecast.get("Day", {}).get("Wind", {}).get("Speed", {}).get("Value", None)
            rain_probability = daily_forecast.get("Day", {}).get("RainProbability", 0)
            return {
                "min temperature": min_temperature,
                "max temperature": max_temperature,
                "wind speed": wind_speed,
                "snow probability": snow_probability,
                "rain probability": rain_probability
            }
        else:
            raise ValueError("Неподдерживаемый формат weather_data")
    except KeyError as e:
        return f"Ошибка получения данных о погоде"


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
    try:
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
    except requests.exceptions.RequestException:
        return "Ошибка подключения к серверу."
