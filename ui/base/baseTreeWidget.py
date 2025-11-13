#!/usr/bin/env python3
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *


class BaseTreeWidget(QTreeWidget):
	allExpanded = False

	def __init__(self, driver):
		super().__init__()

		self.allExpanded = False

		self.context_menu = QMenu(self)
		self.actionToggleAllExpanded = self.context_menu.addAction("Toggle all expanded")
		self.actionToggleAllExpanded.triggered.connect(self.handle_toggleAllExpanded)

		# self.setStyleSheet("""
		# 	QTreeWidget {
		# 		/* background-color: #f0f0f0;
		# 		gridline-color: #ccc;
		# 		font: 12px 'Courier New';*/
		# 		background-color: #282c34; /* Dark background */
		# 		color: #abb2bf; /* Light grey text */
		# 		font: 12px 'Courier New';
		# 		/*border: 1px solid #3e4452;*/
		# 		border-radius: 5px;
		# 		/*padding: 10px;*/
		# 	}
		# 	QTreeWidgetItem {
		# 		/*padding: 5px;
		# 		color: #333;
		# 		background-color: #e6f2ff;*/
		# 		/*background-color: #282c34;*/ /* Dark background */
		# 		color: #abb2bf; /* Light grey text */
		# 		font: 12px 'Courier New';
		# 		/*border: 1px solid #3e4452;
		# 		border-radius: 5px;*/
		# 		padding: 5px;
		# 	}
		# 	QTreeWidgetItem:selected {
		# 		/*background-color: #3399ff;
		# 		color: white;*/
		# 		/*background-color: #282c34;*/ /* Dark background */
		# 		color: #abb2bf; /* Light grey text */
		# 		font: 12px 'Courier New';
		# 		/*border: 1px solid #3e4452;
		# 		border-radius: 5px;
		# 		padding: 10px;*/
		# 	}
		# """)

		self.driver = driver

	def contextMenuEvent(self, event):
		self.context_menu.exec(event.globalPos())

	def mousePressEvent(self, event):
		modifiers = event.modifiers()
		if modifiers & Qt.KeyboardModifier.ShiftModifier:
			index = self.indexAt(event.pos())
			if index.isValid():
				item = self.itemFromIndex(index)
				if item:
					column = index.column()
					text = item.text(column)
					QApplication.clipboard().setText(text)
					self.window().updateStatusBar(f"Copied '{text}' to clipboard ...")
				# self.window().updateStatusBar(f"Copied '{text}' to clipboard ...")
		super().mousePressEvent(event)

	def resetContent(self):
		print(f"resetContent in baseTreeWidget!!!!")
		self.clear()

	def handle_toggleAllExpanded(self):
		self.allExpanded = not self.allExpanded
		if self.allExpanded:
			self.expandAll()
		else:
			self.collapseAll()
