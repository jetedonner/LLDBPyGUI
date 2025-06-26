#!/usr/bin/env python3

import lldb

import array
#from enum import Enum
import enum

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from ui.customQt.QHexTableWidget import *
from ui.customQt.QHexTextEdit import *

class QMemoryViewer(QWidget):
	
	driver = None
	byteGrouping = ByteGrouping.TwoChars
	startAddress = None
	hexData = None
	
	def __init__(self, driver, parent=None):
		QWidget.__init__(self, parent=parent)
		
		self.driver = driver
		
		self.layMain = QVBoxLayout()
		self.layMemViewer = QHBoxLayout()
		self.gbpMemViewer = QGroupBox("Memory viewer")
		self.gbpMemViewer.setLayout(self.layMemViewer)
		
		self.lblMemAddr = QLabel("Address:")
		self.lblMemAddr.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.layMemViewer.addWidget(self.lblMemAddr)
		
		self.txtMemAddr = QLineEdit()
		self.txtMemAddr.setStyleSheet("""
			QLineEdit {
				background-color: #282c34; /* Dark background */
				color: #abb2bf; /* Light grey text */
				border: 1px solid #3e4452;
				border-radius: 5px;
				padding: 5px;
				font: 12px 'Courier New';
			}
		""")
		self.txtMemAddr.setText("0x100003f50")
		self.txtMemAddr.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.txtMemAddr.returnPressed.connect(self.click_ReadMemory)
		self.layMemViewer.addWidget(self.txtMemAddr)
		
		self.lblMemSize = QLabel("Size:")
		self.lblMemSize.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.layMemViewer.addWidget(self.lblMemSize)
		
		self.txtMemSize = QLineEdit()
		self.txtMemSize.setStyleSheet("""
			QLineEdit {
				background-color: #282c34; /* Dark background */
				color: #abb2bf; /* Light grey text */
				border: 1px solid #3e4452;
				border-radius: 5px;
				padding: 5px;
				font: 12px 'Courier New';
			}
		""")
		self.txtMemSize.setText("0x100")
		self.txtMemSize.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.txtMemSize.returnPressed.connect(self.click_ReadMemory)
		self.layMemViewer.addWidget(self.txtMemSize)
		
		self.cmdViewAddr = QPushButton("View memory")
		self.cmdViewAddr.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.cmdViewAddr.clicked.connect(self.click_ReadMemory)
		self.layMemViewer.addWidget(self.cmdViewAddr)
		
		self.lblGrouping = QLabel("Grouping:")
		self.layMemViewer.addWidget(self.lblGrouping)
		
		self.cmbGrouping = QComboBox()
		
		# Access member names from the `__members__` dictionary
		member_names = list(ByteGrouping.__members__.keys())
		
		# Add names to the combo box
		self.cmbGrouping.addItems(member_names)
		self.cmbGrouping.setCurrentIndex(1)
		self.cmbGrouping.currentIndexChanged.connect(self.cmbGrouping_changed)
		
		self.layMemViewer.addWidget(self.cmbGrouping)
		
#		self.formattedTextEdit = FormattedTextEdit()
#		self.layMemViewer.addWidget(self.formattedTextEdit)
		
		
		
		self.layMemViewer.addStretch(0)
		
		self.layMain.addWidget(self.gbpMemViewer)
		
		self.tblHex = QHexTableWidget()
		self.tblHex.sigChanged.connect(self.handle_sigChanged)
		self.layMain.addWidget(self.tblHex)
		self.setLayout(self.layMain)
		
	def handle_sigChanged(self, start_pos, end_pos, edited_text):
#		self.formatGrouping()
		pass
		
	def resetContent(self):
		self.tblHex.resetContent()
		
#	def handle_showMemoryFor(self):
#		sender = self.sender()  # get the sender object
#		if isinstance(sender, QAction):
#			action = sender  # it's the QAction itself
#		else:
#			# Find the QAction within the sender (e.g., QMenu or QToolBar)
#			action = sender.findChild(QAction)
#			
#		self.doReadMemory(self.quickToolTip.get_memory_address(self.driver.debugger, action.data()))
##		print(f"Triggering QAction: {action.text()}")
		
	def doReadMemory(self, address, size = 0x100):
#		self.window().tabWidgetDbg.setCurrentWidget(self.window().tabMemory)
		self.txtMemAddr.setText(hex(address))
		self.txtMemSize.setText(hex(size))
		try:
#           global debugger
#			self.handle_readMemory(self.driver.debugger, int(self.window().tblHex.txtMemAddr.text(), 16), int(self.window().tblHex.txtMemSize.text(), 16))
			self.handle_readMemory(self.driver.debugger, address, size)
		except Exception as e:
			print(f"Error while reading memory from process: {e}")
			
			
	def cmbGrouping_changed(self, currentIdx:int):
		idx = 0
		for member in ByteGrouping:
			if idx == currentIdx:
				self.byteGrouping = member
				self.formatGrouping()
				break
			idx += 1
				
	def formatGrouping(self):
		self.tblHex.resetContent()
		if self.hexData != None:
			for i in range(0, len(self.hexData), 16):
				rawData = ""
				current_values = self.hexData[i:i+16]
				print(f'current_values => {current_values} => len: {len(current_values)}')
				for single in current_values:
					integer_value = int(single, 16)
					utf_8_char = chr(integer_value)
					rawData += utf_8_char
				print(f'rawData => {rawData} => len: {len(rawData)}')
				current_string = self.formatHexStringFourChars(' '.join(current_values), self.byteGrouping)
				self.tblHex.addRow(hex(self.startAddress + i), current_string, rawData)
			
	def click_ReadMemory(self):
		try:
			self.handle_readMemory(self.driver.debugger, int(self.txtMemAddr.text(), 16), int(self.txtMemSize.text(), 16))
		except Exception as e:
			print(f"Error while reading memory from process: {e}")
			
	def handle_readMemory(self, debugger, address, data_size = 0x100):
		error_ref = lldb.SBError()
		process = debugger.GetSelectedTarget().GetProcess()
		memory = process.ReadMemory(address, data_size, error_ref)
		if error_ref.Success():
			self.setTxtHex(memory, True, int(self.txtMemAddr.text(), 16))
		else:
			print(str(error_ref))
			

	def formatHexStringFourChars(self, hex_string, grouping):
		
		no_space_text = hex_string.replace(" ", "")
		strLen = len(no_space_text)
		
		if grouping == ByteGrouping.NoGrouping:
			return no_space_text
		elif grouping == ByteGrouping.TwoChars:
			hex_pairs = re.findall(r'..', no_space_text)
		elif grouping == ByteGrouping.FourChars:
			hex_pairs = re.findall(r'....', no_space_text)
		elif grouping == ByteGrouping.EightChars:
			hex_pairs = re.findall(r'........', no_space_text)
		else:
			hex_pairs = ""
			
		if len(hex_pairs) < (strLen / grouping.value[1]):
			return hex_string

		formatted_string = ' '.join(hex_pairs)
		
		return formatted_string
	
	def setTxtHex(self, txtInBytes, showAddress = True, startAddress:int = 0):
		self.tblHex.resetContent()
		try:
			self.startAddress = startAddress
			self.hexData = [format(byte, '02x') for byte in txtInBytes]
			self.formatGrouping()
		except Exception as e:
			print(f"Exception: '{e}' while converting bytes '{txtInBytes}' to HEX string")
			pass