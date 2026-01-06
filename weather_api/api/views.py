import os
from datetime import datetime, timedelta

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from dotenv import load_dotenv
from drf_yasg.utils import swagger_auto_schema

from .auth import get_city_from_auth_service
from .exceptions import WeatherException
from .services import WeatherService
from .serializers import (
    WeatherRequestSerializer,
    WeatherResponseSerializer
)

load_dotenv()

API_KEY = os.getenv('WEATHEAPI_KEY')
WEATHER_URL = os.getenv('WEATHER_URL')


class Weather(viewsets.ViewSet):

    def _get_weather_data(self, validated_data):
        """
        Общий метод для получения данных о погоде.
        Теперь получает город из микросервиса weather_auth.
        """
        user = validated_data.get('user')
        city = validated_data.get('city')
        # Если city не указан, получаем из weather_auth по username
        if city is None:
            if not user:
                # Если user не указан, вызываем исключение
                raise WeatherException(
                    'Необходимо указать либо user, либо city.',
                    status_code=400
                )
            # Получаем город из weather_auth по username
            city = get_city_from_auth_service(user)
            if city is None:
                raise WeatherException(
                    f'Город не найден для пользователя {user}. '
                    'Пожалуйста, укажите город '
                    'или зарегистрируйтесь в системе.',
                    status_code=404
                )
        days = validated_data['days']
        weather_service = WeatherService(API_KEY, WEATHER_URL)
        data = weather_service.fetch_data(city, days=days)
        return data, city

    def _process_weather_request(
        self, request, forecast_callback, *callback_args
    ):
        """
        Базовый метод для обработки weather запросов с обработкой исключений.
        """
        serializer = WeatherRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            data, city = self._get_weather_data(serializer.validated_data)
            forecast = forecast_callback(data, *callback_args)
            response_data = {
                'city': city,
                'forecast': forecast,
            }
            response_serializer = WeatherResponseSerializer(data=response_data)
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data)
        except WeatherException as e:
            return Response(
                {'error': str(e)},
                status=e.status_code
            )
        except Exception as e:
            return Response(
                {'error': f'Weather service error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        request_body=WeatherRequestSerializer,
        responses={200: WeatherResponseSerializer}
    )
    @action(detail=False, methods=['post'])
    def weather_to_days(self, request):
        """Выдаёт погоду на на 1 - 3 дня."""
        return self._process_weather_request(
            request,
            WeatherService(API_KEY, WEATHER_URL).get_data_for_day
        )

    @swagger_auto_schema(
        request_body=WeatherRequestSerializer,
        responses={200: WeatherResponseSerializer}
    )
    @action(detail=False, methods=['post'])
    def today(self, request):
        """Выдаёт погоду на сегодня."""
        return self._process_weather_request(
            request,
            WeatherService(API_KEY, WEATHER_URL).get_data_for_day
        )

    @swagger_auto_schema(
        request_body=WeatherRequestSerializer,
        responses={200: WeatherResponseSerializer}
    )
    @action(detail=False, methods=['post'])
    def now(self, request):
        """Эндпоинт для получения данных за текущий,
        округленный к ближайшему, час.
        """
        # Округление времени
        now = datetime.now()
        rounded_time = now + timedelta(minutes=30)
        rounded_hour = rounded_time.replace(
            minute=0, second=0, microsecond=0
        ).hour
        return self._process_weather_request(
            request,
            WeatherService(API_KEY, WEATHER_URL).get_data_for_hour,
            rounded_hour
        )
