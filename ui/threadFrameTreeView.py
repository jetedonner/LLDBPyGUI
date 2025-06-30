#!/usr/bin/env python3

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from config import *
from ui.baseTreeWidget import *

class ThreadFrameTreeWidget(BaseTreeWidget):
	
#	actionShowMemory = None
	
	def __init__(self):
		super().__init__(None)
#       self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
		self.context_menu = QMenu(self)
		actionShowInfos = self.context_menu.addAction("Show infos")
		
		self.actionShowMemoryFrom = self.context_menu.addAction("Show memory")
		self.actionShowMemoryTo = self.context_menu.addAction("Show memory after End")
		
		self.setFont(ConfigClass.font)
		self.setHeaderLabels(['Num / ID', 'Hex ID', 'Process / Threads / Frames', 'PC', 'Lang (guess)'])
		self.header().resizeSection(0, 148)
		self.header().resizeSection(1, 128)
		self.header().resizeSection(2, 512)
		self.header().resizeSection(3, 128)
#		self.doubleClicked.connect(self.handle_doubleClick)
		
	def contextMenuEvent(self, event):
		# Show the context menu
		self.context_menu.exec(event.globalPos())
		
#	def mouseDoubleClickEvent(self, event):
#		daItem = self.itemAt(event.pos().x(), event.pos().y())
#		
#		if daItem.col
	
	def mouseDoubleClickEvent(self, event):
		daItem = self.itemAt(event.pos().x(), event.pos().y())
		if daItem == None:
			return
		col = self.columnAt(event.pos().x())
		if col == 3 and daItem.text(col) is not None and daItem.text(col) != "":
			self.window().doReadMemory(int(daItem.text(col), 16))
			
#	def handle_doubleClick(self, event):
#		if event.column() == 3:
#			self.selectedItems()[]
#			print(f"event => {event.column()}")