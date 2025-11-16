from rest_framework import serializers

from .models import UserCity


class UserCitySerializer(serializers.ModelSerializer):
    city = serializers.CharField(
        max_length=100,
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
