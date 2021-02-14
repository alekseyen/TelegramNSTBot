from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.input_file import InputFile

from bot.misc import bot, dp, task_queue

content_name = None
style_name = None


class Photos(StatesGroup):
    content_state = State()
    style_state = State()


@dp.message_handler(commands="neural_style_transfer", state="*")
async def advanced_nst_start(message: types.Message):
    await message.answer("Please upload content image")
    await Photos.content_state.set()


@dp.message_handler(state=Photos.content_state, content_types=['photo', types.ContentType.DOCUMENT])
async def photo1(message: types.Message, state: FSMContext):
    global content_name
    name = None
    if message.document is None:
        name = message.photo[-1].file_id
        await message.photo[-1].download(f'data/content_{name}')
    else:
        name = message.document.file_id
        await message.document.download(f'data/content_{name}')

    content_name = f'data/content_{name}'

    await state.update_data(pic=content_name)
    await Photos.next()
    await message.answer("Content image is uploaded, please send style image")


@dp.message_handler(state=Photos.style_state, content_types=['photo', types.ContentType.DOCUMENT])
async def photo2(message: types.Message, state: FSMContext):
    global style_name, content_name
    name = None

    if message.document is None:
        name = message.photo[-1].file_id
        await message.photo[-1].download(f'data/style_{name}')
    else:
        name = message.document.file_id
        await message.document.download(f'data/style_{name}')

    style_name = f'data/style_{name}'
    await state.update_data(pic=style_name)
    await state.finish()
    await message.answer("Style image is uploaded, pls wait ..")

    task_queue.put({'type': 'nst', 'message': message, 'style_path': style_name,
                    'content_path': content_name})
