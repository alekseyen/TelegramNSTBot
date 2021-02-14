from aiogram import types
from bot.misc import dp


@dp.message_handler(content_types=types.ContentTypes.ANY, state="*")
async def all_other_messages(message: types.Message):
    if message.content_type == "text":
        await message.reply("I am not programmed to answer that query, pls use \help")
    else:
        await message.reply("Please use \help")
