from PyQt6.QtWidgets import QApplication, QTextEdit
from PyQt6.QtGui import QTextCursor, QKeyEvent
from PyQt6.QtCore import Qt

from config import *
from ui.customQt.QConsoleTextEdit import QConsoleTextEdit
from ui.dbgOutputTextEdit import OutputStream
from ui.helper.dbgOutputHelper import logDbgC


class ConsoleWidget(QConsoleTextEdit):
    def __init__(self):
        super().__init__()
        # self.setFontFamily("Courier")
        # self.setText("Welcome to the PyQt Console!\ndave@Mia /: ")
        # self.prompt = ">>> "
        self.prompt = "dave@Mia /: "
        self.setUndoRedoEnabled(False)
        self.setTabChangesFocus(True)

        self.setStyleSheet("""
            QTextEdit {
                background-color: #282c34; /* Dark background */
                color: #abb2bf; /* Light grey text */
                border: 1px solid #3e4452;
                border-radius: 5px;
                padding: 5px;
                font: 'Courier New';
            }
        """)
        # self.setFontFamily("Courier New")

        self.output_stream = OutputStream()
        # debug_console = DebugConsole()


        self.output_stream.text_written.connect(self.append_text)

        # Redirect Python stdout
        import sys
        sys.stdout = self.output_stream

    def append_text(self, text):
        # logDbgC(f"append_text called .... {text}")
        self.moveCursor(self.textCursor().MoveOperation.EndOfLine)
        # self.append(text)
        # self.textCursor().insertText(text)
        self.appendEscapedText(text, False)
        self.ensureCursorVisible()

    def keyPressEvent(self, event):
        logDbgC(f"ConsoleWidget => keyPressEvent: {event}...")

        cursor = self.textCursor()
        doc_text = self.toPlainText()
        last_line_start = doc_text.rfind('\n') + 1
        prompt_pos = doc_text.rfind(self.prompt, last_line_start)

        cursor_pos = cursor.position()
        input_start = prompt_pos + len(self.prompt)

        # Prevent backspacing into prompt
        if event.key() == Qt.Key.Key_Backspace:
            if cursor_pos <= input_start:
                return  # Block backspace
        elif cursor_pos < input_start:
            # Move cursor back into safe zone
            cursor.setPosition(len(doc_text))
            self.setTextCursor(cursor)

        if event.key() == Qt.Key.Key_Return:
            user_input = doc_text[input_start:]
            self.append(f"{user_input}\n")
            self.insertPlainText(f"{self.prompt}")
            self.moveCursor(QTextCursor.MoveOperation.End)
        else:
            super().keyPressEvent(event)

# app = QApplication([])
# console = ConsoleWidget()
# console.resize(600, 400)
# console.show()
# app.exec()
