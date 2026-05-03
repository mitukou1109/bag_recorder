"""User interface management for bag recorder."""

from typing import List, Optional, Tuple

import sys
import termios

from bag_recorder.check_scroll import CheckScroll

# UI Constants
UI_ALIGN = 4
UI_MARGIN = 2
UI_CHECK_CHAR = "*"
UI_PROMPT = "Choose topics to record:"


def select_topics(
    topics: List[str],
    cached_selection: Optional[List[bool]],
    cached_process_indices: Optional[List[int]],
) -> List[Tuple[str, int]]:
    """Display UI for topic selection.

    Args:
        topics: Available topics
        cached_selection: Previously selected topics

    Returns:
        List of selected topics
    """
    tty_state = None
    if sys.stdin.isatty():
        try:
            tty_state = termios.tcgetattr(sys.stdin.fileno())
        except termios.error:
            tty_state = None

    selector = CheckScroll(
        prompt=UI_PROMPT,
        choices=topics,
        check=UI_CHECK_CHAR,
        checked=cached_selection,
        process_indices=cached_process_indices,
        align=UI_ALIGN,
        margin=UI_MARGIN,
    )
    try:
        return selector.launch()
    finally:
        if tty_state is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, tty_state)
