# bag_recorder

Interactive ROS bag recorder with topic selection for ROS 1 and ROS 2.

> Streamline your ROS bag recording workflow with an intuitive terminal UI designed to make topic selection quick and effortless.

## ✨ Features

- **Interactive Topic Selection**: Choose topics to record with a scrollable checklist interface
- **ROS 1 & ROS 2 Support**: Automatically detects your ROS version and uses the appropriate commands
- **Topic Filtering**: Excludes common system topics (`/rosout`, `/rosout_agg`, `/parameter_events`) by default
- **Selection Memory**: Remembers your last selection for faster setup on subsequent runs
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
- **Enter**: Start recording selected topics
- **Ctrl+C**: Cancel and exit
