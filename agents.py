from aiogram import types
from bot import bot

class Agents:
    def __init__(self):
        self.agents = ["Agent 1", "Agent 2", "Agent 3"]  # Add your agents here

    async def show(self, message: types.Message):
        keyboard = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(agent, callback_data=agent) for agent in self.agents]
        keyboard.add(*buttons)
        await bot.send_message(message.chat.id, "Choose an agent:", reply_markup=keyboard)

