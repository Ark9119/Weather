import random

from rest_framework import serializers

from .models import UserCity


class UserCitySerializer(serializers.ModelSerializer):

    class Meta:
        model = UserCity
        fields = ('user', 'city')

    def create(self, validated_data):
        user = validated_data.get('user')
        city = validated_data.get('city')
        # if user is None:
        #     user = random.randint(1, 10000)  # или другой диапазон
        # validated_data['user'] = user
        # return super().create(validated_data)
        return UserCity.objects.create(user=user, city=city)
