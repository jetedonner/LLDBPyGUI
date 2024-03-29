#!/usr/bin/env python3

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from dbg.fileInfos import *

from config import *

class FileStructureTreeWidget(QTreeWidget):
	
#	actionShowMemory = None
	
	def __init__(self):
		super().__init__()
#       self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
		self.context_menu = QMenu(self)
		actionShowInfos = self.context_menu.addAction("Show infos")
		
		self.actionShowMemoryFrom = self.context_menu.addAction("Show memory")
		self.actionShowMemoryTo = self.context_menu.addAction("Show memory after End")
		
		self.setFont(ConfigClass.font)
		self.setHeaderLabels(['Sections / Symbols', 'Address From', 'Address To', 'File-Size', 'Byte-Size', 'Type'])
		self.header().resizeSection(0, 196)
		self.header().resizeSection(1, 128)
		self.header().resizeSection(2, 128)
		self.header().resizeSection(3, 128)
		self.header().resizeSection(4, 256)
		
	def contextMenuEvent(self, event):
		# Show the context menu
		self.context_menu.exec(event.globalPos())
		
		
class FileStructureWidget(QWidget):
	
#	actionShowMemory = None
	
	def __init__(self, driver):
		super().__init__()
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
			print(f"cmbModules_changed => {index}")
			self.loadFileStruct(index)
		
	def loadFileStruct(self, index):
		# self.thread.GetFrameAtIndex(1)
		target = self.driver.getTarget()
		process = target.GetProcess()
		self.thread = process.GetThreadAtIndex(0)
		self.treFile.clear()
		module = self.thread.GetFrameAtIndex(index).GetModule()
		for sec in module.section_iter():
			sectionNode = QTreeWidgetItem(self.treFile, [sec.GetName(), str(hex(sec.GetFileAddress())), str(hex(sec.GetFileAddress() + sec.GetByteSize())), hex(sec.GetFileByteSize()), hex(sec.GetByteSize()), SectionTypeString(sec.GetSectionType()) + " (" + str(sec.GetSectionType()) + ")"])
			
			for idx3 in range(sec.GetNumSubSections()):
	#									print(sec.GetSubSectionAtIndex(idx3).GetName())
				
				subSec = sec.GetSubSectionAtIndex(idx3)
				
				subSectionNode = QTreeWidgetItem(sectionNode, [subSec.GetName(), str(hex(subSec.GetFileAddress())), str(hex(subSec.GetFileAddress() + subSec.GetByteSize())), hex(subSec.GetFileByteSize()), hex(subSec.GetByteSize()), SectionTypeString(subSec.GetSectionType()) + " (" + str(subSec.GetSectionType()) + ")"])
				
				for sym in module.symbol_in_section_iter(subSec):
					subSectionNode2 = QTreeWidgetItem(subSectionNode, [sym.GetName(), str(hex(sym.GetStartAddress().GetFileAddress())), str(hex(sym.GetEndAddress().GetFileAddress())), hex(sym.GetSize()), '', f'{SymbolTypeString(sym.GetType())} ({sym.GetType()})'])