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

from .exceptions import WeatherException
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

    def _get_weather_data(self, request, required_days=None):
        """
        Общий метод для получения данных о погоде.
        Отдаёт списки данных, город и дни.
        """
        user = request.data.get('user')
        take_response_city = request.data.get('city')
        if take_response_city is None:
            try:
                city = UserCity.objects.get(user=user).city
            except UserCity.DoesNotExist:
                raise WeatherException(
                    'Данного пользователя нет в базе.',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        else:
            city = take_response_city
        if not city:
            raise WeatherException(
                'Missing parameter: city',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        if not request.data.get('days'):
            raise WeatherException(
                'Missing parameter: days',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        else:
            days = request.data.get('days')
        weather_service = WeatherService(API_KEY, WEATHER_URL)
        try:
            data = weather_service.fetch_data(city, days=days)
            return data, city
        except WeatherException as e:
            raise e
        except Exception as e:
            raise WeatherException(
                f'Weather service error: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def weather_to_days(self, request):
        """Выдаёт погоду на на 1 - 3 дня."""
        try:
            data, city = self._get_weather_data(
                request, required_days=True
            )
            forecast = WeatherService(
                API_KEY, WEATHER_URL
            ).get_data_for_day(data)
        except WeatherException as e:
            return Response(
                {'error': str(e)},
                status=e.status_code
            )
        return Response({
            'city': city,
            'forecast': forecast,
        })

    @action(detail=False, methods=['post'])
    def today(self, request):
        """Выдаёт погоду на сегодня."""
        try:
            data, city = self._get_weather_data(request)
            forecast = WeatherService(
                API_KEY, WEATHER_URL
            ).get_data_for_day(data)
            today_forecast = forecast  # [0] if forecast else {} - это если нужно возвращать один день, а не список дней с одним днём
        except WeatherException as e:
            return Response(
                {'error': str(e)},
                status=e.status_code
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
        try:
            data, city = self._get_weather_data(request)
            # Округление времени
            now = datetime.now()
            rounded_time = now + timedelta(minutes=30)
            rounded_hour = rounded_time.replace(
                minute=0, second=0, microsecond=0
            ).hour
            this_time_forecast = WeatherService(
                API_KEY, WEATHER_URL
            ).get_data_for_hour(
                data, hour=rounded_hour
            )
        except WeatherException as e:
            return Response(
                {'error': str(e)},
                status=e.status_code
            )

        return Response({
            'city': city,
            'forecast': this_time_forecast
        })
