import asyncio
import logging
import shutil
from threading import Thread
from google_drive_downloader import GoogleDriveDownloader as gdd
import os

from aiogram import types
from aiogram.types import InputFile
from aiogram.utils.executor import start_webhook
import subprocess

import bot.handlers
from bot.misc import bot, dp, loop, task_queue
from bot.settings import (WEBHOOK_URL, WEBHOOK_PATH,
                          WEBAPP_HOST, WEBAPP_PORT)


async def on_startup(dp):
    logging.warning('Starting connection.')
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dp):
    logging.warning('Bye! Shutting down webhook connection')
    await dp.storage.close()
    await dp.storage.wait_closed()
    thread.join()


async def send_photo(message: types.Message, photo):
    await bot.send_photo(message.chat.id, photo, 'result')


def task_scheduler():
    while True:
        if not task_queue.empty():
            task = task_queue.get()

            if task['type'] == 'nst':

                subprocess.run(
                    f'python3 bot/Algos/vanila_nst/main.py eval --content-image {task["content_path"]} --style-image {task["content_path"]} --model bot/Algos/vanila_nst/models/21styles.model --content-size 256 --style-size 256 --cuda=0',
                    shell=True)

                photo = InputFile(path_or_bytesio='output.jpg')  # fix
            elif task['type'] == 'gan':
                chosen_model = task['model']
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

                subprocess.run(
                    'python3 main.py --testing True --dataset_dir datasets/test_root --checkpoint_dir checkpoints '
                    '--gpu_ids -1 --crop_height 500 --crop_width 500 --idt_coef 0.1 --checkpoint checkpoints/model.ckpt',
                    shell=True)
                photo = InputFile(path_or_bytesio='results/sample.jpg')  # fix

                os.chdir('../../..')

            send_fut = asyncio.run_coroutine_threadsafe(send_photo(task['message'], photo), loop)
            send_fut.result()

            task_queue.task_done()
        asyncio.sleep(2)


thread = Thread(target=task_scheduler)


def main():
    thread.start()

    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        loop=loop,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
