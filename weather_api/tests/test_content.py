def test_weather_to_days_response(client, valid_request_data_for_days):
    """
    Тест успешного запроса к weather_to_days эндпоинту
    """
    response = client.post(
        '/weather/weather_to_days/',
        data=valid_request_data_for_days,
        format='json'
    )
    response_data = response.json()
    assert 'city' in response_data
    assert 'forecast' in response_data
    assert isinstance(response_data['city'], str)
    assert isinstance(response_data['forecast'], list)
