from aiogram import Bot, Dispatcher, executor, types

import database as db
from config import TELEGRAM_TOKEN as TOKEN
from lastfm_utils import get_artist_info, get_top_albums

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message) -> None:
    """Send welcome message and request wallet if this is a new user"""

    if {"user_id": message.chat.id} not in db.fetchall("users", ["user_id"]):
        db.insert("users", {"user_id": message.chat.id})

        await message.answer(
            "Добро пожаловать!👋\n"
            "Чтобы узнать подробную информацию об исполнителе используй /info `имя исполнителя`\n"
            "Чтобы добавить исполнителя в избранное используй /add `имя исполнителя`\n"
            "Чтобы удалить исполнителя из избранного используй /del `имя исполнителя`\n"
            "Чтобы узнать топ3 альбомы исполнителя используй /top `имя исполнителя`\n"
            "Чтобы узнать топ2 альбомы исполнителей в избранном используй /favorites"
        )

    else:
        await message.answer(
            "Привет еще раз)\n" "Напиши /help, чтобы узнать команды"
        )


@dp.message_handler(commands=["help"])
async def send_help(message: types.Message) -> None:
    await message.answer(
        "Чтобы узнать подробную информацию об исполнителе используй /info `имя исполнителя`\n"
        "Чтобы добавить исполнителя в избранное используй /add `имя исполнителя`\n"
        "Чтобы удалить исполнителя из избранного используй /del `имя исполнителя`\n"
        "Чтобы узнать топ3 альбомы используй /top `имя исполнителя`\n"
        "Чтобы узнать топ2 альбомы исполнителей в избранном используй /favorites"
    )


@dp.message_handler(commands=["info"])
async def send_info(message: types.Message) -> None:
    message_text = " ".join(tuple(message.text.split())[1::])
    if message_text and get_artist_info(message_text):
        await message.answer(get_artist_info(message_text))
    else:
        await message.answer("Ошибка! Неверное имя артиста.")


@dp.message_handler(commands=["add"])
async def add_artist(message: types.Message) -> None:
    artist = " ".join(tuple(message.text.split())[1::])
    if artist and get_artist_info(artist):
        db.insert("users", {"user_id": message.from_id, "artist_name": artist})
        await message.answer(f"Артист {artist} добавлен в список избранного!")
    else:
        await message.answer("Ошибка! Неверное имя артиста.")


@dp.message_handler(commands=["del"])
async def del_artist(message: types.Message) -> None:
    artist = " ".join(tuple(message.text.split())[1::])
    if artist:
        db.delete("users", message.from_id, artist)
        await message.answer(f"Артист {artist} удален из списка избранного!")
    else:
        await message.answer("Ошибка!")


@dp.message_handler(commands=["top"])
async def send_top_albums(message: types.Message) -> None:
    message_text = " ".join(tuple(message.text.split())[1::])
    if message_text:
        await message.answer(get_top_albums(message_text))
    else:
        await message.answer("Ошибка!")


@dp.message_handler(commands=["favourites", "favorites"])
async def send_favorites(message: types.Message) -> None:
    result = db.fetchall("users", ["artist_name"], message.from_id)
    favorites_artists = [
        artist["artist_name"] for artist in result if artist["artist_name"]
    ]
    bot_message = "Избранное:\n"
    for artist in favorites_artists:
        bot_message += f"{artist}:\n{get_top_albums(artist, 2)}\n"
    await message.answer(bot_message)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
