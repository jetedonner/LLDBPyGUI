#!/usr/bin/env python3

import os

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets
from config import *
#from ui.settingsDialog import *

# from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
import markdown
import sys

class CreditsDialog(QDialog):
	def __init__(self, title = "", prompt = ""):
		super().__init__()
		
		# print("ELLO")

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
		self.image_label.setPixmap(ConfigClass.pixBugGreen)
		
			# Add label to layout
		
		self.message = QLabel(prompt)
		self.layoutImg.addWidget(self.image_label)
		self.spacer = QSpacerItem(20, 40, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)  # Adjust spacer size as needed
		self.layoutImg.addItem(self.spacer)
		self.wdtImg = QWidget()
		self.wdtImg.setLayout(self.layoutImg)
		self.layoutMain.addWidget(self.wdtImg)
		self.layout.addWidget(self.message)
		self.wdtInner.setLayout(self.layout)
		self.layoutMain.addWidget(self.wdtInner)
		self.setLayout(self.layoutMain)

		self.resize(800, 600)

		self.viewReadme = QWebEngineView()
		self.viewReadme.setHtml(self.loadMD("README.md"))

		self.viewCredits = QWebEngineView()
		self.viewCredits.setHtml(self.loadMD("CREDITS.md"))

		self.viewLicense = QWebEngineView()
		self.viewLicense.setHtml(self.loadMD("LICENSE.md"))


		self.window = QWidget()
		self.window.setWindowTitle("About / Infos")
		self.layout2 = QVBoxLayout()

		self.tabs = QTabWidget()

		# First tab
		self.tab1 = QWidget()
		self.tab1_layout = QVBoxLayout()
		# self.tab1_layout.addWidget(QLabel("This is the first tab"))
		self.tab1_layout.addWidget(self.viewReadme)
		self.tab1.setLayout(self.tab1_layout)

		# Second tab
		self.tab2 = QWidget()
		self.tab2_layout = QVBoxLayout()
		self.tab2_layout.addWidget(self.viewCredits)
		self.tab2.setLayout(self.tab2_layout)

		self.tab3 = QWidget()
		self.tab3_layout = QVBoxLayout()
		self.tab3_layout.addWidget(self.viewLicense)
		self.tab3.setLayout(self.tab3_layout)

		self.tabs.addTab(self.tab1, "Readme")
		self.tabs.addTab(self.tab2, "Credits")
		self.tabs.addTab(self.tab3, "License")

		self.layout2.addWidget(self.tabs)
		self.window.setLayout(self.layout2)

		self.layout.addWidget(self.window)

		self.layout.addWidget(self.buttonBox)
	
	def loadMD(self, fileName):
		script_dir = os.path.dirname(os.path.abspath(__file__))
		md_path = os.path.join(script_dir + "/../../", fileName)

		# Read the Markdown file content
		with open(md_path, "r", encoding="utf-8") as f:
			md_text = f.read()

		return markdown.markdown(md_text, extensions=["fenced_code", "tables"])
		
# 	def chkOrderByName_clicked(self, checked):
# 		self.process_info.sort(key=lambda item: item[1 if checked else 0])
# 		self.cmbPID.clear()
# 		for pid, name in self.process_info:
# 			self.cmbPID.addItem(str(name + " (" + str(pid) + ")"), pid)
		
# 	def showEvent(self, event):
# 		super().showEvent(event)
# 		self.txtPID.setFocus()
# 		self.txtPID.selectAll()
		
# 	def loadPIDs(self):
# 		import psutil
		
# 		# Get list of all processes
# 		self.processes = list(psutil.process_iter())
		
# 		# Extract PID and name for each process
# 		self.process_info = []
# 		for process in self.processes:
# 			try:
# 				self.process_info.append((process.pid, process.name()))
# #				self.cmbPID.addItem(str(process.name() + " (" + str(process.pid) + ")"), process.pid)
# 			except (psutil.NoSuchProcess, psutil.AccessDenied):
# 				# Handle potential errors (process might disappear or insufficient permissions)
# 				pass
		
# 		# Sort process_info by process name in ascending order
# #		self.process_info.sort(key=lambda item: item[0])  # Sort by the second element (process name)
		
# 		# Populate the combobox with sorted items
# 		for pid, name in self.process_info:
# 			self.cmbPID.addItem(str(name + " (" + str(pid) + ")"), pid)
				
# 	def getProcessForPID(self):
# 		for process in self.processes:
# 			if str(process.pid) == self.txtPID.text():
# 				return process
# 		return None
	
# 	def getSelectedProcess(self):
# 		if self.txtPID.text() != "":
# 			return self.getProcessForPID()
# 		return self.processes[self.cmbPID.currentIndex()]