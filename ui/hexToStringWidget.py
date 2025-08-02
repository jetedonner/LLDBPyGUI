#!/usr/bin/env python3
import lldb

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets
from PyQt6.QtGui import QClipboard

from lib.utils import hex_to_string
from ui.customQt.QConsoleTextEdit import *
from ui.customQt.QHexTextEdit import QHexTextEdit
from ui.dialogs.dialogHelper import showOpenFileDialog

from worker.workerManager import *

from config import *

class HexToStringWidget(QWidget):

	oldCursorPos = -1

	def __init__(self):
		super().__init__()
		self.oldCursorPos = -1

		self.wdtParent = QWidget()
		self.wdtParent.setContentsMargins(0, 0, 0, 0)
		self.wdtParent.setLayout(QVBoxLayout())
		self.lblHexStats = QLabel("Hex-Statistics:")
		self.lblHexStats.setFont(ConfigClass.font)
		self.wdtParent.layout().addWidget(self.lblHexStats)
		# self.lblTitle = QLabel("HEX <-> ASCII Converter")
		# self.lblTitle.setFont(ConfigClass.fontTitle)
		# self.wdtParent.layout().addWidget(self.lblTitle)

		self.wdtHexValue = QWidget()
		self.wdtHexValue.setContentsMargins(0, 0, 0, 0)
		self.wdtHexValue.setLayout(QVBoxLayout())
		self.wdtHexValue.layout().setContentsMargins(0, 0, 0, 0)
		self.setLayout(QVBoxLayout())

		self.splitterTools = QSplitter()
		self.splitterTools.setContentsMargins(0, 0, 0, 0)
		self.splitterTools.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.splitterTools.setOrientation(Qt.Orientation.Vertical)
		# self.txtHexToStringInput = QTextEdit("73 68 6f 77")
		# self.txtHexToStringInput.setTabChangesFocus(True)
		# self.txtHexToStringInput.setStyleSheet(textEditStylesheet)
		# self.txtHexToStringInput.textChanged.connect(self.handle_txtHexToStringChanged)
		# self.txtHexToStringInput.cursorPositionChanged.connect(self.handle_txtHexToStringCursorPositionChanged)

		self.txtHexToStringInput = QHexTextEdit()  # ReadOnlySelectableTextEdit(None, True) #
		self.txtHexToStringInput.ommitFormatting = False
		self.txtHexToStringInput.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		# logDbgC(f"=======>>>>>>>>>>> self.txtHexToStringInput (before-0): {self.txtHexToStringInput.toPlainText()}",
		# 		DebugLevel.Verbose)
		# self.txtHexToStringInput.setText("")
		# logDbgC(f"=======>>>>>>>>>>> self.txtHexToStringInput (before-1): {self.txtHexToStringInput.toPlainText()}",
		# 		DebugLevel.Verbose)
		self.txtHexToStringInput.setFont(ConfigClass.font)
		self.txtHexToStringInput.setStyleSheet("""
						QTextEdit {
							background-color: #282c34; /* Dark background */
							color: #abb2bf; /* Light grey text */
							border: 1px solid #3e4452;
							border-radius: 5px;
							padding: 5px;
							font: 12px 'Courier New';
							selection-background-color: #ff0000;
						}
					""")
		# self.txtHexToStringInput.textChanged.connect(self.handle_txtHexToStringChanged)
		# self.txtHexToStringInput.selectionChanged.connect(self.txtHex_selectionchanged)

		self.lblHexTitlePrefix = "Hex-Statistics:"
		self.lblHexTitle = QLabel(self.lblHexTitlePrefix)
		self.wdtHexValue.layout().addWidget(self.lblHexTitle)
		self.wdtHexValue.layout().addWidget(self.txtHexToStringInput)
		self.splitterTools.addWidget(self.wdtHexValue)

		self.wdtStringValue = QWidget()
		self.wdtStringValue.setContentsMargins(0, 0, 0, 0)
		self.wdtStringValue.setLayout(QVBoxLayout())
		self.wdtStringValue.layout().setContentsMargins(0, 0, 0, 0)
		self.txtAsciiStringOutput = QTextEdit("")
		self.txtAsciiStringOutput.setTabChangesFocus(True)
		self.wdtStringValue.layout().addWidget(QLabel("String-Value:"))
		self.wdtStringValue.layout().addWidget(self.txtAsciiStringOutput)
		self.txtAsciiStringOutput.setStyleSheet(textEditStylesheet)
		# self.txtAsciiStringOutput.textChanged.connect(self.handle_txtAsciiStringOutputChanged)
		# self.txtAsciiStringOutput.setPlaceholderText("Enter a hex value above t")
		self.splitterTools.addWidget(self.wdtStringValue)
		self.splitterTools.setStretchFactor(0, 60)
		self.splitterTools.setStretchFactor(1, 40)
		self.wdtParent.layout().addWidget(self.splitterTools)
		self.layout().addWidget(self.wdtParent)

		self.last_text = ""
		# logDbgC(f"=======>>>>>>>>>>> self.txtHexToStringInput (before-2): {self.txtHexToStringInput.toPlainText()}",
		# 		DebugLevel.Verbose)
		# logDbgC(f"=======>>>>>>>>>>> self.txtAsciiStringOutput (before): {self.txtAsciiStringOutput.toPlainText()}",
		# 		DebugLevel.Verbose)
		self.handle_txtHexToStringChanged()
		self.txtHexToStringInput.textChanged.connect(self.handle_txtHexToStringChanged)
		# self.txtHexToStringInput.selectionChanged.connect(self.txtHex_selectionchanged)
		self.txtAsciiStringOutput.textChanged.connect(self.handle_txtAsciiStringOutputChanged)
		# logDbgC(f"=======>>>>>>>>>>> self.txtHexToStringInput: {self.txtHexToStringInput.toPlainText()}", DebugLevel.Verbose)
		# logDbgC(f"=======>>>>>>>>>>> self.txtAsciiStringOutput: {self.txtAsciiStringOutput.toPlainText()}", DebugLevel.Verbose)
		# self.txtHexToStringInput.setPlainText("73 68 6f 77")
		# self.setReadOnly(True)
		# self.setFont(ConfigClass.font)
		#
		# self.verticalScrollBar().valueChanged.connect(self.handle_valueChanged)
		# self.verticalScrollBar().rangeChanged.connect(self.handle_rangeChanged)
		#
		# self.context_menu = QMenu(self)
		# self.actionOpenSourcefile = self.context_menu.addAction("Open sourcefile")
		#
		# self.copy_menu =self.context_menu.addMenu("Copy sourcecode")


		# ba = QByteArray('show'.encode()) # , "68", "6f", "77"
		# ba_as_hex_string = ba.toHex(b' ')
		# logDbgC(f"ba_as_hex_string: {ba_as_hex_string}")

	# updateHexSel = False
	# def txtHex_selectionchanged(self):
	# 	# if not self.updateHexSel or not self.updateTxt:
	# 	# 	return
	# 	self.handle_txtHexToStringChanged()
	# 	pass

	def handle_txtHexToStringCursorPositionChanged(self):
		cursor = self.txtHexToStringInput.textCursor()
		pos = cursor.position()
		self.oldCursorPos = pos
		logDbgC(f"Cursor-Pos: {pos}", DebugLevel.Verbose)
		pass

	def handle_txtAsciiStringOutputChanged(self):
		logDbgC(f"=======>>>>>>>>>>> handle_txtAsciiStringOutputChanged ....")
		rawTxt = self.txtAsciiStringOutput.toPlainText()
		ba = QByteArray(rawTxt.encode())
		hex_string = bytearray(ba.toHex(b' ')).decode("utf-8")
		logDbgC(f"hex_string: {hex_string}", DebugLevel.Verbose)
		self.txtHexToStringInput.blockSignals(True)
		self.txtHexToStringInput.setPlainText(hex_string)
		self.txtHexToStringInput.blockSignals(False)

	def insert_space(self, s, position):
		return s[:position] + " " + s[position:]

	def handle_txtHexToStringChanged(self):
		logDbgC(f"=======>>>>>>>>>>> handle_txtHexToStringChanged ....")
		self.txtAsciiStringOutput.blockSignals(True)
		# cursor = self.txtHexToStringInput.textCursor()
		# self.oldCursorPos = cursor.position()
		#
		rawTxt = self.txtHexToStringInput.toPlainText()
		if len(rawTxt) > 2:
			blocks = (len(rawTxt) - 2)
			if blocks % 3 == 0:
				strBytes = str(int(blocks / 3))
			else:
				strBytes = "~" + str(int(blocks / 3))
		else:
			strBytes = "-"

		self.lblHexTitle.setText(self.lblHexTitlePrefix + f" Bytes: {strBytes}")
		# lenTxt = len(rawTxt)
		# if (self.oldCursorPos - 2) % 3 == 0:
		# 	if lenTxt > self.oldCursorPos:
		# 		if rawTxt[self.oldCursorPos + 1] != " ":
		# 			self.insert_space(rawTxt, self.oldCursorPos + 1)
		#
		# # if self.oldCursorPos <= lenTxt > 2:
		# # 	if self.oldCursorPos == lenTxt - 1:
		# # 		if rawTxt[lenTxt - 2] != " ":
		# # 			rawTxt += " "
		# # 			self.oldCursorPos += 1
		# # 		pass
		# # if rawTxt[self.oldCursorPos - 1] == " " or self.oldCursorPos == len(rawTxt):
		# # 	self.oldCursorPos += 1
		#
		# # self.format_hex(rawTxt)

		# self.txtHexToStringInput.blockSignals(True)
		# self.txtHexToStringInput.setPlainText(rawTxt)
		# cursor.setPosition(self.oldCursorPos)
		# self.txtHexToStringInput.setTextCursor(cursor)
		# self.txtHexToStringInput.blockSignals(False)
		try:
			self.txtAsciiStringOutput.setPlainText(hex_to_string(rawTxt.split()))
		except Exception as e:
			logDbgC(f"Error while converting hex value to string! Exception: {e}")
		self.txtAsciiStringOutput.blockSignals(False)

	def format_hex(self, txtToFormat):
		logDbgC(f"format_hex....")
		# Block signal to prevent recursion
		self.txtHexToStringInput.blockSignals(True)

		raw_text = txtToFormat #self.txtHexToStringInput.toPlainText()
		cleaned = ''.join(c for c in raw_text if c.strip())  # remove spaces/newlines
		grouped = ' '.join(cleaned[i:i + 2] for i in range(0, len(cleaned), 2))

		if grouped != self.last_text:
			cursor = self.txtHexToStringInput.textCursor()
			pos = cursor.position()
			if self.oldCursorPos == len(grouped) and grouped[len(grouped) - 2] != " ":
				self.txtHexToStringInput.setPlainText(grouped + " ")
				self.oldCursorPos += 1
				cursor.setPosition(self.oldCursorPos)
				self.last_text = grouped + " "
			else:
				self.txtHexToStringInput.setPlainText(grouped)
				cursor.setPosition(min(self.oldCursorPos, len(grouped)))
				self.last_text = grouped

			self.txtHexToStringInput.setTextCursor(cursor)


		self.txtHexToStringInput.blockSignals(False)

# 	def contextMenuEvent(self,  event, anyparam = None):
# 			self.context_menu.exec(event.globalPos())
#
# 	def copyRaw(self, param1):
# 		logDbgC(f"Copy raw...")
# 		self.copySelectedText()
#
# 	def copyPretty(self, param1):
# 		logDbgC(f"Copy pretty...")
# 		self.copySelectedText()
#
# 	def copySelectedText(self):
# 		selected_text = self.textCursor().selectedText()
# 		if selected_text:
# 			clipboard = QApplication.clipboard()
# 			clipboard.setText(selected_text)
# 			logDbgC(f"Copied to clipboard: { selected_text}")
# 		else:
# 			logDbgC("No text selected!")
#
# 	def getNextNBSpace(self, text, start_pos):
# 		decoded_text = text.encode('utf-8').decode('utf-8')  # Encode and decode to handle the byte sequence
# 		position = decoded_text.find('\xa0', start_pos)  # Search for the nearby text
# 		return position
#
# 		scroll_value = line_num * self.fontMetrics().height()
# 		scroll_value -= self.viewport().height() / 2
# #		print(f"Scroll To Line => scroll_value: {linePos} / {self.fontMetrics().height()} / {self.viewport().height() / 2} / {scroll_value}")
# #		scroll_value = 500
# 		self.verticalScrollBar().setValue(int(scroll_value))
#
# 	def scroll_to_line(self, line_text):
# 		#		QApplication.processEvents()
# #		print(f"Scroll To Line: {line_text}")
# 		search_string = "=&gt;"
#
# 		text = self.document().findBlockByNumber(0).text()
# 		position = text.find(line_text)
# 		start_pos = position + 3
# #		print(f"Scroll To Line => start_pos: {start_pos}")
# 		#		print(f"Scroll To Line: {line_text} => {position} / {start_pos}")
# 		linePos = 1
# 		try:
# 			end_pos = self.getNextNBSpace(text, start_pos)
# 			if text[start_pos:end_pos] == '':
# 				return
# 			linePos = int(text[start_pos:end_pos])
# 		except Exception as e:
# 			print(f"Exception: {e}")
# 			pass
#
# 		scroll_value = linePos * self.fontMetrics().height()
# 		scroll_value -= self.viewport().height() / 2
# #		print(f"Scroll To Line => scroll_value: {linePos} / {self.fontMetrics().height()} / {self.viewport().height() / 2} / {scroll_value}")
# #		scroll_value = 500
# 		self.verticalScrollBar().setValue(int(scroll_value))
#
# 	def handle_valueChanged(self, value):
# 		# print(f'handle_valueChanged => {value}')
# 		pass
#
# 	def handle_rangeChanged(self, min, max):
# 		# print(f'handle_rangeChanged: min => {min} / max => {max}')
# 		pass