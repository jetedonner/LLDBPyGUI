import json

import lldb
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent, QColor
from PyQt6.QtWidgets import QMenu, QTreeWidgetItem, QWidget, QSizePolicy, QSpacerItem, QVBoxLayout, QHBoxLayout, \
	QDialogButtonBox

from config import ConfigClass
from helper.debugHelper import logDbgC
from lib.settings import SettingsHelper, SettingsValues
from lib.thirdParty.breakpointManager import BreakpointManager
from lib.thirdParty.lldbutil import get_module_from_breakpoint_location
from ui.base.baseTreeWidget import BaseTreeWidget
from ui.customQt.QClickLabel import QClickLabel
from ui.dialogs.dialogHelper import showSaveFileDialog, showOpenFileDialog, InputDialog


class EditableTreeItem(QTreeWidgetItem):
	isBPEnabled = True

	# textEdited = pyqtSignal(object, int, str)

	def __init__(self, parent, text):
		super().__init__(parent, text)

	def toggleBP(self):
		self.enableBP(not self.isBPEnabled)

	def enableBP(self, enabled):
		self.isBPEnabled = enabled
		if enabled:
			self.setIcon(1, ConfigClass.iconBPEnabled)
		else:
			self.setIcon(1, ConfigClass.iconBPDisabled)


class BreakpointWidget(QWidget):
	driver = None

	def __init__(self, driver):  # , bpHelper):
		super().__init__()

		self.driver = driver

		self.layBPCtrls = QVBoxLayout()
		self.layBPCtrls.setContentsMargins(0, 0, 0, 0)
		self.wdtBPCtrls = QWidget()
		self.wdtBPCtrls.setContentsMargins(0, 0, 0, 0)
		self.wdtBPCtrls.setLayout(self.layBPCtrls)
		self.cmdDeleteAll = QClickLabel()
		self.cmdDeleteAll.setContentsMargins(0, 0, 0, 0)
		self.cmdDeleteAll.setPixmap(ConfigClass.pixDelete.scaledToWidth(24))
		self.cmdDeleteAll.setToolTip("Delete all breakpoints")
		self.cmdDeleteAll.setStatusTip("Delete all breakpoints")
		self.cmdDeleteAll.clicked.connect(self.cmdDeleteAll_clicked)

		self.cmdLoadBPs = QClickLabel()
		self.cmdLoadBPs.setContentsMargins(0, 0, 0, 0)
		self.cmdLoadBPs.setPixmap(ConfigClass.pixOpen.scaledToWidth(24))
		self.cmdLoadBPs.setToolTip("Load breakpoints")
		self.cmdLoadBPs.setStatusTip("Load breakpoints")
		self.cmdLoadBPs.clicked.connect(self.cmdLoadBPs_clicked)

		self.cmdSaveBPs = QClickLabel()
		self.cmdSaveBPs.setContentsMargins(0, 0, 0, 0)
		self.cmdSaveBPs.setPixmap(ConfigClass.pixSave.scaledToWidth(24))
		self.cmdSaveBPs.setToolTip("Save breakpoints")
		self.cmdSaveBPs.setStatusTip("Save breakpoints")
		self.cmdSaveBPs.clicked.connect(self.cmdSaveBPs_clicked)

		self.cmdAddBPByName = QClickLabel()
		self.cmdAddBPByName.setContentsMargins(0, 0, 0, 0)
		self.cmdAddBPByName.setPixmap(ConfigClass.pixName.scaledToWidth(24))
		self.cmdAddBPByName.setToolTip("Add breakpoint by name")
		self.cmdAddBPByName.setStatusTip("Add breakpoint by name")
		self.cmdAddBPByName.clicked.connect(self.cmdAddBPByName_clicked)

		self.layBPCtrls.addWidget(self.cmdDeleteAll)
		self.layBPCtrls.addWidget(self.cmdSaveBPs)
		self.layBPCtrls.addWidget(self.cmdLoadBPs)
		self.layBPCtrls.addWidget(self.cmdAddBPByName)

		self.spacer = QSpacerItem(0, 70, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.MinimumExpanding)
		# self.spacer.setContentsMargins(0, 0, 0, 0)
		self.layBPCtrls.addItem(self.spacer)

		self.treBP = BreakpointTreeWidget(driver)
		self.treBP.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		self.cmdDeleteAll.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.wdtBPCtrls.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.layBPWPMain = QHBoxLayout()
		self.layBPWPMain.setContentsMargins(0, 0, 0, 0)
		self.layBPWPMain.addWidget(self.wdtBPCtrls)
		self.layBPWPMain.addWidget(self.treBP)
		self.setLayout(self.layBPWPMain)

	def cmdAddBPByName_clicked(self):
		dlgBPName = InputDialog("Enter BP name", "Enter the symbol name for the breakpoint to set", "", "Enter a symbol name ...")
		# bpNameSet = dlgBPName.exec()
		if dlgBPName.exec() and dlgBPName.button_clicked == QDialogButtonBox.StandardButton.Ok:
			bpNameSet = dlgBPName.txtInput.text()
			if bpNameSet is not None and bpNameSet != "":
				self.treBP.bpMgr.addBPByName(bpNameSet, "", "TestName")
				self.window().updateStatusBar(f"Breakpoint '{bpNameSet}' added (Name: 'TestName') ...")

	def cmdDeleteAll_clicked(self):
		self.treBP.bpMgr.deleteAllBPs()

	def cmdLoadBPs_clicked(self):
		# def loadBPs(self, filepath):
		logDbgC(f"Loading BPs ...")
		filepath = showOpenFileDialog()
		if filepath is not None and filepath != "":
			target = self.driver.target
			self.load_breakpoints_from_file(target, filepath)
			# path_spec = lldb.SBFileSpec(filepath)
			# bkpt_list = lldb.SBBreakpointList(target)
			#
			# # Load breakpoints from the file
			# error = target.BreakpointsCreateFromFile(path_spec, bkpt_list)
			# if error is not None and not error.Success():
			#     logDbgC(f"Error while getting the Breakpoints from file ({filepath}): {error}")
			# else:
			#     logDbgC(f"LOADED BPs FROM FILE!!!!")
			#     logDbgC(f"{bkpt_list}")
			#     # dir(bkpt_list)
			#     logDbgC(dir(bkpt_list))
			#     for brIdx in range(bkpt_list.GetSize()):
			#         for bl in bkpt_list.GetBreakpointAtIndex(brIdx):
			#             logDbgC(f"bl.GetAddress(): {bl.GetAddress()}")

	def cmdSaveBPs_clicked(self):
		logDbgC(f"Save BPs ...")
		filename = showSaveFileDialog(None, "BP-JSON (*.bpson)")  # self.window().app
		if filename is not None and filename != "":
			logDbgC(f"Save BPs as '{filename}' ...")
			# # self.bpHelper.saveBPs(filename)
			# error = self.driver.target.BreakpointsWriteToFile(lldb.SBFileSpec(filename))
			# if not error.Success():
			#     logDbgC(f"saveBPs => Error: {error}")
			self.save_breakpoints(self.driver.target, filename)
		pass

	def serialize_breakpoint(self, bp, target):
		locations = []
		for i in range(bp.GetNumLocations()):
			loc = bp.GetLocationAtIndex(i)
			addr = loc.GetAddress()
			# target = lldb.debugger.GetSelectedTarget()
			locations.append({
				"id": loc.GetID(),
				"id_full": str(bp.GetID()) + "." + str(loc.GetID()),
				"load_address": addr.GetLoadAddress(target),
				"offset": addr.GetOffset(),
				"enabled": loc.IsEnabled(),
				"symbol": addr.GetSymbol().GetName() if addr.GetSymbol() else None
			})

		bpNames = lldb.SBStringList()
		bp.GetNames(bpNames)
		num_names = bpNames.GetSize()
		if num_names > 0:
			name = num_names.GetStringAtIndex(0)
		else:
			name = ""

		return {
			"id": bp.GetID(),
			"enabled": bp.IsEnabled(),
			# "name": bp.GetBreakpointName(),
			"name": name,
			"locations": locations,
			"condition": bp.GetCondition(),
			"thread_id": bp.GetThreadID(),
			"thread_index": bp.GetThreadIndex(),
			"thread_name": bp.GetThreadName(),
			"queue_name": bp.GetQueueName(),
			"ignore_count": bp.GetIgnoreCount(),
			"hit_count": bp.GetHitCount()
		}

	def save_breakpoints(self, target, filepath):
		breakpoints = [self.serialize_breakpoint(target.GetBreakpointAtIndex(i), target)
					   for i in range(target.GetNumBreakpoints())]
		with open(filepath, "w", encoding="utf-8") as f:
			json.dump(breakpoints, f, indent=2)

	def load_breakpoints_from_file(self, target, filepath):
		with open(filepath, "r", encoding="utf-8") as f:
			breakpoints_data = json.load(f)

		logDbgC(f"breakpoints_data: {breakpoints_data} ...")
		for bp_data in breakpoints_data:
			locs = bp_data.get("locations")
			logDbgC(f"locs: {locs} ...")
			if locs is None:
				continue
			for loc in locs:
				addr = loc.get("load_address")
				logDbgC(f"addr: {addr} ...")
				if addr is None:
					continue

				# Create breakpoint by address
				bp = target.BreakpointCreateByAddress(addr)

				# Restore metadata
				# if bp_data.get("enabled") is False:
				#     bp.SetEnabled(False)
				# if loc.get("enabled") == "false":
				allEnabled = True
				for bl in bp:
					bl.SetEnabled(loc.get("enabled") == True)
					if loc.get("enabled") == False:
						allEnabled = False

				bp.SetEnabled(allEnabled)

				# if bp_data.get("enabled") is False:
				#     bp.SetEnabled(False)

				if bp_data.get("condition"):
					bp.SetCondition(bp_data["condition"])
				if bp_data.get("ignore_count", 0) > 0:
					bp.SetIgnoreCount(bp_data["ignore_count"])
				if bp_data.get("name"):
					target.AddNameToBreakpoint(bp, bp_data["name"])

	def clearPC(self):
		self.treBP.clearPC()

	def removeBreakpoint(self, bp):
		self.treBP.removeBreakpoint(bp)

	def addBreakpoint(self, bp):
		self.treBP.addBreakpoint(bp)

	def enableBreakpoint(self, bp, enable):
		self.treBP.enableBreakpoint(bp, enable)

	def updateBreakpointValues(self, values):
		self.treBP.updateBreakpointValues(values)

	def setPC(self, pc, setColor=True):
		self.treBP.setPC(pc, setColor)


class BreakpointTreeWidget(BaseTreeWidget):
	# arrBPConditions = {}
	# oldBPName = ""
	nextViewAddress = None

	def __init__(self, driver):  # , bpHelper):
		super().__init__(driver)

		self.old_value = None

		self.bpMgr = BreakpointManager(self.driver)

		self.setContentsMargins(0, 0, 0, 0)

		self.context_menu = QMenu(self)

		# self.actionShowInfos = self.context_menu.addAction("Show infos")
		# self.context_menu.addSeparator()
		self.actionEnableBP = self.context_menu.addAction("Toggle Breakpoint")
		self.actionEnableBP.triggered.connect(self.handle_toggleBP)
		self.actionDeleteBP = self.context_menu.addAction("Delete Breakpoint")
		self.actionDeleteBP.triggered.connect(self.deleteBreakpoint)
		# self.actionEnableAllBP = self.context_menu.addAction("Enable All Breakpoints")
		# self.actionDisableAllBP = self.context_menu.addAction("Disable All Breakpoints")
		# self.context_menu.addSeparator()
		#
		# self.actionShowInFinder = self.context_menu.addAction("Show in Finder")
		# self.actionShowInFinder.triggered.connect(self.handle_showInFinder)
		# self.actionShowInTerminal = self.context_menu.addAction("Show in Terminal")
		# self.actionShowInTerminal.triggered.connect(self.handle_showInTerminal)
		# self.actionShowMemoryFrom = self.context_menu.addAction("Show memory")
		# self.actionShowMemoryTo = self.context_menu.addAction("Show memory after End")
		# self.context_menu.addSeparator()
		# self.actionGoToAddress = self.context_menu.addAction("GoTo address")
		# self.actionGoToAddress.triggered.connect(self.handle_gotoAddr)
		# self.context_menu.addSeparator()
		# self.actionToggleSingleShot = self.context_menu.addAction("Toggle one shot")
		# self.actionToggleSingleShot.triggered.connect(self.handle_toggleSingleShot)

		self.setFont(ConfigClass.font)
		self.setHeaderLabels(['#', 'State', 'Address', 'Name', 'Hit', 'Condition', 'Commands', '1 Shot', 'Module'])
		self.header().resizeSection(0, 96)
		self.header().resizeSection(1, 56)
		self.header().resizeSection(2, 128)
		self.header().resizeSection(3, 128)
		self.header().resizeSection(4, 128)
		self.header().resizeSection(5, 128)
		self.header().resizeSection(6, 250)
		self.header().resizeSection(7, 48)
		self.header().resizeSection(8, 140)
		self.setMouseTracking(True)
		# #		self.treBPs.itemDoubleClicked.connect(self.handle_itemDoubleClicked)
		# self.currentItemChanged.connect(self.handle_currentItemChanged)
		self.itemChanged.connect(self.handle_itemChanged)
		self.itemClicked.connect(self.store_old_value)
		# self.itemEntered.connect(self.handle_itemEntered)

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

	def mouseDoubleClickEvent(self, event) -> None:
		# logDbgC(f"HELLO FROM BP DOUBLECLICKEDICLICK ...")
		daItem = self.itemAt(event.pos().x(), event.pos().y())
		if daItem is not None:
			col = self.columnAt(event.pos().x())
			logDbgC(f"HELLO FROM BP DOUBLECLICKEDICLICK col: {col} / daItem.text(0): {daItem.text(0)}...")
			if daItem.childCount() > 0:
				if col == 3:
					# # daItem
					# self.openPersistentEditor(daItem, col)
					# currItm = self.currentItem()
					self.editItem(daItem)
					self.openPersistentEditor(daItem, col)
				return
			elif col == 1:
				logDbgC(f"handle_toggleBP => id: {daItem.text(0)}, enable: {not daItem.isBPEnabled} ...")
				# if "." in daItem.text(0):
				#     self.bpMgr.enableBPByID(daItem.text(0).split(".")[0], not daItem.isBPEnabled)
				self.bpMgr.enableBPByID(daItem.text(0), not daItem.isBPEnabled)
			elif col == 2:
				self.viewAddressInModule(daItem.text(2), daItem.text(8))
				# self.window().wdtDisassembly.tblDisassembly.viewAddress(daItem.text(2))
				# logDbgC(
				# 	f"Disassemble module on double clickediclick => module: {daItem.text(8)}, address: {daItem.text(2)}, daItem.toolTip({col}): {daItem.toolTip(col)} ...")
				# self.nextViewAddress = daItem.text(2)
				# for mod in self.driver.target.modules:
				# 	if mod.GetFileSpec().GetFilename() == daItem.text(8):
				# 		self.window().checkLoadModule(mod.GetFileSpec())
				# 		break
				# pass
			elif col == 3:
				# # daItem
				# self.openPersistentEditor(daItem, col)
				# currItm = self.currentItem()
				self.editItem(daItem)
				self.openPersistentEditor(daItem, col)
				pass
			# elif col == 7:
			#     # self.window().txtMultiline.viewAddress(daItem.text(2))
			#     logDbgC(f"Toggle one shot ....")
			#     pass
			elif col == 8:
				self.viewAddressInModule(daItem.text(2), daItem.text(8))
				# logDbgC(
				# 	f"Disassemble module on double clickediclick => module: {daItem.text(col)}, address: {daItem.text(2)}, daItem.toolTip({col}): {daItem.toolTip(col)} ...")
				# self.nextViewAddress = daItem.text(2)
				# for mod in self.driver.target.modules:
				# 	if mod.GetFileSpec().GetFilename() == daItem.text(col):
				# 		self.window().checkLoadModule(mod.GetFileSpec())
				# 		break
				# self.window().wdtFiles.select_module(daItem.text(col), False)
				# self.window().wdtDisassembly.tblDisassembly.viewAddress(daItem.text(2))
			elif col == 5:
				self.openPersistentEditor(daItem, col)
				self.editItem(daItem, col)
		super().mouseDoubleClickEvent(event)

	def viewAddressInModule(self, address, module):
		logDbgC(f"Disassemble module on double clickediclick => module: {module}, address: {address} ...")
		self.nextViewAddress = address
		for mod in self.driver.target.modules:
			if mod.GetFileSpec().GetFilename() == module:
				self.window().checkLoadModule(mod.GetFileSpec(), False)
				break

	def store_old_value(self, item, column):
		self.old_value = item.text(column)

	def handle_itemChanged(self, item):
		# if not self.suspendChangeHandler:
		col = self.currentColumn()
		if col == 3:
			new_name = item.text(col)
			bpID = self.currentItem().text(0).split(".")[0]
			print(f"Old value: {self.old_value}, New value: {new_name}")
			if self.old_value and self.old_value != "":
				self.bpMgr.deleteNameFromBP(bpID, self.old_value)
				self.old_value = None  # Reset after use

			if new_name and new_name != "":
				logDbgC(f"handle_itemChanged => id: {bpID}, name: {new_name} ...")
				# new_value = item.text(2)
				# print(f"Old value: {self.old_value}, New value: {new_name}")
				# if self.old_value != "":
				# 	self.bpMgr.deleteNameFromBP(bpID, self.old_value)
				# self.old_value = None  # Reset after use
				# if new_name != "":
				self.bpMgr.addNameToBP(bpID, new_name)

	def handle_currentItemChanged(self, cur, prev):
		self.closeAllEditors(prev)

	def closeAllEditors(self, item):
		if self.isPersistentEditorOpen(item, 3):
			self.closePersistentEditor(item, 3)
		if self.isPersistentEditorOpen(item, 5):
			self.closePersistentEditor(item, 5)
		if self.isPersistentEditorOpen(item, 6):
			self.closePersistentEditor(item, 6)

	def disassemble_dylib(self, debugger, dylib_path="/usr/lib/system/libsystem_c.dylib"):
		self.window().start_loadDisassemblyWorkerNG(dylib_path, True)

	def handle_toggleBP(self):
		daItem = self.currentItem()
		logDbgC(f"handle_toggleBP => id: {daItem.text(0)}, enable: {not daItem.isBPEnabled} ...")
		self.bpMgr.enableBPByID(daItem.text(0), not daItem.isBPEnabled)

	def addBreakpoint(self, bp):
		nameMain = ""
		cmd = ""
		names = lldb.SBStringList()
		bp.GetNames(names)
		for name in names:
			nameMain = name
			cmd = bp.GetCondition()
			break
		bpNode = EditableTreeItem(self, [str(bp.GetID()), '', '', nameMain, str(bp.GetHitCount()), bp.GetCondition(), cmd,
										 'Yes' if bp.IsOneShot() else 'No', ''])
		bpNode.enableBP(bp.IsEnabled())
		idx = 1
		loadAddr = ""
		for bl in bp:
			txtID = str(bp.GetID()) + "." + str(idx)

			sectionNode = EditableTreeItem(bpNode, [txtID, '', hex(bl.GetLoadAddress()), nameMain, str(bl.GetHitCount()),
													bl.GetCondition(), '', 'Yes' if bp.IsOneShot() else 'No',
													get_module_from_breakpoint_location(
														bl).GetFileSpec().GetFilename()])

			loadAddr = hex(bl.GetLoadAddress())
			sectionNode.enableBP(bl.IsEnabled())
			sectionNode.setToolTip(1, f"Enabled: {bl.IsEnabled()}")
			sectionNode.setToolTip(8, str(bl.GetAddress().GetModule().GetFileSpec().fullpath))
			sectionNode.setTextAlignment(0, Qt.AlignmentFlag.AlignLeft)
			idx += 1
		bpNode.setExpanded(True)
		self.window().updateStatusBar(f"Added new breakpoint @: {loadAddr}")

	def removeBreakpoint(self, bpID):
		logDbgC(f"==========>>>>>>>>>>>>> removeBreakpoint({bpID} ...")
		# daItem = self.currentItem()
		for childPar in range(self.invisibleRootItem().childCount()):
			if self.invisibleRootItem().child(childPar).text(0) == str(bpID):
				self.invisibleRootItem().child(childPar).removeChild(self.invisibleRootItem().child(childPar))
				break
			for childChild in range(self.invisibleRootItem().child(childPar).childCount()):
				if self.invisibleRootItem().child(childPar).child(childChild) != None:
					# print(
					#     f'self.invisibleRootItem().child(childPar).child(childChild): {self.invisibleRootItem().child(childPar).child(childChild).text(2)} / {address}')
					if self.invisibleRootItem().child(childPar).child(childChild).text(0) == str(bpID):
						self.invisibleRootItem().child(childPar).removeChild(
							self.invisibleRootItem().child(childPar).child(childChild))
					# if self.invisibleRootItem().child(childPar).child(childChild).text(2).lower() == address.lower():
					#     self.invisibleRootItem().child(childPar).child(childChild).enableBP(enable)
					#     allDisabled = True
					#     for i in range(self.invisibleRootItem().child(childPar).childCount()):
					#         if self.invisibleRootItem().child(childPar).child(i).isBPEnabled:
					#             allDisabled = False
					#             break
					#     self.invisibleRootItem().child(childPar).enableBP(not allDisabled)
		# if daItem.childCount() > 0:
		#     daItem = daItem.child(0)
		# self.window().updateStatusBar(f"Deleted breakpoint @: {daItem.text(2)}")
		# self.bpMgr.deleteBPByID(daItem.text(0))

	def deleteBreakpoint(self):
		daItem = self.currentItem()
		# if daItem.childCount() > 0:
		#     daItem = daItem.child(0)
		self.window().updateStatusBar(f"Deleted breakpoint @: {daItem.text(2)}")
		# self.bpMgr.deleteBPByID(daItem.text(0))
		self.bpMgr.deleteBPByAddr(daItem.text(2))


	def enableBreakpoint(self, bp, enable=True):
		for bl in bp:
			self.enableBreakpointLocationByAddress(hex(bl.GetLoadAddress()), enable)

	def enableBreakpointLocationByAddress(self, address, enable=True):
		for childPar in range(self.invisibleRootItem().childCount()):
			for childChild in range(self.invisibleRootItem().child(childPar).childCount()):
				if self.invisibleRootItem().child(childPar).child(childChild) != None:
					print(
						f'self.invisibleRootItem().child(childPar).child(childChild): {self.invisibleRootItem().child(childPar).child(childChild).text(2)} / {address}')
					if self.invisibleRootItem().child(childPar).child(childChild).text(2).lower() == address.lower():
						self.invisibleRootItem().child(childPar).child(childChild).enableBP(enable)
						allDisabled = True
						for i in range(self.invisibleRootItem().child(childPar).childCount()):
							if self.invisibleRootItem().child(childPar).child(i).isBPEnabled:
								allDisabled = False
								break
						self.invisibleRootItem().child(childPar).enableBP(not allDisabled)
						break

	def applyToAllCells(self, action):
		items = self.getAllItemsAndSubitems()
		for item in items:
			for subitem in item.subItems:
				# self.scrollToItem(subitem)
				for i in range(subitem.columnCount()):
					action(subitem, i)

	def applyToAddress(self, address, action):

		self.applyToAllCells(
			lambda subitem, i: action(subitem, i)
			if int(subitem.text(2), 16) == address and subitem.isBPEnabled
			else None
		)

	def applyToACell(self, action):
		items = self.getAllItemsAndSubitems()
		for item in items:
			for subitem in item.subItems:
				for i in range(subitem.columnCount()):
					action(subitem, i)

	def applyToID(self, id, action):
		self.applyToAllCells(
			lambda subitem, i: action(subitem, i)
			if str(subitem.text(0)) == id
			else None
		)

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

	# def clearPC(self):
	#     self.applyToAllCells(lambda subitem, i: subitem.setBackground(i, ConfigClass.colorTransparent))

	# FIXME: SET and READ row no so we don't have to loop all rows
	def clearPC(self):
		items = self.getAllItemsAndSubitems()
		for item in items:
			for subitem in item.subItems:
				for i in range(subitem.columnCount()):
					subitem.setBackground(i, ConfigClass.colorTransparent)

	def setPC(self, address, setPCColor=True):
		# logDbgC(f"BPWidget.setPC({address}, {setPCColor}) ...")
		try:
			if isinstance(address, str):
				pc_address = int(address, 16)
			else:
				pc_address = address
		except Exception as e:
			logDbgC(f"Exception while breakpointTreeWidget.setPC: {e} ...")
			return

		logDbgC(f"BPWidget.setPC({pc_address}, {setPCColor}) AFTER ...")

		bgColor = QColor(SettingsHelper().getValue(SettingsValues.SelectedRowColor))
		self.applyToAddress(
			pc_address,
			lambda subitem, i: (subitem.setBackground(i, bgColor), self.scrollToItem(subitem))[
				0] if setPCColor else subitem.setBackground(i, ConfigClass.colorTransparent)
		)
		# # self.vi
		# items = self.getAllItemsAndSubitems()
		# for item in items:
		#     for subitem in item.subItems:
		#         # for i in range(subitem.columnCount()):
		#         if subitem.text(2) == address:
		#             self.scrollToItem(item, subitem)
		#             break

	def updateBreakpointValues(self, bl):
		bp = bl.GetBreakpoint()
		logDbgC(f"updateBreakpointValues({bp}) ...")
		rootItem = self.invisibleRootItem()
		for childPar in range(rootItem.childCount()):
			parentItem = rootItem.child(childPar)
			if parentItem.text(0) == str(bp.GetID()):
				parentItem.setText(4, str(bp.GetHitCount()))
				#     # if parentItem.text(4) != str(arrBPHits.get(str(bp.GetID()))):
				#     #     parentItem.setText(4, str(arrBPHits.get(str(bp.GetID()))))
				#     sHitCount = str(bp.GetHitCount())
				#     if parentItem.text(4) != sHitCount:
				#         parentItem.setText(4, sHitCount)
				for childChild in range(parentItem.childCount()):
					childItem = parentItem.child(childChild)
					if childItem != None:
						if childItem.text(0) == str(bp.GetID()) + "." + str(bl.GetID()):
							sHitCount = str(bl.GetHitCount())
							if childItem.text(4) != sHitCount:
								childItem.setText(4, sHitCount)

				# # if breakpoint.GetNumLocations() == 1:
				# # 	bp_loc = breakpoint.GetLocationAtIndex(0)
				# # else:
				# # 	bp_loc_id = thread.GetStopReasonDataAtIndex(1)
				# # 	bp_loc = breakpoint.FindLocationByID(bp_loc_id)
				# #
				# # print(f"bp_loc.GetID() => {bp_loc.GetID()}")
				# # # if(breakpoint.GetCondition() != ""):
				# # print(arrBPConditions)
				# # print(breakpoint.GetID())
				# bpCond = arrBPConditions.get(str(bp.GetID()))  # + "." + str(bp.GetID()))
				# bpHit = arrBPHits.get(str(bp.GetID()))
				# if bpHit is not None and bpHit != "":
				#     # if bp.GetCondition() != None and str(bp.GetCondition()) != "":
				#     if parentItem.text(4) != str(bpHit):
				#         parentItem.setText(4, str(bpHit))
				#     # print("SETTING HITCOUNT TO VAL (bpHit)")
				# else:
				#     if parentItem.text(4) != "":
				#         # print("SETTING HITCOUNT TO EMPTY (bpHit)")
				#         parentItem.setText(4, "")
				#
				# if bpCond is not None and bpCond != "":
				#     # if bp.GetCondition() != None and str(bp.GetCondition()) != "":
				#     if parentItem.text(5) != str(bpCond):
				#         parentItem.setText(5, str(bpCond))
				#     # print("SETTING CONDITION TO VAL (BP)")
				# else:
				#     if parentItem.text(5) != "":
				#         # print("SETTING CONDITION TO EMPTY (BP)")
				#         parentItem.setText(5, "")
				#
				# idx = 0
				# for bl in bp:
				#     for childChild in range(parentItem.childCount()):
				#         childItem = parentItem.child(childChild)
				#         if childItem != None:
				#             if childItem.text(0) == str(bp.GetID()) + "." + str(bl.GetID()):
				#                 if arrBPHits.get(
				#                         str(bp.GetID()) + "." + str(bl.GetID())) is not None and childItem.text(
				#                         4) != str(arrBPHits.get(str(bp.GetID()) + "." + str(bl.GetID()))):
				#                     # childItem.setText(4, str(arrBPHits.get(str(bp.GetID()) + "." + str(bl.GetID()))))
				#                     childItem.setText(4, str(bl.GetHitCount()))
				#                 else:
				#                     childItem.setText(4, str(bl.GetHitCount()))
				#                 bpCondBL = arrBPConditions.get(str(bp.GetID()) + "." + str(bl.GetID()))
				#                 if bpCondBL is not None and str(bpCondBL) != "":
				#                     # if bl.GetCondition() != None and str(bl.GetCondition()) != "":
				#                     if childItem.text(5) != str(bpCondBL):
				#                         childItem.setText(5, str(bpCondBL))
				#                         print("SETTING CONDITION TO VAL (BL)")
				#                 else:
				#                     if childItem.text(5) != "":
				#                         print("SETTING CONDITION TO EMPTY (BL)")
				#                         childItem.setText(5, "")
				#                 break
				#     idx += 1
				# break
