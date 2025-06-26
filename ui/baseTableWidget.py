#!/usr/bin/env python3

from PyQt6.QtWidgets import *

class BaseTableWidget(QTableWidget):
	
	def __init__(self):
		super().__init__()

		self.setStyleSheet("""
		    QTableWidget {
		        /* background-color: #f0f0f0;
		        gridline-color: #ccc;
		        font: 12px 'Courier New';*/
		        background-color: #282c34; /* Dark background */
		        font: 12px 'Courier New';
                color: #abb2bf; /* Light grey text */
                /*border: 1px solid #3e4452;*/
                border-radius: 5px;
                /*padding: 10px;*/
		    }
		    QTableWidget::item {
		        /*padding: 5px;
		        color: #333;
		        background-color: #e6f2ff;*/
		        /*background-color: #282c34;*/ /* Dark background */
                color: #abb2bf; /* Light grey text */
                font: 12px 'Courier New';
                /*border: 1px solid #3e4452;
                border-radius: 5px;*/
                padding: 5px;
		    }
		    QTableWidget::item:selected {
		        /*background-color: #3399ff;
		        color: white;*/
		        /*background-color: #282c34;*/ /* Dark background */
                color: #abb2bf; /* Light grey text */
                font: 12px 'Courier New';
                /*border: 1px solid #3e4452;
                border-radius: 5px;
                padding: 10px;*/
		    }
		""")
		
	def getSelectedRow(self):
		if self.selectedItems() != None and len(self.selectedItems()) > 0:
			return self.selectedItems()[0].row()
		return None
	
	def getSelectedItem(self, col):
		selRow = self.getSelectedRow()
		if selRow != None:
			return self.item(selRow, col)
		return None