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
    # print(f'request_data {request_data}')
    city = request_data.get('city')
    # print(f'city {city}')
    days = request_data.get('days')
    # print(f'days {days}')
    url = f"{WEATHER_URL}?key={API_KEY}&q={city}&days={days}"
    response = requests.get(url)
    if response.status_code != 200:
        return JsonResponse(
            {'error': 'Cannot get data from weather API'}, status=500
        )
    # response_data = response.json()
    # return response_data



# def take_data_from_hour(response_data):
#     data_from_hour = response_data['forecast']['forecastday'][0]['hour']
#     return data_from_hour


# def calculation_temp(data):
#     every_hour_temp = [entry['temp_c'] for entry in data]
#     pprint(f'every_hour_temp {every_hour_temp}')
#     return (every_hour_temp)


# @csrf_exempt
# def give_json_response(*args):
#     day_temp = calculation_temp(take_data_from_hour(weather_forecast()))
#     result = {
#         'test_fild': day_temp
#     }
#     return JsonResponse(result)
  
    response_data = response.json()
    # pprint(response_data)
    # Пример обработки - вернем температуру и описание на сегодня
    current_temp = response_data['current']['temp_c']
    condition = response_data['current']['condition']['text']
    hours = response_data['forecast']['forecastday']
    for i in hours:
        # print(f'many hour {hour}')
        hour = i['hour']
    # hour = response_data['forecast']['forecastday'][0]['hour']
        pprint(f'hour {hour}')
        # Влажность
        every_hour_humidity = [entry['humidity'] for entry in hour]
        pprint(f'every_hour_humidity {every_hour_humidity}')
        # Разбивка по часам с 00 до 23
        every_hour_time = [
            datetime.strptime(t, '%Y-%m-%d %H:%M').strftime('%H') for t in [entry['time'] for entry in hour]
        ]
        pprint(f'every_hour_time {every_hour_time}')
        # Температура
        every_hour_temp = [entry['temp_c'] for entry in hour]
        pprint(f'every_hour_temp {every_hour_temp}')
        # Шанс дождя
        every_hour_chance_of_rain = [entry['chance_of_rain'] for entry in hour]
        pprint(f'every_hour_chance_of_rain {every_hour_chance_of_rain}')
        # Будет ли дождь True(1)/False(0)
        every_hour_will_it_rain = [entry['will_it_rain'] for entry in hour]
        pprint(f'every_hour_will_it_rain {every_hour_will_it_rain}')
        # Облачность
        every_hour_cloud = [entry['cloud'] for entry in hour]
        pprint(f'every_hour_cloud {every_hour_cloud}')
        # Округлённый час для настоящего момента
        now = datetime.now()
        print(f'Сечас {now}')
        delta = timedelta(minutes=30)
        rounded_time = now + delta
        # Округляем до часа
        rounded_hour = rounded_time.replace(minute=0, second=0, microsecond=0).hour
        print(f'Округленный час: {rounded_hour}')
        """
        Чтобы получить значение с данного часа нужно получать
        элемент из любого списка подставляя индексом нынешний час.
        Потому что в списке часов индексы у каждого элемента равняются этому часу.
        [0] = 00, [1] = 01 & ets.
        """
        random_index = 5
        now_t = every_hour_temp[rounded_hour:]
        pprint(f'с {every_hour_time[rounded_hour]} будет {now_t}')
        t_for_end_day = sum(now_t)/len(now_t)
        print(f'температура до конца дня {t_for_end_day}')

        result = {
            'city': city,
            'temperature_c': current_temp,
            'condition': condition,
            'test_fild': now_t
        }
    return JsonResponse(result)
