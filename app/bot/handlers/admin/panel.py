from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from app.services.admin_service import AdminService
from app.infrastructure.database.session import AsyncSessionLocal
from app.bot.keyboards.admin import admin_main_menu, admin_back_btn, admin_media_list_btn
from app.core.config import settings

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS

@router.message(F.text.lower().in_({"/admin", "/panel", "admin", "panel"}), F.from_user.id.in_(settings.ADMIN_IDS))
async def cmd_admin_panel(message: types.Message):
    await message.answer("<b>👔Admin panelga hush kelibsiz !</b>", reply_markup=admin_main_menu(), parse_mode="HTML")

@router.message(F.text == "🔙Chiqish", F.from_user.id.in_(settings.ADMIN_IDS))
async def cmd_admin_exit(message: types.Message):
    from app.bot.keyboards.default import get_main_menu
    await message.answer("<b>🏠Bosh menyu</b>", reply_markup=get_main_menu(), parse_mode="HTML")

@router.message(F.text == "📊Statistika", F.from_user.id.in_(settings.ADMIN_IDS))
async def cmd_admin_stats(message: types.Message):
    async with AsyncSessionLocal() as session:
        service = AdminService(session)
        stats = await service.get_statistics()
        
    text = f"""
<b>📊Botining statistikasi :</b>

<i>👥Foydalanuvchilar soni: {stats['users_count']} ta</i>
<i>🔸Animelar soni: {stats['anime_count']} ta</i>
<i>🔹Dramalar soni: {stats['drama_count']} ta</i>
"""
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "💬Xabar Yuborish", F.from_user.id.in_(settings.ADMIN_IDS))
async def cmd_admin_broadcast(message: types.Message):
    await message.answer("<b>💬Habar yuborish turini tanlang:</b>\n(Hozircha faqat test)", reply_markup=admin_back_btn(), parse_mode="HTML")

@router.message(F.text == "🔐Majburiy A'zo", F.from_user.id.in_(settings.ADMIN_IDS))
async def cmd_admin_sponsors(message: types.Message):
    async with AsyncSessionLocal() as session:
        service = AdminService(session)
        sponsors = await service.get_all_sponsors()
        
    from app.bot.keyboards.admin import admin_sponsors_list_btn
    await message.answer("<b>🔐Homiy kanallar:</b>", reply_markup=admin_sponsors_list_btn(sponsors), parse_mode="HTML")

# Add Media Handlers
from app.bot.states.admin import AddMediaStates, BroadcastStates, SponsorshipStates, StaffStates, PostingStates

@router.message(F.text == "➕Media Qo'shish", F.from_user.id.in_(settings.ADMIN_IDS))
async def cmd_add_media(message: types.Message, state: FSMContext):
    await message.answer("<b>✨Yangi media nomini yuboring</b>", reply_markup=admin_back_btn(), parse_mode="HTML")
    await state.set_state(AddMediaStates.waiting_for_title)

@router.message(AddMediaStates.waiting_for_title, F.from_user.id.in_(settings.ADMIN_IDS))
async def process_media_title(message: types.Message, state: FSMContext):
    if message.text == "🔙Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi", reply_markup=admin_main_menu())
        return
        
    await state.update_data(title=message.text)
    await message.answer("<b>Media turini tanlang (anime/drama):</b>", reply_markup=admin_back_btn(), parse_mode="HTML") # Should be buttons ideally, simplified for text input now or use type buttons
    await state.set_state(AddMediaStates.waiting_for_type)

@router.message(AddMediaStates.waiting_for_type, F.from_user.id.in_(settings.ADMIN_IDS))
async def process_media_type(message: types.Message, state: FSMContext):
    msg_type = message.text.lower()
    if "anime" in msg_type:
        msg_type = "anime"
    elif "drama" in msg_type:
        msg_type = "drama"
    else:
        await message.answer("Iltimos 'anime' yoki 'drama' deb yozing.")
        return

    await state.update_data(media_type=msg_type)
    await message.answer("<b>Janrni kiriting:</b>", reply_markup=admin_back_btn(), parse_mode="HTML")
    await state.set_state(AddMediaStates.waiting_for_genre)

@router.message(AddMediaStates.waiting_for_genre, F.from_user.id.in_(settings.ADMIN_IDS))
async def process_media_genre(message: types.Message, state: FSMContext):
    data = await state.get_data()
    genre = message.text
    
    async with AsyncSessionLocal() as session:
        service = AdminService(session)
        media = await service.add_media(
            title=data['title'],
            media_type=data['media_type'],
            genre=genre
        )
    
    await message.answer(f"✅ <b>{media.name}</b> qo'shildi! ID: {media.id}. Kod: {media.code if hasattr(media, 'code') else 'N/A'}", reply_markup=admin_main_menu(), parse_mode="HTML")
    await state.clear()


# Broadcast Handlers
@router.message(F.text == "💬Xabar Yuborish") # Fixed filter to be generally accessible but protected by inner check
async def cmd_broadcast_enter(message: types.Message, state: FSMContext):
    if message.from_user.id not in settings.ADMIN_IDS: return
    await message.answer("<b>Xabaringizni yuboring (Text, Rasm, Video):</b>", reply_markup=admin_back_btn(), parse_mode="HTML")
    await state.set_state(BroadcastStates.waiting_for_message)

@router.message(BroadcastStates.waiting_for_message)
async def process_broadcast_message(message: types.Message, state: FSMContext):
    # Determine message type and copy to all users (simplified version)
    # Ideally should use a background task for large broadcasts
    
    await message.answer("Xabar yuborish boshlandi...", reply_markup=admin_main_menu())
    
    async with AsyncSessionLocal() as session:
        # We need a method to get all users
        from sqlalchemy import select
        from app.infrastructure.database.models.user import User
        users = await session.execute(select(User.id))
        user_ids = users.scalars().all()
        
        count = 0
        blocked = 0
        from aiogram.exceptions import TelegramForbiddenError
        
        for user_id in user_ids:
            try:
                await message.copy_to(chat_id=user_id)
                count += 1
                await asyncio.sleep(0.05) # Rate limit
            except TelegramForbiddenError:
                blocked += 1
            except Exception as e:
                pass
                
        await message.answer(f"✅ Xabar yuborildi.\nJami: {len(user_ids)}\nYuborildi: {count}\nBlokladi: {blocked}")
    
    await state.clear()

# Back Handler
@router.callback_query(F.data == "admin_back")
async def cb_admin_back(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await call.message.answer("<b>👔Admin panel</b>", reply_markup=admin_main_menu(), parse_mode="HTML")

# Sponsorship Handlers
@router.callback_query(F.data == "admin_sponsors_add", F.from_user.id.in_(settings.ADMIN_IDS)) # Need to add button for this in list
async def cb_add_sponsor(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("<b>Kanal ID sini yuboring:</b>\n(Masalan: -100123456789)", reply_markup=admin_back_btn(), parse_mode="HTML")
    await state.set_state(SponsorshipStates.waiting_for_channel_id)

@router.message(SponsorshipStates.waiting_for_channel_id, F.from_user.id.in_(settings.ADMIN_IDS))
async def process_sponsor_id(message: types.Message, state: FSMContext):
    try:
        channel_id = int(message.text)
        await state.update_data(channel_id=channel_id)
        await message.answer("<b>Kanal nomini yuboring:</b>", reply_markup=admin_back_btn(), parse_mode="HTML")
        await state.set_state(SponsorshipStates.waiting_for_channel_name)
    except ValueError:
        await message.answer("Iltimos to'g'ri ID kiriting (raqam).")

@router.message(SponsorshipStates.waiting_for_channel_name, F.from_user.id.in_(settings.ADMIN_IDS))
async def process_sponsor_name(message: types.Message, state: FSMContext):
    await state.update_data(channel_name=message.text)
    await message.answer("<b>Kanal linkini yuboring:</b>", reply_markup=admin_back_btn(), parse_mode="HTML")
    await state.set_state(SponsorshipStates.waiting_for_channel_link)

@router.message(SponsorshipStates.waiting_for_channel_link, F.from_user.id.in_(settings.ADMIN_IDS))
async def process_sponsor_link(message: types.Message, state: FSMContext):
    await state.update_data(channel_link=message.text)
    await message.answer("<b>Majburiy a'zolik limitini kiriting:</b>\n(Nechta odamga yetganda o'chishi kerak? Cheksiz bo'lsa 0)", reply_markup=admin_back_btn(), parse_mode="HTML")
    await state.set_state(SponsorshipStates.waiting_for_user_limit)

@router.message(SponsorshipStates.waiting_for_user_limit, F.from_user.id.in_(settings.ADMIN_IDS))
async def process_sponsor_limit(message: types.Message, state: FSMContext):
    try:
        limit = int(message.text)
        data = await state.get_data()
        
        async with AsyncSessionLocal() as session:
            service = AdminService(session)
            await service.add_sponsor(
                channel_id=data['channel_id'],
                name=data['channel_name'],
                link=data['channel_link'],
                limit=limit
            )
            
        await message.answer("✅ Kanal muvaffaqiyatli qo'shildi!", reply_markup=admin_main_menu(), parse_mode="HTML")
        await state.clear()
    except ValueError:
        await message.answer("Iltimos raqam kiriting.")

@router.callback_query(F.data.startswith("admin_sponsor_delete_"), F.from_user.id.in_(settings.ADMIN_IDS))
async def cb_delete_sponsor(call: types.CallbackQuery):
    channel_id = int(call.data.split("_")[-1])
    
    async with AsyncSessionLocal() as session:
        service = AdminService(session)
        await service.delete_sponsor(channel_id)
        
    await call.message.answer("🗑 Kanal o'chirildi.")
    # Refresh list
    async with AsyncSessionLocal() as session:
        service = AdminService(session)
        sponsors = await service.get_all_sponsors()
        
    from app.bot.keyboards.admin import admin_sponsors_list_btn
    await call.message.edit_reply_markup(reply_markup=admin_sponsors_list_btn(sponsors))

# Staff Handlers
@router.message(F.text == "👔Admin Qo'shish", F.from_user.id.in_(settings.ADMIN_IDS))
async def cmd_admin_staff(message: types.Message):
    async with AsyncSessionLocal() as session:
        service = AdminService(session)
        staff = await service.get_all_staff()
        
    from app.bot.keyboards.admin import admin_staff_list_btn
    await message.answer("<b>👔Adminlar:</b>\n(O'chirish uchun ustiga bosing)", reply_markup=admin_staff_list_btn(staff), parse_mode="HTML")

@router.callback_query(F.data == "admin_staff_add", F.from_user.id.in_(settings.ADMIN_IDS))
async def cb_add_staff(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("<b>Yangi admin ID sini yuboring:</b>", reply_markup=admin_back_btn(), parse_mode="HTML")
    await state.set_state(StaffStates.waiting_for_id)

@router.message(StaffStates.waiting_for_id, F.from_user.id.in_(settings.ADMIN_IDS))
async def process_staff_id(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)
        async with AsyncSessionLocal() as session:
            service = AdminService(session)
            await service.add_staff(user_id)
            
        await message.answer(f"✅ User {user_id} admin qilindi.", reply_markup=admin_main_menu())
        await state.clear()
    except ValueError:
        await message.answer("Raqam bo'lishi kerak.")

@router.callback_query(F.data.startswith("admin_staff_delete_"), F.from_user.id.in_(settings.ADMIN_IDS))
async def cb_delete_staff(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[-1])
    
    if user_id in settings.ADMIN_IDS:
        await call.answer("Asosiy adminni o'chira olmaysiz!", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        service = AdminService(session)
        await service.remove_staff(user_id)
        
    await call.message.answer(f"🗑 Admin {user_id} o'chirildi.")
    # Refresh
    async with AsyncSessionLocal() as session:
        service = AdminService(session)
        staff = await service.get_all_staff()
        
    from app.bot.keyboards.admin import admin_staff_list_btn
    await call.message.edit_reply_markup(reply_markup=admin_staff_list_btn(staff))


# Posting Handlers (Simplified for now - just text)
@router.message(F.text.in_({"📤Post Qilish", "📤Qismni Post Qilish"}), F.from_user.id.in_(settings.ADMIN_IDS))
async def cmd_admin_post(message: types.Message, state: FSMContext):
    await message.answer("<b>Post qilinishi kerak bo'lgan media nomini kiriting:</b>", reply_markup=admin_back_btn(), parse_mode="HTML")
    await state.set_state(PostingStates.search)

@router.message(PostingStates.search, F.from_user.id.in_(settings.ADMIN_IDS))
async def process_post_search(message: types.Message, state: FSMContext):
    from app.services.media_service import MediaService
    
    async with AsyncSessionLocal() as session:
        service = MediaService(session)
        # Search for media
        results = await service.search_media(message.text)
        
    if not results:
        await message.answer("❌ Hech narsa topilmadi.", reply_markup=admin_main_menu())
        await state.clear()
        return

    from app.bot.keyboards.admin import admin_media_list_btn
    # We need a new keyboard or reuse existing list but with different callback
    # Reuse admin_media_list_btn but maybe we need a specific one for posting?
    # For now, let's just show list. But callback "admin_media_{id}" needs to be handled.
    # We should probably create a specific keyboard for posting selection or handle the generic one.
    # Let's use specific callback for posting selection.
    
    builder = InlineKeyboardBuilder()
    for i in results:
        type_emoji = "🔸" if i.type == "anime" else "🔹"
        builder.add(InlineKeyboardButton(text=f"{type_emoji}{i.name}", callback_data=f"admin_post_select_{i.id}"))
    builder.add(InlineKeyboardButton(text="🔙Chiqish", callback_data="admin_back"))
    builder.adjust(1)
        
    await message.answer("<b>Natijalar:</b>\nTanlang:", reply_markup=builder.as_markup(), parse_mode="HTML")

@router.callback_query(F.data.startswith("admin_post_select_"), F.from_user.id.in_(settings.ADMIN_IDS))
async def cb_post_select(call: types.CallbackQuery, state: FSMContext):
    media_id = int(call.data.split("_")[-1])
    # Logic to post to channel
    # Validation: check channel IDs in settings
    
    target_channel = settings.TRAILERS_BASE_CHAT # Defaulting to trailers for now, or logic to choose
    
    # Needs to fetch media details and post.
    # Simplified: Just notify it's done for now or try to send.
    
    await call.message.answer(f"✅ Media {media_id} kanalga chiqarilmoqda... (Hozircha test)", reply_markup=admin_main_menu())
    await state.clear()
