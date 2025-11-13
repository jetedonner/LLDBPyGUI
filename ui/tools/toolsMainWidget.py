import ast

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QSplitter, QTextEdit, QVBoxLayout, QPushButton, QComboBox, \
	QGroupBox

from helper.debugHelper import logDbgC
from lib.thirdParty.lldbutil import int_to_bytearray, bytearray_to_int
from ui.base.baseCleanPasteTextEdit import CleanPasteTextEdit


class ToolsMainWidget(QWidget):

	def __init__(self):
		super().__init__()

		self.setContentsMargins(0, 0, 0, 0)
		self.setLayout(QVBoxLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)
		# self.layout().addWidget(QLabel("Hello Tools ..."))

		self.splitterMain = QSplitter(Qt.Orientation.Vertical)
		self.splitterMain.setContentsMargins(0, 0, 0, 0)
		self.txtInput = CleanPasteTextEdit()
		# self.txtInput.setDocumentTitle("DocTitle")
		self.txtInput.setContentsMargins(0, 0, 0, 0)
		self.txtInput.setPlaceholderText(f"Enter input sequence ...")

		self.layInput = QVBoxLayout()
		self.layInput.setContentsMargins(0, 0, 0, 0)
		self.layInput.addWidget(self.txtInput)
		self.grpInput = QGroupBox("Input:")
		self.grpInput.setContentsMargins(0, 0, 0, 0)
		self.grpInput.setLayout(self.layInput)

		self.splitterMain.addWidget(self.grpInput)

		self.txtOutput = QTextEdit()
		self.txtOutput.setContentsMargins(0, 0, 0, 0)
		# self.txtOutput.setPlaceholderText(f"")
		self.layOutput = QVBoxLayout()
		self.layOutput.setContentsMargins(0, 0, 0, 0)
		self.layOutput.addWidget(self.txtOutput)
		self.grpOutput = QGroupBox("Output:")
		self.grpOutput.setContentsMargins(0, 0, 0, 0)
		self.grpOutput.setLayout(self.layOutput)

		self.splitterMain.addWidget(self.grpOutput)

		self.layCtrls = QHBoxLayout()
		self.wdtCtrls = QWidget()
		self.wdtCtrls.setLayout(self.layCtrls)

		self.cmbConversionType = QComboBox()

		self.cmbConversionType.addItem(f"Int to Byte string", 1)
		self.cmbConversionType.addItem(f"Byte string to Int", 2)
		self.cmbConversionType.addItem(f"ASCII string to HEX string", 3)
		self.cmbConversionType.addItem(f"HEX string to ASCII string", 4)
		self.layCtrls.addWidget(self.cmbConversionType)

		self.cmdConvert = QPushButton("Convert")
		self.cmdConvert.clicked.connect(self.handle_convert_clicked)
		self.layCtrls.setAlignment(Qt.AlignmentFlag.AlignRight)
		self.layCtrls.addWidget(self.cmdConvert)

		self.layout().addWidget(self.splitterMain)
		self.layout().addWidget(self.wdtCtrls)
		self.txtInput.textChanged.connect(self.handle_convert_clicked)

	def handle_convert_clicked(self):
		try:
			idConvType = self.cmbConversionType.currentData()
			logDbgC(f"idConvType: {idConvType}")
			if idConvType == 2:
				# self.convertInputToOutput(None)
				sInput = self.txtInput.toPlainText()
				if sInput is None or sInput == "":
					return
				byte_array = ast.literal_eval(sInput)
				print(byte_array)
				logDbgC(f"byte_array: {byte_array}")
				nOut = bytearray_to_int(byte_array, 8)
				sOut = str(nOut)
				self.txtOutput.setText(sOut)
			elif idConvType == 1:
				self.convertInputToOutput(None)
			elif idConvType == 3:
				# self.convertInputToOutput(None)
				ascii_string = self.txtInput.toPlainText()  # "Hello, world!"
				# hex_representation = ascii_string.encode('ascii').hex()

				hex_with_spaces = ' '.join(f'{b:02x}' for b in ascii_string.encode('ascii'))
				print(hex_with_spaces)  # Output: 48 65 6c 6c 6f 2c 20 77 6f 72 6c 64 21
				self.txtOutput.setText(hex_with_spaces)
				# pass
				# print(hex_representation)  # Output: 48656c6c6f2c20776f726c6421
				# self.txtOutput.setText(hex_representation)
			elif idConvType == 4:
				hex_string = self.txtInput.toPlainText()  # "48656c6c6f2c20776f726c6421"  # This is "Hello, world!" in hex
				ascii_string = bytes.fromhex(hex_string).decode('ascii')

				print(ascii_string)  # Output: Hello, world!
				self.txtOutput.setText(ascii_string)
			else:
				pass
		except Exception as e:
			logDbgC(f"Exception while conversion: {e} ...")

	def convertInputToOutput(self, funtCall):
		sInput = self.txtInput.toPlainText()
		if sInput is None or sInput == "":
			return
		baOut = int_to_bytearray(int(sInput), 8)
		if baOut:
			# arOut = baOut
			sOut = f"Byte array: {str(repr(baOut))}\r\n\r\nHex string: {baOut.hex()}"
			self.txtOutput.setText(sOut)
		pass
