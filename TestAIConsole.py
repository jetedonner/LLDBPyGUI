import sys
import re
import html
import subprocess
from PyQt6.QtWidgets import QApplication, QTextEdit, QMainWindow
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor

class ConsoleTextEdit(QTextEdit):
    ansi_colors = {
        "\x1b[30m": "black", "\x1b[31m": "red", "\x1b[32m": "green", "\x1b[33m": "yellow",
        "\x1b[34m": "blue", "\x1b[35m": "magenta", "\x1b[36m": "cyan", "\x1b[37m": "white",
        "\x1b[0m": "white"
    }

    def __init__(self, prompt="$ "):
        super().__init__()
        self.prompt = prompt
        self.setAcceptRichText(True)
        self.setUndoRedoEnabled(False)
        self.setCursorWidth(2)
        self.setStyleSheet("""
			QTextEdit {
				background-color: #282c34; /* Dark background */
				color: #abb2bf; /* Light grey text */
				border: 1px solid #3e4452;
				border-radius: 5px;
				padding: 5px;
				font: 12px 'Courier New';
			}
		""")
        # self.setStyleSheet("""
        # 	QTextEdit {
        # 		background-color: #282c34; /* Dark background */
        # 		color: #abb2bf; /* Light grey text */
        # 		border: 1px solid #3e4452;
        # 		border-radius: 5px;
        # 		padding: 5px;
        # 		font: 12px 'Courier New';
        # 	}
        # """)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        self.setHtml(f"<span style='color:white;'>{self.prompt}</span>")
        self.command_buffer = ""
        self.marker = "__END__MARKER__"
        self.history = []
        self.history_index = -1
        self.multiline_mode = False

        self.proc = subprocess.Popen(
            ["zsh"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        self.proc.stdin.write("source ~/.zshrc\n")
        self.proc.stdin.flush()

        self.moveCursor(QTextCursor.MoveOperation.End)

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if modifiers == Qt.KeyboardModifier.ShiftModifier:
                self.command_buffer += "\n"
                self.insertPlainText("\n")
                return
            cmd = self.command_buffer.strip()
            self.append("")  # move to next line
            self.send_command(cmd)
            if cmd:
                self.history.append(cmd)
                self.history_index = len(self.history)
            self.command_buffer = ""
            # self.insertHtml(f"<span style='color:white;'>{self.prompt}</span>")
        elif key == Qt.Key.Key_Backspace:
            if len(self.command_buffer) > 0:
                self.command_buffer = self.command_buffer[:-1]
                self.textCursor().deletePreviousChar()
        elif key == Qt.Key.Key_Up:
            if self.history and self.history_index > 0:
                self.history_index -= 1
                self.replace_current_line(self.history[self.history_index])
        elif key == Qt.Key.Key_Down:
            if self.history and self.history_index < len(self.history) - 1:
                self.history_index += 1
                self.replace_current_line(self.history[self.history_index])
            else:
                self.history_index = len(self.history)
                self.replace_current_line("")
        else:
            char = event.text()
            if char:
                self.command_buffer += char
                self.insertPlainText(char)

        self.moveCursor(QTextCursor.MoveOperation.End)

    def replace_current_line(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(self.prompt + text)
        self.command_buffer = text

    def send_command(self, cmd):
        if not cmd:
            self.insertHtml(f"<span style='color:white;'>{self.prompt}</span>")
            return
        try:
            self.proc.stdin.write(f"{cmd}\necho {self.marker}\n")
            self.proc.stdin.flush()
            QTimer.singleShot(50, self.read_output)
        except Exception as e:
            self.insertHtml(f"<span style='color:red;'>Error: {e}</span>")

    def read_output(self):
        while True:
            line = self.proc.stdout.readline()
            if not line or self.marker in line:
                break
            self.appendEscapedText(line)
        self.insertHtml(f"<span style='color:white;'>{self.prompt}</span>")

    def appendEscapedText(self, text):
        html_text = self.format_ansi(text)
        self.moveCursor(QTextCursor.MoveOperation.End)
        self.insertHtml(html_text)
        self.moveCursor(QTextCursor.MoveOperation.End)

    def format_ansi(self, text):
        text = html.escape(text)
        text = text.replace("\r\n", "<br/>\r\n")
        text = text.replace("\n", "<br/>\n")
        for code, color in self.ansi_colors.items():
            text = text.replace(html.escape(code), f"</span><span style='color:{color};'>")
        return f"<span style='color:white;'>{text}</span>"

class ConsoleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Console")
        self.setGeometry(100, 100, 800, 600)
        self.console = ConsoleTextEdit()
        self.setCentralWidget(self.console)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConsoleWindow()
    window.show()
    sys.exit(app.exec())