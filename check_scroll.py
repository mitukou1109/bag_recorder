import bullet
from bullet.charDef import *

@bullet.keyhandler.init
class CheckScroll:
    def __init__(
        self,
        prompt: str = "",
        choices: list = [],
        check: str = "√",
        check_color: str = bullet.colors.foreground["default"],
        check_on_switch: str = bullet.colors.REVERSE,
        word_color: str = bullet.colors.foreground["default"],
        word_on_switch: str = bullet.colors.REVERSE,
        background_color: str = bullet.colors.background["default"],
        background_on_switch: str = bullet.colors.REVERSE,
        pad_right=0,
        indent: int = 0,
        align=0,
        margin: int = 0,
        shift: int = 0,
        height=None,
        return_index: bool = False,
    ):
        if not choices:
            raise ValueError("Choices cannot be empty!")
        if indent < 0:
            raise ValueError("Indent must be >= 0!")
        if margin < 0:
            raise ValueError("Margin must be >= 0!")

        self.prompt = prompt
        self.choices = choices
        self.checked = [False] * len(self.choices)
        self.pos = 0
        self.indent = indent
        self.align = align
        self.margin = margin
        self.shift = shift
        self.check = check
        self.check_color = check_color
        self.check_on_switch = check_on_switch
        self.word_color = word_color
        self.word_on_switch = word_on_switch
        self.background_color = background_color
        self.background_on_switch = background_on_switch
        self.pad_right = pad_right
        self.max_width = len(max(self.choices, key=len)) + self.pad_right
        self.height = min(len(self.choices), height if height else len(self.choices))
        self.top = 0
        self.return_index = return_index

    def renderRows(self):
        self.printRow(self.top, indicator="↑" if self.top != 0 else "")
        bullet.utils.forceWrite("\n")
        for i in range(self.top + 1, self.top + self.height - 1):
            self.printRow(i)
            bullet.utils.forceWrite("\n")
        if self.top + self.height - 1 < len(self.choices):
            self.printRow(self.top + self.height - 1, indicator="↓")

    def printRow(self, idx, indicator=""):
        bullet.utils.forceWrite(" " * (self.indent + self.align))
        back_color = (
            self.background_on_switch if idx == self.pos else self.background_color
        )
        word_color = self.word_on_switch if idx == self.pos else self.word_color
        check_color = self.check_on_switch if idx == self.pos else self.check_color
        if self.checked[idx]:
            bullet.utils.cprint(self.check, check_color, back_color, end="")
        else:
            bullet.utils.cprint(" ", check_color, back_color, end="")
        bullet.utils.cprint(
            " " * self.margin + self.choices[idx], word_color, back_color, end=""
        )
        bullet.utils.cprint(
            " " * (self.max_width - len(self.choices[idx])), on=back_color, end=""
        )
        bullet.utils.cprint(
            indicator, color=bullet.colors.foreground["default"], end=""
        )
        bullet.utils.moveCursorHead()

    @bullet.keyhandler.register(SPACE_CHAR)
    def toggleRow(self):
        self.checked[self.pos] = not self.checked[self.pos]
        self.renderRows()
        bullet.utils.moveCursorUp(self.height)

    @bullet.keyhandler.register(ARROW_UP_KEY)
    def moveUp(self):
        if self.pos > 0:
            self.pos -= 1
            if self.pos < self.top:
                self.top -= 1
            self.renderRows()
            bullet.utils.moveCursorUp(self.height)

    @bullet.keyhandler.register(ARROW_DOWN_KEY)
    def moveDown(self):
        if self.pos < len(self.choices) - 1:
            self.pos += 1
            if self.pos >= self.top + self.height:
                self.top += 1
            self.renderRows()
            bullet.utils.moveCursorUp(self.height)

    @bullet.keyhandler.register(NEWLINE_KEY)
    def accept(self):
        bullet.utils.moveCursorDown(self.height - (self.pos - self.top))
        ret = (
            [i for i, checked in enumerate(self.checked) if checked]
            if self.return_index
            else [
                choice for choice, checked in zip(self.choices, self.checked) if checked
            ]
        )
        self.pos = 0
        return ret

    @bullet.keyhandler.register(INTERRUPT_KEY)
    def interrupt(self):
        raise KeyboardInterrupt

    def launch(self):
        if self.prompt:
            bullet.utils.forceWrite(self.prompt + "\n")
        self.renderRows()
        bullet.utils.moveCursorUp(self.height)
        with bullet.cursor.hide():
            return self.accept()
