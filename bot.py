import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo
from aiogram.filters import Command

TOKEN = "123"
WEB_APP_URL = "123"

bot = Bot(token=TOKEN)

dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Открыть Поиск Лиц", web_app=WebAppInfo(url=WEB_APP_URL))]
        ],
        resize_keyboard=True
    )
    await message.answer("Привет! Нажми кнопку ниже, чтобы запустить Mini App", reply_markup=markup)

async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())