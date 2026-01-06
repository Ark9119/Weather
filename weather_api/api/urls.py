from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import Weather


router = DefaultRouter()
router.register(r'weather', Weather, basename='weather')


urlpatterns = [
    path('', include(router.urls)),
]
