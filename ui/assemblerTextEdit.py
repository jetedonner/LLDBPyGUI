#!/usr/bin/env python3

import lldb
import os
import sys
import re
import pyperclip

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QBrush, QPixmap, QImage
from PyQt6 import uic, QtWidgets, QtGui

# from ui.customQt.QControlFlowWidget import FixedScrollBar
from ui.helper.quickToolTip import *
from ui.helper.locationStack import *
from ui.baseTableWidget import *

from config import *

import lib.utils
from  ui.dialogs.dialogHelper import *
from dbg.breakpointHelper import *
from ui.helper.dbgOutputHelper import *
# from dbg.breakpointHelper import *
# from PyQt6.QtWidgets import QStyleFactory


from PyQt6.QtWidgets import QStyledItemDelegate
from PyQt6.QtGui import QBrush, QPalette, QColor
from PyQt6.QtCore import Qt


# class ForegroundFixDelegate(QStyledItemDelegate):
# 	def initStyleOption(self, option, index):
# 		super().initStyleOption(option, index)
# 		fg = index.data(Qt.ItemDataRole.ForegroundRole)
# 		if isinstance(fg, QBrush):
# 			option.palette.setBrush(QPalette.ColorRole.Text, fg)
# 		elif isinstance(fg, QColor) and fg.isValid():
# 			option.palette.setColor(QPalette.ColorRole.Text, fg)


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
			
	def setBPOn(self, on = True):
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

		color = QtGui.QColor("#FFFFFF")

		# if index.column() == 1:
		# 	color = QtGui.QColor("#34ebc6")
		# elif index.column() == 2:
		# 	color = QtGui.QColor("#FFFFFF")
		# elif index.column() == 3:
		# 	color = QtGui.QColor("#9546c7")
		if index.column() == 0:
			color = QtGui.QColor("#000000")

			cg = (
				QtGui.QPalette.ColorGroup.Normal
				if option.state & QtWidgets.QStyle.StateFlag.State_Enabled
				else QtGui.QPalette.ColorGroup.Disabled
			)
			if option.text == "I" or option.text == ">I":
				option.palette.setColor(cg, QtGui.QPalette.ColorRole.HighlightedText, color)
				option.palette.setColor(cg, QtGui.QPalette.ColorRole.Text, color)
				option.palette.setBrush(QtGui.QPalette.ColorRole.Text, QBrush(color))
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
		if index.column() == 0:
			color = QtGui.QColor("#000000")
			painter._color = color

		super().paint(painter, option, index)
		# print(f"CustomDelegate paint() / index: {dir(index)}....")
		if option.state & QStyle.StateFlag.State_Selected:# Qt.State_Selected:
			# option.palette.setColor(QPalette.ColorRole.Text, QColor("black"))

			brush = QBrush(Qt.GlobalColor.darkYellow)
			# Set custom background color for selected rows
			option.backgroundBrush = brush # Adjust color as desired


		else:
			# option.palette.setColor(QPalette.ColorRole.Text, QColor("black"))
			# Create a temporary QPixmap and fill it with the brush color
			pixmap = QPixmap(option.rect.size())  # Adjust dimensions as needed
			# logDbg(f"index.column: {index.column()}")
			pixmap.fill(Qt.GlobalColor.transparent)
			# if index.column() != 1:
			# 	return
			# 	# pixmap.fill(Qt.GlobalColor.black)
			# 	# painter.setBrush(QColor("black"))
			# 	pass
			# else:
			# 	pixmap.fill(Qt.GlobalColor.transparent)

			# if index.column == 0:
			# 	pixmap.fill(Qt.GlobalColor.black)

			# Convert the QPixmap to a QImage
			image = pixmap.toImage()
			
			painter.drawImage(option.rect, image)#option.background())





		# painter.setBrush(QBrush(QColor("black")))
		# painter.end()
		
class DisassemblyTableWidget(BaseTableWidget):
	
	sigEnableBP = pyqtSignal(str, bool)
	sigBPOn = pyqtSignal(str, bool)
	
	actionShowMemory = None
	quickToolTip = QuickToolTip()
	
#	def getSelectedRow(self):
#		if self.selectedItems() != None and len(self.selectedItems()) > 0:
#			return self.selectedItems()[0].row()
#		return None
#	
#	def getSelectedItem(self, col):
#		selRow = self.getSelectedRow()
#		if selRow != None:
#			return self.item(selRow, col)
#		return None
		
	def handle_copyHexValue(self):
#		selItem = self.getSelectedItem(5)
		if (selItem := self.getSelectedItem(5)) != None:
			pyperclip.copy(selItem.text())
			lib.utils.setStatusBar(f"Copied to clipboard HEX value: {selItem.text()}")
#		if self.item(self.selectedItems()[0].row(), 5) != None:
#			item = self.item(self.selectedItems()[0].row(), 5)
#			pyperclip.copy(item.text())
		
	def handle_copyInstruction(self):
#		if self.item(self.selectedItems()[0].row(), 3) != None and self.item(self.selectedItems()[0].row(), 4) != None:
#			itemMnem = self.item(self.selectedItems()[0].row(), 3)
#			itemOps = self.item(self.selectedItems()[0].row(), 4)
		if (itemMnem := self.getSelectedItem(3)) != None:
			if (itemOps := self.getSelectedItem(4)) != None:
				pyperclip.copy(itemMnem.text() + " " + itemOps.text())
				lib.utils.setStatusBar(f"Copied to clipboard instruction: {itemMnem.text()} {itemOps.text()}")
		
	def handle_copyAddress(self):
		if self.item(self.selectedItems()[0].row(), 2) != None:
			item = self.item(self.selectedItems()[0].row(), 2)
			pyperclip.copy(item.text())
			lib.utils.setStatusBar(f"Copied to clipboard address: {item.text()}")
		
	def handle_toggleBP(self):
		if self.item(self.selectedItems()[0].row(), 1) != None:
			item = self.item(self.selectedItems()[0].row(), 1)
			item.toggleBPOn()
			lib.utils.setStatusBar(f"Toggled breakpoint @: {self.item(self.selectedItems()[0].row(), 2).text()} to: {item.isBPOn}")
			self.sigBPOn.emit(self.item(self.selectedItems()[0].row(), 2).text(), item.isBPOn)
		pass
	
	def handle_deleteAllBPs(self):
		for i in range(self.rowCount()):
			if self.item(i, 1) != None:
				self.item(i, 1).setBPOn(False)
		
	def enableBP(self, address, enabled):
		for i in range(self.rowCount()):
			if self.item(i, 2) != None and self.item(i, 2).text() == address:
				item = self.item(i, 1)
#				item.toggleBPEnabled()
				item.enableBP(enabled)
				lib.utils.setStatusBar(f"Enabled breakpoint @: 0x{address:X} ({enabled})")
				break
		pass

	def getRowForAddress(self, address):
		for i in range(self.rowCount()):
			if self.item(i, 2) != None and self.item(i, 2).text() == address:
				return i
				# item = self.item(i, 1)
				# #				item.toggleBPEnabled()
				# item.enableBP(enabled)
				# lib.utils.setStatusBar(f"Enabled breakpoint @: 0x{address:X} ({enabled})")
				# break
		return 0
		
	def handle_editBP(self):
#		self.sigEnableBP.emit(self.item(self.selectedItems()[0].row(), 3).text(), item.isBPEnabled)
		if self.item(self.selectedItems()[0].row(), 2) != None:
			self.window().tabWidgetDbg.setCurrentIndex(2)
			self.window().wdtBPsWPs.treBPs.setFocus()
			self.window().wdtBPsWPs.treBPs.selectBPRow(self.item(self.selectedItems()[0].row(), 2).text())
#		pass
		
	def handle_enableBP(self):
		if self.item(self.selectedItems()[0].row(), 1) != None:
			item = self.item(self.selectedItems()[0].row(), 1)
			item.enableBP(not item.isBPEnabled)
#			self.window().wdtBPsWPs.treBPs.enableBPByAddress(self.item(self.selectedItems()[0].row(), 2).text(),  item.isBPEnabled)
		
	def handle_editCondition(self):
		BreakpointHelper(self.window(), self.window().driver).handle_editCondition(self, 2, 5)
		
	def handle_setPC(self):
		if self.item(self.selectedItems()[0].row(), 2) != None:
			dlg = InputDialog("Set new PC", "Please enter address for PC", self.item(self.selectedItems()[0].row(), 2).text())
			if dlg.exec():
				# print(f'dlg.txtInput: {dlg.txtInput.text()}')
				
				frame = self.driver.getTarget().GetProcess().GetThreadAtIndex(0).GetFrameAtIndex(0)
				if frame:
					newPC = int(str(dlg.txtInput.text()), 16)
					frame.SetPC(newPC)
					self.parent.setPC(newPC)
#					self.setPC(newPC)

	def get_total_table_height(self):
		total_height = 0
		for row in range(self.rowCount()):
			total_height += self.rowHeight(row)
		return total_height

	def handle_gotoAddr(self):
		if self.item(self.selectedItems()[0].row(), 2) != None:
			gotoDlg = GotoAddressDialog(self.item(self.selectedItems()[0].row(), 2).text())
			if gotoDlg.exec():
				# print(f"GOING TO ADDRESS: {gotoDlg.txtInput.text()}")
				# lib.utils.setStatusBar(f"Go to address to clipboard instruction: {gotoDlg.txtInput.text()} {temOps.text()}")
				newPC = str(gotoDlg.txtInput.text())
				lib.utils.setStatusBar(f"Go to address: {newPC}")
				self.parent.viewAddress(newPC)
			pass
		
	driver = None
	symbolCount = 0
	# setIT = False
	def setBGColor(self, row, colored = False, colorIn = QColor(220, 220, 255, 80), rangeIn = None, fgColor = None):
		if rangeIn is None:
			rangeIn = range(self.columnCount())
		if not colored:
			color = QColor(220, 220, 255, 0)
		else:
			color = colorIn #QColor(220, 220, 255, 80)
		# Set background color for a specific item
		for i in rangeIn: # range(self.columnCount()):
			# logDbg(f"i: {i}")
			item = self.item(row, i)  # Replace with desired row and column index
			if item is not None:
				# logDbg(f"item: {item}")
				item.setBackground(color)
				# logDbg(f"setBackground: {color}")
				if fgColor is not None:
					item.setForeground(fgColor)
					logDbg(f"item.setForeground({fgColor.isValid()}).....")
		
		# self.setIT w= not self.setIT
	disableScroll = False
	def on_scroll(self, value):
		if not self.disableScroll:
			# print(f"Scrolled to position: {value}")
			# logDbg(f"scroll: {value + 150}")
			self.window().wdtControlFlow.view.verticalScrollBar().setValue(value)
			# self.window().wdtControlFlow.view.centerOn(0, value + 150) # / 0.8231292517)
			# self.scroll()
			# self.view.verticalScrollBar().scroll(0, 0.783171521)

	bpHelper = None

	def __init__(self, driver, bpHelper, parent):
		super().__init__()
		
		self.driver = driver
		self.bpHelper = bpHelper
		self.parent = parent

		# self.setStyle(QStyleFactory.create("Fusion"))
		# self.setItemDelegate(ForegroundFixDelegate(self))

		self.context_menu = QMenu(self)
		
		self.actionEnableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
		self.actionEnableBP.triggered.connect(self.handle_enableBP)
		self.actionDeleteBP = self.context_menu.addAction("Delete Breakpoint")
		self.actionDeleteBP.triggered.connect(self.deleteBP_clicked)
		self.actionEditBP = self.context_menu.addAction("Edit Breakpoint")
		self.actionEditBP.triggered.connect(self.handle_editBP)
		self.context_menu.addSeparator()
		self.actionEditHexValue = self.context_menu.addAction("Edit Hex Value")
		self.actionEditHexValue.triggered.connect(self.handle_editHexValue)
		self.context_menu.addSeparator()
		actionEditCondition = self.context_menu.addAction("Edit condition")
		actionEditCondition.triggered.connect(self.handle_editCondition)
		
		self.context_menu.addSeparator()
		actionCopyAddress = self.context_menu.addAction("Copy address")
		actionCopyAddress.triggered.connect(self.handle_copyAddress)
		actionCopyInstruction = self.context_menu.addAction("Copy instruction")
		actionCopyInstruction.triggered.connect(self.handle_copyInstruction)
		actionCopyHex = self.context_menu.addAction("Copy hex value")
		actionCopyHex.triggered.connect(self.handle_copyHexValue)
		self.context_menu.addSeparator()
		self.actionFindReferences = self.context_menu.addAction("Find references")
		self.actionFindReferences.triggered.connect(self.handle_findReferences)
		self.actionShowMemory = self.context_menu.addAction("Show memory")
		self.actionShowMemoryFor = self.context_menu.addAction("Show memory for ...")
		self.actionShowMemoryFor.setStatusTip("Show memory for ...")
		self.actionShowMemoryFor.triggered.connect(self.handle_showMemoryFor)
		self.context_menu.addSeparator()
		self.actionSetPC = self.context_menu.addAction("Set new PC")
		self.actionSetPC.triggered.connect(self.handle_setPC)
		self.actionGotoAddr = self.context_menu.addAction("Goto Address")
		self.actionGotoAddr.triggered.connect(self.handle_gotoAddr)
		self.context_menu.addSeparator()
		self.actionRememberLoc = self.context_menu.addAction("Remember Location")
		self.actionRememberLoc.triggered.connect(self.handle_RememberLoc)
		self.actionRememberLocBlack = self.context_menu.addAction("Remember Location BLACK")
		self.actionRememberLocBlack.triggered.connect(self.handle_RememberLocBlack)
		
		self.setColumnCount(8)
		self.setColumnWidth(0, 42)
		self.setColumnWidth(1, 32)
		self.setColumnWidth(2, 108)
		self.setColumnWidth(3, 84)
		self.setColumnWidth(4, 256)
		self.setColumnWidth(5, 240)
		self.setColumnWidth(6, 180)
		self.setColumnWidth(7, 300)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.horizontalHeader().setHighlightSections(False)
		self.setHorizontalHeaderLabels(['PC', 'BP', 'Address', 'Mnemonic', 'Operands', 'Hex', 'Data', 'Comment']) # '#', 
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

		# Usage (assuming you have a created table widget named `table`):
		self.delegate = CustomStyledItemDelegate()
		self.setItemDelegate(self.delegate)		
		
#		self.horizontalHeaderItem(6).setFont(ConfigClass.font)
		self.setFont(ConfigClass.font)
		
		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
		self.setMouseTracking(True)
		self.cellDoubleClicked.connect(self.on_double_click)
		self.setVerticalScrollBar(QScrollBar())
		self.verticalScrollBar().valueChanged.connect(self.on_scroll)

	def keyPressEvent(self, event):
		if event.key() == Qt.Key.Key_Left:
			# self.label.setText("Left arrow pressed!")
			self.handle_left_arrow()
		elif event.key() == Qt.Key.Key_Right:
			# self.label.setText("Left arrow pressed!")
			self.handle_right_arrow()

	def handle_left_arrow(self):
		# 🔧 Insert your LLDB Python API logic here
		print("Executing LLDB action for left arrow...")
		self.window().back_clicked()

	def handle_right_arrow(self):
		# 🔧 Insert your LLDB Python API logic here
		print("Executing LLDB action for right arrow...")
		self.window().forward_clicked()

	itemOld = None
	
	def mouseMoveEvent(self, event):	
		pos = event.pos()
		item = self.itemAt(pos)
		
		if item != None and self.itemOld != item:
			row, col = item.row(), item.column()
			if col == 4:
#				print(f"Cell: ({row}, {col}), Mouse: ({pos.x()}, {pos.y()})")
				item.setToolTip(self.quickToolTip.getQuickToolTip(item.text(), self.driver.debugger))
				itemMnem = self.item(row, 3)
				if itemMnem.text() in ("jmp", "jne", "jnz", "je", "jz", "call"):
					self.window().updateStatusBar(f"DoubleClick to jump to {item.text()}", False)
				else:
					self.window().resetStatusBar()
#				if len(self.selectedItems()) > 0 and self.item(self.selectedItems()[0].row(), 3) != None:
#					if self.item(self.selectedItems()[0].row(), 3).text() == "jmp":
#						self.window().updateStatusBar("Jump to ...")
					
			self.itemOld = item
		
		# Call the original method to ensure default behavior continues
		super().mouseMoveEvent(event)
		
	def on_double_click(self, row, col):
		if col in range(2):
#			self.toggleBPOn(row)
			# bp = self.driver.getTarget().BreakpointCreateByAddress(int(self.item(self.selectedItems()[0].row(), 2).text(), 16))
			if self.item(self.selectedItems()[0].row(), 2) is not None and self.item(self.selectedItems()[0].row(), 1) is not None:
				self.bpHelper.enableBP(self.item(self.selectedItems()[0].row(), 2).text(), not self.item(self.selectedItems()[0].row(), 1).isBPEnabled, False)
			pass
		# elif col == 4:
		# elif col == 4:
		# 	y = self.rowViewportPosition(row)
		# 	x = self.columnViewportPosition(4)
		#
		# 	print(f'y: {y} / {QPoint(x, y)} / {self.viewport().mapToGlobal(QPoint(x, y))} / {self.verticalHeader().sectionPosition(row)}')
		elif col == 5:
			lib.utils.setStatusBar(f"Editing data @: {str(self.item(self.selectedItems()[0].row(), 2).text())}")
		elif col in range(3, 5):
			if self.item(self.selectedItems()[0].row(), 3) != None:
				# arrJumpMnemonics = ("call", "jmp", "jne", "jz", "je", "jnz", "jle", "jl", "jge", "jg")
				if self.item(self.selectedItems()[0].row(), 3).text().startswith(JMP_MNEMONICS): #("call", "jmp", "jne", "jz", "je", "jnz", "jle", "jl", "jge", "jg")):
					jumpAddr = str(self.item(self.selectedItems()[0].row(), 4).text())
					self.parent.locationStack.pushLocation(str(self.item(self.selectedItems()[0].row(), 2).text()))
					self.parent.locationStack.pushLocation(jumpAddr)
					self.parent.viewAddress(jumpAddr)
					# newPC = str(gotoDlg.txtInput.text())
					# lib.utils.setStatusBar(f"Go to address: {newPC}")
					# self.window().txtMultiline.viewAddress(newPC)
			
	def contextMenuEvent(self, event):
		if len(self.selectedItems()) <= 0:
			return
		if self.item(self.selectedItems()[0].row(), 1) != None:
			if self.item(self.selectedItems()[0].row(), 1).isBPEnabled:
				self.actionEnableBP.setText("Disable Breakpoint")
			else:
				self.actionEnableBP.setText("Enable Breakpoint")
			self.actionEnableBP.setData(self.item(self.selectedItems()[0].row(), 1).isBPEnabled)
			
			self.actionShowMemoryFor.setText("Show memory for:")
			self.actionShowMemoryFor.setEnabled(False)
			self.actionShowMemoryFor.setData("")
			if self.item(self.selectedItems()[0].row(), 4) != None:
				operandsText = self.quickToolTip.getOperandsText(self.item(self.selectedItems()[0].row(), 4).text())
				if operandsText != "":
					self.actionShowMemoryFor.setText("Show memory for: " + operandsText)
					self.actionShowMemoryFor.setEnabled(True)
					self.actionShowMemoryFor.setData(operandsText)
			
		self.context_menu.exec(event.globalPos())
	
	def handle_editHexValue(self):
		print(f"handle_editHexValue => ")
		pass
		
	def deleteBP_clicked(self):
		self.bpHelper.deleteBP(self.item(self.selectedItems()[0].row(), 2).text())
		pass
		
	def deleteBP(self, address):
		for row in range(self.rowCount()):
#			print(f'CHECKING BREAKPOINT AT ADDRESS: {self.item(row, 3).text()}')
			if self.item(row, 2) != None and self.item(row, 2).text().lower() == address.lower():
#				self.toggleBPOn(row, updateBPWidget)
				self.item(row, 1).setBPOn(False)
				break
		
	def getSelItemText(self, col):
		if self.item(self.selectedItems()[0].row(), col) != None:
			return self.item(self.selectedItems()[0].row(), col).text()
		else:
			return ""
	
	def handle_findReferences(self):
		address = self.getSelItemText(2)
		self.window().start_findReferencesWorker(address)
		
	def handle_showMemoryFor(self):
		sender = self.sender()  # get the sender object
		if isinstance(sender, QAction):
			action = sender  # it's the QAction itself
		else:
			# Find the QAction within the sender (e.g., QMenu or QToolBar)
			action = sender.findChild(QAction)
		self.window().tabWidgetMain.setCurrentIndex(2)
		# print(f"action ===============>>>>>>>>>>>> {action.data()}")
		addr = self.quickToolTip.get_memory_address(self.driver.debugger, action.data())
		# print(f"GETTING Memory for 0x{addr:X}")
		lib.utils.setStatusBar(f"Showing memory for: 0x{addr:X}")
		# self.window().updateStatusBar(f"Showing memory for: 0x{addr:X} ...")
		self.doReadMemory(addr)
#		print(f"Triggering QAction: {action.text()}")

	def handle_RememberLocBlack(self):
		if self.item(self.selectedItems()[0].row(), 2) != None:
			self.item(self.selectedItems()[0].row(), 0).setForeground(QBrush(QColor("black")))

			logDbgC(f"Foreground: {self.item(self.selectedItems()[0].row(), 0).foreground()} / {self.item(self.selectedItems()[0].row(), 0).foreground().color().name()}")

	def handle_RememberLoc(self):
		logDbgC(f"handle_RememberLoc ...")
		if self.item(self.selectedItems()[0].row(), 2) != None:
			arrRememberedLocs[self.getSelItemText(2)] = {"id": len(arrRememberedLocs), "address": self.getSelItemText(2), "opcode": self.getSelItemText(3), "params": self.getSelItemText(4), "hex": self.getSelItemText(5), "data": self.getSelItemText(6), "comment": self.getSelItemText(7)}
			self.setBGColor(self.selectedItems()[0].row(), True, QColor("yellow"), range(1), QColor("black"))
			address = self.getSelItemText(2)
			logDbg(f"Remember Location ... {address}")
			if self.item(self.selectedItems()[0].row(), 0).text().endswith(">"):
				self.item(self.selectedItems()[0].row(), 0).setText(self.item(self.selectedItems()[0].row(), 0).text() + "I")
				self.window().handle_loadRememberLocation("TestLoc", self.getSelItemText(3), self.getSelItemText(5), self.getSelItemText(4), self.getSelItemText(2), self.getSelItemText(7))
			elif not self.item(self.selectedItems()[0].row(), 0).text().endswith("I"):
				self.item(self.selectedItems()[0].row(), 0).setText("I")
				self.window().handle_loadRememberLocation("TestLoc", self.getSelItemText(3), self.getSelItemText(5), self.getSelItemText(4), self.getSelItemText(2), self.getSelItemText(7))
			print(arrRememberedLocs[self.getSelItemText(2)])
		pass
			
	def doReadMemory(self, address, size = 0x100):
		self.window().tabWidgetDbg.setCurrentWidget(self.window().tabMemory)
		self.window().tblHex.txtMemAddr.setText(hex(address))
		self.window().tblHex.txtMemSize.setText(hex(size))
		try:
#           global debugger
#			self.handle_readMemory(self.driver.debugger, int(self.window().tblHex.txtMemAddr.text(), 16), int(self.window().tblHex.txtMemSize.text(), 16))
			self.window().tblHex.handle_readMemory(self.driver.debugger, int(self.window().tblHex.txtMemAddr.text(), 16), int(self.window().tblHex.txtMemSize.text(), 16))
		except Exception as e:
			print(f"Error while reading memory from process: {e}")
			
	def toggleBPOn(self, row, updateBPWidget = True):
#		print(f'TOGGLE BP: {self.item(row, 3).text()}')
		if self.item(row, 1) != None:
			item = self.item(row, 1)
			item.toggleBPOn()
			if updateBPWidget:
				self.sigBPOn.emit(self.item(row, 2).text(), item.isBPOn)
		pass
		
	def toggleBPAtAddress(self, address, updateBPWidget = True):
		for row in range(self.rowCount()):
#			print(f'CHECKING BREAKPOINT AT ADDRESS: {self.item(row, 3).text()}')
			if self.item(row, 3) != None and self.item(row, 2).text() == address:
				self.toggleBPOn(row, updateBPWidget)
				break
		pass
	
	def enableBP(self, address, enabled = True):
		for row in range(self.rowCount()):
#			print(f'CHECKING BREAKPOINT AT ADDRESS: {self.item(row, 3).text()}')
			if self.item(row, 2) != None and self.item(row, 2).text().lower() == address.lower():
#				self.toggleBPOn(row, updateBPWidget)
				self.item(row, 1).enableBP(enabled)
				break
		
	def setBPAtAddress(self, address, on = True, updateBPWidget = True):
		for row in range(self.rowCount()):
			if self.item(row, 2) != None and self.item(row, 2).text() == address:
				if self.item(row, 1) != None:
					self.item(row, 1).setBPOn(on)
					if updateBPWidget:
						self.sigBPOn.emit(self.item(row, 2).text(), on)
					break
		pass
		
	def removeBPAtAddress(self, address):
		for row in range(self.rowCount()):
			if self.item(row, 2) != None and self.item(row, 2).text() == address:
				if self.item(row, 1) != None:
					self.item(row, 1).setBPOn(False)
	#				if updateBPWidget:
	#					self.sigBPOn.emit(self.item(row, 3).text(), on)
					break
		pass
		
	def resetContent(self):
		self.setRowCount(0)
			
	def addRow(self, lineNum, address, instr, args, comment, data, dataNg, rip = ""):
		currRowCount = self.rowCount()
		self.setRowCount(currRowCount + 1)
		
		item = DisassemblyImageTableWidgetItem()
		
		self.addItem(currRowCount, 0, ('>' if rip == address else '') + ('I' if False else ''))
		self.setItem(currRowCount, 1, item)
		self.addItem(currRowCount, 2, address)
		self.addItem(currRowCount, 3, instr)
		self.addItem(currRowCount, 4, args)
		self.addItem(currRowCount, 5, data)
		self.addItem(currRowCount, 6, dataNg)
		self.addItem(currRowCount, 7, comment)
		
		self.setRowHeight(currRowCount, 14)
		# print(f"address: {address}")
		return item
		
		
	def addItem(self, row, col, txt):
		
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		if col != 5:
			item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
		
		# Insert the items into the row
		self.setItem(row, col, item)
		
	def scrollToRow(self, row):
		allHeight = 0
		for i in range(self.rowCount()):
			# logDbgC(f"self.rowHeight({i}) => {self.rowHeight(i)}....")
			allHeight += self.rowHeight(i)
			if i == row:
				break
		allHeight -= (self.viewport().height() / 2) + (self.rowHeight(1) / 2)
		# logDbgC(f"allHeight: {allHeight} / row: {row}")
		self.verticalScrollBar().setValue(int(allHeight))
# 		if self.rowCount() >= 1:
# 			row_to_scroll = row + self.symbolCount
# 			scroll_value = (row_to_scroll - self.viewport().height() / (2 * self.rowHeight(1))) * self.rowHeight(1)
# #			print(f'scroll_value => {scroll_value}')
# 			self.verticalScrollBar().setValue(int(scroll_value))
# #			print(f'self.verticalScrollBar().value() => {self.verticalScrollBar().value()}')
# 			QApplication.processEvents()
# 			# self.act = QAction("onScroll")

		
class AssemblerTextEdit(QWidget):
	
	table = None
	locationStack = LocationStack()
	
	def resetContent(self):
		self.table.resetContent()
		self.table.symbolCount = 0
	
	def appendAsmSymbol(self, addr, symbol):
		# Define the text for the spanning cell
		text = symbol
		
		table_widget = self.table
		# Get the row count
		row_count = table_widget.rowCount()
		
		# Insert a new row
		table_widget.insertRow(row_count)
		
		# Create a spanning cell item
		item = QTableWidgetItem(f'{text}')
		item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
		item.setBackground(QColor(64, 0, 255, 96))
		item.setForeground(QColor("black"))
		# Set the item to span all columns
		table_widget.setSpan(row_count, 0, 1, table_widget.columnCount())  # Adjust row and column indices as needed
		# Set the item in the table
		table_widget.setItem(row_count, 0, item)
		self.table.symbolCount += 1

		# row_index = item.row()  # Get the row of the item
		# height = table_widget.verticalHeader().sectionSize(row_index)
		# logDbg(f"Row height: {height}")
		pass
		
	def appendAsmText(self, addr, instr, args, comment, data, dataNg, addLineNum = True, rip = "", lineNo = -1):
#		if addLineNum:
#			self.table.addRow(0, addr, instr, args, comment, data, rip)
#		else:
		item = self.table.addRow(0, addr, instr, args, comment, data, dataNg, rip)
		self.table.item(item.row(), 0).setText(str(lineNo))
		# item.setBPOn()
		# row_index = item.row()  # Get the row of the item
		# height = self.table.verticalHeader().sectionSize(row_index)
		# logDbg(f"Row height: {height}")

			
	def setTextColor(self, color = "black", lineNum = False):
		pass
	
	def getAddressFromSelected(self):
		if self.table.selectedItems()[0].row() != None and self.table.item(self.table.selectedItems()[0].row(), 2) != None:
			return self.table.item(self.table.selectedItems()[0].row(), 2).text()
		return None
	
	def pushAddressFromSelected(self):
		addrSel = self.getAddressFromSelected()
		if addrSel != None:
			self.locationStack.pushLocation(addrSel)

	def viewCurrentAddress(self):
		# for row in range(self.table.rowCount()):
		# 	if self.table.item(row, 2) != None:
		# 		if self.table.item(row, 2).text().lower() == address.lower():
					#					self.table.item(row, 0).setText('>')
		self.table.setFocus(Qt.FocusReason.NoFocusReason)
		self.table.selectRow(self.currentPCRow)
		self.table.scrollToRow(self.currentPCRow)
		# break
		# if pushLocation:
		# 	self.locationStack.pushLocation(address.lower())

	def viewAddress(self, address, pushLocation = True):
		for row in range(self.table.rowCount()):
			if self.table.item(row, 2) != None:
				if self.table.item(row, 2).text().lower() == address.lower():
#					self.table.item(row, 0).setText('>')
					self.table.setFocus(Qt.FocusReason.NoFocusReason)
					self.table.selectRow(row)
					self.table.scrollToRow(row)
					break
		if pushLocation:
			self.locationStack.pushLocation(address.lower())
	
	currentPCRow = -1
	def clearPC(self):
		logDbgC(f"clearPC ...")
		if self.table.item(self.currentPCRow, 0) != None:
			if self.table.item(self.currentPCRow, 0).text().endswith("I"):
				self.table.item(self.currentPCRow, 0).setText('I')
			else:
				if self.table.item(self.currentPCRow, 0).text().isdigit():
					pass
				else:
					self.table.item(self.currentPCRow, 0).setText('')
			curRememberLoc = arrRememberedLocs.get(self.table.item(self.currentPCRow, 2).text())
			if curRememberLoc is not None:
				self.table.setBGColor(self.currentPCRow, False, QColor(220, 220, 255, 0), range(1, 8))
				self.table.item(self.currentPCRow, 0).setForeground(QColor("black"))
			else:
				self.table.setBGColor(self.currentPCRow, False)
		pass
		
	def setPC(self, pc, pushLocation = False):
		logDbgC(f"pc: {getAddrStr(pc)}")
		if isinstance(pc, str):
			currentPC = pc.lower()
		else:
			currentPC = hex(pc).lower()

		# logDbgC(f"setPC: {currentPC} ({pc})")
		for row in range(self.table.rowCount()):
			if self.table.item(row, 2) != None:
				if self.table.item(row, 2).text().lower() == currentPC:
					self.currentPCRow = row
					# self.table.item(row, 0).setText('>')
					# logDbgC(f"setPC => row: {row}")
					self.table.setFocus(Qt.FocusReason.NoFocusReason)
					self.table.selectRow(row)
					self.table.scrollToRow(row)

					# self.viewAddress()
					self.table.setBGColor(row, True)
				else:
					if self.table.item(row, 0).text().isdigit():
						pass
					else:
						self.table.item(row, 0).setText('')
					self.table.setBGColor(row, False, QColor(220, 220, 255, 0), range(1, 8))

				curRememberLoc = arrRememberedLocs.get(self.table.item(row, 2).text())
				if curRememberLoc is not None:
					self.table.setBGColor(row, True, QColor("yellow"), range(1), QColor("black"))
					if not self.table.item(row, 0).text().endswith('I'):
					# 	self.table.item(row, 0).setText(self.table.item(row, 0).text())
					# else:
						self.table.item(row, 0).setText(self.table.item(row, 0).text() + 'I') #  + 'I'
						self.table.item(row, 0).setForeground(QColor("black"))
		
		if pushLocation:
			self.locationStack.pushLocation(currentPC)
		
	def enableBP(self, address, enabled = True):
		self.table.enableBP(address, enabled)
		
	def deleteBP(self, address):
		self.table.deleteBP(address)
		pass
		
	driver = None
	
	def __init__(self, driver, bpHelper):
		super().__init__()
		self.driver = driver
		self.setLayout(QHBoxLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)
		
		self.frame = QFrame()
		self.frame.setContentsMargins(0, 0, 0, 0)
		
		self.vlayout = QHBoxLayout()
		self.frame.setLayout(self.vlayout)
		
		self.table = DisassemblyTableWidget(self.driver, bpHelper, self)
		self.table.setContentsMargins(0, 0, 0, 0)
		self.vlayout.addWidget(self.table)
		
		self.vlayout.setSpacing(0)
		self.vlayout.setContentsMargins(0, 0, 0, 0)
		
		self.frame.setFrameShape(QFrame.Shape.NoFrame)
		self.frame.setFrameStyle(QFrame.Shape.NoFrame)
		self.frame.setContentsMargins(0, 0, 0, 0)
		
		self.widget = QWidget()
		self.widget.setContentsMargins(0, 0, 0, 0)
		self.layFrame = QHBoxLayout()
		self.layFrame.setContentsMargins(0, 0, 0, 0)
		self.layFrame.addWidget(self.frame)
		self.widget.setLayout(self.layFrame)
		
		self.layout().addWidget(self.widget)