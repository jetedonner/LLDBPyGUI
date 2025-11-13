import lldb
from PyQt6.QtCore import pyqtSignal

from lib.fileInfos import GetFileHeader
from lib.subworker.baseSubWorker import BaseSubWorker, SubWorkerType


class LoadFileInfosSubWorker(BaseSubWorker):
	subwkrType = SubWorkerType.LOAD_FILEINFOS_SUBWORKER

	loadFileInfosCallback = pyqtSignal(object, object)

	def __init__(self, driver):
		super(LoadFileInfosSubWorker, self).__init__(driver)

	def runSubWorker(self, driver, *argv, **args):
		super().runSubWorker(driver, *argv, **args)
		self.getFileInfos()

	def getFileInfos(self):
		if self.target:
			exe = self.target.GetExecutable().GetDirectory() + "/" + self.target.GetExecutable().GetFilename()  # "/libexternal.dylib" # + self.target.GetExecutable().GetFilename()
			mach_header = GetFileHeader(exe)
			self.loadFileInfosCallback.emit(mach_header, self.target)
