"""User interface management for bag recorder."""

from typing import List, Optional

from bag_recorder.check_scroll import CheckScroll

# UI Constants
UI_ALIGN = 4
UI_MARGIN = 2
UI_CHECK_CHAR = "*"


def select_topics(
    topics: List[str], cached_selection: Optional[List[bool]]
) -> List[str]:
    """Display UI for topic selection.

    Args:
        topics: Available topics
        cached_selection: Previously selected topics

    Returns:
        List of selected topics
    """
    selector = CheckScroll(
        prompt="Choose topics to record:",
        choices=topics,
        check=UI_CHECK_CHAR,
        checked=cached_selection,
        align=UI_ALIGN,
        margin=UI_MARGIN,
    )
    return selector.launch()
