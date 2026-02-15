from typing import List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.models.media import Media

class MediaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_code(self, code: int) -> Optional[Media]:
        result = await self.session.execute(select(Media).where(Media.code == code))
        return result.scalar_one_or_none()

    async def search_by_name(self, query: str, limit: int = 10) -> List[Media]:
        stmt = select(Media).where(
            or_(
                Media.name.ilike(f"%{query}%"),
                Media.original_name.ilike(f"%{query}%")
            )
        ).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_latest(self, limit: int = 10) -> List[Media]:
        stmt = select(Media).order_by(Media.id.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all(self) -> List[Media]:
        result = await self.session.execute(select(Media))
        return list(result.scalars().all())
