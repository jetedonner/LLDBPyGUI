from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QPoint, QModelIndex, QSize, QRect
from PyQt6.QtGui import QColor, QIcon, QPalette, QBrush, QPixmap, QKeyEvent, QPainter
from PyQt6.QtWidgets import QMenu, QScrollBar, QTableWidget, QWidget, QHBoxLayout, QSplitter, QTableWidgetItem, \
	QStyledItemDelegate, QStyle, QSizePolicy, QDockWidget, QLabel, QVBoxLayout, QApplication

from config import ConfigClass
from constants import JMP_MNEMONICS
from helper.arm64MnemonicReference import Arm64MnemonicReference
from helper.debugHelper import logDbgC, getAddrFromOperands, get_main_window, getAddrDelta, printStacktrace, debug_stack
from lib.fileInfos import is_hex_string
from lib.locationStack import LocationStack
from lib.settings import SettingsHelper, SettingsValues
from lib.thirdParty.breakpointManager import BreakpointManager
from ui.base.baseTableWidget import BaseTableWidget
from ui.customQt.QControlFlowWidget import QControlFlowWidget
from ui.debugger.functionListView import FunctionsListViewWidget
from ui.debugger.quickToolTip import QuickToolTip
from ui.dialogs.dialogHelper import WebDialog

COL_LINE = -1
COL_PC = 0
COL_BP = 1
COL_ADDRESS = 2
COL_MNEMONIC = 3
COL_OPERANDS = 4
COL_HEX = 5
COL_DATA = 6
COL_COMMENT = 7


class DisassemblyImageTableWidgetItem(QTableWidgetItem):
	iconStd = None
	iconBPEnabled = None
	iconBPDisabled = None

	isBPOn = False
	isBPEnabled = False

	def __init__(self):
		self.iconStd = QIcon()
		super().__init__(self.iconStd, "", QTableWidgetItem.ItemType.Type)
		self.iconBPEnabled = ConfigClass.iconBPEnabled
		self.iconBPDisabled = ConfigClass.iconBPDisabled
		self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsEditable)

	def setBPOn(self, on=True):
		if on:
			self.isBPEnabled = True
			self.setIcon(self.iconBPEnabled)
		else:
			self.isBPEnabled = False
			self.setIcon(self.iconStd)

	def enableBP(self, enabled):
		#		self.isBPOn = not self.isBPOn
		if enabled:
			self.isBPEnabled = True
			self.setIcon(self.iconBPEnabled)
		else:
			self.isBPEnabled = False
			self.setIcon(self.iconBPDisabled)


class CustomStyledItemDelegate(QStyledItemDelegate):

	def initStyleOption(self, option, index):
		super(CustomStyledItemDelegate, self).initStyleOption(option, index)

		color = QColor("#FFFFFF")

		if index.column() == COL_PC or index.column() == COL_LINE:
			color = QColor("#000000")

			cg = (
				QPalette.ColorGroup.Normal
				if option.state & QStyle.StateFlag.State_Enabled
				else QPalette.ColorGroup.Disabled
			)
			if option.text == "I" or option.text == ">I":
				option.palette.setColor(cg, QPalette.ColorRole.HighlightedText, color)
				option.palette.setColor(cg, QPalette.ColorRole.Text, color)
				QBrush(color).setStyle()
				option.palette.setBrush(QPalette.ColorRole.Text, QBrush(color))

	# if option.state & QtWidgets.QStyle.StateFlag.State_Selected:
	# 	option.palette.setColor(cg, QtGui.QPalette.ColorRole.HighlightedText, color)

	# option.palette.setBrush(QtGui.QPalette.ColorRole.Text, color)
	# def initStyleOption(self, option, index):
	# 	super().initStyleOption(option, index)
	# 	print(f"CustomDelegate initStyleOption()....")
	# 	fg = index.data(Qt.ItemDataRole.ForegroundRole)
	# 	if isinstance(fg, QBrush):
	# 		fg.setColor(QColor("black"))
	# 		option.palette.setBrush(QPalette.ColorRole.Text, fg)
	# 	elif isinstance(fg, QColor) and fg.isValid():
	# 		fg.setNamedColor("black") #= QColor("black")
	# 		option.palette.setColor(QPalette.ColorRole.Text, fg)

	def paint(self, painter, option, index):
		if index.column() == COL_PC or index.column() == COL_LINE:
			color = QColor("#000000")
			painter._color = color

		super().paint(painter, option, index)

		if option.state & QStyle.StateFlag.State_Selected:  # Qt.State_Selected:
			brush = QBrush(Qt.GlobalColor.darkYellow)
			# Set custom background color for selected rows
			option.backgroundBrush = brush  # Adjust color as desired
		else:
			# Create a temporary QPixmap and fill it with the brush color
			pixmap = QPixmap(option.rect.size())  # Adjust dimensions as needed
			pixmap.fill(Qt.GlobalColor.transparent)
			image = pixmap.toImage()
			painter.drawImage(option.rect, image)  # option.background())


class DisassemblyWidget(QWidget):
	tblDisassembly = None
	disassemblies = {}
	lastModuleKey = None  # Add this to your class init or setup
	lastSymbolKey = None
	lastSubSymbolKey = None

	def __init__(self, driver, bpHelper, parent):
		super().__init__()

		self.driver = driver
		self.bpHelper = bpHelper
		self.parent = parent

		self.instCnt = 0

		self.setContentsMargins(0, 0, 0, 0)
		self.tblDisassembly = DisassemblyTableWidget(driver, bpHelper, parent)
		self.tblDisassembly.setContentsMargins(0, 0, 0, 0)
		self.setLayout(QHBoxLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.splitterDisassmbly = QSplitter()
		self.splitterDisassmbly.setContentsMargins(0, 0, 0, 0)
		self.splitterDisassmbly.setOrientation(Qt.Orientation.Horizontal)

		self.wdtControlFlow = QControlFlowWidget(self, self.driver)
		self.wdtControlFlow.setContentsMargins(0, 0, 0, 0)  # self.wdtControlFlow.setContentsMargins(0, 30, 0, 0)
		self.wdtControlFlow.setMaximumWidth(83)
		self.wdtControlFlow.setFixedWidth(83)

		self.wdtFunctionList = FunctionsListViewWidget(self.driver)
		# self.splitterDbgFunc = QSplitter()
		# self.splitterDbgFunc.setOrientation()
		# self.splitterDbg.addWidget(self.wdtDisassembly)
		# self.splitterDbg.addWidget(self.wdtFunctionList)
		self.wdtFunctionList.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.splitterDisassmbly.addWidget(self.wdtControlFlow)
		self.splitterDisassmbly.addWidget(self.tblDisassembly)
		get_main_window().dock_right = QDockWidget("Symbols / Strings / Actions", get_main_window())
		get_main_window().dock_right.setObjectName("Symbols / Strings / Actions")
		get_main_window().dock_right.setWidget(self.wdtFunctionList)
		get_main_window().addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, get_main_window().dock_right)
		# get_main_window().dock_right.to
		# va = QDockWidget()
		# va.
		# self.mainWin = get_main_window()
		# self.mainWin.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.mainWin.dock_right)
		# self.splitterDisassmbly.addWidget(self.wdtFunctionList)
		self.splitterDisassmbly.setStretchFactor(0, 15)
		self.splitterDisassmbly.setStretchFactor(1, 60)
		self.splitterDisassmbly.setStretchFactor(2, 25)

		self.layout().addWidget(self.splitterDisassmbly)
		# sizesOfDis = self.splitterDisassmbly.sizes()
		# # width = self.width()
		# midSize = self.width() - 256 - sizesOfDis[0] - sizesOfDis[1]
		# self.splitterDisassmbly.setSizes([sizesOfDis[0], midSize, 256])
		# self.splitterDisassmbly.setRubberBand(1)

	def resetContent(self):
		self.instCnt = 0
		self.lastModuleKey = None  # Add this to your class init or setup
		self.lastSymbolKey = None
		self.lastSubSymbolKey = None

		self.tblDisassembly.resetContent()
		logDbgC(f"self.wdtControlFlow.resetContent() ...")
		self.wdtControlFlow.resetContent(True)
		self.wdtFunctionList.resetContent()

	def handle_loadSymbol(self, symbol, loadDisassembly=True):
		# print(f"handle_loadSymbol => {symbol} ...")
		isBold = False
		if symbol == "__text" or symbol == "__stubs" or symbol == "__objc_stubs" or symbol == "__cstring":
			isBold = True
			if loadDisassembly:
				self.disassemblies[self.lastModuleKey][str(symbol)] = {}
			self.lastSymbolKey = str(symbol)  # Track the current symbol
		else:
			# print(self.disassemblies)
			# self.disassemblies[len(self.disassemblies) - 1] += str(symbol)
			# print(self.disassemblies)
			if self.lastSymbolKey:
				if loadDisassembly:
					self.disassemblies[self.lastModuleKey][self.lastSymbolKey].update(
						{str(symbol): {}})  # += {str(symbol): {}}
				self.lastSubSymbolKey = str(symbol)
				# self.disassemblies[self.lastSymbolKey].append(str(symbol))
			else:
				print("Warning: No previous symbol key to append to.")

		# print(self.disassemblies)
		self.appendAsmSymbol(0x0, str(symbol), isBold)

	# QApplication.processEvents()

	def handle_workerFinished(self, connections=[], moduleName="<no name>", instructions={}, newPC=0x0,
							  loadDisassembly=True):
		# print(f"len(connections): {len(connections)} (1) ...")
		if loadDisassembly and connections != [] and len(
				connections) > 0:  # and len(self.disassemblies[moduleName]["connections"]) <= 0:
			self.disassemblies[moduleName]["connections"] = connections
			# logDbgC(f"Setting connections (1) ...")

		# self.modulesAndInstructions = instructions
		if self.disassemblies[moduleName]["connections"] != [] and (
				len(self.disassemblies[moduleName]["connections"]) > 0):
			# self.wdtDisassembly.wdtControlFlow.draw_invisibleHeight()
			self.wdtControlFlow.loadConnectionsFromWorker(self.disassemblies[moduleName]["connections"])

	def handle_loadModule(self, module):
		self.lastModuleKey = module
		self.disassemblies[module] = {}
		print(self.disassemblies)

	def handle_loadString(self, addr, idx, string, loadDisassembly=True):
		if loadDisassembly:
			if self.lastSymbolKey:
				self.disassemblies[self.lastModuleKey][self.lastSymbolKey].update({idx: [addr, string]})
				# pass
		self.appendString(addr, idx + 1, string)
		# logDbgC(f"handle_loadString() => string: {string} @{addr} ({int(addr, 16)}) ...")
		self.wdtFunctionList.addString(string, int(addr, 16))
		# QApplication.processEvents()
		# pass

	# oldComment = ""
	def handle_loadInstruction(self, instruction, target=None, loadDisassembly=True):
		self.instCnt += 1
		# if target is None:
		#     daTarget = self.driver.target
		# else:
		daTarget = self.driver.target  # target

		daData = str(instruction.GetData(daTarget))
		if loadDisassembly:
			if self.lastSubSymbolKey:
				self.disassemblies[self.lastModuleKey][self.lastSymbolKey][self.lastSubSymbolKey].update(
					{self.instCnt: instruction})

		idx = daData.find("                             ")
		if idx == -1:
			idx = daData.find("		            ")
			if idx == -1:
				idx = daData.find("		         ")
				if idx == -1:
					idx = daData.find("		      ")
		if idx != -1:
			daHex = daData[:idx]
			daDataNg = daData[idx:]
		else:
			daHex = ""
			daDataNg = ""
		comment = instruction.GetComment(daTarget)
		# comment = inst.GetComment(self.target)
		# print(f"comment: {comment} / {daTarget} ...")
		# if comment == '"setAction:"':
		#     newOldComment = self.oldComment.strip('"')
		#     logDbgC(f"FOUND SETACTION: {newOldComment} !!!!")
		# else:
		#     self.oldComment = comment
		delta_addr, delta_addrHex = getAddrDelta(instruction, daTarget)  # self.driver.target)

		# print(f"LIBADDR: {hex(int(str(instruction.GetAddress().GetLoadAddress(daTarget)), 10))}")
		if is_hex_string(instruction.GetOperands(daTarget)) and int(instruction.GetOperands(daTarget), 16) < int(
				"0x100000000", 16):
			self.appendAsmText(hex(int(str(instruction.GetAddress().GetLoadAddress(daTarget)), 10)),
							   instruction.GetMnemonic(daTarget), hex(int(instruction.GetOperands(daTarget), 16) + (
					delta_addr if int(instruction.GetOperands(daTarget), 16) < int("0x100000000", 16) else 0)), comment,
							   daHex, "".join(str(daDataNg).split()), True, "", self.instCnt - 1)
		else:
			self.appendAsmText(hex(int(str(instruction.GetAddress().GetLoadAddress(daTarget)), 10)),
							   instruction.GetMnemonic(daTarget), instruction.GetOperands(daTarget), comment,
							   daHex, "".join(str(daDataNg).split()), True, "", self.instCnt - 1)

	def appendAsmSymbol(self, addr, symbol, bold=False):
		# print(f"appendAsmSymbol: {symbol}")
		# Define the text for the spanning cell
		# text = symbol

		table_widget = self.tblDisassembly
		# Get the row count
		row_count = table_widget.rowCount()

		# Insert a new row
		table_widget.insertRow(row_count)

		# titleLabel = text or "__stubs" # text if text is not None else "__stubs"
		# Create a spanning cell item
		item = QTableWidgetItem(f'{symbol or "__stubs"}')
		item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
		if bold:
			item.setBackground(QColor(138, 57, 0))  # 0, 22, 161))
			# item.setBackground(QColor(0, 22, 161))
		else:
			item.setBackground(QColor(64, 0, 255, 96))
		item.setForeground(QColor("black"))
		# item.font().setBold(True)
		# fnt = item.font()
		# fnt.setBold(bold)
		if bold:
			item.setFont(ConfigClass.fontBold)
		# Set the item to span all columns
		table_widget.setSpan(row_count, 0, 1, table_widget.columnCount())  # Adjust row and column indices as needed
		# Set the item in the table
		table_widget.setItem(row_count, 0, item)
		self.tblDisassembly.symbolCount += 1

	# row_index = item.row()  # Get the row of the item
	# height = table_widget.verticalHeader().sectionSize(row_index)
	# logDbg(f"Row height: {height}")

	def appendString(self, addr, idx, string):
		self.tblDisassembly.addRowString(idx, addr, string)

	def appendAsmText(self, addr, instr, args, comment, data, dataNg, addLineNum=True, rip="", lineNo=-1):
		item = self.tblDisassembly.addRow(lineNo, addr, instr, args, comment, data, dataNg, rip)

	# TMP HACK -> MOVE AWAY FROM HERE !!!
	arrRememberedLocs = {}

	currentPCRow = -1

	def clearPC(self):
		self.tblDisassembly.clearPC()
		# logDbgC(f"!!!!!!!! IN CLEAR PC {self.currentPCRow} / {COL_PC} !!!!!!!!")
		# if self.tblDisassembly.item(self.currentPCRow, COL_PC) is not None:
		#     logDbgC(f"!!!!!!!! IN CLEAR PC !!!!!!!! {COL_PC} / {self.tblDisassembly.item(self.currentPCRow, COL_PC).text()} ...")
		#     if self.tblDisassembly.item(self.currentPCRow, COL_PC).text().endswith("I"):
		#         self.tblDisassembly.item(self.currentPCRow, COL_PC).setText('I')
		#     else:
		#         if self.tblDisassembly.item(self.currentPCRow, COL_PC).text().isdigit():
		#             pass
		#         else:
		#             self.tblDisassembly.item(self.currentPCRow, COL_PC).setText('')
		#         self.tblDisassembly.item(self.currentPCRow, COL_PC).setText('')
		# # else:
		# #     self.tblDisassembly.item(self.currentPCRow, COL_PC).setText('')
		#     # curRememberLoc = arrRememberedLocs.get(self.table.item(self.currentPCRow, COL_ADDRESS).text())
		#     # if curRememberLoc is not None:
		#     #     self.table.setBGColor(self.currentPCRow, False, QColor(220, 220, 255, 0), range(1, 8))
		#     #     self.table.item(self.currentPCRow, COL_PC).setForeground(QColor("black"))
		#     # else:
		#     #     self.table.setBGColor(self.currentPCRow, False)

	def getCurrentModule(self):
		return self.tblDisassembly.getCurrentModule()

	def setCurrentModule(self, newCurModule):
		return self.tblDisassembly.setCurrentModule(newCurModule)

	def setPC(self, pc, pushLocation=False):
		return self.tblDisassembly.setPC(pc, pushLocation)
		# # logDbgC(f"pc: {getAddrStr(pc)}")
		# if isinstance(pc, str):
		#     currentPC = pc.lower()
		# else:
		#     currentPC = hex(pc).lower()
		#
		# # logDbgC(f"setPC: {currentPC} ({pc})")
		# for row in range(self.tblDisassembly.rowCount()):
		#     if self.tblDisassembly.item(row, COL_ADDRESS) != None:
		#         if self.tblDisassembly.item(row, COL_ADDRESS).text().lower() == currentPC:
		#             self.currentPCRow = row
		#             self.tblDisassembly.item(row, COL_PC).setText('>')
		#             # logDbgC(f"setPC => row: {row}")
		#             # self.tblDisassembly.setFocus(Qt.FocuasReason.NoFocusReason)
		#             self.tblDisassembly.selectRow(row)
		#             self.tblDisassembly.scrollToRow(row)
		#
		#             # self.viewAddress()
		#             self.tblDisassembly.setBGColor(row, True)
		#         else:
		#             # if self.table.item(row, COL_PC).text().isdigit():
		#             # 	pass
		#             # else:
		#             self.tblDisassembly.item(row, COL_PC).setText('')
		#             self.tblDisassembly.setBGColor(row, False, QColor(220, 220, 255, 0),
		#                                   range(1, 9 if self.tblDisassembly.showLineNumber else 8))
		#
		# #         curRememberLoc = arrRememberedLocs.get(self.table.item(row, COL_ADDRESS).text())
		# #         if curRememberLoc is not None:
		# #             self.table.setBGColor(row, True, QColor("yellow"), range(COL_BP), QColor("black"))
		# #             if not self.table.item(row, COL_PC).text().endswith('I'):
		# #                 # 	self.table.item(row, 0).setText(self.table.item(row, 0).text())
		# #                 # else:
		# #                 self.table.item(row, COL_PC).setText(self.table.item(row, COL_PC).text() + 'I')  # + 'I'
		# #                 self.table.item(row, COL_PC).setForeground(QColor("black"))
		# #
		# # if pushLocation:
		# #     self.locationStack.pushLocation(currentPC)


class SelectedItemBGDelegate(QStyledItemDelegate):

	# def sizeHint(self, option, index):
	#     return QSize(320, 20)  # Width, Height

	# def __init__(self, parent, QObject=None, *args, **kwargs): # real signature unknown; NOTE: unreliably restored from __doc__
	#     super(QStyledItemDelegate, self).__init__(parent, None, *args, **kwargs)
	#     pass

	def initStyleOption(self, option, index):
		super(SelectedItemBGDelegate, self).initStyleOption(option, index)

		# option.backgroundBrush = QBrush(QColor(SettingsHelper().getValue(SettingsValues.SelectedRowColor)))

	# class WidthBasedDelegate(QStyledItemDelegate):
	# def sizeHint(self, option, index):
	#     text = index.data()
	#     font_metrics = QFontMetrics(ConfigClass.font12) # option.font)
	#     width = font_metrics.horizontalAdvance(text)
	#     height = 20 # font_metrics.height()
	#     return QSize(width, height)

	def paint(self, painter: QPainter, option, index: QModelIndex):
		painter.save()

		painter.setFont(ConfigClass.font12)
		# Get data
		icon = index.data(Qt.ItemDataRole.DecorationRole)
		text = index.data(Qt.ItemDataRole.DisplayRole)
		row = int(index.data(Qt.ItemDataRole.UserRole))

		# Icon
		icon_size = QSize(18, 18)
		icon_rect = QRect(option.rect.left() + 5, option.rect.top() + 2, icon_size.width(), icon_size.height())

		option.rect.setHeight(icon_size.height() + 4)

		if option.state & QtWidgets.QStyle.StateFlag.State_Selected:
			# QColor(SettingsHelper().getValue(SettingsValues.SelectedRowColor))
			painter.fillRect(option.rect, QColor(SettingsHelper().getValue(
				SettingsValues.SelectedRowColor)))  # ConfigClass.colorSelected) # QColor("#9b000c")) #144aff"))

		# if isinstance(icon, QPixmap):
		#     # scaled_icon = icon.scaled(icon_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
		#     painter.drawPixmap(icon_rect, icon)

		text_rect = icon_rect
		text_rect.setLeft(icon_rect.right() + 5)
		text_rect.setWidth(option.rect.width() - icon_size.width() - 10)
		# # text_rect = QRect(
		# #     icon_rect.right() + 5,
		# #     option.rect.top(),
		# #     option.rect.width() - icon_size.width() - 10,
		# #     icon_size.height() + 10
		# # )
		#
		# print(f"text_rect: {text_rect} / text: {text} / row: {row}...")
		#
		# # painter.setFont(ConfigClass.font12)
		painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, text)

		painter.restore()


class DisassemblyTableWidget(BaseTableWidget):
	actionCopyAddress = None

	symbolCount = 0
	locationStack = LocationStack()
	# TMP HACK -> MOVE AWAY FROM HERE !!!
	arrRememberedLocs = {}

	currentPCRow = 0
	oldMouseMoveItem = None
	itemOld = None

	bpMgr = None

	def __init__(self, driver, bpHelper, parent):
		super().__init__()

		self.driver = driver
		self.bpHelper = bpHelper
		self.parent = parent
		self.showLineNumber = SettingsHelper().getValue(SettingsValues.ShowLineNumInDisassembly)
		self.bpMgr = BreakpointManager(self.driver)

		self.setHelper = SettingsHelper()
		self.quickToolTip = QuickToolTip()
		self.oldMouseMoveItem = None
		self.arm64Ref = Arm64MnemonicReference()
		# self.arm64Ref.getDoc("MOVK")

		# self.setStyle(QStyleFactory.create("Fusion"))
		# self.setItemDelegate(ForegroundFixDelegate(self))

		# self.setItemDelegate(SelectedItemBGDelegate())

		self.context_menu = QMenu(self)
		self.actionEnableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
		# self.actionEnableBP.triggered.connect(self.handle_enableBP)
		self.actionDeleteBP = self.context_menu.addAction("Delete Breakpoint")
		self.actionDeleteBP.triggered.connect(self.deleteBP_clicked)
		self.actionEditBP = self.context_menu.addAction("Edit Breakpoint")
		# self.actionEditBP.triggered.connect(self.handle_editBP)
		self.context_menu.addSeparator()
		self.actionEditHexValue = self.context_menu.addAction("Edit Hex Value")
		# self.actionEditHexValue.triggered.connect(self.handle_editHexValue)
		self.context_menu.addSeparator()
		self.actionEditCondition = self.context_menu.addAction("Edit condition")
		# self.actionEditCondition.triggered.connect(self.handle_editCondition)

		self.context_menu.addSeparator()
		self.actionCopyAddress = self.context_menu.addAction("Copy address")
		self.actionCopyAddress.triggered.connect(self.handle_copy_address)
		# actionCopyAddress.triggered.connect(self.handle_copyAddress)
		actionCopyInstruction = self.context_menu.addAction("Copy instruction")
		# actionCopyInstruction.triggered.connect(self.handle_copyInstruction)
		actionCopyHex = self.context_menu.addAction("Copy hex value")
		# actionCopyHex.triggered.connect(self.handle_copyHexValue)
		self.context_menu.addSeparator()
		self.actionFindReferences = self.context_menu.addAction("Find references")
		self.actionFindReferences.triggered.connect(self.handle_findReferences)
		self.actionShowMemory = self.context_menu.addAction("Show memory")
		self.actionShowMemory.triggered.connect(self.handle_showMemory)
		self.actionShowMemoryFor = self.context_menu.addAction("Show memory for ...")
		self.actionShowMemoryFor.setStatusTip("Show memory for ...")
		self.actionShowMemoryFor.triggered.connect(self.handle_showMemoryFor)

		self.context_menu.addSeparator()
		self.actionSetPC = self.context_menu.addAction("Set new PC")
		# self.actionSetPC.triggered.connect(self.handle_setPC)
		self.actionGotoAddr = self.context_menu.addAction("Goto Address")
		# self.actionGotoAddr.triggered.connect(self.handle_gotoAddr)
		self.context_menu.addSeparator()
		self.actionRememberLoc = self.context_menu.addAction("Remember Location")
		# self.actionRememberLoc.triggered.connect(self.handle_RememberLoc)
		self.actionRememberLocBlack = self.context_menu.addAction("Remember Location BLACK")
		# self.actionRememberLocBlack.triggered.connect(self.handle_RememberLocBlack)

		colCount = 9 if self.showLineNumber else 8
		self.setColumnCount(colCount)
		curCol = 0

		if self.showLineNumber:
			self.setColumnWidth(curCol, 42)
			labels = ['No.', 'PC', 'BP', 'Address', 'Mnemonic', 'Operands', 'Hex', 'Data', 'Comment']
			global COL_LINE
			COL_LINE = curCol
			curCol += 1
		else:
			labels = ['PC', 'BP', 'Address', 'Mnemonic', 'Operands', 'Hex', 'Data', 'Comment']

		global COL_PC
		COL_PC = curCol + 0
		global COL_BP
		COL_BP = curCol + 1
		global COL_ADDRESS
		COL_ADDRESS = curCol + 2
		global COL_MNEMONIC
		COL_MNEMONIC = curCol + 3
		global COL_OPERANDS
		COL_OPERANDS = curCol + 4
		global COL_HEX
		COL_HEX = curCol + 5
		global COL_DATA
		COL_DATA = curCol + 6
		global COL_COMMENT
		COL_COMMENT = curCol + 7

		self.setColumnWidth(curCol, 42)
		self.setColumnWidth(curCol + 1, 32)
		self.setColumnWidth(curCol + 2, 108)
		self.setColumnWidth(curCol + 3, 84)
		self.setColumnWidth(curCol + 4, 256)
		self.setColumnWidth(curCol + 5, 240)
		self.setColumnWidth(curCol + 6, 180)
		self.setColumnWidth(curCol + 7, 300)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.horizontalHeader().setHighlightSections(False)
		self.setHorizontalHeaderLabels(labels)
		self.horizontalHeaderItem(0).setFont(ConfigClass.font)
		self.horizontalHeaderItem(1).setFont(ConfigClass.font)
		self.horizontalHeaderItem(2).setFont(ConfigClass.font)
		self.horizontalHeaderItem(3).setFont(ConfigClass.font)
		self.horizontalHeaderItem(4).setFont(ConfigClass.font)
		self.horizontalHeaderItem(5).setFont(ConfigClass.font)
		self.horizontalHeaderItem(6).setFont(ConfigClass.font)
		self.horizontalHeaderItem(7).setFont(ConfigClass.font)

		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(3).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(4).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(6).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(7).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)

		if self.showLineNumber:
			self.horizontalHeaderItem(8).setFont(ConfigClass.font)
			self.horizontalHeaderItem(8).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)

		# # Usage (assuming you have a created table widget named `table`):
		self.delegate = CustomStyledItemDelegate()
		self.setItemDelegate(self.delegate)

		#		self.horizontalHeaderItem(6).setFont(ConfigClass.font)
		self.setFont(ConfigClass.font)

		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
		self.setMouseTracking(True)
		# self.cellClicked.connect(self.on_cell_clicked)
		self.cellDoubleClicked.connect(self.on_double_click)
		self.setVerticalScrollBar(QScrollBar())
		self.verticalScrollBar().valueChanged.connect(self.on_scroll)

		self.overlay = HoverOverlay()
		# self.setMouseTracking(True)
		self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

	def keyPressEvent(self, event: QKeyEvent):
		# logDbgC(f"AssemblyTableWidget.keyPressEvent({event}) ...")
		modifiers = event.modifiers()
		# if modifiers & Qt.KeyboardModifier.ShiftModifier:
		#     print("Shift is pressed")
		if modifiers & Qt.KeyboardModifier.ControlModifier:  # MetaModifier:  # ⌘ Command on macOS
			print("Command is pressed")
			# self.tryShowMnemonicDoc(event)

	def keyReleaseEvent(self, event: QKeyEvent):
		print("Key released:", event.key())

	def mouseMoveEvent(self, event):
		pos = event.pos()
		item = self.itemAt(pos)
		# logDbgC(f"pos: {pos}, item: {item} / text: {item.text()}, self.itemOld: {self.itemOld} ...")
		if item != None and self.itemOld != item:
			self.itemOld = item
			row, col = item.row(), item.column()
			# logDbgC(f"row: {row}, col: {col} ...")
			if col == COL_OPERANDS:
				item.setToolTip(self.quickToolTip.getQuickToolTip(item.text(), self.driver.debugger))
			# elif col == COL_ADDRESS:

			if self.item(row, COL_ADDRESS):
				self.actionShowMemoryFor.setText(f"Show memory pc: '{self.item(row, COL_ADDRESS).text()}'")


		modifiers = event.modifiers()
		if modifiers & Qt.KeyboardModifier.ControlModifier:
			self.tryShowMnemonicDoc(event)
		else:
			self.overlay.hide()
		super().mouseMoveEvent(event)

	def handle_copy_address(self):
		QApplication.clipboard().setText(self.item(self.selectedItems()[0].row(), COL_ADDRESS).text())

	def leaveEvent(self, event):
		self.overlay.hide()

	def handle_findReferences(self):
		row = self.selectedItems()[0].row()
		logDbgC(f"handle_findReferences: {self.item(row, 3).text()} ...")

	def tryShowMnemonicDoc(self, event):
		print(f"if modifiers & Qt.KeyboardModifier.ControlModifier: ...")
		if self.setHelper.getValue(SettingsValues.ShowMnemonicInfo):
			index = self.indexAt(event.pos())
			if index.isValid():
				item = self.itemAt(event.pos())
				if item is not None and item.column() == 4:  # and self.oldMouseMoveItem != item:
					if self.oldMouseMoveItem != item:
						self.oldMouseMoveItem = item
						cell_rect = self.visualRect(index)
						global_pos = self.viewport().mapToGlobal(cell_rect.topLeft())
						# self.arm64Ref.getDoc(str(index.data()))
						title, desc = self.arm64Ref.getDoc(str(index.data()).upper())
						if title != "" and desc != "":
							self.overlay.showAt(global_pos + QPoint(0, cell_rect.height() + 15), f"{title}", f"{desc}")
						else:
							self.overlay.hide()
				else:
					self.overlay.hide()
			else:
				self.overlay.hide()
		# else:
		#     self.overlay.hide()

	# def mouseMoveEvent(self, event):
	#     # pos = event.pos()
	#     # item = self.itemAt(pos)
	#     #
	#     # if item != None and self.itemOld != item:
	#     #     row, col = item.row(), item.column()
	#     #     if col == COL_OPERANDS:
	#     #         #				print(f"Cell: ({row}, {col}), Mouse: ({pos.x()}, {pos.y()})")
	#     #         item.setToolTip(self.quickToolTip.getQuickToolTip(item.text(), self.driver.debugger))
	#     #         itemMnem = self.item(row, COL_MNEMONIC)
	#     #         if itemMnem.text() in ("jmp", "jne", "jnz", "je", "jz", "call"):
	#     #             self.window().updateStatusBar(f"DoubleClick to jump to {item.text()}", False)
	#     #         else:
	#     #             self.window().resetStatusBar()
	#     #     #				if len(self.selectedItems()) > 0 and self.item(self.selectedItems()[0].row(), 3) != None:
	#     #     #					if self.item(self.selectedItems()[0].row(), 3).text() == "jmp":
	#     #     #						self.window().updateStatusBar("Jump to ...")
	#     #
	#     #     self.itemOld = item
	#     #
	#     # # Call the original method to ensure default behavior continues
	#     super().mouseMoveEvent(event)

	def on_double_click(self, row, col):
		# pass
		logDbgC(f"DISASM double_clickediclick ... COL_ADDRESS: {COL_ADDRESS} / COL_BP: {COL_BP}")
		addr = self.item(row, COL_ADDRESS)
		if col in range(3 if self.showLineNumber else 2):
			logDbgC(f"=============>>>>>>>>>>>>>>>> INHEA (0)")
			# #			self.toggleBPOn(row)
			# # bp = self.driver.getTarget().BreakpointCreateByAddress(int(self.item(self.selectedItems()[0].row(), 2).text(), 16))
			# addr = self.item(row, COL_ADDRESS)
			bpCol = self.item(row, COL_BP)
			if addr is not None and bpCol is not None:
				logDbgC(f"=============>>>>>>>>>>>>>>>> INHEA (1)")
				bFound = False
				for i in range(self.driver.target.GetNumBreakpoints()):
					bp = self.driver.target.GetBreakpointAtIndex(i)
					logDbgC(f"=============>>>>>>>>>>>>>>>> INHEA (2)")
					if bp.GetNumLocations() > 0:
						for j in range(bp.GetNumLocations()):
							logDbgC(f"=============>>>>>>>>>>>>>>>> INHEA (3)")
							bl = bp.GetLocationAtIndex(j)
							if bl:
								logDbgC(f"=============>>>>>>>>>>>>>>>> INHEA (4)")
								if addr.text() == hex(bl.GetAddress().GetLoadAddress(self.driver.target)):
									logDbgC(f"=============>>>>>>>>>>>>>>>> INHEA (5)")
									self.bpMgr.enableBPByID(f"{bp.GetID()}.{bl.GetID()}", not bpCol.isBPEnabled)
									# if bpCol.isBPEnabled:
									#     logDbgC(f"=============>>>>>>>>>>>>>>>> INHEA (7) {bp.GetID()}.{bl.GetID()}")
									#     self.driver.debugger.HandleCommand(f"br disable {bp.GetID()}.{bl.GetID()}")
									# else:
									#     logDbgC(f"=============>>>>>>>>>>>>>>>> INHEA (8)")
									#     self.driver.debugger.HandleCommand(f"br enable {bp.GetID()}.{bl.GetID()}")
									bFound = True
									break
						if bFound:
							break
				if not bFound:  # -s {modName}
					self.driver.debugger.HandleCommand(f"br set -a {addr.text()}")

					# bp.GetID()
					# if bp.isBPEnabled:

				#     # self.driver.debugger.HandleCommand(f"br set -a {self.item(self.selectedItems()[0].row(), COL_ADDRESS).text()}")
				#     self.bpHelper.enableBP(addr.text(), not bp.isBPEnabled, False)
				#     self.toggleBP(addr.text())
				#     self.window().wdtBPsWPs.treBPs.toggleBP(addr.text())
				logDbgC(
					f"Setting Breakpoint from DisassemblyTableWidget @ {addr} / status: {bpCol} / {bpCol.isBPEnabled} ...")
				# if bp.isBPEnabled:
				#     self.driver.debugger.HandleCommand("br disable ")
			pass
		elif col == COL_HEX:
			# lib.utils.setStatusBar(f"Editing data @: {str(self.item(self.selectedItems()[0].row(), 2).text())}")
			logDbgC(f"Editing Hex Value in TableWidget ...")
		elif col == COL_MNEMONIC:
			iMnemonic = self.item(row, COL_MNEMONIC).text()
			# logDbgC(f"Show mnemonic doc: {iMnemonic} ...")
			self.open_dialog(iMnemonic)
		elif col in range(5 if self.showLineNumber else 4, 6 if self.showLineNumber else 5):
			logDbgC(f"Trying to jump to operand address in TableWidget ...")
			iMnemonic = self.item(row, COL_MNEMONIC)
			if iMnemonic is not None:
				sMnemonic = iMnemonic.text()
				if sMnemonic in JMP_MNEMONICS:
					iOperand = self.item(row, COL_OPERANDS)
					if iOperand is not None:
						sOperand = iOperand.text()
						sAddrJumpTo = getAddrFromOperands(sMnemonic, sOperand)
						self.locationStack.pushLocation(str(addr.text()))
						bRet = self.viewAddress(sAddrJumpTo)
						logDbgC(f"Trying to jump to memory @ {sAddrJumpTo} / Operand: {sOperand} / result: {bRet}...")

						if not bRet:
							self.window().handle_showMemory(sAddrJumpTo)
			# if self.item(self.selectedItems()[0].row(), COL_MNEMONIC) != None:
			#     # arrJumpMnemonics = ("call", "jmp", "jne", "jz", "je", "jnz", "jle", "jl", "jge", "jg")
			#     if self.item(self.selectedItems()[0].row(), COL_MNEMONIC).text().startswith(
			#             JMP_MNEMONICS):  # ("call", "jmp", "jne", "jz", "je", "jnz", "jle", "jl", "jge", "jg")):
			#         jumpAddr = str(self.item(self.selectedItems()[0].row(), COL_OPERANDS).text())
			#
			#         if sMnemonic == "cbnz" or sMnemonic == "cbz":
			#             sAddrJumpTo = sAddrJumpTo.split(",")[1].strip()
			#
			#         self.parent.locationStack.pushLocation(
			#             str(self.item(self.selectedItems()[0].row(), COL_ADDRESS).text()))
			#         self.parent.locationStack.pushLocation(jumpAddr)
			#         self.parent.viewAddress(jumpAddr)
			#     # newPC = str(gotoDlg.txtInput.text())
			#     # lib.utils.setStatusBar(f"Go to address: {newPC}")
			#     # self.window().txtMultiline.viewAddress(newPC)

	def open_dialog(self, iMnemonic):
		dialog = WebDialog(f"https://arm.jonpalmisc.com/latest_aarch64/{iMnemonic}")
		dialog.exec()

	def contextMenuEvent(self, event):
		# if len(self.selectedItems()) <= 0:
		#     return
		# if self.item(self.selectedItems()[0].row(), COL_BP) != None:
		#     if self.item(self.selectedItems()[0].row(), COL_BP).isBPEnabled:
		#         self.actionEnableBP.setText("Disable Breakpoint")
		#     else:
		#         self.actionEnableBP.setText("Enable Breakpoint")
		#     self.actionEnableBP.setData(self.item(self.selectedItems()[0].row(), COL_BP).isBPEnabled)
		#
		#     self.actionShowMemoryFor.setText("Show memory for:")
		#     self.actionShowMemoryFor.setEnabled(False)
		#     self.actionShowMemoryFor.setData("")
		#     if self.item(self.selectedItems()[0].row(), COL_MNEMONIC) != None:
		#         operandsText = self.quickToolTip.getOperandsText(
		#             self.item(self.selectedItems()[0].row(), COL_MNEMONIC).text())
		#         if operandsText != "":
		#             self.actionShowMemoryFor.setText("Show memory for: " + operandsText)
		#             self.actionShowMemoryFor.setEnabled(True)
		#             self.actionShowMemoryFor.setData(operandsText)

		self.context_menu.exec(event.globalPos())

	def handle_showMemory(self):
		# self.tabWidgetReg.setTabVisible()
		# self.window().idxMemTab.setTabVisible(2, True)

		if len(self.selectedItems()) > 0 and self.item(self.selectedItems()[0].row(), 3) != None:
			self.window().handle_showMemory(self.item(self.selectedItems()[0].row(),
													  3).text())  # tabWidgetMain.setCurrentIndex(self.window().idxMemTab) # , True
		# self.window().idxMemTab.setTabVisible(2, True)
		# self.idxMemTab = self.tabWidgetMain.addTab(self.tblHex, "Memory")
		pass

	def handle_showMemoryFor(self):
		if len(self.selectedItems()) > 0 and self.item(self.selectedItems()[0].row(), COL_ADDRESS) != None:
			currItem = self.item(self.selectedItems()[0].row(), COL_ADDRESS)
			self.window().handle_showMemory(currItem.text())

	def deleteBP_clicked(self):
		self.bpMgr = BreakpointManager(self.driver)
		self.bpMgr.deleteAllBPs()
		# return
		# row = self.selectedItems()[0].row()
		# addr = self.item(row, COL_ADDRESS)
		# bpCol = self.item(row, COL_BP)
		# bFound = False
		# logDbgC(f"deleteBP_clicked => row: {row}, addr: {addr.text()}")
		# if addr is not None and bpCol is not None:
		#     for i in range(self.driver.target.GetNumBreakpoints()):
		#         bp = self.driver.target.GetBreakpointAtIndex(i)
		#         if bp.GetNumLocations() > 0:
		#             bl = bp.GetLocationAtIndex(0)
		#             if bl:
		#                 if addr.text() == hex(bl.GetAddress().GetLoadAddress(self.driver.target)):
		#                     logDbgC(f"deleteBP_clicked => row: {row}, addr: {addr.text()} ===>>> FOUND")
		#                     # if bpCol.isBPEnabled:
		#                     #     self.driver.debugger.HandleCommand(f"br disable {bp.GetID()}")
		#                     # else:
		#                     #     self.driver.debugger.HandleCommand(f"br enable {bp.GetID()}")
		#                     self.driver.debugger.HandleCommand(f"breakpoint delete-f {addr.text()}")
		#                     bFound = True
		#                     break
		#     if not bFound:  # -s {modName}
		#         pass
		# return bFound

		# self.driver.debugger.HandleCommand(f"breakpoint delete-f {self.item(self.selectedItems()[0].row(), COL_ADDRESS).text()}")
		# self.bpHelper.deleteBP(self.item(self.selectedItems()[0].row(), COL_ADDRESS).text())

	disableScroll = False

	def on_scroll(self, value):
		if not self.disableScroll:
			self.window().wdtDisassembly.wdtControlFlow.view.verticalScrollBar().setValue(value)

	def resetContent(self):
		self.setRowCount(0)
		self.symbolCount = 0

	def viewAddress(self, address, pushLocation=True):
		bRet = False
		for row in range(self.rowCount()):
			if self.item(row, COL_ADDRESS) != None:
				if self.item(row, COL_ADDRESS).text().lower() == address.lower():
					#					self.item(row, 0).setText('>')
					self.setFocus(Qt.FocusReason.NoFocusReason)
					self.selectRow(row)
					self.scrollToRow(row)

					if pushLocation:
						self.locationStack.pushLocation(address.lower())

					bRet = True
					break

		return bRet

	def selectAndViewRow(self, row=-1):
		if row == -1:
			rowToSelectAndView = self.currentPCRow
		else:
			rowToSelectAndView = row

		self.selectRow(rowToSelectAndView)
		self.scrollToRow(rowToSelectAndView)

		self.setBGColor(rowToSelectAndView, True)

	currentModule = ""

	def getCurrentModule(self):
		return self.currentModule

	def setCurrentModule(self, newCurModule):
		if self.currentModule != newCurModule:
			self.currentModule = newCurModule
			return True
		return False

	def setPC(self, pc, pushLocation=False):
		# printStacktrace(self.driver)
		# debug_stack()
		pcToUse = pc
		# if self.window().treBreakpoints.treBP.nextViewAddress:
		# 	pcToUse = self.window().treBreakpoints.treBP.nextViewAddress
		# 	self.window().treBreakpoints.treBP.nextViewAddress = None

		# logDbgC(f"setPC: {pc} / pushLocation: {pushLocation} ...")
		if pc is None or pc == "":
			return


		# currPCInt = 0x0
		if isinstance(pcToUse, str):
			currentPC = pcToUse.lower()
			currPCInt = int(pcToUse, 16)
		else:
			currentPC = hex(pcToUse).lower()
			currPCInt = pcToUse

		# logDbgC(f"pc: {currentPC} / {currPCInt} => SET NEW PC !!!!!")

		bAddrFound = False
		# logDbgC(f"setPC: {currentPC} ({pc})")
		for row in range(self.rowCount()):
			if self.item(row, COL_ADDRESS) != None:
				if int(self.item(row, COL_ADDRESS).text().lower(), 16) == currPCInt:  # currentPC:
					self.currentPCRow = row
					self.item(row, COL_PC).setText('>')
					# logDbgC(f"SETTING > to row: {row} / currentPC: {currentPC} ...")
					# logDbgC(f"setPC => row: {row}")
					# self.tblDisassembly.setFocus(Qt.FocuasReason.NoFocusReason)
					# self.selectRow(row)
					# self.scrollToRow(row)
					#
					# # self.viewAddress()
					# self.setBGColor(row, True)
					self.selectAndViewRow(row)
					bAddrFound = True
				else:
					# if self.table.item(row, COL_PC).text().isdigit():
					# 	pass
					# else:
					self.item(row, COL_PC).setText('')
					self.setBGColor(row, False, QColor(220, 220, 255, 0),
									range(0, 9 if self.showLineNumber else 8))

		#         curRememberLoc = arrRememberedLocs.get(self.table.item(row, COL_ADDRESS).text())
		#         if curRememberLoc is not None:
		#             self.table.setBGColor(row, True, QColor("yellow"), range(COL_BP), QColor("black"))
		#             if not self.table.item(row, COL_PC).text().endswith('I'):
		#                 # 	self.table.item(row, 0).setText(self.table.item(row, 0).text())
		#                 # else:
		#                 self.table.item(row, COL_PC).setText(self.table.item(row, COL_PC).text() + 'I')  # + 'I'
		#                 self.table.item(row, COL_PC).setForeground(QColor("black"))
		#
		if pushLocation:
			self.locationStack.pushLocation(currentPC)
		return bAddrFound

	def clearPC(self):
		# logDbgC(f"!!!!!!!! IN CLEAR PC {self.currentPCRow} / {COL_PC} !!!!!!!!")
		if self.item(self.currentPCRow, COL_PC) is not None:
			# logDbgC(f"!!!!!!!! IN CLEAR PC !!!!!!!! {COL_PC} / {self.item(self.currentPCRow, COL_PC).text()} ...")
			self.setBGColor(self.currentPCRow, False)
			if self.item(self.currentPCRow, COL_PC).text().endswith("I"):
				self.item(self.currentPCRow, COL_PC).setText('I')
			else:
				if self.item(self.currentPCRow, COL_PC).text().isdigit():
					pass
				else:
					self.item(self.currentPCRow, COL_PC).setText('')
				# self.item(self.currentPCRow, COL_PC).setText('')
		# else:
		#     self.tblDisassembly.item(self.currentPCRow, COL_PC).setText('')
		# curRememberLoc = arrRememberedLocs.get(self.table.item(self.currentPCRow, COL_ADDRESS).text())
		# if curRememberLoc is not None:
		#     self.table.setBGColor(self.currentPCRow, False, QColor(220, 220, 255, 0), range(1, 8))
		#     self.table.item(self.currentPCRow, COL_PC).setForeground(QColor("black"))
		# else:
		#     self.table.setBGColor(self.currentPCRow, False)

	def getRowForAddress(self, address):
		cntSymbvols = 0
		for i in range(self.rowCount()):
			# if self.columnSpan(i, 0) >= self.columnCount() and self.item(i, 0).text().startswith("__"):
			#     cntSymbvols -= 1
			if self.item(i, COL_ADDRESS) != None and self.item(i, COL_ADDRESS).text() == address:
				# return i + cntSymbvols
				return int(i + cntSymbvols), int(self.item(i, 0).text())
		return 0, 0

	def get_total_table_height(self):
		total_height = 0
		for row in range(self.rowCount()):
			total_height += self.rowHeight(row)
		return total_height

	def setBGColor(self, row, colored=False, colorIn=QColor(220, 220, 255, 80), rangeIn=None, fgColor=None):
		if rangeIn is None:
			rangeIn = range(self.columnCount())
		if not colored:
			color = QColor(220, 220, 255, 0)
		else:
			color = colorIn  # QColor(220, 220, 255, 80)
		# Set background color for a specific item
		for i in rangeIn:  # range(self.columnCount()):
			# logDbg(f"i: {i}")
			item = self.item(row, i)  # Replace with desired row and column index
			if item is not None:
				# logDbg(f"item: {item}")
				item.setBackground(color)
				# logDbg(f"setBackground: {color}")
				if fgColor is not None:
					item.setForeground(fgColor)
					logDbgC(f"item.setForeground({fgColor.isValid()}).....")

	# def setBGColor(self, row, colored=False, colorIn=QColor(220, 220, 255, 80), rangeIn=None, fgColor=None):
	#     if rangeIn is None:
	#         rangeIn = range(self.columnCount())
	#     if not colored:
	#         color = QColor(220, 220, 255, 0)
	#     else:
	#         color = colorIn
	#
	#     for i in rangeIn:
	#         item = self.item(row, i)
	#         if item is not None:
	#             item.setBackground(color)
	#             if fgColor is not None:
	#                 item.setForeground(fgColor)
	#                 logDbgC(f"item.setForeground({fgColor.isValid()}).....")

	def addRow(self, lineNum, address, instr, args, comment, data, dataNg, rip=""):
		currRowCount = self.rowCount()
		self.setRowCount(currRowCount + 1)

		item = DisassemblyImageTableWidgetItem()
		curCol = 0
		if self.showLineNumber:
			self.addItem(currRowCount, COL_LINE, str(lineNum + 1))
			curCol += 1

		self.addItem(currRowCount, COL_PC, ('>' if rip == address else '') + ('I' if False else ''))
		self.setItem(currRowCount, COL_BP, item)
		self.addItem(currRowCount, COL_ADDRESS, address)
		self.addItem(currRowCount, COL_MNEMONIC, instr)
		if instr == "adrp":
			# logDbgC(f"adrp HIT!!! => {hex(self.get_page_address(int(address, 16)))} ...")
			# Split the string at the comma
			parts = args.split(',')

			offset = int(parts[1].strip()) * 0x1000
			# Replace the second part and strip any whitespace
			updated = f"{parts[0].strip()}, {hex(self.get_page_address(int(address, 16)) + offset)}"
			self.addItem(currRowCount, COL_OPERANDS, updated)
		else:
			self.addItem(currRowCount, COL_OPERANDS, args)
		# self.addItem(currRowCount, curCol + 4, args)
		self.addItem(currRowCount, COL_HEX, data)
		self.addItem(currRowCount, COL_DATA, dataNg)
		self.addItem(currRowCount, COL_COMMENT, comment)

		self.setRowHeight(currRowCount, 14)
		return item

	def get_page_address(self, instruction_addr, page_size=0x1000):
		page_mask = ~(page_size - 1)
		return instruction_addr & page_mask

	def addRowString(self, lineNum, address, string=""):
		if string == "":
			return

		table_widget = self
		row_count = table_widget.rowCount()
		table_widget.insertRow(row_count)

		item2 = QTableWidgetItem(f'{string}' or "__cstring")
		item2.setFlags(item2.flags() & ~Qt.ItemFlag.ItemIsEditable)

		item = DisassemblyImageTableWidgetItem()
		curCol = 0
		if self.showLineNumber:
			self.addItem(row_count, COL_LINE, str(lineNum))
			curCol += 1

		self.addItem(row_count, COL_PC, '')  # ('>' if rip == address else '') + ('I' if False else ''))
		self.setItem(row_count, COL_BP, item)
		self.addItem(row_count, COL_ADDRESS, address)
		table_widget.setSpan(row_count, COL_MNEMONIC, 1,
							 table_widget.columnCount() - (COL_MNEMONIC))  # Adjust row and column indices as needed
		self.setItem(row_count, COL_MNEMONIC, item2)
		# self.addItem(currRowCount, curCol + 4, args)
		# self.addItem(currRowCount, curCol + 5, data)
		# self.addItem(currRowCount, curCol + 6, dataNg)
		# self.addItem(currRowCount, curCol + 7, comment)

		self.setRowHeight(row_count, 14)

	def addItem(self, row, col, txt):

		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		if col != COL_HEX:
			item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Qt.ItemFlag.ItemIsSelectable)

		# Insert the items into the row
		self.setItem(row, col, item)

	def scrollToRow(self, row):
		allHeight = 0
		for i in range(self.rowCount()):
			allHeight += self.rowHeight(i)
			if i == row:
				break
		allHeight -= (self.viewport().height() / 2) + (self.rowHeight(1) / 2)
		self.verticalScrollBar().setValue(int(allHeight))

	def enableBP(self, address, enabled):
		for row in range(self.rowCount()):
			itmRow = self.item(row, COL_ADDRESS)
			if itmRow != None and itmRow.text().lower() == address.lower():
				item = self.item(row, COL_BP)
				#				item.toggleBPEnabled()
				# logDbgC(f"assemblerTextEdit.enableBP...")
				item.enableBP(enabled)
				# lib.utils.setStatusBar(f"Enabled breakpoint @: 0x{address:X} ({enabled})")
				break

	def deleteBP(self, address):
		for row in range(self.rowCount()):
			#			print(f'CHECKING BREAKPOINT AT ADDRESS: {self.item(row, 3).text()}')
			# if self.item(row, COL_ADDRESS) != None and self.item(row, COL_ADDRESS).text().lower() == address.lower():
			itmRow = self.item(row, COL_ADDRESS)
			if itmRow != None and itmRow.text().lower() == address.lower():
				#				self.toggleBPOn(row, updateBPWidget)
				self.item(row, COL_BP).setBPOn(False)
				break


class HoverOverlay(QWidget):

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
		self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
		self.setStyleSheet("background-color: rgba(0, 0, 0, 128); border-radius: 6px;")
		self.setWindowOpacity(0.85)

		# Add a QLabel to show the text
		self.label = QLabel("", self)
		self.label.setStyleSheet("color: white; font: bold 12px; padding: 6px;")
		layout = QVBoxLayout(self)
		layout.addWidget(self.label)
		self.labelDesc = QLabel("", self)
		self.labelDesc.setStyleSheet("color: white; font: 12px; padding: 6px;")
		layout.addWidget(self.labelDesc)
		layout.setContentsMargins(0, 0, 0, 0)

		self.hide()

	def showAt(self, pos, title, desc):
		self.label.setText(title)
		self.labelDesc.setText(desc)
		self.adjustSize()
		self.move(pos)
		self.show()
