import pytest
import os
import uuid
import requests

from django.test import Client
from dotenv import load_dotenv


load_dotenv()

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://127.0.0.1:8002')


@pytest.fixture
def url_weather_for_3_days():
    return '/weather/weather_to_days/'


@pytest.fixture
def url_weather_today():
    return '/weather/today/'


@pytest.fixture
def url_weather_now():
    return '/weather/now/'


@pytest.fixture
def client():
    """Создаем Django тестовый клиент"""
    return Client()


@pytest.fixture
def valid_request_data_for_3_days():
    """Валидные данные для запроса на 3 дня"""
    return {
        'user': 'testuser',
        'city': 'Moscow',
        'days': 3
    }


@pytest.fixture
def valid_request_data_for_one_day():
    """Валидные данные для запроса на 1 день"""
    return {
        'user': 'testuser',
        'city': 'Moscow',
        'days': 1
    }


@pytest.fixture
def no_user_request_data_for_3_days():
    """Без поля user данные для запроса на 3 дня"""
    return {
        'city': 'Moscow',
        'days': 3
    }


@pytest.fixture
def no_user_request_data_for_1_days():
    """Без поля user данные для запроса на 1 день"""
    return {
        'city': 'Moscow',
        'days': 3
    }


@pytest.fixture
def no_city_request_data_for_3_days():
    """Без поля city данные для запроса на 3 дня"""
    return {
        'user': 'testuser',
        'days': 3
    }


@pytest.fixture
def no_city_request_data_for_1_days():
    """Без поля city данные для запроса на 1 день"""
    return {
        'user': 'testuser',
        'days': 3
    }


@pytest.fixture(scope='session')
def registered_user():
    """
    Фикстура создает тестового пользователя в сервисе авторизации,
    выполняет тест и затем удаляет пользователя.
    """
    # Генерируем уникальное имя пользователя
    username = f'testuser_{uuid.uuid4().hex[:8]}'
    password = 'testpass123'
    city = 'Moscow'

    # Создаем пользователя
    register_url = f'{AUTH_SERVICE_URL}/auth/register'
    register_data = {
        'username': username,
        'password': password,
        'city': city
    }

    try:
        # Регистрация
        register_response = requests.post(
            register_url,
            json=register_data,
        )
        register_response.raise_for_status()
        # Получаем токен
        login_url = f'{AUTH_SERVICE_URL}/auth/login'
        login_data = {
            'username': username,
            'password': password
        }
        login_response = requests.post(
            login_url,
            json=login_data,
        )
        login_response.raise_for_status()
        token_data = login_response.json()
        token = token_data.get('access_token', token_data.get('token', ''))

        if not token:
            pytest.skip('Не удалось получить токен авторизации')

        # Возвращаем данные пользователя
        user_data = {
            'username': username,
            'password': password,
            'city': city,
            'token': token
        }

        yield user_data

    except requests.exceptions.RequestException as e:
        pytest.skip(f'Сервис авторизации недоступен: {str(e)}')

    finally:
        # Удаляем пользователя
        try:
            delete_url = f'{AUTH_SERVICE_URL}/users/me'
            headers = {'Authorization': f'Bearer {token}'}
            requests.delete(delete_url, headers=headers, timeout=5)
        except Exception:
            pass  # Игнорируем ошибки при удалении


@pytest.fixture
def request_data_for_registered_user(registered_user):
    """
    Данные для запроса с зарегистрированным пользователем на 3 дня
    """
    return {
        'user': registered_user['username'],
        'days': 3
    }


@pytest.fixture
def request_data_for_registered_user_one_day(registered_user):
    """
    Данные для запроса с зарегистрированным пользователем на 1 день
    """
    return {
        'user': registered_user['username'],
        'days': 1
    }
