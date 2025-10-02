"""Tests for icon updater"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from icon_updater import IconUpdater


@pytest.mark.asyncio
class TestIconUpdater:
    """Test suite for IconUpdater"""

    def test_init(self):
        """Test updater initialization"""
        mock_api = Mock()
        updater = IconUpdater(mock_api, size=1024)

        assert updater.api == mock_api
        assert updater.size == 1024

    async def test_download_and_convert_icon(self, temp_dir):
        """Test downloading and converting icons"""
        mock_api = AsyncMock()
        mock_api.download_icon = AsyncMock(return_value=True)

        updater = IconUpdater(mock_api, size=512)
        updater.icons_dir = temp_dir

        # Create a fake PNG file
        temp_png = temp_dir / "test_temp.png"
        from PIL import Image

        img = Image.new("RGB", (512, 512), color="red")
        img.save(temp_png)

        with patch.object(updater.api, "download_icon", return_value=True):
            with patch("icon_updater.Path.unlink"):
                # Mock the temp file to exist
                with patch("icon_updater.Image.open", return_value=img):
                    result = await updater._download_and_convert_icon(
                        "https://example.com/icon.png", "TestGame"
                    )

        assert result is not None
        assert result.suffix == ".ico"

    @pytest.mark.asyncio
    async def test_create_backup(self, temp_dir, sample_desktop_item):
        """Test backup creation"""
        mock_api = Mock()
        updater = IconUpdater(mock_api)

        items = [sample_desktop_item]

        with patch("icon_updater.Path.home", return_value=temp_dir):
            backup_path = updater._create_backup(items)

        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.suffix == ".json"

        # Verify backup content
        import json

        with open(backup_path) as f:
            backup_data = json.load(f)

        assert "timestamp" in backup_data
        assert "items" in backup_data
        assert len(backup_data["items"]) == 1

    @patch("icon_updater.win32com.client.Dispatch")
    @patch("icon_updater.pythoncom")
    def test_update_lnk_icon(self, mock_pythoncom, mock_dispatch, sample_desktop_item):
        """Test updating .lnk shortcut icon"""
        mock_api = Mock()
        updater = IconUpdater(mock_api)

        # Mock shortcut object
        mock_shortcut = MagicMock()
        mock_shell = MagicMock()
        mock_shell.CreateShortCut.return_value = mock_shortcut
        mock_dispatch.return_value = mock_shell

        icon_path = Path("C:\\test\\icon.ico")
        result = updater._update_lnk_icon(sample_desktop_item, icon_path)

        assert result is True
        mock_shortcut.Save.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_items_skip_no_icon(self, sample_desktop_item):
        """Test processing items when no icon found"""
        mock_api = AsyncMock()
        mock_api.get_best_icon = AsyncMock(return_value=None)

        updater = IconUpdater(mock_api)

        results = await updater.process_items([sample_desktop_item], auto_apply=True, backup=False)

        assert results["skipped"] == 1
        assert results["success"] == 0
        assert results["failed"] == 0
