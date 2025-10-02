"""
SteamGridDB API Integration
Search and download high-quality game icons from SteamGridDB
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional

import aiohttp

from game_matcher import GameMatcher

logger = logging.getLogger("ICON.API")


class SteamGridAPI:
    """Interface for SteamGridDB API operations"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.steamgriddb.com/api/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "ICON-DesktopReplacer/1.0",
            "Accept": "application/json",
        }
        self.session: Optional[aiohttp.ClientSession] = None

        # Simple in-memory cache
        self._game_cache = {}  # name -> game_data
        self._icon_cache = {}  # game_id -> icon_list

        # Game matcher for intelligent name matching
        self.matcher = GameMatcher()

    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            connector = aiohttp.TCPConnector(limit=50, limit_per_host=20, ttl_dns_cache=300)
            self.session = aiohttp.ClientSession(
                headers=self.headers, timeout=timeout, connector=connector
            )

    async def search_game_by_name(self, name: str, return_all: bool = False):
        """Search for game by name

        Args:
            name: Game name to search for
            return_all: If True, return all matching games with scores. If False, return best match only.

        Returns:
            If return_all=False: Single game dict or None
            If return_all=True: List of (game, score) tuples or None
        """
        # Check cache
        cache_key = f"{name}:{'all' if return_all else 'best'}"
        if cache_key in self._game_cache:
            logger.debug(f"Cache hit for '{name}'")
            return self._game_cache[cache_key]

        await self._ensure_session()

        # Try multiple search variations for punctuation and special characters
        search_queries = [name]

        # Add ASCII-normalized version (ü→u, é→e, etc.) for games like "Brütal Legend"
        import unicodedata

        ascii_name = unicodedata.normalize("NFKD", name).encode("ASCII", "ignore").decode("ASCII")
        if ascii_name != name:
            search_queries.append(ascii_name)

        # Add variations with common punctuation (handles "Wanted Dead" -> "Wanted: Dead")
        words = name.split()
        if len(words) >= 2:
            # Try adding colon after first word (e.g., "Wanted: Dead")
            search_queries.append(f"{words[0]}: {' '.join(words[1:])}")
            # Try with hyphen
            search_queries.append(f"{words[0]} - {' '.join(words[1:])}")

        games = []
        for query in search_queries:
            try:
                url = f"{self.base_url}/search/autocomplete/{query}"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        query_games = data.get("data", [])
                        if query_games:
                            # Add games, avoiding duplicates
                            game_ids = {g.get("id") for g in games}
                            for game in query_games:
                                if game.get("id") not in game_ids:
                                    games.append(game)
                            if query != name:
                                logger.info(f"Found additional results with variation: '{query}'")
            except Exception as e:
                logger.debug(f"Error trying variation '{query}': {e}")
                continue

        # Process results
        if games:
            if return_all:
                # Return all matches with scores
                matches = self.matcher.find_all_matches(name, games)
                self._game_cache[cache_key] = matches
                logger.info(f"Found {len(matches)} potential matches for '{name}'")
                return matches
            else:
                # Find best match
                game_data = self.matcher.find_best_match(name, games)
                self._game_cache[cache_key] = game_data
                logger.info(f"Found game: {game_data.get('name')} (ID: {game_data.get('id')})")
                return game_data
        else:
            logger.warning(f"No results for '{name}'")
            self._game_cache[cache_key] = None
            return None

    async def get_icons(self, game_id: int, dimensions: str = "1024x1024") -> List[Dict]:
        """Get icons for a specific game"""
        # Check cache - include sort in key to bust old cache
        cache_key = (game_id, dimensions, "oldest")
        if cache_key in self._icon_cache:
            logger.debug(f"Cache hit for game ID {game_id} icons")
            return self._icon_cache[cache_key]

        await self._ensure_session()

        try:
            url = f"{self.base_url}/icons/game/{game_id}"
            params = {
                "sort_by": "created",  # Sort by upload date
                "sort_order": "asc",  # Oldest first
            }

            # Add dimension filter if specified
            if dimensions:
                params["dimensions"] = dimensions

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    icons = data.get("data", [])

                    # Cache the result
                    self._icon_cache[cache_key] = icons
                    logger.info(f"Found {len(icons)} icons for game ID {game_id}")
                    return icons
                elif response.status == 404:
                    logger.warning(f"No icons found for game ID {game_id}")
                    self._icon_cache[cache_key] = []
                    return []
                else:
                    text = await response.text()
                    logger.error(f"API Error {response.status}: {text}")
                    return []

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"Error getting icons for game ID {game_id}: {e}")
            return []

    async def get_grids(self, game_id: int, dimensions: str = "1024x1024") -> List[Dict]:
        """Get grid artwork for a specific game (square 1:1 ratio)"""
        # Check cache - include sort in key to bust old cache
        cache_key = (game_id, f"grid_{dimensions}", "oldest")
        if cache_key in self._icon_cache:
            logger.debug(f"Cache hit for game ID {game_id} grids")
            return self._icon_cache[cache_key]

        await self._ensure_session()

        try:
            url = f"{self.base_url}/grids/game/{game_id}"
            params = {
                "sort_by": "created",  # Sort by upload date
                "sort_order": "asc",  # Oldest first
            }

            # Add dimension filter if specified
            if dimensions:
                params["dimensions"] = dimensions

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    grids = data.get("data", [])

                    # Cache the result
                    self._icon_cache[cache_key] = grids
                    logger.info(f"Found {len(grids)} grids for game ID {game_id}")
                    return grids
                elif response.status == 404:
                    logger.warning(f"No grids found for game ID {game_id}")
                    self._icon_cache[cache_key] = []
                    return []
                else:
                    text = await response.text()
                    logger.error(f"API Error {response.status}: {text}")
                    return []

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"Error getting grids for game ID {game_id}: {e}")
            return []

    async def download_icon(self, url: str, save_path: Path) -> bool:
        """Download icon from URL"""
        try:
            # CDN URLs don't need authentication - create a new session without auth headers
            timeout = aiohttp.ClientTimeout(total=60, connect=10)
            async with aiohttp.ClientSession(timeout=timeout) as cdn_session:
                async with cdn_session.get(
                    url, headers={"User-Agent": "ICON-DesktopReplacer/1.0"}
                ) as response:
                    if response.status == 200:
                        save_path.parent.mkdir(parents=True, exist_ok=True)

                        with open(save_path, "wb") as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)

                        logger.info(f"Downloaded icon to {save_path}")
                        return True
                    else:
                        logger.error(f"Download failed: {response.status} for {url}")
                        return False

        except (aiohttp.ClientError, asyncio.TimeoutError, IOError) as e:
            logger.error(f"Error downloading icon: {e}")
            return False

    async def get_best_icon(self, game_name: str, size: int = 1024) -> Optional[Dict]:
        """Get the best icon for a game (oldest first)"""
        # Search for game
        game = await self.search_game_by_name(game_name)
        if not game:
            return None

        game_id = game.get("id")
        if not game_id:
            return None

        # Try to get square grids first (better for desktop icons)
        dimensions = f"{size}x{size}"
        grids = await self.get_grids(game_id, dimensions)

        if grids:
            # Return first (oldest due to API sort)
            return grids[0]

        # Fallback to regular icons
        icons = await self.get_icons(game_id, dimensions)

        if icons:
            # Return first (oldest due to API sort)
            return icons[0]

        return None

    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
