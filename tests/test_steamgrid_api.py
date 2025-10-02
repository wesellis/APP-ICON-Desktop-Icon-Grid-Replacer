"""Tests for SteamGridDB API integration"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from steamgrid_api import SteamGridAPI


@pytest.mark.asyncio
class TestSteamGridAPI:
    """Test suite for SteamGridDB API"""

    async def test_init(self, mock_api_key):
        """Test API initialization"""
        api = SteamGridAPI(mock_api_key)
        assert api.api_key == mock_api_key
        assert api.base_url == "https://www.steamgriddb.com/api/v2"
        assert api.session is None

    async def test_context_manager(self, mock_api_key):
        """Test async context manager"""
        async with SteamGridAPI(mock_api_key) as api:
            assert api.session is not None
            assert not api.session.closed

    async def test_search_game_by_name(self, mock_api_key, sample_game_data):
        """Test searching for games by name"""
        async with SteamGridAPI(mock_api_key) as api:
            # Mock the aiohttp response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=sample_game_data)

            with patch.object(api.session, 'get', return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock())):
                result = await api.search_game_by_name("Test Game")

            assert result is not None
            assert result['name'] == "Test Game"
            assert result['id'] == 12345

    async def test_search_game_not_found(self, mock_api_key):
        """Test searching for non-existent game"""
        async with SteamGridAPI(mock_api_key) as api:
            mock_response = AsyncMock()
            mock_response.status = 404

            with patch.object(api.session, 'get', return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock())):
                result = await api.search_game_by_name("NonExistent")

            assert result is None

    async def test_cache_hit(self, mock_api_key, sample_game_data):
        """Test that cache works correctly"""
        async with SteamGridAPI(mock_api_key) as api:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=sample_game_data)

            with patch.object(api.session, 'get', return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock())) as mock_get:
                # First call should hit the API
                result1 = await api.search_game_by_name("Test Game")
                # Second call should use cache
                result2 = await api.search_game_by_name("Test Game")

                assert result1 == result2
                # Should only call API once
                assert mock_get.call_count == 1

    async def test_get_best_icon(self, mock_api_key, sample_game_data, sample_icon_data):
        """Test getting best icon for a game"""
        async with SteamGridAPI(mock_api_key) as api:
            # Mock game search
            mock_game_response = AsyncMock()
            mock_game_response.status = 200
            mock_game_response.json = AsyncMock(return_value=sample_game_data)

            # Mock grids response
            mock_grids_response = AsyncMock()
            mock_grids_response.status = 200
            mock_grids_response.json = AsyncMock(return_value=sample_icon_data)

            with patch.object(api.session, 'get') as mock_get:
                mock_get.return_value = AsyncMock(
                    __aenter__=AsyncMock(side_effect=[mock_game_response, mock_grids_response]),
                    __aexit__=AsyncMock()
                )

                result = await api.get_best_icon("Test Game", 1024)

            assert result is not None
            assert 'url' in result

    def test_find_best_match(self, mock_api_key):
        """Test game name matching algorithm"""
        api = SteamGridAPI(mock_api_key)

        games = [
            {"id": 1, "name": "Test Game 2"},
            {"id": 2, "name": "Test Game"},
            {"id": 3, "name": "Another Test Game"}
        ]

        # Should find exact match
        result = api._find_best_match("Test Game", games)
        assert result['id'] == 2

    def test_find_best_match_with_numbers(self, mock_api_key):
        """Test game name matching with numbers"""
        api = SteamGridAPI(mock_api_key)

        games = [
            {"id": 1, "name": "Pac-Man"},
            {"id": 2, "name": "Pac-Man 256"},
            {"id": 3, "name": "Pac-Man Championship"}
        ]

        # Should prefer game with matching number
        result = api._find_best_match("Pac-Man 256", games)
        assert result['id'] == 2

    async def test_download_icon(self, mock_api_key, temp_dir):
        """Test icon download"""
        async with SteamGridAPI(mock_api_key) as api:
            save_path = temp_dir / "test_icon.png"

            mock_response = AsyncMock()
            mock_response.status = 200
            mock_content = Mock()
            mock_content.iter_chunked = AsyncMock(return_value=[b'test data'])
            mock_response.content = mock_content

            with patch.object(api.session, 'get', return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock())):
                result = await api.download_icon("https://example.com/icon.png", save_path)

            assert result is True
            assert save_path.exists()
