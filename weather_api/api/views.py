# views.py
import os
from datetime import datetime, timedelta
import random

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, exceptions
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dotenv import load_dotenv

from .models import UserCity
from .services import WeatherService
from .serializers import UserCitySerializer


load_dotenv()

API_KEY = os.getenv('WEATHEAPI_KEY')
WEATHER_URL = os.getenv('WEATHER_URL')


# @method_decorator(csrf_exempt, name='dispatch')
class UserCityViewSet(viewsets.ModelViewSet):
    queryset = UserCity.objects.all()
    serializer_class = UserCitySerializer

    def get_object(self):
        # Получаем число из URL
        user_id = self.kwargs.get('pk')
        try:
            # Ищем объект по полю user
            obj = UserCity.objects.get(user=user_id)
        except UserCity.DoesNotExist:
            raise exceptions.NotFound(
                'UserCity with specified user not found.'
            )
        return obj

    def create(self, request, *args, **kwargs):
        print("Create method called")
        user_id = request.data.get('user')
        # city = request.data.get('city')

        # Если user_id не передан, возвращаем ошибку
        if not user_id:
            return Response(
                {'error': 'user is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            instance = UserCity.objects.get(user=user_id)
            # Обновляем существующую запись
            serializer = self.get_serializer(
                instance, data=request.data, partial=True
            )
        except UserCity.DoesNotExist:
            # Создаем новую запись
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        """пут запрос к /sity/<id>, передаём user и sity - меняем sity"""
        user = request.data.get('user')
        obj = UserCity.objects.get(user=user)
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class Weather(viewsets.ViewSet):
    """Выдаёт погоду на 1 - 3 дня."""
    def create(self, request):
        # Получаем параметры из тела POST-запроса
        """
        city = request.data.get('city')
        получаем из тела запроса город
        """
        user = request.data.get('user')
        # получаем город через user пользователя в базе
        # если нужно найти по ID в базе, то (id=user)
        take_response_city = request.data.get('city')
        if take_response_city is None:
            city = UserCity.objects.get(user=user).city
        else:
            city = take_response_city
        # print(city)  # TODO СДЕЛАТЬ УСЛОВИЕ ЕСЛИ ПЕРЕДАН В ТЕЛЕ, ЕСЛИ НЕ ПЕРЕДАН В ТЕЛЕ, ТО ИЩЕМ В БАЗЕ
        days = request.data.get('days')

        # Проверка необходимых параметров
        if not city or not days:
            return Response(
                {'error': 'Missing parameters: city and days are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Создаем сервисный объект
        weather_service = WeatherService(API_KEY, WEATHER_URL)
        try:
            data = weather_service.fetch_data(city, days)
            forecast = weather_service.get_data_for_day(data)
        except Exception as e:
            # Обработка ошибок при вызове API или парсинге
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'city': city,
            'forecast': forecast,
        })

    @action(detail=False, methods=['post'])
    def today(self, request):
        """Выдаёт погоду на сегодня."""
        # city = request.data.get('city')
        user = request.data.get('user')
        print(f'user {user}')
        take_response_city = request.data.get('city')
        print(f'take_response_city {take_response_city}')
        if take_response_city is None:
            city = UserCity.objects.get(user=user).city
            
        else:
            city = take_response_city
        print(f'city {city}')
        days = 1
        if not city:
            return Response(
                {'error': 'Missing parameter: city'},
                status=status.HTTP_400_BAD_REQUEST
            )

        weather_service = WeatherService(API_KEY, WEATHER_URL)
        try:
            data = weather_service.fetch_data(city, days=days)
            forecast = weather_service.get_data_for_day(data)
            today_forecast = forecast[days - 1] if forecast else {}  # for what? #TODO
            # print(today_forecast)
        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'city': city,
            'forecast': today_forecast
        })

    @action(detail=False, methods=['post'])
    def now(self, request):
        """Эндпоинт для получения данных за текущий,
        округленный к ближайшему, час.
        """
        # city = request.data.get('city')
        user = request.data.get('user')
        take_response_city = request.data.get('city')
        if take_response_city is None:
            city = UserCity.objects.get(user=user).city
        else:
            city = take_response_city
        days = 1
        if not city:
            return Response(
                {'error': 'Missing parameter: city'},
                status=status.HTTP_400_BAD_REQUEST
            )

        weather_service = WeatherService(API_KEY, WEATHER_URL)

        try:
            # Округление времени
            now = datetime.now()
            rounded_time = now + timedelta(minutes=30)
            rounded_hour = rounded_time.replace(
                minute=0, second=0, microsecond=0
            ).hour
            data = weather_service.fetch_data(city, days=days)
            this_time_forecast = weather_service.get_data_for_hour(
                data, hour=rounded_hour
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'city': city,
            'forecast': this_time_forecast
        })
