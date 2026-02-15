import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.core.config import settings
from app.infrastructure.database.session import AsyncSessionLocal
from app.bot.middlewares.db_session import DbSessionMiddleware
from app.bot.middlewares.logging import LoggingMiddleware
from app.bot.middlewares.user import UserMiddleware
from app.bot.handlers import start, search, media
from app.bot.handlers.admin import add_media

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    
    # Debug: Env Vars
    import os
    logging.info(f"Env POSTGRES_HOST: {os.getenv('POSTGRES_HOST')}")
    logging.info(f"Env DATABASE_URL present: {bool(os.getenv('DATABASE_URL'))}")

    db_url = settings.DATABASE_URL
    if db_url:
        safe_url = db_url.split("@")[-1] if "@" in db_url else "NO_CREDENTIALS"
        logging.info(f"Connecting to Database at: {safe_url}")
    else:
        logging.error("DATABASE_URL is empty!")


    if settings.SENTRY_DSN:
        import sentry_sdk
        sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=1.0)
        logging.info("Sentry initialized")

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Middlewares
    dp.update.middleware(DbSessionMiddleware(session_pool=AsyncSessionLocal))
    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(UserMiddleware())

    # Initialize Database
    from app.infrastructure.database.session import engine
    from app.infrastructure.database.models.base import Base
    # Import all models to ensure they are registered in Base
    import app.infrastructure.database.models.user
    import app.infrastructure.database.models.media
    import app.infrastructure.database.models.sponsor
    
    logging.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Preload Media to Redis
    logging.info("Preloading media to Redis...")
    async with AsyncSessionLocal() as session:
        from app.services.media_service import MediaService
        service = MediaService(session)
        await service.preload_all_media()
    logging.info("Preload complete.")


    # Register routers
    from app.bot.handlers.admin import panel
    dp.include_router(panel.router)
    # dp.include_router(add_media.router) # Removed to avoid conflict with panel.py
    dp.include_router(start.router)
    from app.bot.handlers import menu
    dp.include_router(menu.router)
    dp.include_router(search.router)
    dp.include_router(media.router)

    logging.info("Starting bot...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
