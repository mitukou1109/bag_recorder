"""Cache management for bag recorder."""

import hashlib
from pathlib import Path
from typing import List, Optional, Tuple

# Constants
CACHE_DIR = Path.home() / ".cache" / "bag_recorder"
CACHE_SEPARATOR = "\t"
DEFAULT_PROCESS_INDEX = 1


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


def load_cached_selection(
    cache_path: Path, topics: List[str]
) -> Tuple[Optional[List[bool]], Optional[List[int]]]:
    """Load previously selected topics from cache.

    Args:
        cache_path: Path to cache file
        topics: Current available topics

    Returns:
        Tuple of checked states and process indices, or (None, None) if cache not found
    """
    try:
        with open(cache_path, "r") as f:
            cached_entries = [line.strip() for line in f if line.strip()]
        cached_indices = {}
        for entry in cached_entries:
            if CACHE_SEPARATOR in entry:
                topic, index_text = entry.split(CACHE_SEPARATOR, 1)
                try:
                    cached_indices[topic] = max(DEFAULT_PROCESS_INDEX, int(index_text))
                except ValueError:
                    cached_indices[topic] = DEFAULT_PROCESS_INDEX
            else:
                cached_indices[entry] = DEFAULT_PROCESS_INDEX
        checked = [topic in cached_indices for topic in topics]
        process_indices = [
            cached_indices.get(topic, DEFAULT_PROCESS_INDEX) for topic in topics
        ]
        return checked, process_indices
    except FileNotFoundError:
        return None, None


def save_selection(cache_path: Path, topics: List[Tuple[str, int]]) -> None:
    """Save selected topics to cache.

    Args:
        cache_path: Path to cache file
        topics: Selected topics and their process indices
    """
    with open(cache_path, "w") as f:
        f.write(
            "\n".join(f"{topic}{CACHE_SEPARATOR}{index}" for topic, index in topics)
        )
