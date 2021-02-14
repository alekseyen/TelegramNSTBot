import requests
import wget
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.input_file import InputFile

from bot.misc import bot
from bot.misc import dp


class DeepAiPhotos(StatesGroup):
    content_state = State()
    style_state = State()


@dp.message_handler(commands="deep_ai", state="*")
async def advanced_nst_start(message: types.Message):
    await message.answer("Please upload content image")
    await DeepAiPhotos.content_state.set()


@dp.message_handler(state=DeepAiPhotos.content_state, content_types=['photo', types.ContentType.DOCUMENT])
async def photo1(message: types.Message, state: FSMContext):
    if message.document is None:
        await message.photo[-1].download('data/content.jpg')
    else:
        await message.document.download(f'data/content.{str(message.document.file_name).split(".")[1]}')

    await state.update_data(pic='data/content.jpg')
    await DeepAiPhotos.next()
    await message.answer("Content image is uploaded, please send style image")


@dp.message_handler(state=DeepAiPhotos.style_state, content_types=['photo', types.ContentType.DOCUMENT])
async def photo2(message: types.Message, state: FSMContext):
    if message.document is None:
        await message.photo[-1].download('data/style.jpg')
    else:
        await message.document.download(f'data/style.{str(message.document.file_name).split(".")[1]}')

    await state.update_data(pic='data/style.jpg')
    await state.finish()
    await message.answer("Style image is uploaded, pls wait ..")
    await create_photo(message)


@dp.async_task
async def create_photo(message: types.Message):
    r = requests.post(
        "https://api.deepai.org/api/fast-style-transfer",
        files={
            'content': open('data/content.jpg', 'rb'),
            'style': open('data/style.jpg', 'rb'),
        },
        headers={'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'}
    )

    img = wget.download(r.json()['output_url'])  # , out='output.jpg')

    photo = InputFile(path_or_bytesio=img)
    await bot.send_photo(message.chat.id, photo, 'result')
