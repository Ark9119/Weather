import pytest

from pytest_lazy_fixtures import lf


@pytest.mark.parametrize(
    ['urls', 'request_data'],
    [
        (lf('url_weather_for_3_days'), lf('valid_request_data_for_3_days')),
        (lf('url_weather_today'), lf('valid_request_data_for_one_day')),
        (lf('url_weather_now'), lf('valid_request_data_for_one_day')),
    ]
)
def test_endpoint_success(client, request_data, urls):
    """
    Тест успешного запроса ко всем эндпоинтам
    """
    response = client.post(
        urls,
        data=request_data,
        format='json'
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'urls',
    [
        lf('url_weather_for_3_days'),
        lf('url_weather_today'),
        lf('url_weather_now'),
    ]
)
def test_weather_to_days_method_not_allowed(
    client, urls, valid_request_data_for_3_days
):
    """
    Тест запрещённых методов запроса
    """
    response = client.get(
        urls,
        data=valid_request_data_for_3_days,
        format='json'
    )
    assert response.status_code == 405


@pytest.mark.parametrize(
    ['urls', 'request_data'],
    [
        (lf('url_weather_for_3_days'), lf('no_user_request_data_for_3_days')),
        (lf('url_weather_today'), lf('no_user_request_data_for_1_days')),
        (lf('url_weather_now'), lf('no_user_request_data_for_1_days')),
    ]
)
def test_no_user_request(
    client,
    urls,
    request_data
):
    """
    Тест запроса без передачи поля user
    """

    response = client.post(
        urls,
        data=request_data,
        format='json'
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    ['urls', 'request_data'],
    [
        (lf('url_weather_for_3_days'), lf('no_city_request_data_for_3_days')),
        (lf('url_weather_today'), lf('no_city_request_data_for_1_days')),
        (lf('url_weather_now'), lf('no_city_request_data_for_1_days')),
    ]
)
def test_no_city_request(
    client,
    urls,
    request_data
):
    """
    Тест запроса без передачи поля city
    """

    response = client.post(
        urls,
        data=request_data,
        format='json'
    )
    assert response.status_code == 404
    assert 'Город не найден для пользователя' in response.json()['error']


@pytest.mark.parametrize(
    'urls',
    [
        lf('url_weather_for_3_days'),
        lf('url_weather_today'),
        lf('url_weather_now'),
    ]
)
def test_request_invalid_data(
    client,
    urls
):
    """
    Тест с некорректными данными
    """
    invalid_data = [
        {},
        {'user': 'testuser', 'city': 'Moscow'},
        {'user': 'testuser', 'days': 10},
        {'user': 'testuser', 'city': 'Moscow', 'days': 0},
        {'user': 'testuser', 'city': 'Moscow', 'days': -1},
    ]

    for data in invalid_data:
        response = client.post(urls, data=data, format='json')
        assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.parametrize(
    ['urls', 'request_data'],
    [
        (
            lf('url_weather_for_3_days'),
            lf('request_data_for_registered_user')
        ),
        (
            lf('url_weather_today'),
            lf('request_data_for_registered_user_one_day')
        ),
        (
            lf('url_weather_now'),
            lf('request_data_for_registered_user_one_day')
        ),
    ]
)
def test_with_registered_user_success(
    client, urls, request_data, registered_user
):
    """
    Тест успешного запроса с зарегистрированным пользователем
    (город извлекается из сервиса авторизации)
    """
    response = client.post(
        urls,
        data=request_data,
        format='json'
    )
    # Проверяем успешный статус
    assert response.status_code == 200
    # Проверяем, что город в ответе соответствует городу пользователя
    response_data = response.json()
    assert 'city' in response_data
    assert response_data['city'] == registered_user['city']
    # Проверяем структуру ответа
    assert 'forecast' in response_data
    assert isinstance(response_data['forecast'], list)


@pytest.mark.integration
def test_registered_user_creation(registered_user):
    """
    Проверка, что фикстура правильно создает пользователя
    """
    assert isinstance(registered_user, dict)
    assert 'username' in registered_user
    assert 'city' in registered_user
    assert 'token' in registered_user
    assert registered_user['city'] == 'Moscow'
