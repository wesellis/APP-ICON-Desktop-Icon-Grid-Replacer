"""
Icon Updater
Backward compatibility wrapper around new modular architecture

This module maintains the IconUpdater class interface while delegating
to the new modular components for actual implementation.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from icon_coordinator import IconCoordinator
from shortcut_updater import ShortcutUpdater

logger = logging.getLogger("ICON.Updater")


class IconUpdater:
    """
    Icon updater - delegates to modular components

    Maintained for backward compatibility. New code should use IconCoordinator directly.
    """

    def __init__(self, api, size: int = 1024):
        """
        Initialize icon updater

        Args:
            api: SteamGridDB API instance
            size: Target icon size (512 or 1024)
        """
        # Delegate to new coordinator
        self._coordinator = IconCoordinator(api, size)
        self._shortcut_updater = ShortcutUpdater()

    async def process_items(
        self, items: List[Dict], auto_apply: bool = False, backup: bool = True
    ) -> Dict:
        """
        Process desktop items and replace icons

        Args:
            items: List of desktop items
            auto_apply: Auto-apply without confirmation
            backup: Create backup before changes

        Returns:
            Results dict with counts
        """
        return await self._coordinator.process_items(items, auto_apply, backup)

    def restore_from_backup(self, backup_file: Path) -> bool:
        """
        Restore icons from backup file

        Args:
            backup_file: Path to backup JSON

        Returns:
            True if successful
        """
        return self._shortcut_updater.restore_from_backup(backup_file)

    def _refresh_icon_cache(self):
        """Refresh icon cache - delegates to coordinator's cache manager"""
        self._coordinator.cache_manager.refresh_cache_and_restart()
