from app.infrastructure.cache.redis_client import get_redis
import json

class BroadcastService:
    QUEUE_KEY = "broadcast_queue"

    async def schedule_broadcast(self, message_text: str, admin_id: int):
        """
        Push broadcast task to queue.
        In a real scenario, this might push a task ID, and the worker fetches users.
        Or push the message content and the worker iterates all users.
        """
        redis = await get_redis()
        task = {
            "type": "broadcast",
            "text": message_text,
            "admin_id": admin_id
        }
        await redis.lpush(self.QUEUE_KEY, json.dumps(task))
        await redis.close()
