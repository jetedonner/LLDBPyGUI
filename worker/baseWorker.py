#!/usr/bin/env python3

import lldb

from PyQt6.QtCore import *


class BaseWorkerReceiver(QObject):
	interruptWorker = pyqtSignal()


class BaseWorkerSignals(QObject):
	finished = pyqtSignal()
	sendStatusBarUpdate = pyqtSignal(str)
	sendProgressUpdate = pyqtSignal(int, str)


class BaseWorker(QRunnable):
	interruptWorker = False
	driver = None

	def __init__(self, driver):
		super(BaseWorker, self).__init__()
		self.isWorkerActive = False
		self.driver = driver

		self.signals = BaseWorkerSignals()

	def run(self):
		# QCoreApplication.processEvents()
		self.runWorker()

	def runWorker(self):
		if self.isWorkerActive:
			self.interruptWorker = True
			return
		else:
			self.interruptWorker = False
		self.isWorkerActive = True
		# QCoreApplication.processEvents()

		self.workerFunc()

		self.isWorkerActive = False
		self.signals.finished.emit()

	# QCoreApplication.processEvents()

	def workerFunc(self):
		pass

	def sendStatusBarUpdate(self, statustxt=""):
		self.signals.sendStatusBarUpdate.emit(statustxt)

	# QCoreApplication.processEvents()

	def sendProgressUpdate(self, progress, statustxt=""):
		self.signals.sendProgressUpdate.emit(int(progress), statustxt)

	# QCoreApplication.processEvents()

	def handle_interruptWorker(self):
		#		print(f"Received interrupt in the sysLog worker thread")
		self.interruptWorker = True
		self.isWorkerActive = False
		pass
