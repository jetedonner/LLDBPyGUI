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

from dbg.breakpointHelper import *
from ui.customQt.QClickLabel import *
from ui.dialogs.dialogHelper import *
from ui.baseTreeWidget import *

from config import *

class EditableTreeItem(QTreeWidgetItem):
	
	isBPEnabled = True
	textEdited = pyqtSignal(object, int, str)
	
	def __init__(self, parent, text):
		super().__init__(parent, text)
#		self.setText(0, text)
#		self.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled)  # Set flags for editing


		
	def toggleBP(self):
		self.enableBP(not self.isBPEnabled)
		
	def enableBP(self, enabled):
		if self.isBPEnabled and not enabled:
			self.isBPEnabled = False
			self.setIcon(1, ConfigClass.iconBPDisabled)
		elif not self.isBPEnabled and enabled: 
			self.isBPEnabled = True
			self.setIcon(1, ConfigClass.iconBPEnabled)
		else:
			if enabled:
				self.setIcon(1, ConfigClass.iconBPEnabled) 
			else:
				self.setIcon(1, ConfigClass.iconBPDisabled) 
				
class BreakpointTreeWidget(BaseTreeWidget):
	
	def __init__(self, driver, bpHelper):
		super().__init__(driver)

		# self.setStyleSheet("""
		# 	QTreeWidget {
		# 		/* background-color: #f0f0f0;
		# 		gridline-color: #ccc;
		# 		font: 12px 'Courier New';*/
		# 		background-color: #282c34; /* Dark background */
		# 		color: #abb2bf; /* Light grey text */
		# 		/*border: 1px solid #3e4452;*/
		# 		border-radius: 5px;
		# 		/*padding: 10px;*/
		# 	}
		# 	QTreeWidgetItem {
		# 		/*padding: 5px;
		# 		color: #333;
		# 		background-color: #e6f2ff;*/
		# 		background-color: #282c34; /* Dark background */
		# 		color: #abb2bf; /* Light grey text */
		# 		/*border: 1px solid #3e4452;
		# 		border-radius: 5px;*/
		# 		padding: 5px;
		# 	}
		# 	QTreeWidgetItem:selected {
		# 		/*background-color: #3399ff;
		# 		color: white;*/
		# 		background-color: #282c34; /* Dark background */
		# 		color: #abb2bf; /* Light grey text */
		# 		/*border: 1px solid #3e4452;
		# 		border-radius: 5px;
		# 		padding: 10px;*/
		# 	}
		# """)
		#
		# self.driver = driver
		self.bpHelper = bpHelper
		
#       self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
		self.breakpointHelper = BreakpointHelper(self.window(), self.driver)
		self.context_menu = QMenu(self)
		
		self.actionShowInfos = self.context_menu.addAction("Show infos")
		self.context_menu.addSeparator()
		self.actionEnableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
		self.actionDeleteBP = self.context_menu.addAction("Delete Breakpoint")
		self.actionDeleteBP.triggered.connect(self.handle_deleteBP)
		self.actionEnableAllBP = self.context_menu.addAction("Enable All Breakpoints")
		self.actionDisableAllBP = self.context_menu.addAction("Disable All Breakpoints")
		self.context_menu.addSeparator()
		
		self.actionShowMemoryFrom = self.context_menu.addAction("Show memory")
		self.actionShowMemoryTo = self.context_menu.addAction("Show memory after End")
		self.context_menu.addSeparator()
		self.actionGoToAddress = self.context_menu.addAction("GoTo address")
		self.actionGoToAddress.triggered.connect(self.handle_gotoAddr)
		
		self.setFont(ConfigClass.font)
		self.setHeaderLabels(['#', 'State', 'Address', 'Name', 'Hit', 'Condition', 'Commands'])
		self.header().resizeSection(0, 96)
		self.header().resizeSection(1, 56)
		self.header().resizeSection(2, 128)
		self.header().resizeSection(3, 128)
		self.header().resizeSection(4, 128)
		self.header().resizeSection(5, 128)
		self.header().resizeSection(6, 32)
		self.header().resizeSection(7, 48)
		self.header().resizeSection(8, 256)
		self.setMouseTracking(True)
#		self.treBPs.itemDoubleClicked.connect(self.handle_itemDoubleClicked)
		self.currentItemChanged.connect(self.handle_currentItemChanged)
		self.itemChanged.connect(self.handle_itemChanged)
		self.itemEntered.connect(self.handle_itemEntered)

	# FIXME: SET and READ row no so we don't have to loop all rows
	def clearPC(self):
		items = self.getAllItemsAndSubitems()
		for item in items:
			for subitem in item.subItems:
				for i in range(subitem.columnCount()):
					subitem.setBackground(i, ConfigClass.colorTransparent)
					
	def setPC(self, address, setPC=True):
		items = self.getAllItemsAndSubitems()
		for item in items:
			for subitem in item.subItems:
				if int(subitem.text(2), 16) == int(address, 16) and subitem.isBPEnabled:
#					if self.invisibleRootItem().child(childPar).child(childChild).text(2) == address:
#						print(f'FOUND ADDRESS FOR PC: {address}')
					if setPC:
						for i in range(subitem.columnCount()):
							subitem.setBackground(i, ConfigClass.colorGreen)
					self.scrollToItem(subitem, 
						QAbstractItemView.ScrollHint.PositionAtCenter)
					if not setPC:
						break
				else:
					if setPC:
						for i in range(subitem.columnCount()):
							subitem.setBackground(i, ConfigClass.colorTransparent)
							
	def handle_deleteBP(self):
		daItem = self.currentItem()
		if daItem.childCount() > 0:
			daItem = daItem.child(0)
		self.bpHelper.deleteBP(daItem.text(2))
		pass
	
	def addBP(self, bp, enabled = True):
		names = lldb.SBStringList()
		bp.GetNames(names)
		num_names = names.GetSize()
		if num_names > 0:
			name = names.GetStringAtIndex(0)
		else:
			name = ""
		cmds = lldb.SBStringList()
		bp.GetCommandLineCommands(cmds)
		num_cmds = cmds.GetSize()
		if num_cmds > 0:
			cmd = cmds.GetStringAtIndex(0)
		else:
			cmd = ""
			
		bpNode = EditableTreeItem(self, [str(bp.GetID()), '', '', name, str(bp.GetHitCount()), bp.GetCondition(), cmd])
		bpNode.enableBP(bp.IsEnabled())
		idx = 1
		for bl in bp:
#			if initTable:
#				self.txtMultiline.table.setBPAtAddress(hex(bl.GetLoadAddress()), True, False)
			
#				print(f"SETTING UP BP CALLBACK")
#				print(f"command script import --allow-reload ./lldbpyGUIWindow.py")
			extra_args = lldb.SBStructuredData()
#				self.driver.handleCommand("command script import --allow-reload lldbpyGUIWindow.py")
#				bp.SetScriptCallbackFunction("lldbpyGUIWindow.my_callback", extra_args)
			
			txtID = str(bp.GetID()) + "." + str(idx)
			sectionNode = EditableTreeItem(bpNode, [txtID, '', hex(bl.GetLoadAddress()), name, str(bl.GetHitCount()), bl.GetCondition(), ''])
			sectionNode.enableBP(bl.IsEnabled())
			sectionNode.setToolTip(1, f"Enabled: {bl.IsEnabled()}")
			sectionNode.setTextAlignment(0, Qt.AlignmentFlag.AlignLeft)
			idx += 1
		bpNode.setExpanded(True)
			
	def deleteBP(self, bpId):
		rootItem = self.invisibleRootItem()
		daItem = None
		found = False
		for childPar in range(rootItem.childCount()):
			parentItem = rootItem.child(childPar)
			if parentItem.text(0) == str(bpId):
				daItem = parentItem
				found = True
				break
			else:
				for childChild in range(parentItem.childCount()):
					childItem = parentItem.child(childChild)
					if childItem.text(0) == str(bpId):
						daItem = childItem
						found = True
						break
			if found:
				break
		if found:
			self.setCurrentItem(daItem)
			index = self.currentIndex()
			# Check if a valid item is selected
			if index.isValid():
				# Remove and delete the item
				removed_item = self.takeTopLevelItem(index.row())
				del removed_item  # Alternatively, you can use removed_item.delete()
			
		pass
		
	def selectBPRow(self, address):
		rootItem = self.invisibleRootItem()
#		daItem = None
		found = False
		for childPar in range(rootItem.childCount()):
			parentItem = rootItem.child(childPar)
#			if parentItem.text(0) == str(bpId):
#				daItem = parentItem
#				found = True
#				break
#			else:
			for childChild in range(parentItem.childCount()):
				childItem = parentItem.child(childChild)
				if childItem.text(2) == address:
					daItem = childItem
					self.setCurrentItem(daItem)
					found = True
					break
			if found:
				break
#		if found:
#			self.setCurrentItem(daItem)
#			index = self.currentIndex()
#			# Check if a valid item is selected
#			if index.isValid():
#				# Remove and delete the item
#				removed_item = self.takeTopLevelItem(index.row())
#				del removed_item  # Alternatively, you can use removed_item.delete()
				
		pass
		
	
	def handle_gotoAddr(self):
		newAddr = self.currentItem().text(2)
		if newAddr != "":
			self.window().txtMultiline.viewAddress(newAddr)
			
	oldBPName = ""
	def handle_itemEntered(self, item, col):
		if col == 1:
			item.setToolTip(col, "State: " + str(item.isBPEnabled))
		elif col == 2:
			addrTxt = item.text(2)
			if addrTxt != None and addrTxt != "":
				self.window().updateStatusBar(f"Goto instruction @ address {addrTxt}")
				
		self.oldBPName = item.text(3)
		item.setData(5, Qt.ItemDataRole.UserRole, item.text(5))
		
		pass
		
	def event(self, event):
		if isinstance(event, QKeyEvent):
#			print(f"event: {event.key()}")
			if event.key() == Qt.Key.Key_Return:
				if self.isPersistentEditorOpen(self.currentItem(), self.currentColumn()):
					self.closePersistentEditor(self.currentItem(), self.currentColumn())
#					return True
				else:
					if self.currentItem().childCount() == 0:
						col = self.currentColumn()
						if col == 3 or col == 5 or col == 6:
							self.openPersistentEditor(self.currentItem(), col)
							self.editItem(self.currentItem(), col)
		return super().event(event)
	
	def contextMenuEvent(self, event):
		self.context_menu.exec(event.globalPos())
		
	def handle_itemChanged(self, item, col):
		print(f'ITEM CHANGED => {item.text(col)} / {col}')
		if col == 5 and item.childCount() == 0:
#			print(f"UPDATEING BP Condition of BP {item.text(0)} to '{item.text(col)}'")
			target = self.window().driver.getTarget()
			
			for i in range(target.GetNumBreakpoints()):
				bp = target.GetBreakpointAtIndex(i)
				for bl in bp:
					if item.text(0) == str(bp.GetID()) + "." + str(bl.GetID()):
						if item.data(5, Qt.ItemDataRole.UserRole) != item.text(5):
							item.setData(5, Qt.ItemDataRole.UserRole, item.text(5))
							if str(bp.GetCondition()) != item.text(col) and not (bp.GetCondition() == None and item.text(5) == ""):
								print(f"==========>>>>>>>>> SETTING CONDITION BP!!! => bp: {str(bp.GetCondition())} / item: {item.text(col)}")
								bp.SetCondition(item.text(col))
							if str(bl.GetCondition()) != item.text(col) and not (bl.GetCondition() == None and item.text(5) == ""):
								print(f"==========>>>>>>>>> SETTING CONDITION BL!!! => bl: {str(bl.GetCondition())} / item: {item.text(col)}")
								bl.SetCondition(item.text(col))
							rootItem = self.invisibleRootItem()
							for childPar in range(rootItem.childCount()):
								parentItem = rootItem.child(childPar)
								if parentItem.text(0) == str(bp.GetID()):
	#								parentItem.setText(4, str(bp.GetHitCount()))
									if item.text(col) != None and item.text(col) != "":
										parentItem.setText(5, str(item.text(col)))
									else:
										parentItem.setText(5, "")
									break
	#						print(f"GOT BP {item.text(0)}")
							break
		elif col == 3 and item.childCount() == 0:
#			print(f"UPDATEING BP-NAME: {item.text(0)} => {item.text(col)}")
			target = self.window().driver.getTarget()
			bpFound = False
			for i in range(target.GetNumBreakpoints()):
				bp = target.GetBreakpointAtIndex(i)
				for bl in bp:
					name_list = lldb.SBStringList()
					bp.GetNames(name_list)
					num_names = name_list.GetSize()
					name_list.AppendString("")
					num_names = 1
					for j in range(num_names):
						name = name_list.GetStringAtIndex(j)
						if name == self.oldBPName:
							bp.RemoveName(self.oldBPName)
							bp.AddName(item.text(col))
							bpFound = True
							break
					if bpFound:
						break
					
	def getAllItemsAndSubitems(self):
		itemsRet = []
		for childPar in range(self.invisibleRootItem().childCount()):
			itemsRet.append(self.invisibleRootItem().child(childPar))
			itemsRet[-1].subItems = []
			for childChild in range(self.invisibleRootItem().child(childPar).childCount()):
				if self.invisibleRootItem().child(childPar).child(childChild) != None:
					itemsRet[-1].subItems.append(self.invisibleRootItem().child(childPar).child(childChild))
#					self.invisibleRootItem().child(childPar).child(childChild).enableBP(True)
					
		return itemsRet
	
	def enableAllBPs():
		for childPar in range(self.invisibleRootItem().childCount()):
			for childChild in range(self.invisibleRootItem().child(childPar).childCount()):
				if self.invisibleRootItem().child(childPar).child(childChild) != None:
					self.invisibleRootItem().child(childPar).child(childChild).enableBP(True)
		pass
		
	def enableBPByAddress(self, address, enabled):
		for childPar in range(self.invisibleRootItem().childCount()):
			for childChild in range(self.invisibleRootItem().child(childPar).childCount()):
				if self.invisibleRootItem().child(childPar).child(childChild) != None:
					print(f'self.invisibleRootItem().child(childPar).child(childChild): {self.invisibleRootItem().child(childPar).child(childChild).text(2)} / {address}')
					if self.invisibleRootItem().child(childPar).child(childChild).text(2) == address:
						self.invisibleRootItem().child(childPar).child(childChild).enableBP(enabled)
#						if daItem.parent() != None:
		#				newEnabled = daItem.isBPEnabled
						allDisabled = True
						for i in range(self.invisibleRootItem().child(childPar).childCount()):
							if self.invisibleRootItem().child(childPar).child(i).isBPEnabled:
								allDisabled = False
								break
						self.invisibleRootItem().child(childPar).enableBP(not allDisabled)
						break
		pass
		
	def enableBP(self, address, enabled):
		for childPar in range(self.invisibleRootItem().childCount()):
			for childChild in range(self.invisibleRootItem().child(childPar).childCount()):
				if self.invisibleRootItem().child(childPar).child(childChild) != None:
					print(f'self.invisibleRootItem().child(childPar).child(childChild): {self.invisibleRootItem().child(childPar).child(childChild).text(2)} / {address}')
					if self.invisibleRootItem().child(childPar).child(childChild).text(2).lower() == address.lower():
						self.invisibleRootItem().child(childPar).child(childChild).enableBP(enabled)
						allDisabled = True
						for i in range(self.invisibleRootItem().child(childPar).childCount()):
							if self.invisibleRootItem().child(childPar).child(i).isBPEnabled:
								allDisabled = False
								break
						self.invisibleRootItem().child(childPar).enableBP(not allDisabled)
						break
		pass
		
	def mouseDoubleClickEvent(self, event):
		daItem = self.itemAt(event.pos().x(), event.pos().y())
		if daItem == None:
			return
		col = self.columnAt(event.pos().x())
		if daItem.childCount() > 0:
			super().mouseDoubleClickEvent(event)
		elif col == 1:
			self.bpHelper.enableBP(daItem.text(2), not daItem.isBPEnabled)
		elif col == 2:
			self.window().txtMultiline.viewAddress(daItem.text(2))
			pass
		else:
			if col == 3 or col == 5 or col == 6:
				self.openPersistentEditor(daItem, col)
				self.editItem(daItem, col)

	def handle_tableView_changed(self, index):
		print(f'handle_tableView_changed => {index}')
#		self.closeAllEditors
		
	def handle_currentItemChanged(self, cur, prev):
#		print("ITEM CHANGED")
		self.closeAllEditors(prev)
		
	def closeAllEditors(self, item):
		if self.isPersistentEditorOpen(item, 3):
			self.closePersistentEditor(item, 3)
		if self.isPersistentEditorOpen(item, 5):
			self.closePersistentEditor(item, 5)
		if self.isPersistentEditorOpen(item, 6):
			self.closePersistentEditor(item, 6)
			
class BPsWPsWidget(QWidget):
	
	driver = None
	workerManager = None
	
	def __init__(self, driver, workerManager, bpHelper):
		super().__init__()
		self.driver = driver
		self.bpHelper = bpHelper
		
		self.workerManager = workerManager
		
		self.layBPWPMain = QHBoxLayout()
		self.layBPWPMain.setContentsMargins(0, 0, 0, 0)
		self.setContentsMargins(0, 0, 0, 0)
#		self.tabWidgetBPsWPs = QTabWidget()
		
		self.treBPs = BreakpointTreeWidget(self.driver, self.bpHelper)
		self.treBPs.setContentsMargins(0, 0, 0, 0)
#		self.cmdAddBP = ClickLabel()
#		self.cmdAddBP.setPixmap(ConfigClass.pixAdd)
#		self.cmdAddBP.setToolTip("Add Breakpoints")
#		self.cmdAddBP.clicked.connect(self.click_addBP)
#		self.cmdAddBP.setContentsMargins(0, 0, 0, 0)
#		
#		self.cmdEnableAll = ClickLabel()
#		self.cmdEnableAll.setPixmap(ConfigClass.pixBugGreen)
#		self.cmdEnableAll.setToolTip("Enable ALL Breakpoints")
#		self.cmdEnableAll.clicked.connect(self.click_enableAll)
#		self.cmdEnableAll.setContentsMargins(0, 0, 0, 0)
#		
#		self.cmdSaveBP = ClickLabel()
#		self.cmdSaveBP.setPixmap(ConfigClass.pixSave)
#		self.cmdSaveBP.setToolTip("Save Breakpoints")
#		self.cmdSaveBP.clicked.connect(self.click_saveBP)
#		self.cmdSaveBP.setContentsMargins(0, 0, 0, 0)
#		
#		self.cmdLoadBP = ClickLabel()
#		self.cmdLoadBP.setPixmap(ConfigClass.pixLoad)
#		self.cmdLoadBP.setToolTip("Load Breakpoints")
#		self.cmdLoadBP.clicked.connect(self.click_loadBP)
#		self.cmdLoadBP.setContentsMargins(0, 0, 0, 0)
#		
#		self.cmdReloadBPs = ClickLabel()
#		self.cmdReloadBPs.setPixmap(ConfigClass.pixReload)
#		self.cmdReloadBPs.setToolTip("Reload Breakpoints")
#		self.cmdReloadBPs.clicked.connect(self.click_reloadBP)
#		self.cmdReloadBPs.setContentsMargins(0, 0, 0, 0)
#		
#		self.cmdDeleteAllBP = ClickLabel()
#		self.cmdDeleteAllBP.setPixmap(ConfigClass.pixTrash)
#		self.cmdDeleteAllBP.setToolTip("Delete ALL Breakpoints")
#		self.cmdDeleteAllBP.clicked.connect(self.click_deleteAllBP)
#		self.cmdDeleteAllBP.setContentsMargins(0, 0, 0, 0)
#		
#		self.wgtBPCtrls = QWidget()
#		self.wgtBPCtrls.setContentsMargins(0, 10, 0, 0)
#		self.wgtBPCtrls.setLayout(QHBoxLayout())
#		self.wgtBPCtrls.layout().addWidget(self.cmdAddBP)
#		self.wgtBPCtrls.layout().addWidget(self.cmdEnableAll)
#		self.wgtBPCtrls.layout().addWidget(self.cmdSaveBP)
#		self.wgtBPCtrls.layout().addWidget(self.cmdLoadBP)
#		self.wgtBPCtrls.layout().addWidget(self.cmdReloadBPs)
#		self.wgtBPCtrls.layout().addWidget(self.cmdDeleteAllBP)
##		self.wgtBPCtrls.layout().setContentsMargins(0, 0, 0, 0)
#		self.wgtBPCtrls.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

#		self.wdtBPs = QWidget()
#		self.wdtBPs.setLayout(QVBoxLayout())
##		self.wdtBPs.layout().addWidget(self.wgtBPCtrls)
#		self.wdtBPs.layout().addWidget(self.treBPs)
#		self.wdtBPs.setContentsMargins(0, 0, 0, 0)
#		
#		self.tabWidgetBPsWPs.addTab(self.wdtBPs, "Breakpoints")
		
#		self.tblWPs = WatchpointsTableWidget(self.driver)
#		self.tabWidgetBPsWPs.addTab(self.tblWPs, "Watchpoints")
		self.toolbar = QToolBar('Main ToolBar')
#		self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)
		
		self.delete_action = QAction(QIcon(ConfigClass.pixGears.scaledToWidth(24)), '&Delete all breakpoints', self)
		self.delete_action.setStatusTip('Delete all breakpoints')
#		self.delete_action.setShortcut('Ctrl+L')
#		self.delete_action.triggered.connect(self.load_clicked)
		self.toolbar.addAction(self.delete_action)
		
#		self.layBPWPMain.addWidget(self.treBPs)
		self.layBPCtrls = QVBoxLayout()
		self.wdtBPCtrls = QWidget()
		self.wdtBPCtrls.setContentsMargins(0, 0, 0, 0)
		self.wdtBPCtrls.setLayout(self.layBPCtrls)
		self.cmdDeleteAll = QClickLabel()
		self.cmdDeleteAll.setContentsMargins(0, 0, 0, 0)
		self.cmdDeleteAll.setPixmap(ConfigClass.pixDelete.scaledToWidth(24))
		self.cmdDeleteAll.setToolTip("Delete all breakpoints")
		self.cmdDeleteAll.setStatusTip("Delete all breakpoints")
		self.cmdDeleteAll.clicked.connect(self.cmdDeleteAll_clicked)
		
		self.cmdSaveBPs = QClickLabel()
		self.cmdSaveBPs.setContentsMargins(0, 0, 0, 0)
		self.cmdSaveBPs.setPixmap(ConfigClass.pixSave.scaledToWidth(24))
		self.cmdSaveBPs.setToolTip("Save breakpoints")
		self.cmdSaveBPs.setStatusTip("Save breakpoints")
		self.cmdSaveBPs.clicked.connect(self.cmdSaveBPs_clicked)
		
		self.layBPCtrls.addWidget(self.cmdDeleteAll)
		self.layBPCtrls.addWidget(self.cmdSaveBPs)
		self.spacer = QSpacerItem(0, 200, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.MinimumExpanding)
		self.layBPCtrls.addItem(self.spacer)
		self.treBPs.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
#		self.layBPWPMain.addWidget(self.treBPs)
		self.cmdDeleteAll.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.wdtBPCtrls.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.layBPWPMain.addWidget(self.wdtBPCtrls)
		self.layBPWPMain.addWidget(self.treBPs)
		
#		self.layBPWPMain.addWidget(self.toolbar)
		# Set stylesheet for icon size
#		stylesheet = "QToolBar > QToolButton { icon-size: 16px; }"  # Adjust size as needed
#		self.toolbar.setStyleSheet(stylesheet)
			
		self.setLayout(self.layBPWPMain)
		
	def cmdSaveBPs_clicked(self):
		print(f"Save BPs ...")
		filename = showSaveFileDialog(self.window().app)
		if filename != "":
			print(f"Save BPs as '{filename}' ...")
			self.bpHelper.saveBPs(filename)
		
	def cmdDeleteAll_clicked(self):
#		print(f"Delete All BPs ...")
		dlg = ConfirmDialog("Delete all breakpoints?", "Do you really want to delete all breakpoints?")
		if dlg.exec() and dlg.button_clicked == QDialogButtonBox.StandardButton.Ok:
			print(f"Delete All BPs YESSS ...")
			
		
	def reloadBreakpoints(self, initTable = True):
		self.workerManager.start_loadBreakpointsWorker(self.handle_loadBreakpointsFinished, self.handle_loadBreakpointValue, self.handle_updateBreakpointValue, initTable)
		
	def handle_loadBreakpointValue(self, bp, initTable):	
		self.treBPs.addBP(bp)
		for bl in bp:
			self.window().txtMultiline.enableBP(hex(bl.GetLoadAddress()), bl.IsEnabled())

	def handle_updateBreakpointValue(self, bp):
		rootItem = self.treBPs.invisibleRootItem()
		for childPar in range(rootItem.childCount()):
			parentItem = rootItem.child(childPar)
			if parentItem.text(0) == str(bp.GetID()):
				if parentItem.text(4) != str(bp.GetHitCount()):
					parentItem.setText(4, str(bp.GetHitCount()))
				if bp.GetCondition() != None and str(bp.GetCondition()) != "":
					if parentItem.text(5) != str(bp.GetCondition()):
						parentItem.setText(5, str(bp.GetCondition()))
						print("SETTING CONDITION TO VAL (BP)")
				else:
					if parentItem.text(5) != "":
						print("SETTING CONDITION TO EMPTY (BP)")
						parentItem.setText(5, "")
						
				idx = 0
				for bl in bp:
					for childChild in range(parentItem.childCount()):
						childItem = parentItem.child(childChild)
						if childItem != None:
							if childItem.text(0) == str(bp.GetID()) + "." + str(bl.GetID()):
								if childItem.text(4) != str(bl.GetHitCount()):
									childItem.setText(4, str(bl.GetHitCount()))
								if bl.GetCondition() != None and str(bl.GetCondition()) != "":
									if childItem.text(5) != str(bl.GetCondition()):
										childItem.setText(5, str(bl.GetCondition()))
										print("SETTING CONDITION TO VAL (BL)")
								else:
									if childItem.text(5) != "":
										print("SETTING CONDITION TO EMPTY (BL)")
										childItem.setText(5, "")
								break
					idx += 1
				break
	
	def handle_loadBreakpointsFinished(self):
#		self.treBPs.setPC(self.rip)
		pass