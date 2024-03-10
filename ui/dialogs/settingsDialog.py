#!/usr/bin/env python3

import os
import sys

from enum import Enum
#import re	
	
from os.path import abspath
from os.path import dirname, realpath
from os import getcwd, path

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from config import *
from lib.settings import *
	
class BrowseWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		
		self.path_label = QLabel()
		self.browse_button = QPushButton("Browse")
		self.browse_button.clicked.connect(self.handle_browse_click)
		
		layout = QHBoxLayout()
		layout.addWidget(self.path_label)
		layout.addWidget(self.browse_button)
		self.setLayout(layout)
		
		self.selected_path = None  # Store the selected path
		
	def handle_browse_click(self):
#		item = self# self.tblGeneral.item(row, column)
#		if isinstance(item, ColorTableWidgetItem):
		color = QColorDialog.getColor(self.parent().getColor())
		if color.isValid():
			self.parent().setColor(color)
				
#		# Get a filename using QFileDialog
#		filename, _ = QFileDialog.getOpenFileName(self, "Select File")
#		if filename:
#			self.path_label.setText(filename)
#			self.selected_path = filename  # Update stored path
#			
#			# Emit a custom signal for path selection (optional)
#			# self.pathSelected.emit(filename)
			
class ColorTableWidgetItem(QTableWidgetItem):
	def __init__(self, color=None, parent=None):
		super().__init__(parent)
		self._color = color
		self.setBackground(self._color)
		
	def getColor(self):
		return self._color
	
	def setColor(self, color):
		self._color = QColor(color)
		self.setBackground(self._color)
		
		
class SettingsDialog(QDialog):
	
	settings = QSettings("DaVe_inc", "LLDBPyGUI")
	setHelper = None
	
	def initDefaults(self):
		self.settings.setValue(SettingsValues.ConfirmRestartTarget.value[0], True)
		self.settings.setValue(SettingsValues.ConfirmQuitApp.value[0], True)
		self.settings.setValue(SettingsValues.DisassemblerShowQuickTooltip.value[0], True)
		self.settings.setValue(SettingsValues.CmdHistory.value[0], True)
		self.settings.setValue(SettingsValues.MemViewShowSelectedStatubarMsg.value[0], True)
		self.settings.setValue(SettingsValues.VisualizeCurrentBP.value[0], True)
		self.settings.setValue(SettingsValues.UseNativeDialogs.value[0], True)
		self.settings.setValue(SettingsValues.EventListenerTimestampFormat.value[0], "%Y-%m-%d %H:%M:%S")
		self.settings.setValue(SettingsValues.KeepWatchpointsEnabled.value[0], True)
		
		self.settings.setValue(SettingsValues.LoadTestTarget.value[0], True)
		self.settings.setValue(SettingsValues.LoadTestBPs.value[0], True)
		self.settings.setValue(SettingsValues.StopAtEntry.value[0], False)
		self.settings.setValue(SettingsValues.BreakAtMainFunc.value[0], True)
		self.settings.setValue(SettingsValues.MainFuncName.value[0], "main")
	
	def __init__(self, settingsHelper = None):
		super().__init__()
		# loading the ui file with uic module
		project_root = dirname(realpath(__file__))
		settingsDialogPath = os.path.join(project_root, '..', '..', 'resources', 'designer', 'settingsDialog.ui')
		
		uic.loadUi(settingsDialogPath, self)
		
		if settingsHelper != None:
			self.setHelper = settingsHelper
		else:
			self.setHelper = SettingsHelper()
			
		self.tblGeneral = self.findChild(QtWidgets.QTableWidget, "tblGeneral")
		
		self.tblDeveloper = self.findChild(QtWidgets.QTableWidget, "tblDeveloper")
		
		self.cmdLoadDefaults.clicked.connect(self.click_loadDefaults)
		self.cmdTest.clicked.connect(self.click_test)
		
#		log(f"Loading settings from file: '{self.settings.fileName()}'")
		self.accepted.connect(self.click_saveSettings)
		
		self.tblGeneral.cellClicked.connect(self.on_table_cell_clicked)
		
		self.loadSettings()
		
	def loadSettings(self):
		for i in range(2):
			self.tblGeneral.item(0, i).setCheckState(self.setHelper.getChecked(SettingsValues.ConfirmRestartTarget))
			self.tblGeneral.item(1, i).setCheckState(self.setHelper.getChecked(SettingsValues.ConfirmQuitApp))
			self.tblGeneral.item(2, i).setCheckState(self.setHelper.getChecked(SettingsValues.DisassemblerShowQuickTooltip))
			self.tblGeneral.item(3, i).setCheckState(self.setHelper.getChecked(SettingsValues.CmdHistory))
			self.tblGeneral.item(4, i).setCheckState(self.setHelper.getChecked(SettingsValues.MemViewShowSelectedStatubarMsg))
			self.tblGeneral.item(5, i).setCheckState(self.setHelper.getChecked(SettingsValues.VisualizeCurrentBP))
			self.tblGeneral.item(6, i).setCheckState(self.setHelper.getChecked(SettingsValues.UseNativeDialogs))
			self.tblGeneral.item(9, i).setCheckState(self.setHelper.getChecked(SettingsValues.KeepWatchpointsEnabled))
		
		
		
		item = ColorTableWidgetItem(QColor(0, 255, 0, 128))
#		browse_widget = BrowseWidget()
		
		# Set the table item widget (assuming you have a table created)
#		table_item = QTableWidgetItem()
#		table_item.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)  # Adjust size policy
#		table_widget.setItem(row, column, browse_widget)
		
		self.tblGeneral.setItem(7, 1, item)
#		self.tblGeneral.setCellWidget(7, 1, item)
		self.tblGeneral.item(8, 1).setText(self.setHelper.getValue(SettingsValues.EventListenerTimestampFormat))
		
		self.tblDeveloper.item(0, 1).setCheckState(self.setHelper.getChecked(SettingsValues.LoadTestTarget))
		self.tblDeveloper.item(1, 1).setCheckState(self.setHelper.getChecked(SettingsValues.LoadTestBPs))
		self.tblDeveloper.item(2, 1).setCheckState(self.setHelper.getChecked(SettingsValues.StopAtEntry))
		self.tblDeveloper.item(3, 1).setCheckState(self.setHelper.getChecked(SettingsValues.BreakAtMainFunc))
		self.tblDeveloper.item(3, 1).setText(self.setHelper.getValue(SettingsValues.MainFuncName))
		
		
#		self.settings.setValue(SettingsValues.BreakAtMainFunc.value[0], True)
#		self.settings.setValue(SettingsValues.MainFuncName.value[0], "main")
		
	def click_test(self):
		print(f'{SettingsValues.CmdHistory.value[0]} => {self.settings.value(SettingsValues.CmdHistory.value[0], False)}')
		QColorDialog.getColor(QColor("red"))
	
	def on_table_cell_clicked(self, row, column):
		item = self.tblGeneral.item(row, column)
		if isinstance(item, ColorTableWidgetItem):
			color = QColorDialog.getColor(item.getColor())
			if color.isValid():
				item.setColor(color)
				self.tblGeneral.clear()
				
	def click_loadDefaults(self):
		self.initDefaults()
		
	def click_saveSettings(self):
		colCheckBox = 0
		self.setHelper.setChecked(SettingsValues.ConfirmRestartTarget, self.tblGeneral.item(0, colCheckBox))
		self.setHelper.setChecked(SettingsValues.ConfirmQuitApp, self.tblGeneral.item(1, colCheckBox))
		self.setHelper.setChecked(SettingsValues.DisassemblerShowQuickTooltip, self.tblGeneral.item(2, colCheckBox))
		self.setHelper.setChecked(SettingsValues.CmdHistory, self.tblGeneral.item(3, colCheckBox))
		self.setHelper.setChecked(SettingsValues.MemViewShowSelectedStatubarMsg, self.tblGeneral.item(4, colCheckBox))
		self.setHelper.setChecked(SettingsValues.VisualizeCurrentBP, self.tblGeneral.item(5, colCheckBox))
		self.setHelper.setChecked(SettingsValues.UseNativeDialogs, self.tblGeneral.item(6, colCheckBox))
		self.setHelper.setValue(SettingsValues.EventListenerTimestampFormat, self.tblGeneral.item(8, 1).text())
		self.setHelper.setChecked(SettingsValues.KeepWatchpointsEnabled, self.tblGeneral.item(9, colCheckBox))
		
		
		self.setHelper.setChecked(SettingsValues.LoadTestTarget, self.tblDeveloper.item(0, 1))
		self.setHelper.setChecked(SettingsValues.LoadTestBPs, self.tblDeveloper.item(1, 1))
		self.setHelper.setChecked(SettingsValues.StopAtEntry, self.tblDeveloper.item(2, 1))
		self.setHelper.setChecked(SettingsValues.BreakAtMainFunc, self.tblDeveloper.item(3, 1))
		self.setHelper.setValue(SettingsValues.MainFuncName, self.tblDeveloper.item(3, 1).text())
		