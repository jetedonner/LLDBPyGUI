#!/usr/bin/env python3

from config import *
from lib.fileInfos import *
from lib.utils import *
from ui.base.baseTreeWidget import *


# from ui.helper.lldbutil import symbol_type_to_str


class FileStructureTreeWidget(BaseTreeWidget):
	#	actionShowMemory = None

	selectedModule = None

	def __init__(self):
		super().__init__(None)
		self.setContentsMargins(0, 0, 0, 0)
		self.setContentsMargins(0, 0, 0, 0)
		#       self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
		# 		self.context_menu = QMenu(self)
		self.context_menu.addSeparator()
		actionShowInfos = self.context_menu.addAction("Show infos")

		self.actionShowMemoryFrom = self.context_menu.addAction("Show memory")
		self.actionShowMemoryFrom.triggered.connect(self.handle_showMemory)
		self.actionShowMemoryTo = self.context_menu.addAction("Show memory after End")
		self.actionShowMemoryTo = self.context_menu.addSeparator()
		self.actionSetBP = self.context_menu.addAction("Set breakpoint")
		self.actionSetBP.triggered.connect(self.handle_setbp)

		self.setFont(ConfigClass.font)
		self.setHeaderLabels(
			['Sections / Symbols', 'Load From', 'Load To', 'File From', 'File To', 'File-Size', 'Byte-Size', 'Type'])
		self.header().resizeSection(0, 316)
		self.header().resizeSection(1, 128)
		self.header().resizeSection(2, 128)
		self.header().resizeSection(3, 128)
		self.header().resizeSection(4, 128)
		self.header().resizeSection(5, 128)
		self.header().resizeSection(6, 256)

	def handle_setbp(self, event=None):
		daItem = self.currentItem()
		if daItem:
			modName = (self.selectedModule.GetFileSpec().GetFilename() if self.selectedModule is not None else "")
			addr = daItem.text(3)
			# self.window().driver.debugger.HandleCommand(f"br set -a {daItem.text(1)} -s SwiftREPLTestApp.debug.dylib")
			logDbgC(f"modName: {modName} => br set -a {addr} -s {modName}")
			self.window().driver.debugger.HandleCommand(f"br set -a {addr} -s {modName}")
		# self.window().updateStatusBar(f"Set breakpoint @ {addr} in module: {modName} ...")
		# # Set breakpoint by address
		# # self.selectedModule
		# bp = target.BreakpointCreateByAddress(address.GetLoadAddress(target))
		# if bp.IsValid() and bp.GetNumLocations() > 0:
		# 	result.PutCString(f"✅ Breakpoint set at address: 0x{address.GetLoadAddress(target):x}")
		# else:
		# 	result.PutCString("⚠️ Breakpoint could not be resolved at address.")
		pass

	def mouseDoubleClickEvent(self, event):
		daItem = self.itemAt(event.pos().x(), event.pos().y())
		if daItem is None:
			return

		col = self.columnAt(event.pos().x())
		# if daItem.childCount() > 0:
		# 	super().mouseDoubleClickEvent(event)

		if col == 1 or col == 2 or col == 3 or col == 4:
			self.window().handle_showMemory(
				daItem.text(col))  # .doReadMemory(int(daItem.text(1), 16), int(daItem.text(3), 16))
		# 		self.openPersistentEditor(daItem, col)
		# 		self.editItem(daItem, col)
		elif col == 0 and daItem.parent() is not None and daItem.parent().text(
				0) == "__text" and daItem.childCount() == 0:
			# self.window().tabWidgetMain.setCurrentWidget(self.window().splitter)
			# self.window().txtMultiline.viewAddress(daItem.text(1))
			pass
		pass

	def handle_showMemory(self):
		daItem = self.currentItem()

		self.window().handle_showMemory(daItem.text(self.currentColumn()))
	# # if daItem.childCount() > 0:
	# # 	daItem = daItem.child(0)
	# # setStatusBar(f"Deleted breakpoint @: {daItem.text(2)}")
	# self.window().doReadMemory(int(daItem.text(1), 16), int(daItem.text(3), 16))
	# # self.doReadMemory(addr)
	# pass
	#
	#
	# if len(self.selectedItems()) > 0 and self.item(self.selectedItems()[0].row(), 3) != None:
	# 	self.window().handle_showMemory(self.item(self.selectedItems()[0].row(),
	# 											  3).text())  # tabWidgetMain.setCurrentIndex(self.window().idxMemTab) # , True

# def contextMenuEvent(self, event):
# 	# Show the context menu
# 	self.context_menu.exec(event.globalPos())


class FileStructureWidget(QWidget):
	#	actionShowMemory = None
	thread = None

	def __init__(self, driver):
		super().__init__()
		self.thread = None

		self.setContentsMargins(0, 0, 0, 0)
		self.driver = driver
		self.wdtFile = QWidget()
		self.wdtFile.setContentsMargins(0, 0, 0, 0)
		self.layFile = QHBoxLayout()
		self.layFile.setContentsMargins(0, 0, 0, 0)
		self.wdtFile.setLayout(self.layFile)
		self.treFile = FileStructureTreeWidget()
		self.treFile.setContentsMargins(0, 0, 0, 0)
		self.cmbModules = QComboBox()
		self.cmbModules.setContentsMargins(0, 0, 0, 0)
		self.cmbModules.currentIndexChanged.connect(self.cmbModules_changed)
		self.lblModule = QLabel("Module:")
		self.lblModule.setContentsMargins(0, 0, 0, 0)
		self.lblModule.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.layFile.addWidget(self.lblModule)
		self.cmbModules.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		self.layFile.addWidget(self.cmbModules)
		self.setLayout(QVBoxLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().addWidget(self.wdtFile)
		self.layout().addWidget(self.treFile)

	def resetContent(self):
		self.cmbModules.clear()
		self.treFile.clear()

	def cmbModules_changed(self, index):
		if index >= 0:
			modules = self.driver.target.modules
			if modules is not None and len(modules) > index:
				self.treFile.clear()
				module = modules[index]
				self.addFileStructInfo(module)
			else:
				self.loadFileStruct(index)

	def loadFileStruct(self, index=0):
		target = self.driver.target
		# logDbgC(f"loadFileStruct => target: {target}", DebugLevel.Verbose)
		process = target.GetProcess()
		# logDbgC(f"loadFileStruct => process: {process}", DebugLevel.Verbose)
		# logDbgC(f"loadFileStruct => process.num_threads: {process.num_threads}", DebugLevel.Verbose)
		self.thread = process.GetThreadAtIndex(index)
		self.treFile.clear()
		# logDbgC(f"loadFileStruct => thread: {self.thread}", DebugLevel.Verbose)
		# logDbgC(f"loadFileStruct => thread.num_frames: {self.thread.num_frames}", DebugLevel.Verbose)
		for i in range(self.thread.num_frames):
			module = self.thread.GetFrameAtIndex(i).GetModule()
			self.addFileStructInfo(module)

	def addFileStructInfo(self, module):
		self.treFile.selectedModule = module
		for sec in module.section_iter():
			sectionNode = QTreeWidgetItem(self.treFile,
										  [sec.GetName(), str(hex(sec.GetLoadAddress(self.driver.target))),
										   str(hex(sec.GetLoadAddress(self.driver.target) + sec.size)),
										   str(hex(sec.GetFileAddress())),
										   str(hex(sec.GetFileAddress() + sec.GetByteSize())),
										   hex(sec.GetFileByteSize()), hex(sec.GetByteSize()),
										   SectionTypeString(sec.GetSectionType()) + " (" + str(
											   sec.GetSectionType()) + ")"])

			for idx3 in range(sec.GetNumSubSections()):
				#									print(sec.GetSubSectionAtIndex(idx3).GetName())

				subSec = sec.GetSubSectionAtIndex(idx3)

				subSectionNode = QTreeWidgetItem(sectionNode,
												 [subSec.GetName(), str(hex(subSec.GetLoadAddress(self.driver.target))),
												  str(hex(subSec.GetLoadAddress(self.driver.target) + subSec.size)),
												  str(hex(subSec.GetFileAddress())),
												  str(hex(subSec.GetFileAddress() + subSec.GetByteSize())),
												  hex(subSec.GetFileByteSize()), hex(subSec.GetByteSize()),
												  SectionTypeString(subSec.GetSectionType()) + " (" + str(
													  subSec.GetSectionType()) + ")"])

				for sym in module.symbol_in_section_iter(subSec):
					subSectionNode2 = QTreeWidgetItem(subSectionNode, [sym.GetName(), str(hex(
						getLoadAddress(sym.GetStartAddress(), self.driver.target))), str(hex(
						getLoadAddress(sym.GetEndAddress(), self.driver.target))),
																	   str(hex(sym.GetStartAddress().GetFileAddress())),
																	   str(hex(sym.GetEndAddress().GetFileAddress())),
																	   hex(sym.GetSize()), '',
																	   f'{SymbolTypeString(sym.GetType())} ({sym.GetType()})'])

	def loadModulesCallback(self, frame, modules=None):
		logDbgC(f"RELOADED MODULES")
		self.cmbModules.clear()
		if modules is not None and len(modules) > 0:
			for i in range(len(modules)):
				self.cmbModules.addItem(modules[i].GetFileSpec().GetFilename() + " (" + str(i) + ")")
		else:
			self.cmbModules.addItem(
				frame.GetModule().GetFileSpec().GetFilename() + " (" + str(frame.GetFrameID()) + ")")
