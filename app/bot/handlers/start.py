from aiogram import Router, types
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.database.models.user import User
from app.bot.keyboards.default import get_main_menu

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    # Check if user exists
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            id=user_id,
            username=username,
            full_name=full_name,
            language=message.from_user.language_code
        )
        session.add(user)
        # Commit happens automatically if managed correctly, or manual commit here
        await session.commit()
        await message.answer(
            f"👋 <b>Botimizga xush kelibsiz</b>, {full_name}!",
            reply_markup=get_main_menu()
        )
    else:
        await message.answer(
            f"Salom yana bir bor, {full_name}!",
            reply_markup=get_main_menu()
        )
