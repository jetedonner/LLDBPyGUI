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

#from ui.customQt.QClickLabel import *
from ui.assemblerTextEdit import *
from ui.dialogs.dialogHelper import *
#from dbg.helper.breakpointHelper import *
#from ui.addBreakpointDialog import *
#from ui.breakpointTreeView import *

#def breakpointHandlerAuto(dummy, frame, bpno, err):
#		print("breakpointHandlerAuto ...")
#		print("YESSSSSSS GETTTTTTTIIIIINNNNNNNGGGGG THERE!!!!!!")

class WatchpointsTableWidget(QTableWidget):
	
	ommitCellChanged = False
	
	def __init__(self, driver):
		super().__init__()
		self.driver = driver
		
#		self.driver.handleCommand("command script add -h '(lldbinit) The breakpoint callback function (auto).' --function breakpointTableWidget.breakpointHandlerAuto bpcbauto")
		
		self.initTable()
		self.context_menu = QMenu(self)
		self.actionEnableWP = self.context_menu.addAction("Enable / Disable Watchpoint")
#		self.actionEnableWP.triggered.connect(self.handle_enableWP)
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
#					for bl in bp_cur:
#						name_list = lldb.SBStringList()
#						bp_cur.GetNames(name_list)
#						num_names = name_list.GetSize()
#						name_list.AppendString("")
#						num_names = 1
#						for j in range(num_names):
#							name = name_list.GetStringAtIndex(j)
#							if name == self.oldBPName:
#								bp_cur.RemoveName(self.oldBPName)
#								bp_cur.AddName(self.item(row, 3).text())
#						wpFound = True
##								break
#						if wpFound:
#							break
			elif col == 8: # Name changed
				target = self.driver.getTarget()
				wpFound = False
				for i in range(target.GetNumWatchpoints()):
					wp_cur = target.GetWatchpointAtIndex(i)
					if "#" + str(wp_cur.GetID()) == self.item(self.selectedItems()[0].row(), 1).text():
						wp_cur.SetCondition(self.item(self.selectedItems()[0].row(), 8).text())
						break
			pass
			
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
		
#		item.enableBP(state)
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