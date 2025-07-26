#!/usr/bin/env python3
import time

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from ui.customQt.QClickLabel import *
from config import *
from ui.helper.dbgOutputHelper import logDbgC, DebugLevel, get_main_window


class UserActionNeededDialog(QDialog):

	timerSteps = 3
	timerStepsCur = 0
	tmrDlgShowing = None

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

		# Create layout and label for the GIF
		layout = QVBoxLayout()
		# self.gif_label = QLabel()
		# # self.gif_label.setFixedSize(QSize(96, 96))
		# layout.addWidget(self.gif_label, alignment=Qt.AlignmentFlag.AlignCenter)
		self.lblMsg = QLabel(f"")
		self.lblMsg2 = QLabel(f"")
		self.setRemainingTimer(self.timerSteps)
		self.lblTitle = QLabel("User action needed!")
		self.fntTitle = QFont()
		self.fntTitle.setFamily(f"Courier New")
		self.fntTitle.setBold(True)
		self.fntTitle.setPointSize(21)

		# palTitle = QPalette()
		# clrTitle = QColor("red")
		# palTitle.setColor(QPalette.ColorRole.HighlightedText, clrTitle)
		# palTitle.setColor(QPalette.ColorRole.Text, clrTitle)
		# palTitle.setBrush(QPalette.ColorRole.Text, QBrush(clrTitle))
		#
		# # palTitle.setColor(QPalette.ColorRole.Text)
		# self.lblTitle.setPalette(palTitle)
		self.lblTitle.setFont(self.fntTitle)
		self.lblTitle.setStyleSheet("color: red;")
		layout.addWidget(self.lblTitle, alignment=Qt.AlignmentFlag.AlignCenter)

		self.setLayout(layout)

		layout.addWidget(self.lblMsg, alignment=Qt.AlignmentFlag.AlignCenter)
		layout.addWidget(self.lblMsg2, alignment=Qt.AlignmentFlag.AlignCenter)
	
		# Load and set the animated GIF
		# self.movie = QMovie("./resources/img/Bean-Eater@1x-1.0s-200px-200px.gif") #DoubleRingSpinner.gif") #Loading-Eclipse-200pxX200px.gif") #
		# self.movie.setScaledSize(QSize(64, 64))
		# self.gif_label.setMovie(self.movie)
		# self.movie.start()
		
		bg_color = QColor(220, 220, 220, 128)  # Adjust alpha value for desired transparency

		palette = self.palette()
		palette.setColor(palette.ColorRole.Window, bg_color)
		self.setPalette(palette)
		self.setFixedSize(350, 175)
		# Set default corner radius
		self.corner_radius = 10
		self.border_width = 5
		
		# Create rounded corner mask
		self.create_rounded_mask()
		
		# Set the mask for the dialog
		self.setMask(self.rounded_mask)
		
		self.setModal(True)

		self.startCloseTimer()

	def setRemainingTimer(self, remainingSecs):
		self.lblMsg.setText(f"!!! SCANF HIT !!!")
		self.lblMsg2.setText(f"Going to LLDB Console in {remainingSecs} sec ...")

	def startCloseTimer(self):
		self.timerSteps = 3
		self.timerStepsCur = 0
		self.tmrDlgShowing = QTimer()
		self.tmrDlgShowing.setInterval(1000)  # 0.5 seconds
		self.tmrDlgShowing.timeout.connect(self.handle_timerEvent)
		self.tmrDlgShowing.start()
		self.handle_timerEvent()

	def handle_timerEvent(self):
		if self.timerStepsCur <= self.timerSteps:
			self.setRemainingTimer(self.timerSteps - self.timerStepsCur)
			self.timerStepsCur += 1
		else:
			self.handle_closeAndGotoConsole()

	def handle_closeAndGotoConsole(self):
		if self.tmrDlgShowing.isActive():
			self.tmrDlgShowing.stop()

		# self.tmrDlgShowing.killTimer()
		self.close()
		get_main_window().wdtBPsWPs.treBPs.show_notification()

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
		if event.key() == Qt.Key.Key_Escape or event.key() == Qt.Key.Key_Space or event.key() == Qt.Key.Key_Return:
			self.handle_closeAndGotoConsole()
		# if event.key() == Qt.Key.Key_Escape:
		# 	logDbgC("Escape ignored.", DebugLevel.Verbose)
		# 	event.ignore()  # Prevent default reject()
		# else:
		super().keyPressEvent(event)