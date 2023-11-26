import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import Throttled
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InputFile
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

bot = Bot(token="6964231551:AAEnnyNoj6xRkCxEShyff3WwXpNBLqJvH5U")  # Тут токен
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)


@dp.message_handler(content_types="text")
async def parser(message: types.Message):
    pattern = r'(http[s]?://)?(www\.)?[\w.]+\.[\w]+'
    match = re.search(pattern, message.text)
    if match:
        print(match.group())
        keyboard = types.InlineKeyboardMarkup()
        buttons = [
            types.InlineKeyboardButton(text="Создать скриншот!", callback_data=f"{match.group()}")
        ]
        keyboard.add(*buttons)
        await message.reply(f"В сообщении обнаружена ссылка!", reply_markup=keyboard)


@dp.callback_query_handler()
async def process_callback_button(callback_query: CallbackQuery):
    action = callback_query.data
    print(action)
    messages = callback_query.message
    await messages.edit_text("Запускаю селениум...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--proxy-server=socks5://тутпрокси')  # Тут прокси
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
    await messages.edit_text("Делаю скриншот...")
    driver.get(action)
    driver.save_screenshot(f"screen/{callback_query.message.chat.id}.png")
    driver.quit()
    await messages.delete()
    photo = InputFile(f'screen/{callback_query.message.chat.id}.png')
    await bot.send_photo(callback_query.message.chat.id, photo, f"Скриншот успешно сделан!\nСайт: {action}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)