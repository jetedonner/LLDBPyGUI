#!/usr/bin/env python3
import lldb 
from itertools import islice

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from ui.customQt.QSwitch import *
from ui.customQt.QHistoryLineEdit import *
from ui.customQt.QConsoleTextEdit import *

from lib.settings import *
from config import *
from ui.helper.dbgOutputHelper import logDbgC


class StopHookWidget(QWidget):
	
#	actionShowMemory = None
	workerManager = None
	def __init__(self, workerManager):
		super().__init__()
		
		self.workerManager = workerManager
		
		self.setHelper = SettingsHelper()
		
		# self.wdgCmd = QWidget()
#		self.wdgCommands = QWidget()
		self.layCmdParent = QVBoxLayout()
		self.layCmdParent.setContentsMargins(0, 0, 0, 0)
		self.layCmdParent.addWidget(QLabel(f"STOP-HOOK"))
		# # self.layCmdParent.setSpacing(5)
		# self.layCmd = QHBoxLayout()
		# self.layCmd.setContentsMargins(0, 0, 0, 0)
		# self.wdgCmd.setLayout(self.layCmd)
		self.setLayout(self.layCmdParent)
		
		# # self.lblCmd = QLabel("Command: ")
		# # self.lblCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		# # self.lblCmd.setStyleSheet("""
		# # 	QLabel {
		# # 		color: #abb2bf;
		# # 		padding: 5px;
		# # 	}
		# # """)
		#
		# # self.lstCommands = self.load_history()
		#
		# self.txtCmd = QHistoryLineEdit(self.setHelper.getValue(SettingsValues.CmdHistory), self.setHelper.getValue(SettingsValues.PersistentCommandHistory))
		# self.txtCmd.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		# # self.txtCmd.setText(ConfigClass.initialCommand)
		# self.txtCmd.setPlaceholderText("Enter LLDB command here ...")
		# self.txtCmd.returnPressed.connect(self.execCommand_clicked)
		# self.txtCmd.availCompletitions.connect(self.handle_availCompletitions)
		# self.txtCmd.setFocus(Qt.FocusReason.NoFocusReason)
		# self.txtCmd.setStyleSheet("""
		# 	QLineEdit {
		# 		background-color: #3e4452; /* Slightly lighter dark */
		# 		color: #abb2bf;
		# 		border: 1px solid #5c6370;
		# 		border-radius: 5px;
		# 		padding: 5px;
		# 		font: 12px 'Courier New';
		# 	}
		# 	QLineEdit:focus {
		# 		/*border: 1px solid #61afef;*/ /* Highlight on focus */
		# 	}
		# """)
		#
		# self.swtAutoscroll = QSwitch("Autoscroll")
		# self.swtAutoscroll.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		# self.swtAutoscroll.setChecked(True)
		#
		# self.cmdExecuteCmd = QPushButton("Execute")
		# self.cmdExecuteCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		# self.cmdExecuteCmd.clicked.connect(self.execCommand_clicked)
		#
		# self.cmdClear = QPushButton()
		# self.cmdClear.setIcon(ConfigClass.iconTrash)
		# self.cmdClear.setToolTip("Clear the Commands log")
		# self.cmdClear.setIconSize(QSize(16, 16))
		# self.cmdClear.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		# self.cmdClear.clicked.connect(self.clear_clicked)
		#
		# # self.layCmd.addWidget(self.lblCmd)
		# self.layCmd.addWidget(self.txtCmd)
		# self.layCmd.addWidget(self.cmdExecuteCmd)
		# self.layCmd.addWidget(self.swtAutoscroll)
		# self.layCmd.addWidget(self.cmdClear)
		# self.wdgCmd.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
		#
		# self.txtCommands = QConsoleTextEdit()
		# self.txtCommands.setReadOnly(True)
		# self.txtCommands.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		# self.txtCommands.setFont(ConfigClass.font)
		# self.txtCommands.setText("Here you can run LLDB commands. Type 'help' for a list of available commands.\n")
		# self.setStyleSheet("""
		# 		    QConsoleTextEdit {
		# 		        /* background-color: #f0f0f0;
		# 		        gridline-color: #ccc;*/
		# 		        font: 12px 'Courier New';
		# 		        background-color: #282c34; /* Dark background */
		#                 color: #abb2bf; /* Light grey text */
		#                 /*border: 1px solid #3e4452;*/
		#                 border-radius: 5px;
		#                 padding: 5px;
		# 		    }
		# 		""")
		# self.layCmdParent.addWidget(self.txtCommands)
		# self.layCmdParent.addWidget(self.wdgCmd)
		
# 	def handle_availCompletitions(self, compl):
#
# 		self.txtCommands.append("Available Completions:")
# #		self.win.scroll(1)
# 		for m in islice(compl, 1, None):
# 			self.txtCommands.append(m)
# 		pass
#
# 	def clear_clicked(self):
# 		self.txtCommands.setText("")
# #		command_interpreter = self.debugger.GetCommandInterpreter()
#
# #		self.data = self.txtCmd.text()
# #		matches = lldb.SBStringList()
# #		commandinterpreter = self.workerManager.driver.debugger.GetCommandInterpreter()
# #		commandinterpreter.HandleCompletion(
# #			self.data, len(self.data), 0, -1, matches)
# #		if len(matches) > 0:
# #			self.txtCmd.insert(matches.GetStringAtIndex(0))
# #		for match in matches:
# #			print(match)
#
# 	def execCommand_clicked(self):
# 		logDbgC(f"execCommand_clicked() in commandsWidget ...")
# 		newCommand = ""
# 		if self.setHelper.getValue(SettingsValues.CmdHistory):
# 			newCommand = self.txtCmd.addCommandToHistory()
# 			self.txtCmd.setText("")
#
# 		self.txtCommands.append(f"({PROMPT_TEXT}) {newCommand.strip()}")
# 		if newCommand.strip().lower() in ["clear", "clr"]:
# 			self.clear_clicked()
# 		else:
# 			self.workerManager.start_execCommandWorker(newCommand, self.handle_commandFinished)
#
# 	def handle_commandFinished(self, res):
# 		sOutput = ""
# 		if res.Succeeded():
# 			sOutput = res.GetOutput()
# 			self.txtCommands.appendEscapedText(sOutput)
# 			# self.center_last_arrow_line()
# 			# # Find the line with "->"
# 			# lines = sOutput.splitlines()
# 			# for i, line in enumerate(lines):
# 			# 	if "->" in line:
# 			# 		cursor = self.txtCommands.textCursor()
# 			# 		# Move to start
# 			# 		cursor.movePosition(QTextCursor.MoveOperation.Start)
# 			# 		# Move to the line
# 			# 		for _ in range(i):
# 			# 			cursor.movePosition(QTextCursor.MoveOperation.Down)
# 			# 		cursor.select(QTextCursor.SelectionType.LineUnderCursor)
# 			# 		self.txtCommands.setTextCursor(cursor)
# 			# 		self.txtCommands.centerCursor()
# 			# 		break
# 			# # if sOutput.contains("->"):
# 			# 	# self.txtCommands
# 		else:
# 			self.txtCommands.appendEscapedText(f"{res.GetError()}")
#
# 		if not res.Succeeded() or (res.Succeeded() and (sOutput.find("->") == -1 or not self.center_last_arrow_line())):
# 			if self.swtAutoscroll.isChecked():
# 				self.sb = self.txtCommands.verticalScrollBar()
# 				self.sb.setValue(self.sb.maximum())
#
# 	def center_last_arrow_line(self):
# 		bRet = False
# 		# Get all lines from the QTextEdit
# 		lines = self.txtCommands.toPlainText().splitlines()
#
# 		# Find the last line that starts with "->"
# 		for i in reversed(range(len(lines))):
# 			if lines[i].startswith("->"):
# 				target_line_index = i
# 				bRet = True
# 				break
# 		else:
# 			return bRet # No matching line found
#
# 		# Create a cursor and move to the start
# 		cursor = self.txtCommands.textCursor()
# 		cursor.movePosition(QTextCursor.MoveOperation.Start)
#
# 		# Move down to the target line
# 		for _ in range(target_line_index):
# 			cursor.movePosition(QTextCursor.MoveOperation.Down)
#
# 		# Set the cursor and center it
# 		# self.txtCmd.cursor(cursor)
# 		self.txtCommands.setTextCursor(cursor)
# 		return bRet
#
# 	def resetContent(self, resetCommandHistory=False, resetConsole=False):
# 			self.txtCmd.clearCommandText(resetCommandHistory)
# 			if resetConsole:
# 				self.txtCommands.setText("")
			
	