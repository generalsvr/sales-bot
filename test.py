
# загружаем библиотеки
from aiogram import Bot, Dispatcher, executor, types

# это наш токен, который мы получили от @BotFather
API_TOKEN = 'BOT TOKEN HERE'

# создаем бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # вот так мы отправляем сообщение
    await bot.send_message(message.chat.id, "Привет! Я бот, который повторяет за тобой")


# обработчик команды /keyboard
@dp.message_handler(commands=['keyboard'])
async def say_something(message: types.Message):
    buttons = [
        types.InlineKeyboardButton(text="Кнопка 1", callback_data="button1"),
        types.InlineKeyboardButton(text="Кнопка 2", callback_data="button2"),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    await bot.send_message(message.chat.id, "вот так делаем кнопки", reply_markup=keyboard)

# обработчик любого текстового сообщения
@dp.message_handler()
async def echo(message: types.Message):
    # вот так отвечаем на сообщение
    await bot.send_message(message.chat.id, message.text)


# это нужно, чтобы запустить бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)