import os
from os.path import dirname, realpath

from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QDialog


class AboutDialog(QDialog):
	# settings = QSettings("DaVe_inc", f"{APP_NAME}")
	# setHelper = None
	#
	# def initDefaults(self):
	#
	#     # GENERAL
	#     self.settings.setValue(SettingsValues.ConfirmRestartTarget.value[0], True)
	#     self.settings.setValue(SettingsValues.ConfirmQuitApp.value[0], True)
	#     self.settings.setValue(SettingsValues.DisassemblerShowQuickTooltip.value[0], True)
	#     self.settings.setValue(SettingsValues.CmdHistory.value[0], True)
	#     self.settings.setValue(SettingsValues.MemViewShowSelectedStatubarMsg.value[0], True)
	#     self.settings.setValue(SettingsValues.VisualizeCurrentBP.value[0], True)
	#     self.settings.setValue(SettingsValues.UseNativeDialogs.value[0], True)
	#     self.settings.setValue(SettingsValues.EventListenerTimestampFormat.value[0], "%Y-%m-%d %H:%M:%S")
	#     self.settings.setValue(SettingsValues.KeepWatchpointsEnabled.value[0], True)
	#     self.settings.setValue(SettingsValues.HexGrouping.value[0], 1)
	#     self.settings.setValue(SettingsValues.StatusBarMsgTimeout.value[0], 1500)
	#     self.settings.setValue(SettingsValues.ExitLLDBOnAppExit.value[0], True)
	#     self.settings.setValue(SettingsValues.ShowDateInLogView.value[0], True)
	#     self.settings.setValue(SettingsValues.ShowDateInLogView.value[0], True)
	#     self.settings.setValue(SettingsValues.AutoBreakpointForScanf.value[0], True)
	#     self.settings.setValue(SettingsValues.AutoScrollDbgOutput.value[0], True)
	#     self.settings.setValue(SettingsValues.ShowLineNumInDisassembly.value[0], True)
	#     self.settings.setValue(SettingsValues.ASMMaxLines.value[0], 5)
	#     self.settings.setValue(SettingsValues.MaxCommandHistoryCharCount.value[0], 5000)
	#     self.settings.setValue(SettingsValues.OrderPIDsByName.value[0], True)
	#     self.settings.setValue(SettingsValues.AutomaticallyDisassembleModules.value[0], True)
	#     self.settings.setValue(SettingsValues.SaveWindowStateOnExit.value[0], True)
	#     self.settings.setValue(SettingsValues.ShowTipsAtStartup.value[0], True)
	#
	#     # DEVELOPER
	#     self.settings.setValue(SettingsValues.LoadTestTarget.value[0], True)
	#     self.settings.setValue(SettingsValues.LoadTestBPs.value[0], True)
	#     self.settings.setValue(SettingsValues.StopAtEntry.value[0], False)
	#     self.settings.setValue(SettingsValues.BreakAtMainFunc.value[0], True)
	#     self.settings.setValue(SettingsValues.MainFuncName.value[0], "main")
	#     self.settings.setValue(SettingsValues.BreakpointAtMainFunc.value[0], True)
	#     self.settings.setValue(SettingsValues.ClearConsoleComplete.value[0], True)
	#     self.settings.setValue(SettingsValues.PersistentCommandHistory.value[0], True)

	def __init__(self, settingsHelper=None):
		super().__init__()

		project_root = dirname(realpath(__file__))
		settingsDialogPath = os.path.join(project_root, '..', '..', 'resources', 'designer', 'aboutDialog.ui')

		uic.loadUi(settingsDialogPath, self)

		self.cmdClose = self.findChild(QtWidgets.QPushButton, "cmdClose")
		if self.cmdClose:
			self.cmdClose.clicked.connect(self.handle_close)

	def handle_close(self):
		self.close()
		# if settingsHelper != None:
		#     self.setHelper = settingsHelper
		# else:
		#     self.setHelper = SettingsHelper()
		#
		# self.tblGeneral = self.findChild(QtWidgets.QTableWidget, "tblGeneral")
		#
		# self.tblDeveloper = self.findChild(QtWidgets.QTableWidget, "tblDeveloper")
		#
		# self.cmdLoadDefaults.clicked.connect(self.click_loadDefaults)
		# self.cmdTest.clicked.connect(self.click_test)
		#
		# self.accepted.connect(self.click_saveSettings)
		#
		# self.tblGeneral.cellClicked.connect(self.on_table_cell_clicked)
		#
		# self.loadSettings()

	# def loadSettings(self):
	#
	#     # GENERAL
	#     for i in range(2):
	#         self.tblGeneral.item(0, i).setCheckState(self.setHelper.getChecked(SettingsValues.ConfirmRestartTarget))
	#         self.tblGeneral.item(1, i).setCheckState(self.setHelper.getChecked(SettingsValues.ConfirmQuitApp))
	#         self.tblGeneral.item(2, i).setCheckState(
	#             self.setHelper.getChecked(SettingsValues.DisassemblerShowQuickTooltip))
	#         self.tblGeneral.item(3, i).setCheckState(self.setHelper.getChecked(SettingsValues.CmdHistory))
	#         self.tblGeneral.item(4, i).setCheckState(
	#             self.setHelper.getChecked(SettingsValues.MemViewShowSelectedStatubarMsg))
	#         self.tblGeneral.item(5, i).setCheckState(self.setHelper.getChecked(SettingsValues.VisualizeCurrentBP))
	#         self.tblGeneral.item(6, i).setCheckState(self.setHelper.getChecked(SettingsValues.UseNativeDialogs))
	#         self.tblGeneral.item(9, i).setCheckState(self.setHelper.getChecked(SettingsValues.KeepWatchpointsEnabled))
	#         self.tblGeneral.item(12, i).setCheckState(self.setHelper.getChecked(SettingsValues.ExitLLDBOnAppExit))
	#         self.tblGeneral.item(13, i).setCheckState(self.setHelper.getChecked(SettingsValues.ShowDateInLogView))
	#         self.tblGeneral.item(15, i).setCheckState(self.setHelper.getChecked(SettingsValues.AutoBreakpointForScanf))
	#         self.tblGeneral.item(16, i).setCheckState(self.setHelper.getChecked(SettingsValues.AutoScrollDbgOutput))
	#         self.tblGeneral.item(17, i).setCheckState(
	#             self.setHelper.getChecked(SettingsValues.ShowLineNumInDisassembly))
	#         self.tblGeneral.item(20, i).setCheckState(self.setHelper.getChecked(SettingsValues.OrderPIDsByName))
	#         self.tblGeneral.item(21, i).setCheckState(
	#             self.setHelper.getChecked(SettingsValues.AutomaticallyDisassembleModules))
	#         self.tblGeneral.item(22, i).setCheckState(self.setHelper.getChecked(SettingsValues.SaveWindowStateOnExit))
	#         self.tblGeneral.item(23, i).setCheckState(self.setHelper.getChecked(SettingsValues.ShowTipsAtStartup))
	#
	#         if i == 0:
	#             item = QTableWidgetItem("Input handling (i.e. scanf)")
	#         else:
	#             item = QTableWidgetItem("")
	#
	#         item.setBackground(Qt.GlobalColor.lightGray)
	#         item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable & ~Qt.ItemFlag.ItemIsSelectable)
	#         item.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
	#         self.tblGeneral.setItem(14, i, item)
	#
	#     self.tblGeneral.item(11, 1).setText(str(self.setHelper.getValue(SettingsValues.StatusBarMsgTimeout)))
	#     self.tblGeneral.item(18, 1).setText(str(self.setHelper.getValue(SettingsValues.ASMMaxLines)))
	#     self.tblGeneral.item(19, 1).setText(str(self.setHelper.getValue(SettingsValues.MaxCommandHistoryCharCount)))
	#     # self.tblGeneral.item(20, 1).setText(str(self.setHelper.getValue(SettingsValues.AutomaticallyDisassembleModules)))
	#
	#     self.cmbGrouping = QComboBox()
	#     member_names = list(ByteGrouping.__members__.keys())
	#     self.cmbGrouping.addItems(member_names)
	#     self.cmbGrouping.setCurrentIndex(self.setHelper.getValue(SettingsValues.HexGrouping))
	#     self.tblGeneral.setCellWidget(10, 1, self.cmbGrouping)
	#
	#     item = ColorTableWidgetItem(QColor(0, 255, 0, 128))
	#
	#     self.tblGeneral.setItem(7, 1, item)
	#     self.tblGeneral.item(8, 1).setText(self.setHelper.getValue(SettingsValues.EventListenerTimestampFormat))
	#
	#     # DEVELOPER
	#     self.tblDeveloper.item(0, 0).setCheckState(self.setHelper.getChecked(SettingsValues.LoadTestTarget))
	#     self.tblDeveloper.item(1, 1).setCheckState(self.setHelper.getChecked(SettingsValues.LoadTestBPs))
	#     self.tblDeveloper.item(2, 1).setCheckState(self.setHelper.getChecked(SettingsValues.StopAtEntry))
	#     self.tblDeveloper.item(3, 1).setCheckState(self.setHelper.getChecked(SettingsValues.BreakAtMainFunc))
	#     self.tblDeveloper.item(3, 1).setText(self.setHelper.getValue(SettingsValues.MainFuncName))
	#     self.tblDeveloper.item(4, 1).setCheckState(self.setHelper.getChecked(SettingsValues.BreakpointAtMainFunc))
	#     self.tblDeveloper.item(5, 1).setCheckState(self.setHelper.getChecked(SettingsValues.ClearConsoleComplete))
	#     self.tblDeveloper.item(6, 1).setCheckState(self.setHelper.getChecked(SettingsValues.PersistentCommandHistory))
	#
	#     self.browse_widget = BrowseWidget()
	#
	#     # ...
	#     # Create the delegate with desired margin
	#     # delegate = MarginDelegate(margin_size=0)
	#
	#     #		# Set the delegate for the table or specific items
	#     #		table.setItemDelegate(delegate)  # Set for all items
	#     #		# OR
	#     #		some_item = QTableWidgetItem("Item Text")
	#     #		some_item.setData(Qt.ItemDataRole.UserRole, delegate)
	#     #		Set the table item widget (assuming you have a table created)
	#     self.table_item = QTableWidgetItem()
	#     # self.table_item.setData(Qt.ItemDataRole.UserRole, delegate)
	#     #		self.table_item.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)  # Adjust size policy
	#     self.tblDeveloper.setItem(0, 1, self.table_item)
	#     self.tblDeveloper.setCellWidget(0, 1, self.browse_widget)
	#
	# def click_test(self):
	#     print(
	#         f'{SettingsValues.CmdHistory.value[0]} => {self.settings.value(SettingsValues.CmdHistory.value[0], False)}')
	#     QColorDialog.getColor(QColor("red"))
	#
	# def on_table_cell_clicked(self, row, column):
	#     item = self.tblGeneral.item(row, column)
	#     if isinstance(item, ColorTableWidgetItem):
	#         color = QColorDialog.getColor(item.getColor())
	#         if color.isValid():
	#             item.setColor(color)
	#             self.tblGeneral.clear()
