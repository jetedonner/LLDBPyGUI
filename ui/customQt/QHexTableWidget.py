#!/usr/bin/env python3
import lldb

import array
import enum
import re
import math

from PyQt6 import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from config import *
from ui.dialogs.settingsDialog import *


#class ByteGrouping(enum.Enum):
#	NoGrouping = ("No Grouping", 1) #"No grouping"
#	TwoChars = ("Two", 2) #"Two characters"
#	FourChars = ("Four", 4) #"Four characters"
#	EightChars = ("Eight", 8) #"Four characters"
	
class ReadOnlySelectableTextEdit(QTextEdit):
	
	isReadOnly = True
	
	def __init__(self, parent=None):
		super().__init__(parent)
		
		self.context_menu = QMenu(self)
		actionEditMemory = self.context_menu.addAction("Edit memory")
		actionEditMemory.triggered.connect(self.handle_editMemory)
		actionWriteMemory = self.context_menu.addAction("Write memory")
		actionWriteMemory.triggered.connect(self.handle_writeMemory)
		self.textChanged.connect(self.handle_text_changed)
		
	def handle_text_changed(self):
		# Get the current cursor position
		cursor = self.textCursor()
		
		# Get the start and end positions of the edited text
		start_pos = cursor.selectionStart()
		end_pos = cursor.selectionEnd()
		
		# Access and process the edited text (optional)
		edited_text = self.toPlainText()[start_pos:end_pos]
		
		print(f"Text changed! Start: {start_pos}, End: {end_pos}, Edited Text: {edited_text}")
		
	def contextMenuEvent(self, event):
		self.context_menu.exec(event.globalPos())
		
	def handle_editMemory(self):
		self.isReadOnly = not self.isReadOnly
#		self.setTextBackgroundColor(QColor.green())
#		self.setStyleSheet("background-color: rgba(0, 255, 0, 48);")
		if not self.isReadOnly:
			p = self.viewport().palette()
			p.setColor(self.viewport().backgroundRole(), QtGui.QColor(0, 255, 0, 24))
			self.viewport().setPalette(p)
		else:
			p = self.viewport().palette()
			p.setColor(self.viewport().backgroundRole(), QtGui.QColor(0, 255, 0, 0))
			self.viewport().setPalette(p)
		
	def handle_writeMemory(self):
		# Target memory address to write to
		memory_address = 0x100003f50  # Replace with the actual address
		
		# Data to write (as a byte string)
#		data_to_write = b"NOP"
		data_to_write = bytes.fromhex("90")
		
		# Write the data to memory
		error = lldb.SBError()
		bytes_written = self.window().driver.getTarget().GetProcess().WriteMemory(memory_address, data_to_write, error)
		
		if error.Success():
			print(f"Wrote {bytes_written} bytes to memory address 0x{memory_address:x}")
		else:
			print(f"Error writing memory: {error}")
		
	def keyPressEvent(self, event):
		if (self.isReadOnly and event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down)) or not self.isReadOnly:
			# Only allow arrow key selection
			super().keyPressEvent(event)
		else:
			event.ignore()  # Ignore any editing-related key presses
		
class QHexTableWidget(QTableWidget):
	
	startAddr = ""
	
	def __init__(self, parent=None):
		QTableWidget.__init__(self, parent=parent)
		
		self.context_menu = QMenu(self)
		actionEditMemory = self.context_menu.addAction("Edit memory")
		actionEditMemory.triggered.connect(self.handle_editMemory)
#		actionDisableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
#		actionDisableBP.triggered.connect(self.handle_disableBP)
#		
#		self.context_menu.addSeparator()
		
		self.setColumnCount(3)
		self.setColumnWidth(0, 128)
		self.setColumnWidth(1, 512)
		self.setColumnWidth(2, 512)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.horizontalHeader().setHighlightSections(False)
		self.setHorizontalHeaderLabels(['Address', 'Hex-Value', 'Raw-Data'])
		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.setFont(ConfigClass.font)
		
		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
		self.setShowGrid(False)

	def contextMenuEvent(self, event):
		self.context_menu.exec(event.globalPos())
		
	def handle_editMemory(self):
		self.txtHex.isReadOnly = not self.txtHex.isReadOnly
		pass
		
	def resetContent(self):
		self.setRowCount(0)
			
	def addRow(self, address, value, raw):
		currRowCount = self.rowCount()
		
		if currRowCount == 0:
			self.line_height = 30
			
			self.setRowCount(currRowCount + 1)
			self.txtAddr = ReadOnlySelectableTextEdit()
			self.txtAddr.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
			self.txtAddr.setText(address)
			self.startAddr = int(address, 16)
			self.txtAddr.setFont(ConfigClass.font)
			
			blockFmt = QTextBlockFormat()
			blockFmt.setLineHeight(self.line_height, 2)
			
			theCursor = self.txtAddr.textCursor()
			theCursor.clearSelection()
			theCursor.select(QTextCursor.SelectionType.Document)
			theCursor.mergeBlockFormat(blockFmt)
			
			self.setCellWidget(currRowCount, 0, self.txtAddr)
			
			self.txtHex = ReadOnlySelectableTextEdit()
			self.txtHex.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
			self.txtHex.setText(value)
			self.txtHex.setFont(ConfigClass.font)
			self.txtHex.setStyleSheet("selection-background-color: #ff0000;")
			
			theCursor2 = self.txtHex.textCursor()
			theCursor2.clearSelection()
			theCursor2.select(QTextCursor.SelectionType.Document)
			theCursor2.mergeBlockFormat(blockFmt)
			self.txtHex.selectionChanged.connect(self.txtHex_selectionchanged)
			self.setCellWidget(currRowCount, 1, self.txtHex)
			
			self.txtData = ReadOnlySelectableTextEdit()
			self.txtData.acceptRichText()
			self.txtData.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
			self.txtData.insertHtml(raw) # + "<br>")
			self.txtData.setFont(ConfigClass.font)
			self.txtData.setStyleSheet("selection-background-color: #ff0000;")
			
#			theCursor3 = self.txtData.textCursor()
#			theCursor3.clearSelection()
#			theCursor3.select(QTextCursor.SelectionType.Document)
#			theCursor3.mergeBlockFormat(blockFmt)
			
			blockFmt2 = QTextBlockFormat()
			blockFmt2.setLineHeight(self.line_height, 2)
			theCursor3 = self.txtData.textCursor()
			theCursor3.clearSelection()
			theCursor3.select(QTextCursor.SelectionType.Document)
			theCursor3.mergeBlockFormat(blockFmt2)
			self.txtData.selectionChanged.connect(self.txtData_selectionchanged)
#			self.txtData.setLineSpacing(30)
			self.setCellWidget(currRowCount, 2, self.txtData)
#			cursor = self.txtData.textCursor()
#			if cursor.block():
#				block_format = cursor.blockFormat()
#				block_format.setLineHeight(self.line_height, 2)
			
			self.txtAddr.verticalScrollBar().valueChanged.connect(self.handle_scroll_change)	
			self.txtHex.verticalScrollBar().valueChanged.connect(self.handle_scroll_change)	
			self.txtData.verticalScrollBar().valueChanged.connect(self.handle_scroll_change)	
			
#			reference_line_height = self.txtData.textCursor().blockFormat().lineHeight(20)  # Get reference line height
#			stylesheet = self.create_line_height_stylesheet(reference_line_height)
#			self.txtHex.setStyleSheet(stylesheet)
			
#			self.synchronize_scroll(self.txtAddr, self.txtHex)
		else:
			self.txtAddr.append(address)
			self.txtHex.append(value)
			self.txtData.insertHtml("<br>" + raw) #.append(raw) # .replace("\n", "\\n")
			blockFmt2 = QTextBlockFormat()
			blockFmt2.setLineHeight(self.line_height, 2)
			theCursor3 = self.txtData.textCursor()
			theCursor3.clearSelection()
			theCursor3.select(QTextCursor.SelectionType.Document)
			theCursor3.mergeBlockFormat(blockFmt2)

		self.setRowHeight(currRowCount, self.get_required_row_height(self.txtAddr, self.height()))
	
	def create_line_height_stylesheet(self, reference_line_height):
		stylesheet = ""
		# Loop through lines in the second text edit
		for line_index, line in enumerate(self.txtData.toPlainText().splitlines()):
			# Calculate desired font size or spacing based on reference line height
			# Adjust stylesheet rulesaa as needed (e.g., using line numbers or custom markers)
			stylesheet += f":global(.QTextEdit) line[{line_index}] {{ font-size: {reference_line_height * 1.2}px; }}"  # Example font size adjustment
		return stylesheet
	
#	def synchronize_scroll(self, widget1, widget2):
	def handle_scroll_change(self, value):
		self.txtAddr.verticalScrollBar().setValue(value)
		self.txtHex.verticalScrollBar().setValue(value)
		self.txtData.verticalScrollBar().setValue(value)
			
#		widget1.verticalScrollBar().valueChanged.connect(handle_scroll_change)	
	
	def get_required_height(self, text_edit):
		total_height = 0
		cursor = text_edit.textCursor()
		cursor.movePosition(QTextCursor.MoveOperation.Start)
		while cursor.hasSelection():
			block_format = cursor.blockFormat()
			total_height += block_format.height()
			cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
#		print(f'total_height: {total_height}')
		return total_height - text_edit.verticalScrollBar().height() - text_edit.frameWidth() * 2  # Adjust for margins and padding
	
	def get_required_row_height(self, text_edit, minimum_row_height):
		content_height = self.get_required_height(text_edit)  # Use your previous method
		cell_padding = 5  # Adjust based on your widget properties
		return max(content_height + cell_padding, minimum_row_height)
	
	def handle_selectionChanged(self, tableWidget, item):
#		print(f"Item changed: {self.row(tableWidget)} {item.selectionStart()} / {item.selectionEnd()}")
#		print(self.cellWidget(self.row(tableWidget), 2).text())
#		self.cellWidget(self.row(tableWidget), 2).setSelection((item.selectionStart()/3), ((item.selectionEnd()+1)/3))
		cursor = self.textCursor()
		pass
	
	def addItem(self, row, col, txt):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		if col == 0:
			item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
		
		# Insert the items into the row
		self.setItem(row, col, item)
		
	updateHexSel = True
	updateSel = True
	
	def hexPosToData(self, hexPos):
		modHexPos = hexPos % 3
		difToAdd = 0
		if modHexPos > 0:
			difToAdd = 3 % modHexPos
		
		dataPos = int((hexPos + difToAdd) / 3)
		return dataPos
	
	def txtHex_selectionchanged(self):
		if not self.updateHexSel or not self.updateTxt:
			return
		
		cursorHex = self.txtHex.textCursor()
		hexStart = cursorHex.selectionStart()
		hexEnd = cursorHex.selectionEnd()
		dataStart = self.hexPosToData(hexStart) + (int(hexStart / 48))
		dataEnd = self.hexPosToData(hexEnd) + (int(hexEnd / 48))
		
#		print(f"txtHex Selection start: %d end: %d => Address: {hex(self.startAddr + self.hexPosToData(hexStart))} - {hex(self.startAddr + self.hexPosToData(hexEnd))}" % (hexStart, hexEnd))
		
		if SettingsHelper.GetValue(SettingsValues.MemViewShowSelectedStatubarMsg):
			self.window().updateStatusBar(f'Selected memory: {hex(self.startAddr + self.hexPosToData(hexStart))} - {hex(self.startAddr + self.hexPosToData(hexEnd))}')
			
#		print(f'===> Data-Start: {dataStart} / End: {dataEnd}')
		
		cursorData = self.txtData.textCursor()
		cursorData.clearSelection()
		txtLen = len(self.txtData.toPlainText())
		
		if dataStart > txtLen:
			dataStart = 0
		cursorData.setPosition(dataStart)

		if dataEnd > txtLen:
			dataEnd = txtLen - 1

		cursorData.setPosition(dataEnd, QTextCursor.MoveMode.KeepAnchor)
		
		self.updateHexSel = False
		self.updateSel = False
		self.txtData.setTextCursor(cursorData)
		self.updateHexSel = True
		self.updateSel = True
		self.txtData.ensureCursorVisible()
		
	updateTxt = True
	updateHexTxt = True
	
	def dataPosToHex(self, dataPos):
		hexPos = dataPos * 3
		if hexPos % 2 > 0:
			hexPos -= 1
			
		if dataPos % 2 == 0:
			hexPos -= 1
			
#		# FIXME: This is a ugly hack and not working properly
#		if hexPos % 6 == 0:
#			hexPos -= 1 # math.floor(hexPos / 6 ) * 1
			
		return hexPos
	
	def txtData_selectionchanged(self):
		if not self.updateSel or not self.updateTxt:
			return

		cursorData = self.txtData.textCursor()
		dataStart = cursorData.selectionStart()
		dataEnd = cursorData.selectionEnd()
		hexStart = self.dataPosToHex(dataStart) - (int(dataStart / 17) * 3) # + ((int(dataStart / 17) * 1)) # math.floor
		hexEnd = self.dataPosToHex(dataEnd) - (int(dataEnd / 17) * 3) # + ((int(dataEnd / 17) * 1))
		
		cursorHex = self.txtHex.textCursor()
		cursorHex.clearSelection()
		txtLen = len(self.txtHex.toPlainText())

#		print("txtData Selection start: %d end: %d" % (dataStart, dataEnd))
#		print(f'===> Hex-Start: {hexStart} / End: {hexEnd}')
#		print(f'(math.floor(hexEnd  / 48)) = {(math.floor(hexEnd  / 48))}')
##		hexEnd -= (math.floor(hexEnd / 48))
##		if math.floor((hexEnd / 48)) > 0:
##			hexEnd -= (math.floor((hexEnd / 48) * 2))
#		print(f'=======> Hex-Start: {hexStart} / End: {hexEnd}')
			
		if hexStart > txtLen:
			hexStart = 0
		elif hexStart < 0:
			hexStart = 0
			
		if hexEnd > txtLen:
			hexEnd = txtLen - 1
		
		cursorHex.setPosition(hexStart)
		cursorHex.setPosition(hexEnd, QTextCursor.MoveMode.KeepAnchor)
		self.updateTxt = False
		self.updateHexTxt = False
		self.txtHex.setTextCursor(cursorHex)
		self.updateTxt = True
		self.updateHexTxt = True
		self.txtHex.ensureCursorVisible()
		