from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.database.session import get_db
from app.infrastructure.database.models.media import Media

router = APIRouter()

@router.get("/", response_model=List[dict])
async def read_medias(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve medias.
    """
    result = await db.execute(select(Media).offset(skip).limit(limit))
    medias = result.scalars().all()
    # Pydantic models should be used here for serialization strictly, 
    # but for prototype returning dicts/ORM objects works with FastAPI jsonable_encoder
    return medias

@router.post("/", response_model=dict)
async def create_media(
    media_in: dict,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new media.
    """
    # Simple dict implementation for speed. Use Pydantic schemas in production.
    media = Media(**media_in)
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media

@router.get("/{media_id}", response_model=dict)
async def read_media(
    media_id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get media by ID.
    """
    media = await db.get(Media, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return media
