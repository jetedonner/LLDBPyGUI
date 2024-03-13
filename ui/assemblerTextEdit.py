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
from PyQt6 import uic, QtWidgets

from ui.helper.quickToolTip import *
from ui.helper.locationStack import *

from config import *
	
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
	def paint(self, painter, option, index):
		super().paint(painter, option, index)
		
		if option.state & QStyle.StateFlag.State_Selected:# Qt.State_Selected:
			
			brush = QBrush(Qt.GlobalColor.darkYellow)
			# Set custom background color for selected rows
			option.backgroundBrush = brush # Adjust color as desired
		else:
			# Create a temporary QPixmap and fill it with the brush color
			pixmap = QPixmap(option.rect.size())  # Adjust dimensions as needed
			pixmap.fill(Qt.GlobalColor.transparent)
			
			# Convert the QPixmap to a QImage
			image = pixmap.toImage()
			
			painter.drawImage(option.rect, image)#option.background())
		
class DisassemblyTableWidget(QTableWidget):
	
	sigEnableBP = pyqtSignal(str, bool)
	sigBPOn = pyqtSignal(str, bool)
	
	actionShowMemory = None
	quickToolTip = QuickToolTip()
	
	def handle_copyHexValue(self):
		if self.item(self.selectedItems()[0].row(), 5) != None:
			item = self.item(self.selectedItems()[0].row(), 5)
			pyperclip.copy(item.text())
		
	def handle_copyInstruction(self):
		if self.item(self.selectedItems()[0].row(), 3) != None:
			item = self.item(self.selectedItems()[0].row(), 3)
			pyperclip.copy(item.text())
		
	def handle_copyAddress(self):
		if self.item(self.selectedItems()[0].row(), 2) != None:
			item = self.item(self.selectedItems()[0].row(), 2)
			pyperclip.copy(item.text())
		
	def handle_toggleBP(self):
		if self.item(self.selectedItems()[0].row(), 1) != None:
			item = self.item(self.selectedItems()[0].row(), 1)
			item.toggleBPOn()
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
				break
		pass
		
	def handle_editBP(self):
#		self.sigEnableBP.emit(self.item(self.selectedItems()[0].row(), 3).text(), item.isBPEnabled)
		if self.item(self.selectedItems()[0].row(), 2) != None:
			self.window().tabWidgetDbg.setCurrentIndex(2)
			self.window().wdtBPsWPs.tblBPs.setFocus()
			self.window().wdtBPsWPs.tblBPs.selectBPRow(self.item(self.selectedItems()[0].row(), 2).text())
#		pass
		
	def handle_enableBP(self):
		if self.item(self.selectedItems()[0].row(), 1) != None:
			item = self.item(self.selectedItems()[0].row(), 1)
			item.enableBP(not item.isBPEnabled)
#			self.window().wdtBPsWPs.treBPs.enableBPByAddress(self.item(self.selectedItems()[0].row(), 2).text(),  item.isBPEnabled)
		
	def handle_editCondition(self):
		BreakpointHelper().handle_editCondition(self, 2, 5)
		
	def handle_setPC(self):
		if self.item(self.selectedItems()[0].row(), 2) != None:
			dlg = InputDialog("Set new PC", "Please enter address for PC", self.item(self.selectedItems()[0].row(), 2).text())
			if dlg.exec():
				print(f'dlg.txtInput: {dlg.txtInput.text()}')
				
				frame = self.driver.getTarget().GetProcess().GetThreadAtIndex(0).GetFrameAtIndex(0)
				if frame:
					newPC = int(str(dlg.txtInput.text()), 16)
					frame.SetPC(newPC)
					self.window().txtMultiline.setPC(newPC)
#					self.setPC(newPC)
					
	def handle_gotoAddr(self):
		if self.item(self.selectedItems()[0].row(), 2) != None:
			gotoDlg = GotoAddressDialog(self.item(self.selectedItems()[0].row(), 2).text())
			if gotoDlg.exec():
				print(f"GOING TO ADDRESS: {gotoDlg.txtInput.text()}")
				newPC = str(gotoDlg.txtInput.text())
				self.window().txtMultiline.viewAddress(newPC)
			pass
		
	driver = None
	symbolCount = 0
	setIT = False
	def setBGColor(self, row, colored):
		if not colored:
			color = QColor(220, 220, 255, 0)
		else:
			color = QColor(220, 220, 255, 80)
		# Set background color for a specific item
		for i in range(self.columnCount()):
			item = self.item(row, i)  # Replace with desired row and column index
			if item is not None:
				item.setBackground(color)
		
		self.setIT = not self.setIT
		
	def __init__(self, driver, bpHelper):
		super().__init__()
		
		self.driver = driver
		self.bpHelper = bpHelper
		
		self.context_menu = QMenu(self)
		
		self.actionEnableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
		self.actionEnableBP.triggered.connect(self.handle_enableBP)
		self.actionDeleteBP = self.context_menu.addAction("Delete Breakpoint")
		self.actionDeleteBP.triggered.connect(self.deleteBP_clicked)
		self.actionEditBP = self.context_menu.addAction("Edit Breakpoint")
		self.actionEditBP.triggered.connect(self.handle_editBP)
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
		
		self.setColumnCount(7)
		self.setColumnWidth(0, 24)
		self.setColumnWidth(1, 32)
		self.setColumnWidth(2, 108)
		self.setColumnWidth(3, 84)
		self.setColumnWidth(4, 256)
		self.setColumnWidth(5, 324)
		self.setColumnWidth(6, 304)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.horizontalHeader().setHighlightSections(False)
		self.setHorizontalHeaderLabels(['PC', 'BP', 'Address', 'Mnemonic', 'Operands', 'Hex', 'Comment']) # '#', 
		self.horizontalHeaderItem(0).setFont(ConfigClass.font)
		self.horizontalHeaderItem(1).setFont(ConfigClass.font)
		self.horizontalHeaderItem(2).setFont(ConfigClass.font)
		self.horizontalHeaderItem(3).setFont(ConfigClass.font)
		self.horizontalHeaderItem(4).setFont(ConfigClass.font)
		self.horizontalHeaderItem(5).setFont(ConfigClass.font)
		self.horizontalHeaderItem(6).setFont(ConfigClass.font)
		
		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(3).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(4).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(6).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)

		# Usage (assuming you have a created table widget named `table`):
		self.delegate = CustomStyledItemDelegate()
		self.setItemDelegate(self.delegate)		
		
#		self.horizontalHeaderItem(6).setFont(ConfigClass.font)
		self.setFont(ConfigClass.font)
		
		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
		self.setMouseTracking(True)
		self.cellDoubleClicked.connect(self.on_double_click)
		
	itemOld = None
	
	def mouseMoveEvent(self, event):	
		pos = event.pos()
		item = self.itemAt(pos)
		if item != None and self.itemOld != item:
			row, col = item.row(), item.column()
			if col == 4:
#				print(f"Cell: ({row}, {col}), Mouse: ({pos.x()}, {pos.y()})")
				item.setToolTip(self.quickToolTip.getQuickToolTip(item.text(), self.driver.debugger))
			self.itemOld = item
		
		# Call the original method to ensure default behavior continues
		super().mouseMoveEvent(event)
		
	def on_double_click(self, row, col):
		if col in range(2):
#			self.toggleBPOn(row)
			self.bpHelper.enableBP(self.item(self.selectedItems()[0].row(), 2).text(), not self.item(self.selectedItems()[0].row(), 1).isBPEnabled)
		elif col in range(3, 5):
			if self.item(self.selectedItems()[0].row(), 3) != None:
				if self.item(self.selectedItems()[0].row(), 3).text().startswith(("call", "jmp", "jne", "jz", "jnz")):
					jumpAddr = str(self.item(self.selectedItems()[0].row(), 4).text())
					self.window().txtMultiline.locationStack.pushLocation(str(self.item(self.selectedItems()[0].row(), 2).text()))	
					self.window().txtMultiline.locationStack.pushLocation(jumpAddr)
					self.window().txtMultiline.viewAddress(jumpAddr)
			
	def contextMenuEvent(self, event):
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
		self.window().start_findReferencesWorker(address, True)
		
	def handle_showMemoryFor(self):
		sender = self.sender()  # get the sender object
		if isinstance(sender, QAction):
			action = sender  # it's the QAction itself
		else:
			# Find the QAction within the sender (e.g., QMenu or QToolBar)
			action = sender.findChild(QAction)
		print(f"action ===============>>>>>>>>>>>> {action.data()}")
		addr = self.quickToolTip.get_memory_address(self.driver.debugger, action.data())
		print(f"GETTING Memory for {addr}")
		self.doReadMemory(addr)
#		print(f"Triggering QAction: {action.text()}")
			
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
			
	def addRow(self, lineNum, address, instr, args, comment, data, rip = ""):
		currRowCount = self.rowCount()
		self.setRowCount(currRowCount + 1)
		
		item = DisassemblyImageTableWidgetItem()
		
		self.addItem(currRowCount, 0, ('>' if rip == address else ''))
		self.setItem(currRowCount, 1, item)
		self.addItem(currRowCount, 2, address)
		self.addItem(currRowCount, 3, instr)
		self.addItem(currRowCount, 4, args)
		self.addItem(currRowCount, 5, data)
		self.addItem(currRowCount, 6, comment)
		
		self.setRowHeight(currRowCount, 14)
		
		
	def addItem(self, row, col, txt):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
		
		# Insert the items into the row
		self.setItem(row, col, item)
		
	def scrollToRow(self, row):
		if self.rowCount() >= 1:
			row_to_scroll = row + self.symbolCount
			scroll_value = (row_to_scroll - self.viewport().height() / (2 * self.rowHeight(1))) * self.rowHeight(1)
#			print(f'scroll_value => {scroll_value}')
			self.verticalScrollBar().setValue(int(scroll_value))
#			print(f'self.verticalScrollBar().value() => {self.verticalScrollBar().value()}')
			QApplication.processEvents()
		
class AssemblerTextEdit(QWidget):
	
	table = None
	locationStack = LocationStack()
	
	def resetContent(self):
		self.table.resetContent()
	
	def appendAsmSymbol(self, addr, symbol):
		# Define the text for the spanning cell
		text = symbol
		
		table_widget = self.table
		# Get the row count
		row_count = table_widget.rowCount()
		
		# Insert a new row
		table_widget.insertRow(row_count)
		
		# Create a spanning cell item
		item = QTableWidgetItem(f'function: {text}')
		item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
		item.setBackground(QColor(64, 0, 255, 96))
		# Set the item to span all columns
		table_widget.setSpan(row_count, 0, 1, table_widget.columnCount())  # Adjust row and column indices as needed
		
		# Set the item in the table
		table_widget.setItem(row_count, 0, item)
		self.table.symbolCount += 1
		pass
		
	def appendAsmText(self, addr, instr, args, comment, data, addLineNum = True, rip = ""):
#		if addLineNum:
#			self.table.addRow(0, addr, instr, args, comment, data, rip)
#		else:
		self.table.addRow(0, addr, instr, args, comment, data, rip)
			
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
		self.table.item(self.currentPCRow, 0).setText('')
		self.table.setBGColor(self.currentPCRow, False)
		pass
		
	def setPC(self, pc, pushLocation = False):
		currentPC = hex(pc).lower()
		for row in range(self.table.rowCount()):
			if self.table.item(row, 2) != None:
				if self.table.item(row, 2).text().lower() == currentPC:
					self.currentPCRow = row
					self.table.item(row, 0).setText('>')
					self.table.scrollToRow(row)
					self.table.setBGColor(row, True)
				else:
					self.table.item(row, 0).setText('')
					self.table.setBGColor(row, False)
		
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
		
		self.frame = QFrame()
		
		self.vlayout = QHBoxLayout()
		self.frame.setLayout(self.vlayout)
		
		self.table = DisassemblyTableWidget(self.driver, bpHelper)
		
		self.vlayout.addWidget(self.table)
		
		self.vlayout.setSpacing(0)
		self.vlayout.setContentsMargins(0, 0, 0, 0)
		
		self.frame.setFrameShape(QFrame.Shape.NoFrame)
		self.frame.setFrameStyle(QFrame.Shape.NoFrame)
		self.frame.setContentsMargins(0, 0, 0, 0)
		
		self.widget = QWidget()
		self.layFrame = QHBoxLayout()
		self.layFrame.addWidget(self.frame)
		self.widget.setLayout(self.layFrame)
		
		self.layout().addWidget(self.widget)