#!/usr/bin/env python3
import os
import sys
import enum
	
import re

from PyQt6 import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

#from PyQt6.QtGui import *
#from PyQt6.QtCore import Qt
#from PyQt6.QtWidgets import QApplication, QTextEdit

font = QFont("Courier New")

class IntHexValidator(QValidator):
	def __init__(self, parent=None):
		super().__init__(parent)
#		self.int_regex = QtCore.QRegExp(r"^-?\d+$")  # Allows signed integers
#		self.hex_regex = QtCore.QRegExp(r"^0x[0-9a-fA-F]+$")  # Allows hex values with 0x prefix
	
		self.int_regex = r"^-?\d+$"  # Match anything within square brackets, excluding the brackets themselves
		self.hex_regex = r"^(0[xX])?[A-Fa-f0-9]+$" #"^(0x|0X)?[a-fA-F0-9]+$" # ^0x[0-9a-fA-F]+$"
	
	def validate(self, input_text, pos):
		try:
#			help(QValidator.validate)
#			print(help(QValidator.validate))
			print(f"Validating: '{input_text}', pos: {pos}")
			# Check if input is empty or a single minus sign
			if input_text == "" or input_text == "-":
				return (QValidator.State.Acceptable, input_text, pos)
	
			if re.search(self.int_regex, input_text): #.exactMatch(input_text):
				return (QValidator.State.Acceptable, input_text, pos)
	
			# Check for valid hex value
			if re.search(self.hex_regex, input_text): #if self.hex_regex.exactMatch(input_text):
				return (QValidator.State.Acceptable, input_text, pos)
			elif input_text.lower() == "0x": # or input_text == "0X":
				return (QValidator.State.Acceptable, input_text, pos)
	
		except Exception as e:
			print(f"Error validating: {e}")
	
		# Invalid input
		return (QValidator.State.Invalid, input_text, pos)
	
	
	
class ByteGrouping(enum.Enum):
	NoGrouping = ("No Grouping", 1) #"No grouping"
	TwoChars = ("Two", 2) #"Two characters"
	FourChars = ("Four", 4) #"Four characters"
	EightChars = ("Eight", 8) #"Four characters"
	
class QHexTextEdit(QTextEdit):
	
	ommitFormatting = True
	context_menu = None
	isReadOnly = True
	
	sigEdit = pyqtSignal()
	sigWrite = pyqtSignal()
	sigCancel = pyqtSignal()
	
	
#	def __init__(self, parent=None, hasContextMenu = False):
#		super().__init__(parent)
#		
#		self.hasContextMenu = hasContextMenu
#		
#		self.textChanged.connect(self.handle_text_changed)
#		
#	def handle_text_changed(self):
#		# Get the current cursor position
#		cursor = self.textCursor()
#		
#		# Get the start and end positions of the edited text
#		start_pos = cursor.selectionStart() - 1
#		end_pos = cursor.selectionEnd()
#		
#		# Access and process the edited text (optional)
#		edited_text = self.toPlainText()[start_pos:end_pos]
#		
#		print(f"Text changed! Start: {start_pos}, End: {end_pos}, Edited Text: {edited_text}")
			
	def contextMenuEvent(self, event):
		if self.context_menu != None:
			self.context_menu.exec(event.globalPos())
			
	def __init__(self, parent=None):
		super().__init__(parent)
#		if self.hasContextMenu:
		self.context_menu = QMenu(self)
		self.actionEditMemory = self.context_menu.addAction("Edit memory")
		self.actionEditMemory.triggered.connect(self.handle_editMemory)
		self.actionWriteMemory = self.context_menu.addAction("Write memory")
		self.actionWriteMemory.triggered.connect(self.handle_writeMemory)
			
		self.textChanged.connect(self.format_text)
		self.setFont(font)
#		self.setValidator(IntHexValidator())
		
	def handle_editMemory(self):
		self.ommitFormatting = False
		self.sigEdit.emit()
		pass
#		self.isReadOnly = not self.isReadOnly
##		self.setTextBackgroundColor(QColor.green())
##		self.setStyleSheet("background-color: rgba(0, 255, 0, 48);")
#		if not self.isReadOnly:
#			p = self.viewport().palette()
#			p.setColor(self.viewport().backgroundRole(), QtGui.QColor(0, 255, 0, 24))
#			self.viewport().setPalette(p)
#		else:
#			p = self.viewport().palette()
#			p.setColor(self.viewport().backgroundRole(), QtGui.QColor(0, 255, 0, 0))
#			self.viewport().setPalette(p)
		
	def handle_writeMemory(self):
		self.ommitFormatting = True
		self.sigWrite.emit()
		pass
		
	def format_text(self):
		if not self.ommitFormatting:
			self.ommitFormatting = True
			cursor = self.textCursor()
			text = self.toPlainText()
			# Limit text length to 8 characters (4 digits, 3 spaces)
#			text = text[:8]
#			formatted_text = ""
#			for i in range(0, len(text), 2):
#				if i > 0:
#					formatted_text += " "
#				formatted_text += text[i:i+2]
			# Get the start and end positions of the edited text
			start_pos = cursor.selectionStart() - 1
			end_pos = cursor.selectionEnd()
			
			# Access and process the edited text (optional)
			edited_text = self.toPlainText()[start_pos:end_pos]
			
			formatted_text = ""
			if edited_text.lower() in list(["a", "b", "c", "d", "e", "f", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", " ", "\n"]):
				print(f"IS HEX")
			else:
				print(f"IS NOT HEX => {edited_text} ({start_pos} / {end_pos})")
				
				tmp_text = self.toPlainText()[:start_pos]
				tmp_text += self.toPlainText()[end_pos:]
				current_line = ""
				for char in tmp_text:
					if char == "\n":
						formatted_text += self.formatHexStringFourChars(current_line) + "\n"
						current_line = ""
					else:
						current_line += char
						
				# Print the last line if it doesn't end with a newline
				if current_line:
					formatted_text += self.formatHexStringFourChars(current_line)
					
				self.setPlainText(formatted_text)
				cursor.setPosition(start_pos + (0 if len(formatted_text) % 3 == 2 else 0))
	#			cursor.setPosition(end_pos, QTextCursor.MoveMode.KeepAnchor)
				self.setTextCursor(cursor)
				self.ommitFormatting = False
				return
			
			print(f"Text changed! Start: {start_pos}, End: {end_pos}, Edited Text: {edited_text}")
			
			
#			for line in text.splitlines():
#				formatted_text += self.formatHexStringFourChars(line) + ("\n" if line[:-1] == "\n" else "")
			current_line = ""
			for char in text:
				if char == "\n":
					formatted_text += self.formatHexStringFourChars(current_line) + "\n"
					current_line = ""
				else:
					current_line += char
					
			# Print the last line if it doesn't end with a newline
			if current_line:
				formatted_text += self.formatHexStringFourChars(current_line)
				
			self.setPlainText(formatted_text)
			
#			self.setCursorPosition(len(formatted_text))  # Set cursor to the end
			cursor.setPosition(end_pos + (1 if len(formatted_text) % 3 == 2 else 0))
#			cursor.setPosition(end_pos, QTextCursor.MoveMode.KeepAnchor)
			self.setTextCursor(cursor)
			self.ommitFormatting = False
		
	def formatHexStringFourChars(self, hex_string, grouping = ByteGrouping.TwoChars):
		
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
		
#app = QApplication([])
#
## Create formatted text edit
#formatted_edit = QHexTextEdit()
#formatted_edit.show()
#
#app.exec()