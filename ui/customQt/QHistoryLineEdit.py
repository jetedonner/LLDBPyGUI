#!/usr/bin/env python3
import json
from pathlib import Path

import lldb
from PyQt6 import QtCore
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from helper.debugHelper import logDbgC
from lib.settings import SettingsHelper, SettingsValues

# from ui.helper.dbgOutputHelper import logDbgC

HISTORY_FILE = Path("./input_history.json")


class QHistoryLineEdit(QLineEdit):
	availCompletitions = QtCore.pyqtSignal(object)

	lstCommands = []
	currCmd = 0
	doAddCmdToHist = True
	persistentHistory = True
	historyFile = Path(HISTORY_FILE)

	def save_history(self, history):
		print(f"Total characters: {len(history)}... Char count inside boundaries: {'yes' if len(history) <= SettingsHelper().getValue(SettingsValues.MaxCommandHistoryCharCount) else 'no'}")
		if len(history) <= SettingsHelper().getValue(SettingsValues.MaxCommandHistoryCharCount):
			with open(self.historyFile, "w") as f:
				json.dump(history, f)

	def clear_history(self):
		if self.historyFile.exists():
			with open(self.historyFile, "w") as f:
				f.write("")

	def load_history(self):
		if self.historyFile.exists():
			with open(self.historyFile, "r") as f:
				fileContent = f.read()
				if fileContent is not None and fileContent != "":
					return json.loads(fileContent)
		return []

	def __init__(self, doAddCmdToHist=True, persistentHistory=False, historyFile=""):
		super().__init__()

		if historyFile != "":
			self.historyFile = Path(historyFile)
		# self.setStyleSheet("""
		# 	QLineEdit {
		# 		background-color: #282c34; /* Dark background */
		# 		color: #abb2bf; /* Light grey text */
		# 		border: 1px solid #3e4452;
		# 		border-radius: 5px;
		# 		padding: 10px;
		# 		font: 12px 'Courier New';
		# 	}
		# """)
		self.doAddCmdToHist = doAddCmdToHist
		self.persistentHistory = persistentHistory

		if self.doAddCmdToHist and persistentHistory:
			self.lstCommands = self.load_history()
		if len(self.lstCommands) > 0:
			self.currCmd = len(self.lstCommands)

		self.installEventFilter(self)  # Install event filter on the line edit

	def eventFilter(self, obj, event):
		if event.type() == QEvent.Type.ShortcutOverride:
			# Check if the shortcut is for tab key
			if event.key() == Qt.Key.Key_Tab:
				# Override shortcut and execute custom function
				self.data = self.text()
				matches = lldb.SBStringList()
				commandinterpreter = self.window().driver.debugger.GetCommandInterpreter()
				commandinterpreter.HandleCompletion(
					self.data, len(self.data), 0, -1, matches)

				if matches.GetSize() == 2:
					self.insert(matches.GetStringAtIndex(0))
					t = QtCore.QTimer()
					t.singleShot(0, self.onTimer)
				else:
					self.availCompletitions.emit(matches)
					t = QtCore.QTimer()
					t.singleShot(0, self.onTimer)

				#				event.ignore()
				#				self.custom_tab_function()
				return True  # Consume the event
		return super().eventFilter(obj, event)

	def onTimer(self):
		self.setFocus()

	def keyPressEvent(self, event):
		# logDbgC(f"HistoryLineEdit.keyPressEvent({event}) ...")
		#		print(f"keyPressEvent {event.key()}!!!!")
		if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
			#			print("Up or down key pressed")
			if event.key() == Qt.Key.Key_Up:
				if self.currCmd == -1:
					if len(self.lstCommands) > 0:
						self.currCmd = len(self.lstCommands) - 1
						self.setText(self.lstCommands[self.currCmd])
				elif self.currCmd > 0:
					self.currCmd -= 1
					if self.currCmd < len(self.lstCommands):
						self.setText(self.lstCommands[self.currCmd])
				self.setCursorPosition(len(self.text()))
				logDbgC(f"self.cursorPosition: {self.cursorPosition()} ...")
				return
			else:
				if self.currCmd < len(self.lstCommands) - 1:
					self.currCmd += 1
					self.setText(self.lstCommands[self.currCmd])
			# Prevent event from being passed to QLineEdit for default behavior
			event.accept()

		elif event.key() == Qt.Key.Key_Return:
			if self.doAddCmdToHist:
				print(f"keyPressEvent() in QHistoryLineEdit ...")
				self.addCommandToHistory()
		# super(QHistoryLineEdit, self).keyPressEvent(event)
		# pass
		# else:
		super(QHistoryLineEdit, self).keyPressEvent(event)

	def addCommandToHistory(self):
		newCommand = ""
		if self.doAddCmdToHist:
			newCommand = self.text()
			if newCommand is None or newCommand == "":
				return newCommand

			if len(self.lstCommands) > 0:
				if self.lstCommands[len(self.lstCommands) - 1] != newCommand:
					self.lstCommands.append(newCommand)
					# self.currCmd = len(self.lstCommands) - 1
					self.currCmd = -1  # len(self.lstCommands) - 1
			else:
				self.lstCommands.append(newCommand)
				self.currCmd = -1  # len(self.lstCommands) - 1
			if self.persistentHistory:
				self.save_history(self.lstCommands)
		return newCommand

	def clearCommandText(self, clearCommandHistory=False, clearPersistentHistory=False):
		self.setText("")
		if clearCommandHistory:
			self.lstCommands.clear()
		if clearPersistentHistory:
			self.clear_history()
