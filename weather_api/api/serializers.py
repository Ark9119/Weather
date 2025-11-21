from rest_framework import serializers

from .constants import (
    MAX_LENGTH_CITY
)
from .models import UserCity


class UserCitySerializer(serializers.ModelSerializer):
    city = serializers.CharField(
        max_length=MAX_LENGTH_CITY,
        error_messages={
            'max_length': 'Название города не может превышать 100 символов.'
        }
    )

    class Meta:
        model = UserCity
        fields = ('user', 'city')

    def create(self, validated_data):
        user = validated_data.get('user')
        city = validated_data.get('city')
        return UserCity.objects.create(user=user, city=city)


class WeatherRequestSerializer(serializers.Serializer):
    user = serializers.CharField(
        required=False,
        help_text=(
            'ID пользователя'
            '(если не указан city, будет взят город из профиля пользователя)'
        )
    )
    city = serializers.CharField(
        required=False,
        max_length=MAX_LENGTH_CITY,
        error_messages={
            'max_length': 'Название города не может превышать 100 символов.'
        },
        help_text=(
            'Город (если не указан,'
            'будет использован город из профиля пользователя)'
        )
    )
    days = serializers.IntegerField(
        min_value=1,
        max_value=3,
        error_messages={
            'min_value': 'days должно быть в диапазоне от 1 до 3, включительно.',
            'max_value': 'days должно быть в диапазоне от 1 до 3, включительно.'
        },
        help_text='Количество дней для прогноза (1-3).'
    )

    def validate(self, data):
        """
        Проверяем, что указан хотя бы один из параметров: user или city.
        """
        if not data.get('user') and not data.get('city'):
            raise serializers.ValidationError(
                'Необходимо указать либо user, либо city.'
            )
        # Если указан user, проверяем что он существует в базе
        if data.get('user') and not data.get('city'):
            try:
                UserCity.objects.get(user=data['user'])
            except UserCity.DoesNotExist:
                raise serializers.ValidationError(
                    'Данного пользователя нет в базе.'
                )
        return data


class WeatherResponseSerializer(serializers.Serializer):
    city = serializers.CharField(
        help_text='Город для которого получен прогноз.'
    )
    forecast = serializers.ListField(
        child=serializers.DictField(),
        help_text='Список прогнозов погоды.'
    )
