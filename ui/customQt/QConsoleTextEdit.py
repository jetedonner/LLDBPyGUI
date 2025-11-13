#!/usr/bin/env python3

import html
import re
import sys

from PyQt6.QtCore import *
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import *

from ui.customQt.QAnsiColorTextEdit import QAnsiColorTextEdit

# from config import ConfigClass  # FIXME: Turn back on when ConfigClass is fixed
# from helper.debugHelper import logDbgC  # FIXME: Turn back on when ConfigClass is fixed

APP_NAME = "ConsoleTextEditWindow-TEST"
WINDOW_SIZE = 720
APP_VERSION = "v0.0.1"

class QConsoleTextEdit(QAnsiColorTextEdit):
	# ansi_dict = {"\x1b[30m": "black", "\x1b[31m": "red", "\x1b[32m": "green", "\x1b[33m": "yellow", "\x1b[34m": "blue",
	# 			 "\x1b[35m": "magenta", "\x1b[36m": "cyan", "\x1b[37m": "white", "\x1b[0m": "white", "\x1b[4m": "white",
	# 			 "\x1b[0;30m": "blacklight", "\x1b[0;31m": "IndianRed", "\x1b[0;32m": "LightGreen",
	# 			 "\x1b[0;33m": "LightYellow", "\x1b[0;34m": "LightBlue", "\x1b[0;35m": "LightPink",
	# 			 "\x1b[0;36m": "LightCyan", "\x1b[0;37m": "WhiteSmoke"}
	#
	# patternEscapedStdAnsi = re.compile(r"\x1b\[\d{1,}[m]")
	# patternEscapedLightAnsi = re.compile(r"\x1b\[[0][;]\d{1,}[m]")
	currDir = "LLDBGUI"
	promptTemplate = f"dave@Ava #currDir# % "
	prompt = promptTemplate.replace("#currDir#", currDir)
	proc = None

	def setPrompt(self, newPrompt = ""):
		if newPrompt != "":
			self.prompt = newPrompt

	def __init__(self, prompt=""):
		super().__init__()
		self.proc = None

		self.setPrompt(prompt)
		# self.setAcceptRichText(True)
		# fontStr = "Courier New"
		# font = QFont(fontStr)
		# self.setFont(font) # ConfigClass.font) # FIXME: Turn back on when ConfigClass is fixed
		#
		# self.setContentsMargins(0, 0, 0, 0)
		self.installEventFilter(self)
		self.append(self.prompt)

	marker = "__END__MARKER__"

	def sendCmd(self, cmd):
		import subprocess
		if cmd.startswith(self.prompt):
			cmd = cmd.removeprefix(self.prompt)

		parts = cmd.split(" ")
		if len(parts) > 0:
			try:
				# # proc = subprocess.Popen(
				# # 	# ["python3", "-c", "print('Hello from parent')"],
				# # 	cmd.split(" "),
				# # 	stdout=subprocess.PIPE,
				# # 	stderr=subprocess.PIPE,
				# # 	text=True
				# # )
				# # output, error = proc.communicate()
				# # self.append(f"{output.strip()}\n")
				# # extend
				# arrCmds = ["zsh", "-i", "-c", cmd]
				# # arrCmds.extend(parts)
				# proc = subprocess.Popen(
				# 	arrCmds,
				# 	stdout=subprocess.PIPE,
				# 	stderr=subprocess.PIPE,
				# 	text=True
				# )
				# out, err = proc.communicate()
				# print("Output:", out)
				# print("Error:", err)
				# self.append(f"{out.strip()}\n")
				import subprocess

				if not self.proc:
					self.proc = subprocess.Popen(
						["zsh"],
						stdin=subprocess.PIPE,
						stdout=subprocess.PIPE,
						stderr=subprocess.STDOUT,
						text=True,
						bufsize=1  # Line-buffered
					)
					self.proc.stdin.write("source ~/.zshrc\n")
					self.proc.stdin.flush()
					self.proc.stdin.write("source ~/.zprofile\n")
					self.proc.stdin.flush()

				# self.proc.stdin.write(f"{cmd}\necho {self.marker}\n")
				# self.proc.stdin.flush()
				#
				# output_lines = []
				# while True:
				# 	line = self.proc.stdout.readline()
				# 	if not line:
				# 		break  # Subprocess died
				# 	if self.marker in line:
				# 		break
				# 	output_lines.append(line.strip())

				self.proc.stdin.write(f"{cmd}\npwd\necho __END__MARKER__\n")
				self.proc.stdin.flush()

				output_lines = []
				while True:
					line = self.proc.stdout.readline()
					if "__END__MARKER__" in line:
						break
					output_lines.append(line.strip())

				# Extract the last part of the path
				if output_lines:
					full_path = output_lines[-1]
					last_part = full_path.rstrip("/").split("/")[-1]
					# self.append(f"Current directory: {last_part}")
					self.currDir = last_part
					self.prompt = self.promptTemplate.replace("#currDir#", self.currDir)

				for line in output_lines[:len(output_lines) - 1]:
					self.append(line)
				self.append(self.prompt)
				if len(self.historyshell) <= 0 or (len(self.historyshell) > 0 and cmd != self.historyshell[len(self.historyshell) - 1]):
					self.historyshell.append(cmd)
				self.currHistIdx = len(self.historyshell)
				# # Start a persistent zsh shell
				# if not self.proc:
				# 	self.proc = subprocess.Popen(
				# 		["zsh", "-i", "-c", f"{cmd}\necho {self.marker}\n"],
				# 		stdin=subprocess.PIPE,
				# 		stdout=subprocess.PIPE,
				# 		stderr=subprocess.PIPE,
				# 		text=True
				# 	)
				# else:
				# 	self.proc.stdin.write(f"{cmd}\necho {self.marker}\n")
				# 	self.proc.stdin.flush()
				#
				# output_lines = []
				# while True:
				# 	line = self.proc.stdout.readline()
				# 	if self.marker in line:
				# 		break
				# 	output_lines.append(line.strip())
				#
				# for line in output_lines:
				# 	# self.append(line)
				# 	self.append(f"{line}")
				# self.append(f"\n")
				# # # Send a command
				# # self.proc.stdin.write(f"{cmd}\n")
				# # self.proc.stdin.flush()
				# #
				# # # Read output (you may need to read multiple lines)
				# # # output = self.proc.stdout.readline()
				# # lines = self.proc.stdout.readlines()
				# # # while output:
				# # for line in lines:
				# # 	print("Output:", line.strip())
				# # 	self.append(f"{line.strip()}\n")
				# # 	# output = self.proc.stdout.readline()
			except Exception as e:
				self.append(f"Error executing command: {e}\n")
		else:
			self.append(f"Command not found ...\n")

	def eventFilter(self, widget, event):
		if event.type() == QEvent.Type.KeyPress and widget is self:
			print(f"IN EVENTFILTER")
			key = event.key()
			if key == Qt.Key.Key_Escape:
				print(f'escape')
			else:
				if key == Qt.Key.Key_Return:
					last_block = self.document().lastBlock()
					last_line_text = last_block.text()
					print(f"Last line: {last_line_text}")
					if last_line_text != "":
						self.sendCmd(last_line_text)
						# self.append('return')
						return True
				elif key == Qt.Key.Key_Enter:
					# self.sendCmd("zsh")
					self.append('enter')
				# return True
		return QWidget.eventFilter(self, widget, event)

	currHistIdx = 0
	historyshell = []
	# class QConsoleTextEdit(QTextEdit):
	def keyPressEvent(self, event):
		# Ignore all navigation keys
		if event.key() in (
				Qt.Key.Key_Up,
				Qt.Key.Key_Down,
				Qt.Key.Key_Left,
				Qt.Key.Key_Right,
				Qt.Key.Key_PageUp,
				Qt.Key.Key_PageDown,
				Qt.Key.Key_Home,
				Qt.Key.Key_End
		):
			if event.key() in (
					Qt.Key.Key_Up,
					Qt.Key.Key_Down
			):
				oldHistCmd = ""
				if self.currHistIdx >= 0 and self.currHistIdx < len(self.historyshell):
					oldHistCmd = self.historyshell[self.currHistIdx]
				last_block = self.document().lastBlock()
				last_line_text = last_block.text()
				bRemoveLastCmd = False
				if event.key() == Qt.Key.Key_Up:
					self.currHistIdx -= 1
				else:
					self.currHistIdx += 1
					if self.currHistIdx >= len(self.historyshell):
						bRemoveLastCmd = True
				self.currHistIdx = max(0, min(self.currHistIdx, len(self.historyshell) - 1))

				if not last_line_text.endswith(self.historyshell[self.currHistIdx]) or bRemoveLastCmd:
					if last_line_text.endswith(oldHistCmd) or bRemoveLastCmd:
						if self.toPlainText().endswith(oldHistCmd):
							cleanStr = self.toPlainText().removesuffix(oldHistCmd)
							self.setPlainText(cleanStr)
							self.moveCursor(QTextCursor.MoveOperation.End)
					if not bRemoveLastCmd:
						self.insertPlainText(self.historyshell[self.currHistIdx])
				if bRemoveLastCmd:
					self.currHistIdx += 1
			return  # Do nothing

		if event.key() == Qt.Key.Key_Backspace:
			last_block = self.document().lastBlock()
			last_line_text = last_block.text()
			print(f"Last line: {last_line_text}")
			if last_line_text != "":
				if last_line_text.endswith(self.prompt):
					return

		# Handle other keys normally
		super().keyPressEvent(event)

		if event.key() != Qt.Key.Key_Control: # , Qt.Key.Key_Command):
			# Force cursor to end
			self.moveCursor(QTextCursor.MoveOperation.End)

	def mousePressEvent(self, event):
		modifiers = event.modifiers()
		if not modifiers & Qt.KeyboardModifier.ShiftModifier and not modifiers & Qt.KeyboardModifier.ControlModifier:
			self.moveCursor(QTextCursor.MoveOperation.End)
			event.ignore()

	# def setEscapedText(self, text):
	# 	formattedText = self.formatText(text)
	# 	self.setHtml(formattedText)
	# 	self.append(f"\n")
	#
	# def appendEscapedText(self, text, newLine=True):
	# 	htmlText = self.formatText(text)
	# 	if newLine or self.toHtml() == "":
	# 		self.append(f"{htmlText}\n")
	# 	else:
	# 		self.insertHtml(f"{htmlText}\n")
	#
	# def formatSpecialChars(self, text):
	# 	text = html.escape(text, True)
	# 	text = text.replace("\r\n", "<br/>\r\n")
	# 	text = text.replace("\n", "<br/>\r\n")
	# 	text = text.replace(" ", "&nbsp;")
	# 	text = text.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
	# 	return text
	#
	# def formatText(self, text):
	# 	text = self.formatSpecialChars(text)
	# 	ansi_colors = self.patternEscapedStdAnsi.finditer(text)
	# 	formattedText = "<span color='white'>"
	# 	currPos = 0
	# 	for ansi_color in ansi_colors:
	# 		formattedText += text[currPos:(ansi_color.start())]
	# 		formattedText += "</span><span style='color: " + self.ansi_dict[ansi_color.group(0)] + "'>"
	# 		currPos = ansi_color.end()
	# 	formattedText += text[currPos:]
	# 	formattedText += "</span>"
	#
	# 	ansi_colors = self.patternEscapedLightAnsi.finditer(formattedText)
	# 	formattedText2 = "<span color='white'>"
	# 	currPos = 0
	# 	for ansi_color in ansi_colors:
	# 		formattedText2 += formattedText[currPos:(ansi_color.start())]
	# 		formattedText2 += "</span><span style='color: " + self.ansi_dict[ansi_color.group(0)] + "'>"
	# 		currPos = ansi_color.end()
	# 	formattedText2 += formattedText[currPos:]
	# 	formattedText2 += "</span>"
	# 	return formattedText2


class QConsoleTextEditWindow(QMainWindow):
	mytext = "" # "thread #1: tid = 0xa8f62d, 0x0000000100003f40 hello_world_test_loop`main, queue = \x1b[32m'com.apple.main-thread'\x1b[0m, stop reason = \x1b[31mbreakpoint 1.1\x1b[0m\nthread #2: tid = 0xa8f62d, 0x0000000100003f40 hello_world_test_loop`main, queue = \x1b[35m'com.apple.main-thread'\x1b[0m, stop reason = \x1b[36mbreakpoint 1.1\x1b[0m"

	def __init__(self):
		super().__init__()
		self.setWindowTitle(APP_NAME + " " + APP_VERSION)
		self.setBaseSize(WINDOW_SIZE * 2, WINDOW_SIZE)
		self.setMinimumSize(WINDOW_SIZE * 2, WINDOW_SIZE + 72)
		self.layout = QHBoxLayout()
		self.centralWidget = QWidget(self)
		self.centralWidget.setLayout(self.layout)
		self.setCentralWidget(self.centralWidget)
		self.txtConsole = QConsoleTextEdit()
		self.layout.addWidget(self.txtConsole)
		# self.txtConsole.setEscapedText(self.mytext)
		# self.txtConsole.appendEscapedText(self.mytext)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = QConsoleTextEditWindow()
	window.app = app
	window.show()
	try:
		sys.exit(app.exec())
	except SystemExit:
		print("LLDBPyGUI application exited cleanly.")