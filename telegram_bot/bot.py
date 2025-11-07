import os

import asyncio
import aiohttp

from aiogram import Bot, types, Router, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv('TOKEN_TELEGRAM')
bot = Bot(token=str(TOKEN))
dp = Dispatcher()
router = Router()

# Регистрируем router в dispatcher
dp.include_router(router)


# Создаем состояния для FSM
class WeatherStates(StatesGroup):
    waiting_city = State()


# Создаем клавиатуру
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Изменить город')],
        [
            KeyboardButton(text='Погода на 3 дня'),
            KeyboardButton(text='Погода сегодня'),
            KeyboardButton(text='Погода сейчас')
        ]
    ],
    resize_keyboard=True  # чтобы клавиатура была адаптивной
)


async def fetch_weather_data(api_url, payload):
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                city = data.get('city')
                forecast = data.get('forecast')
                return city, forecast, response.status, None
            else:
                try:
                    error_data = await response.json()
                    error_message = error_data.get('error', 'Unknown error')
                    print(f'error_message {error_message}')
                except Exception as e:
                    print(f'eeeee{e}')
                    error_message = await response.text(e)
                return None, None, response.status, error_message


async def check_user_exists(user):
    """Проверяет, есть ли пользователь в базе через GET запрос"""
    api_url = f'http://127.0.0.1:8000/city/{user}/'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return True, data.get('city')  # Пользователь есть, возвращаем город
                elif response.status == 404:
                    return False, None  # Пользователя нет
                else:
                    print(f"Unexpected status code: {response.status}")
                    return False, None
    except Exception as e:
        print(f"Error checking user existence: {e}")
        return False, None


# @router.message(CommandStart())
# async def start_cmd(message: types.Message):
#     await message.answer(
#         'Это была команда старт',
#         reply_markup=main_menu_keyboard
#     )
@router.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or str(user_id)
    # Проверяем, есть ли пользователь в базе
    user_exists, current_city = await check_user_exists(user_id)

    if not user_exists:
        # Пользователя нет в базе - предлагаем указать город
        await message.answer(
            f'Добро пожаловать, {username}! 👋\n\n'
            'Я ваш погодный бот. Для начала работы нужно указать ваш город.\n'
            'Пожалуйста, введите название города:'
        )
        # Сохраняем user_id в состоянии, чтобы использовать при сохранении города
        await state.update_data(user_id=user_id, username=username)
        await state.set_state(WeatherStates.waiting_city)
    else:
        # Пользователь уже есть в базе - показываем меню
        await message.answer(
            f'С возвращением, {username}! ✅\n\n'
            f'Ваш текущий город: {current_city}\n'
            'Выберите опцию из меню ниже:',
            reply_markup=main_menu_keyboard
        )


@router.message(Command(commands=['test']))
async def test_cmd(message: types.Message):
    api_url = 'http://127.0.0.1:8000/city/'
    payload = {
        'city': 'testcity',
        'user': 'hdfgg'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload) as response:
            data = await response.json()
            await message.answer(
                    f'test {data}',
                )


# Обработчик для получения города от пользователя
@router.message(WeatherStates.waiting_city)
async def process_city(message: types.Message, state: FSMContext):
    city = message.text.strip()
    user_data = await state.get_data()
    # user_id = message.from_user.id
    user_id = user_data.get('user_id', message.from_user.id)
    username = user_data.get('username', message.from_user.username or message.from_user.first_name or str(user_id))

    if not city:
        await message.answer("Пожалуйста, введите корректное название города:")
        return

    api_url = 'http://127.0.0.1:8000/city/'
    payload = {
        # 'city': f'{city}',
        'city': city,
        'user': user_id
    }
    print(f'payload {payload}')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload) as response:
                if response.status == 200 or response.status == 201:
                    data = await response.json()
                    print(f'data: {data}')
                    saved_city = data.get('city')
                    user = data.get('user')
                    await message.answer(
                        f'Для пользователя {user}'
                        f'установлен город {saved_city}',
                        reply_markup=main_menu_keyboard
                    )
                else:
                    await message.answer(
                        # f'Ошибка при запоминании города: {response.status}',
                        # reply_markup=main_menu_keyboard
                        f'❌ Ошибка при сохранении города: {response.status}.'
                        f'{error_text}\n'
                        'Пожалуйста, попробуйте еще раз:'
                    )
    except Exception as e:
        await message.answer(
            # f'Произошла ошибка: {str(e)}',
            # reply_markup=main_menu_keyboard
            f'❌ Произошла ошибка: {str(e)}\n'
            'Пожалуйста, попробуйте еще раз:'
        )
    # Сбрасываем состояние
    await state.clear()


# @router.message()
@router.message(F.text.in_([
    "Изменить город", "Погода на 3 дня", "Погода сегодня", "Погода сейчас"
]))
async def handle_buttons_and_text(message: types.Message, state: FSMContext):
    text = message.text
    if text == "Изменить город":
        await remember_city(message, state)
    elif text == 'Погода на 3 дня':
        await weather_command(message, state)
    elif text == 'Погода сегодня':
        await weather_today(message, state)
    elif text == 'Погода сейчас':
        await weather_now(message, state)


# Начало процесса изменения города
async def remember_city(message: types.Message, state: FSMContext):
    # await message.answer("Введите название города:")
    # # Устанавливаем состояние ожидания города
    # await state.set_state(WeatherStates.waiting_city)
    # Сохраняем user_id в состоянии
    await state.update_data(
        user_id=message.from_user.id,
        username=message.from_user.username or message.from_user.first_name or str(message.from_user.id)
    )
    await message.answer("Введите название вашего города:")
    await state.set_state(WeatherStates.waiting_city)


async def handle_weather_request(
    message: types.Message,
    state: FSMContext,
    api_url: str,
    days: str = None
):
    """Общая функция для обработки запросов погоды"""
    user_id = message.from_user.id

    # Проверяем, есть ли пользователь в базе
    user_in_db, current_city = await check_user_exists(user_id)

    if not user_in_db:
        await message.answer(
            '📍 Для получения прогноза погоды сначала нужно'
            'указать ваш город.\n'
            'Пожалуйста, введите название города:'
        )
        await state.update_data(
            user_id=user_id,
            username=(
                message.from_user.username
                or message.from_user.first_name
                or str(user_id)
            )
        )
        await state.set_state(WeatherStates.waiting_city)
        return

    # Если пользователь есть в базе, делаем запрос погоды
    payload = {'user': user_id}
    if days:
        payload['days'] = days

    city, forecast, status, error_message = await fetch_weather_data(
        api_url, payload
    )
    # print(status)
    if status == 200:
        if isinstance(forecast, list):
            # Для прогноза на несколько дней
            weather_text = f"🌤 Прогноз погоды в {city}:\n\n"
            for i, day in enumerate(forecast, 1):
                weather_text += f"День {i}: {day}\n"
            await message.answer(weather_text)
        else:
            # Для прогноза на один день
            await message.answer(f"🌤 Погода в {city}: {forecast}")
    else:
        # Используем конкретное сообщение об ошибке от API
        if status == 400:
            # Для ошибок валидации (неправильный город и т.д.)
            await message.answer(
                f"❌ {error_message}\n"
                "Пожалуйста, укажите ваш город еще раз:"
            )
            await state.update_data(
                user_id=user_id,
                username=(
                    message.from_user.username
                    or message.from_user.first_name
                    or str(user_id)
                )
            )
            await state.set_state(WeatherStates.waiting_city)
        elif status == 500:
            # Для внутренних ошибок сервера
            await message.answer(
                f"❌ Внутренняя ошибка сервера: {error_message}\n"
                "Пожалуйста, попробуйте позже."
            )
        else:
            # Для всех остальных ошибок
            await message.answer(
                f'❌ Ошибка при получении погоды (код {status}): {error_message}'
            )


@router.message(Command(commands=['weather']))
async def weather_command(message: types.Message, state: FSMContext):
    api_url = 'http://127.0.0.1:8000/weather/weather_to_days/'
    await handle_weather_request(message, state, api_url, '3')


@router.message(Command(commands=['today']))
async def weather_today(message: types.Message, state: FSMContext):
    api_url = 'http://127.0.0.1:8000/weather/today/'
    await handle_weather_request(message, state, api_url, '1')


@router.message(Command(commands=['now']))
async def weather_now(message: types.Message, state: FSMContext):
    api_url = 'http://127.0.0.1:8000/weather/now/'
    await handle_weather_request(message, state, api_url, '1')


# @router.message(Command(commands=['weather']))
# async def weather_command(message: types.Message):
#     api_url = 'http://127.0.0.1:8000/weather/'
#     user_id = message.from_user.id
#     # payload = {'city': 'Moscow', 'days': '3'}
#     payload = {'user': user_id, 'days': '3'}
#     city, forecast, status = await fetch_weather_data(api_url, payload)
#     if city and forecast:
#         for day in forecast:
#             await message.answer(f'Погода в {city}: {day}')
#     else:
#         await message.answer(f'Ошибка при получении погоды: {status}')


# @router.message(Command(commands=['today']))
# async def weather_today(message: types.Message):
#     api_url = 'http://127.0.0.1:8000/weather/today/'
#     user_id = message.from_user.id
#     payload = {
#         'user': user_id
#     }
#     city, forecast, status = await fetch_weather_data(api_url, payload)
#     if city and forecast:
#         await message.answer(f'Погода в {city}: {forecast}')
#     else:
#         await message.answer(f'Ошибка при получении погоды: {status}')


# @router.message(Command(commands=['now']))
# async def weather_now(message: types.Message):
#     api_url = 'http://127.0.0.1:8000/weather/now/'
#     user_id = message.from_user.id
#     payload = {
#         'user': user_id
#     }
#     city, forecast, status = await fetch_weather_data(api_url, payload)
#     if city and forecast:
#         await message.answer(f'Погода в {city}: {forecast}')
#     else:
#         await message.answer(f'Ошибка при получении погоды: {status}')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
