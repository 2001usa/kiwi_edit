import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        
        if isinstance(event, Message):
            logger.info(f"MSG | User: {user.id if user else 'N/A'} | Text: {event.text[:20] if event.text else 'Non-text'}")
        elif isinstance(event, CallbackQuery):
            logger.info(f"CB  | User: {user.id if user else 'N/A'} | Data: {event.data}")
            
        return await handler(event, data)
