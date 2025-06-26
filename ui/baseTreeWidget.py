#!/usr/bin/env python3

from PyQt6.QtWidgets import *

class BaseTreeWidget(QTreeWidget):
	
	def __init__(self, driver):
		super().__init__()

		self.setStyleSheet("""
			QTreeWidget {
				/* background-color: #f0f0f0;
				gridline-color: #ccc;
				font: 12px 'Courier New';*/
				background-color: #282c34; /* Dark background */
				color: #abb2bf; /* Light grey text */
				font: 12px 'Courier New';
				/*border: 1px solid #3e4452;*/
				border-radius: 5px;
				/*padding: 10px;*/
			}
			QTreeWidgetItem {
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
			QTreeWidgetItem:selected {
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
		
		self.driver = driver