"""User interface management for bag recorder."""

from typing import List, Optional, Tuple

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
    selector = CheckScroll(
        prompt=UI_PROMPT,
        choices=topics,
        check=UI_CHECK_CHAR,
        checked=cached_selection,
        process_indices=cached_process_indices,
        align=UI_ALIGN,
        margin=UI_MARGIN,
    )
    return selector.launch()
