from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import Weather, UserCityViewSet


router = DefaultRouter()
router.register(r'weather', Weather, basename='weather')
router.register(r'city', UserCityViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
