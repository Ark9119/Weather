import os
import asyncio
import aiohttp
from aiogram import Bot, types, Router, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN_TELEGRAM')
bot = Bot(token=str(TOKEN))
dp = Dispatcher()
router = Router()
dp.include_router(router)


class WeatherStates(StatesGroup):
    waiting_city = State()


main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Изменить город')],
        [
            KeyboardButton(text='Погода на 3 дня'),
            KeyboardButton(text='Погода сегодня'),
            KeyboardButton(text='Погода сейчас')
        ]
    ],
    resize_keyboard=True
)


async def make_api_request(api_url: str, payload: dict = None, method: str = 'POST'):
    """Универсальная функция для API-запросов"""
    async with aiohttp.ClientSession() as session:
        async with session.request(method, api_url, json=payload) as response:
            try:
                data = await response.json() if response.status != 204 else None
            except:
                data = None
                
            if response.status in (200, 201):
                return data, response.status, None
            else:
                error_msg = data.get('error', 'Unknown error') if data else await response.text()
                return None, response.status, error_msg


async def check_user_exists(user_id: int):
    """Проверяет наличие пользователя в базе"""
    api_url = f'http://127.0.0.1:8000/city/{user_id}/'
    data, status, error = await make_api_request(api_url, method='GET')
    
    if status == 200:
        return True, data.get('city')
    elif status == 404:
        return False, None
    else:
        print(f"Error checking user: {error}")
        return False, None


async def save_user_city(user_id: int, city: str):
    """Сохраняет город для пользователя"""
    api_url = 'http://127.0.0.1:8000/city/'
    payload = {'city': city, 'user': user_id}
    return await make_api_request(api_url, payload)


async def get_weather_data(user_id: int, endpoint: str, days: str = None):
    """Получает данные о погоде"""
    api_url = f'http://127.0.0.1:8000/weather/{endpoint}/'
    payload = {'user': user_id}
    if days:
        payload['days'] = days
        
    data, status, error = await make_api_request(api_url, payload)
    if status == 200:
        city = data.get('city')
        forecast = data.get('forecast')
        return city, forecast, status, error
    return None, None, status, error


@router.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or str(user_id)
    
    user_exists, current_city = await check_user_exists(user_id)

    if not user_exists:
        await message.answer(
            f'Добро пожаловать, {username}! 👋\n\n'
            'Я ваш погодный бот. Для начала работы нужно указать ваш город.\n'
            'Пожалуйста, введите название города:'
        )
        await state.update_data(user_id=user_id, username=username)
        await state.set_state(WeatherStates.waiting_city)
    else:
        await message.answer(
            f'С возвращением, {username}! ✅\n\n'
            f'Ваш текущий город: {current_city}\n'
            'Выберите опцию из меню ниже:',
            reply_markup=main_menu_keyboard
        )


@router.message(WeatherStates.waiting_city)
async def process_city(message: types.Message, state: FSMContext):
    city = message.text.strip()
    user_data = await state.get_data()
    user_id = user_data.get('user_id', message.from_user.id)

    if not city:
        await message.answer("Пожалуйста, введите корректное название города:")
        return

    data, status, error = await save_user_city(user_id, city)
    
    if status in (200, 201):
        saved_city = data.get('city')
        await message.answer(
            f'Город {saved_city} успешно сохранен!',
            reply_markup=main_menu_keyboard
        )
        await state.clear()
    else:
        error_msg = error or 'Неизвестная ошибка'
        await message.answer(
            f'❌ Ошибка при сохранении города: {error_msg}\n'
            'Пожалуйста, попробуйте еще раз:'
        )


async def handle_weather_request(
    message: types.Message,
    state: FSMContext,
    endpoint: str,
    days: str = None
):
    """Общая функция для обработки запросов погоды"""
    user_id = message.from_user.id

    user_exists, current_city = await check_user_exists(user_id)

    if not user_exists:
        await message.answer(
            '📍 Для получения прогноза погоды сначала нужно указать ваш город.\n'
            'Пожалуйста, введите название города:'
        )
        await state.update_data(
            user_id=user_id,
            username=message.from_user.username or message.from_user.first_name or str(user_id)
        )
        await state.set_state(WeatherStates.waiting_city)
        return

    city, forecast, status, error = await get_weather_data(user_id, endpoint, days)

    if status == 200:
        if isinstance(forecast, list):
            weather_text = f"🌤 Прогноз погоды в {city}:\n\n"
            for i, day in enumerate(forecast, 1):
                weather_text += f"День {i}: {day}\n"
            await message.answer(weather_text)
        else:
            await message.answer(f"🌤 Погода в {city}: {forecast}")
    else:
        error_msg = error or 'Неизвестная ошибка'
        if status == 400:
            await message.answer(
                f"❌ {error_msg}\n"
                "Пожалуйста, укажите ваш город еще раз:"
            )
            await state.update_data(
                user_id=user_id,
                username=message.from_user.username or message.from_user.first_name or str(user_id)
            )
            await state.set_state(WeatherStates.waiting_city)
        else:
            await message.answer(f'❌ Ошибка при получении погоды: {error_msg}')


@router.message(F.text == "Изменить город")
async def change_city(message: types.Message, state: FSMContext):
    await state.update_data(
        user_id=message.from_user.id,
        username=message.from_user.username or message.from_user.first_name or str(message.from_user.id)
    )
    await message.answer("Введите название вашего города:")
    await state.set_state(WeatherStates.waiting_city)


@router.message(F.text == "Погода на 3 дня")
async def weather_3_days(message: types.Message, state: FSMContext):
    await handle_weather_request(message, state, 'weather_to_days', '3')


@router.message(F.text == "Погода сегодня")
async def weather_today(message: types.Message, state: FSMContext):
    await handle_weather_request(message, state, 'today', '1')


@router.message(F.text == "Погода сейчас")
async def weather_now(message: types.Message, state: FSMContext):
    await handle_weather_request(message, state, 'now', '1')


@router.message(Command(commands=['weather']))
async def weather_command(message: types.Message, state: FSMContext):
    await handle_weather_request(message, state, 'weather_to_days', '3')


@router.message(Command(commands=['today']))
async def today_command(message: types.Message, state: FSMContext):
    await handle_weather_request(message, state, 'today', '1')


@router.message(Command(commands=['now']))
async def now_command(message: types.Message, state: FSMContext):
    await handle_weather_request(message, state, 'now', '1')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())