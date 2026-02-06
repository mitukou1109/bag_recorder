"""ROS-related functionality for bag recorder."""

import os
import subprocess
import sys
from typing import List

# Constants
EXCLUDED_TOPICS = [
    "/rosout",
    "/rosout_agg",
    "/parameter_events",
]


def get_ros_commands() -> tuple[List[str], List[str]]:
    """Get ROS commands based on ROS version.

    Returns:
        tuple: (topic_list_command, bag_record_command)
    """
    if os.getenv("ROS_VERSION") == "2":
        return ["ros2", "topic", "list"], ["ros2", "bag", "record"]
    return ["rostopic", "list"], ["rosbag", "record"]


def fetch_topic_list(command: List[str]) -> List[str]:
    """Fetch available ROS topics.

    Args:
        command: Command to list topics

    Returns:
        List of topic names excluding predefined topics

    Raises:
        SystemExit: If command fails or no topics available
    """
    result = subprocess.run(command, capture_output=True, text=True)

    if result.stderr:
        print(f"Error fetching topics: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    topics = [
        topic
        for topic in result.stdout.rstrip("\r\n").split("\n")
        if topic and topic not in EXCLUDED_TOPICS
    ]

    if not topics:
        print("No topics available to record")
        sys.exit(1)

    return topics


def record_bag(
    command: List[str], topics: List[str], additional_args: List[str]
) -> None:
    """Start ROS bag recording.

    Args:
        command: Base bag record command
        topics: Topics to record
        additional_args: Additional command line arguments
    """
    subprocess.run(command + topics + additional_args)
