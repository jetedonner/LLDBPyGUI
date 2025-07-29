#!/usr/bin/env python3
import lldb

import json
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets
from ui.baseTreeWidget import *

from config import *

class StatisticsTreeWidget(BaseTreeWidget):
	
	def __init__(self, driver):
		super().__init__(driver)
		# self.driver = driver
#       self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
		self.context_menu = QMenu(self)
		actionShowInfos = self.context_menu.addAction("Show infos")
		self.setHeaderLabels(['Key', 'Value', 'Type'])
		self.setFont(ConfigClass.font)
		self.header().resizeSection(0, 396)
		self.header().resizeSection(1, 512)
		self.header().resizeSection(2, 96)
		
	def contextMenuEvent(self, event):
		# Show the context menu
		self.context_menu.exec(event.globalPos())
	
	def loadFileStats(self):
		statistics = self.driver.getTarget().GetStatistics()
		stream = lldb.SBStream()
		success = statistics.GetAsJSON(stream)
		if success:
			self.loadJSON(str(stream.GetData()))
			
	def loadJSONCallback(self, json_string):
		json_data = json.loads(json_string)
		self.populate_tree(json_data, self)
		QApplication.processEvents()
		
	def populate_tree(self, json_data, parent):
		try:
			if isinstance(json_data, str) or isinstance(json_data, int) or isinstance(json_data, float) or isinstance(json_data, bool):
				child_item = QTreeWidgetItem(parent, [str(json_data), '', ''])
				child_item.setExpanded(True)
			elif isinstance(json_data, tuple):
				tp = tuple(json_data)
				for innerItem in range(len(tp)):
					self.populate_tree(tp[innerItem], parent)
			else:
				for key, value in json_data.items():
					if isinstance(value, dict):
						child_item = QTreeWidgetItem(parent, [str(key), '', ''])
						child_item.setExpanded(True)
						self.populate_tree(value, child_item)
					elif isinstance(value, list):
						idx = 0
						child_item = QTreeWidgetItem(parent, [str(key), '', ''])
						child_item.setExpanded(True)
						appendStr = ""
						for innerItem in value:
							idx += 1
							if key == "modules":
								for key2, value2 in innerItem.items():
									if key2 == "path":
										appendStr = value2
										break
							child_item2 = QTreeWidgetItem(child_item, [str(idx) + " " + appendStr, '', ''])
#							child_item2.setExpanded(True)
							self.populate_tree(innerItem, child_item2)
						child_item.setText(0, child_item.text(0) + " (" + str(idx) + ")")
					else:
						valStr = str(value)
						if isinstance(value, int):
							valStr += " (" + hex(value) + ")"
						child_item = QTreeWidgetItem(parent, [str(key), valStr, str(type(value).__name__)])
						child_item.setExpanded(True)
		except Exception as e:
			print(f"Exception while parsing JSON: {e}")