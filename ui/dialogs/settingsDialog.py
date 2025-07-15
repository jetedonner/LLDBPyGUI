#!/usr/bin/env python3

from lib.settings import *
from ui.dialogs.dialogHelper import *

class BrowseWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		
		self.path_label = QLabel()
		self.browse_button = QPushButton("Browse")
		self.browse_button.setContentsMargins(0, 0, 0, 0)
		self.browse_button.clicked.connect(self.handle_browse_click)
		
		layout = QHBoxLayout()
		layout.addWidget(self.path_label)
		layout.addWidget(self.browse_button)
		self.setLayout(layout)
		
		self.selected_path = None
		
	def handle_browse_click(self):
		filename = showOpenFileDialog()
		if filename:
			print(f"Setting: '{filename} as test target")
			pass
			
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
		self.settings.setValue(SettingsValues.HexGrouping.value[0], 1)
		self.settings.setValue(SettingsValues.StatusBarMsgTimeout.value[0], 1500)
		self.settings.setValue(SettingsValues.ExitLLDBOnAppExit.value[0], True)
		self.settings.setValue(SettingsValues.ShowDateInLogView.value[0], True)
		
		self.settings.setValue(SettingsValues.LoadTestTarget.value[0], True)
		self.settings.setValue(SettingsValues.LoadTestBPs.value[0], True)
		self.settings.setValue(SettingsValues.StopAtEntry.value[0], False)
		self.settings.setValue(SettingsValues.BreakAtMainFunc.value[0], True)
		self.settings.setValue(SettingsValues.MainFuncName.value[0], "main")
		self.settings.setValue(SettingsValues.BreakpointAtMainFunc.value[0], True)
		self.settings.setValue(SettingsValues.ClearConsoleComplete.value[0], True)
		self.settings.setValue(SettingsValues.PersistentCommandHistory.value[0], True)



	
	def __init__(self, settingsHelper = None):
		super().__init__()

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
			self.tblGeneral.item(12, i).setCheckState(self.setHelper.getChecked(SettingsValues.ExitLLDBOnAppExit))
			self.tblGeneral.item(13, i).setCheckState(self.setHelper.getChecked(SettingsValues.ShowDateInLogView))

		self.tblGeneral.item(11, 1).setText(str(self.setHelper.getValue(SettingsValues.StatusBarMsgTimeout)))

		self.cmbGrouping = QComboBox()
		member_names = list(ByteGrouping.__members__.keys())
		self.cmbGrouping.addItems(member_names)
		self.cmbGrouping.setCurrentIndex(self.setHelper.getValue(SettingsValues.HexGrouping))
		self.tblGeneral.setCellWidget(10, 1, self.cmbGrouping)
		
		
		item = ColorTableWidgetItem(QColor(0, 255, 0, 128))
		
		self.tblGeneral.setItem(7, 1, item)
		self.tblGeneral.item(8, 1).setText(self.setHelper.getValue(SettingsValues.EventListenerTimestampFormat))
		
		self.tblDeveloper.item(0, 0).setCheckState(self.setHelper.getChecked(SettingsValues.LoadTestTarget))
		self.tblDeveloper.item(1, 1).setCheckState(self.setHelper.getChecked(SettingsValues.LoadTestBPs))
		self.tblDeveloper.item(2, 1).setCheckState(self.setHelper.getChecked(SettingsValues.StopAtEntry))
		self.tblDeveloper.item(3, 1).setCheckState(self.setHelper.getChecked(SettingsValues.BreakAtMainFunc))
		self.tblDeveloper.item(3, 1).setText(self.setHelper.getValue(SettingsValues.MainFuncName))
		self.tblDeveloper.item(4, 1).setCheckState(self.setHelper.getChecked(SettingsValues.BreakpointAtMainFunc))
		self.tblDeveloper.item(5, 1).setCheckState(self.setHelper.getChecked(SettingsValues.ClearConsoleComplete))
		self.tblDeveloper.item(6, 1).setCheckState(self.setHelper.getChecked(SettingsValues.PersistentCommandHistory))

		self.browse_widget = BrowseWidget()
		
		# ...
		# Create the delegate with desired margin
		delegate = MarginDelegate(margin_size=0)
		
#		# Set the delegate for the table or specific items
#		table.setItemDelegate(delegate)  # Set for all items
#		# OR
#		some_item = QTableWidgetItem("Item Text")
#		some_item.setData(Qt.ItemDataRole.UserRole, delegate)
#		Set the table item widget (assuming you have a table created)
		self.table_item = QTableWidgetItem()
		self.table_item.setData(Qt.ItemDataRole.UserRole, delegate)
#		self.table_item.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)  # Adjust size policy
		self.tblDeveloper.setItem(0, 1, self.table_item)
		self.tblDeveloper.setCellWidget(0, 1, self.browse_widget)
		
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
		self.setHelper.setValue(SettingsValues.HexGrouping, self.cmbGrouping.currentIndex())
		self.setHelper.setValue(SettingsValues.StatusBarMsgTimeout, int(self.tblGeneral.item(11, 1).text()))
		self.setHelper.setChecked(SettingsValues.ExitLLDBOnAppExit, self.tblGeneral.item(12, colCheckBox))
		self.setHelper.setChecked(SettingsValues.ShowDateInLogView, self.tblGeneral.item(13, colCheckBox))

		self.setHelper.setChecked(SettingsValues.LoadTestTarget, self.tblDeveloper.item(0, 0))
		self.setHelper.setChecked(SettingsValues.LoadTestBPs, self.tblDeveloper.item(1, 1))
		self.setHelper.setChecked(SettingsValues.StopAtEntry, self.tblDeveloper.item(2, 1))
		self.setHelper.setChecked(SettingsValues.BreakAtMainFunc, self.tblDeveloper.item(3, 1))
		self.setHelper.setValue(SettingsValues.MainFuncName, self.tblDeveloper.item(3, 1).text())
		self.setHelper.setChecked(SettingsValues.BreakpointAtMainFunc, self.tblDeveloper.item(4, 1))
		self.setHelper.setChecked(SettingsValues.ClearConsoleComplete, self.tblDeveloper.item(5, 1))
		self.setHelper.setChecked(SettingsValues.PersistentCommandHistory, self.tblDeveloper.item(6, 1))


		
class MarginDelegate(QStyledItemDelegate):
	def __init__(self, margin_size=5, parent=None):
		super().__init__(parent)
		self.margin_size = margin_size
		
	def paint(self, painter, option, index):
		# Access and modify the QStyleOptionTableItem for custom drawing
		modified_option = QStyleOptionTableItem(*option)
		
		# Adjust content rectangle based on desired margins
		modified_option.rect.adjust(self.margin_size, self.margin_size, -self.margin_size, -self.margin_size)
		
		# Call the base class paint method with the modified option
		super().paint(painter, modified_option, index)
		
	def sizeHint(self, option, index):
		# Adjust size hint based on margins if necessary
		size = super().sizeHint(option, index)
		size.setWidth(size.width() + 2 * self.margin_size)
		size.setHeight(size.height() + 2 * self.margin_size)
		return size