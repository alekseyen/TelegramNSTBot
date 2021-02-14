import os
import shutil

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.input_file import InputFile
from google_drive_downloader import GoogleDriveDownloader as gdd

from bot.misc import bot, dp, task_queue


class GanStates(StatesGroup):
    waiting_model = State()
    waiting_pic1 = State()
    waiting_pic2 = State()


# InlineKeyboard
gan_kb = InlineKeyboardMarkup(row_width=3)
btn_summer_winter = InlineKeyboardButton('🌕 Summer & Winter ❄️', callback_data='summer_to_winter')
btn_monet = InlineKeyboardButton('Monet 🎨', callback_data='monet')
btn_vangogh = InlineKeyboardButton('Vangogh 🌃', callback_data='vangogh')
gan_kb.add(btn_summer_winter)
gan_kb.add(btn_monet)
gan_kb.add(btn_vangogh)

chosen_model = None


@dp.message_handler(commands="styling_gan", state="*")
async def gan_start(message: types.Message):
    await GanStates.waiting_model.set()
    await message.answer(
        '''You have chosen *Style Gan* model. To do transformation I use `cyclegan`: https://github.com/junyanz/CycleGAN based on paper: https://arxiv.org/pdf/1703.10593.pdf. I train model on google colab with 100 epoch, using following datesets (training one model was taking 5-10 hours depending on the data size):
        - summer2winter (133mb | 2740 images 256x256)
        - monet2photo (310mb | 8231 images 256x256)
        - vangogh2photo (309mb | 7838 images 256x256)''',
        reply_markup=gan_kb, reply=False, disable_web_page_preview=True, parse_mode='Markdown')

    photo = InputFile(path_or_bytesio='bot/Algos/cyclegan/help-images/model_choose.png')
    await bot.send_photo(message.chat.id, photo, 'Examples')


@dp.callback_query_handler(lambda x: x.data == 'summer_to_winter', state=GanStates.waiting_model)
async def model1(callback_query: types.CallbackQuery, state: FSMContext):
    global chosen_model

    await bot.send_message(callback_query.from_user.id,
                           text='Please send **two** images to apply summer-winter style to it', parse_mode='Markdown')
    chosen_model = 'summer_to_winter'
    await GanStates.next()


@dp.callback_query_handler(lambda x: x.data == 'monet', state=GanStates.waiting_model)
async def model2(callback_query: types.CallbackQuery, state: FSMContext):
    global chosen_model

    await bot.send_message(callback_query.from_user.id, text='Please send **two** image to apply monet style to it',
                           parse_mode='Markdown')
    chosen_model = 'monet'
    await GanStates.next()


@dp.callback_query_handler(lambda x: x.data == 'vangogh', state=GanStates.waiting_model)
async def model3(callback_query: types.CallbackQuery, state: FSMContext):
    global chosen_model

    await bot.send_message(callback_query.from_user.id, text='Please send **two** images to apply vangogh style it',
                           parse_mode='Markdown')
    chosen_model = 'vangogh'
    await GanStates.next()


@dp.message_handler(state=GanStates.waiting_pic1, content_types=['photo', types.ContentType.DOCUMENT])
async def photo1(message: types.Message, state: FSMContext):
    if message.document is None:
        await message.photo[-1].download('data/img1.jpg')
    else:
        await message.document.download(f'data/img1.{str(message.document.file_name).split(".")[1]}')

    await state.update_data(pic='data/img1.jpg')
    await message.answer("Please send the second image..")
    await GanStates.next()


@dp.message_handler(state=GanStates.waiting_pic2, content_types=['photo', types.ContentType.DOCUMENT])
async def photo2(message: types.Message, state: FSMContext):
    if message.document is None:
        await message.photo[-1].download('data/img2.jpg')
    else:
        await message.document.download(f'data/img2.{str(message.document.file_name).split(".")[1]}')

    await state.update_data(pic='data/img2.jpg')
    await state.finish()
    await message.answer(f'I get your two pictures, get the model: {chosen_model}.'
                         f' Starting to download pretrained model... (pls wait ~3 min)')

    task_queue.put(
        {'type': 'gan', 'model': chosen_model, 'message': message, 'style_path': 'data/style.jpg',
         'content_path': 'data/content.jpg'})


# await create_photo(message)


@dp.async_task
async def create_photo(message: types.Message):
    # await message.answer(f'I get your two pictures, get the model: {chosen_model}.'
    #                      f' Starting to download pretrained model... (pls wait ~3 min)', )
    await message.answer('Starting to work(~3 min)..')

    shutil.move('data/img1.jpg', 'bot/Algos/cyclegan/datasets/test_root/testA/img1.jpg')
    shutil.move('data/img2.jpg', 'bot/Algos/cyclegan/datasets/test_root/testB/img2.jpg')

    ########

    if chosen_model == 'summer_to_winter':
        link = '1tbYQNGBW3zrBZTl2Om3_IEN2tmvA1rmF'
    # скачиваем образ1
    elif chosen_model == 'vangogh':
        link = '1_PVn400veyxwPWfdQLlE3K9PzHxS3VxI'
    elif chosen_model == 'monet':
        link = '1ix3sZzC1zKsvv1S3xihqHqKypqwHyrI9'

    ##########

    gdd.download_file_from_google_drive(file_id=link,
                                        dest_path='bot/Algos/cyclegan/checkpoints/model.ckpt',
                                        showsize=True)

    os.chdir('bot/Algos/cyclegan')
    import subprocess

    subprocess.run(
        'python3 main.py --testing True --dataset_dir datasets/test_root --checkpoint_dir checkpoints '
        '--gpu_ids -1 --crop_height 500 --crop_width 500 --idt_coef 0.1 --checkpoint checkpoints/model.ckpt',
        shell=True)

    photo = InputFile(path_or_bytesio='results/sample.jpg')

    os.chdir('../../..')
    await bot.send_photo(message.chat.id, photo, "your res:")
