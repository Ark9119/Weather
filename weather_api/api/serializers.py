import random

from rest_framework import serializers

from .models import UserCity


class UserCitySerializer(serializers.ModelSerializer):
    # user = serializers.IntegerField(required=False)

    class Meta:
        model = UserCity
        fields = ('user', 'city')

    def create(self, validated_data):
        # user = validated_data.get('user', None)
        user = validated_data.get('user')
        city = validated_data.get('city')
        # if user is None:
        #     user = random.randint(1, 10000)  # или другой диапазон
        # validated_data['user'] = user
        # return super().create(validated_data)
        return UserCity.objects.create(user=user, city=city)

    # def update(self, instance, validated_data):
    #     instance.city = validated_data.get('city', instance.city)
    #     instance.user = validated_data.get('user', instance.user)
    #     instance.save()
    #     return instance
