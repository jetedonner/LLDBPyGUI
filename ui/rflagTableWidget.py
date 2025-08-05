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

from prettyflags import pfl_cmd
from ui.baseTableWidget import *
from config import *
from ui.helper.dbgOutputHelper import logDbgC, get_main_window, DebugLevel


class RFlagWidget(QWidget):
	def __init__(self,parent=None, driver=None):
		super().__init__(parent)

		self.setContentsMargins(0, 0, 0, 0)
		self.tblRFlag = RFlagTableWidget()
		self.setLayout(QVBoxLayout())
		# self.wdtLabel = QLabel("rFlags / eFlags: ")
		# self.layout().addWidget(self.wdtLabel)
		self.layout().addWidget(self.tblRFlag)
		self.layout().setContentsMargins(0, 0, 0, 0)
		if driver is not None:
			self.tblRFlag.loadRFlags(driver.debugger)
		# self.wdtLabel.setText(
		# 	"rFlags / eFlags: ")  # + hex(self.tblRFlag.rflags_value) + " / " + format(self.tblRFlag.rflags_value, 'b') + " / " + pfl_cmd(get_main_window().driver.debugger, "", res, []))
		# 	# res = 0
		# 	# self.wdtLabel.setText("rFlags / eFlags: ")# + hex(self.tblRFlag.rflags_value) + " / " + format(self.tblRFlag.rflags_value, 'b') + " / " + pfl_cmd(get_main_window().driver.debugger, "", res, []))
		# 	# self.tblRFlag.addRow("--- QUICK ---", "--- FLAG ---", "--- INFOS ---")
		# 	# self.tblRFlag.addRow("int", str(self.tblRFlag.rflags_value), "")
		# 	# self.tblRFlag.addRow("hex", hex(self.tblRFlag.rflags_value), "")
		# 	# self.tblRFlag.addRow("binary", format(self.tblRFlag.rflags_value, 'b'), "")
		# 	# self.tblRFlag.addRow("quick", pfl_cmd(get_main_window().driver.debugger, "", res, []), "")
		# 	# logDbgC(f"rFlags / eFlags:\n- Unsigned: {hex(self.tblRFlag.rflags_value)} / {self.tblRFlag.rflags_value}\n- Binary: " + format(self.tblRFlag.rflags_value, 'b') + "\n- Flags: " + pfl_cmd(get_main_window().driver.debugger, "", res, []))

class RFlagTableWidget(BaseTableWidget):

	rflags_value = 0x0

	def __init__(self):
		super().__init__()
		self.context_menu = QMenu(self)
#		actionToggleBP = self.context_menu.addAction("Toggle Breakpoint")
#		actionToggleBP.triggered.connect(self.handle_toggleBP)
#		actionDisableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
#		actionDisableBP.triggered.connect(self.handle_disableBP)
#		
#		self.context_menu.addSeparator()
		self.rflags_value = 0x0

		self.setColumnCount(3)
		self.setColumnWidth(0, 128)
		self.setColumnWidth(1, 196)
		self.setColumnWidth(2, 768)
		self.verticalHeader().hide()
		self.horizontalHeader().hide()
		# self.horizontalHeader().setHighlightSections(False)
		# self.setHorizontalHeaderLabels(['Flag', 'Value', 'Desc'])
		# self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		# self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		# self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.setFont(ConfigClass.font)
		
		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
		self.setMouseTracking(True)
		self.cellDoubleClicked.connect(self.on_double_click)
		self.itemEntered.connect(self.handle_itemEntered)
		self.setContentsMargins(0, 0, 0, 0)

	# def initRFlagsWidget(self):
	# 	tabDet2 = QWidget()
	# 	tabDet2.setContentsMargins(0, 0, 0, 0)
	# 	tblReg2 = RFlagTableWidget()
	# 	tabDet2.tblWdgt = tblReg2
	# 	self.tblRegs.append(tblReg2)
	# 	tabDet2.setLayout(QVBoxLayout())
	# 	tabDet2.layout().addWidget(tblReg2)
	# 	tabDet2.layout().setContentsMargins(0, 0, 0, 0)
	# 	self.tabWidgetReg.addTab(tabDet2, "rFlags/eFlags")
	# 	tblReg2.loadRFlags(self.driver.debugger)
	# 	pass

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

		self.rflags_value = rflags_reg.GetValueAsUnsigned()
		# rflags_value = self.rflags_value
		logDbgC(f"rflags_value: {hex(self.rflags_value)}", DebugLevel.Verbose)

		# flags = []

		res = 0
		# self.wdtLabel.setText(
		# 	"rFlags / eFlags: ")  # + hex(self.tblRFlag.rflags_value) + " / " + format(self.tblRFlag.rflags_value, 'b') + " / " + pfl_cmd(get_main_window().driver.debugger, "", res, []))
		self.addRow("FLAG OVERVIEW:", "", "")
		self.addRow("--- DATA TYPE ---", "--- VALUE ---", "--- INFOS ---")
		self.addRow("int", str(self.rflags_value), "Complete Flag with all bits as INT")
		self.addRow("hex", hex(self.rflags_value), "Complete Flag with all bits as HEX")
		self.addRow("binary", format(self.rflags_value, 'b'), "Complete Flag with all bits as BINARY")
		self.addRow("quick", pfl_cmd(get_main_window().driver.debugger, "", res, []), "Quickview all flags")
		logDbgC(
			f"rFlags / eFlags:\n- Unsigned: {hex(self.rflags_value)} / {self.rflags_value}\n- Binary: " + format(
				self.rflags_value, 'b') + "\n- Flags: " + pfl_cmd(get_main_window().driver.debugger, "", res,
																		   []), DebugLevel.Verbose )
		logDbgC(f"RFLAGS: 0x{self.rflags_value:016x}", DebugLevel.Verbose)

		self.addRow("", "", "")
		self.addRow("FLAG DETAILS:", "", "")
		self.addRow("--- FLAG NAME ---", "--- OPTION ---", "--- DESCRIPTION ---")
		# Define the flags and their bit positions
		# (Bit 0 to 21 are the most common ones to check)
		if (self.rflags_value >> 0) & 1:
			# flags.append("CF (Carry)")
			self.addRow("CF", "Carry", "=1 > CY (Carry) / =0 > NC (No Carry) - Mask: 0x0001")
		else:
			# flags.append("NC (No Carry)")
			self.addRow("NC", "No Carry", "=1 > CY (Carry) / =0 > NC (No Carry) - Mask: 0x0001")

		# Bit 1 is reserved and always 1
		# if (rflags_value >> 1) & 1: flags.append("1 (Reserved)")

		if (self.rflags_value >> 2) & 1:
			# flags.append("PF (Parity Even)")
			self.addRow("PF", "Parity Even", "=1 > PE (Parity Even) / =0 > PO (Parity Odd) - Mask: 0x0004")
		else:
			# flags.append("PO (Parity Odd)")
			self.addRow("PO", "Parity Odd", "=1 > PE (Parity Even) / =0 > PO (Parity Odd) - Mask: 0x0004")

		# Bit 3 is reserved and always 0

		if (self.rflags_value >> 4) & 1:
			# flags.append("AF/NA (Auxiliary Carry)")
			self.addRow("AF", "Auxiliary Carry", "=1 > AC (Auxiliary Carry) / =0 > NA (No Auxiliary Carry) - Mask: 0x0010")
		else:
			# flags.append("NA/AF (No Auxiliary Carry)")
			self.addRow("NA", "No Auxiliary Carry", "=1 > AC (Auxiliary Carry) / =0 > NA (No Auxiliary Carry) - Mask: 0x0010")

		# Bit 5 is reserved and always 0

		if (self.rflags_value >> 6) & 1:
			# flags.append("ZF/NZ (Zero)")
			self.addRow("ZF", "Zero Flag", "=1 > ZR (Zero) / =0 > NZ (Not Zero) - Mask: 0x0040")
		else:
			# flags.append("NZ/ZF (Not Zero)")
			self.addRow("NZ", "Not Zero", "=1 > ZR (Zero) / =0 > NZ (Not Zero) - Mask: 0x0040")

		if (self.rflags_value >> 7) & 1:
			# flags.append("SF/PL (Sign Negative)")
			self.addRow("SF", "Sign Negative", "=1 > NG (Negative) / =0 > PL (Positive) - Mask: 0x0080")
		else:
			# flags.append("PL/FL (Sign Positive)")
			self.addRow("PL", "Sign Positive", "=1 > NG (Negative) / =0 > PL (Positive) - Mask: 0x0080")

		if (self.rflags_value >> 8) & 1:
			# flags.append("TF/NTF (Trap/Single Step)")
			self.addRow("TF", "Trap/Single Step", "Trap flag (single step) - Mask: 0x0100")
		else:
			# flags.append("NTF/TF (No Trap/Single Step)")
			self.addRow("NTF", "No Trap/Single Step", "Trap flag (single step) - Mask: 0x0100")

		if (self.rflags_value >> 9) & 1:
			# flags.append("IF/ID (Interrupt Enable)")
			self.addRow("IF", "Interrupt Enable", "=1 > EI (Enable Interrupt) / =0 > DI (Disable Interrupt) - Mask: 0x0200")
		else:
			# flags.append("ID/IF (Interrupt Disable)")
			self.addRow("ID", "Interrupt Disable", "=1 > EI (Enable Interrupt) / =0 > DI (Disable Interrupt) - Mask: 0x0200")

		if (self.rflags_value >> 10) & 1:
			# flags.append("DF/DU (Direction Down)")
			self.addRow("DF", "Direction Down", "=1 > DN (Down) / =0 > UP (Up) - Mask: 0x0400")
		else:
			# flags.append("DU/DF (Direction Up)")
			self.addRow("DU", "Direction Up", "=1 > DN (Down) / =0 > UP (Up) - Mask: 0x0400")

		if (self.rflags_value >> 11) & 1:
			# flags.append("OF/NO (Overflow)")
			self.addRow("OF", "Overflow", "=1 > OV (Overflow) / =0 > NV (Not Overflow) - Mask: 0x0800")
		else:
			# flags.append("NO/OF (No Overflow)")
			self.addRow("NO", "No Overflow", "=1 > OV (Overflow) / =0 > NV (Not Overflow) - Mask: 0x0800")

		iopl = (self.rflags_value >> 12) & 0x3  # 2 bits
		# flags.append(f"IOPL={iopl}")
		self.addRow("IOPL", f"{iopl}", "Mask: 0x3000")

		if (self.rflags_value >> 14) & 1:
			# flags.append("NT/NNT (Nested Task)")
			self.addRow("NT", "Nested Task", "Mask: 0x4000")
		else:
			# flags.append("NNT/NT (Not Nested Task)")
			self.addRow("NNT", "Not Nested Task", "Mask: 0x4000")

		# Bit 15 is reserved and always 0

		if (self.rflags_value >> 16) & 1: self.addRow("RF", "Resume Flag", "Resume flag (386+ only) - Mask: 0x0001 0000") #flags.append("RF (Resume Flag)")

		if (self.rflags_value >> 17) & 1: self.addRow("VM", "Virtual-8086 Mode", "Virtual 8086 mode flag (386+ only) - Mask: 0x0002 0000") # flags.append("VM (Virtual-8086 Mode)")

		if (self.rflags_value >> 18) & 1: self.addRow("AC", "Alignment Check", "Alignment Check (486+, ring 3) SMAP Access Check (Broadwell+, ring 0-2) - Mask: 0x0004 0000") # flags.append("AC (Alignment Check)")

		if (self.rflags_value >> 19) & 1: self.addRow("VIF", "Virtual Interrupt", "Virtual interrupt flag (Pentium+) - Mask: 0x0008 0000") # flags.append("VIF (Virtual Interrupt)")

		if (self.rflags_value >> 20) & 1: self.addRow("VIP", "Virtual Interrupt Pending", "Virtual interrupt pending (Pentium+) - Mask: 0x0010 0000") # flags.append("VIP (Virtual Interrupt Pending)")

		if (self.rflags_value >> 21) & 1: self.addRow("ID", "ID Flag", "Able to use CPUID instruction (Pentium+) - Mask: 0x0020 0000") # flags.append("ID (ID Flag)")



		# result.AppendMessage(f"RFLAGS: 0x{rflags_value:016x} [{', '.join(flags)}]")
		# logDbgC(f"flags: {flags}")