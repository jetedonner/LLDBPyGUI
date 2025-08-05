#!/usr/bin/env python3
import lldb

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets, QtCore

import json
from pathlib import Path

from lib.settings import SettingsHelper, SettingsValues
from ui.helper.dbgOutputHelper import logDbgC

HISTORY_FILE = Path("./input_history.json")


class QHistoryLineEdit(QLineEdit):
	
	availCompletitions = QtCore.pyqtSignal(object)
	
	lstCommands = []
	currCmd = 0
	doAddCmdToHist = True
	persistentHistory = True

	def save_history(self, history):
		if HISTORY_FILE.exists():
			# count = 0
			# # oldHist = ""
			# # with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
			# # 	for chunk in iter(lambda: f.read(8192), ''):  # Read in small blocks
			# # 		count += len(chunk)
			# # 		oldHist += chunk
			# oldHist = self.load_history()
			# newHist = oldHist + history
			print(f"Total characters: {len(history)}... Char count inside boundaries: {'yes' if len(history) <= SettingsHelper().getValue(SettingsValues.MaxCommandHistoryCharCount) else 'no'}")
			if len(history) <= SettingsHelper().getValue(SettingsValues.MaxCommandHistoryCharCount):
				with open(HISTORY_FILE, "w") as f:
					json.dump(history, f)

	def clear_history(self):
		if HISTORY_FILE.exists():
			with open(HISTORY_FILE, "w") as f:
				f.write("")

	def load_history(self):
		if HISTORY_FILE.exists():
			with open(HISTORY_FILE, "r") as f:
				fileContent = f.read()
				if fileContent is not None and fileContent != "":
					return json.loads(fileContent)
		return []

	def __init__(self, doAddCmdToHist=True, persistentHistory=False):
		super().__init__()

		self.setStyleSheet("""
			QLineEdit {
				background-color: #282c34; /* Dark background */
				color: #abb2bf; /* Light grey text */
				border: 1px solid #3e4452;
				border-radius: 5px;
				padding: 10px;
				font: 12px 'Courier New';
			}
		""")
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
			else:
				if self.currCmd < len(self.lstCommands) - 1:
					self.currCmd += 1
					self.setText(self.lstCommands[self.currCmd])
			# Prevent event from being passed to QLineEdit for default behavior
			event.accept()

		elif event.key() == Qt.Key.Key_Return:
			if self.doAddCmdToHist:
				logDbgC(f"keyPressEvent() in QHistoryLineEdit ...")
				self.addCommandToHistory()
			super(QHistoryLineEdit, self).keyPressEvent(event)
			pass
		else:
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
				self.currCmd = -1 #len(self.lstCommands) - 1
			if self.persistentHistory:
				self.save_history(self.lstCommands)
		return newCommand

	def clearCommandText(self, clearCommandHistory=False, clearPersistentHistory=False):
		self.setText("")
		if clearCommandHistory:
			self.lstCommands.clear()
		if clearPersistentHistory:
			self.clear_history()

				
			