# bag_recorder

Interactive ROS bag recorder with topic selection for ROS 1 and ROS 2

## Features

- **Interactive Topic Selection**: Choose topics to record with a scrollable checklist
- **ROS 1 & ROS 2 Support**: Automatically detects your ROS version
- **Topic Filtering**: Excludes common system topics (`/rosout`, `/rosout_agg`, `/parameter_events`)
- **Selection Memory**: Remembers your last selection for the next run
- **Scrollable Interface**: Handles large topic lists with scroll indicators

## Requirements

- ROS 1 or ROS 2

## Installation

```bash
git clone https://github.com/mitukou1109/bag_recorder.git
cd bag_recorder
```

Install dependencies with [uv](https://docs.astral.sh/uv/getting-started/installation/):

```bash
uv sync
```

Or with pip:

```bash
pip install .
```

## Usage

```bash
uv run main.py
```

Pass additional options to the bag record command:

```bash
# Specify output directory
uv run main.py -o /path/to/output
```

### Interactive Controls

- **↑/↓**: Navigate through topics
- **Space**: Toggle topic selection
- **Enter**: Start recording selected topics
- **Ctrl+C**: Cancel
