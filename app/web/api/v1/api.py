from fastapi import APIRouter
from app.web.api.v1.endpoints import media

api_router = APIRouter()
api_router.include_router(media.router, prefix="/media", tags=["media"])
