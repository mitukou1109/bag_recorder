import shutil
import signal
from typing import List

import bullet
import bullet.charDef


@bullet.keyhandler.init
class CheckScroll:
    def __init__(
        self,
        *,
        prompt: str,
        choices: List[str],
        checked: List[bool],
        check: str,
        align: int,
        margin: int,
    ):
        if not choices:
            raise ValueError("Choices cannot be empty!")
        if margin < 0:
            raise ValueError("Margin must be >= 0!")

        self.prompt = prompt
        self.choices = choices
        self.checked = checked if checked is not None else [False] * len(self.choices)
        self.pos = 0

        self.align = align
        self.margin = margin
        self.up_indicator = "↑ ↑ ↑"
        self.down_indicator = "↓ ↓ ↓"

        self.check = check

        self.max_width = len(max(self.choices, key=len))

        self.top = 0
        self._update_height()

        signal.signal(signal.SIGWINCH, self._handle_window_change)

    def renderRows(self):
        self.printBorder(indicator=self.up_indicator if self.top != 0 else "")
        bullet.utils.forceWrite("\n")
        bottom = self.top + self.height
        for i in range(self.top, bottom):
            self.printRow(i)
            bullet.utils.forceWrite("\n")
        self.printBorder(
            indicator=self.down_indicator if bottom < len(self.choices) else ""
        )

    def printRow(self, idx):
        bullet.utils.forceWrite(" " * self.align)
        bg_color = (
            bullet.colors.REVERSE
            if idx == self.pos
            else bullet.colors.background["default"]
        )
        fg_color = (
            bullet.colors.REVERSE
            if idx == self.pos
            else bullet.colors.foreground["default"]
        )

        if self.checked[idx]:
            bullet.utils.cprint(
                self.check + " " * self.margin, fg_color, bg_color, end=""
            )
        else:
            bullet.utils.cprint(
                " " * (len(self.check) + self.margin), fg_color, bg_color, end=""
            )
        bullet.utils.cprint(self.choices[idx], fg_color, bg_color, end="")
        bullet.utils.cprint(
            " " * (self.max_width - len(self.choices[idx])), on=bg_color, end=""
        )
        bullet.utils.moveCursorHead()

    def printBorder(self, indicator=""):
        bullet.utils.forceWrite(" " * (self.align + len(self.check) + self.margin))
        bullet.utils.cprint(indicator, end="")
        bullet.utils.moveCursorHead()

    @bullet.keyhandler.register(bullet.charDef.SPACE_CHAR)
    def toggleRow(self):
        self.checked[self.pos] = not self.checked[self.pos]
        self.printRow(self.pos)

    @bullet.keyhandler.register(bullet.charDef.ARROW_UP_KEY)
    def moveUp(self):
        if self.pos == self.top:
            if self.top == 0:
                return
            else:
                bullet.utils.moveCursorUp(1)
                bullet.utils.clearConsoleDown(self.height + 1)
                self.pos, self.top = self.pos - 1, self.top - 1
                self.renderRows()
                bullet.utils.moveCursorUp(self.height)
        else:
            bullet.utils.clearLine()
            self.pos -= 1
            self.printRow(self.pos + 1)
            bullet.utils.moveCursorUp(1)
            self.printRow(self.pos)

    @bullet.keyhandler.register(bullet.charDef.ARROW_DOWN_KEY)
    def moveDown(self):
        if self.pos == self.top + self.height - 1:
            if self.top + self.height == len(self.choices):
                return
            else:
                bullet.utils.moveCursorDown(1)
                bullet.utils.clearConsoleUp(self.height + 2)
                bullet.utils.moveCursorDown(1)
                self.pos, self.top = self.pos + 1, self.top + 1
                self.renderRows()
                bullet.utils.moveCursorUp(1)
        else:
            bullet.utils.clearLine()
            self.pos += 1
            self.printRow(self.pos - 1)
            bullet.utils.moveCursorDown(1)
            self.printRow(self.pos)

    @bullet.keyhandler.register(bullet.charDef.NEWLINE_KEY)
    def accept(self):
        bullet.utils.moveCursorDown(self.top + self.height - self.pos + 1)
        bullet.utils.forceWrite("\n")
        ret = [self.choices[i] for i in range(len(self.choices)) if self.checked[i]]
        self.pos = 0
        self.checked = [False] * len(self.choices)
        return ret

    @bullet.keyhandler.register(bullet.charDef.INTERRUPT_KEY)
    def interrupt(self):
        bullet.utils.moveCursorDown(self.top + self.height - self.pos)
        raise KeyboardInterrupt

    def launch(self):
        if self.prompt:
            bullet.utils.forceWrite(self.prompt + "\n")
        self.renderRows()
        bullet.utils.moveCursorUp(self.height)
        with bullet.cursor.hide():
            while True:
                ret = self.handle_input()
                if ret is not None:
                    return ret

    def _update_height(self):
        self.height = min(len(self.choices), shutil.get_terminal_size().lines - 3)

    def _handle_window_change(self, *_):
        bullet.utils.moveCursorDown(self.top + self.height - self.pos + 1)
        bullet.utils.clearConsoleUp(self.height + 2)
        bullet.utils.moveCursorDown(1)

        self._update_height()
        if self.pos >= self.top + self.height:
            self.pos = self.top + self.height - 1

        if self.prompt:
            bullet.utils.forceWrite(self.prompt + "\n")
        self.renderRows()
        bullet.utils.moveCursorUp(self.top + self.height - self.pos)
