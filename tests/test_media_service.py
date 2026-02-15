import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.media_service import MediaService
from app.infrastructure.database.models.media import Media

@pytest.mark.asyncio
async def test_search_media_found():
    # Mock dependencies
    mock_session = AsyncMock()
    service = MediaService(mock_session)
    
    # Mock Repository result
    mock_media = Media(id=1, name="Test Movie", type="movie")
    service.media_repo.search_by_name = AsyncMock(return_value=[mock_media])
    service._get_from_cache = AsyncMock(return_value=None) # Cache miss
    service._set_to_cache = AsyncMock()

    # Action
    results = await service.search_media("Test")

    # Assert
    assert len(results) == 1
    assert results[0].name == "Test Movie"
    service.media_repo.search_by_name.assert_called_once()

@pytest.mark.asyncio
async def test_search_media_empty():
    mock_session = AsyncMock()
    service = MediaService(mock_session)
    service.media_repo.search_by_name = AsyncMock(return_value=[])
    service._get_from_cache = AsyncMock(return_value=None)

    results = await service.search_media("Unknown")
    assert len(results) == 0
