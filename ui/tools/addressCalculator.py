import lldb
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QGroupBox, QTextEdit, QHBoxLayout, QComboBox, QPushButton

from ui.base.baseCleanPasteTextEdit import CleanPasteTextEdit


class AddressClaculatorWidget(QWidget):

	def __init__(self, driver):
		super().__init__()

		self.driver = driver
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
		self.cmbConversionType.addItem(f"Convert Load- to File-Address", 1)
		# self.cmbConversionType.addItem(f"Int to Byte string", 2)
		# self.cmbConversionType.addItem(f"ASCII string to HEX string", 3)
		# self.cmbConversionType.addItem(f"HEX string to ASCII string", 4)
		self.layCtrls.addWidget(self.cmbConversionType)

		self.cmdConvert = QPushButton("Convert")
		self.cmdConvert.clicked.connect(self.handle_convert_clicked)
		self.layCtrls.setAlignment(Qt.AlignmentFlag.AlignRight)
		self.layCtrls.addWidget(self.cmdConvert)

		self.layout().addWidget(self.splitterMain)
		self.layout().addWidget(self.wdtCtrls)

	def handle_convert_clicked(self):
		# Assume you already have a target and module
		target = self.driver.debugger.GetSelectedTarget()
		module = target.GetModuleAtIndex(1)  # Or use target.FindModule(...) for a specific one

		# Get the base address where the module was loaded
		load_addr = module.GetObjectFileHeaderAddress().GetLoadAddress(target)

		# Get the original file address (linked address)
		file_addr = module.GetObjectFileHeaderAddress().GetFileAddress()

		# Calculate the slide
		slide = load_addr - file_addr

		self.txtOutput.setText(f"Load Address: 0x{load_addr:x}\r\nFile Address: 0x{file_addr:x}\r\nSlide: 0x{slide:x}")
		# print(f"File Address: 0x{file_addr:x}")
		# print(f"Slide: 0x{slide:x}")
		pass
