from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QStatusBar, QProgressBar

from helper.debugHelper import logDbgC


class StatusBarManager(QObject):
	mainWindow = None
	statusBar = None
	progressbar = None

	def __init__(self, mainWindow):
		super().__init__()

		self.mainWindow = mainWindow
		self.initStatusBar()

	def initStatusBar(self):
		self.statusBar = QStatusBar()
		self.statusBar.setContentsMargins(0, 0, 10, 0)
		self.mainWindow.setStatusBar(self.statusBar)
		self.progressbar = QProgressBar()
		self.progressbar.setMinimum(0)
		self.progressbar.setMaximum(100)
		self.progressbar.setValue(0)
		self.progressbar.setFixedWidth(256)
		# self.progressbar.setContentsMargins(0, 0, 30, 0)
		self.statusBar.addPermanentWidget(self.progressbar)

	# @staticmethod
	def setStatusMsg(self, msg, timeout=1500, logVerbose=True):
		self.statusBar.showMessage(msg, timeout)
		if logVerbose:
			# logDbgC(f"New status message: {msg}")
			logDbgC(f"{msg}")

	def setProgress(self, progress):
		# logDbgC(f"New progress value: {progress}")
		self.progressbar.setValue(progress)
		# QApplication.processEvents()
