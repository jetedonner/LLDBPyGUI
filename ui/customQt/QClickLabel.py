#!/usr/bin/env python3

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets, QtCore

class QClickLabel(QLabel):
	
	clicked = QtCore.pyqtSignal()
	
	def mousePressEvent(self, event):
		self.clicked.emit()
		QLabel.mousePressEvent(self, event)