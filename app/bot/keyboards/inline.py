from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.infrastructure.database.models.media import Media
from typing import List

def search_results_keyboard(results: List[Media]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for media in results:
        builder.button(text=f"{media.name} ({media.code})", callback_data=f"media_{media.id}")
    builder.adjust(1)
    return builder.as_markup()

def media_details_keyboard(media_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👁 Tezkor ko'rish", callback_data=f"watch_{media_id}")
    builder.button(text="📥 Yuklab olish", callback_data=f"download_{media_id}")
    builder.adjust(1)
    return builder.as_markup()
