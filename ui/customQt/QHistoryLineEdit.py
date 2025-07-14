#!/usr/bin/env python3
import lldb

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets, QtCore

import json
from pathlib import Path

HISTORY_FILE = Path("./input_history.json")


class QHistoryLineEdit(QLineEdit):
	
	availCompletitions = QtCore.pyqtSignal(object)
	
	lstCommands = []
	currCmd = 0
	doAddCmdToHist = True
	persistentHistory = False

	def save_history(self, history):
		with open(HISTORY_FILE, "w") as f:
			json.dump(history, f)

	def clear_history(self):
		with open(HISTORY_FILE, "w") as f:
			f.write("")

	def load_history(self):
		if HISTORY_FILE.exists():
			with open(HISTORY_FILE, "r") as f:
				return json.load(f)
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
				if self.currCmd > 0:
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
				self.addCommandToHistory()
			super(QHistoryLineEdit, self).keyPressEvent(event)
			pass
		else:
			super(QHistoryLineEdit, self).keyPressEvent(event)
		
	def addCommandToHistory(self):
		if self.doAddCmdToHist:
			newCommand = self.text()
			if len(self.lstCommands) > 0:
				if self.lstCommands[len(self.lstCommands) - 1] != newCommand:
					self.lstCommands.append(newCommand)
					self.currCmd = len(self.lstCommands) - 1
			else:
				self.lstCommands.append(newCommand)
				self.currCmd = len(self.lstCommands) - 1
			if self.persistentHistory:
				self.save_history(self.lstCommands)

	def clearCommandText(self, clearCommandHistory=False, clearPersistentHistory=False):
		self.setText("")
		if clearCommandHistory:
			self.lstCommands.clear()
		if clearPersistentHistory:
			self.clear_history()

				
			