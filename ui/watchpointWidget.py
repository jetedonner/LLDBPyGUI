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
from config import *
from lib.settings import *
from dbg.fileInfos import *

from ui.assemblerTextEdit import *
from ui.dialogs.dialogHelper import *

from dbg.watchpointHelper import *
from ui.baseTableWidget import *
#def breakpointHandlerAuto(dummy, frame, bpno, err):
#		print("breakpointHandlerAuto ...")
#		print("YESSSSSSS GETTTTTTTIIIIINNNNNNNGGGGG THERE!!!!!!")

class WatchpointsWidget(QWidget):
	
	wpHelper = None
	forVariable = True
	
	def __init__(self, driver, workerManager):
		super().__init__()
		self.driver = driver
		self.workerManager = workerManager
		self.wpHelper = WatchpointHelper(self.driver)
	
		self.setLayout(QVBoxLayout())
		self.tblWatchpoints = WatchpointsTableWidget(self.driver, self.workerManager)
		self.tblWatchpoints.setContentsMargins(0, 0, 0, 0)
		self.layout().addWidget(self.tblWatchpoints)
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.setContentsMargins(0, 0, 0, 0)
		self.layCtrls = QHBoxLayout()
		self.layCtrls.setContentsMargins(0, 0, 0, 0)
		self.lblType = QLabel("Type:")
		self.lblType.setContentsMargins(0, 0, 0, 0)
		self.layCtrls.addWidget(self.lblType)
		self.optVariable = QRadioButton("Variable")
		self.optVariable.setContentsMargins(0, 0, 0, 0)
		self.optVariable.setChecked(True)
		self.optVariable.clicked.connect(self.optvariable_clicked)
		self.layCtrls.addWidget(self.optVariable)
		self.optAddress = QRadioButton("Expression")
		self.optAddress.setContentsMargins(0, 0, 0, 0)
		self.optAddress.clicked.connect(self.optaddress_clicked)
		self.layCtrls.addWidget(self.optAddress)
#		self.lblAddrVar = QLabel("Variable:")
#		self.layCtrls.addWidget(self.lblAddrVar)
		self.txtMemoryAddress = QLineEdit()
		self.txtMemoryAddress.setStyleSheet("""
			QLineEdit {
				background-color: #282c34; /* Dark background */
				color: #abb2bf; /* Light grey text */
				border: 1px solid #3e4452;
				border-radius: 5px;
				padding: 5px;
				font: 12px 'Courier New';
			}
		""")
		self.txtMemoryAddress.setContentsMargins(0, 0, 0, 0)
		self.txtMemoryAddress.setPlaceholderText("Variable name ...")
		self.txtMemoryAddress.returnPressed.connect(self.addWatchpoint_clicked)
		self.layCtrls.addWidget(self.txtMemoryAddress)
		self.cmdAddWatchpoint = QPushButton("Add Watchpoint")
		self.cmdAddWatchpoint.setContentsMargins(0, 0, 0, 0)
		self.cmdAddWatchpoint.clicked.connect(self.addWatchpoint_clicked)
#		self.layCtrls.addWidget(self.cmdAddWatchpoint)
		self.cmbType = QComboBox()
		self.cmbType.addItems(["read", "write", "read/write"])
		self.cmbType.setContentsMargins(0, 0, 0, 0)
		self.layCtrls.addWidget(self.cmbType)
		self.layCtrls.addWidget(self.cmdAddWatchpoint)
		self.layCtrls.setContentsMargins(0, 0, 0, 0)
		self.wgtCtrls = QWidget()
		self.wgtCtrls.setContentsMargins(0, 0, 0, 0)
		self.wgtCtrls.setLayout(self.layCtrls)
		self.layout().addWidget(self.wgtCtrls)
	
	def optvariable_clicked(self):
#		self.lblAddrVar.setText("Variable:")
		self.forVariable = True
		self.txtMemoryAddress.setPlaceholderText("Variable name ...")
		self.txtMemoryAddress.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
		
	def optaddress_clicked(self):
#		self.lblAddrVar.setText("Address:")
		self.forVariable = False
		self.txtMemoryAddress.setPlaceholderText("Enter Expression ...")
		self.txtMemoryAddress.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
		
	def addWatchpoint_clicked(self):
		print(f"addWatchpoint_clicked")
		if self.forVariable:
			# self.wpHelper.setWatchpointForVariable(self.txtMemoryAddress.text())
			self.watch_var(self.driver.debugger, self.txtMemoryAddress.text(), True, False)
		else:
			self.wpHelper.setWatchpointForExpression(self.txtMemoryAddress.text())
		
	def reloadWatchpoints(self, initTable = True):
		self.tblWatchpoints.reloadWatchpoints(initTable)

	def watch_var(self, debugger, var_name, read = True, write = True):#, command, result, internal_dict):
		target = debugger.GetSelectedTarget()
		process = target.GetProcess()
		thread = process.GetSelectedThread()
		frame = thread.GetSelectedFrame()

		var = frame.FindVariable(var_name)

		if not var.IsValid():
			print(f"Variable '{var_name}' not found.")
			return

		addr = var.GetLoadAddress()
		size = var.GetByteSize()

		errorWP = lldb.SBError()
		wp = target.WatchAddress(addr, size, read, write, errorWP)  # read=True, write=True

		if wp.IsValid():
			print(f"Watchpoint {wp.GetID()} set on '{var_name}' at 0x{addr:x}")
		else:
			print(f"Failed to set watchpoint. ({errorWP})")

		
class WatchpointsTableWidget(BaseTableWidget):
	
	wpsEnabled = {}
	ommitCellChanged = False
	
	def __init__(self, driver, workerManager):
		super().__init__()
		self.driver = driver
		self.workerManager = workerManager
		self.setHelper = SettingsHelper()
		self.wpHelper = WatchpointHelper(self.driver)
#		self.driver.handleCommand("command script add -h '(lldbinit) The breakpoint callback function (auto).' --function breakpointTableWidget.breakpointHandlerAuto bpcbauto")
		
		self.initTable()
		self.context_menu = QMenu(self)
		self.actionEnableWP = self.context_menu.addAction("Enable / Disable Watchpoint")
		self.actionEnableWP.triggered.connect(self.handle_enableWP)
		self.actionDeleteWP = self.context_menu.addAction("Delete Watchpoint")
		self.actionDeleteWP.triggered.connect(self.handle_deleteWP)
		self.context_menu.addSeparator()
		
		self.setContentsMargins(0, 0, 0, 0)
#		actionDeleteBP = self.context_menu.addAction("Delete Breakpoint")
#		actionDeleteBP.triggered.connect(self.handle_deleteBP)
##		actionToggleBP = self.context_menu.addAction("Toggle Breakpoint")
##		actionToggleBP.triggered.connect(self.handle_toggleBP)
#		
#		actionEditCondition = self.context_menu.addAction("Edit condition")
#		actionEditCondition.triggered.connect(self.handle_editCondition)
#		
#		self.context_menu.addSeparator()
#		actionGotoAddress = self.context_menu.addAction("Goto address")
#		actionGotoAddress.triggered.connect(self.handle_gotoAddress)
#		actionCopyAddress = self.context_menu.addAction("Copy address")
#		actionCopyAddress.triggered.connect(self.handle_copyAddress)
#		
#		self.cellDoubleClicked.connect(self.on_double_click)
		self.cellChanged.connect(self.item_changed_handler)
		
#		actionCopyInstruction = self.context_menu.addAction("Copy instruction")
#		actionCopyHex = self.context_menu.addAction("Copy hex value")
#		self.context_menu.addSeparator()
#		actionFindReferences = self.context_menu.addAction("Find references")
#		self.actionShowMemory = self.context_menu.addAction("Show memory")
#		
		
	def initTable(self):
		self.setColumnCount(11)
		self.setColumnWidth(0, 48)
		self.setColumnWidth(1, 32)
		self.setColumnWidth(2, 128)
		self.setColumnWidth(3, 82)
		self.setColumnWidth(4, 100)
		self.setColumnWidth(5, 164)
		self.setColumnWidth(6, 128)
		self.setColumnWidth(7, 32)
		self.setColumnWidth(8, 48)
		self.setColumnWidth(9, 256)
		self.setColumnWidth(10, 224)
#		self.setColumnWidth(5, 324)
#		self.setColumnWidth(6, 304)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.horizontalHeader().setHighlightSections(False)
		self.setHorizontalHeaderLabels(['State', '#', 'Address', 'Size', 'Kind', 'Spec', 'Type', 'Hit', 'Ignore', 'Condition', 'Value'])#, 'Instruction', 'Hex', 'Comment'])
		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(3).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(4).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(6).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(7).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(8).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(9).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(10).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
#		self.horizontalHeaderItem(6).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
		self.setFont(ConfigClass.font)
#		
		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
		self.cellDoubleClicked.connect(self.on_double_click)
#		self.addRow(True, 1, "0x10000", "noname", 0, "nocond")
		pass
		
	oldBPName = ""
	
	def resetContent(self):
		self.setRowCount(0)
		
	def on_double_click(self, row, col):
		if col == 0:
			self.handle_enableWP()
		elif col == 2:
			self.window().doReadMemory(int(self.item(row, 2).text(), 16))
		elif col == 5:
			try:
				memAddr = int(self.item(row, 5).text(), 16)
				self.window().doReadMemory(memAddr)
				pass
			except Exception as e:
				pass
			pass
		pass
		
	def contextMenuEvent(self, event):
		pass
		if self.item(self.selectedItems()[0].row(), 0).isBPEnabled:
			self.actionEnableWP.setText("Disable Watchpoint")
		else:
			self.actionEnableWP.setText("Enable Watchpoint")
			
#		for i in dir(event):
#			print(i)
#			print(event.pos())
#			print(self.itemAt(event.pos().x(), event.pos().y()))
#			print(self.selectedItems())
		self.context_menu.exec(event.globalPos())
		
	def handle_deleteWP(self):
		row = self.selectedItems()[0].row()
		selItem = self.item(row, 1)
		print(f"{selItem.text()[1:]}")
		if self.driver.getTarget().DeleteWatchpoint(int(selItem.text()[1:])):
			self.removeRow(row)
		else:
			print(f"Could not delete Watchpoint #{selItem.text()[1:]}")
		
	def handle_enableWP(self):
#		item.enableBP(state)
		selItem = self.item(self.selectedItems()[0].row(), 0)
		selItem.isBPEnabled = not selItem.isBPEnabled
		if self.item(self.selectedItems()[0].row(), 0).isBPEnabled:
#			self.actionEnableWP.setText("Disable Watchpoint")
#			self.item(self.selectedItems()[0].row(), 0).isBPEnabled
			selItem.setIcon(ConfigClass.iconEyeRed)
		else:
			selItem.setIcon(ConfigClass.iconEyeGrey)
		
	def item_changed_handler(self, row, col):
		if not self.ommitCellChanged:
			if col == 6: # Type changed
				print(f"def item_changed_handler(self, row, col):")
#				self.wpHelper.SetCondition
				target = self.driver.getTarget()
				wpFound = False
				for i in range(target.GetNumWatchpoints()):
					wp_cur = target.GetWatchpointAtIndex(i)
					if "#" + str(wp_cur.GetID()) == self.item(self.selectedItems()[0].row(), 1).text():
						wp_cur.SetCondition(self.item(self.selectedItems()[0].row(), col).text())
						print(f"SETTING TYPE: {wp_cur}")
						break
				pass
			elif col == 8: # Name changed
				target = self.driver.getTarget()
				wpFound = False
				for i in range(target.GetNumWatchpoints()):
					wp_cur = target.GetWatchpointAtIndex(i)
					if "#" + str(wp_cur.GetID()) == self.item(self.selectedItems()[0].row(), 1).text():
						wp_cur.SetIgnoreCount(int(self.item(self.selectedItems()[0].row(), col).text()))
						print(f"SETTING IGNORE-COUNT: {wp_cur}")
						break
			elif col == 9: # Name changed
				target = self.driver.getTarget()
				wpFound = False
				for i in range(target.GetNumWatchpoints()):
					wp_cur = target.GetWatchpointAtIndex(i)
					if "#" + str(wp_cur.GetID()) == self.item(self.selectedItems()[0].row(), 1).text():
						wp_cur.SetCondition(self.item(self.selectedItems()[0].row(), col).text())
						break
			pass
	
	def reloadWatchpoints(self, initTable = True):
		self.workerManager.start_loadWatchpointsWorker(self.handle_loadWatchpointsFinished, self.handle_loadWatchpointValue, self.handle_updateWatchpointValue, initTable)
	
	def handle_loadWatchpointsFinished(self):
#		self.wdtBPsWPs.treBPs.setPC(self.rip)
		pass
		
	def handle_loadWatchpointValue(self, wp):
#		if initTable:
#			self.txtMultiline.table.setBPAtAddress(loadAddr, True, False)
		print(f"wp.IsWatchingReads() => {wp.IsWatchingReads()} and wp.IsWatchingWrites() => {wp.IsWatchingWrites()}")
		self.wpsEnabled[wp.GetID()] = wp.IsEnabled()
		self.addRow(wp.IsEnabled(), wp.GetID(), hex(wp.GetWatchAddress()), hex(wp.GetWatchSize()), WatchpointValueKindString(wp.GetWatchValueKind()), wp.GetWatchSpec(), ("rw" if wp.IsWatchingReads() and wp.IsWatchingWrites() else ("r" if wp.IsWatchingReads() else "") + ("w" if wp.IsWatchingWrites() else "")), wp.GetHitCount(), wp.GetIgnoreCount(), wp.GetCondition())
		
		
	def handle_updateWatchpointValue(self, wp):
#		print(f'wp.GetWatchValueKind() =====================>>>>>>>>>>>>>> {wp.GetWatchValueKind()} / {lldb.eWatchPointValueKindExpression}')
		
		newEnabled = wp.IsEnabled()
		if self.setHelper.getValue(SettingsValues.KeepWatchpointsEnabled) and wp.GetID() in self.wpsEnabled.keys():
			if self.wpsEnabled[wp.GetID()] != newEnabled:
				newEnabled = not newEnabled
				wp.SetEnabled(newEnabled)
			else:
				self.wpsEnabled[wp.GetID()] = newEnabled
				wp.SetEnabled(newEnabled)
			
		print(f"!!!!wp.IsWatchingReads() => {wp.IsWatchingReads()} and wp.IsWatchingWrites() => {wp.IsWatchingWrites()}")
		self.updateRow(newEnabled, wp.GetID(), hex(wp.GetWatchAddress()), hex(wp.GetWatchSize()), WatchpointValueKindString(wp.GetWatchValueKind()), wp.GetWatchSpec(), ("rw" if wp.IsWatchingReads() and wp.IsWatchingWrites() else ("r" if wp.IsWatchingReads() else "") + ("w" if wp.IsWatchingWrites() else "")) , wp.GetHitCount(), wp.GetIgnoreCount(), wp.GetCondition())
		
	def updateRow(self, state, num, address, size, kind, spec, name, hitcount, ignore, condition):
		self.ommitCellChanged = True
		value = ""
		memory = self.getValue(int(address, 16), int(size, 16))
		if memory != None:
			try:
#				condition = memory #.decode('utf-8')
				# Interpret the byte array as an unsigned integer
				value = str(int.from_bytes(memory, byteorder='little', signed=False))
				
			except Exception as e:
				print(f"Exception while converting memory value {memory} to string! {e}")
		rowFound = False
		for i in range(self.rowCount()):
			if self.item(i, 1).text() == "#" + str(num):
				rowFound = True
				self.item(i, 0).isBPEnabled = state
				if not state:
					self.item(i, 0).setIcon(ConfigClass.iconEyeGrey)
				else:
					self.item(i, 0).setIcon(ConfigClass.iconEyeRed)
#				self.item(i, 0).enableBP(state)
				self.item(i, 2).setText(str(address))
				self.item(i, 3).setText(str(size))
				self.item(i, 4).setText(str(kind))
				self.item(i, 5).setText(str(spec))
				self.item(i, 6).setText(str(name))
				self.item(i, 7).setText(str(hitcount))
				self.item(i, 8).setText(str(ignore))
				self.item(i, 9).setText("" if condition == None else str(condition))
				self.item(i, 10).setText(str(value))
				break
		if not rowFound:
			self.addRow(state, num, address, size, kind, spec, name, hitcount, ignore, condition)
		self.ommitCellChanged = False
		

	def addRow(self, state, num, address, size, kind, spec, name, hitcount, ignore, condition):
		self.ommitCellChanged = True
		value = ""
		memory = self.getValue(int(address, 16), int(size, 16))
		if memory != None:
			try:
#				condition = memory.decode('utf-8')
				value = str(int.from_bytes(memory, byteorder='little', signed=False))
			except Exception as e:
				print(f"Exception while converting memory value {memory} to string! {e}")
		currRowCount = self.rowCount()
		self.setRowCount(currRowCount + 1)
		item = DisassemblyImageTableWidgetItem()
		
		item.enableBP(state)
#		item.setIcon(ConfigClass.iconEyeRed)
		if not state:
			item.setIcon(ConfigClass.iconEyeGrey)
		else:
			item.setIcon(ConfigClass.iconEyeRed)
		self.setItem(currRowCount, 0, item)
		self.addItem(currRowCount, 1, "#" + str(num))
		self.addItem(currRowCount, 2, str(address))
		self.addItem(currRowCount, 3, str(size))
		self.addItem(currRowCount, 4, str(kind))
		self.addItem(currRowCount, 5, str(spec))
		self.addItem(currRowCount, 6, str(name))
		self.addItem(currRowCount, 7, str(hitcount))
		self.addItem(currRowCount, 8, str(ignore))
		self.addItem(currRowCount, 9, "" if condition == None else str(condition))
		self.addItem(currRowCount, 10, str(value))
		self.setRowHeight(currRowCount, 18)
		self.ommitCellChanged = False
		
	def addItem(self, row, col, txt):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		if col != 6 and col != 8 and col != 9:
			item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
			
		# Insert the items into the row
		self.setItem(row, col, item)
		
	def getValue(self, address, size):
		error_ref = lldb.SBError()
		process = self.driver.debugger.GetSelectedTarget().GetProcess()
		print(f"self.driver.debugger.GetSelectedTarget().GetProcess() => {self.driver.debugger.GetSelectedTarget().GetProcess()}")
		memory = process.ReadMemory(address, size, error_ref)
		if error_ref.Success():
#			dataTillNull = self.extract_data_until_null(memory)
			return self.extract_data_until_null(memory)
		return None
	
	def extract_data_until_null(self, byte_data):
		null_index = byte_data.find(b'\x00')
		if null_index != -1:
			return byte_data[:null_index + 1]
		else:
			return None