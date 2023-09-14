from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup

import pickle
import numpy as np
from sklearn.manifold import TSNE
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sentence_transformers import SentenceTransformer
from PIL import Image
import time

im_model = SentenceTransformer('clip-ViT-L-14', device='cuda:0')

def get_image_embeddings(img_name):
    img_emb = im_model.encode([Image.open(img_name)], convert_to_tensor=True)
    return img_emb.cpu()[0].numpy()

BOT_TOKEN = "6522653863:AAGfwFcmR5zU_ReTsp7eayan7kiGNjhmMn4"

bot = Bot(token=BOT_TOKEN) # sexting
dp = Dispatcher(bot, storage=MemoryStorage())


def process_photo(photo):
    # load pickle 
    clf = pickle.load(open("/model2.pkl", "rb"))

    # get embeddings
    img_emb = get_image_embeddings(photo)

    # predict
    pred = clf.predict([img_emb])[0]

    # return prediction
    return pred

# start command handler
@dp.message_handler(Command("start"))
async def start(message: types.Message):
    await message.reply("Отправь фото\n\nКласс True - это уходит на глубокий анализ\nКласс False - пропускаем")


# bot image handler
@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message: types.Message):
    # get photo
    photo = message.photo[-1]

    # download photo
    photo = await photo.download()
    
    print(photo.name)

    start = time.time()

    # process photo
    pred = process_photo(photo.name)

    pred_time = round(time.time() - start, 2)

    # send prediction
    if int(pred) == 1:
        await message.reply(f"Prediction: ***False ❌***\n\nВремя: {pred_time} с", parse_mode="Markdown")
    else:
        await message.reply(f"Prediction: ***True ✅***\n\nВремя: {pred_time} с", parse_mode="Markdown")
        

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)