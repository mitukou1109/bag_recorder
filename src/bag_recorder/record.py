"""ROS bag recorder with interactive topic selection."""

import sys

from bag_recorder.cache import get_cache_path, load_cached_selection, save_selection
from bag_recorder.ros import fetch_topic_list, get_ros_config, record_bag
from bag_recorder.ui import select_topics


def main() -> None:
    """Main entry point."""
    try:
        cache_path = get_cache_path()
        ros_config = get_ros_config()

        # Fetch available topics
        topics = fetch_topic_list(ros_config.topic_list_cmd)

        # Load cached selection
        cached_selection, cached_process_indices = load_cached_selection(
            cache_path, topics
        )

        # Select topics interactively
        selected_topics = select_topics(
            topics, cached_selection, cached_process_indices
        )

        if not selected_topics:
            sys.exit(0)

        # Save selection
        save_selection(cache_path, selected_topics)

        # Record bag
        additional_args = sys.argv[1:]
        record_bag(ros_config, selected_topics, additional_args)

    except KeyboardInterrupt:
        sys.exit(0)
