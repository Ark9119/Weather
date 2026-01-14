import os
import requests

from dotenv import load_dotenv


load_dotenv()

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL')  # , 'http://127.0.0.1:8002')


def get_city_from_auth_service(username: str) -> str | None:
    """
    Получение города пользователя из микросервиса weather_auth.
    Args:
        username: Имя пользователя в системе weather_auth
    Returns:
        str: Название города или None, если пользователь не найден
    Raises:
        requests.RequestException: При ошибке соединения с weather_auth
    """
    try:
        response = requests.get(
            f'{AUTH_SERVICE_URL}/users/{username}/city',
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('city')
        elif response.status_code == 404:
            return None
        else:
            print(
                f'Ошибка при получении города из weather_auth:'
                f'{response.status_code}'
            )
            return None
    except requests.exceptions.RequestException as e:
        print(f'Ошибка соединения с weather_auth: {str(e)}')
        return None
    except Exception as e:
        print(f'Неожиданная ошибка при получении города: {str(e)}')
        return None


def validate_token_from_auth_service(token: str) -> str | None:
    """
    Валидация JWT токена через weather_auth и получение username.
    Args:
        token: JWT токен для валидации
    Returns:
        str: username пользователя или None, если токен недействителен
    """
    try:
        response = requests.get(
            f'{AUTH_SERVICE_URL}/users/validate-token',
            headers={'Authorization': f'Bearer {token}'},
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('username')
        return None
    except Exception as e:
        print(f'Ошибка при валидации токена: {str(e)}')
        return None
