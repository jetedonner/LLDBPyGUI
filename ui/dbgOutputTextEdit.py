from PyQt6.QtWidgets import QApplication, QTextEdit
from PyQt6.QtGui import QTextCursor, QKeyEvent
from PyQt6.QtCore import Qt
from datetime import datetime

from config import *
from lib.settings import *

class DbgOutputWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layHMain = QHBoxLayout()
        self.layCtrls = QVBoxLayout()

        self.cmdShrink = QPushButton()
        # self.cmdShrink.setToolTip("Hide Debug Output...")
        self.cmdShrink.setIcon(ConfigClass.iconShrink)
        self.cmdShrink.setMaximumWidth(18)
        self.cmdShrink.clicked.connect(self.cmdShrink_clicked)
        self.cmdShrink.setContentsMargins(0, 0, 0, 0)
        self.cmdShrink.setStatusTip(f"Hide debug output console...")
        self.layCtrls.setContentsMargins(10, 0, 0, 0)
        self.layCtrls.addWidget(self.cmdShrink)

        self.cmdClear = QPushButton()
        # self.cmdClear.setToolTip("Clear Debug Output...")
        self.cmdClear.setIcon(ConfigClass.iconClear)
        self.cmdClear.setMaximumWidth(18)
        self.cmdClear.clicked.connect(self.cmdClear_clicked)
        self.cmdClear.setContentsMargins(0, 0, 0, 0)
        self.cmdShrink.setStatusTip(f"Clear debug output console...")
        # self.layCtrls.setContentsMargins(10, 0, 0, 0)
        self.layCtrls.addWidget(self.cmdClear)

        # Add stretch to push everything above it to the top
        self.layCtrls.addStretch()
        self.wdtCtrls = QWidget()
        self.wdtCtrls.setLayout(self.layCtrls)
        self.layHMain.addWidget(self.wdtCtrls)
        self.txtDbg = DbgOutputTextEdit()
        self.txtDbg.setContentsMargins(0, 0, 0, 0)
        self.layHMain.addWidget(self.txtDbg)
        self.layHMain.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layHMain)

    def logDbg(self, logMsg):
        self.txtDbg.logDbg(logMsg)

    def cmdShrink_clicked(self):
        self.window().splitterDbgMain.setSizes([1, 0])
        pass

    def cmdClear_clicked(self):
        self.txtDbg.setText("")
        pass

class DbgOutputTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        # self.setFontFamily("Courier")
        # self.setText("Welcome to the PyQt Console!\ndave@Mia /: ")
        # self.prompt = ">>> "

        # self.layHMain = QHBoxLayout()
        # self.wdtHMain = QWidget()

        # self.setText("Output: ...")
        self.setReadOnly(True)
        self.setUndoRedoEnabled(False)
        self.setTabChangesFocus(True)

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
        # self.setFontFamily("Courier New")

    def logDbg(self, logMsg):
        # sDateTimeFormat = "%H:%M:%S"
        # if SettingsHelper().getValue(SettingsValues.ShowDateInLogView):
        #     sDateTimeFormat = "%Y-%m-%d %H:%M:%S"
        # now = datetime.now()
        # timestamp = now.strftime(sDateTimeFormat)  # Format as 'YYYY-MM-DD HH:MM:SS'
        #
        # self.append(f"{timestamp}: {logMsg}")
        self.append(logMsg)
    # def keyPressEvent(self, event):
    #     cursor = self.textCursor()
    #     doc_text = self.toPlainText()
    #     last_line_start = doc_text.rfind('\n') + 1
    #     prompt_pos = doc_text.rfind(self.prompt, last_line_start)
    #
    #     cursor_pos = cursor.position()
    #     input_start = prompt_pos + len(self.prompt)
    #
    #     # Prevent backspacing into prompt
    #     if event.key() == Qt.Key.Key_Backspace:
    #         if cursor_pos <= input_start:
    #             return  # Block backspace
    #     elif cursor_pos < input_start:
    #         # Move cursor back into safe zone
    #         cursor.setPosition(len(doc_text))
    #         self.setTextCursor(cursor)
    #
    #     if event.key() == Qt.Key.Key_Return:
    #         user_input = doc_text[input_start:]
    #         self.append(f"{user_input}\n")
    #         self.insertPlainText(f"{self.prompt}")
    #         self.moveCursor(QTextCursor.MoveOperation.End)
    #     else:
    #         super().keyPressEvent(event)

# app = QApplication([])
# console = ConsoleWidget()
# console.resize(600, 400)
# console.show()
# app.exec()
