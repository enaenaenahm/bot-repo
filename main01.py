#7669266906:AAE9stnjsufHb1q7_hHVViI4f8PrLGcx9bI
import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import re
from aiogram import F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

NAME_REGEX = re.compile(r'^[A-Za-zА-Яа-яЁё\s\-]+$')

logging.basicConfig(level=logging.INFO)
API_TOKEN = "7669266906:AAE9stnjsufHb1q7_hHVViI4f8PrLGcx9bI"

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Registration(StatesGroup):
    name = State()
    phone = State()
    confirm = State()

users_db = {}
recipes_db = {
    "завтрак": ["Овсянка с фруктами", "Омлет с овощами", "Гречка с молоком"],
    "обед": ["Курица с рисом", "Суп", "Греческий салат"],
    "ужин": ["Рыба с овощами", "Творог", "Курица-гриль"],
    "перекус": ["Яблоко", "Йогурт", "Орехи"]
}

def main_kb(user_id: int):
    if user_id in users_db:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Рацион 🍽"), KeyboardButton(text="Услуги 💼")],
                [KeyboardButton(text="Обратная связь 📩")]
            ],
            resize_keyboard=True
        )
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Регистрация")]],
        resize_keyboard=True
    )

def services_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подписка 🔓"), KeyboardButton(text="Сопровождение 👨‍🍳")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )

def diet_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Завтрак"), KeyboardButton(text="Обед")],
            [KeyboardButton(text="Ужин"), KeyboardButton(text="Перекус")],
            [KeyboardButton(text="Меню на день"), KeyboardButton(text="Меню на неделю")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! Для начала работы пройди регистрацию:",
        reply_markup=main_kb(message.from_user.id)
    )

@dp.message(F.text == "Регистрация")
async def start_registration(message: types.Message, state: FSMContext):
    await message.answer("Введите ваше имя:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Registration.name)

@dp.message(Registration.name)
async def process_name(message: types.Message, state: FSMContext):
    if not NAME_REGEX.fullmatch(message.text):
        await message.answer("❌ Имя может содержать только русские/английские буквы, пробелы и дефисы.\nПопробуйте еще раз:")
        return  # Остаемся в состоянии Registration.name
    
    await state.update_data(name=message.text)
    await message.answer("Введите ваш номер телефона:")
    await state.set_state(Registration.phone)

@dp.message(Registration.phone)
async def process_phone(message: types.Message, state: FSMContext):
    # Удаляем все нецифровые символы
    phone = ''.join(filter(str.isdigit, message.text))
    
    # Проверяем длину номера
    if len(phone) not in (10, 11) or not phone.isdigit():
        await message.answer("❌ Номер должен содержать 10 или 11 цифр!\nПример: 79876543210\nПопробуйте еще раз:")
        return  # Остаемся в состоянии Registration.phone
    
    await state.update_data(phone=phone)
    await message.answer("Подтвердите согласие на обработку данных (Да/Нет):")
    await state.set_state(Registration.confirm)

@dp.message(Registration.confirm)
async def process_confirm(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text.lower() == "да":
        data = await state.get_data()
        users_db[user_id] = data
        await message.answer(
            "✅ Регистрация завершена!",
            reply_markup=main_kb(user_id)
        )
    else:
        await message.answer(
            "❌ Регистрация отменена",
            reply_markup=main_kb(user_id)
        )
    await state.clear()

@dp.message(F.text == "Услуги 💼")
async def services_menu(message: types.Message):
    await message.answer("Выберите услугу:", reply_markup=services_kb())

@dp.message(F.text == "Рацион 🍽")
async def diet_menu(message: types.Message):
    await message.answer("Выбери категорию:", reply_markup=diet_kb())

@dp.message(F.text.in_({"Завтрак", "Обед", "Ужин", "Перекус"}))
async def random_recipe(message: types.Message):
    meal_type = message.text.lower()
    recipe = random.choice(recipes_db[meal_type])
    await message.answer(f"🍴 {message.text}: {recipe}")

@dp.message(F.text == "Меню на день")
async def daily_menu(message: types.Message):
    menu = []
    for meal in ["завтрак", "обед", "ужин", "перекус"]:
        recipe = random.choice(recipes_db[meal])
        menu.append(f"• {meal.capitalize()}: {recipe}")
    await message.answer("\n".join(menu))

@dp.message(F.text == "Меню на неделю")
async def weekly_menu(message: types.Message):
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    weekly_meals = []
    for day in days:
        daily = [random.choice(recipes_db[meal]) for meal in recipes_db]
        weekly_meals.append(f"{day}: " + ", ".join(daily))
    await message.answer("\n".join(weekly_meals))

@dp.message(F.text == "Назад")
async def back(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_kb(message.from_user.id))

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())