from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.models.user import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, telegram_id: int) -> Optional[User]:
        return await self.session.get(User, telegram_id)

    async def add(self, user: User) -> User:
        self.session.add(user)
        # Commit is usually handled by the service or unit of work, 
        # but for simplicity in this active record style repo we might leave it to service
        return user
