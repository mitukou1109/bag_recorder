"""Scrollable checkbox selection interface using bullet library."""

import shutil
import signal
from typing import List, Optional

import bullet
import bullet.charDef

# Constants
MIN_TERMINAL_LINES = 3
UP_INDICATOR = "↑ ↑ ↑"
DOWN_INDICATOR = "↓ ↓ ↓"
DEFAULT_PROCESS_INDEX = 1
UNASSIGNED_INDEX_LABEL = "-"


@bullet.keyhandler.init
class CheckScroll:
    """Interactive scrollable checkbox list for terminal.

    Attributes:
        prompt: Prompt text to display
        choices: List of options
        checked: Boolean list of checked states
        check: Character to display for checked items
        align: Left padding
        margin: Space between checkbox and text
    """

    def __init__(
        self,
        *,
        prompt: str,
        choices: List[str],
        checked: Optional[List[bool]] = None,
        process_indices: Optional[List[Optional[int]]] = None,
        check: str = "*",
        align: int = 4,
        margin: int = 2,
    ):
        """Initialize CheckScroll.

        Args:
            prompt: Prompt text to display
            choices: List of options
            checked: Initial checked states (defaults to all False)
            check: Character for checked items
            align: Left padding
            margin: Space between checkbox and text

        Raises:
            ValueError: If choices is empty or margin is negative
        """
        if not choices:
            raise ValueError("Choices cannot be empty!")
        if margin < 0:
            raise ValueError("Margin must be >= 0!")

        self.prompt = prompt
        self.choices = choices
        self.checked = checked if checked is not None else [False] * len(self.choices)
        self.pos = 0
        self.top = 0

        if process_indices is None:
            self.process_indices = [DEFAULT_PROCESS_INDEX] * len(self.choices)
        else:
            sanitized = []
            for value in process_indices:
                if value is None:
                    sanitized.append(None)
                else:
                    sanitized.append(max(DEFAULT_PROCESS_INDEX, int(value)))
            self.process_indices = sanitized + [DEFAULT_PROCESS_INDEX] * (
                len(self.choices) - len(sanitized)
            )
            self.process_indices = self.process_indices[: len(self.choices)]
        self._normalize_indices_inplace()

        self.align = align
        self.margin = margin
        self.check = check

        self.max_width = len(max(self._choice_label(i) for i in range(len(choices))))
        self._update_height()

        signal.signal(signal.SIGWINCH, self._handle_window_change)

    def render_rows(self) -> None:
        """Render visible rows with scroll indicators."""
        self._print_border(indicator=UP_INDICATOR if self.top != 0 else "")
        bullet.utils.forceWrite("\n")

        bottom = self.top + self.height
        for i in range(self.top, bottom):
            self._print_row(i)
            bullet.utils.forceWrite("\n")

        self._print_border(
            indicator=DOWN_INDICATOR if bottom < len(self.choices) else ""
        )

    def _choice_label(self, idx: int) -> str:
        """Build the display label for a choice.

        Args:
            idx: Index of the choice

        Returns:
            Formatted label string
        """
        if not self.checked[idx]:
            return f"[{UNASSIGNED_INDEX_LABEL}] {self.choices[idx]}"
        return f"[{self.process_indices[idx]}] {self.choices[idx]}"

    def _print_row(self, idx: int) -> None:
        """Print a single row with proper formatting.

        Args:
            idx: Index of the row to print
        """
        bullet.utils.forceWrite(" " * self.align)

        is_selected = idx == self.pos
        bg_color = (
            bullet.colors.REVERSE
            if is_selected
            else bullet.colors.background["default"]
        )
        fg_color = (
            bullet.colors.REVERSE
            if is_selected
            else bullet.colors.foreground["default"]
        )

        # Print checkbox
        checkbox = self.check if self.checked[idx] else " " * len(self.check)
        bullet.utils.cprint(checkbox + " " * self.margin, fg_color, bg_color, end="")

        # Print choice text with padding
        label = self._choice_label(idx)
        bullet.utils.cprint(label, fg_color, bg_color, end="")
        padding = " " * (self.max_width - len(label))
        bullet.utils.cprint(padding, on=bg_color, end="")

        bullet.utils.moveCursorHead()

    def _print_border(self, indicator: str = "") -> None:
        """Print border with optional scroll indicator.

        Args:
            indicator: Text to show in the border (e.g., scroll arrows)
        """
        bullet.utils.forceWrite(" " * (self.align + len(self.check) + self.margin))
        bullet.utils.cprint(indicator, end="")
        bullet.utils.moveCursorHead()

    @bullet.keyhandler.register(bullet.charDef.SPACE_CHAR)
    def toggle_row(self) -> None:
        """Toggle the checkbox state of the current row."""
        self.checked[self.pos] = not self.checked[self.pos]
        if self.checked[self.pos]:
            if self.process_indices[self.pos] is None:
                self.process_indices[self.pos] = DEFAULT_PROCESS_INDEX
        else:
            self.process_indices[self.pos] = None
        self._normalize_process_indices()
        self._print_row(self.pos)

    @bullet.keyhandler.register(bullet.charDef.ARROW_LEFT_KEY)
    def decrease_process_index(self) -> None:
        """Decrease process index for the current checked row."""
        if not self.checked[self.pos]:
            return
        current_value = self.process_indices[self.pos]
        if current_value is None:
            return
        if current_value == DEFAULT_PROCESS_INDEX:
            return
        self.process_indices[self.pos] = current_value - 1
        self._normalize_process_indices()

    @bullet.keyhandler.register(bullet.charDef.ARROW_RIGHT_KEY)
    def increase_process_index(self) -> None:
        """Increase process index for the current checked row."""
        if not self.checked[self.pos]:
            return
        if self.process_indices[self.pos] is None:
            self.process_indices[self.pos] = DEFAULT_PROCESS_INDEX
        max_index = self._max_index()
        if self.process_indices[self.pos] >= max_index:
            return
        self.process_indices[self.pos] += 1
        self._normalize_process_indices()

    @bullet.keyhandler.register(bullet.charDef.ARROW_UP_KEY)
    def move_up(self) -> None:
        """Move selection up, scrolling if necessary."""
        if self.pos == self.top:
            if self.top == 0:
                return
            # Scroll up
            bullet.utils.moveCursorUp(1)
            bullet.utils.clearConsoleDown(self.height + 1)
            self.pos -= 1
            self.top -= 1
            self.render_rows()
            bullet.utils.moveCursorUp(self.height)
        else:
            # Move within visible area
            bullet.utils.clearLine()
            self.pos -= 1
            self._print_row(self.pos + 1)
            bullet.utils.moveCursorUp(1)
            self._print_row(self.pos)

    @bullet.keyhandler.register(bullet.charDef.ARROW_DOWN_KEY)
    def move_down(self) -> None:
        """Move selection down, scrolling if necessary."""
        bottom = self.top + self.height
        if self.pos == bottom - 1:
            if bottom == len(self.choices):
                return
            # Scroll down
            bullet.utils.moveCursorDown(1)
            bullet.utils.clearConsoleUp(self.height + 2)
            bullet.utils.moveCursorDown(1)
            self.pos += 1
            self.top += 1
            self.render_rows()
            bullet.utils.moveCursorUp(1)
        else:
            # Move within visible area
            bullet.utils.clearLine()
            self.pos += 1
            self._print_row(self.pos - 1)
            bullet.utils.moveCursorDown(1)
            self._print_row(self.pos)

    @bullet.keyhandler.register(bullet.charDef.NEWLINE_KEY)
    def accept(self) -> List[tuple[str, int]]:
        """Accept selection and return checked choices.

        Returns:
            List of selected choice strings
        """
        bullet.utils.moveCursorDown(self.top + self.height - self.pos + 1)
        bullet.utils.forceWrite("\n")
        return [
            (choice, process_index)
            for choice, process_index, is_checked in zip(
                self.choices, self.process_indices, self.checked
            )
            if is_checked
        ]

    @bullet.keyhandler.register(bullet.charDef.INTERRUPT_KEY)
    def interrupt(self) -> None:
        """Handle keyboard interrupt (Ctrl+C)."""
        bullet.utils.moveCursorDown(self.top + self.height - self.pos)
        raise KeyboardInterrupt

    def launch(self) -> List[str]:
        """Launch the interactive selection UI.

        Returns:
            List of selected choices
        """
        if self.prompt:
            bullet.utils.forceWrite(self.prompt + "\n")

        self.render_rows()
        bullet.utils.moveCursorUp(self.height)

        with bullet.cursor.hide():
            while True:
                result = self.handle_input()
                if result is not None:
                    return result

    def _update_height(self) -> None:
        """Update the visible height based on terminal size."""
        terminal_lines = shutil.get_terminal_size().lines
        self.height = min(len(self.choices), terminal_lines - MIN_TERMINAL_LINES)

    def _handle_window_change(self, *_) -> None:
        """Handle terminal window resize events.

        Args:
            *_: Signal handler arguments (unused)
        """
        # Update height and adjust position if needed
        self._update_height()
        if self.pos >= self.top + self.height:
            self.pos = self.top + self.height - 1

        self._redraw()

    def _refresh_after_index_change(self) -> None:
        """Refresh UI after a process index update."""
        new_width = max(self.max_width, len(self._choice_label(self.pos)))
        if new_width != self.max_width:
            self.max_width = new_width
            self._redraw()
            return
        self._print_row(self.pos)

    def _max_index(self) -> int:
        """Return the maximum allowed process index."""
        return sum(1 for checked in self.checked if checked)

    def _normalize_process_indices(self) -> None:
        """Ensure indices are contiguous and within topic count."""
        before = list(self.process_indices)
        self._normalize_indices_inplace()

        max_width = max(
            self.max_width,
            max(len(self._choice_label(i)) for i in range(len(self.choices))),
        )
        if max_width != self.max_width:
            self.max_width = max_width
            self._redraw()
            return

        if any(
            old != new
            for i, (old, new) in enumerate(zip(before, self.process_indices))
            if i != self.pos
        ):
            self._redraw()
            return

        self._refresh_after_index_change()

    def _normalize_indices_inplace(self) -> None:
        """Normalize indices to be contiguous without touching the UI."""
        for i, checked in enumerate(self.checked):
            if not checked:
                self.process_indices[i] = None
            elif self.process_indices[i] is None:
                self.process_indices[i] = DEFAULT_PROCESS_INDEX

        checked_indices = sorted(
            {
                self.process_indices[i]
                for i, checked in enumerate(self.checked)
                if checked and self.process_indices[i] is not None
            }
        )
        if not checked_indices:
            return

        mapping = {old: new for new, old in enumerate(checked_indices, start=1)}
        for i, checked in enumerate(self.checked):
            if checked:
                self.process_indices[i] = mapping[self.process_indices[i]]

    def _redraw(self) -> None:
        """Redraw the UI while keeping the cursor position."""
        bullet.utils.moveCursorDown(self.top + self.height - self.pos + 1)
        bullet.utils.clearConsoleUp(self.height + 3)
        bullet.utils.moveCursorDown(1)

        if self.prompt:
            bullet.utils.forceWrite(self.prompt + "\n")
        self.render_rows()
        bullet.utils.moveCursorUp(self.top + self.height - self.pos)
