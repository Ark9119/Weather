def test_weather_to_days_success(client, valid_request_data_for_days):
    """
    Тест успешного запроса к weather_to_days эндпоинту
    """
    response = client.post(
        '/weather/weather_to_days/',
        data=valid_request_data_for_days,
        format='json'
    )
    assert response.status_code == 200


def test_weather_to_days_method_not_allowed(
    client, valid_request_data_for_days
):
    """
    Тест успешного запроса к weather_to_days эндпоинту
    """
    assert isinstance(valid_request_data_for_days, dict)
    print('при запросе передаётся словарь')

    response = client.get(
        '/weather/weather_to_days/',
        data=valid_request_data_for_days,
        format='json'
    )
    assert response.status_code == 405
