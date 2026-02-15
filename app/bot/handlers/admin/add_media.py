from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.bot.states.admin import AddMediaStates
from app.services.admin_service import AdminService
from app.core.config import settings

router = Router()

# Filter for admin check could be better placed in middleware or filter
def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS

@router.message(F.text == "/add_media")
async def start_add_media(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer(f"⛔️ Siz admin emassiz. ID: {message.from_user.id}")
        return
    await message.answer("🎬 Kino nomini kiriting:")
    await state.set_state(AddMediaStates.waiting_for_title)

@router.message(AddMediaStates.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Turi qanday? (anime/movie/series)")
    await state.set_state(AddMediaStates.waiting_for_type)

@router.message(AddMediaStates.waiting_for_type)
async def process_type(message: types.Message, state: FSMContext):
    await state.update_data(media_type=message.text.lower())
    await message.answer("Janrni kiriting (masalan: Action, Drama):")
    await state.set_state(AddMediaStates.waiting_for_genre)

@router.message(AddMediaStates.waiting_for_genre)
async def process_genre(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    genre = message.text
    
    service = AdminService(session)
    media = await service.add_media(
        title=data['title'],
        media_type=data['media_type'],
        genre=genre
    )
    
    await message.answer(f"✅ <b>{media.name}</b> qo'shildi! ID: {media.id}. Kod: {media.code if hasattr(media, 'code') else 'N/A'}")
    await state.clear()
