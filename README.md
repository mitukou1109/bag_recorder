# bag_recorder

Interactive ROS bag recorder with topic selection for ROS 1 and ROS 2.

> Streamline your ROS bag recording workflow with an intuitive terminal UI designed to make topic selection quick and effortless.

## ✨ Features

- **Interactive Topic Selection**: Choose topics to record with a scrollable checklist interface
- **ROS 1 & ROS 2 Support**: Automatically detects your ROS version and uses the appropriate commands
- **Topic Filtering**: Excludes common system topics (`/rosout`, `/rosout_agg`, `/parameter_events`) by default
- **Selection Memory**: Remembers your last selection (including process indices) for faster setup on subsequent runs
- **Per-Process Grouping**: Assign topics to different record processes with left/right keys
- **Scrollable Interface**: Handles large topic lists with visual scroll indicators

## 📋 Requirements

- ROS 1 or ROS 2
- [uv](https://docs.astral.sh/uv/getting-started/installation/) - Modern Python package and project manager

## ⚡ Quick Start

```bash
uv tool install git+https://github.com/mitukou1109/bag_recorder
record-bag
```

## 📖 Usage

### Basic Usage

```bash
record-bag
```

### With Options

Pass additional options to the bag record command:

```bash
record-bag -a -o /path/to/output
```

### Interactive Controls

- **↑/↓**: Navigate through topics
- **Space**: Toggle topic selection
- **←/→**: Change process index for the selected topic (checked only)
- **Enter**: Start recording selected topics
- **Ctrl+C**: Cancel and exit

### Process Index

Each checked topic has a process index (shown before the topic name) that determines which `rosbag`/`ros2 bag` process it belongs to.

- Topics with the same index are recorded by the same process.
- Indices are always contiguous among checked topics (1..N).
- Unchecked topics show `[-]` (no index assigned).

### Bag Naming

When multiple processes are used, the tool ensures unique bag names per process.

- ROS 1 default: `YYYY-MM-DD-HH-MM-SS-{index}.bag`
- ROS 2 default: `rosbag2_YYYY_MM_DD-HH_MM_SS-{index}`
- With `-o`/`-O`: the provided name gets `-{index}` appended
