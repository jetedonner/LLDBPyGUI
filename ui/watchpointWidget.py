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

from ui.assemblerTextEdit import *
from ui.dialogs.dialogHelper import *

from dbg.watchpointHelper import *

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
		self.layout().addWidget(self.tblWatchpoints)
		self.layCtrls = QHBoxLayout()
		self.lblType = QLabel("Type:")
		self.layCtrls.addWidget(self.lblType)
		self.optVariable = QRadioButton("Variable")
		self.optVariable.setChecked(True)
		self.optVariable.clicked.connect(self.optvariable_clicked)
		self.layCtrls.addWidget(self.optVariable)
		self.optAddress = QRadioButton("Address")
		self.optAddress.clicked.connect(self.optaddress_clicked)
		self.layCtrls.addWidget(self.optAddress)
#		self.lblAddrVar = QLabel("Variable:")
#		self.layCtrls.addWidget(self.lblAddrVar)
		self.txtMemoryAddress = QLineEdit()
		self.txtMemoryAddress.setPlaceholderText("Variable name ...")
		self.layCtrls.addWidget(self.txtMemoryAddress)
		self.cmdAddWatchpoint = QPushButton("Add Watchpoint")
		self.cmdAddWatchpoint.clicked.connect(self.addWatchpoint_clicked)
		self.layCtrls.addWidget(self.cmdAddWatchpoint)
		self.wgtCtrls = QWidget()
		self.wgtCtrls.setLayout(self.layCtrls)
		self.layout().addWidget(self.wgtCtrls)
	
	def optvariable_clicked(self):
#		self.lblAddrVar.setText("Variable:")
		self.forVariable = True
		self.txtMemoryAddress.setPlaceholderText("Variable name ...")
		
	def optaddress_clicked(self):
#		self.lblAddrVar.setText("Address:")
		self.forVariable = False
		self.txtMemoryAddress.setPlaceholderText("Memory address ...")
		
	def addWatchpoint_clicked(self):
		print(f"addWatchpoint_clicked")
		if self.forVariable:
			self.wpHelper.setWatchpointForVariable(self.txtMemoryAddress.text())
		else:
			self.wpHelper.setWatchpointForExpression(self.txtMemoryAddress.text())
		
	def reloadWatchpoints(self, initTable = True):
		self.tblWatchpoints.reloadWatchpoints(initTable)
		
class WatchpointsTableWidget(QTableWidget):
	
	wpsEnabled = {}
	ommitCellChanged = False
	
	def __init__(self, driver, workerManager):
		super().__init__()
		self.driver = driver
		self.workerManager = workerManager
		self.setHelper = SettingsHelper()
#		self.driver.handleCommand("command script add -h '(lldbinit) The breakpoint callback function (auto).' --function breakpointTableWidget.breakpointHandlerAuto bpcbauto")
		
		self.initTable()
		self.context_menu = QMenu(self)
		self.actionEnableWP = self.context_menu.addAction("Enable / Disable Watchpoint")
		self.actionEnableWP.triggered.connect(self.handle_enableWP)
		self.actionDeleteWP = self.context_menu.addAction("Delete Watchpoint")
		self.actionDeleteWP.triggered.connect(self.handle_deleteWP)
		self.context_menu.addSeparator()
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
#		self.cellChanged.connect(self.item_changed_handler)
		
#		actionCopyInstruction = self.context_menu.addAction("Copy instruction")
#		actionCopyHex = self.context_menu.addAction("Copy hex value")
#		self.context_menu.addSeparator()
#		actionFindReferences = self.context_menu.addAction("Find references")
#		self.actionShowMemory = self.context_menu.addAction("Show memory")
#		
		
	def initTable(self):
		self.setColumnCount(9)
		self.setColumnWidth(0, 48)
		self.setColumnWidth(1, 32)
		self.setColumnWidth(2, 128)
		self.setColumnWidth(3, 128)
		self.setColumnWidth(4, 128)
		self.setColumnWidth(5, 128)
		self.setColumnWidth(6, 32)
		self.setColumnWidth(7, 48)
		self.setColumnWidth(8, 256)
#		self.setColumnWidth(5, 324)
#		self.setColumnWidth(6, 304)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.horizontalHeader().setHighlightSections(False)
		self.setHorizontalHeaderLabels(['State', '#', 'Address', 'Size', 'Spec', 'Type', 'Hit', 'Ignore', 'Condition'])#, 'Instruction', 'Hex', 'Comment'])
		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(3).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(4).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(6).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(7).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(8).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
#		self.horizontalHeaderItem(6).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
		self.setFont(ConfigClass.font)
#		
		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
#		self.cellDoubleClicked.connect(self.on_double_click)
#		self.addRow(True, 1, "0x10000", "noname", 0, "nocond")
		pass
		
	oldBPName = ""
	
	def resetContent(self):
		self.setRowCount(0)
		
#	def on_double_click(self, row, col):
#		if col == 3:
#			self.oldBPName = self.item(row, 3).text()
#		elif col == 2:
##			self.oldBPName = self.item(row, 3).text()
#			self.window().txtMultiline.viewAddress(self.item(row, 2).text())
#			pass
#		pass
		
	def contextMenuEvent(self, event):
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
			if col == 7: # Name changed
				target = self.driver.getTarget()
				wpFound = False
				for i in range(target.GetNumWatchpoints()):
					wp_cur = target.GetWatchpointAtIndex(i)
					if "#" + str(wp_cur.GetID()) == self.item(self.selectedItems()[0].row(), 1).text():
						wp_cur.SetIgnoreCount(int(self.item(self.selectedItems()[0].row(), 7).text()))
						break
			elif col == 8: # Name changed
				target = self.driver.getTarget()
				wpFound = False
				for i in range(target.GetNumWatchpoints()):
					wp_cur = target.GetWatchpointAtIndex(i)
					if "#" + str(wp_cur.GetID()) == self.item(self.selectedItems()[0].row(), 1).text():
						wp_cur.SetCondition(self.item(self.selectedItems()[0].row(), 8).text())
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
		self.wpsEnabled[wp.GetID()] = wp.IsEnabled()
		self.addRow(wp.IsEnabled(), wp.GetID(), hex(wp.GetWatchAddress()), hex(wp.GetWatchSize()), wp.GetWatchSpec(), ("r" if wp.IsWatchingReads() else "") + ("" if wp.IsWatchingReads() and wp.IsWatchingWrites() else "") + ("w" if wp.IsWatchingWrites() else ""), wp.GetHitCount(), wp.GetIgnoreCount(), wp.GetCondition())
		
		
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
			
		self.updateRow(newEnabled, wp.GetID(), hex(wp.GetWatchAddress()), hex(wp.GetWatchSize()), wp.GetWatchSpec(), ("r" if wp.IsWatchingReads() else "") + ("" if wp.IsWatchingReads() and wp.IsWatchingWrites() else "") + ("w" if wp.IsWatchingWrites() else ""), wp.GetHitCount(), wp.GetIgnoreCount(), wp.GetCondition())
		
	def updateRow(self, state, num, address, size, spec, name, hitcount, ignore, condition):
		self.ommitCellChanged = True
		
		for i in range(self.rowCount()):
			if self.item(i, 1).text() == "#" + str(num):
				if not state:
					self.item(i, 0).setIcon(ConfigClass.iconEyeGrey)
				else:
					self.item(i, 0).setIcon(ConfigClass.iconEyeRed)
#				self.item(i, 0).enableBP(state)
				self.item(i, 2).setText(str(address))
				self.item(i, 3).setText(str(size))
				self.item(i, 4).setText(str(spec))
				self.item(i, 5).setText(str(name))
				self.item(i, 6).setText(str(hitcount))
				self.item(i, 7).setText(str(ignore))
				self.item(i, 8).setText("" if condition == None else str(condition))
				break
		self.ommitCellChanged = False
		
	def addRow(self, state, num, address, size, spec, name, hitcount, ignore, condition):
		self.ommitCellChanged = True
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
		self.addItem(currRowCount, 4, str(spec))
		self.addItem(currRowCount, 5, str(name))
		self.addItem(currRowCount, 6, str(hitcount))
		self.addItem(currRowCount, 7, str(ignore))
		self.addItem(currRowCount, 8, "" if condition == None else str(condition))
		self.setRowHeight(currRowCount, 18)
		self.ommitCellChanged = False
		
	def addItem(self, row, col, txt):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		if col != 5 and col != 7 and col != 8:
			item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
			
		# Insert the items into the row
		self.setItem(row, col, item)