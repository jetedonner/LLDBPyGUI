#!/usr/bin/env python3

from PyQt6 import QtCore
from PyQt6.QtWidgets import *


class QClickLabel(QLabel):
	clicked = QtCore.pyqtSignal()

	def mousePressEvent(self, event):
		self.clicked.emit()
		QLabel.mousePressEvent(self, event)
