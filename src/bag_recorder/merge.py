"""Merge multiple ROS 2 bag recordings into one."""

import argparse
import subprocess
import uuid
from pathlib import Path

DEFAULT_OPTIONS_DIR = Path("/tmp") / "bag_recorder"


def main() -> None:
    """CLI entry point for merging ROS 2 bag recordings."""
    parser = _create_parser()
    args, output_option_args = parser.parse_known_args()

    try:
        bag_arguments, positional_option_args = _split_bag_paths_and_options(
            args.bag_paths
        )
    except ValueError as error:
        parser.error(str(error))
    output_option_args = positional_option_args + output_option_args

    if len(bag_arguments) == 1:
        prefix_path = Path(bag_arguments[0])
        bag_paths = _find_bag_paths(prefix_path.parent, prefix_path.name)
        if not bag_paths:
            raise FileNotFoundError(
                f"No bag directories found for prefix: {prefix_path}"
            )
        default_uri = str(prefix_path)
    else:
        bag_paths = [Path(bag_path) for bag_path in bag_arguments]
        default_uri = str(bag_paths[0].parent / "merged_bag")

    print("Bags to merge:")
    for bag_path in bag_paths:
        print(f"  {bag_path}")

    try:
        confirmed = input("Merge these bags? [y/N]: ").strip().lower() in {"y", "yes"}
    except (EOFError, KeyboardInterrupt):
        confirmed = False

    if not confirmed:
        print("Merge cancelled.")
        return

    if args.options_file:
        if output_option_args:
            print(
                "Warning: Ignoring output options specified as arguments since --options-file is provided."
            )
        options_path = Path(args.options_file)
    else:
        try:
            options_path = _create_options_file(
                output_option_args, default_uri=default_uri
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
        "bag_paths",
        nargs="+",
        help=(
            "One bag path prefix, or multiple bag paths "
            "to merge directly."
        ),
    )
    parser.add_argument(
        "--options-file",
        help="Path to output options file.",
    )
    return parser


def _split_bag_paths_and_options(arguments: list[str]) -> tuple[list[str], list[str]]:
    """Separate positional bag paths from key:=value output options."""
    bag_paths = []
    output_options = []
    for argument in arguments:
        if ":=" in argument:
            output_options.append(argument)
        else:
            bag_paths.append(argument)

    if not bag_paths:
        raise ValueError("Specify at least one bag path")
    return bag_paths, output_options


def _create_options_file(output_option_args: list[str], default_uri: str) -> Path:
    """Create a temporary output options file from command line arguments."""
    output_options = _parse_output_options(output_option_args)
    output_options.setdefault("uri", default_uri)
    output_options.setdefault("storage_id", "mcap")

    options_path = DEFAULT_OPTIONS_DIR / f"merge_options_{uuid.uuid4().hex}.yaml"
    _write_options_file(options_path, output_options)
    return options_path


def _find_bag_paths(root: Path, prefix: str) -> list[Path]:
    """Find ROS 2 bag directories whose names start with the prefix."""
    return sorted(
        path
        for path in root.iterdir()
        if path.name.startswith(prefix)
        and path.is_dir()
        and (path / "metadata.yaml").is_file()
    )


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
