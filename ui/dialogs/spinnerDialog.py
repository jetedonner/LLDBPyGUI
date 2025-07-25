#!/usr/bin/env python3
import time

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from ui.customQt.QClickLabel import *
from config import *
from ui.helper.dbgOutputHelper import logDbgC, DebugLevel


class SpinnerDialog(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

		# Create layout and label for the GIF
		layout = QVBoxLayout()
		self.gif_label = QLabel()
		# self.gif_label.setFixedSize(QSize(96, 96))
		layout.addWidget(self.gif_label, alignment=Qt.AlignmentFlag.AlignCenter)
		self.setLayout(layout)
		self.lblMsg = QLabel(f"Loading target ...")
		layout.addWidget(self.lblMsg, alignment=Qt.AlignmentFlag.AlignCenter)
	
		# Load and set the animated GIF
		self.movie = QMovie("./resources/img/DoubleRingSpinner.gif")
		self.movie.setScaledSize(QSize(64, 64))
		self.gif_label.setMovie(self.movie)
		self.movie.start()
		
		bg_color = QColor(220, 220, 220, 128)  # Adjust alpha value for desired transparency

		palette = self.palette()
		palette.setColor(palette.ColorRole.Window, bg_color)
		self.setPalette(palette)
		self.setFixedSize(150, 115)
		# Set default corner radius
		self.corner_radius = 10
		self.border_width = 5
		
		# Create rounded corner mask
		self.create_rounded_mask()
		
		# Set the mask for the dialog
		self.setMask(self.rounded_mask)
		
		self.setModal(True)
		
	def create_rounded_mask(self):
		size = self.rect().size()
		
		mask = QBitmap(size)
		mask.fill(Qt.GlobalColor.white)  # Transparent background
		
		painter = QPainter(mask)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # Enable antialiasing for smoother edges
		path = QPainterPath()
		path.addRoundedRect(0, 0, size.width(), size.height(), self.corner_radius, self.corner_radius)
		painter.fillPath(path, QBrush(Qt.GlobalColor.black))  # Fill with white (adjust as needed)
		painter.end()
		self.rounded_mask = mask
		
	def paintEvent(self, event):
		size = self.rect().size()
		painter = QPainter(self)
		
		# Draw white border
		pen = QPen(QColor(100, 100, 100), self.border_width)  # White pen with border width
		painter.setPen(pen)
		path = QPainterPath()
		path.addRoundedRect(0, 0, size.width(), size.height(), self.corner_radius, self.corner_radius)
#		painter.drawRect(self.rect())  # Draw rectangle around the entire dialog
		painter.strokePath(path, pen)
		super().paintEvent(event)
		
	def set_background_color(self, color):
		"""Sets the background color of the dialog with desired transparency.

		Args:
			color (QColor): The desired background color with alpha channel for transparency.
		"""
		self.setWindowOpacity(color.alpha() / 255)
		palette = self.palette()
		palette.setColor(palette.ColorRole.Window, color)
#		palette.setWindowColor(color)
		self.setPalette(palette)

	def keyPressEvent(self, event: QKeyEvent):
		if event.key() == Qt.Key.Key_Escape:
			logDbgC("Escape ignored.", DebugLevel.Verbose)
			event.ignore()  # Prevent default reject()
		else:
			super().keyPressEvent(event)