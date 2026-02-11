"""ROS-related functionality for bag recorder."""

import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

# Constants
EXCLUDED_TOPICS = [
    "/rosout",
    "/rosout_agg",
    "/parameter_events",
]
ROS_VERSION_ENV = "ROS_VERSION"
ROS2_VERSION_VALUE = "2"
SHUTDOWN_TIMEOUT_SECONDS = 5


@dataclass(frozen=True)
class RosConfig:
    """ROS command and naming configuration."""

    topic_list_cmd: List[str]
    bag_record_cmd: List[str]
    output_flag: str
    timestamp_format: str
    default_name_template: str


ROS1_CONFIG = RosConfig(
    topic_list_cmd=["rostopic", "list"],
    bag_record_cmd=["rosbag", "record"],
    output_flag="-O",
    timestamp_format="%Y-%m-%d-%H-%M-%S",
    default_name_template="{timestamp}-{index}.bag",
)

ROS2_CONFIG = RosConfig(
    topic_list_cmd=["ros2", "topic", "list"],
    bag_record_cmd=["ros2", "bag", "record"],
    output_flag="-o",
    timestamp_format="%Y_%m_%d-%H_%M_%S",
    default_name_template="rosbag2_{timestamp}-{index}",
)


def get_ros_config() -> RosConfig:
    """Get ROS configuration based on ROS version."""
    if os.getenv(ROS_VERSION_ENV) == ROS2_VERSION_VALUE:
        return ROS2_CONFIG
    return ROS1_CONFIG


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
    config: RosConfig,
    selections: List[Tuple[str, int]],
    additional_args: List[str],
) -> None:
    """Start ROS bag recording.

    Args:
        config: ROS command and naming configuration
        selections: Topics with their assigned process index
        additional_args: Additional command line arguments
    """
    if not selections:
        return

    grouped_topics: Dict[int, List[str]] = {}
    for topic, process_index in selections:
        grouped_topics.setdefault(process_index, []).append(topic)

    output_name_arg = _extract_output_name(additional_args, config.output_flag)
    timestamp = time.strftime(config.timestamp_format)

    processes = []
    for process_index in sorted(grouped_topics):
        topics = grouped_topics[process_index]
        output_args = _build_output_args(
            config, output_name_arg, process_index, timestamp
        )
        processes.append(
            subprocess.Popen(
                config.bag_record_cmd + output_args + topics + additional_args,
                start_new_session=True,
            )
        )

    try:
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        _shutdown_processes(processes)


def _extract_output_name(args: List[str], output_flag: str) -> str | None:
    """Return the output name passed by the user, if any."""
    if output_flag not in args:
        return None
    try:
        idx = args.index(output_flag)
        return args[idx + 1]
    except (ValueError, IndexError):
        return None


def _build_output_args(
    config: RosConfig,
    output_name: str | None,
    process_index: int,
    timestamp: str,
) -> List[str]:
    """Build output args that guarantee unique bag names."""
    if output_name:
        name = f"{output_name}-{process_index}"
    else:
        name = config.default_name_template.format(
            timestamp=timestamp, index=process_index
        )
    return [config.output_flag, name]


def _shutdown_processes(processes: List[subprocess.Popen]) -> None:
    """Gracefully stop bag processes after Ctrl+C."""
    for process in processes:
        _send_sigint(process)

    for process in processes:
        try:
            process.wait(timeout=SHUTDOWN_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=SHUTDOWN_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                process.kill()


def _send_sigint(process: subprocess.Popen) -> None:
    """Send SIGINT to the process group if available."""
    try:
        os.killpg(process.pid, signal.SIGINT)
    except ProcessLookupError:
        return
    except OSError:
        process.send_signal(signal.SIGINT)
