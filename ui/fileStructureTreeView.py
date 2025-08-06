#!/usr/bin/env python3

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets
from ui.baseTreeWidget import *
from dbg.fileInfos import *
from lib.utils import *

from config import *
from ui.helper.dbgOutputHelper import logDbg
from ui.helper.lldbutil import symbol_type_to_str


class FileStructureTreeWidget(BaseTreeWidget):
	
#	actionShowMemory = None
	
	def __init__(self):
		super().__init__(None)
#       self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
		self.context_menu = QMenu(self)
		actionShowInfos = self.context_menu.addAction("Show infos")
		
		self.actionShowMemoryFrom = self.context_menu.addAction("Show memory")
		self.actionShowMemoryFrom.triggered.connect(self.handle_showMemory)
		self.actionShowMemoryTo = self.context_menu.addAction("Show memory after End")
		self.actionShowMemoryTo = self.context_menu.addSeparator()
		self.actionSetBP = self.context_menu.addAction("Set breakpoint")
		self.actionSetBP.triggered.connect(self.handle_setbp)
		
		self.setFont(ConfigClass.font)
		self.setHeaderLabels(['Sections / Symbols', 'Load From', 'Load To', 'File From', 'File To', 'File-Size', 'Byte-Size', 'Type'])
		self.header().resizeSection(0, 166)
		self.header().resizeSection(1, 128)
		self.header().resizeSection(2, 128)
		self.header().resizeSection(3, 128)
		self.header().resizeSection(4, 128)
		self.header().resizeSection(5, 128)
		self.header().resizeSection(6, 256)

	def handle_setbp(self, event=None):
		daItem = self.currentItem()
		if daItem:
			self.window().driver.debugger.HandleCommand(f"br set -a {daItem.text(1)}  -s SwiftREPLTestApp.debug.dylib")
		pass

	def mouseDoubleClickEvent(self, event):
		daItem = self.itemAt(event.pos().x(), event.pos().y())
		if daItem is None:
			return
		col = self.columnAt(event.pos().x())
		# if daItem.childCount() > 0:
		# 	super().mouseDoubleClickEvent(event)

		if col == 1 or col == 2 or col == 3:
			self.window().doReadMemory(int(daItem.text(1), 16), int(daItem.text(3), 16))
		# 		self.openPersistentEditor(daItem, col)
		# 		self.editItem(daItem, col)
		elif col == 0 and daItem.parent().text(0) == "__text" and daItem.childCount() == 0:
			self.window().tabWidgetMain.setCurrentWidget(self.window().splitter)
			self.window().txtMultiline.viewAddress(daItem.text(1))
		pass

	def handle_showMemory(self):
		daItem = self.currentItem()
		# if daItem.childCount() > 0:
		# 	daItem = daItem.child(0)
		# setStatusBar(f"Deleted breakpoint @: {daItem.text(2)}")
		self.window().doReadMemory(int(daItem.text(1), 16), int(daItem.text(3), 16))
		# self.doReadMemory(addr)
		pass

	def contextMenuEvent(self, event):
		# Show the context menu
		self.context_menu.exec(event.globalPos())
		
		
class FileStructureWidget(QWidget):
	
#	actionShowMemory = None
	thread = None

	def __init__(self, driver):
		super().__init__()
		self.thread = None

		self.driver = driver
		self.wdtFile = QWidget()
		self.layFile = QHBoxLayout()
		self.wdtFile.setLayout(self.layFile)
		self.treFile = FileStructureTreeWidget()
#		self.treFile.actionShowMemoryFrom.triggered.connect(self.handle_showMemoryFileStructureFrom)
#		self.treFile.actionShowMemoryTo.triggered.connect(self.handle_showMemoryFileStructureTo)
		self.cmbModules = QComboBox()
		self.cmbModules.currentIndexChanged.connect(self.cmbModules_changed)
		self.lblModule = QLabel("Module:")
		self.lblModule.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.layFile.addWidget(self.lblModule)
		self.cmbModules.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		self.layFile.addWidget(self.cmbModules)
#		self.tabWidgetStruct = QWidget()
		self.setLayout(QVBoxLayout())
		self.layout().addWidget(self.wdtFile)
		self.layout().addWidget(self.treFile)
		
	def resetContent(self):
		self.cmbModules.clear()
		self.treFile.clear()
		
	def cmbModules_changed(self, index):
		if index >= 0:
			logDbgC(f"cmbModules_changed => {index}")
			# self.loadFileStruct(index)

			modules = self.driver.getTarget().modules
			if modules is not None and len(modules) > index:
				self.treFile.clear()
				module = modules[index]
				self.addFileStructInfo(module)
				# INDENT = "    "
				# INDENT2 = "        "
				# logDbgC('Number of sections: %d' % module.GetNumSections())
				# for sec in module.section_iter():
				# 	logDbgC(sec)
				# 	if sec.GetName() == "__TEXT":
				# 		# Iterates the text section and prints each symbols within each sub-section.
				# 		for subsec in sec:
				# 			logDbgC(INDENT + repr(subsec))
				# 			for sym in module.symbol_in_section_iter(subsec):
				# 				logDbgC(INDENT2 + repr(sym))
				# 				if sym.GetDisplayName():
				# 					logDbgC(INDENT2 + sym.GetDisplayName())
				#
				# 				logDbgC(INDENT2 + 'symbol tqype: %s' % symbol_type_to_str(sym.GetType()))
				# 				# address = sym.GetStartAddress()
				# 				# if address.IsValid():
				# 				# 	load_addr = address.GetLoadAddress(self.driver.getTarget())
				# 				# 	logDbgC(INDENT2 + f"Symbol load address: 0x{load_addr:x}")
				#
				# 				logDbgC(INDENT2 + f"Symbol load address: 0x{getLoadAddress(sym.GetStartAddress(), self.driver.getTarget()):x}")
				# 		break
				# # for i in range(len(modules)):
				# # 	# self.cmbModules.addItem(
				# # 	# 	modules[i].GetFileSpec().GetFilename() + " (" + str(i) + ")")
				# #
				pass
			else:
				# self.tabWidgetStruct.cmbModules.addItem(
				# 	frame.GetModule().GetFileSpec().GetFilename() + " (" + str(frame.GetFrameID()) + ")")
				self.loadFileStruct(index)
		
	def loadFileStruct(self, index = 0):
		# self.thread.GetFrameAtIndex(1)
		target = self.driver.getTarget()
		logDbgC(f"loadFileStruct => target: {target}", DebugLevel.Verbose)
		process = target.GetProcess()
		logDbgC(f"loadFileStruct => process: {process}", DebugLevel.Verbose)
		logDbgC(f"loadFileStruct => process.num_threads: {process.num_threads}", DebugLevel.Verbose)
		self.thread = process.GetThreadAtIndex(index)
		self.treFile.clear()
		logDbgC(f"loadFileStruct => thread: {self.thread}", DebugLevel.Verbose)
		logDbgC(f"loadFileStruct => thread.num_frames: {self.thread.num_frames}", DebugLevel.Verbose)

		for i in range(self.thread.num_frames):
			module = self.thread.GetFrameAtIndex(i).GetModule()
			self.addFileStructInfo(module)


	def addFileStructInfo(self, module):
		for sec in module.section_iter():
			sectionNode = QTreeWidgetItem(self.treFile, [sec.GetName(), str(hex(sec.GetLoadAddress(self.driver.getTarget()))), str(hex(sec.GetLoadAddress(self.driver.getTarget()) + sec.size)), str(hex(sec.GetFileAddress())), str(hex(sec.GetFileAddress() + sec.GetByteSize())), hex(sec.GetFileByteSize()), hex(sec.GetByteSize()), SectionTypeString(sec.GetSectionType()) + " (" + str(sec.GetSectionType()) + ")"])

			for idx3 in range(sec.GetNumSubSections()):
	#									print(sec.GetSubSectionAtIndex(idx3).GetName())

				subSec = sec.GetSubSectionAtIndex(idx3)

				subSectionNode = QTreeWidgetItem(sectionNode, [subSec.GetName(), str(hex(subSec.GetLoadAddress(self.driver.getTarget()))), str(hex(subSec.GetLoadAddress(self.driver.getTarget()) + subSec.size)), str(hex(subSec.GetFileAddress())), str(hex(subSec.GetFileAddress() + subSec.GetByteSize())), hex(subSec.GetFileByteSize()), hex(subSec.GetByteSize()), SectionTypeString(subSec.GetSectionType()) + " (" + str(subSec.GetSectionType()) + ")"])

				for sym in module.symbol_in_section_iter(subSec):
					subSectionNode2 = QTreeWidgetItem(subSectionNode, [sym.GetName(), str(hex(getLoadAddress(sym.GetStartAddress(), self.driver.getTarget()))), str(hex(getLoadAddress(sym.GetEndAddress(), self.driver.getTarget()))), str(hex(sym.GetStartAddress().GetFileAddress())), str(hex(sym.GetEndAddress().GetFileAddress())), hex(sym.GetSize()), '', f'{SymbolTypeString(sym.GetType())} ({sym.GetType()})'])