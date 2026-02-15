from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from app.infrastructure.cache.redis_client import get_redis

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 0.5):
        self.limit = limit

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)
            
        user_id = event.from_user.id
        key = f"throttle:{user_id}"
        
        redis = await get_redis()
        # Simple token bucket or leaky bucket algorithm can be used.
        # Here we just check if key exists (simple lock)
        
        is_throttled = await redis.get(key)
        if is_throttled:
            # Drop update or warn
            # await event.answer("Too many requests!") 
            return
            
        await redis.set(key, "1", px=int(self.limit * 1000))
        await redis.close()
        
        return await handler(event, data)
