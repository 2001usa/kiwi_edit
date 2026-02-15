from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.services.media_service import MediaService

router = Router()

@router.callback_query(F.data.startswith("watch_"))
async def handle_watch_media(callback: types.CallbackQuery, session: AsyncSession):
    media_id = int(callback.data.split("_")[1])
    service = MediaService(session)
    episodes = await service.get_episodes(media_id)
    
    if not episodes:
        await callback.answer("Hozircha qismlar yuklanmagan.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for ep in episodes:
        builder.button(text=f"{ep.episode_number}-qism", callback_data=f"ep_{media_id}_{ep.episode_number}")
    builder.button(text="🔙 Ortga", callback_data=f"media_{media_id}")
    builder.adjust(4) # 4 columns
    
    await callback.message.edit_text(
        "Qismni tanlang:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("ep_"))
async def handle_episode_selection(callback: types.CallbackQuery, session: AsyncSession):
    # ep_mediaid_epnum
    parts = callback.data.split("_")
    media_id = int(parts[1])
    ep_num = int(parts[2])
    
    service = MediaService(session)
    file_id = await service.get_episode_video(media_id, ep_num)
    
    if not file_id:
        await callback.answer("Fayl topilmadi.", show_alert=True)
        return

    await callback.message.answer_video(
        video=file_id,
        caption=f"{ep_num}-qism"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("download_"))
async def handle_download_media(callback: types.CallbackQuery):
    await callback.answer("Tez orada...", show_alert=True)
