import yandex_weather_api
import requests
from bs4 import BeautifulSoup


# Класс для нахождения координат города(широты и долготы)
class YandexGeocoder:

    def __init__(self, geocoder_key: str):
        self.geocoder_key = geocoder_key

    @staticmethod
    def from_api_token_path(geocoder_token_filepath: str):
        with open(geocoder_token_filepath) as f:
            geocoder_api_key = f.read()
        return YandexGeocoder(geocoder_api_key)

    # Создание ссылки для запроса координат города
    def create_url(self, city_name: str):
        url_base = 'https://geocode-maps.yandex.ru/1.x/?format=json'
        url_attributes = f'&apikey={self.geocoder_key}&geocode={city_name}'
        return url_base + url_attributes

    # Получение координат при помощи обработки html
    @staticmethod
    def get_coordinates(response):
        coords = response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        return coords.split()

    def __call__(self, city_name: str):
        url = self.create_url(city_name)
        response = requests.get(url)
        return self.get_coordinates(response)


# Класс, работающий с сервисом ЯндексПогода. Используется для нахождения погоды по координатам
class YandexWeatherForecast:

    def __init__(self, weather_key: str):
        self.weather_key = weather_key

    @staticmethod
    def from_api_token_path(weather_token_filepath: str):
        with open(weather_token_filepath) as f:
            weather_api_key = f.read()
        return YandexWeatherForecast(weather_api_key)

    # Получение температуры в данный момент по прогнозу из API
    @staticmethod
    def current_temperature(forecast) -> int:
        return int(forecast['fact']['temp'])

    # Получение прогноза по координатам при помощи API
    def get_forecast(self, coordinates):
        return yandex_weather_api.get(requests.Session(), self.weather_key, lat=coordinates[0], lon=coordinates[1])

    def __call__(self, coordinates):
        forecast = self.get_forecast(coordinates)
        cur_t = self.current_temperature(forecast)
        return {
            'cur_t': cur_t,
        }


# Класс, работающий с сайтом weather.com. Используется для нахождения погоды по координатам
class WeatherComForecast:

    # Создание ссылки по координатам
    @staticmethod
    def create_url(coordinates, language: str):
        return f'https://weather.com/{language}/weather/today/l/{coordinates[0]},{coordinates[1]}?unit=m'

    # Получение температуры в данный момент по прогнозу
    @staticmethod
    def current_temperature(soup):
        return soup.find('div', 'CurrentConditions--primary--39Y3f').find('span').contents[0][:-1]

    def __call__(self, coordinates, language):
        url = self.create_url(coordinates, language)
        response = requests.get(url)
        soup = BeautifulSoup(response.content)
        cur_t = self.current_temperature(soup)
        return {
            'cur_t': cur_t,
        }


# Класс, работающий с сайтом accuweather. По названию города находит его id. По id показывает погоду в городе
class AccuWeatherForecast:

    def __init__(self, api_key: str):
        self.api_key = api_key

    @staticmethod
    def from_api_token_path(token_filepath: str):
        with open(token_filepath) as f:
            api_key = f.read()
        return AccuWeatherForecast(api_key)

    # Создание ссылки для получения id искомого города
    def create_city_key_url(self, language: str, city_name: str):
        url_base = 'https://dataservice.accuweather.com/locations/v1/cities/autocomplete'
        url_attributes = f'?apikey={self.api_key}&q={city_name}&language={language}'
        return url_base + url_attributes

    # Получение id искомого города
    def get_city_key(self, language, city_name):
        url = self.create_city_key_url(language, city_name)
        response = requests.get(url)
        return response.json()[0]['Key']

    # Создание ссылки для нахождения погоды в искомом городе
    def create_weather_url(self, city_key, language):
        url_base = 'https://dataservice.accuweather.com/forecasts/v1/daily/5day/'
        url_attributes = f'{city_key}?apikey={self.api_key}&language={language}&details=false&metric=true'
        return url_base + url_attributes

    # Получение минимальной погоды в данный день
    @staticmethod
    def minimum_temperature(response) -> int:
        return int(response.json()['DailyForecasts'][0]['Temperature']['Minimum']['Value'])

    # Получение максимальной погоды в данный день
    @staticmethod
    def maximum_temperature(response) -> int:
        return int(response.json()['DailyForecasts'][0]['Temperature']['Maximum']['Value'])

    def __call__(self, language: str, city_name: str):
        city_key = self.get_city_key(language, city_name)
        url_weather = self.create_weather_url(city_key, language)
        response = requests.get(url_weather)
        min_t = self.minimum_temperature(response)
        max_t = self.maximum_temperature(response)
        return {
            'min_t': min_t,
            'max_t': max_t,
        }
