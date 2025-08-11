#!/usr/bin/env python3

import psutil
import os

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets
from config import *
from lib.settings import SettingsValues
from ui.helper.dbgOutputHelper import settingHelper


#from ui.settingsDialog import *

class ProcessesDialog(QDialog):
	def __init__(self, title = "", prompt = ""):
		super().__init__()
		
		self.setWindowTitle(title)
		
		QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		
		self.buttonBox = QDialogButtonBox(QBtn)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)
		
		self.wdtInner = QWidget()
		self.layoutMain = QHBoxLayout()
		self.layout = QVBoxLayout()
		self.layoutImg = QVBoxLayout()
		self.image_label = QLabel()
		self.image_label.setPixmap(ConfigClass.pixGears)
		
			# Add label to layout
		
		self.message = QLabel(prompt)
		self.cmbPID = QComboBox()
		self.cmbPID.currentIndexChanged.connect(self.cmbPID_changed)
		self.layoutImg.addWidget(self.image_label)
		self.spacer = QSpacerItem(20, 40, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)  # Adjust spacer size as needed
		self.layoutImg.addItem(self.spacer)
		self.wdtImg = QWidget()
		self.wdtImg.setLayout(self.layoutImg)
		self.layoutMain.addWidget(self.wdtImg)
		self.layout.addWidget(self.message)
		self.layout.addWidget(self.cmbPID)
		
		self.wdtManual = QWidget()
		self.layoutManual = QHBoxLayout()
		self.txtPID = QLineEdit()
		# Create and set a validator for integers only
		self.validator = QIntValidator(self.txtPID)
		self.txtPID.setValidator(self.validator)
		self.txtPID.setPlaceholderText("Enter PID manually ...")
		self.txtPID.setText("19091")
		self.layoutManual.addWidget(QLabel("PID:"))
		self.layoutManual.addWidget(self.txtPID)
		self.wdtManual.setLayout(self.layoutManual)
		self.chkOrderByName = QCheckBox("Order processes by name")
		self.chkOrderByName.setChecked(settingHelper.GetValue(SettingsValues.OrderPIDsByName))
		self.chkOrderByName.clicked.connect(self.chkOrderByName_clicked)
		self.layout.addWidget(self.chkOrderByName)
		self.layout.addWidget(self.wdtManual)
		self.layout.addWidget(self.buttonBox)
		self.wdtInner.setLayout(self.layout)
		self.layoutMain.addWidget(self.wdtInner)
		self.setLayout(self.layoutMain)
		self.loadPIDs()
	
	def cmbPID_changed(self, index):
		self.txtPID.setText(str(self.process_info[index][0]))
		
	def chkOrderByName_clicked(self, checked):
		settingHelper.setValue(SettingsValues.OrderPIDsByName, checked)
		self.process_info.sort(key=lambda item: item[1 if checked else 0])
		self.cmbPID.clear()
		for pid, name in self.process_info:
			self.cmbPID.addItem(str(name + " (" + str(pid) + ")"), pid)
		
	def showEvent(self, event):
		super().showEvent(event)
		self.txtPID.setFocus()
		self.txtPID.selectAll()
		
	def loadPIDs(self):
		# import psutil
		
		# Get list of all processes
		self.processes = list(psutil.process_iter())
		
		# Extract PID and name for each process
		self.process_info = []
		for process in self.processes:
			try:
				self.process_info.append((process.pid, process.name()))
#				self.cmbPID.addItem(str(process.name() + " (" + str(process.pid) + ")"), process.pid)
			except (psutil.NoSuchProcess, psutil.AccessDenied):
				# Handle potential errors (process might disappear or insufficient permissions)
				pass
		
		# Sort process_info by process name in ascending order
#		self.process_info.sort(key=lambda item: item[0])  # Sort by the second element (process name)
		
		# Populate the combobox with sorted items
		# if settingHelper.GetValue(SettingsValues.OrderPIDsByName):
		self.process_info.sort(key=lambda item: item[1 if settingHelper.GetValue(SettingsValues.OrderPIDsByName) else 0])
		for pid, name in self.process_info:
			self.cmbPID.addItem(str(name + " (" + str(pid) + ")"), pid)
				
	def getProcessForPID(self):
		for process in self.processes:
			if str(process.pid) == self.txtPID.text():
				return process
		return None
	
	def getSelectedProcess(self):
		if self.txtPID.text() != "":
			return self.getProcessForPID()
		return self.processes[self.cmbPID.currentIndex()]