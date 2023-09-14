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

im_model = SentenceTransformer('clip-ViT-B-32')

def get_image_embeddings(img_name):
    img_emb = im_model.encode([Image.open(img_name)], convert_to_tensor=True)
    return img_emb.cpu()[0].numpy()

BOT_TOKEN = "6440607788:AAGKXiEmguhZNv0rg6gS7qOktdiGr2a8S4k"

bot = Bot(token=BOT_TOKEN) # sexting
dp = Dispatcher(bot, storage=MemoryStorage())


def process_photo(photo):
    # load pickle 
    clf = pickle.load(open("rf.pkl", "rb"))

    # get embeddings
    img_emb = get_image_embeddings(photo)

    # predict
    pred = clf.predict([img_emb])[0]

    # return prediction
    return pred

# start command handler
@dp.message_handler(Command("start"))
async def start(message: types.Message):
    await message.reply("Отправь фото")


# bot image handler
@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message: types.Message):
    # get photo
    photo = message.photo[-1]

    # download photo
    photo = await photo.download()

    # process photo
    pred = process_photo(photo)

    # send prediction
    await message.reply(f"Prediction: {pred}")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp)