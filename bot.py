from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup

from prompts import *
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

@dp.message_handler(Command('girls'), state="*")
async def agents_handler(message: types.Message, state: FSMContext):
    agents = ["Lisa (18, EN)", "Лера (16, RU)"]
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = [types.InlineKeyboardButton(agent, callback_data=agent) for agent in agents]
    keyboard.add(*buttons)

    data = await state.get_data()
    lang = data.get("language", "english")

    if lang == "english":
        await bot.send_message(message.chat.id, "🤖 Choose a girl:", reply_markup=keyboard)
    elif lang == "russian":
        await bot.send_message(message.chat.id, "🤖 Выберите модель:", reply_markup=keyboard)

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
        await message.answer("***⚙️ Commands:***\n\n/new - Start new conversation.\n/girls - Choose a girl\n/language - Choose a language", parse_mode="Markdown")
    elif lang == "russian":
        await message.answer("***⚙️ Команды:***\n\n/new - Начать новый диалог.\n/girls - Выбрать модель\n/language - Выбрать язык", parse_mode="Markdown")

@dp.message_handler(Command('new'), state="*")
async def begin_conversation(message: types.Message, state: FSMContext):

    await StateMachine.CHAT.set()
    data = await state.get_data()
    lang = data.get("language", "english")
    

    if lang == "english":
        message__ = await message.answer("⚡️ Starting new conversation...")
        SYSTEM_PROMPT = PORN_LLAMA_EN + " Hi babe\nGirl:"
    elif lang == "russian":
        message__ = await message.answer("⚡️ Начинаю новый диалог...")
        SYSTEM_PROMPT = PORN_LLAMA_RU + " Привет, малышка\nGirl:"

    buffer = []
    tokens = LLAMA_GLOBAL.tokenize(SYSTEM_PROMPT.encode("utf-8"))
    for token in LLAMA_GLOBAL.generate(tokens, top_k=40, top_p=0.95, temp=1.0, repeat_penalty=1.1):
        detok = LLAMA_GLOBAL.detokenize([token]).decode()
        if detok == "\n":
            print("FINISHED")
            await bot.edit_message_text("".join(buffer), message__.chat.id, message__.message_id)
            return
        else:
            buffer.append(LLAMA_GLOBAL.detokenize([token]).decode())
            if len(buffer) % 3 == 0:
                await bot.edit_message_text("".join(buffer), message__.chat.id, message__.message_id)

@dp.message_handler(lambda message: message.text, state=StateMachine.CHAT)
async def conversation_handler(message: types.Message, state: FSMContext):

    data = await state.get_data()
    lang = data.get("language", "english")

    if lang == "english":
        message__ = await message.answer("💋 Hoe is typing...")
        SYSTEM_PROMPT = PORN_LLAMA_EN + message.text + "\nGirl:"
    elif lang == "russian":
        message__ = await message.answer("💋 Шкура пишет...")
        SYSTEM_PROMPT = PORN_LLAMA_RU + message.text + "\nGirl:"

    buffer = []
    tokens = LLAMA_GLOBAL.tokenize(SYSTEM_PROMPT.encode("utf-8"))
    for token in LLAMA_GLOBAL.generate(tokens, top_k=40, top_p=0.95, temp=1.0, repeat_penalty=1.1):
        detok = LLAMA_GLOBAL.detokenize([token]).decode()
        if detok == "\n":
            print("FINISHED")
            await bot.edit_message_text("".join(buffer), message__.chat.id, message__.message_id)
            return
        else:
            buffer.append(LLAMA_GLOBAL.detokenize([token]).decode())
            if len(buffer) % 3 == 0:
                await bot.edit_message_text("".join(buffer), message__.chat.id, message__.message_id)

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