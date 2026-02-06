"""Cache management for bag recorder."""

import hashlib
from pathlib import Path
from typing import List, Optional

# Constants
CACHE_DIR = Path.home() / ".cache" / "bag_recorder"


def get_cache_path() -> Path:
    """Get the cache file path for the current working directory.

    Each working directory gets its own cache file based on a hash of the path.

    Returns:
        Path to the cache file
    """
    # Create cache directory if it doesn't exist
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Generate unique filename based on current working directory
    cwd_hash = hashlib.md5(str(Path.cwd()).encode()).hexdigest()
    return CACHE_DIR / f"{cwd_hash}.cache"


def load_cached_selection(cache_path: Path, topics: List[str]) -> Optional[List[bool]]:
    """Load previously selected topics from cache.

    Args:
        cache_path: Path to cache file
        topics: Current available topics

    Returns:
        List of boolean values indicating checked state, or None if cache not found
    """
    try:
        with open(cache_path, "r") as f:
            cached_topics = {line.strip() for line in f}
        return [topic in cached_topics for topic in topics]
    except FileNotFoundError:
        return None


def save_selection(cache_path: Path, topics: List[str]) -> None:
    """Save selected topics to cache.

    Args:
        cache_path: Path to cache file
        topics: Selected topics to save
    """
    with open(cache_path, "w") as f:
        f.write("\n".join(topics))
