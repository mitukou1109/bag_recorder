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

        self.align = align
        self.margin = margin
        self.check = check

        self.max_width = len(max(self.choices, key=len))
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
        bullet.utils.cprint(self.choices[idx], fg_color, bg_color, end="")
        padding = " " * (self.max_width - len(self.choices[idx]))
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
        self._print_row(self.pos)

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
    def accept(self) -> List[str]:
        """Accept selection and return checked choices.

        Returns:
            List of selected choice strings
        """
        bullet.utils.moveCursorDown(self.top + self.height - self.pos + 1)
        bullet.utils.forceWrite("\n")
        return [
            choice
            for choice, is_checked in zip(self.choices, self.checked)
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
        # Clear current display
        bullet.utils.moveCursorDown(self.top + self.height - self.pos + 1)
        bullet.utils.clearConsoleUp(self.height + 2)
        bullet.utils.moveCursorDown(1)

        # Update height and adjust position if needed
        self._update_height()
        if self.pos >= self.top + self.height:
            self.pos = self.top + self.height - 1

        # Redraw
        if self.prompt:
            bullet.utils.forceWrite(self.prompt + "\n")
        self.render_rows()
        bullet.utils.moveCursorUp(self.top + self.height - self.pos)
