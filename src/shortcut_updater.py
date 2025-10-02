"""
Shortcut Updater
Handles updating icons for shortcuts (.lnk, .desktop, .url files)
"""

import configparser
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from platform_handler import PlatformHandler

logger = logging.getLogger("ICON.ShortcutUpdater")


class ShortcutUpdater:
    """Update shortcut icons and manage backups"""

    def __init__(self):
        """Initialize shortcut updater"""
        self.platform_handler = PlatformHandler.get_handler()
        self.backup_dir = Path.home() / ".icon_replacer" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def update_shortcut_icon(self, item: Dict, icon_path: Path) -> bool:
        """
        Update icon for a shortcut file

        Args:
            item: Item dict with path, type, etc.
            icon_path: Path to new icon file

        Returns:
            True if successful, False otherwise
        """
        try:
            if item["type"] in [".lnk", ".desktop"]:
                return self.platform_handler.update_shortcut_icon(Path(item["path"]), icon_path)
            elif item["type"] == ".url":
                return self._update_url_icon(item, icon_path)
            else:
                logger.warning(f"Cannot update icon for {item['type']} files")
                return False

        except Exception as e:
            logger.error(f"Error updating shortcut icon: {e}")
            return False

    def _update_url_icon(self, item: Dict, icon_path: Path) -> bool:
        """
        Update .url shortcut icon

        Args:
            item: Item dict with path
            icon_path: Path to new icon

        Returns:
            True if successful
        """
        try:
            # Read the .url file
            config = configparser.ConfigParser()
            config.read(item["path"], encoding="utf-8")

            # Ensure InternetShortcut section exists
            if not config.has_section("InternetShortcut"):
                config.add_section("InternetShortcut")

            # Set icon file and index
            config.set("InternetShortcut", "IconFile", str(icon_path))
            config.set("InternetShortcut", "IconIndex", "0")

            # Write back to file
            with open(item["path"], "w", encoding="utf-8") as f:
                config.write(f, space_around_delimiters=False)

            logger.info(f"Updated .url icon: {item['path']}")
            return True

        except Exception as e:
            logger.error(f"Error updating .url icon: {e}")
            return False

    def create_backup(self, items: List[Dict]) -> Optional[Path]:
        """
        Create backup of current icon settings

        Args:
            items: List of item dicts to backup

        Returns:
            Path to backup file or None if failed
        """
        try:
            # Create timestamped backup file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"backup_{timestamp}.json"

            # Save item information
            backup_data = {
                "timestamp": timestamp,
                "items": [
                    {
                        "path": item["path"],
                        "name": item["name"],
                        "icon_path": item.get("icon_path"),
                        "icon_index": item.get("icon_index", 0),
                    }
                    for item in items
                ],
            }

            with open(backup_file, "w") as f:
                json.dump(backup_data, f, indent=2)

            logger.info(f"Backup created at {backup_file}")
            return backup_file

        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None

    def restore_from_backup(self, backup_file: Path) -> bool:
        """
        Restore icons from backup file

        Args:
            backup_file: Path to backup JSON file

        Returns:
            True if successful
        """
        try:
            with open(backup_file, "r") as f:
                backup_data = json.load(f)

            # Windows-specific restore using COM
            if sys.platform == "win32":
                return self._restore_windows_backup(backup_data)
            elif sys.platform.startswith("linux"):
                return self._restore_linux_backup(backup_data)
            else:
                logger.error(f"Restore not supported on {sys.platform}")
                return False

        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            return False

    def _restore_windows_backup(self, backup_data: dict) -> bool:
        """Restore Windows shortcuts from backup"""
        try:
            import pythoncom
            import win32com.client

            pythoncom.CoInitialize()

            try:
                shell = win32com.client.Dispatch("WScript.Shell")

                for item_data in backup_data["items"]:
                    if Path(item_data["path"]).suffix.lower() == ".lnk":
                        shortcut = shell.CreateShortCut(item_data["path"])

                        if item_data.get("icon_path"):
                            icon_index = item_data.get("icon_index", 0)
                            shortcut.IconLocation = f"{item_data['icon_path']},{icon_index}"
                        else:
                            # Reset to default
                            shortcut.IconLocation = ""

                        shortcut.Save()

                logger.info(f"Restored Windows shortcuts from backup")
                return True

            finally:
                pythoncom.CoUninitialize()

        except Exception as e:
            logger.error(f"Error restoring Windows backup: {e}")
            return False

    def _restore_linux_backup(self, backup_data: dict) -> bool:
        """Restore Linux .desktop files from backup"""
        try:
            for item_data in backup_data["items"]:
                if Path(item_data["path"]).suffix.lower() == ".desktop":
                    config = configparser.ConfigParser()
                    config.read(item_data["path"], encoding="utf-8")

                    if config.has_section("Desktop Entry"):
                        if item_data.get("icon_path"):
                            config.set("Desktop Entry", "Icon", item_data["icon_path"])
                        else:
                            # Remove icon entry to reset to default
                            config.remove_option("Desktop Entry", "Icon")

                        with open(item_data["path"], "w", encoding="utf-8") as f:
                            config.write(f, space_around_delimiters=False)

            logger.info(f"Restored Linux .desktop files from backup")
            return True

        except Exception as e:
            logger.error(f"Error restoring Linux backup: {e}")
            return False
