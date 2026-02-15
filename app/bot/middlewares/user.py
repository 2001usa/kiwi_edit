from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_service import UserService

class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Get user from event
        user: User = data.get("event_from_user")
        if not user:
            return await handler(event, data)
            
        session: AsyncSession = data.get("db_session")
        if not session:
             # Should be after DbSessionMiddleware
             return await handler(event, data)
             
        service = UserService(session)
        # Register or update user
        db_user = await service.register_user(
            telegram_id=user.id,
            username=user.username,
            full_name=user.full_name
        )
        
        # Inject db_user into handler data if needed
        data["user"] = db_user
        
        return await handler(event, data)
