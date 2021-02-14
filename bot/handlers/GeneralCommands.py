from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.misc import dp

# Reply keyboard
button_nst = KeyboardButton('/neural_style_transfer')
button_cyclegan = KeyboardButton('/styling_gan')
button_deep_ai = KeyboardButton('/deep_ai')
greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
greet_kb.add(button_nst).add(button_cyclegan).add(button_deep_ai)


@dp.message_handler(commands=['start', 'help'], state="*")
async def cmd_start(message: types.Message):
    await message.reply(
        "👋 Hello,  this bot applies a style transfer algorithm from one photo to another. Please select from the following menu: "
        "\n /neural_style_transfer"
        # "\n /advanced_nst (2 style images)" # TODO
        "\n /deep_ai"
        "\n /styling_gan",
        reply_markup=greet_kb)
