import os
from datetime import datetime, timedelta

from rest_framework import viewsets, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from dotenv import load_dotenv
from drf_yasg.utils import swagger_auto_schema

from .exceptions import WeatherException
from .models import UserCity
from .services import WeatherService
from .serializers import (
    UserCitySerializer,
    WeatherRequestSerializer,
    WeatherResponseSerializer
)

load_dotenv()

API_KEY = os.getenv('WEATHEAPI_KEY')
WEATHER_URL = os.getenv('WEATHER_URL')


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
        """Внесение в базу пользователя и привязка города к его имени."""
        user_id = request.data.get('user')

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

    def _get_weather_data(self, validated_data):
        """
        Общий метод для получения данных о погоде.
        Теперь принимает validated_data вместо request
        """
        user = validated_data.get('user')
        city = validated_data.get('city')
        # Если city не указан, берем из профиля пользователя
        if city is None:
            city = UserCity.objects.get(user=user).city
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
        serializer.is_valid(raise_exception=True)  # Валидация входных данных
        try:
            data, city = self._get_weather_data(serializer.validated_data)
            forecast = forecast_callback(data, *callback_args)
            # Используем сериализатор для валидации ответа
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
