# Проект Weather

## О проекте: 
**API-сервис** посылающий API запросы к международному погодному сервису,
принимающий и обрабатывающий ответы.
Эти ответы отдаются пользователю через Телеграм-бота,
в котором они так же обрабатываются.

## Лицензия: 
[![License](https://img.shields.io/badge/License-View-blue)](LICENSE)

## Возможности:
- Можно в запросе передавать искомый город или добавить пользователя
в базу данных по любому идентификатору и привязать к нему город.
- Масштабируемость: 
    - Возможность добавить типы запросов к погодному сервису(сейчас 3 типа запросов).
    - Возможность добавлять/убирать поля с характеристиками погоды,
    приходящие в ответе от погодного сервиса.
- Асинхронный Телеграм-бот, независимый от API,
идентифицирует пользователя по ID с сохранением города в базу данных.
Можно независмо от ответа API настраивать отображение характеристик погоды,
производить расчёты для реализации любой логики интерпритации погодных явлений.


## Технологии
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-092E20?&logo=django)](https://www.djangoproject.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)](https://www.sqlite.org/)
[![Django REST Framework](https://img.shields.io/badge/Django_REST_Framework-grey?logo=django)](https://www.django-rest-framework.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-2C9C49%3Flogo%3Dtelegram%26logoColor%3Dwhite)](https://aiogram.dev/)


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
