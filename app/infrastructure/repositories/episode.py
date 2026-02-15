from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.models.media import Episode

class EpisodeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_media_id(self, media_id: int) -> List[Episode]:
        stmt = select(Episode).where(Episode.media_id == media_id).order_by(Episode.episode_number.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_episode(self, media_id: int, episode_num: int) -> Episode | None:
        stmt = select(Episode).where(
            Episode.media_id == media_id,
            Episode.episode_number == episode_num
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
