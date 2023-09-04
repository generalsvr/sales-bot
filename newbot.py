import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

TOKEN = "766919436:AAFaTfZicf4A-iRXuylOHq9xbqg6QQwfC34"

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    bot = message.bot
    # result = await bot.create_forum_topic(chat_id="@testing_sexting", name="Testing")
    # print(result) # message_thread_id=10 name='Testing' icon_color=7322096 icon_custom_emoji_id=None
    await bot.send_message(chat_id="@testing_sexting", message_thread_id=10, text="Hello, world!")

async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())