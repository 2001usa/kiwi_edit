from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.media_service import MediaService
from app.bot.keyboards.inline import search_results_keyboard, media_details_keyboard

router = Router()

@router.message(F.text & ~F.text.startswith("/"))
async def handle_search_or_code(message: types.Message, session: AsyncSession):
    service = MediaService(session)
    text = message.text.strip()
    
    # Check if text is a code (digits)
    if text.isdigit():
        code = int(text)
        media = await service.get_media_by_code(code)
        if media:
            await message.answer(
                f"🎬 <b>{media.name}</b>\n\nJanr: {media.genre}\nStatus: {media.status}",
                reply_markup=media_details_keyboard(media.id)
            )
        else:
            await message.answer("❌ Bunday kodli media topilmadi.")
        return

    # Treat as search query
    results = await service.search_media(text)
    if not results:
        await message.answer("🔍 Hech narsa topilmadi.")
        return
    
    await message.answer(
        "🔍 <b>Qidiruv natijalari:</b>",
        reply_markup=search_results_keyboard(results)
    )

@router.callback_query(F.data.startswith("media_"))
async def handle_media_selection(callback: types.CallbackQuery, session: AsyncSession):
    media_id = int(callback.data.split("_")[1])
    # For now, just show menu. If we need details, use service.get_media_details(media_id)
    await callback.message.edit_text(
        f"Media ID: {media_id}\nTanlang:",
        reply_markup=media_details_keyboard(media_id)
    )

