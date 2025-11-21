from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
]


schema_view = get_schema_view(
    openapi.Info(
        title='Weather',
        default_version='1.0',
        description='Документация для проекта Weather',
        contact=openapi.Contact(
            email='ark9119@yandex.ru',
            url='https://github.com/Ark9119'
        ),
        license=openapi.License(
            name='Проприетарная лицензия',
            url='https://github.com/Ark9119/weather/blob/main/LICENSE'
        ),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    path(
        'swagger<format>/',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
