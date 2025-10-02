"""Pytest configuration and fixtures"""

import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp = Path(tempfile.mkdtemp())
    yield temp
    shutil.rmtree(temp, ignore_errors=True)


@pytest.fixture
def mock_api_key():
    """Provide a mock API key"""
    return "test_api_key_12345"


@pytest.fixture
def sample_game_data():
    """Sample game data from SteamGridDB API"""
    return {"data": [{"id": 12345, "name": "Test Game", "types": ["steam"], "verified": True}]}


@pytest.fixture
def sample_icon_data():
    """Sample icon data from SteamGridDB API"""
    return {
        "data": [
            {
                "id": 1,
                "url": "https://example.com/icon1.png",
                "thumb": "https://example.com/icon1_thumb.png",
                "score": 95,
                "votes": 100,
                "width": 1024,
                "height": 1024,
            },
            {
                "id": 2,
                "url": "https://example.com/icon2.png",
                "thumb": "https://example.com/icon2_thumb.png",
                "score": 90,
                "votes": 80,
                "width": 1024,
                "height": 1024,
            },
        ]
    }


@pytest.fixture
def sample_desktop_item():
    """Sample desktop item"""
    return {
        "path": "C:\\Users\\Test\\Desktop\\Test.lnk",
        "filename": "Test.lnk",
        "name": "Test",
        "type": ".lnk",
        "target": "C:\\Program Files\\Test\\Test.exe",
        "icon_path": "C:\\Program Files\\Test\\Test.exe",
        "icon_index": 0,
        "clean_name": "Test",
    }
