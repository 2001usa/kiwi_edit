import asyncio
import json
import logging
import signal
from aiogram import Bot
from app.core.config import settings
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.database.session import AsyncSessionLocal
from sqlalchemy import select
from app.infrastructure.database.models.user import User

# Configure structured logging (simplified)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("worker")

class WorkerService:
    def __init__(self):
        self.running = True
        self.bot = Bot(token=settings.BOT_TOKEN)

    async def process_broadcast(self, text: str):
        logger.info("Starting broadcast task")
        async with AsyncSessionLocal() as session:
            try:
                # Optimized: fetching only IDs in chunks (cursor) would be better for 50k+
                # For now using stream()
                stmt = select(User.id).execution_options(yield_per=100)
                result = await session.stream(stmt)
                
                count = 0
                async for row in result:
                    if not self.running:
                        break
                        
                    user_id = row[0]
                    try:
                        await self.bot.send_message(user_id, text)
                        count += 1
                        # Rate limit respected
                        await asyncio.sleep(0.04) # ~25 msg/sec
                    except Exception as e:
                        # Log but continue
                        pass
                
                logger.info(f"Broadcast completed. Messages sent: {count}")
            except Exception as e:
                logger.error(f"Broadcast failed: {e}")

    async def run(self):
        redis = await get_redis()
        logger.info("Worker service started. Waiting for tasks...")
        
        while self.running:
            try:
                # Blocking pop with timeout so we can check self.running
                task_raw = await redis.brpop("broadcast_queue", timeout=2)
                
                if task_raw:
                    _, data = task_raw
                    task = json.loads(data)
                    
                    if task.get("type") == "broadcast":
                        await self.process_broadcast(task.get("text"))
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                await asyncio.sleep(5)
        
        logger.info("Worker shutting down...")
        await self.bot.session.close()

async def main():
    service = WorkerService()
    
    # Graceful shutdown handler
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: setattr(service, 'running', False))
    
    await service.run()

if __name__ == "__main__":
    try:
        if os.name == 'nt':
            # Windows signal handling workaround
            asyncio.run(main()) 
        else:
             # Unix
            asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        logger.critical(f"Fatal worker error: {e}")
