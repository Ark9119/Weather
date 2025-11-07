# services.py
import requests
from pprint import pprint

from .exceptions import WeatherException


class WeatherService:
    """Список полей для извлечения.
    Bce доступные поля:
    'time'
    'temp_c'
    'wind_kph'
    'precip_mm'
    'humidity'
    'cloud'
    'will_it_rain'
    'chance_of_rain'
    'chance_of_snow'
    Больше/меньше полей можно настроить на сайте weatherapi.com.
    """
    hourly_fields = ['temp_c', 'cloud', 'humidity', 'chance_of_rain']

    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url

    def fetch_data(self, city, days):
        """Запрос и получение джейсона с данными."""
        url = f'{self.api_url}?key={self.api_key}&q={city}&days={days}'
        response = requests.get(url)
        if response.status_code == 400:
            raise WeatherException(
                'Ошибка в написании города.', status_code=response.status_code
            )
        if response.status_code != 200:
            raise WeatherException(
                'Ошибка при получении данных API',
                status_code=response.status_code
            )
        return response.json()

    def get_data_for_day(self, data):
        """Получение списка значений за весь день."""
        days = data['forecast']['forecastday']
        results = []
        for day in days:
            date = day['date']
            hourly_data = day['hour']
            hourly_info = {}
            for field in self.hourly_fields:
                hourly_info[field] = self.every_hour_field(hourly_data, field)
            results.append({
                'found_country': data['location']['country'],
                'found_city': data['location']['name'],
                'date': date,
                **hourly_info
            })
        return results

    def get_data_for_hour(self, data, hour):
        """Получение значений в конкретный час."""
        days = data['forecast']['forecastday']
        results = []
        for day in days:
            date = day['date']
            hourly_data = day['hour']
            hourly_info = {}
            for field in self.hourly_fields:
                hourly_info[field] = self.every_hour_field(hourly_data, field)
            day_result = {
                'found_country': data['location']['country'],
                'found_city': data['location']['name'],
                'date': date
            }
            for field in self.hourly_fields:
                day_result[field] = hourly_info[field][hour]
            results.append(day_result)
        return results

    def every_hour_field(self, hourly_data, field_name):
        """Общий метод для извлечения любого поля из hourly_data."""
        for entry in hourly_data:
            if field_name not in entry:
                raise KeyError(
                    f'Поле "{field_name}" отсутствует в данных для часа.'
                )
        return [entry[field_name] for entry in hourly_data]
