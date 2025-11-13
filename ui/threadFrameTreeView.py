#!/usr/bin/env python3

from config import *
from lib.fileInfos import GuessLanguage
from ui.base.baseTreeWidget import *


class ThreadFrameTreeWidget(BaseTreeWidget):
	#	actionShowMemory = None
	process = None
	thread = None

	def __init__(self, driver):
		super().__init__(None)
		self.driver = driver
		#       self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
		self.context_menu = QMenu(self)
		actionShowInfos = self.context_menu.addAction("Show infos")

		self.actionShowMemoryFrom = self.context_menu.addAction("Show memory")
		self.actionShowMemoryTo = self.context_menu.addAction("Show memory after End")

		self.setFont(ConfigClass.font)
		self.setHeaderLabels(['Num / ID', 'Hex ID', 'Process / Thread / Frame', 'PC', 'Language (guess)'])
		self.header().resizeSection(0, 148)
		self.header().resizeSection(1, 128)
		self.header().resizeSection(2, 512)
		self.header().resizeSection(3, 128)

	#		self.doubleClicked.connect(self.handle_doubleClick)

	def contextMenuEvent(self, event):
		self.context_menu.exec(event.globalPos())

	def mouseDoubleClickEvent(self, event):
		daItem = self.itemAt(event.pos().x(), event.pos().y())
		if daItem is None:
			return

		col = self.columnAt(event.pos().x())
		if (col == 2 or col == 3) and daItem.text(3) is not None and daItem.text(3) != "":
			# self.window().doReadMemory(int(daItem.text(col), 16))
			self.window().wdtDisassembly.tblDisassembly.viewAddress(daItem.text(3))

	def loadStacktrace(self):
		self.process = self.driver.target.GetProcess()
		self.thread = self.process.GetThreadAtIndex(0)

		idx = 0
		if self.thread:
			self.clear()
			self.processNode = QTreeWidgetItem(self, ["#0 " + str(self.process.GetProcessID()),
													  hex(self.process.GetProcessID()) + "",
													  self.process.GetTarget().GetExecutable().GetFilename(), '', ''])
			self.threadNode = QTreeWidgetItem(self.processNode, ["#" + str(idx) + " " + str(self.thread.GetThreadID()),
																 hex(self.thread.GetThreadID()) + "",
																 self.thread.GetQueueName(), '', ''])
			numFrames = self.thread.GetNumFrames()

			for idx2 in range(numFrames):
				frame = self.thread.GetFrameAtIndex(idx2)
				frameNode = QTreeWidgetItem(self.threadNode,
											["#" + str(frame.GetFrameID()), "", str(frame.GetPCAddress()),
											 str(hex(frame.GetPC())), GuessLanguage(frame)])
				idx += 1

			self.processNode.setExpanded(True)
			self.threadNode.setExpanded(True)
		QApplication.processEvents()
