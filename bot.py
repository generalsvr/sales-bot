from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup

from prompts import *
import re
from llama_cpp import Llama
import json

from googletrans import Translator
translator = Translator()

STOP_TOKENS = ["\n", "#", " #", "# "]

# bot = Bot(token="6321687305:AAGQRd_nlp6CFO44gaq_xrqptWSqtdyW040") # prod
bot = Bot(token="6440607788:AAGKXiEmguhZNv0rg6gS7qOktdiGr2a8S4k") # sexting
dp = Dispatcher(bot, storage=MemoryStorage())
LLAMA_GLOBAL = Llama(model_path="/root/nous-hermes-llama2-13B.gguf.q5_K_M.bin", n_gpu_layers=43, seed=-1, n_ctx=1536)

class StateMachine(StatesGroup):
    MAIN_MENU = State()
    CHAT = State()

@dp.message_handler(Command('girls'), state="*")
async def agents_handler(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = [
        types.InlineKeyboardButton("Lisa (18)", callback_data="lisa"),
        types.InlineKeyboardButton("Маша (16)", callback_data="maha")
    ]
    keyboard.add(*buttons)

    data = await state.get_data()
    lang = data.get("language", "english")

    if lang == "english":
        await bot.send_message(message.chat.id, "🤖 Choose a hoe:", reply_markup=keyboard)
    elif lang == "russian":
        await bot.send_message(message.chat.id, "🤖 Выберите девочку:", reply_markup=keyboard)

# @dp.message_handler(Command('sampling'), state="*")
# async def agents_handler(message: types.Message, state: FSMContext):
#     keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
#     buttons = [
#         types.InlineKeyboardButton("Top K", callback_data="topk"),
#         types.InlineKeyboardButton("Mirostat V2", callback_data="mirostat")
#     ]
#     keyboard.add(*buttons)

#     data = await state.get_data()
#     lang = data.get("language", "english")

#     if lang == "english":
#         await bot.send_message(message.chat.id, "🎛 Choose a sampling method:", reply_markup=keyboard)
#     elif lang == "russian":
#         await bot.send_message(message.chat.id, "🎛 Выберите метод семплинга:", reply_markup=keyboard)


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

    await message.answer("***⚙️ Как пользоваться:***\n\n/new - Начать новый диалог. Удаляет польностью историю чата. Девочка пишет привет первая\n\n❗️ Сейчас стоит небольшая моделька, которую надо еще дообучать. Цель этого демо - показать примерные способности AI в области sexting.\n\nПосле дообучения модели будет добавлена способность посылать фото (заранее заготовленные)", parse_mode="Markdown")

    # if lang == "english":
    #     await message.answer("***⚙️ Commands:***\n\n/new - Start new conversation.\n/girls - choose a hoe", parse_mode="Markdown")
    # elif lang == "russian":
    #     await message.answer("***⚙️ Команды:***\n\n/new - Начать новый диалог.\n/girls - выбрать модель", parse_mode="Markdown")

@dp.message_handler(Command('new'), state="*")
async def begin_conversation(message: types.Message, state: FSMContext):

    await StateMachine.CHAT.set()
    data = await state.get_data()
    lang = data.get("language", "english")
    girl = data.get("girl", "lisa")
    sampling = data.get("sampling", "top_k")

    await state.update_data(chat_memory="")

    init_message = "User: hi sweet kitty 😘\nGirl:"

    if girl == "lisa":
        formatted_prompt = PORN_LLAMA_EN.format(bio=LISA_BIO, name="Lisa")
    elif girl == "maha":
        formatted_prompt = PORN_LLAMA_EN.format(bio=MAHA_BIO, name="Masha")

    if lang == "english":
        message__ = await message.answer("⚡️ Conversation history deleted. Starting new conversation...")    
    elif lang == "russian":
        message__ = await message.answer("⚡️ История диалога удалена. Начинаю новый диалог...")

    SYSTEM_PROMPT = formatted_prompt + init_message

    buffer = []
    if sampling == "top_k":
        kwargs = {"prompt" : SYSTEM_PROMPT, "top_k" : 40, "top_p" : 0.95, "temperature" : 0.4, "repeat_penalty" : 1.1, "stream" : True, "max_tokens" : 128}
    else:
        kwargs = {"prompt" : SYSTEM_PROMPT, "mirostat_mode" : 2, "temp" : 0.4, "stream" : True, "max_tokens" : 128}

    for token in LLAMA_GLOBAL.create_completion(**kwargs):
        detok = token["choices"][0]["text"]
        if detok in STOP_TOKENS:
            print("FINISHED REASON ", detok)
            try:
                await bot.edit_message_text("".join(buffer), message__.chat.id, message__.message_id)
            except:
                pass
            await state.update_data(chat_memory=init_message + "".join(buffer) + "\n")
            return
        else:
            buffer.append(detok)
            if len(buffer) % 3 == 0:
                try:
                    await bot.edit_message_text("".join(buffer), message__.chat.id, message__.message_id)
                except:
                    pass

    await state.update_data(chat_memory=init_message + "".join(buffer) + "\n")


@dp.message_handler(Command('gen_data'), state="*")
async def begin_conversation_gen(message: types.Message, state: FSMContext):
    buffer = []
    kwargs = {"prompt" : PORN_LLAMA_EN, "mirostat_mode" : 2, "temperature" : 0.4, "stream" : True, "max_tokens" : 1024}
    # good or bad conversation keyboard
    buttons = [
        types.InlineKeyboardButton("👍 Good", callback_data="good"),
        types.InlineKeyboardButton("👎 Bad", callback_data="bad")
    ]
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(*buttons)

    await message.answer("🤖 Генерируем диалог (пару минут)...")

    for token in LLAMA_GLOBAL.create_completion(**kwargs):
        detok = token["choices"][0]["text"]
        buffer.append(detok)

    await state.update_data(data_gen="".join(buffer))
    await bot.send_message(message.chat.id, "".join(buffer), reply_markup=keyboard)
        

# callback for good or bad conversation
@dp.callback_query_handler(lambda c: c.data in ["good", "bad"], state="*")
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    # save data to file if good as jsonl {"text" : "User: ... \nGirl: ..."}
    data = await state.get_data()
    data_gen = data.get("data_gen")
    
    if callback_query.data == "good":
        jsonl = {"text" : data_gen}
        with open("good.jsonl", "a") as f:
            f.write(json.dumps(jsonl) + "\n")
    elif callback_query.data == "bad":
        jsonl = {"text" : data_gen}
        with open("bad.jsonl", "a") as f:
            f.write(json.dumps(jsonl) + "\n") 

    
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text("✅ Saved", callback_query.message.chat.id, callback_query.message.message_id)

@dp.message_handler(lambda message: message.text, state="*")
async def conversation_handler(message: types.Message, state: FSMContext):

    data = await state.get_data()
    lang = data.get("language", "english")
    memory = data.get("chat_memory")
    girl = data.get("girl", "lisa")
    sampling = data.get("sampling", "top_k")

    if not memory:
        memory = ""
        print("MEMORY IS NONE")

    if girl == "lisa":
        formatted_prompt = PORN_LLAMA_EN.format(bio=LISA_BIO, name="Lisa")
    elif girl == "maha":
        formatted_prompt = PORN_LLAMA_EN.format(bio=MAHA_BIO, name="Masha")

    if lang == "english":
        message__ = await message.answer("💋 Hoe is typing...")
    elif lang == "russian":
        message__ = await message.answer("💋 Шкура пишет...")

    SYSTEM_PROMPT = formatted_prompt + memory + "User: " +  message.text.lower() + "\nGirl:"

    print("SYSTEM PROMPT \n\n", SYSTEM_PROMPT)

    buffer = ""
    if sampling == "top_k":
        kwargs = {"prompt" : SYSTEM_PROMPT, "top_k" : 40, "top_p" : 0.95, "temperature" : 0.4, "repeat_penalty" : 1.1, "stream" : True}
    else:
        kwargs = {"prompt" : SYSTEM_PROMPT, "mirostat_mode" : 2, "temp" : 0.4, "stream" : True}

    for token in LLAMA_GLOBAL.create_completion(**kwargs):
        detok = token["choices"][0]["text"]
        if detok in STOP_TOKENS:
            print("FINISHED REASON ", detok)

            memory += "User: " + message.text + "\nGirl:" + buffer + "\n"
            await state.update_data(chat_memory=memory)

            msg_clean = re.sub(r"\[.]", "", buffer)

            if "[1]" in buffer:
                await bot.send_photo(message__.chat.id, open("pussy/1.jpg", "rb"))
            elif "[2]" in buffer:
                await bot.send_photo(message__.chat.id, open("ass/1.jpg", "rb"))
            elif "[3]" in buffer:
                await bot.send_photo(message__.chat.id, open("tits/1.jpg", "rb"))
            elif "[4]" in buffer:
                await bot.send_photo(message__.chat.id, open("legs/1.jpg", "rb"))
            elif "[P]" in buffer:
                keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
                buttons = [
                    types.InlineKeyboardButton("✅ Pay now", callback_data="payment"),
                ]
                keyboard.add(*buttons)
                await bot.send_message(message.chat.id, "Payment event triggered", reply_markup=keyboard)

            if lang == "english":
                await bot.edit_message_text(msg_clean, message__.chat.id, message__.message_id)
            elif lang == "russian":
                ru_text = translator.translate(msg_clean, src='en', dest='ru').text
                await bot.edit_message_text(ru_text, message__.chat.id, message__.message_id)

            return
        else:
            buffer += detok
            if len(buffer) % 3 == 0:
                try:
                    await bot.edit_message_text(buffer, message__.chat.id, message__.message_id)
                except:
                    pass


    memory += "User: " + message.text + "\nGirl:" + buffer + "\n"
    print("MEMORY: ", memory)
    await state.update_data(chat_memory=memory)

    if "[1]" in buffer:
        await bot.send_photo(message__.chat.id, open("pussy/1.jpg", "rb"))
    elif "[2]" in buffer:
        await bot.send_photo(message__.chat.id, open("ass/1.jpg", "rb"))
    elif "[3]" in buffer:
        await bot.send_photo(message__.chat.id, open("tits/1.jpg", "rb"))
    elif "[4]" in buffer:
        await bot.send_photo(message__.chat.id, open("legs/1.jpg", "rb"))
    elif "[P]" in buffer:
        keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
        buttons = [
            types.InlineKeyboardButton("✅ Pay now", callback_data="payment"),
        ]
        keyboard.add(*buttons)
        buffer = buffer.replace("[P]", "")
        await bot.send_message(message.chat.id, "Payment event triggered", reply_markup=keyboard)

    msg_clean = re.sub(r"\[.]", "", buffer)

    if lang == "english":
        await bot.edit_message_text(msg_clean, message__.chat.id, message__.message_id)
    elif lang == "russian":
        ru_text = translator.translate(msg_clean, src='en', dest='ru').text
        await bot.edit_message_text(ru_text, message__.chat.id, message__.message_id)


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
    await bot.edit_message_text(f"💰 Payment simulated (видео добавлю потом)", message.chat.id, message.message_id)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)