from typing import List, Optional
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.media import MediaRepository
from app.infrastructure.repositories.episode import EpisodeRepository
from app.infrastructure.database.models.media import Media, Episode
from app.infrastructure.cache.redis_client import get_redis

class MediaService:
    def __init__(self, session: AsyncSession):
        self.media_repo = MediaRepository(session)
        self.episode_repo = EpisodeRepository(session)
        self.redis = None # Will be initialized on demand via get_redis()

    async def _get_from_cache(self, key: str):
        redis = await get_redis()
        data = await redis.get(key)
        return json.loads(data) if data else None

    async def _set_to_cache(self, key: str, data: any, expire: int = 3600):
        redis = await get_redis()
        # Serialize objects to dicts if needed
        if isinstance(data, list):
            serialized = [
                 {k: v for k, v in item.__dict__.items() if not k.startswith('_')} 
                 if hasattr(item, "__dict__") else item
                 for item in data
            ]
        elif hasattr(data, "__dict__"):
            serialized = {k: v for k, v in data.__dict__.items() if not k.startswith('_')}
        else:
            serialized = data
            
        await redis.set(key, json.dumps(serialized), ex=expire)

    async def search_media(self, query: str) -> List[Media]:
        clean_query = query.strip().lower()
        if not clean_query:
            return []

        cache_key = f"search:{clean_query}"
        cached_data = await self._get_from_cache(cache_key)
        
        if cached_data:
            return [Media(**item) for item in cached_data]

        results = await self.media_repo.search_by_name(clean_query)
        
        if results:
            await self._set_to_cache(cache_key, results, expire=600)
        
        return results

    async def get_media_by_code(self, code: int) -> Optional[Media]:
        cache_key = f"media:code:{code}"
        cached_data = await self._get_from_cache(cache_key)
        
        if cached_data:
            return Media(**cached_data)

        media = await self.media_repo.get_by_code(code)
        
        if media:
            await self._set_to_cache(cache_key, media, expire=3600)
            
        return media

    async def get_episodes(self, media_id: int) -> List[Episode]:
        cache_key = f"episodes:{media_id}"
        cached_data = await self._get_from_cache(cache_key)
        
        if cached_data:
             return [Episode(**item) for item in cached_data]

        episodes = await self.episode_repo.get_by_media_id(media_id)
        
        if episodes:
            await self._set_to_cache(cache_key, episodes, expire=3600)
        
        return episodes

    async def get_episode_video(self, media_id: int, episode_num: int) -> Optional[str]:
        cache_key = f"file_id:{media_id}:{episode_num}"
        cached_file_id = await self._get_from_cache(cache_key)
        
        if cached_file_id:
            return cached_file_id

        episode = await self.episode_repo.get_episode(media_id, episode_num)
        if episode and episode.episode_file_id:
            await self._set_to_cache(cache_key, episode.episode_file_id, expire=86400)
            return episode.episode_file_id
        return None

    async def preload_all_media(self):
        media_list = await self.media_repo.get_all()
        count = 0
        for media in media_list:
            # Cache by code
            if media.code:
                await self._set_to_cache(f"media:code:{media.code}", media, expire=86400)
            
            # Cache by search query (name and original_name)
            # This is a bit tricky for search, as search uses 'ilike %query%'. 
            # We can't easily preload all possible search substrings. 
            # But we can at least ensure if someone gets by code, it's fast.
            # For strict name match, we could cache, but search_media logic expects a list.
            
            # Let's just warm up the object itself if we had a "get_by_id" or similar.
            # Currently get_media_by_code is the critical one for "Code orqali qidiruv".
            count += 1
            
        print(f"Preloaded {count} media items to Redis.")
