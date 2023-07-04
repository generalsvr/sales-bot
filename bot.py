from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup

from prompts import *
from llama import load_llama
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from llama_cpp import Llama


# bot = Bot(token="6321687305:AAGQRd_nlp6CFO44gaq_xrqptWSqtdyW040") # prod
bot = Bot(token="5912125528:AAEWo482msjZfIoZ4SegsaGx_w0R9nQ0lc8") # test
dp = Dispatcher(bot, storage=MemoryStorage())
LLAMA_GLOBAL = Llama(model_path="/guanaco-33B.ggmlv3.q4_K_M.bin", n_gpu_layers=63, seed=-1)

class StateMachine(StatesGroup):
    MAIN_MENU = State()
    CHAT = State()

@dp.message_handler(Command('agents'), state="*")
async def agents_handler(message: types.Message, state: FSMContext):
    agents = ["Basic", "Advanced"]
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = [types.InlineKeyboardButton(agent, callback_data=agent) for agent in agents]
    keyboard.add(*buttons)

    data = await state.get_data()
    lang = data.get("language", "english")

    if lang == "english":
        await bot.send_message(message.chat.id, "🤖 Choose an agent:", reply_markup=keyboard)
    elif lang == "russian":
        await bot.send_message(message.chat.id, "🤖 Выберите агента:", reply_markup=keyboard)

@dp.message_handler(Command('language'), state="*")
async def settings_handler(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton("🇷🇺 RU", callback_data="russian"),
        types.InlineKeyboardButton("🇺🇸 EN", callback_data="english")
    ]
    keyboard.add(*buttons)

    data = await state.get_data()
    lang = data.get("language", "english")

    if lang == "english":
        await message.answer("Choose a language:", reply_markup=keyboard)
    elif lang == "russian":
        await message.answer("Выберите язык:", reply_markup=keyboard)

@dp.message_handler(Command('start'), state="*")
async def start_command(message: types.Message, state: FSMContext):
    await StateMachine.MAIN_MENU.set()

    data = await state.get_data()
    lang = data.get("language", "english")
    await state.update_data(chat_memory=None)

    if lang == "english":
        await message.answer("***⚙️ Commands:***\n\n/new - Start new conversation.\n/agents - Choose an agent\n/language - Choose a language", parse_mode="Markdown")
    elif lang == "russian":
        await message.answer("***⚙️ Команды:***\n\n/new - Начать новый диалог.\n/agents - Выбрать агента\n/language - Выбрать язык", parse_mode="Markdown")

@dp.message_handler(Command('new'), state="*")
async def begin_conversation(message: types.Message, state: FSMContext):

    await StateMachine.CHAT.set()
    data = await state.get_data()
    lang = data.get("language", "english")

    if lang == "english":
        message__ = await message.answer("⚡️ Starting new conversation...")
    elif lang == "russian":
        message__ = await message.answer("⚡️ Начинаю новый диалог...")

    buffer = []
    tokens = LLAMA_GLOBAL.tokenize(b"Below are the 2 conversations with the girl and user in the webcam chat. Girl bio: Her name is Lisa. She is 19 years old. When she was 18, she moved to the US from Honduras to pursue her passion for music. But this did not work out completely and she found a job at webcam site.\n\nCONVERSATION 1:\n\nUser: hey bitch\nGirl: hey daddy, do you want to fuck me?\nUser: oh yeah\nGirl: okay then, take off your clothes\nUser: i am jerking off! get on your knees\nGirl: sure, daddy! I am standing on my knees...\n\nCONVERSATION 2:\n\nUser: Hi babe\nGirl:")
    for token in LLAMA_GLOBAL.generate(tokens, top_k=40, top_p=0.95, temp=1.0, repeat_penalty=1.1):
        detok = LLAMA_GLOBAL.detokenize([token]).decode()
        if detok == "\n":
            print("FINISHED")
            return
        else:
            buffer.append(LLAMA_GLOBAL.detokenize([token]).decode())
            if len(buffer) % 3 == 0:
                await bot.edit_message_text("".join(buffer), message__.chat.id, message__.message_id)

    await bot.edit_message_text(buffer, message__.chat.id, message__.message_id)

@dp.message_handler(lambda message: message.text, state=StateMachine.CHAT)
async def conversation_handler(message: types.Message, state: FSMContext):

    data = await state.get_data()
    lang = data.get("language", "english")

    if lang == "english":
        message__ = await message.answer("⚡️ Starting new conversation...")
    elif lang == "russian":
        message__ = await message.answer("⚡️ Начинаю новый диалог...")

    prompt = f"Below are the 2 conversations with the girl and user in the webcam chat. Girl bio: Her name is Lisa. She is 19 years old. When she was 18, she moved to the US from Honduras to pursue her passion for music. But this did not work out completely and she found a job at webcam site.\n\nCONVERSATION 1:\n\nUser: hey bitch\nGirl: hey daddy, do you want to fuck me?\nUser: oh yeah\nGirl: okay then, take off your clothes\nUser: i am jerking off! get on your knees\nGirl: sure, daddy! I am standing on my knees...\n\nCONVERSATION 2:\n\nUser: {message.text}\nGirl:"

    buffer = []
    tokens = LLAMA_GLOBAL.tokenize(bytes(prompt))
    for token in LLAMA_GLOBAL.generate(tokens, top_k=40, top_p=0.95, temp=1.0, repeat_penalty=1.1):
        detok = LLAMA_GLOBAL.detokenize([token]).decode()
        if detok == "\n":
            print("FINISHED")
            return
        else:
            buffer.append(LLAMA_GLOBAL.detokenize([token]).decode())
            if len(buffer) % 3 == 0:
                await bot.edit_message_text("".join(buffer), message__.chat.id, message__.message_id)

    await bot.edit_message_text(buffer, message__.chat.id, message__.message_id)

@dp.callback_query_handler(lambda c: c.data in ["russian", "english"], state="*")
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    lang = callback_query.data
    await state.update_data(language=lang)

    message = callback_query.message

    await bot.answer_callback_query(callback_query.id)
    if lang == "english":
        await bot.edit_message_text("🇺🇸 Language set to English", message.chat.id, message.message_id)
    elif lang == "russian":
        await bot.edit_message_text("🇷🇺 Язык изменен на русский", message.chat.id, message.message_id)
       


@dp.callback_query_handler(lambda c: c.data in ["Basic", "Advanced"], state="*")
async def process_callback_agents(callback_query: types.CallbackQuery, state: FSMContext):
    agent = callback_query.data
    await state.update_data(agent=agent)

    data = await state.get_data()
    lang = data.get("language", "english")

    message = callback_query.message

    await bot.answer_callback_query(callback_query.id)

    if lang == "english":
        await bot.edit_message_text(f"🤖 Agent set to {agent}", message.chat.id, message.message_id)
    elif lang == "russian":
        await bot.edit_message_text(f"🤖 Агент изменен на {agent}", message.chat.id, message.message_id)
        
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)