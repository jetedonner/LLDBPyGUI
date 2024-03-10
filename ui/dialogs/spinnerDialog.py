#!/usr/bin/env python3
import time

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from ui.customQt.QClickLabel import *
from config import *

class SpinnerDialog(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
#		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
		
		# Create layout and widgets
#		self.layout = QVBoxLayout()
#		self.image_label = QLabel()
#		self.layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)
#		self.setLayout(self.layout)
#		self.cmdDeleteAll = QClickLabel()
#		self.cmdDeleteAll.setContentsMargins(0, 0, 0, 0)
#		self.cmdDeleteAll.setPixmap(ConfigClass.pixDelete.scaledToWidth(24))
#		self.layout.addWidget(self.cmdDeleteAll, alignment=Qt.AlignmentFlag.AlignCenter)
		
		# Create layout and label for the GIF
		layout = QVBoxLayout()
		self.gif_label = QLabel()
		layout.addWidget(self.gif_label, alignment=Qt.AlignmentFlag.AlignCenter)
		self.setLayout(layout)
	
		# Load and set the animated GIF
		self.movie = QMovie("/Volumes/Data/dev/_reversing/disassembler/LLDBPyGUI/LLDBPyGUI/resources/img/Spinner2-200px.gif")
		self.movie.setScaledSize(QSize(64, 64))
		self.gif_label.setMovie(self.movie)
		self.movie.start()
		
		bg_color = QColor(220, 220, 220, 128)  # Adjust alpha value for desired transparency
		
#		pd = ProcessesDialog("Hey", "Zwei")
#		pd.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
#		pd.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
#		dialog = SpinnerDialog()
#		se§lf.setWindowOpacity(bg_color.alpha() / 255)
		palette = self.palette()
		palette.setColor(palette.ColorRole.Window, bg_color)
		#		palette.setWindowColor(color)
		self.setPalette(palette)
		
		# Set up spinning image
#		self.movie = QMovie("/Volumes/Data/dev/_reversing/disassembler/LLDBPyGUI/resources/img/spinner-1s-200px.gif")  # Replace with your GIF path
#		self.image_label.setMovie(self.movie)
#		self.movie.start()
#		while(True):
#			# Pause the program for 2 seconds
#			time.sleep(1)
#		self.corner_radius = 10
		# Set stylesheet for rounded corners
#		stylesheet = "QDialog { border-radius: 10px; }"  # Adjust radius as needed
#		self.setStyleSheet(stylesheet))
		
		# ... (other dialog setup)
#		
#	def paintEvent(self, event):
#		painter = QPainter(self)
#		path = QPath()
#		path.addRoundedRect(self.rect(), self.corner_radius, self.corner_radius)
#		painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # Enable antialiasing for smoother edges
#		painter.fillPath(path, QBrush(QColor(255, 255, 255)))  # Fill with white (adjust as needed)
#		painter.setPen(QPen(QColor(0, 0, 0), 1))  # Set border pen (optional)
#		painter.drawPath(path)
#		super().paintEvent(event)
		self.setFixedSize(150, 75)
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
#		current_size = self.rect().size()
#		new_width = current_size.width() - 6
#		new_height = current_size.height() - 6
#		current_size = QSize(new_width, new_height)
		
		mask = QBitmap(size)
		mask.fill(Qt.GlobalColor.white)  # Transparent background
		
		painter = QPainter(mask)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # Enable antialiasing for smoother edges
		path = QPainterPath()
		path.addRoundedRect(0, 0, size.width(), size.height(), self.corner_radius, self.corner_radius)
		
#		path2 = QPainterPath()
#		path2.addRoundedRect(3, 3, current_size.width(), current_size.height(), self.corner_radius, self.corner_radius)
#		pen = QPen(Qt.GlobalColor.red, 3)
#		painter.strokePath(path2, pen)
		
		
		painter.fillPath(path, QBrush(Qt.GlobalColor.black))  # Fill with white (adjust as needed)
		
		
		painter.end()
		
		self.rounded_mask = mask
		
	def paintEvent(self, event):
		size = self.rect().size()
		painter = QPainter(self)
		
		# Draw content area (optional)
		# ... (your content drawing logic)
		
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