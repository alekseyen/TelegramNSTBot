import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.input_file import InputFile

from bot.misc import bot
from bot.misc import dp


# from Algos.AdvancedNST import AdvancedNst

class Photos(StatesGroup):
    waiting_for_pic1 = State()
    waiting_for_pic2 = State()
    waiting_for_pic3 = State()


@dp.message_handler(commands="advanced_nst", state="*")
async def advanced_nst_start(message: types.Message):
    await message.answer("Please upload style image 1")
    await Photos.waiting_for_pic1.set()


@dp.message_handler(state=Photos.waiting_for_pic1, content_types=['photo', types.ContentType.DOCUMENT])
async def photo1(message: types.Message, state: FSMContext):
    if message.document is None:
        await message.photo[-1].download('data/style1.jpg')
    else:
        await message.document.download(f'data/style1.{str(message.document.file_name).split(".")[1]}')

    await state.update_data(pic='data/style1.jpg')
    await Photos.next()
    await message.answer("Style picture 1 is uploaded, pls send next one")


@dp.message_handler(state=Photos.waiting_for_pic2, content_types=['photo', types.ContentType.DOCUMENT])
async def photo2(message: types.Message, state: FSMContext):
    if message.document is None:
        await message.photo[-1].download('data/style2.jpg')
    else:
        await message.document.download(f'data/style2.{str(message.document.file_name).split(".")[1]}')

    await state.update_data(pic='data/style2.jpg')
    await Photos.next()
    await message.answer("Style picture 2 is uploaded too, pls send content image")


@dp.message_handler(state=Photos.waiting_for_pic3, content_types=['photo', types.ContentType.DOCUMENT])
async def photo3(message: types.Message, state: FSMContext):
    if message.document is None:
        await message.photo[-1].download('data/content.jpg')
    else:
        await message.document.download(f'data/content.{str(message.document.file_name).split(".")[1]}')

    await state.update_data(pic='data/content.jpg')
    await state.finish()
    print(os.listdir())
    await message.answer("All images is uploaded. I am starting to work on Style Transfering, pls wait..")

    # await create_photo(message)
    # my_thread = threading.Thread(target=create_photo, args=(message,))
    # my_thread.start()
    await create_photo(message)


@dp.async_task
async def create_photo(message: types.Message):
    await message.answer('get it')
    import subprocess

    subprocess.run(
        'python3 bot/Algos/vanila_nst/main.py eval --content-image data/content.jpg --style-image data/style2.jpg --model bot/Algos/vanila_nst/models/21styles.model --content-size 200 --cuda=0',
        shell=True)
    print('i did it')

    print(os.listdir())

    photo = InputFile(path_or_bytesio='output.jpg')
    await bot.send_photo(message.chat.id, photo)
