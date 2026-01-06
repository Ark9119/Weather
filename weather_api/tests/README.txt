# Запустить все тесты
pytest tests/test_weather.py -v

# Запустить только интеграционные тесты (требует запущенный сервис авторизации)
pytest tests/test_weather.py -m integration -v

# Запустить обычные тесты (без интеграционных)
pytest tests/test_weather.py -m "not integration" -v