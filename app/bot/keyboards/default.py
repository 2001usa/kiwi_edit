from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="🆔 Kod orqali qidiruv")
    )
    builder.row(
        KeyboardButton(text="🔍Anime Qidirish"),
        KeyboardButton(text="🔍Drama Qidirish")
    )
    builder.row(
        KeyboardButton(text="⚡️AniPass / 💎Lux"),
        KeyboardButton(text="OnGoing animelar🧧")
    )
    builder.row(
        KeyboardButton(text="🏙Rasm orqali qidiruv")
    )
    builder.row(
        KeyboardButton(text="📚Qo'llanma"),
        KeyboardButton(text="💸Reklama va homiylik")
    )
    builder.row(
        KeyboardButton(text="Animelar ro'yxati📓")
    )
    
    return builder.as_markup(resize_keyboard=True)
