# Проект Weather

## О проекте: 
**API-сервис** посылающий API запросы к международному погодному сервису,
принимающий и обрабатывающий ответы.

## Все проекты экосистемы
https://github.com/Ark9119/Weather_AUTH
https://github.com/Ark9119/Weather
https://github.com/Ark9119/Weather_bot
https://github.com/Ark9119/Weather_web

## Лицензия: 
[![License](https://img.shields.io/badge/License-View-blue)](LICENSE)

## Возможности:
- Обработка данных, полученных от погодного сервиса.
- В запросе можно передавать искомый город или идентификатор авторизованного
    в сервисе Weather_AUTH(https://github.com/Ark9119/Weather_AUTH)
    и получать город, привязанный к пользователю.
- Обработка ошибок погодного сервиса, ошибок самого приложения.
- Покрыт тестами(Pytest)

- Масштабируемость: 
    - Возможность добавить типы запросов к погодному сервису(сейчас 3 типа запросов).
    - Возможность добавлять/убирать поля с характеристиками погоды,
    приходящие в ответе от погодного сервиса.
- Есть готовые проекты для отдачи информации пользователю:
    - Телеграм бот https://github.com/Ark9119/Weather_bot
    - WEB Application https://github.com/Ark9119/Weather_web


## Технологии
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-092E20?&logo=django)](https://www.djangoproject.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)](https://www.sqlite.org/)
[![Django REST Framework](https://img.shields.io/badge/Django_REST_Framework-grey?logo=django)](https://www.django-rest-framework.org/)


## Документация в swagger формате доступна по эндпоинту:
(http://127.0.0.1:8000/swagger/)

## Примеры запросов к API:

### Сохранение/изменение города(привязка к идентификатору пользователя):

```
POST /city/
```

Тело запроса:
```
{
"city": "str",
"user": "str"
}
```
### Получение города по пользователю

```
GET /city/<user_id>
```

### Получение погоды:

```
POST /weather/weather_to_days/ - на 1-3 дня
```
```
POST /weather/today/ - на сегодня
```
```
POST /weather/now/ - сейчас
```
Тело запроса:
```
{
"city": "str", или "user": "str",
"days": "int"
}
```
Пример ответа:
```
{
    "city": "москва",
    "forecast": [
        {
            "found_country": "Россия",
            "found_city": "Москва",
            "date": "2025-11-18",
            "field": "int or []",
            "field": "int or []",
            ...
        }
    ]
}
```

Автор проекта: [Ivan Kuznetsov]
(https://github.com/Ark9119/Weather)
