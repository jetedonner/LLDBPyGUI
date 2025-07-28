#!/usr/bin/env python3
import lldb

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets
from PyQt6.QtGui import QClipboard

from ui.customQt.QConsoleTextEdit import *
from ui.dialogs.dialogHelper import showOpenFileDialog

from worker.workerManager import *

from config import *

class SourceTextEdit(QConsoleTextEdit):
	
	def __init__(self):
		super().__init__()
		
		self.setReadOnly(True)
		self.setFont(ConfigClass.font)
		
		self.verticalScrollBar().valueChanged.connect(self.handle_valueChanged)
		self.verticalScrollBar().rangeChanged.connect(self.handle_rangeChanged)

		self.context_menu = QMenu(self)
		self.actionOpenSourcefile = self.context_menu.addAction("Open sourcefile")

		self.copy_menu =self.context_menu.addMenu("Copy sourcecode")

		# self.actionExpandAll.addMenu()
		self.actionCopyRaw = self.copy_menu.addAction("Copy raw")
		self.actionCopyPretty = self.copy_menu.addAction("Copy pretty")

		self.actionCopyRaw.triggered.connect(self.copyRaw)
		self.actionCopyPretty.triggered.connect(self.copyPretty)
		self.actionOpenSourcefile.triggered.connect(self.openSourcefile)

	def contextMenuEvent(self,  event, anyparam = None):
			self.context_menu.exec(event.globalPos())

	def openSourcefile(self, param):
		logDbgC(f"Open sourcefile called... (param: {param})")
		filename = showOpenFileDialog()
		# logDbgC(f"Open sourcefile => filename:  {filename}")
		if filename != "":
			logDbgC(f"Open sourcefile => filename:  {filename}")
			# self.window().worker.runLoadSourceCode(filename)
			# self.window().start_loadSourceWorker()
			self.window().workerManager.start_loadSourceWorker(self.window().driver.debugger, filename, self.window().handle_loadSourceFinished, 1)

	# def handle_loadSourceFinished(self):
	# 	pass

	def copyRaw(self, param1):
		logDbgC(f"Copy raw...")
		self.copySelectedText()

	def copyPretty(self, param1):
		logDbgC(f"Copy pretty...")
		self.copySelectedText()

	def copySelectedText(self):
		selected_text = self.textCursor().selectedText()
		if selected_text:
			clipboard = QApplication.clipboard()
			clipboard.setText(selected_text)
			logDbgC(f"Copied to clipboard: { selected_text}")
		else:
			logDbgC("No text selected!")

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
		# print(f'handle_valueChanged => {value}')
		pass
		
	def handle_rangeChanged(self, min, max):
		# print(f'handle_rangeChanged: min => {min} / max => {max}')
		pass