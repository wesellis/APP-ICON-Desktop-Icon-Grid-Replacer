"""
Game Matching Algorithm
Smart matching of shortcut names to SteamGridDB game entries with scoring
"""

import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger('ICON.Matcher')


class GameMatcher:
    """Intelligent game name matching with scoring algorithm"""

    def __init__(self):
        """Initialize game matcher"""
        pass

    def find_best_match(self, query: str, games: List[Dict]) -> Dict:
        """
        Find the best matching game from search results

        Args:
            query: Search query (cleaned game name)
            games: List of game dictionaries from API

        Returns:
            Best matching game dictionary
        """
        query_lower = query.lower().strip()

        # First: Look for exact match (case-insensitive)
        for game in games:
            game_name = game.get('name', '').lower().strip()
            if game_name == query_lower:
                logger.debug(f"Exact match found: {game.get('name')}")
                return game

        # Score all games and return best match
        scored_games = self._score_games(query, games)

        if not scored_games:
            logger.debug(f"No good match found, using first result")
            return games[0]

        # Return highest scoring game
        best_match = max(scored_games, key=lambda x: x[1])
        logger.debug(f"Best match: {best_match[0].get('name')} (score: {best_match[1]})")
        return best_match[0]

    def find_all_matches(self, query: str, games: List[Dict]) -> List[Tuple[Dict, float]]:
        """
        Find all matching games with their scores

        Args:
            query: Search query (cleaned game name)
            games: List of game dictionaries from API

        Returns:
            List of (game, score) tuples sorted by score (highest first)
        """
        query_lower = query.lower().strip()

        # First: Look for exact match (case-insensitive)
        for game in games:
            game_name = game.get('name', '').lower().strip()
            if game_name == query_lower:
                logger.debug(f"Exact match found: {game.get('name')}")
                return [(game, 1000.0)]  # Only return exact match if found

        # Score all games
        scored_games = self._score_games(query, games)

        # Sort by score descending
        scored_games.sort(key=lambda x: x[1], reverse=True)

        # Return top 5 or all if less than 5
        return scored_games[:5] if scored_games else [(games[0], 0.0)]

    def _score_games(self, query: str, games: List[Dict]) -> List[Tuple[Dict, float]]:
        """
        Score all games based on how well they match the query

        Args:
            query: Search query
            games: List of game dictionaries

        Returns:
            List of (game, score) tuples (only games with positive scores)
        """
        query_lower = query.lower().strip()

        # Extract numbers and words from query
        query_numbers = set(re.findall(r'\d+', query_lower))
        query_words = set(query_lower.split())

        scored_games = []

        for game in games:
            game_name = game.get('name', '').lower().strip()
            score = self._calculate_score(query_lower, query_numbers, query_words, game_name)

            if score > 0:  # Only include games with positive score
                scored_games.append((game, score))

        return scored_games

    def _calculate_score(
        self,
        query_lower: str,
        query_numbers: set,
        query_words: set,
        game_name: str
    ) -> float:
        """
        Calculate match score for a single game

        Scoring criteria:
        - Exact match: 1000 points
        - Starts with query: 900 points
        - Contains query: 800 points
        - Contains all words: 700 points
        - Matching numbers: +200 points
        - Missing numbers: skip game entirely
        - Missing words: -100 per word
        - Longer names: -0.1 per character

        Args:
            query_lower: Lowercase query string
            query_numbers: Set of numbers in query
            query_words: Set of words in query
            game_name: Lowercase game name to score

        Returns:
            Score (higher is better, 0 or negative means poor match)
        """
        game_numbers = set(re.findall(r'\d+', game_name))
        game_words = set(game_name.split())

        # CRITICAL: If query has numbers, the game MUST have those exact numbers
        # This prevents matching "Pac-Man" when looking for "Pac-Man 256"
        if query_numbers:
            if not query_numbers.issubset(game_numbers):
                logger.debug(
                    f"Skipping '{game_name}' - numbers don't match "
                    f"(query: {query_numbers}, game: {game_numbers})"
                )
                return 0.0

        score = 0.0

        # Base score based on string matching
        if game_name == query_lower:
            score = 1000.0  # Exact match
        elif game_name.startswith(query_lower):
            score = 900.0  # Query at start
        elif query_lower in game_name:
            score = 800.0  # Query contained
        elif all(word in game_name for word in query_words):
            score = 700.0  # All words present
            # Bonus for same word count
            if len(game_words) == len(query_words):
                score += 50.0
        else:
            # Poor match if none of the above criteria met
            score = 100.0

        # Bonus: Numbers match exactly
        if query_numbers and query_numbers == game_numbers:
            score += 200.0

        # Penalty: Missing words from query
        missing_words = query_words - game_words
        if missing_words:
            score -= len(missing_words) * 100.0

        # Penalty: Prefer shorter names (more specific)
        # Slight penalty for length to prefer "Game" over "Game: Complete Edition"
        score -= len(game_name) * 0.1

        return score
