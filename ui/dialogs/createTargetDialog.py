#!/usr/bin/env python3

import os

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets
from config import *
from ui.customQt.QSwitch import QSwitch, SwitchSize, SwitchLabelPos
from ui.dialogs.dialogHelper import showOpenFileDialog


#from ui.settingsDialog import *

class CreateTargetDialog(QDialog):

	loadSourceCode = True

	def __init__(self, title = "Create Target - Options", prompt = "Enter options for creating a new target"):
		super().__init__()

		self.loadSourceCode = True
		
		self.setWindowTitle(title)
		self.setMinimumWidth(720)
		QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

		self.buttonBox = QDialogButtonBox(QBtn)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)

		self.message = QLabel(prompt)

		self.wdtInner = QWidget()
		self.layoutMain = QHBoxLayout()
		self.layout = QVBoxLayout()

		# IMAGE
		self.layoutImg = QVBoxLayout()
		self.image_label = QLabel()
		self.image_label.setPixmap(ConfigClass.pixBugLg)
		self.layoutImg.addWidget(self.image_label)
		self.spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)  # Adjust spacer size as needed
		self.layoutImg.addItem(self.spacer)
		self.wdtImg = QWidget()
		self.wdtImg.setLayout(self.layoutImg)
		self.layoutMain.addWidget(self.wdtImg)

		self.layout.addWidget(self.message)

		# TARGET
		self.wdtTarget = QWidget()
		self.wdtTarget.setContentsMargins(0, 0, 0, 0)
		self.layoutTarget = QHBoxLayout()
		self.layoutTarget.setContentsMargins(0, 0, 0, 0)
		self.txtTarget = QLineEdit()
		self.txtTarget.setPlaceholderText("Select a target ...")
		self.layoutTarget.addWidget(QLabel("Target:"))
		self.layoutTarget.addWidget(self.txtTarget)
		self.cmdOpenTarget = QPushButton("...")
		self.cmdOpenTarget.clicked.connect(self.openTarget_clicked)
		self.layoutTarget.addWidget(self.cmdOpenTarget)
		self.wdtTarget.setLayout(self.layoutTarget)
		self.layout.addWidget(self.wdtTarget)

		# LOADER
		self.wdtLoader = QWidget()
		self.wdtLoader.setContentsMargins(0, 0, 0, 0)
		self.layoutLoader = QHBoxLayout()
		self.layoutLoader.setContentsMargins(0, 0, 0, 0)
		self.cmbLoader = QComboBox()
		self.cmbLoader.addItems(["Mach-O Intel 64bits"])
		self.cmbLoader.setEditable(True)  # 🔑 This enables free text input
		self.cmbLoader.setPlaceholderText("Select an Loader ...")
		self.layoutLoader.addWidget(QLabel("Loader:"))
		self.cmbLoader.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
		self.layoutLoader.addWidget(self.cmbLoader)
		self.wdtLoader.setLayout(self.layoutLoader)
		self.layout.addWidget(self.wdtLoader)

		# ARCHITECTURE
		self.wdtArch = QWidget()
		self.wdtArch.setContentsMargins(0, 0, 0, 0)
		self.layoutArch = QHBoxLayout()
		self.layoutArch.setContentsMargins(0, 0, 0, 0)
		self.cmbArch = QComboBox()
		self.cmbArch.addItems(["x86_64-apple-macosx15.1.1", "ARM64", "x86_64", "AARCH"])
		self.cmbArch.setEditable(True)  # 🔑 This enables free text input
		self.cmbArch.setPlaceholderText("Select an architecture ...")
		self.layoutArch.addWidget(QLabel("Arch:"))
		self.cmbArch.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
		self.layoutArch.addWidget(self.cmbArch)
		self.wdtArch.setLayout(self.layoutArch)
		self.layout.addWidget(self.wdtArch)

		self.wdtManual = QWidget()
		self.wdtManual.setContentsMargins(0, 0, 0, 0)
		self.layoutManual = QHBoxLayout()
		self.layoutManual.setContentsMargins(0, 0, 0, 0)
		self.txtArgs = QLineEdit()
		# Create and set a validator for integers only
		# self.validator = QValidator(self.txtArgs)
		# self.validator.fil
		# self.txtArgs.setValidator(self.validator)
		self.txtArgs.setPlaceholderText("Enter arguments for target ...")
		# self.txtArgs.setText("19091")
		self.layoutManual.addWidget(QLabel("Args:"))
		self.layoutManual.addWidget(self.txtArgs)
		self.wdtManual.setLayout(self.layoutManual)
		# self.chkOrderByName = QCheckBox("Order processes by name")
		# self.chkOrderByName.clicked.connect(self.chkOrderByName_clicked)
		# self.layout.addWidget(self.chkOrderByName)
		self.layout.addWidget(self.wdtManual)

		self.swtLoadSourceCode = QSwitch("Load sourcecode", SwitchSize.Small, SwitchLabelPos.Trailing)
		self.swtLoadSourceCode.checked.connect(self.swtLoadSourceCode_checked)
		self.swtLoadSourceCode.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.swtLoadSourceCode.setChecked(True)
		self.swtLoadSourceCode.setContentsMargins(0, 0, 0, 0)
		# self.laySearchTop.addWidget(self.swtCaseSensitive)
		self.layout.addWidget(self.swtLoadSourceCode)

		self.layout.addWidget(self.buttonBox)
		self.wdtInner.setLayout(self.layout)
		self.layoutMain.addWidget(self.wdtInner)
		self.setLayout(self.layoutMain)
		# self.loadPIDs()

	def swtLoadSourceCode_checked(self, checked):
		self.loadSourceCode = checked

	def openTarget_clicked(self):
		filename = showOpenFileDialog()
		if filename != None and filename != "":
			self.txtTarget.setText(filename)
		pass

	# def cmbPID_changed(self, index):
	# 	self.txtArgs.setText(str(self.process_info[index][0]))
	#
	# def chkOrderByName_clicked(self, checked):
	# 	self.process_info.sort(key=lambda item: item[1 if checked else 0])
	# 	self.cmbPID.clear()
	# 	for pid, name in self.process_info:
	# 		self.cmbPID.addItem(str(name + " (" + str(pid) + ")"), pid)
		
	# def showEvent(self, event):
	# 	super().showEvent(event)
	# 	self.txtArgs.setFocus()
	# 	self.txtArgs.selectAll()
		
# 	def loadPIDs(self):
# 		import psutil
#
# 		# Get list of all processes
# 		self.processes = list(psutil.process_iter())
#
# 		# Extract PID and name for each process
# 		self.process_info = []
# 		for process in self.processes:
# 			try:
# 				self.process_info.append((process.pid, process.name()))
# #				self.cmbPID.addItem(str(process.name() + " (" + str(process.pid) + ")"), process.pid)
# 			except (psutil.NoSuchProcess, psutil.AccessDenied):
# 				# Handle potential errors (process might disappear or insufficient permissions)
# 				pass
#
# 		# Sort process_info by process name in ascending order
# #		self.process_info.sort(key=lambda item: item[0])  # Sort by the second element (process name)
#
# 		# Populate the combobox with sorted items
# 		for pid, name in self.process_info:
# 			self.cmbPID.addItem(str(name + " (" + str(pid) + ")"), pid)
#
# 	def getProcessForPID(self):
# 		for process in self.processes:
# 			if str(process.pid) == self.txtArgs.text():
# 				return process
# 		return None
#
# 	def getSelectedProcess(self):
# 		if self.txtArgs.text() != "":
# 			return self.getProcessForPID()
# 		return self.processes[self.cmbPID.currentIndex()]