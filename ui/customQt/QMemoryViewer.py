#!/usr/bin/env python3

import lldb

# from helper..dbgOutputHelper import logDbgC
from helper.debugHelper import logDbgC
from ui.customQt.QHexLineEdit import QHexLineEdit
from ui.customQt.QHexTableWidget import *
from ui.customQt.QHexTextEdit import *


# from enum import Enum


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

		self.txtMemAddr = QHexLineEdit() # QLineEdit()
		# hex_validator = QRegularExpressionValidator(QRegularExpression("^0x[0-9a-fA-F]*$")) #  QRegularExpression("^[0-9a-fA-F]*$"))
		# self.txtMemAddr.setValidator(hex_validator)

		# self.txtMemAddr.setStyleSheet("""
		# 	QLineEdit {
		# 		background-color: #282c34; /* Dark background */
		# 		color: #abb2bf; /* Light grey text */
		# 		border: 1px solid #3e4452;
		# 		border-radius: 5px;
		# 		padding: 5px;
		# 		font: 12px 'Courier New';
		# 	}
		# """)
		self.txtMemAddr.setText("0x100003f50")
		self.txtMemAddr.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.txtMemAddr.returnPressed.connect(self.click_ReadMemory)
		self.layMemViewer.addWidget(self.txtMemAddr)

		self.cmdBack = QPushButton("<")
		self.cmdBack.setToolTip(f"Go back to previous memory location")
		self.cmdBack.clicked.connect(self.cmdBack_clicked)
		self.layMemViewer.addWidget(self.cmdBack)
		self.cmdForward = QPushButton(">")
		self.cmdForward.setToolTip(f"Go forward to next memory location")
		self.cmdForward.clicked.connect(self.cmdForward_clicked)
		self.layMemViewer.addWidget(self.cmdForward)

		self.lblMemSize = QLabel("Size:")
		self.lblMemSize.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.layMemViewer.addWidget(self.lblMemSize)

		self.txtMemSize = QHexLineEdit() # QLineEdit()
		# self.txtMemSize.setValidator(hex_validator)
		# self.txtMemSize.setStyleSheet("""
		# 	QLineEdit {
		# 		background-color: #282c34; /* Dark background */
		# 		color: #abb2bf; /* Light grey text */
		# 		border: 1px solid #3e4452;
		# 		border-radius: 5px;
		# 		padding: 5px;
		# 		font: 12px 'Courier New';
		# 	}
		# """)
		self.txtMemSize.setText(str(ConfigClass.defaultMemJumpDist))
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

		# self.cmdBack = QPushButton("<")
		# self.cmdBack.setToolTip(f"Go back to previous memory location")
		# self.cmdBack.clicked.connect(self.cmdBack_clicked)
		# self.layMemViewer.addWidget(self.cmdBack)
		# self.cmdForward = QPushButton(">")
		# self.cmdForward.setToolTip(f"Go forward to next memory location")
		# self.cmdForward.clicked.connect(self.cmdForward_clicked)
		# self.layMemViewer.addWidget(self.cmdForward)
		self.layMemViewer.addStretch(0)
		self.layMain.addWidget(self.gbpMemViewer)

		self.tblHex = QHexTableWidget()
		self.tblHex.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.tblHex.sigChanged.connect(self.handle_sigChanged)
		self.layMain.addWidget(self.tblHex)
		self.setLayout(self.layMain)

	isUpdateing = False

	def handle_sigChanged(self, start_pos, end_pos, edited_text):
		pass

	def resetContent(self):
		self.tblHex.resetContent()

	def cmdBack_clicked(self):
		currAddr = self.txtMemAddr.text()
		if currAddr and currAddr != "":
			try:
				currAddr = int(currAddr, 16)
				currSize = self.txtMemSize.text()
				size = ConfigClass.defaultMemJumpDist
				if currSize and currSize != "":
					size = int(currSize, 16)

				if currAddr > ConfigClass.defaultMemJumpDist:
					self.txtMemAddr.setText(hex(currAddr - ConfigClass.defaultMemJumpDist))
					self.doReadMemory(currAddr - ConfigClass.defaultMemJumpDist, size)
				else:
					self.doReadMemory(0, size)
			except Exception as e:
				print(f"Error while reading memory from process: {e}")
		pass

	def cmdForward_clicked(self):
		currAddr = self.txtMemAddr.text()
		if currAddr and currAddr != "":
			try:
				currAddr = int(currAddr, 16)
				currSize = self.txtMemSize.text()
				size = ConfigClass.defaultMemJumpDist
				if currSize and currSize != "":
					size = int(currSize, 16)

				if currAddr < 0xFFFFFFFFFFFFFFFF - ConfigClass.defaultMemJumpDist:
					self.txtMemAddr.setText(hex(currAddr + ConfigClass.defaultMemJumpDist))
					self.doReadMemory(currAddr + ConfigClass.defaultMemJumpDist, size)
				else:
					self.doReadMemory(0xFFFFFFFFFFFFFFFF, size)
			except Exception as e:
				print(f"Error while reading memory from process: {e}")

	def doReadMemory(self, address, size=0x100):
		self.txtMemAddr.setText(hex(address))
		self.txtMemSize.setText(hex(size))
		try:
			self.handle_readMemory(self.driver.debugger, address, size)
		except Exception as e:
			print(f"Error while reading memory from process: {e}")

	def cmbGrouping_changed(self, currentIdx: int):
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
				current_values = self.hexData[i:i + 16]
				# print(f'current_values => {current_values} => len: {len(current_values)}')
				for single in current_values:
					integer_value = int(single, 16)
					utf_8_char = chr(integer_value)
					rawData += utf_8_char
				# print(f'rawData => {rawData} => len: {len(rawData)}')
				current_string = self.formatHexStringFourChars(' '.join(current_values), self.byteGrouping)
				self.tblHex.addRow(hex(self.startAddress + i), current_string, rawData)

	def click_ReadMemory(self):
		logDbgC(f"click_ReadMemory() in QMemoryViewer ...")
		try:
			self.handle_readMemory(self.driver.debugger, int(self.txtMemAddr.text(), 16),
								   int(self.txtMemSize.text(), 16))
		except Exception as e:
			print(f"Error while reading memory from process: {e}")

	def handle_readMemory(self, debugger, address, data_size=0x100):
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

	def setTxtHex(self, txtInBytes, showAddress=True, startAddress: int = 0):
		self.tblHex.resetContent()
		try:
			self.startAddress = startAddress
			self.hexData = [format(byte, '02x') for byte in txtInBytes]
			self.formatGrouping()
		except Exception as e:
			print(f"Exception: '{e}' while converting bytes '{txtInBytes}' to HEX string")
			pass
