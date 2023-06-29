from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup

from prompts import SYSTEM_PROMPT
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

bot = Bot(token="5828347904:AAFP4uv7X1mkRWC4bamYL-ezGQswnyO2hNk")
dp = Dispatcher(bot, storage=MemoryStorage())

MODEL = "gpt-4" # gpt-3.5-turbo 

class StateMachine(StatesGroup):
    MAIN_MENU = State()
    CHAT = State()

@dp.message_handler(Command('start'))
async def start_command(message: types.Message, state: FSMContext):
    await StateMachine.MAIN_MENU.set()
    await state.update_data(chat_memory=None)
    await message.answer("***⚙️ Commands:***\n\n/new - Start new conversation.\n/agents - Choose an agent\n/settings - Choose a language", parse_mode="Markdown")

@dp.message_handler(Command('new'))
async def begin_conversation(message: types.Message, state: FSMContext):

    await StateMachine.CHAT.set()
    data = await state.get_data()
    lang = data.get("language", "english")

    message = await message.answer("⚡️ Starting new conversation...")

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            SYSTEM_PROMPT
        ),
        SystemMessagePromptTemplate.from_template(
            f"Your customer name is {message.from_user.first_name}. Generate first message in {lang}."
        ),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])

    llm = ChatOpenAI(temperature=0, model=MODEL)
    memory = ConversationBufferMemory(return_messages=True)
    conversation = ConversationChain(memory=memory, prompt=prompt, llm=llm)
    response = conversation.predict(input="Hi")

    await state.update_data(chat_memory=memory)

    # update message with new response
    await bot.edit_message_text(response, message.chat.id, message.message_id)


@dp.message_handler(lambda message: message.text, state=StateMachine.MAIN_MENU)
async def conversation_handler(message: types.Message, state: FSMContext):
    await message.answer("Please use /new command to start a new conversation.")


@dp.message_handler(lambda message: message.text, state=StateMachine.CHAT)
async def conversation_handler(message: types.Message, state: FSMContext):

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            SYSTEM_PROMPT
        ),
        SystemMessagePromptTemplate.from_template(
            f"Your customer name is {message.from_user.first_name}."
        ),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])

    llm = ChatOpenAI(temperature=0, model=MODEL)

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

    await state.update_data(chat_memory=memory)
    await message.answer(response)

@dp.message_handler(Command('agents'))
async def agents_handler(message: types.Message):
    agents = ["Agent 1", "Agent 2", "Agent 3"]
    keyboard = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(agent, callback_data=agent) for agent in agents]
    keyboard.add(*buttons)
    await bot.send_message(message.chat.id, "Choose an agent:", reply_markup=keyboard)

@dp.message_handler(Command('settings'))
async def settings_handler(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton("RU", callback_data="russian"),
        types.InlineKeyboardButton("EN", callback_data="english")
    ]
    keyboard.add(*buttons)
    await message.answer("Choose a language:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in ["russian", "english"])
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    lang = callback_query.data
    await state.update_data(language=lang)

    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f"Language set to {lang.upper()}")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)