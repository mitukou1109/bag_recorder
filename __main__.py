#!/usr/bin/python3

from .check_scroll import CheckScroll
import subprocess
import sys
import os

excluded_topics = [
    "/rosout",
    "/rosout_agg",
    "/parameter_events",
]

if os.getenv("ROS_VERSION") == "2":
    topic_list_command = ["ros2", "topic", "list"]
    bag_record_command = ["ros2", "bag", "record"]
else:
    topic_list_command = ["rostopic", "list"]
    bag_record_command = ["rosbag", "record"]

topic_list_result = subprocess.run(topic_list_command, capture_output=True, text=True)

if topic_list_result.stderr:
    print(topic_list_result.stderr)
    exit(1)

topic_list = [
    topic
    for topic in topic_list_result.stdout.rstrip("\r\n").split("\n")
    if topic not in excluded_topics
]

if not topic_list:
    print("No topics available to record\n")
    exit(1)

topics_check = CheckScroll(
    prompt="Choose topics to record:",
    choices=topic_list,
    check="*",
    align=4,
    margin=2,
    height=10,
)

try:
    topics_to_record = topics_check.launch()
    if not topics_to_record:
        exit()
    options = sys.argv[1:] if len(sys.argv) > 1 else []
    subprocess.run(bag_record_command + topics_to_record + options)
except KeyboardInterrupt:
    exit()
