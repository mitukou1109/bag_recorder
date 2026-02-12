"""Merge multiple ROS 2 bag recordings into one."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Iterable, List

DEFAULT_OPTIONS_DIR = Path("/tmp") / "bag_recorder"
OPTIONS_FILE_PREFIX = "merge_options_"
OPTIONS_FILE_SUFFIX = ".yaml"
BAG_INDEX_PATTERN = re.compile(r"^(?P<base>.+)-(?P<index>\d+)$")


def main() -> None:
    """CLI entry point for merging ROS 2 bag recordings."""
    parser = argparse.ArgumentParser(
        description="Merge multiple ROS 2 bag recordings created by record-bag.",
    )
    parser.add_argument(
        "bag_path",
        help="Base bag path (absolute or relative) without the -{index} suffix.",
    )
    parser.add_argument(
        "--options",
        help="Path to ros2 bag convert output options YAML.",
    )
    args = parser.parse_args()

    base_path = Path(args.bag_path)
    base_name = base_path.name
    options_path = _resolve_options_path(args.options)
    if args.options is None:
        _write_options_file(options_path, str(base_path))

    bag_paths = _find_bag_paths(base_path.parent, base_name)
    if not bag_paths:
        print(
            f"No bag directories found for base name: {base_name}",
            file=sys.stderr,
        )
        sys.exit(1)

    command = _build_merge_command(bag_paths, options_path)
    subprocess.run(command, check=False)


def _find_bag_paths(root: Path, base_name: str) -> List[Path]:
    """Find bag directories matching the base name and numeric suffix."""
    candidates = []
    for path in root.iterdir():
        if not path.is_dir():
            continue
        match = BAG_INDEX_PATTERN.match(path.name)
        if not match or match.group("base") != base_name:
            continue
        candidates.append((int(match.group("index")), path))

    return [path for _, path in sorted(candidates, key=lambda item: item[0])]


def _build_merge_command(bag_paths: Iterable[Path], options_path: Path) -> List[str]:
    """Build the ros2 bag convert command."""
    command = ["ros2", "bag", "convert"]
    for bag_path in bag_paths:
        command.extend(["-i", str(bag_path)])
    command.extend(["-o", str(options_path)])
    return command


def _resolve_options_path(options_arg: str | None) -> Path:
    """Return the options file path, creating a temp path if needed."""
    if options_arg:
        return Path(options_arg)

    DEFAULT_OPTIONS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{OPTIONS_FILE_PREFIX}{uuid.uuid4().hex}{OPTIONS_FILE_SUFFIX}"
    return DEFAULT_OPTIONS_DIR / filename


def _write_options_file(options_path: Path, bag_name: str) -> None:
    """Create merge options YAML for the output bag."""
    options_path.write_text(
        f"output_bags:\n  - uri: {bag_name}\n",
        encoding="utf-8",
    )
