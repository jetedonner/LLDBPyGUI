#!/usr/bin/env python3
import lldb
import os
import sys
import re
import pyperclip

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets
from ui.baseTableWidget import *
from config import *
from ui.helper.dbgOutputHelper import logDbgC


class RFlagTableWidget(BaseTableWidget):
		
	def __init__(self):
		super().__init__()
		self.context_menu = QMenu(self)
#		actionToggleBP = self.context_menu.addAction("Toggle Breakpoint")
#		actionToggleBP.triggered.connect(self.handle_toggleBP)
#		actionDisableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
#		actionDisableBP.triggered.connect(self.handle_disableBP)
#		
#		self.context_menu.addSeparator()
		
		self.setColumnCount(3)
		self.setColumnWidth(0, 128)
		self.setColumnWidth(1, 196)
		self.setColumnWidth(2, 768)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.horizontalHeader().setHighlightSections(False)
		self.setHorizontalHeaderLabels(['Flag', 'Value', 'Desc'])
		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.setFont(ConfigClass.font)
		
		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
		self.setMouseTracking(True)
		self.cellDoubleClicked.connect(self.on_double_click)
		self.itemEntered.connect(self.handle_itemEntered)
		self.setContentsMargins(0, 0, 0, 0)
		
	def handle_itemEntered(self, item):
#		if item.column() == 1:
#			item.setToolTip(f"Register: {item.tableWidget().item(item.row(), 0).text()}\nValue: {str(int(item.tableWidget().item(item.row(), 1).text(), 16))}")
#		print(f"ITEM ENTERED: {item}")
		pass
		
	def on_double_click(self, row, col):
#		if col in range(3):
#			self.toggleBPOn(row)
##			self.sigBPOn.emit(self.item(self.selectedItems()[0].row(), 3).text(), self.item(self.selectedItems()[0].row(), 1).isBPOn)
		# if col == 1:
		# 	print(f'Memory for Register: {self.item(row, 0).text()} => {self.item(row, col).text()}')
		# 	self.window().doReadMemory(int(self.item(row, col).text(), 16))
		pass
			
	def contextMenuEvent(self, event):
#		for i in dir(event):
#			print(i)
#		print(event.pos())
#		print(self.itemAt(event.pos().x(), event.pos().y()))
#		print(self.selectedItems())
#		self.context_menu.exec(event.globalPos())
		pass
		
	def resetContent(self):
		self.setRowCount(0)
#		for row in range(self.rowCount(), 0):
#			self.removeRow(row)
			
	def addRow(self, flag, value, desc):
		currRowCount = self.rowCount()
		self.setRowCount(currRowCount + 1)
		self.addItem(currRowCount, 0, str(flag))
		self.addItem(currRowCount, 1, str(value))
		self.addItem(currRowCount, 2, str(desc))
		self.setRowHeight(currRowCount, 18)
		
		
	def addItem(self, row, col, txt):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
		
		# Insert the items into the row
		self.setItem(row, col, item)

	def loadRFlags(self, debugger):

		self.resetContent()

		target = debugger.GetSelectedTarget()
		# if not target:
		# 	result.AppendError("No target selected.")
		# 	return

		process = target.GetProcess()
		# if not process:
		# 	result.AppendError("No process running.")
		# 	return

		thread = process.GetSelectedThread()
		# if not thread:
		# 	result.AppendError("No thread selected.")
		# 	return

		frame = thread.GetSelectedFrame()
		# if not frame:
		# 	result.AppendError("No frame selected.")
		# 	return

		rflags_reg = frame.FindRegister("rflags")
		# if not rflags_reg:
		# 	result.AppendError("Could not find rflags register.")
		# 	return

		rflags_value = rflags_reg.GetValueAsUnsigned()

		flags = []

		# Define the flags and their bit positions
		# (Bit 0 to 21 are the most common ones to check)
		if (rflags_value >> 0) & 1:
			flags.append("CF (Carry)")
			self.addRow("CF", "Carry", "")
		else:
			flags.append("NC (No Carry)")
			self.addRow("NC", "No Carry", "")

		# Bit 1 is reserved and always 1
		# if (rflags_value >> 1) & 1: flags.append("1 (Reserved)")

		if (rflags_value >> 2) & 1:
			flags.append("PF (Parity Even)")
			self.addRow("PF", "Parity Even", "")
		else:
			flags.append("PO (Parity Odd)")
			self.addRow("PO", "Parity Odd", "")

		# Bit 3 is reserved and always 0

		if (rflags_value >> 4) & 1:
			flags.append("AF/NA (Auxiliary Carry)")
			self.addRow("AF", "Auxiliary Carry", "")
		else:
			flags.append("NA/AF (No Auxiliary Carry)")
			self.addRow("NA", "No Auxiliary Carry", "")

		# Bit 5 is reserved and always 0

		if (rflags_value >> 6) & 1:
			flags.append("ZF/NZ (Zero)")
			self.addRow("ZF", "Zero Flag", "")
		else:
			flags.append("NZ/ZF (Not Zero)")
			self.addRow("NZ", "Not Zero", "")

		if (rflags_value >> 7) & 1:
			flags.append("SF/PL (Sign Negative)")
			self.addRow("SF", "Sign Negative", "")
		else:
			flags.append("PL/FL (Sign Positive)")
			self.addRow("PL", "Sign Positive", "")

		if (rflags_value >> 8) & 1:
			flags.append("TF/NTF (Trap/Single Step)")
			self.addRow("TF", "Trap/Single Step", "")
		else:
			flags.append("NTF/TF (No Trap/Single Step)")
			self.addRow("NTF", "No Trap/Single Step", "")

		if (rflags_value >> 9) & 1:
			flags.append("IF/ID (Interrupt Enable)")
			self.addRow("IF", "Interrupt Enable", "")
		else:
			flags.append("ID/IF (Interrupt Disable)")
			self.addRow("ID", "Interrupt Disable", "")

		if (rflags_value >> 10) & 1:
			flags.append("DF/DU (Direction Down)")
			self.addRow("DF", "Direction Down", "")
		else:
			flags.append("DU/DF (Direction Up)")
			self.addRow("DU", "Direction Up", "")

		if (rflags_value >> 11) & 1:
			flags.append("OF/NO (Overflow)")
			self.addRow("OF", "Overflow", "")
		else:
			flags.append("NO/OF (No Overflow)")
			self.addRow("NO", "No Overflow", "")

		iopl = (rflags_value >> 12) & 0x3  # 2 bits
		flags.append(f"IOPL={iopl}")

		if (rflags_value >> 14) & 1:
			flags.append("NT/NNT (Nested Task)")
			self.addRow("NT", "Nested Task", "")
		else:
			flags.append("NNT/NT (Not Nested Task)")
			self.addRow("NNT", "Not Nested Task", "")

		# Bit 15 is reserved and always 0

		if (rflags_value >> 16) & 1: flags.append("RF (Resume Flag)")

		if (rflags_value >> 17) & 1: flags.append("VM (Virtual-8086 Mode)")

		if (rflags_value >> 18) & 1: flags.append("AC (Alignment Check)")

		if (rflags_value >> 19) & 1: flags.append("VIF (Virtual Interrupt)")

		if (rflags_value >> 20) & 1: flags.append("VIP (Virtual Interrupt Pending)")

		if (rflags_value >> 21) & 1: flags.append("ID (ID Flag)")

		# result.AppendMessage(f"RFLAGS: 0x{rflags_value:016x} [{', '.join(flags)}]")
		logDbgC(f"flags: {flags}")