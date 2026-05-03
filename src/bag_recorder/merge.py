"""Merge multiple ROS 2 bag recordings into one."""

import argparse
import re
import subprocess
import uuid
from pathlib import Path

DEFAULT_OPTIONS_DIR = Path("/tmp") / "bag_recorder"


def main() -> None:
    """CLI entry point for merging ROS 2 bag recordings."""
    parser = _create_parser()
    args, output_option_args = parser.parse_known_args()

    base_path = Path(args.bag_path)
    bag_paths = _find_bag_paths(base_path.parent, base_path.name)
    if not bag_paths:
        raise FileNotFoundError(
            f"No bag directories found for base name: {base_path.name}"
        )

    if args.options_file:
        if output_option_args:
            print(
                "Warning: Ignoring output options specified as arguments since --options-file is provided."
            )
        options_path = Path(args.options_file)
    else:
        try:
            options_path = _create_options_file(
                output_option_args, default_uri=str(base_path)
            )
        except ValueError as error:
            parser.error(str(error))

    command = _build_merge_command(bag_paths, options_path)
    subprocess.run(command, check=False)


def _create_parser() -> argparse.ArgumentParser:
    """Create the merge-bag argument parser."""
    parser = argparse.ArgumentParser(
        description="Merge multiple ROS 2 bag recordings created by record-bag.",
    )
    parser.add_argument(
        "bag_path",
        help="Base bag path (absolute or relative) without the -{index} suffix.",
    )
    parser.add_argument(
        "--options-file",
        help="Path to output options file.",
    )
    return parser


def _create_options_file(output_option_args: list[str], default_uri: str) -> Path:
    """Create a temporary output options file from command line arguments."""
    output_options = _parse_output_options(output_option_args)
    output_options.setdefault("uri", default_uri)

    options_path = DEFAULT_OPTIONS_DIR / f"merge_options_{uuid.uuid4().hex}.yaml"
    _write_options_file(options_path, output_options)
    return options_path


def _find_bag_paths(root: Path, base_name: str) -> list[Path]:
    """Find bag directories matching the base name and numeric suffix."""
    candidates = []
    for path in root.iterdir():
        if not path.is_dir():
            continue
        match = re.compile(r"^(?P<base>.+)-(?P<index>\d+)$").match(path.name)
        if not match or match.group("base") != base_name:
            continue
        candidates.append((int(match.group("index")), path))

    return [path for _, path in sorted(candidates, key=lambda item: item[0])]


def _build_merge_command(bag_paths: list[Path], options_path: Path) -> list[str]:
    """Build the ros2 bag convert command."""
    command = ["ros2", "bag", "convert"]
    for bag_path in bag_paths:
        command.extend(["-i", str(bag_path)])
    command.extend(["-o", str(options_path)])
    return command


def _parse_output_options(option_args: list[str]) -> dict[str, str]:
    """Parse key:=value arguments into an output bag options dict."""
    options: dict[str, str] = {}
    for arg in option_args:
        key, separator, value = arg.partition(":=")
        if not separator:
            raise ValueError(f"Expected output option in key:=value format, got: {arg}")
        if not key:
            raise ValueError(f"Expected output option name, got: {arg}")
        options[key] = value

    return options


def _write_options_file(options_path: Path, options: dict[str, str]) -> None:
    """Create merge options YAML for the output bag."""
    options_path.parent.mkdir(parents=True, exist_ok=True)
    content = _format_output_options(options)
    options_path.write_text(content, encoding="utf-8")


def _format_output_options(output_options: dict[str, str]) -> str:
    """Format one output bag options mapping as YAML."""
    lines = ["output_bags:"]
    for index, (key, value) in enumerate(output_options.items()):
        prefix = "  -" if index == 0 else "   "
        lines.append(f"{prefix} {key}: {value}")
    return "\n".join(lines) + "\n"
