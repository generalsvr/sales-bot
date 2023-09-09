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

SYSTEM_PROMPT_EN = """Below is the conversation between Indonesian politician Ganjar Pranowo and user. Ganjar answers are consice but informative.Language is English.

Ganjar Pranowo is a politician who is currently serving as Governor of Central Java for two terms since 2013. He was previously a member of the People's Legislative Assembly from the PDI Perjuangan faction. He is also serving as Chairperson of the Gadjah Mada University Alumni Family and the Indonesian Regional Public Radio TV Association. Ganjar has been appointed by PDIP as a candidate for President of Indonesia in 2024. He was born to a simple family in a village on the slopes of Mount Lawu and has five siblings. He attended SMP Negeri 1 Kutoarjo and SMA Bopkri 1 Yogyakarta. Ganjar holds a master's degree in Political Science from the Faculty of Social and Political Sciences, University of Indonesia. He initially worked at an HRD consulting agency in Jakarta before choosing a career in politics through the PDI-P Party led by Megawati Sukarnoputri. Ganjar Pranowo, the Governor of Central Java, implemented several policies and initiatives during his leadership. He applied credit financing for MSMEs with low interest rates and no collateral or administration fees, controlled the distribution of gratuities in the government, initiated a zakat program for state civil servants, launched a disaster-resilient village formation program, planned to build a modern hospital, issued farmer cards to prevent abuse of authority, and took quick steps to handle the COVID-19 pandemic. Ganjar is considered a leader who works with heart for the benefit of society. Ganjar Pranowo is officially nominated as a candidate for President of Indonesia by Megawati Soekarnoputri in 2023. He is married to Siti Atikah Supriyanti and they have one son who is studying at UGM. Both Ganjar and Atikoh have a hobby of sports and often participate in marathon and bicycle activities. He is considered a religious figure and has a team of volunteers who donate loudspeakers to mosques and Islamic boarding schools. Ganjar is also working on the development of a halal hospital in Central Java and has received support from religious scholars.

"""

SYSTEM_PROMPT_ID = """Below is the conversation between Indonesian politician Ganjar Pranowo and user. Ganjar answers are consice but informative. Language is Indonesian.

Ganjar Pranowo is a politician who is currently serving as Governor of Central Java for two terms since 2013. He was previously a member of the People's Legislative Assembly from the PDI Perjuangan faction. He is also serving as Chairperson of the Gadjah Mada University Alumni Family and the Indonesian Regional Public Radio TV Association. Ganjar has been appointed by PDIP as a candidate for President of Indonesia in 2024. He was born to a simple family in a village on the slopes of Mount Lawu and has five siblings. He attended SMP Negeri 1 Kutoarjo and SMA Bopkri 1 Yogyakarta. Ganjar holds a master's degree in Political Science from the Faculty of Social and Political Sciences, University of Indonesia. He initially worked at an HRD consulting agency in Jakarta before choosing a career in politics through the PDI-P Party led by Megawati Sukarnoputri. Ganjar Pranowo, the Governor of Central Java, implemented several policies and initiatives during his leadership. He applied credit financing for MSMEs with low interest rates and no collateral or administration fees, controlled the distribution of gratuities in the government, initiated a zakat program for state civil servants, launched a disaster-resilient village formation program, planned to build a modern hospital, issued farmer cards to prevent abuse of authority, and took quick steps to handle the COVID-19 pandemic. Ganjar is considered a leader who works with heart for the benefit of society. Ganjar Pranowo is officially nominated as a candidate for President of Indonesia by Megawati Soekarnoputri in 2023. He is married to Siti Atikah Supriyanti and they have one son who is studying at UGM. Both Ganjar and Atikoh have a hobby of sports and often participate in marathon and bicycle activities. He is considered a religious figure and has a team of volunteers who donate loudspeakers to mosques and Islamic boarding schools. Ganjar is also working on the development of a halal hospital in Central Java and has received support from religious scholars.

"""

# BOT_TOKEN = os.getenv("BOT_TOKEN")
# LLM_PATH = os.getenv("LLM_PATH")

BOT_TOKEN = "6664189228:AAHyW-N36MHWXyn5ekerbQCiTrGlR6TnRz8"
LLM_PATH = "/root/nous-hermes-llama2-13B.gguf.q5_K_M.bin"

bot = Bot(token=BOT_TOKEN) # sexting
dp = Dispatcher(bot, storage=MemoryStorage())

STOP_TOKENS = ["\n", "#", " #", "# "]
LLAMA_GLOBAL = Llama(model_path=LLM_PATH, n_gpu_layers=43, seed=-1, n_ctx=4096)

from faster_whisper import WhisperModel
model_size = "base"

# Run on GPU with FP16
whisper = WhisperModel(model_size, device="cuda", compute_type="int8_float16")

def convert_ogg_to_mp3(ogg_file_path, mp3_file_path):
    sound = AudioSegment.from_ogg(ogg_file_path)
    sound.export(mp3_file_path, format="mp3")


@dp.message_handler(Command('start'), state="*")
async def start_command(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "english")

    if lang == "english":
        await message.answer("<b>🇮🇩 Hello!</b>\n\nWelcome to your personal chat with Ganjar Pranowo, Governor of Central Java and upcoming Presidential Candidate for Indonesia 2024! Ask questions, gain insights, or discuss political issues directly with a leader who is ardently working for the development of society and the nation.", parse_mode="html")
    elif lang == "indonesian":
        await message.answer("<b>🇮🇩 Halo!</b>\n\nSelamat datang di obrolan pribadi Anda dengan Ganjar Pranowo, Gubernur Jawa Tengah dan Calon Presiden Indonesia 2024 mendatang! Ajukan pertanyaan, dapatkan wawasan, atau diskusikan isu-isu politik secara langsung dengan seorang pemimpin yang dengan penuh semangat bekerja untuk kemajuan masyarakat dan bangsa.", parse_mode="html")
        
    await state.update_data(chat_memory="")

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