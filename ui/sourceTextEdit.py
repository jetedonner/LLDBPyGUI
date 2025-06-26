#!/usr/bin/env python3
import lldb

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from ui.customQt.QConsoleTextEdit import *

from worker.workerManager import *

from config import *

class SourceTextEdit(QConsoleTextEdit):
	
	def __init__(self):
		super().__init__()
		
		self.setReadOnly(True)
		self.setFont(ConfigClass.font)
		
		self.verticalScrollBar().valueChanged.connect(self.handle_valueChanged)
		self.verticalScrollBar().rangeChanged.connect(self.handle_rangeChanged)
		
	def getNextNBSpace(self, text, start_pos):
		decoded_text = text.encode('utf-8').decode('utf-8')  # Encode and decode to handle the byte sequence
		position = decoded_text.find('\xa0', start_pos)  # Search for the nearby text
		return position
	
	def scroll_to_lineNG(self, line_num):
		#		QApplication.processEvents()
#		print(f"Scroll To Line: {line_text}")
#		search_string = "=&gt;"
#		
#		text = self.document().findBlockByNumber(0).text()
#		position = text.find(line_text)
#		start_pos = position + 3
##		print(f"Scroll To Line => start_pos: {start_pos}")
#		#		print(f"Scroll To Line: {line_text} => {position} / {start_pos}")
#		linePos = 1
#		try:
#			end_pos = self.getNextNBSpace(text, start_pos)
#			if text[start_pos:end_pos] == '':
#				return
#			linePos = int(text[start_pos:end_pos])
#		except Exception as e:
#			print(f"Exception: {e}")
#			pass
			
		scroll_value = line_num * self.fontMetrics().height()
		scroll_value -= self.viewport().height() / 2
#		print(f"Scroll To Line => scroll_value: {linePos} / {self.fontMetrics().height()} / {self.viewport().height() / 2} / {scroll_value}")
#		scroll_value = 500
		self.verticalScrollBar().setValue(int(scroll_value))
		
	def scroll_to_line(self, line_text):
		#		QApplication.processEvents()
#		print(f"Scroll To Line: {line_text}")
		search_string = "=&gt;"
		
		text = self.document().findBlockByNumber(0).text()
		position = text.find(line_text)
		start_pos = position + 3
#		print(f"Scroll To Line => start_pos: {start_pos}")
		#		print(f"Scroll To Line: {line_text} => {position} / {start_pos}")
		linePos = 1
		try:
			end_pos = self.getNextNBSpace(text, start_pos)
			if text[start_pos:end_pos] == '':
				return
			linePos = int(text[start_pos:end_pos])
		except Exception as e:
			print(f"Exception: {e}")
			pass
			
		scroll_value = linePos * self.fontMetrics().height()
		scroll_value -= self.viewport().height() / 2
#		print(f"Scroll To Line => scroll_value: {linePos} / {self.fontMetrics().height()} / {self.viewport().height() / 2} / {scroll_value}")
#		scroll_value = 500
		self.verticalScrollBar().setValue(int(scroll_value))
	
#	def scroll_to_line(self, line_text):
##		QApplication.processEvents()
##		print(f"Scroll To Line: {line_text}")
#		search_string = "=&gt;"
#	
#		text = self.document().findBlockByNumber(0).text()
#		position = text.find(line_text)
#		start_pos = position + 3
#	
##		print(f"Scroll To Line: {line_text} => {position} / {start_pos}")
#	
#		end_pos = self.getNextNBSpace(text, start_pos)
#		if text[start_pos:end_pos] == '':
#			return
#	
#		linePos = int(text[start_pos:end_pos])
#	
#		scroll_value = linePos * self.fontMetrics().height()
#		scroll_value -= self.viewport().height() / 2
#		self.verticalScrollBar().setValue(int(scroll_value))
		
	def handle_valueChanged(self, value):
		print(f'handle_valueChanged => {value}')
		pass
		
	def handle_rangeChanged(self, min, max):
		print(f'handle_rangeChanged: min => {min} / max => {max}')
		pass