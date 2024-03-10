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

class CommandsWidget(QWidget):
	
#	actionShowMemory = None
	workerManager = None
	def __init__(self, workerManager):
		super().__init__()
		
		self.workerManager = workerManager
		
		self.setHelper = SettingsHelper()
		
		self.wdgCmd = QWidget()
#		self.wdgCommands = QWidget()
		self.layCmdParent = QVBoxLayout()
		self.layCmd = QHBoxLayout()
		self.wdgCmd.setLayout(self.layCmd)
		self.setLayout(self.layCmdParent)
		
		self.lblCmd = QLabel("Command: ")
		self.lblCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		
		self.txtCmd = QHistoryLineEdit(self.setHelper.getValue(SettingsValues.CmdHistory))
		self.txtCmd.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		self.txtCmd.setText(ConfigClass.initialCommand)
		self.txtCmd.returnPressed.connect(self.execCommand_clicked)
		self.txtCmd.availCompletitions.connect(self.handle_availCompletitions)
		
		self.swtAutoscroll = QSwitch("Autoscroll")
		self.swtAutoscroll.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.swtAutoscroll.setChecked(True)
		
		self.cmdExecuteCmd = QPushButton("Execute")
		self.cmdExecuteCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.cmdExecuteCmd.clicked.connect(self.execCommand_clicked)
		
		self.cmdClear = QPushButton()
		self.cmdClear.setIcon(ConfigClass.iconTrash)
		self.cmdClear.setToolTip("Clear the Commands log")
		self.cmdClear.setIconSize(QSize(16, 16))
		self.cmdClear.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.cmdClear.clicked.connect(self.clear_clicked)
		
		self.layCmd.addWidget(self.lblCmd)
		self.layCmd.addWidget(self.txtCmd)
		self.layCmd.addWidget(self.cmdExecuteCmd)
		self.layCmd.addWidget(self.swtAutoscroll)
		self.layCmd.addWidget(self.cmdClear)
		self.wdgCmd.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)		
		
		self.txtCommands = QConsoleTextEdit()
		self.txtCommands.setReadOnly(True)
		self.txtCommands.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		self.txtCommands.setFont(ConfigClass.font)
		self.txtCommands.setText("Here you can run LLDB commands. Type 'help' for a list of available commands.\n")
		self.layCmdParent.addWidget(self.txtCommands)
		self.layCmdParent.addWidget(self.wdgCmd)
		
	def handle_availCompletitions(self, compl):
		
		self.txtCommands.append("Available Completions:")
#		self.win.scroll(1)
		for m in islice(compl, 1, None):
			self.txtCommands.append(m)
		pass
		
	def clear_clicked(self):
		self.txtCommands.setText("")
#		command_interpreter = self.debugger.GetCommandInterpreter()
		
#		self.data = self.txtCmd.text()
#		matches = lldb.SBStringList()
#		commandinterpreter = self.workerManager.driver.debugger.GetCommandInterpreter()
#		commandinterpreter.HandleCompletion(
#			self.data, len(self.data), 0, -1, matches)
#		if len(matches) > 0:
#			self.txtCmd.insert(matches.GetStringAtIndex(0))
#		for match in matches:
#			print(match)
		
	def execCommand_clicked(self):
		if self.setHelper.getValue(SettingsValues.CmdHistory):
			self.txtCmd.addCommandToHistory()
			
		self.txtCommands.append(f"({PROMPT_TEXT}) {self.txtCmd.text().strip()}")
		if self.txtCmd.text().strip().lower() in ["clear", "clr"]:
			self.clear_clicked()
		else:
			self.workerManager.start_execCommandWorker(self.txtCmd.text(), self.handle_commandFinished)
		
	def handle_commandFinished(self, res):
		if res.Succeeded():
			self.txtCommands.appendEscapedText(res.GetOutput())
		else:
			self.txtCommands.appendEscapedText(f"{res.GetError()}")
			
		if self.swtAutoscroll.isChecked():
			self.sb = self.txtCommands.verticalScrollBar()
			self.sb.setValue(self.sb.maximum())
			
	