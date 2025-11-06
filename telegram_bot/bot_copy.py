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
                return city, forecast, response.status
            else:
                return None, None, response.status


@router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        'Это была команда старт',
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
    user_id = message.from_user.id
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
                        f'Ошибка при запоминании города: {response.status}',
                        reply_markup=main_menu_keyboard
                    )
    except Exception as e:
        await message.answer(
            f'Произошла ошибка: {str(e)}',
            reply_markup=main_menu_keyboard
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
        await weather_command(message)
    elif text == 'Погода сегодня':
        await weather_today(message)
    elif text == 'Погода сейчас':
        await weather_now(message)


# Начало процесса изменения города
async def remember_city(message: types.Message, state: FSMContext):
    await message.answer("Введите название города:")
    # Устанавливаем состояние ожидания города
    await state.set_state(WeatherStates.waiting_city)


@router.message(Command(commands=['weather']))
async def weather_command(message: types.Message):
    api_url = 'http://127.0.0.1:8000/weather/'
    user_id = message.from_user.id
    # payload = {'city': 'Moscow', 'days': '3'}
    payload = {'user': user_id, 'days': '3'}
    city, forecast, status = await fetch_weather_data(api_url, payload)
    if city and forecast:
        for day in forecast:
            await message.answer(f'Погода в {city}: {day}')
    else:
        await message.answer(f'Ошибка при получении погоды: {status}')


@router.message(Command(commands=['today']))
async def weather_today(message: types.Message):
    api_url = 'http://127.0.0.1:8000/weather/today/'
    user_id = message.from_user.id
    payload = {
        'user': user_id
    }
    city, forecast, status = await fetch_weather_data(api_url, payload)
    if city and forecast:
        await message.answer(f'Погода в {city}: {forecast}')
    else:
        await message.answer(f'Ошибка при получении погоды: {status}')


@router.message(Command(commands=['now']))
async def weather_now(message: types.Message):
    api_url = 'http://127.0.0.1:8000/weather/now/'
    user_id = message.from_user.id
    payload = {
        'user': user_id
    }
    city, forecast, status = await fetch_weather_data(api_url, payload)
    if city and forecast:
        await message.answer(f'Погода в {city}: {forecast}')
    else:
        await message.answer(f'Ошибка при получении погоды: {status}')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
