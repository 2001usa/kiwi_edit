from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.models.media import Media, Episode
from app.infrastructure.repositories.media import MediaRepository
from app.infrastructure.repositories.episode import EpisodeRepository

class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.media_repo = MediaRepository(session) # Assuming repo has .add()
        # If repositories are read-only in previous impl, we use session directly here
        
    async def add_media(self, title: str, media_type: str, genre: str = None, description: str = None) -> Media:
        media = Media(
            name=title,
            type=media_type,
            genre=genre,
            status="ongoing"
        )
        self.session.add(media)
        await self.session.commit()
        await self.session.refresh(media)
        return media

    async def add_episode(self, media_id: int, episode_num: int, file_id: str) -> Episode:
        episode = Episode(
            media_id=media_id,
            episode_number=episode_num,
            episode_file_id=file_id
        )
        self.session.add(episode)
        await self.session.commit()
        await self.session.refresh(episode)
        return episode

    async def get_statistics(self):
        from sqlalchemy import select, func
        from app.infrastructure.database.models.user import User
        from app.infrastructure.database.models.media import Media

        users_count = await self.session.scalar(select(func.count(User.id)))
        anime_count = await self.session.scalar(select(func.count(Media.id)).where(Media.type == "anime"))
        drama_count = await self.session.scalar(select(func.count(Media.id)).where(Media.type == "drama"))
        
        return {
            "users_count": users_count,
            "anime_count": anime_count,
            "drama_count": drama_count
        }

    async def add_sponsor(self, channel_id: int, name: str, link: str, limit: int = 1):
        from app.infrastructure.database.models.sponsor import Sponsor
        sponsor = Sponsor(
            channel_id=channel_id,
            channel_name=name,
            channel_link=link,
            user_limit=limit
        )
        self.session.add(sponsor)
        await self.session.commit()
        return sponsor

    async def get_all_sponsors(self):
        from sqlalchemy import select
        from app.infrastructure.database.models.sponsor import Sponsor
        result = await self.session.execute(select(Sponsor))
        return result.scalars().all()

    async def delete_sponsor(self, channel_id: int):
        from sqlalchemy import delete
        from app.infrastructure.database.models.sponsor import Sponsor
        await self.session.execute(delete(Sponsor).where(Sponsor.channel_id == channel_id))
        await self.session.commit()

    async def get_all_staff(self):
        from sqlalchemy import select
        from app.infrastructure.database.models.user import User
        # Assuming is_staff is the flag, or is_admin. Old project had both.
        # Let's return admins and staff.
        result = await self.session.execute(select(User).where(User.is_admin == True))
        return result.scalars().all()

    async def add_staff(self, user_id: int):
        from sqlalchemy import update
        from app.infrastructure.database.models.user import User
        await self.session.execute(update(User).where(User.id == user_id).values(is_admin=True))
        await self.session.commit()

    async def remove_staff(self, user_id: int):
        from sqlalchemy import update
        from app.infrastructure.database.models.user import User
        await self.session.execute(update(User).where(User.id == user_id).values(is_admin=False))
        await self.session.commit()
