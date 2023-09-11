from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from elevenlabs import set_api_key
set_api_key("89af7bfee0e0611dd8ff4b60ebb8d0a1")

# from prompts import *
from llama_cpp import Llama
import os
from elevenlabs import generate
from pydub import AudioSegment

# sqlite 
import sqlite3
from sqlite3 import Error

# connect to database
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        print(sqlite3.version)
    except Error as e:
        print(e)
    return conn
    

conn = create_connection("bot.db")

# create tables
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, username TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS polls (poll_id INTEGER PRIMARY KEY, question TEXT, answer TEXT)")

SYSTEM_PROMPT_EN = """Below is the conversation between Indonesian politician Ganjar Pranowo and user. Ganjar answers are consice but informative. Language is English.

Ganjar Pranowo is a politician who served as Governor of Central Java for two terms from 2013 to 2023. He was previously a member of the People's Legislative Assembly from the PDI Perjuangan faction. He is also serving as Chairperson of the Gadjah Mada University Alumni Family and the Indonesian Regional Public Radio TV Association. Ganjar has been appointed by PDIP as a candidate for President of Indonesia in 2024. He was born to a simple family in a village on the slopes of Mount Lawu and has five siblings. He attended SMP Negeri 1 Kutoarjo and SMA Bopkri 1 Yogyakarta. Ganjar holds a master's degree in Political Science from the Faculty of Social and Political Sciences, University of Indonesia. He initially worked at an HRD consulting agency in Jakarta before choosing a career in politics through the PDI-P Party led by Megawati Sukarnoputri. Ganjar Pranowo, the Governor of Central Java, implemented several policies and initiatives during his leadership. He applied credit financing for MSMEs with low interest rates and no collateral or administration fees, controlled the distribution of gratuities in the government, initiated a zakat program for state civil servants, launched a disaster-resilient village formation program, planned to build a modern hospital, issued farmer cards to prevent abuse of authority, and took quick steps to handle the COVID-19 pandemic. Ganjar is considered a leader who works with heart for the benefit of society. Ganjar Pranowo is officially nominated as a candidate for President of Indonesia by Megawati Soekarnoputri in 2023. He is married to Siti Atikah Supriyanti and they have one son who is studying at UGM. Both Ganjar and Atikoh have a hobby of sports and often participate in marathon and bicycle activities. He is considered a religious figure and has a team of volunteers who donate loudspeakers to mosques and Islamic boarding schools. Ganjar is also working on the development of a halal hospital in Central Java and has received support from religious scholars.

"""

SYSTEM_PROMPT_ID = """Below is the conversation between Indonesian politician Ganjar Pranowo and user. Ganjar answers are consice but informative. Language is Indonesian.

Ganjar Pranowo is a politician who served as Governor of Central Java for two terms from 2013 to 2023. He was previously a member of the People's Legislative Assembly from the PDI Perjuangan faction. He is also serving as Chairperson of the Gadjah Mada University Alumni Family and the Indonesian Regional Public Radio TV Association. Ganjar has been appointed by PDIP as a candidate for President of Indonesia in 2024. He was born to a simple family in a village on the slopes of Mount Lawu and has five siblings. He attended SMP Negeri 1 Kutoarjo and SMA Bopkri 1 Yogyakarta. Ganjar holds a master's degree in Political Science from the Faculty of Social and Political Sciences, University of Indonesia. He initially worked at an HRD consulting agency in Jakarta before choosing a career in politics through the PDI-P Party led by Megawati Sukarnoputri. Ganjar Pranowo, the Governor of Central Java, implemented several policies and initiatives during his leadership. He applied credit financing for MSMEs with low interest rates and no collateral or administration fees, controlled the distribution of gratuities in the government, initiated a zakat program for state civil servants, launched a disaster-resilient village formation program, planned to build a modern hospital, issued farmer cards to prevent abuse of authority, and took quick steps to handle the COVID-19 pandemic. Ganjar is considered a leader who works with heart for the benefit of society. Ganjar Pranowo is officially nominated as a candidate for President of Indonesia by Megawati Soekarnoputri in 2023. He is married to Siti Atikah Supriyanti and they have one son who is studying at UGM. Both Ganjar and Atikoh have a hobby of sports and often participate in marathon and bicycle activities. He is considered a religious figure and has a team of volunteers who donate loudspeakers to mosques and Islamic boarding schools. Ganjar is also working on the development of a halal hospital in Central Java and has received support from religious scholars.

"""

LEGAL_NOTICE = """***Legal Notice***

This artificial intelligence (AI) bot, designed to represent Ganjar Pranowo, an illustrious politician from Indonesia. All interactions maintain a predictive modeling and not entirely accurate nature, and are exclusively based on publicly accessible information. As a result, this AI bot may occasionally generate misleading, incorrect, or incomplete information. Any errors, discrepancies or omissions should not be interpreted as a form of deception or misinformation.

This AI bot is a tool for casual and entertainment purposes only. It absolutely does not provide professional, legal, financial or medical advice. The bot's responsiveness should not be misconstrued as personal or professional counsel. Users are advised to consult a qualified professional for such advice. 

By utilizing this AI bot, users acknowledge respecting these terms and understanding that the information provided is impersonal and not adapted to any particular user’s needs or circumstances. 

The creators, owners, and operators of this AI bot disclaim any responsibilities for the losses, damages or inconveniences users may experience as a result of using the AI bot. They cannot be held accountable for any decision made or action taken based on interaction with the AI bot.

By engaging with the AI bot, users agree to this disclaimer and our terms and conditions in full. Users who do not agree to this legal notice should ideally refrain from using this bot. This disclaimer may be altered without notice, and it is the user's responsibility to periodically review this disclaimer."""

POLLS = [{"text" : "How important is freedom of press and speech to you?", "options" : ["Very important", "Important", "Neutral", "Not very important", "Not important at all"]},
         {"text" : "How would you rate the state of the Indonesian economy?", "options" : ["Excellent", "Good", "Fair", "Poor", "Very poor"]},
         {"text" : "Which economic issue concerns you the most?", "options" : ["Unemployment and job availability", "Inflation and rising costs of living", "Corruption and misuse of public funds", "Foreign investments and trade relations", "Income inequality and social welfare"]},
         {"text" : "How important is addressing social inequality in Indonesia?", "options" : ["Very important", "Important", "Neutral", "Not very important", "Not important at all"]},
         {"text" : "Which neighboring country should Indonesia prioritize in strengthening diplomatic and economic ties?", "options" : ["Singapore", "Malaysia", "Thailand", "Australia", "Philippines", "Others"]}]

# BOT_TOKEN = os.getenv("BOT_TOKEN")
# LLM_PATH = os.getenv("LLM_PATH")

BOT_TOKEN = "6664189228:AAHyW-N36MHWXyn5ekerbQCiTrGlR6TnRz8"
LLM_PATH = "/root/airoboros-l2-70b-2.1.Q4_K_M.gguf"

bot = Bot(token=BOT_TOKEN) # sexting
dp = Dispatcher(bot, storage=MemoryStorage())

STOP_TOKENS = ["\n", "#", " #", "# "]
LLAMA_GLOBAL = Llama(model_path=LLM_PATH, n_gpu_layers=83, seed=-1, n_ctx=4096)

from faster_whisper import WhisperModel
model_size = "small"

# Run on GPU with FP16
whisper = WhisperModel(model_size, device="cuda", compute_type="int8_float16")

def convert_ogg_to_mp3(ogg_file_path, mp3_file_path):
    sound = AudioSegment.from_ogg(ogg_file_path)
    sound.export(mp3_file_path, format="mp3")


@dp.message_handler(Command('start'), state="*")
async def start_command(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "english")

    # save new user to database if not exists
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (message.from_user.id,))
    rows = cur.fetchall()

    if len(rows) == 0:
        cur.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username))
        conn.commit()

    if lang == "english":
        await message.answer("<b>🇮🇩 Hello!</b>\n\nWelcome to your personal chat with Ganjar Pranowo, Ex-Governor of Central Java and upcoming Presidential Candidate for Indonesia 2024!\n\nAsk questions, gain insights, or discuss political issues directly with a leader who is ardently working for the development of society and the nation.", parse_mode="html")
    elif lang == "indonesian":
        await message.answer("<b>🇮🇩 Halo!</b>\n\nSelamat datang di obrolan pribadi Anda dengan Ganjar Pranowo, Mantan Gubernur Jawa Tengah dan Calon Presiden Indonesia 2024 yang akan datang!\n\nAjukan pertanyaan, dapatkan wawasan, atau bahas masalah politik langsung dengan seorang pemimpin yang dengan tekun bekerja untuk pembangunan masyarakat dan bangsa.", parse_mode="html")

    await state.update_data(chat_memory="")

# models command
@dp.message_handler(Command('models'), state="*")
async def models_handler(message: types.Message, state: FSMContext):
    # choose from GPT and Neyra Politics
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton("🤖 GPT", callback_data="gpt"),
        types.InlineKeyboardButton("🤖 Neyra Politics", callback_data="neyra")
    ]
    keyboard.add(*buttons)

    data = await state.get_data()
    lang = data.get("language", "english")

    if lang == "english":
        await message.answer("Choose a model", reply_markup=keyboard)
    elif lang == "indonesian":
        await message.answer("Pilih model", reply_markup=keyboard)

@dp.message_handler(Command('language'), state="*")
async def settings_handler(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton("🇮🇩 ID", callback_data="indonesian"),
        types.InlineKeyboardButton("🇺🇸 EN", callback_data="english")
    ]
    keyboard.add(*buttons)

    data = await state.get_data()
    lang = data.get("language", "english")

    if lang == "english":
        await message.answer("Choose a language:", reply_markup=keyboard)
    elif lang == "indonesian":
        await message.answer("Pilih bahasa:", reply_markup=keyboard)

# polls command
@dp.message_handler(Command('polls'), state="*")
async def polls_handler(message: types.Message, state: FSMContext):
    # send polls
    data = await state.get_data()
    lang = data.get("language", "english")
    await state.update_data(poll_index=0)

    for poll in POLLS:
        # send poll with custom id
        if lang == "english":
            poll = await message.answer_poll(question=poll["text"], options=poll["options"], is_anonymous=False)
        elif lang == "indonesian":
            poll = await message.answer_poll(question=poll["text"], options=poll["options"], is_anonymous=False)
        
        # save poll id to database
        cur = conn.cursor()
        cur.execute("INSERT INTO polls VALUES (?, ?, ?)", (poll.poll.id, poll.poll.question, ""))
        conn.commit()
        
# poll answer handler
@dp.poll_answer_handler()
async def poll_answer_handler(quiz_answer: types.PollAnswer):
    print(quiz_answer)

    # save answer to database
    cur = conn.cursor()
    cur.execute("UPDATE polls SET answer=? WHERE poll_id=?", (quiz_answer.option_ids[0], quiz_answer.poll_id))
    conn.commit()


# admin command
@dp.message_handler(Command('admin'), state="*")
async def admin_handler(message: types.Message, state: FSMContext):
    # show stats
    data = await state.get_data()
    lang = data.get("language", "english")
    
    
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    rows = cur.fetchall()

    # get polls stats
    cur.execute("SELECT COUNT(*) FROM poll_answers")
    rows2 = cur.fetchall()


    if lang == "english":
        await message.answer("📊 Statistics:\n\nTotal users: " + str(rows[0][0]) + "\nTotal poll answers: " + str(rows2[0][0]))
    elif lang == "indonesian":
        await message.answer("📊 Statistik:\n\nTotal pengguna: " + str(rows[0][0]) + "\nTotal jawaban polling: " + str(rows2[0][0]))

    

# legal command
@dp.message_handler(Command('legal'), state="*")
async def legal_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "english")

    if lang == "english":
        await message.answer(LEGAL_NOTICE, parse_mode="markdown")
    elif lang == "indonesian":
        await message.answer(LEGAL_NOTICE, parse_mode="markdown")

@dp.message_handler(lambda message: message.text, state="*")
async def new_command(message: types.Message, state: FSMContext):
    data = await state.get_data()

    lang = data.get("language", "english")
    memory = data.get("chat_memory", "")

    if lang == "english":
        message__ = await bot.send_message(message.chat.id, "📝 Ganjar is typing...")
    elif lang == "indonesian":
        message__ = await bot.send_message(message.chat.id, "📝 Ganjar sedang mengetik...")

    if lang == "english":
        prompt = SYSTEM_PROMPT_EN + memory + "User:" + message.text + "\nGanjar:"
    elif lang == "indonesian":
        prompt = SYSTEM_PROMPT_ID + memory + "User:" + message.text + "\nGanjar:"

    print("PROMPT: \n\n", prompt)

    buffer = []
    kwargs = {"prompt" : prompt, "top_k" : 40, "top_p" : 0.95, "temperature" : 0.4, "repeat_penalty" : 1.1, "stream" : True, "max_tokens" : 256}

    for token in LLAMA_GLOBAL.create_completion(**kwargs):
        detok = token["choices"][0]["text"]
        if detok in STOP_TOKENS:
            print("FINISHED REASON ", detok)
            try:
                await bot.edit_message_text("".join(buffer), message__.chat.id, message__.message_id)
            except:
                pass
            await state.update_data(chat_memory=memory + "User:" +  message.text + "\nGanjar:" + "".join(buffer) + "\n")
            audio = generate(
                text="".join(buffer),
                voice="lhG8PEIXIoYq5B4mcb5L",
                model='eleven_multilingual_v1'
            )

            await bot.send_voice(message.chat.id, audio)
            return
        else:
            buffer.append(detok)
            if len(buffer) % 3 == 0:
                try:
                    await bot.edit_message_text("".join(buffer), message__.chat.id, message__.message_id)
                except:
                    pass

    await state.update_data(chat_memory=memory + "User:" +  message.text + "\nGanjar:" + "".join(buffer) + "\n")
    audio = generate(
        text="".join(buffer),
        voice="lhG8PEIXIoYq5B4mcb5L",
        model='eleven_multilingual_v1'
    )

    await bot.send_voice(message.chat.id, audio)

# voice message handler
@dp.message_handler(content_types=types.ContentType.VOICE, state="*")
async def voice_handler(message: types.Message, state: FSMContext):

    msg_voice = await message.answer("***⚙️ Analyzing voice message...***", parse_mode="markdown")

    # save voice message
    file_id = message.voice.file_id
    file_info = await bot.get_file(message.voice.file_id)
    file = await bot.download_file(file_info.file_path)

    with open(f"{file_id}.ogg", "wb") as f:
        f.write(file.read())

    # convert to mp3
    convert_ogg_to_mp3(f"{file_id}.ogg", f"{file_id}.mp3")

    segments, _ = whisper.transcribe(f"{file_id}.mp3")
    segments = list(segments) 

    await bot.edit_message_text("***🎙 Voice message:***\n\n" + segments[0].text, message.chat.id, msg_voice.message_id, parse_mode="markdown")

    data = await state.get_data()

    lang = data.get("language", "english")
    memory = data.get("chat_memory", "")

    if lang == "english":
        message__ = await bot.send_message(message.chat.id, "📝 Ganjar is typing...")
    elif lang == "indonesian":
        message__ = await bot.send_message(message.chat.id, "📝 Ganjar sedang mengetik...")

    if lang == "english":
        prompt = SYSTEM_PROMPT_EN + memory + "User:" + segments[0].text + "\nGanjar:"
    elif lang == "indonesian":
        prompt = SYSTEM_PROMPT_ID + memory + "User:" + segments[0].text + "\nGanjar:"

    print("PROMPT: \n\n", prompt)

    buffer = []
    kwargs = {"prompt" : prompt, "top_k" : 40, "top_p" : 0.95, "temperature" : 0.4, "repeat_penalty" : 1.1, "stream" : True, "max_tokens" : 256}

    for token in LLAMA_GLOBAL.create_completion(**kwargs):
        detok = token["choices"][0]["text"]
        if detok in STOP_TOKENS:
            print("FINISHED REASON ", detok)
            try:
                await bot.edit_message_text("".join(buffer), message__.chat.id, message__.message_id)
            except:
                pass
            await state.update_data(chat_memory=memory + "User:" + segments[0].text + "\nGanjar:" + "".join(buffer) + "\n")
            audio = generate(
                text="".join(buffer),
                voice="lhG8PEIXIoYq5B4mcb5L",
                model='eleven_multilingual_v1'
            )

            await bot.send_voice(message.chat.id, audio)
            return
        else:
            buffer.append(detok)
            if len(buffer) % 3 == 0:
                try:
                    await bot.edit_message_text("".join(buffer), message__.chat.id, message__.message_id)
                except:
                    pass

    await state.update_data(chat_memory=memory + "User:" + segments[0].text + "\nGanjar:" + "".join(buffer) + "\n")
    audio = generate(
        text="".join(buffer),
        voice="lhG8PEIXIoYq5B4mcb5L",
        model='eleven_multilingual_v1'
    )

    await bot.send_voice(message.chat.id, audio)



@dp.callback_query_handler(lambda c: c.data in ["indonesian", "english"], state="*")
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    lang = callback_query.data
    await state.update_data(language=lang)

    message = callback_query.message

    await bot.answer_callback_query(callback_query.id)
    if lang == "english":
        await bot.edit_message_text("🇺🇸 Language set to English", message.chat.id, message.message_id)
    elif lang == "indonesian":
        await bot.edit_message_text("🇮🇩 Bahasa diatur ke Bahasa Indonesia", message.chat.id, message.message_id)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)