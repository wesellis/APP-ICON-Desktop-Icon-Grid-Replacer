"""
Desktop Scanner
Scan desktop for shortcuts and executables
"""

import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List

from platform_handler import PlatformHandler

logger = logging.getLogger("ICON.Scanner")


class DesktopScanner:
    """Scan desktop for items that can have icons replaced"""

    def __init__(self):
        # Platform-specific supported types
        if sys.platform == "win32":
            self.supported_types = [".lnk", ".exe", ".url"]
        elif sys.platform.startswith("linux"):
            self.supported_types = [".desktop"]
        else:
            self.supported_types = []

        self.platform_handler = PlatformHandler.get_handler()

    def scan_desktop(self, desktop_path: str = None) -> List[Dict]:
        """Scan desktop for shortcuts and executables"""
        if desktop_path is None:
            desktop_path = str(Path.home() / "Desktop")

        desktop = Path(desktop_path)
        if not desktop.exists():
            logger.error(f"Desktop path not found: {desktop_path}")
            return []

        items = []

        # Scan for supported file types
        for file_path in desktop.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_types:
                item = self._analyze_item(file_path)
                if item:
                    items.append(item)

        logger.info(f"Found {len(items)} items on desktop")
        return items

    def _analyze_item(self, file_path: Path) -> Dict:
        """Analyze a desktop item and extract information"""
        item = {
            "path": str(file_path),
            "filename": file_path.name,
            "name": file_path.stem,
            "type": file_path.suffix.lower(),
            "target": None,
            "icon_path": None,
            "icon_index": 0,
        }

        # Extract clean name (remove common suffixes)
        clean_name = self._clean_name(item["name"])
        item["clean_name"] = clean_name

        # Get additional info based on type
        if item["type"] == ".lnk":
            self._analyze_shortcut(file_path, item)
        elif item["type"] == ".exe":
            item["target"] = str(file_path)
            item["icon_path"] = str(file_path)

        logger.debug(f"Analyzed: {item['name']} -> {item['clean_name']}")
        return item

    def _analyze_shortcut(self, file_path: Path, item: Dict):
        """Extract information from a shortcut (.lnk on Windows, .desktop on Linux)"""
        try:
            self.platform_handler.get_shortcut_info(file_path, item)
        except Exception as e:
            logger.warning(f"Failed to analyze shortcut {file_path}: {e}")

    def _clean_name(self, name: str) -> str:
        """Clean up name for better search results"""
        # Remove common patterns
        patterns = [
            r"\s*-\s*Shortcut.*$",  # Remove "- Shortcut"
            r"\s*\(.*?\)\s*",  # Remove parentheses content
            r"\s*\[.*?\]\s*",  # Remove bracket content
            # r'\s+\d+$',            # DISABLED: Don't remove trailing numbers (breaks sequels like "Game 2")
            r"\.exe$",  # Remove .exe extension
            r"^Steam\s*-\s*",  # Remove "Steam - " prefix
        ]

        clean = name
        for pattern in patterns:
            clean = re.sub(pattern, "", clean, flags=re.IGNORECASE)

        # Trim whitespace
        clean = clean.strip()

        # If we removed everything, use original
        if not clean:
            clean = name

        return clean

    def get_icon_path(self, item: Dict) -> str:
        """Get the icon path for an item"""
        # Priority: explicit icon_path > target > file path
        if item.get("icon_path"):
            return item["icon_path"]
        elif item.get("target"):
            return item["target"]
        else:
            return item["path"]
