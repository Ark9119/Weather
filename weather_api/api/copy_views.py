import os
import requests
import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from pprint import pprint


load_dotenv()

API_KEY = os.getenv('WEATHEAPI_KEY')
WEATHER_URL = os.getenv('WEATHER_URL')


@csrf_exempt  # если планируете POST-запросы из внешних источников
def weather_forecast(request):
    request_data = json.loads(request.body.decode('utf-8'))
    city = request_data.get('city')
    days = request_data.get('days')
    url = f'{WEATHER_URL}?key={API_KEY}&q={city}&days={days}'
    response = requests.get(url)
    if response.status_code != 200:
        return JsonResponse(
            {'error': 'Cannot get data from weather API'}, status=500
        )
    response_data = response.json()
    return give_json(response_data, city)


def give_json(data, city):
    days = data['forecast']['forecastday']
    results = []
    for day in days:
        date = day['date']
        hourly_data = day['hour']
        # Получить температуру для каждого часа
        every_hour_temp = calculation_temp(hourly_data)
        # Можно добавлять другие параметры по аналогии
        results.append({
            'date': date,
            'temperature_c': every_hour_temp,
            # добавьте другие параметры
        })
    return JsonResponse({
        'city': city,
        'every_hour': results,
    })


def calculation_temp(data):
    return [entry['temp_c'] for entry in data]
