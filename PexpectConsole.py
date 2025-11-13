import sys
import pexpect
import re
from PyQt6.QtWidgets import QApplication, QTextEdit, QMainWindow
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QTextCursor, QFont

from helper.debugHelper import logDbgC
from ui.customQt.QAnsiColorTextEdit import QAnsiColorTextEdit


class PexpectConsole(QAnsiColorTextEdit):

	abort = False
	eofReachedCallback = pyqtSignal()

	def __init__(self, prompt="$ "):
		super().__init__()
		self.prompt = prompt
		self.command_buffer = ""
		self.history = []
		self.history_index = -1
		self.abort = False

		# Styling
		# self.setFont(QFont("Courier New", 12))
		# self.setStyleSheet("""
        #     QTextEdit {
        #         background-color: #282c34; /* Dark background */
        #         color: #abb2bf; /* Light grey text */
        #         border: 1px solid #3e4452;
        #         border-radius: 5px;
        #         padding: 5px;
        #         font: 12px 'Courier New';
        #     }
        # """)
		self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
		self.setUndoRedoEnabled(False)
		# self.setAcceptRichText(True)

		# Start shell
		# self.shell = pexpect.spawn("zsh", encoding="utf-8", echo=False)
		self.shell = pexpect.spawn("zsh", ["-i"], encoding="utf-8", echo=False)
		self.shell.sendline("source ~/.zshrc")

		# Prompt
		# self.insertHtml(f"<span style='color:white;'>{self.prompt}</span>")

		# Output reader
		self.timer = QTimer()
		self.timer.timeout.connect(self.read_output)
		self.timer.start(100)

	def keyPressEvent(self, event):
		key = event.key()
		if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
			cmd = self.command_buffer.strip()
			self.append("")  # move to next line
			self.shell.sendline(cmd)
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
		elif key == Qt.Key.Key_Control:
			super().keyPressEvent(event)
			return 
		else:
			char = event.text()
			if char:
				self.command_buffer += char
				self.insertPlainText(char)

		if key != Qt.Key.Key_C:
			self.moveCursor(QTextCursor.MoveOperation.End)


	def replace_current_line(self, text):
		cursor = self.textCursor()
		cursor.movePosition(QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.KeepAnchor)
		cursor.removeSelectedText()
		# cursor.insertText(self.prompt + text)
		self.insertHtml(f"<span style='color:white;'>{self.prompt + text}</span>")
		self.command_buffer = text

	def read_output(self):
		output = ""
		idx = 0
		try:
			while not self.abort and self.shell.expect("\n", timeout=0.01) == 0:
				output = self.shell.before.strip()
				if output:
					# ("<br/>" if not self.clean_output(output).endswith("<br/>") else "") +
					# print(f"output > {output}")
					logDbgC(f"output > {output}")
					# self.insertHtml(self.ansi_to_html(self.clean_output(output)) + ("<br/>" if idx > 0 else ""))
					self.appendEscapedText(self.clean_output(output) + ("<br/>" if idx > 0 else ""))
				if self.abort:
					break
				idx += 1
		except pexpect.exceptions.EOF:
			self.eofReachedCallback.emit()
			return
		except pexpect.exceptions.TIMEOUT:
			if output != "" and not self.abort:
				self.moveCursor(QTextCursor.MoveOperation.End)
				self.insertHtml(f"{self.prompt}")
				self.moveCursor(QTextCursor.MoveOperation.End)
			return

	def clean_output(self, text):
		# Remove control sequences like ESC[...m or ESC]...
		text = re.sub(r'\x1b\[[0-9;?]*[a-zA-Z]', '', text)
		text = re.sub(r'\x1b\][^\x07]*\x07', '', text)  # OSC sequences
		# text = re.sub(r'\x1b\(?[0-9;]*[a-zA-Z]', '', text)
		text = re.sub(r'\x07', '', text)  # Bell character
		text = re.sub(r'^\s*%.*$', '', text, flags=re.MULTILINE)  # zsh prompt lines
		return text.strip()

	def ansi_to_html(self, text):
		# Basic ANSI color mapping
		ansi_map = {
			'30': 'black', '31': 'red', '32': 'green', '33': 'yellow',
			'34': 'blue', '35': 'magenta', '36': 'cyan', '37': 'white',
			'0': 'white'
		}

		def replace_ansi(match):
			code = match.group(1)
			color = ansi_map.get(code, 'white')
			return f"</span><span style='color:{color};'>"

		# Escape HTML and apply color
		text = re.sub(r'\x1b\[([0-9]+)m', replace_ansi, text)
		# text = text.replace("\ [A](https://github.com/Codecors/clone4/tree/e63601aa30362de1a01453a752c29a49a224199c/vendor%2Fansiparse.js?copilot_analytics_metadata=eyJldmVudEluZm9fY2xpY2tTb3VyY2UiOiJjaXRhdGlvbkxpbmsiLCJldmVudEluZm9fY2xpY2tEZXN0aW5hdGlvbiI6Imh0dHBzOlwvXC9naXRodWIuY29tXC9Db2RlY29yc1wvY2xvbmU0XC90cmVlXC9lNjM2MDFhYTMwMzYyZGUxYTAxNDUzYTc1MmMyOWE0OWEyMjQxOTljXC92ZW5kb3IlMkZhbnNpcGFyc2UuanMiLCJldmVudEluZm9fY29udmVyc2F0aW9uSWQiOiJjOEdUdXREY25WRjFGTlZidDhLVjYiLCJldmVudEluZm9fbWVzc2FnZUlkIjoiaTdod0hGU2pIVFJNYXp1TjdqYUR1In0%3D&citationMarker=9F742443-6C92-4C44-BF58-8F5A7C53B6F1)x1b[0m", "</span>")
		return f"<span style='color:white;'>{text}</span>"


class ConsoleWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("PyQt6 Pexpect Console")
		self.setGeometry(100, 100, 800, 600)
		self.console = PexpectConsole()
		self.console.eofReachedCallback.connect(self.eofReachedCallback)
		self.setCentralWidget(self.console)

	def eofReachedCallback(self):
		self.close()

	def closeEvent(self, event):
		self.console.abort = True
		event.accept()


if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = ConsoleWindow()
	window.show()
	sys.exit(app.exec())


#
# import sys
# import pexpect
# import re
# from PyQt6.QtWidgets import QApplication, QTextEdit, QMainWindow
# from PyQt6.QtCore import Qt, QTimer
# from PyQt6.QtGui import QTextCursor, QFont
#
#
# class PexpectConsole(QTextEdit):
# 	def __init__(self, prompt="$ "):
# 		super().__init__()
# 		self.prompt = prompt
# 		self.command_buffer = ""
# 		self.history = []
# 		self.history_index = -1
#
# 		# Styling
# 		self.setFont(QFont("Courier New", 12))
# 		self.setStyleSheet("""
#             QTextEdit {
#                 background-color: #282c34; /* Dark background */
#                 color: #abb2bf; /* Light grey text */
#                 border: 1px solid #3e4452;
#                 border-radius: 5px;
#                 padding: 5px;
#                 font: 12px 'Courier New';
#             }
#         """)
# 		self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
# 		self.setUndoRedoEnabled(False)
# 		self.setAcceptRichText(True)
#
# 		# Start shell
# 		self.shell = pexpect.spawn("zsh", ["-i"], encoding="utf-8", echo=False)
# 		# self.shell = pexpect.spawn("zsh", encoding="utf-8", echo=False)
# 		# self.shell.sendline("source ~/.zshrc")
# 		self.shell.sendline("source ~/.zshrc")
# 		# self.shell.sendline("export PS1='$ '")
# 		self.shell.sendline('export PS1="$ "')
# 		# self.shell.sendline("autoload -Uz compinit; compinit")
# 		# self.shell.setecho(False)
#
# 		# Prompt
# 		# self.insertHtml(f"<span style='color:white;'>{self.prompt}</span>")
#
# 		# Output reader
# 		self.timer = QTimer()
# 		self.timer.timeout.connect(self.read_output)
# 		self.timer.start(100)
#
# 	def keyPressEvent(self, event):
# 		key = event.key()
# 		if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
# 			cmd = self.command_buffer.strip()
# 			self.append("")  # move to next line
# 			self.shell.sendline(cmd)
# 			if cmd:
# 				self.history.append(cmd)
# 				self.history_index = len(self.history)
# 			self.command_buffer = ""
# 			# self.insertHtml(f"<span style='color:white;'>{self.prompt}</span>")
# 		elif key == Qt.Key.Key_Backspace:
# 			if len(self.command_buffer) > 0:
# 				self.command_buffer = self.command_buffer[:-1]
# 				self.textCursor().deletePreviousChar()
# 		elif key == Qt.Key.Key_Tab:
# 			self.shell.send("\t")  # Send raw tab
# 			QTimer.singleShot(50, self.read_outputComp)
# 			return
# 		elif key == Qt.Key.Key_Up:
# 			if self.history and self.history_index > 0:
# 				self.history_index -= 1
# 				self.replace_current_line(self.history[self.history_index])
# 		elif key == Qt.Key.Key_Down:
# 			if self.history and self.history_index < len(self.history) - 1:
# 				self.history_index += 1
# 				self.replace_current_line(self.history[self.history_index])
# 			else:
# 				self.history_index = len(self.history)
# 				self.replace_current_line("")
# 		elif key == Qt.Key.Key_Control:
# 			super().keyPressEvent(event)
# 			return
# 		else:
# 			char = event.text()
# 			if char:
# 				self.command_buffer += char
# 				self.insertPlainText(char)
#
# 		if key != Qt.Key.Key_C:
# 			self.moveCursor(QTextCursor.MoveOperation.End)
# 		# else:
# 		# 	# super().keyPressEvent(event)
# 		# 	pass
#
# 	def replace_current_line(self, text):
# 		cursor = self.textCursor()
# 		cursor.movePosition(QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.KeepAnchor)
# 		cursor.removeSelectedText()
# 		# cursor.insertText(self.prompt + text)
# 		self.insertHtml(f"<span style='color:white;'>{self.prompt + text}</span>")
# 		self.command_buffer = text
#
# 	def read_outputComp(self):
# 		try:
# 			while True:
# 				self.shell.expect("\n", timeout=0.01)
# 				output = self.shell.before.strip()
# 				if output:
# 					cleaned = self.clean_output(output)
# 					self.insertHtml(self.ansi_to_html(cleaned))
# 		except pexpect.exceptions.TIMEOUT:
# 			pass
# 		self.moveCursor(QTextCursor.MoveOperation.End)
#
# 	def read_output(self):
# 		output = ""
# 		idx = 0
# 		try:
# 			while self.shell.expect("\n", timeout=0.01) == 0:
# 				output = self.shell.before.strip()
# 				if output:
# 					# ("<br/>" if not self.clean_output(output).endswith("<br/>") else "") +
# 					self.insertHtml(self.ansi_to_html(self.clean_output(output)) + ("<br/>" if idx > 0 else ""))
# 				idx += 1
# 		except pexpect.exceptions.TIMEOUT:
# 			if output != "":
# 				self.moveCursor(QTextCursor.MoveOperation.End)
# 				self.insertHtml(f"<span style='color:white;'>{self.prompt}</span>")
# 				self.moveCursor(QTextCursor.MoveOperation.End)
# 			# return
#
# 	def clean_output(self, text):
# 		# Remove control sequences like ESC[...m or ESC]...
# 		text = re.sub(r'\x1b\[[0-9;?]*[a-zA-Z]', '', text)
# 		text = re.sub(r'\x1b\][^\x07]*\x07', '', text)  # OSC sequences
# 		text = re.sub(r'\x1b\(?[0-9;]*[a-zA-Z]', '', text)
# 		text = re.sub(r'\x07', '', text)  # Bell character
# 		text = re.sub(r'^\s*%.*$', '', text, flags=re.MULTILINE)  # zsh prompt lines
# 		return text.strip()
#
# 	def ansi_to_html(self, text):
# 		# Basic ANSI color mapping
# 		ansi_map = {
# 			'30': 'black', '31': 'red', '32': 'green', '33': 'yellow',
# 			'34': 'blue', '35': 'magenta', '36': 'cyan', '37': 'white',
# 			'0': 'white'
# 		}
#
# 		def replace_ansi(match):
# 			code = match.group(1)
# 			color = ansi_map.get(code, 'white')
# 			return f"</span><span style='color:{color};'>"
#
# 		# Escape HTML and apply color
# 		text = re.sub(r'\x1b\[([0-9]+)m', replace_ansi, text)
# 		# text = text.replace("\ [A](https://github.com/Codecors/clone4/tree/e63601aa30362de1a01453a752c29a49a224199c/vendor%2Fansiparse.js?copilot_analytics_metadata=eyJldmVudEluZm9fY2xpY2tTb3VyY2UiOiJjaXRhdGlvbkxpbmsiLCJldmVudEluZm9fY2xpY2tEZXN0aW5hdGlvbiI6Imh0dHBzOlwvXC9naXRodWIuY29tXC9Db2RlY29yc1wvY2xvbmU0XC90cmVlXC9lNjM2MDFhYTMwMzYyZGUxYTAxNDUzYTc1MmMyOWE0OWEyMjQxOTljXC92ZW5kb3IlMkZhbnNpcGFyc2UuanMiLCJldmVudEluZm9fY29udmVyc2F0aW9uSWQiOiJjOEdUdXREY25WRjFGTlZidDhLVjYiLCJldmVudEluZm9fbWVzc2FnZUlkIjoiaTdod0hGU2pIVFJNYXp1TjdqYUR1In0%3D&citationMarker=9F742443-6C92-4C44-BF58-8F5A7C53B6F1)x1b[0m", "</span>")
# 		return f"<span style='color:white;'>{text}</span>"
#
#
# class ConsoleWindow(QMainWindow):
# 	def __init__(self):
# 		super().__init__()
# 		self.setWindowTitle("PyQt6 Pexpect Console")
# 		self.setGeometry(100, 100, 800, 600)
# 		self.console = PexpectConsole()
# 		self.setCentralWidget(self.console)
#
#
# if __name__ == "__main__":
# 	app = QApplication(sys.argv)
# 	window = ConsoleWindow()
# 	window.show()
# 	sys.exit(app.exec())
#

# import sys
# import pexpect
# from PyQt6.QtWidgets import QApplication, QTextEdit, QMainWindow
# from PyQt6.QtCore import Qt, QTimer
# from PyQt6.QtGui import QTextCursor
#
# class PexpectConsole(QTextEdit):
#     def __init__(self, prompt="$ "):
#         super().__init__()
#         self.prompt = prompt
#         self.command_buffer = ""
#         self.history = []
#         self.history_index = -1
#
#         self.setStyleSheet("background-color: black; color: white; font-family: monospace;")
#         self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
#         self.setUndoRedoEnabled(False)
#         self.setAcceptRichText(False)
#
#         self.shell = pexpect.spawn("zsh", encoding="utf-8", echo=False)
#         self.shell.sendline("source ~/.zshrc")
#         self.append(self.prompt)
#
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.read_output)
#         self.timer.start(100)
#
#     def keyPressEvent(self, event):
#         key = event.key()
#         if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
#             cmd = self.command_buffer.strip()
#             self.append("")  # move to next line
#             self.shell.sendline(cmd)
#             if cmd:
#                 self.history.append(cmd)
#                 self.history_index = len(self.history)
#             self.command_buffer = ""
#             self.append(self.prompt)
#         elif key == Qt.Key.Key_Backspace:
#             if len(self.command_buffer) > 0:
#                 self.command_buffer = self.command_buffer[:-1]
#                 self.textCursor().deletePreviousChar()
#         elif key == Qt.Key.Key_Up:
#             if self.history and self.history_index > 0:
#                 self.history_index -= 1
#                 self.replace_current_line(self.history[self.history_index])
#         elif key == Qt.Key.Key_Down:
#             if self.history and self.history_index < len(self.history) - 1:
#                 self.history_index += 1
#                 self.replace_current_line(self.history[self.history_index])
#             else:
#                 self.history_index = len(self.history)
#                 self.replace_current_line("")
#         else:
#             char = event.text()
#             if char:
#                 self.command_buffer += char
#                 self.insertPlainText(char)
#
#         self.moveCursor(QTextCursor.MoveOperation.End)
#
#     def replace_current_line(self, text):
#         cursor = self.textCursor()
#         cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock, QTextCursor.MoveMode.KeepAnchor)
#         cursor.removeSelectedText()
#         cursor.insertText(self.prompt + text)
#         self.command_buffer = text
#
#     def read_output(self):
#         try:
#             while self.shell.expect("\n", timeout=0.01) == 0:
#                 output = self.shell.before.strip()
#                 if output:
#                     self.append(output)
#         except pexpect.exceptions.TIMEOUT:
#             pass
#         self.moveCursor(QTextCursor.MoveOperation.End)
#
# class ConsoleWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("PyQt6 Pexpect Console")
#         self.setGeometry(100, 100, 800, 600)
#         self.console = PexpectConsole()
#         self.setCentralWidget(self.console)
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = ConsoleWindow()
#     window.show()
#     sys.exit(app.exec())
