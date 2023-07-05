from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup

from prompts import *
import re
from llama_cpp import Llama

STOP_TOKENS = ["\n", "#", " #", "# "]

# bot = Bot(token="6321687305:AAGQRd_nlp6CFO44gaq_xrqptWSqtdyW040") # prod
bot = Bot(token="5912125528:AAEWo482msjZfIoZ4SegsaGx_w0R9nQ0lc8") # test
dp = Dispatcher(bot, storage=MemoryStorage())
LLAMA_GLOBAL = Llama(model_path="/airoboros-65b-gpt4-1.4.ggmlv3.q4_K_M.bin", n_gpu_layers=83, seed=-1)

class StateMachine(StatesGroup):
    MAIN_MENU = State()
    CHAT = State()

@dp.message_handler(Command('girls'), state="*")
async def agents_handler(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = [
        types.InlineKeyboardButton("Lisa (18, EN)", callback_data="lisa"),
        types.InlineKeyboardButton("Маша (16, RU)", callback_data="maha")
    ]
    keyboard.add(*buttons)

    data = await state.get_data()
    lang = data.get("language", "english")

    if lang == "english":
        await bot.send_message(message.chat.id, "🤖 Choose a hoe:", reply_markup=keyboard)
    elif lang == "russian":
        await bot.send_message(message.chat.id, "🤖 Выберите девочку:", reply_markup=keyboard)

@dp.message_handler(Command('sampling'), state="*")
async def agents_handler(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = [
        types.InlineKeyboardButton("Top K", callback_data="topk"),
        types.InlineKeyboardButton("Mirostat V2", callback_data="mirostat")
    ]
    keyboard.add(*buttons)

    data = await state.get_data()
    lang = data.get("language", "english")

    if lang == "english":
        await bot.send_message(message.chat.id, "🎛 Choose a sampling method:", reply_markup=keyboard)
    elif lang == "russian":
        await bot.send_message(message.chat.id, "🎛 Выберите метод семплинга:", reply_markup=keyboard)


# @dp.message_handler(Command('language'), state="*")
# async def settings_handler(message: types.Message, state: FSMContext):
#     keyboard = types.InlineKeyboardMarkup(row_width=1)
#     buttons = [
#         types.InlineKeyboardButton("🇷🇺 RU", callback_data="russian"),
#         types.InlineKeyboardButton("🇺🇸 EN", callback_data="english")
#     ]
#     keyboard.add(*buttons)

#     data = await state.get_data()
#     lang = data.get("language", "english")

#     if lang == "english":
#         await message.answer("Choose a language:", reply_markup=keyboard)
#     elif lang == "russian":
#         await message.answer("Выберите язык:", reply_markup=keyboard)

@dp.message_handler(Command('start'), state="*")
async def start_command(message: types.Message, state: FSMContext):
    await StateMachine.MAIN_MENU.set()

    data = await state.get_data()
    lang = data.get("language", "english")
    await state.update_data(chat_memory=None)

    if lang == "english":
        await message.answer("***⚙️ Commands:***\n\n/new - Start new conversation.\n/girls - choose a hoe\n/sampling - choose topk or mirostat sampling", parse_mode="Markdown")
    elif lang == "russian":
        await message.answer("***⚙️ Команды:***\n\n/new - Начать новый диалог.\n/girls - выбрать модель\n/sampling - выбрать topk или mirostat sampling", parse_mode="Markdown")

@dp.message_handler(Command('new'), state="*")
async def begin_conversation(message: types.Message, state: FSMContext):

    await StateMachine.CHAT.set()
    data = await state.get_data()
    lang = data.get("language", "english")
    girl = data.get("girl", "lisa")
    sampling = data.get("sampling", "top_k")

    await state.update_data(chat_memory="")
    
    if lang == "english":
        message__ = await message.answer("⚡️ Conversation history deleted. Starting new conversation...")
        init_message = "User: Hi babe\nGirl:"

        if girl == "lisa":
            formatted_prompt = PORN_LLAMA_EN.format(bio=LISA_BIO, name="Lisa")
        elif girl == "maha":
            formatted_prompt = PORN_LLAMA_EN.format(bio=MAHA_BIO, name="Masha")

        SYSTEM_PROMPT = formatted_prompt + init_message
    elif lang == "russian":
        message__ = await message.answer("⚡️ История диалога удалена. Начинаю новый диалог...")
        init_message = "User: Привет, малышка\nGirl:"

        if girl == "lisa":
            formatted_prompt = PORN_LLAMA_EN.format(bio=LISA_BIO, name="Лиза")
        elif girl == "maha":
            formatted_prompt = PORN_LLAMA_EN.format(bio=MAHA_BIO, name="Маша")

        SYSTEM_PROMPT = formatted_prompt + init_message

    buffer = []
    tokens = LLAMA_GLOBAL.tokenize(SYSTEM_PROMPT.encode("utf-8"))

    if sampling == "top_k":
        kwargs = {"tokens" : tokens, "top_k" : 40, "top_p" : 0.95, "temp" : 0.4, "repeat_penalty" : 1.1}
    else:
        kwargs = {"tokens" : tokens, "mirostat_mode" : 2, "temp" : 0.4}

    print("SAMPLING: ", kwargs)

    for token in LLAMA_GLOBAL.generate(**kwargs):
        detok = LLAMA_GLOBAL.detokenize([token]).decode()
        if detok in STOP_TOKENS:
            print("FINISHED REASON ", detok)
            await bot.edit_message_text("".join(buffer), message__.chat.id, message__.message_id)
            await state.update_data(chat_memory=init_message + "".join(buffer) + "\n")
            return
        else:
            buffer.append(LLAMA_GLOBAL.detokenize([token]).decode())
            if len(buffer) % 3 == 0:
                await bot.edit_message_text("".join(buffer), message__.chat.id, message__.message_id)

    await state.update_data(chat_memory=init_message + "".join(buffer) + "\n")

@dp.message_handler(lambda message: message.text, state=StateMachine.CHAT)
async def conversation_handler(message: types.Message, state: FSMContext):

    data = await state.get_data()
    lang = data.get("language", "english")
    memory = data.get("chat_memory", None)
    girl = data.get("girl", "lisa")
    sampling = data.get("sampling", "top_k")

    if lang == "english":
        message__ = await message.answer("💋 Hoe is typing...")

        if girl == "lisa":
            formatted_prompt = PORN_LLAMA_EN.format(bio=LISA_BIO, name="Lisa")
        elif girl == "maha":
            formatted_prompt = PORN_LLAMA_EN.format(bio=MAHA_BIO, name="Masha")

        SYSTEM_PROMPT = formatted_prompt + memory + "User: " + message.text + "\nGirl:"
    elif lang == "russian":
        message__ = await message.answer("💋 Шкура пишет...")

        if girl == "lisa":
            formatted_prompt = PORN_LLAMA_EN.format(bio=LISA_BIO, name="Лиза")
        elif girl == "maha":
            formatted_prompt = PORN_LLAMA_EN.format(bio=MAHA_BIO, name="Маша")

        SYSTEM_PROMPT = formatted_prompt + memory + "User: " +  message.text + "\nGirl:"

    print("SYSTEM PROMPT \n\n", SYSTEM_PROMPT)

    buffer = []
    tokens = LLAMA_GLOBAL.tokenize(SYSTEM_PROMPT.encode("utf-8"))

    if sampling == "top_k":
        kwargs = {"tokens" : tokens, "top_k" : 40, "top_p" : 0.95, "temp" : 0.4, "repeat_penalty" : 1.1}
    else:
        kwargs = {"tokens" : tokens, "mirostat_mode" : 2, "temp" : 0.4}
    
    for token in LLAMA_GLOBAL.generate(**kwargs):
        detok = LLAMA_GLOBAL.detokenize([token]).decode()
        if detok in STOP_TOKENS:
            print("FINISHED REASON ", detok)

            msg = "".join(buffer)
            msg_clean = re.sub(r"\[.]", "", msg)

            await bot.edit_message_text(msg_clean, message__.chat.id, message__.message_id)

            if "[1]" in msg:
                await bot.send_photo(message__.chat.id, open("pussy/1.jpg", "rb"))
            elif "[2]" in msg:
                await bot.send_photo(message__.chat.id, open("ass/1.jpg", "rb"))
            elif "[3]" in msg:
                await bot.send_photo(message__.chat.id, open("tits/1.jpg", "rb"))
            elif "[P]" in msg:
                keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
                buttons = [
                    types.InlineKeyboardButton("✅ Pay now", callback_data="payment"),
                ]
                keyboard.add(*buttons)
                await bot.send_message(message.chat.id, "Payment event triggered", reply_markup=keyboard)

            memory += "User: " + message.text + "\nGirl:" + "".join(buffer) + "\n"
            await state.update_data(chat_memory=memory)
            return
        else:
            buffer.append(LLAMA_GLOBAL.detokenize([token]).decode())
            if len(buffer) % 3 == 0:

                msg = "".join(buffer)
                msg_clean = re.sub(r"\[.]", "", msg)

                if "[1]" in msg:
                    await bot.send_photo(message__.chat.id, open("pussy/1.jpg", "rb"))
                elif "[2]" in msg:
                    await bot.send_photo(message__.chat.id, open("ass/1.jpg", "rb"))
                elif "[3]" in msg:
                    await bot.send_photo(message__.chat.id, open("tits/1.jpg", "rb"))
                elif "[P]" in msg:
                    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
                    buttons = [
                        types.InlineKeyboardButton("✅ Pay now", callback_data="payment"),
                    ]
                    keyboard.add(*buttons)
                    await bot.send_message(message.chat.id, "Payment event triggered", reply_markup=keyboard)

                await bot.edit_message_text(msg_clean, message__.chat.id, message__.message_id)

    memory += "User: " + message.text + "\nGirl:" + "".join(buffer) + "\n"
    await state.update_data(chat_memory=memory)


@dp.message_handler(lambda message: message.text, state="*")
async def conversation_handler_raw(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "english")

    if lang == "english":
        await message.answer("🤖 Use /new command to start a new conversation")
    elif lang == "russian":
        await message.answer("🤖 Используйте команду /new чтобы начать новый диалог")


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
       

@dp.callback_query_handler(lambda c: c.data in ["mirostat", "topk"], state="*")
async def process_callback_sampling(callback_query: types.CallbackQuery, state: FSMContext):
    method = callback_query.data
    data = await state.get_data()
    lang = data.get("language", "english")

    await state.update_data(sampling=method)

    message = callback_query.message

    await bot.answer_callback_query(callback_query.id)
    if lang == "english":
        await bot.edit_message_text(f"✅ Sampling set to {method}", message.chat.id, message.message_id)
    elif lang == "russian":
        await bot.edit_message_text(f"✅ Семплинг изменен на {method}", message.chat.id, message.message_id)

@dp.callback_query_handler(lambda c: c.data in ["maha", "lisa"], state="*")
async def process_callback_agents(callback_query: types.CallbackQuery, state: FSMContext):
    agent = callback_query.data
    await state.update_data(girl=agent)

    data = await state.get_data()
    lang = data.get("language", "english")

    message = callback_query.message

    await bot.answer_callback_query(callback_query.id)

    if lang == "english":
        await bot.edit_message_text(f"🤖 Hoe set to {agent}", message.chat.id, message.message_id)
    elif lang == "russian":
        await bot.edit_message_text(f"🤖 Модель изменена на {agent}", message.chat.id, message.message_id)


@dp.callback_query_handler(lambda c: c.data in ["payment"], state="*")
async def process_callback_agents(callback_query: types.CallbackQuery, state: FSMContext):
    message = callback_query.message

    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(f"💰 Payment simulated", message.chat.id, message.message_id)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)