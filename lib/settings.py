#!/usr/bin/env python3

from enum import Enum

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from config import *

class SettingsValues(Enum):
	ConfirmRestartTarget = ("Confirm restart target", True, bool)
	ConfirmQuitApp = ("Confirm quit app", True, bool)
	DisassemblerShowQuickTooltip = ("Disassembler show QuickTooltip", True, bool)
	CmdHistory = ("Commands history", True, bool)
	MemViewShowSelectedStatubarMsg = ("Memory-Viewer on select show statusbar message", True, bool)
	VisualizeCurrentBP = ("Visualise current breakpoint", True, bool)
	UseNativeDialogs = ("Use native dialogs", True, bool)
	EventListenerTimestampFormat = ("Event-Listener Timestamp Format", "%Y-%m-%d %H:%M:%S", str)
	KeepWatchpointsEnabled = ("Keep watchpoints enabled", True, bool)
	HexGrouping = ("Hex-Value Grouping", 1, int)
	StatusBarMsgTimeout = ("StatusBar message timeout", 1500, int)
	
	# Developer Settings
	LoadTestTarget = ("Load test target", True, bool)
	LoadTestBPs = ("Load test breakpoints", True, bool)
	TestAttachPID = ("Test attach pid", 19840, int)
	StopAtEntry = ("Stop at entry", False, bool)
	BreakAtMainFunc = ("Break at main function", True, bool)
	MainFuncName = ("Main function name", "main", str)
	BreakpointAtMainFunc = ("Set breakpoint at main function", True, bool)
	ClearConsoleComplete = ("Clear console complete with 1 click", True, bool)
	PersistentCommandHistory = ("Save and reload command history when restarting app", True, bool)

	WindowSize = ("Window Size", QSize(1024, 800), QSize)
	
class SettingsHelper(QObject):

	settings = QSettings(ConfigClass.settingsFilename, QSettings.Format.IniFormat)
	
	def __init__(self):
		super().__init__()
		self.settings.setDefaultFormat(QSettings.Format.IniFormat)
		
	@staticmethod
	def getSettings():
		return QSettings(ConfigClass.companyName, ConfigClass.appName)
	
	@staticmethod
	def GetChecked(setting):
		return SettingsHelper().getChecked(setting)
	
	@staticmethod
	def GetValue(setting):
		return SettingsHelper().getValue(setting)
	
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
		self.settings.setValue(SettingsValues.HexGrouping.value[0], 1)
		self.settings.setValue(SettingsValues.StatusBarMsgTimeout.value[0], 1500)
		
		self.settings.setValue(SettingsValues.LoadTestTarget.value[0], True)
		self.settings.setValue(SettingsValues.LoadTestBPs.value[0], True)
		
		self.settings.setValue(SettingsValues.StopAtEntry.value[0], False)
		self.settings.setValue(SettingsValues.BreakAtMainFunc.value[0], True)
		self.settings.setValue(SettingsValues.MainFuncName.value[0], "main")
		self.settings.setValue(SettingsValues.BreakpointAtMainFunc.value[0], True)
		self.settings.setValue(SettingsValues.ClearConsoleComplete.value[0], True)
		self.settings.setValue(SettingsValues.PersistentCommandHistory.value[0], True)




	def beginWriteArray(self, prefix):
		self.settings.beginWriteArray(prefix)
		
	def beginReadArray(self, prefix):
		self.settings.beginReadArray(prefix)
	
	def setArrayValue(self, setting, value):
		self.settings.setValue(setting, value)
	
	def getArrayValue(self, setting):
		return self.settings.value(setting)
	
	def getArrayChecked(self, setting):
		return Qt.CheckState.Checked if self.settings.value(setting) == "true" else Qt.CheckState.Unchecked
		
	def endArray(self):
		self.settings.endArray()
		
	def setValue(self, setting, value):
		self.settings.setValue(setting.value[0], value)
		
	def setChecked(self, setting, checkableItem):
		self.settings.setValue(setting.value[0], checkableItem.checkState() == Qt.CheckState.Checked)
		
	def getChecked(self, setting):
		return Qt.CheckState.Checked if self.settings.value(setting.value[0], setting.value[1], setting.value[2]) else Qt.CheckState.Unchecked
	
	def getValue(self, setting):
		return self.settings.value(setting.value[0], setting.value[1], setting.value[2])