from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def admin_main_menu():
    kb_list = [
        [KeyboardButton(text="➕Media Qo'shish"), KeyboardButton(text="➕Qism Qo'shish")],
        [KeyboardButton(text="✏️Media Tahrirlash"), KeyboardButton(text="✏️Qismni Tahrirlash")],
        [KeyboardButton(text="📊Statistika"), KeyboardButton(text="💬Xabar Yuborish")],
        [KeyboardButton(text="🔐Majburiy A'zo"), KeyboardButton(text="👔Admin Qo'shish")],
        [KeyboardButton(text="📤Post Qilish"), KeyboardButton(text="📤Qismni Post Qilish")],
        [KeyboardButton(text="🔙Chiqish")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)

def admin_back_btn():
    button = InlineKeyboardBuilder()
    button.add(InlineKeyboardButton(text="🔙Bekor qilish", callback_data="admin_back"))
    return button.as_markup()

def admin_media_list_btn(medias):
    button = InlineKeyboardBuilder()
    for i in medias:
        type_emoji = "🔸" if i.type == "anime" else "🔹"
        button.add(InlineKeyboardButton(text=f"{type_emoji}{i.name}", callback_data=f"admin_media_{i.id}"))
    button.add(InlineKeyboardButton(text="🔙Chiqish", callback_data="admin_back"))
    button.adjust(1)
    return button.as_markup()

def admin_msg_type_btn():
    button = InlineKeyboardBuilder()
    button.add(InlineKeyboardButton(text="⚡️Bot nomidan ( tez )", callback_data="admin_msg_type_copy"))
    button.add(InlineKeyboardButton(text="🔁Forward qilib ( sekin )", callback_data="admin_msg_type_forward"))
    button.add(InlineKeyboardButton(text="🔙Bekor qilish", callback_data="admin_back"))
    button.adjust(1)
    return button.as_markup()

def admin_confirm_btn(action: str):
    button = InlineKeyboardBuilder()
    button.add(InlineKeyboardButton(text="✅Ha", callback_data=f"admin_confirm_{action}"), 
               InlineKeyboardButton(text="❌Yo'q", callback_data="admin_cancel"))
    return button.as_markup()

def admin_sponsors_list_btn(sponsors):
    button = InlineKeyboardBuilder()
    for s in sponsors:
        button.add(InlineKeyboardButton(text=f"{s.channel_name} ({s.user_limit})", url=s.channel_link))
        button.add(InlineKeyboardButton(text="🗑", callback_data=f"admin_sponsor_delete_{s.channel_id}"))
    
    button.adjust(2)
    button.row(InlineKeyboardButton(text="➕ Qo'shish", callback_data="admin_sponsors_add"), 
               InlineKeyboardButton(text="🔙Chiqish", callback_data="admin_back"))
    return button.as_markup()

def admin_staff_list_btn(staff_list):
    button = InlineKeyboardBuilder()
    for s in staff_list:
        button.add(InlineKeyboardButton(text=f"{s.full_name or s.username or s.id}", callback_data=f"admin_staff_delete_{s.id}"))
    
    button.adjust(1)
    button.row(InlineKeyboardButton(text="➕ Qo'shish", callback_data="admin_staff_add"), 
               InlineKeyboardButton(text="🔙Chiqish", callback_data="admin_back"))
    return button.as_markup()
