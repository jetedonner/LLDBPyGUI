import lldb
from PyQt6.QtCore import pyqtSignal

from lib.subworker.baseSubWorker import BaseSubWorker, SubWorkerType


class LoadModuleDisassemblySubWorker(BaseSubWorker):
	subwkrType = SubWorkerType.LOAD_FILESTATS_SUBWORKER

	loadJSONCallback = pyqtSignal(str)

	def __init__(self, driver):
		super(LoadModuleDisassemblySubWorker, self).__init__(driver)

	def runSubWorker(self, driver, *argv, **args):
		super().runSubWorker(driver, *argv, **args)
		# self.loadFileStats()

	# def loadFileStats(self):
	#     statistics = self.target.GetStatistics()
	#     stream = lldb.SBStream()
	#     success = statistics.GetAsJSON(stream)
	#     if success:
	#         self.loadJSONCallback.emit(str(stream.GetData()))
