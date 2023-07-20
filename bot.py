__import__('pysqlite3')
import sys
import os
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup

from prompts import *
from embeddings import search
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory


bot = Bot(token="6321687305:AAGQRd_nlp6CFO44gaq_xrqptWSqtdyW040") # prod
# bot = Bot(token="5912125528:AAEWo482msjZfIoZ4SegsaGx_w0R9nQ0lc8") # test

dp = Dispatcher(bot, storage=MemoryStorage())

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

@dp.message_handler(Command('style'), state="*")
async def style_handler(message: types.Message, state: FSMContext):
    agents = ["Formal", "Casual", "Friendly", "Assertive"]
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = [types.InlineKeyboardButton(agent, callback_data=agent) for agent in agents]
    keyboard.add(*buttons)

    data = await state.get_data()
    lang = data.get("language", "english")

    if lang == "english":
        await bot.send_message(message.chat.id, "🤖 Choose a converstaion style:", reply_markup=keyboard)
    elif lang == "russian":
        await bot.send_message(message.chat.id, "🤖 Выберите стиль диалога:", reply_markup=keyboard)


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
        await message.answer("***⚙️ Commands:***\n\n/new - Start new conversation.\n/agents - Choose an agent\n/language - Choose a language\n/style - Choose dialogue style", parse_mode="Markdown")
    elif lang == "russian":
        await message.answer("***⚙️ Команды:***\n\n/new - Начать новый диалог.\n/agents - Выбрать агента\n/language - Выбрать язык\n/style - Выбрать стиль общения", parse_mode="Markdown")

@dp.message_handler(Command('new'), state="*")
async def begin_conversation(message: types.Message, state: FSMContext):

    await StateMachine.CHAT.set()
    data = await state.get_data()
    lang = data.get("language", "english")
    agent = data.get("agent", "Basic")
    dialogue_style = data.get("style", "Formal")

    if lang == "english":
        message__ = await message.answer("⚡️ Starting new conversation...")
    elif lang == "russian":
        message__ = await message.answer("⚡️ Начинаю новый диалог...")

    # SYSTEM_PROMPT = PROMPT_2.format(company_name="Сбербанк", company_business="банковские услуги", company_values="высокое качество обслуживания", conversation_purpose="продать кредит", conversation_type="telegram chat")
    SYSTEM_PROMPT = PROMPT_2.format(company_name="Аскона", company_business="продажа матрасов", company_values="высокое качество обслуживания", conversation_purpose="продать матрас", conversation_type="telegram chat")

    if dialogue_style == "Formal":
        full_prompt = SYSTEM_PROMPT + FORMAL_DIALOGUE
    elif dialogue_style == "Casual":
        full_prompt = SYSTEM_PROMPT + CASUAL_DIALOGUE
    elif dialogue_style == "Friendly":
        full_prompt = SYSTEM_PROMPT + FRIENDLY_DIALOGUE
    elif dialogue_style == "Assertive":
        full_prompt = SYSTEM_PROMPT + ASSERTIVE_DIALOGUE


    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            full_prompt
        ),
        SystemMessagePromptTemplate.from_template(
            f"Customer name is {message.from_user.first_name}. Initiate conversation in {lang}. Remember that you need to sell a product to the customer."
        ),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])

    print(prompt)

    if agent == "Basic":
        llm = ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo")
    elif agent == "Advanced":
        llm = ChatOpenAI(temperature=0.3, model="gpt-4")

    memory = ConversationBufferMemory(return_messages=True)
    conversation = ConversationChain(memory=memory, prompt=prompt, llm=llm)
    response = conversation.predict(input="Write first message to customer:")
    response = response.replace("M:", "")

    await state.update_data(chat_memory=memory)

    # update message with new response
    await bot.edit_message_text(response, message__.chat.id, message__.message_id)


@dp.message_handler(lambda message: message.text, state=StateMachine.CHAT)
async def conversation_handler(message: types.Message, state: FSMContext):

    data = await state.get_data()
    lang = data.get("language", "english")
    agent = data.get("agent", "Basic")
    dialogue_style = data.get("style", "Formal")

    SYSTEM_PROMPT = PROMPT_2.format(company_name="Аскона", company_business="продажа матрасов", company_values="высокое качество обслуживания", conversation_purpose="продать матрас", conversation_type="telegram chat")

    if dialogue_style == "Formal":
        full_prompt = SYSTEM_PROMPT + FORMAL_DIALOGUE
    elif dialogue_style == "Casual":
        full_prompt = SYSTEM_PROMPT + CASUAL_DIALOGUE
    elif dialogue_style == "Friendly":
        full_prompt = SYSTEM_PROMPT + FRIENDLY_DIALOGUE
    elif dialogue_style == "Assertive":
        full_prompt = SYSTEM_PROMPT + ASSERTIVE_DIALOGUE

    if lang == "english":
        message__ = await message.answer("🌀 Bot is typing...")
    elif lang == "russian":
        message__ = await message.answer("🌀 Бот печатает...")

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            full_prompt 
        ),
        # SystemMessagePromptTemplate.from_template(
        #     f"Knowledge base search results:\n{search(message.text)}"
        # ),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])

    print("FULL PROMPT FOR SECOND : \n\n\n")
    print(prompt)

    if agent == "Basic":
        llm = ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo")
    elif agent == "Advanced":
        llm = ChatOpenAI(temperature=0.3, model="gpt-4")

    # get state data
    data = await state.get_data()

    # get chat memory
    memory = data.get("chat_memory")
    if memory is None:
        memory = ConversationBufferMemory(return_messages=True)
    else:
        print("Memory loaded", memory)

    conversation = ConversationChain(memory=memory, prompt=prompt, llm=llm)
    response = conversation.predict(input=message.text)
    response = response.replace("M:", "")

    await state.update_data(chat_memory=memory)
    await bot.edit_message_text(response, message__.chat.id, message__.message_id)

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
        

@dp.callback_query_handler(lambda c: c.data in ["Formal", "Casual", "Friendly", "Assertive"], state="*")
async def process_callback_dialogue(callback_query: types.CallbackQuery, state: FSMContext):
    dialogue = callback_query.data
    await state.update_data(style=dialogue)

    message = callback_query.message

    data = await state.get_data()
    lang = data.get("language", "english")

    await bot.answer_callback_query(callback_query.id)
    if lang == "english":
        await bot.edit_message_text(f"🗣 Style set to {dialogue}", message.chat.id, message.message_id)
    elif lang == "russian":
        await bot.edit_message_text(f"🗣 Стиль изменен на {dialogue}", message.chat.id, message.message_id)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)
