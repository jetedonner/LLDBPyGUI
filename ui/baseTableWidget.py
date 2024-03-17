#!/usr/bin/env python3

from PyQt6.QtWidgets import *

class BaseTableWidget(QTableWidget):
	
	def __init__(self):
		super().__init__()
		
	def getSelectedRow(self):
		if self.selectedItems() != None and len(self.selectedItems()) > 0:
			return self.selectedItems()[0].row()
		return None
	
	def getSelectedItem(self, col):
		selRow = self.getSelectedRow()
		if selRow != None:
			return self.item(selRow, col)
		return None