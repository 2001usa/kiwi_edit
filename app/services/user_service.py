from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.user_repository import UserRepository # Implied existence or need to create
from app.infrastructure.database.models.user import User

class UserService:
    def __init__(self, session: AsyncSession):
        # We assume UserRepository exists or use direct DB access in prototype.
        # For strict service layer, we should have a repo.
        # Let's write raw SQL wrapper here if repo doesn't exist yet, 
        # or assuming the previous steps implied a generic repo.
        self.session = session

    async def register_user(self, telegram_id: int, username: str = None, full_name: str = None) -> User:
        """
        Register a new user or update existing one.
        """
        # Upsert logic would be here
        # For simplicity in this demo, check existing
        user = await self.session.get(User, telegram_id)
        if not user:
            user = User(id=telegram_id, username=username, full_name=full_name)
            self.session.add(user)
            await self.session.commit()
        return user

    async def is_admin(self, telegram_id: int) -> bool:
        from app.core.config import settings
        return telegram_id in settings.ADMIN_IDS
