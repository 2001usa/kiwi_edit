from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.services.media_service import MediaService
from app.infrastructure.database.session import AsyncSessionLocal
import os

router = Router()

@router.message(F.text == "🆔 Kod orqali qidiruv")
async def cmd_search_by_code(message: types.Message):
    await message.answer("Kinoning kodini yuboring:")

@router.message(F.text.in_({"🔍Anime Qidirish", "🔍Drama Qidirish"}))
async def cmd_search_text(message: types.Message):
    await message.answer("<b>🔍Qidirilishi kerak bo'lgan anime nomini yuboring</b>", parse_mode="HTML")

@router.message(F.text == "🏙Rasm orqali qidiruv")
async def cmd_search_image(message: types.Message):
    text = """
<b>🔍Qidirilishi kerak bo'gan anime rasmni kiriting</b>
-
<b>‼️DIQQAT</b>
<i>Yaxshi natija olish uchun animeni videosidan skrinshot olib aynan anime tasvirlangan joyini qirqib keyin rasmni yuboring. Animening Posteri yoki Bannerlarini yubormang !</i>
"""
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "📚Qo'llanma")
async def cmd_guide(message: types.Message):
    text = f"""
📚<b>Botini ishlatish bo'yicha qo'llanma : </b>
-
🔍<b>Anime Qidirish</b> - Botda mavjud bo'lgan animelarni qidirish uchun ishlatiladi. 
🔍<b>Drama Qidirish</b> - Botda mavjud bo'lgan dramalarni qidirish uchun ishlatiladi. 
💸<b>Reklama</b>  - bot adminlari bilan reklama yoki homiylik yuzasidan aloqaga chiqish.
🏙<b>Rasm Orqali Anime Qidiruv</b>  - Nomini topa olmayotgan animeingizni rasm orqali topib beradi.
📓<b>Ro'yxat</b>  - Botga joylangan Anime va Dramalar ro'yhati.
-
🆔Botdagi ID ingiz : <code>{message.from_user.id}</code>
"""
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "💸Reklama va homiylik")
async def cmd_ads(message: types.Message):
    from app.core.config import settings
    text = f"""
<b>📌Reklama va homiylik masalasida admin bilan bog'laning</b>
💬<i>Batafsil: @{settings.ADS_MANAGER_USERNAME}</i>
"""
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "⚡️AniPass / 💎Lux")
async def cmd_premium(message: types.Message):
    text = """
<b>⚡️AniPass / 💎Lux Premium Xizmatlar</b>

Tanlang:
"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⚡️AniPass", callback_data="c,anipass")
    builder.button(text="💎Lux kanal", callback_data="c,lux")
    builder.button(text="🔙Ortga", callback_data="s,back") # Placeholder for back
    builder.adjust(1)
    
    await message.answer(text, parse_mode="HTML", reply_markup=builder.as_markup())

@router.message(F.text == "Animelar ro'yxati📓")
async def cmd_list(message: types.Message):
    async with AsyncSessionLocal() as session:
        service = MediaService(session)
        # We need a method to get all media by type, but currently preload gets all.
        # Ideally, we should filter. For now, let's just get all regex match or getAll.
        # Since we added get_all to repo, we can use it.
        # But we need to filter by type in Python or add method to repo.
        # Let's filter in Python for simplicity as dataset isn't huge yet.
        
        all_media = await service.media_repo.get_all()
        anime_list = [m for m in all_media if m.type == 'anime']
        drama_list = [m for m in all_media if m.type == 'drama']

        # Generate Anime List
        if anime_list:
            filename = "Animelar_royxati.txt"
            with open(filename, "w", encoding="utf-8") as file:
                file.write("Botidagi barcha Animelar ro'yxati:\n\n")
                for num, i in enumerate(anime_list, 1):
                    text = f"""
----  {num}  ----
Nomi : [ {i.name} ]
Janri : {i.genre.replace(',', ' ')}"""
                    file.write(text)
            
            document = FSInputFile(filename)
            await message.answer_document(document, caption="🔸<b>Animelar ro'yxati</b>", parse_mode="HTML")
            os.remove(filename)

        # Generate Drama List
        if drama_list:
            filename = "Dramalar_royxati.txt"
            with open(filename, "w", encoding="utf-8") as file:
                file.write("Botidagi barcha Dramalar ro'yxati:\n\n")
                for num, i in enumerate(drama_list, 1):
                    text = f"""
----  {num}  ----
Nomi : [ {i.name} ]
Janri : {i.genre.replace(',', ' ')}"""
                    file.write(text)
            
            document = FSInputFile(filename)
            await message.answer_document(document, caption="🔹<b>Dramalar ro'yxati</b>", parse_mode="HTML")
            os.remove(filename)

@router.message(F.text == "OnGoing animelar🧧")
async def cmd_ongoing(message: types.Message):
     # Placeholder: Needs repo method for 'loading' status
    async with AsyncSessionLocal() as session:
         # Quick implementation using get_all + filter
        service = MediaService(session)
        all_media = await service.media_repo.get_all()
        ongoing = [m for m in all_media if m.status == 'ongoing']
        
        if ongoing:
            builder = InlineKeyboardBuilder()
            for m in ongoing:
                builder.button(text=f"{m.name}", callback_data=f"media_{m.id}")
            builder.adjust(1)
            
            await message.answer("<b>🧧OnGoing Animelar:</b>", parse_mode="HTML", reply_markup=builder.as_markup())
        else:
            await message.answer("<b>Hozirda OnGoing animelar yo'q</b>", parse_mode="HTML")
