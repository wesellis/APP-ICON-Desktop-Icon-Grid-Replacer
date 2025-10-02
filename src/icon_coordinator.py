"""
Icon Coordinator
Orchestrates icon replacement workflow using modular components
"""

import logging
import re
from pathlib import Path
from typing import Dict, List

from icon_cache import IconCacheManager
from icon_downloader import IconDownloader
from shortcut_updater import ShortcutUpdater

logger = logging.getLogger("ICON.Coordinator")


class IconCoordinator:
    """Coordinates the icon replacement process using modular components"""

    def __init__(self, api, size: int = 1024):
        """
        Initialize icon coordinator

        Args:
            api: SteamGridDB API instance
            size: Target icon size (512 or 1024)
        """
        self.api = api
        self.size = size

        # Initialize components
        icons_dir = Path.home() / ".icon_replacer" / "icons"
        self.downloader = IconDownloader(icons_dir, size)
        self.updater = ShortcutUpdater()
        self.cache_manager = IconCacheManager()

    async def process_items(
        self, items: List[Dict], auto_apply: bool = False, backup: bool = True
    ) -> Dict:
        """
        Process desktop items and replace icons

        Args:
            items: List of desktop items to process
            auto_apply: Auto-apply without confirmation
            backup: Create backup before making changes

        Returns:
            Results dict with success, failed, skipped counts
        """
        results = {"success": 0, "failed": 0, "skipped": 0, "backup_path": None}

        # Clear icon cache BEFORE processing
        print("\n[*] Clearing icon cache before processing...")
        self.cache_manager.clear_cache_only()

        # Create backup if requested
        if backup:
            results["backup_path"] = self.updater.create_backup(items)

        # Process each item
        for i, item in enumerate(items, 1):
            print(f"\n[{i}/{len(items)}] {item['name']}")

            # Search for multiple matches to let user choose
            matches = await self.api.search_game_by_name(item["clean_name"], return_all=True)

            if not matches:
                print(f"  ⚠️  No matches found on SteamGridDB")
                results["skipped"] += 1
                continue

            # Handle game selection
            selected_game = self._select_game(item, matches, results)
            if not selected_game:
                continue

            print(f"  Using: {selected_game.get('name')} (ID: {selected_game.get('id')})")

            # Get icon for selected game
            icon_data = await self._get_icon_for_game(selected_game.get("id"))
            if not icon_data:
                print(f"  ⚠️  No icons found for this game")
                results["skipped"] += 1
                continue

            # Show preview info
            print(f"  ✓ Found: {icon_data.get('url', 'N/A')}")
            print(
                f"    Score: {icon_data.get('score', 0)}, Votes: {icon_data.get('votes', 0)} (Oldest icon)"
            )

            # Confirm if not auto
            if not auto_apply:
                response = input(f"  Apply this icon? (y/n/skip all) [y]: ").strip().lower()
                if response == "skip all":
                    print("  Skipping remaining items...")
                    results["skipped"] += len(items) - i + 1
                    break
                elif response == "n":
                    print("  Skipped")
                    results["skipped"] += 1
                    continue

            # Download and apply icon
            success = await self._apply_icon(item, icon_data, selected_game.get("name"))
            if success:
                print(f"  ✅ Icon updated!")
                results["success"] += 1
            else:
                print(f"  ❌ Failed to update icon")
                results["failed"] += 1

        # Refresh cache if any successful updates
        if results["success"] > 0:
            print("\n[*] Refreshing icon cache...")
            self.cache_manager.refresh_cache_and_restart()

        return results

    def _select_game(self, item: Dict, matches: list, results: Dict):
        """Handle game selection from multiple matches"""
        if len(matches) <= 1:
            return matches[0][0]

        # Extract core words from shortcut name
        core_words = re.sub(
            r"\b(19|20)\d{2}\b|\(.*?\)|\bremake\b|\bremastered\b|\bedition\b|\bdeluxe\b|\bgoty\b|\bcollectors?\b",
            "",
            item["clean_name"],
            flags=re.IGNORECASE,
        ).strip()
        first_words = " ".join(core_words.split()[: min(3, len(core_words.split()))])

        # Find games matching core title
        potential_versions = []
        for game, score in matches:
            game_name = game.get("name", "")
            game_core = re.sub(
                r"\b(19|20)\d{2}\b|\(.*?\)|\bremake\b|\bremastered\b|\bedition\b|\bdeluxe\b|\bgoty\b|\bcollectors?\b",
                "",
                game_name,
                flags=re.IGNORECASE,
            ).strip()

            if (
                core_words.lower() in game_core.lower()
                or game_core.lower() in core_words.lower()
                or first_words.lower() in game_core.lower()
            ):
                potential_versions.append((game, score))

        # Also check for similar high scores
        top_score = matches[0][1]
        similar_matches = [m for m in matches if abs(m[1] - top_score) < 200]

        # Use the larger set
        candidates = (
            potential_versions
            if len(potential_versions) > len(similar_matches)
            else similar_matches
        )

        # Check for multiple years
        has_multiple_years = self._has_multiple_years(candidates)

        if len(candidates) > 1 or has_multiple_years:
            return self._prompt_for_game_selection(candidates, results)

        return matches[0][0]

    def _has_multiple_years(self, candidates: list) -> bool:
        """Check if candidates have multiple different years"""
        years_found = set()
        for game, _ in candidates:
            game_name = game.get("name", "")
            year_match = re.findall(r"\b(19|20)\d{2}\b", game_name)
            if year_match:
                years_found.add(year_match[0])
        return len(years_found) > 1

    def _prompt_for_game_selection(self, candidates: list, results: Dict):
        """Prompt user to select from multiple game candidates"""
        print(f"  Multiple matches found:")
        for idx, (game, score) in enumerate(candidates, 1):
            print(f"    {idx}. {game.get('name')} (ID: {game.get('id')}, Score: {score:.1f})")

        while True:
            try:
                choice = (
                    input(f"  Select game (1-{len(candidates)}) or 's' to skip: ").strip().lower()
                )
                if choice == "s":
                    print("  Skipped")
                    results["skipped"] += 1
                    return None
                choice_num = int(choice)
                if 1 <= choice_num <= len(candidates):
                    return candidates[choice_num - 1][0]
                else:
                    print(f"  Please enter a number between 1 and {len(candidates)}")
            except ValueError:
                print(f"  Please enter a number between 1 and {len(candidates)} or 's' to skip")

    async def _get_icon_for_game(self, game_id: int):
        """Get best icon for a game ID"""
        dimensions = f"{self.size}x{self.size}"

        # Try grids first
        grids = await self.api.get_grids(game_id, dimensions)
        if grids:
            return grids[0]

        # Fallback to icons
        icons = await self.api.get_icons(game_id, dimensions)
        if icons:
            return icons[0]

        return None

    async def _apply_icon(self, item: Dict, icon_data: Dict, game_name: str) -> bool:
        """Download icon and apply to shortcut"""
        # Download and convert
        icon_path = await self.downloader.download_and_convert(
            self.api, icon_data.get("url"), game_name
        )

        if not icon_path:
            return False

        # Update shortcut
        return self.updater.update_shortcut_icon(item, icon_path)
