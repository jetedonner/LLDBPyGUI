# """ Console
# Interactive console widget.  Use to add an interactive python interpreter
# in a GUI application.
#
# Original by deanhystad available here: https://python-forum.io/thread-25117.html
# changes: PySide2 -> pyqt5
#             + line 22: QtCore.Signal(str) -> QtCore.pyqtSignal(str)
# """

import sys
import code
import re
from typing import Callable
from PyQt6 import QtCore, QtGui, QtWidgets
from contextlib import redirect_stdout, redirect_stderr


class LineEdit(QtWidgets.QLineEdit):
    """QLIneEdit with a history buffer for recalling previous lines.
    I also accept tab as input (4 spaces).
    """
    newline = QtCore.pyqtSignal(str)  # Signal when return key pressed

    def __init__(self, history: int = 100) -> 'LineEdit':
        super().__init__()
        self.historymax = history
        self.clearhistory()
        self.promptpattern = re.compile('^[>\.]')

    def clearhistory(self) -> None:
        """Clear history buffer"""
        self.historyindex = 0
        self.historylist = []

    def event(self, ev) -> bool:
        """Intercept tab and arrow key presses.  Insert 4 spaces
        when tab pressed instead of moving to next contorl.  WHen
        arrow up or down are pressed select a line from the history
        buffer.  Emit newline signal when return key is pressed.
        """
        if ev.type() == QtCore.QEvent.Type.KeyPress:
            if ev.key() == int(QtCore.Qt.Key.Key_Tab):
                self.insert('    ')
                return True
            elif ev.key() == int(QtCore.Qt.Key.Key_Up):
                self.recall(self.historyindex - 1)
                return True
            elif ev.key() == int(QtCore.Qt.Key.Key_Down):
                self.recall(self.historyindex + 1)
                return True
            elif ev.key() == int(QtCore.Qt.Key.Key_Home):
                self.recall(0)
                return True
            elif ev.key() == int(QtCore.Qt.Key.Key_End):
                self.recall(len(self.historylist) - 1)
                return True
            elif ev.key() == int(QtCore.Qt.Key.Key_Return):
                self.returnkey()
                return True
        return super().event(ev)

    def returnkey(self) -> None:
        """Return key was pressed.  Add line to history and emit
        the newline signal.
        """
        text = self.text().rstrip()
        self.record(text)
        self.newline.emit(text)
        self.setText('')

    def recall(self, index: int) -> None:
        """Select a line from the history list"""
        length = len(self.historylist)
        if length > 0:
            index = max(0, min(index, length - 1))
            self.setText(self.historylist[index])
            self.historyindex = index

    def record(self, line: str) -> None:
        """Add line to history buffer"""
        self.historyindex += 1
        while len(self.historylist) >= self.historymax - 1:
            self.historylist.pop()
        self.historylist.append(line)
        self.historyindex = min(self.historyindex, len(self.historylist))


class Redirect:
    """Map self.write to a function"""

    def __init__(self, func: Callable):
        self.func = func

    def write(self, line: str) -> None:
        self.func(line)


class Console(QtWidgets.QWidget):
    """A GUI version of code.InteractiveConsole."""

    def __init__(
            self,
            context=locals(),  # context for interpreter
            history: int = 20,  # max lines in history buffer
            blockcount: int = 500  # max lines in output buffer
    ) :
        super().__init__()
        self.setcontext(context)
        self.buffer = []

        self.content = QtWidgets.QGridLayout(self)
        self.content.setContentsMargins(0, 0, 0, 0)
        self.content.setSpacing(0)

        # Display for output and stderr
        self.outdisplay = QtWidgets.QPlainTextEdit(self)
        self.outdisplay.setMaximumBlockCount(blockcount)
        self.outdisplay.setReadOnly(True)
        self.content.addWidget(self.outdisplay, 0, 0, 1, 2)

        # Use color to differentiate input, output and stderr
        self.inpfmt = self.outdisplay.currentCharFormat()
        self.outfmt = QtGui.QTextCharFormat(self.inpfmt)
        self.outfmt.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 255)))
        self.errfmt = QtGui.QTextCharFormat(self.inpfmt)
        self.errfmt.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))

        # Display input prompt left of input edit
        self.promptdisp = QtWidgets.QLineEdit(self)
        self.promptdisp.setReadOnly(True)
        self.promptdisp.setFixedWidth(15)
        self.promptdisp.setFrame(False)
        self.content.addWidget(self.promptdisp, 1, 0)
        self.setprompt('> ')

        # Enter commands here
        self.inpedit = LineEdit(history=history)
        self.inpedit.newline.connect(self.push)
        self.inpedit.setFrame(False)
        self.content.addWidget(self.inpedit, 1, 1)

    def setcontext(self, context):
        """Set context for interpreter"""
        self.interp = code.InteractiveInterpreter(context)

    def resetbuffer(self) -> None:
        """Reset the input buffer."""
        self.buffer = []

    def setprompt(self, text: str):
        self.prompt = text
        self.promptdisp.setText(text)

    def push(self, line: str) -> None:
        """Execute entered command.  Command may span multiple lines"""
        if line == 'clear':
            self.inpedit.clearhistory()
            self.outdisplay.clear()
        else:
            lines = line.split('\n')
            for line in lines:
                if re.match('^[\>\.] ', line):
                    line = line[2:]
                self.writeoutput(self.prompt + line, self.inpfmt)
                self.setprompt('. ')
                self.buffer.append(line)
            # Built a command string from lines in the buffer
            source = "\n".join(self.buffer)
            more = self.interp.runsource(source, '<console>')
            if not more:
                self.setprompt('> ')
                self.resetbuffer()

    def setfont(self, font: QtGui.QFont) -> None:
        """Set font for input and display widgets.  Should be monospaced"""
        self.outdisplay.setFont(font)
        self.inpedit.setFont(font)

    def write(self, line: str) -> None:
        """Capture stdout and display in outdisplay"""
        if len(line) != 1 or ord(line[0]) != 10:
            self.writeoutput(line.rstrip(), self.outfmt)

    def errorwrite(self, line: str) -> None:
        """Capture stderr and display in outdisplay"""
        self.writeoutput(line, self.errfmt)

    def writeoutput(self, line: str, fmt: QtGui.QTextCharFormat = None) -> None:
        """Set text formatting and display line in outdisplay"""
        if fmt is not None:
            self.outdisplay.setCurrentCharFormat(fmt)
        self.outdisplay.appendPlainText(line.rstrip())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    console = Console()
    console.setWindowTitle('Console')
    console.setfont(QtGui.QFont('Lucida Sans Typewriter', 10))

    # Redirect stdout to console.write and stderr to console.errorwrite
    redirect = Redirect(console.errorwrite)
    with redirect_stdout(console), redirect_stderr(redirect):
        console.show()
        sys.exit(app.exec())