"""Tests for desktop scanner"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from desktop_scanner import DesktopScanner


class TestDesktopScanner:
    """Test suite for DesktopScanner"""

    def test_init(self):
        """Test scanner initialization"""
        scanner = DesktopScanner()
        assert scanner.supported_types == [".lnk", ".exe", ".url"]

    def test_clean_name(self):
        """Test name cleaning"""
        scanner = DesktopScanner()

        # Test removing "- Shortcut"
        assert scanner._clean_name("Steam - Shortcut") == "Steam"

        # Test removing parentheses
        assert scanner._clean_name("Game (2)") == "Game"

        # Test removing brackets
        assert scanner._clean_name("App [v1.0]") == "App"

        # Test removing trailing numbers
        assert scanner._clean_name("Program 2") == "Program"

        # Test removing .exe
        assert scanner._clean_name("application.exe") == "application"

        # Test removing Steam prefix
        assert scanner._clean_name("Steam - Game") == "Game"

        # Test combined
        assert scanner._clean_name("Steam - Cool Game (2) - Shortcut") == "Cool Game"

    def test_clean_name_preserves_valid_name(self):
        """Test that valid names are preserved"""
        scanner = DesktopScanner()

        assert scanner._clean_name("Valid Name") == "Valid Name"
        assert scanner._clean_name("Pac-Man 256") == "Pac-Man 256"

    @patch("desktop_scanner.Path")
    def test_scan_desktop_empty(self, mock_path):
        """Test scanning empty desktop"""
        scanner = DesktopScanner()

        mock_desktop = MagicMock()
        mock_desktop.exists.return_value = True
        mock_desktop.iterdir.return_value = []
        mock_path.return_value = mock_desktop
        mock_path.home.return_value = mock_desktop

        items = scanner.scan_desktop()
        assert items == []

    @patch("desktop_scanner.win32com.client.Dispatch")
    @patch("desktop_scanner.pythoncom")
    def test_analyze_shortcut(self, mock_pythoncom, mock_dispatch):
        """Test analyzing a .lnk shortcut"""
        scanner = DesktopScanner()

        # Mock shortcut object
        mock_shortcut = MagicMock()
        mock_shortcut.Targetpath = "C:\\Program Files\\Test\\Test.exe"
        mock_shortcut.IconLocation = "C:\\Program Files\\Test\\Test.exe,0"

        mock_shell = MagicMock()
        mock_shell.CreateShortCut.return_value = mock_shortcut
        mock_dispatch.return_value = mock_shell

        item = {
            "path": "C:\\Users\\Test\\Desktop\\Test.lnk",
            "filename": "Test.lnk",
            "name": "Test",
            "type": ".lnk",
            "target": None,
            "icon_path": None,
            "icon_index": 0,
        }

        scanner._analyze_shortcut(Path(item["path"]), item)

        assert item["target"] == "C:\\Program Files\\Test\\Test.exe"
        assert item["icon_path"] == "C:\\Program Files\\Test\\Test.exe"
        assert item["icon_index"] == 0

    def test_get_icon_path(self):
        """Test getting icon path from item"""
        scanner = DesktopScanner()

        # Test with explicit icon_path
        item = {"path": "test.lnk", "icon_path": "custom_icon.ico", "target": "app.exe"}
        assert scanner.get_icon_path(item) == "custom_icon.ico"

        # Test with target fallback
        item = {"path": "test.lnk", "icon_path": None, "target": "app.exe"}
        assert scanner.get_icon_path(item) == "app.exe"

        # Test with path fallback
        item = {"path": "test.lnk", "icon_path": None, "target": None}
        assert scanner.get_icon_path(item) == "test.lnk"
