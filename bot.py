import asyncio
import logging
import sys
import json
import re

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

# Function to load JSON data


def load_responses(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Function to save JSON data


async def save_responses(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

TOKEN = "BOT_TOKEN"
FILENAME = "words.json"

responses = load_responses(FILENAME)

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {message.from_user.full_name}!")


@dp.message(Command("wadd"))
async def cmd_add(message: types.Message):
    args = message.text.split()

    if len(args) >= 3:
        trigger, word = args[1], args[2]
        responses[trigger] = word
        await save_responses(FILENAME, responses)
        await message.answer(f"<b>Увага!</b> До списку додано: {trigger}: {word}")
    else:
        await message.answer("Будь ласка, вкажуть аргументи. Приклад: /wadd trigger word")


@dp.message(Command("wremove"))
async def cmd_remove(message: types.Message):
    args = message.text.split()

    if len(args) >= 2:
        trigger = args[1]
        if trigger in responses:
            del responses[trigger]
            await save_responses(FILENAME, responses)
            await message.answer(f"<b>Увага!</b> Слово '{trigger}' видалено зі списку.")
        else:
            await message.answer(f"Слово '{trigger}' не знайдено.")
    else:
        await message.answer("Будь ласка, вкажіть аргумент. Нариклад: /wremove trigger")


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "Доступні команди:\n\n"
        "/wadd 'тригер' 'правильне слово' - додати слово до списку\n"
        "/wremove 'тригер' - видалити слово зі списку\n"
        "/list - переглянути список слів\n"
        "/help - показати це меню\n"
    )
    await message.answer(help_text)


@dp.message(Command("list"))
async def cmd_list(message: types.Message):
    words_list = "\n".join(
        [f"{key} : {value}" for key, value in responses.items()])
    if words_list:
        await message.answer(f"<b>Список слів:</b>\n\n{words_list}")
    else:
        await message.answer("<b>Список пустий.</b>")


@dp.message()
async def message_handler(message: types.Message) -> None:
    text = message.text.lower()
    triggered_keywords = []

    for keyword, response in responses.items():
        pattern = rf'\b{re.escape(keyword)}\b'
        if re.search(pattern, text):
            triggered_keywords.append(keyword)

    if triggered_keywords:
        responses_text = "\n".join(
            [f"Ви написали <b>'{trigger}'</b>, але правильно <b>'{responses[trigger]}'</b>." for trigger in triggered_keywords])
        await message.answer(f"Знайдені слова з помилками:\n\n{responses_text}")


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())