import lldb
from PyQt6.QtCore import pyqtSignal

from lib.fileInfos import count_lines_of_code
from lib.subworker.baseSubWorker import BaseSubWorker, SubWorkerType, SubWorkerCommands


class LoadSourcecodeSubWorker(BaseSubWorker):
	subwkrType = SubWorkerType.LOAD_SOURCECODE_SUBWORKER

	finishedLoadSourcecodeCallback = pyqtSignal(str)

	sourceFile = ''
	debugger = None
	lineNum = 1
	isLoadSourceCodeActive = True

	def __init__(self, driver):
		super(LoadSourcecodeSubWorker, self).__init__(driver)

		self.subwkrCmds = {SubWorkerCommands.LOAD_SOURCECODE_SUBWORKER_CMD: self.runSubWorker}

		self.debugger = self.driver.debugger
		self.isLoadSourceCodeActive = False

	def runSubWorker(self, driver, *argv, **args):
		super().runSubWorker(driver, *argv, **args)

		if args:
			self.sourceFile = str(args["sourceFile"])
			self.lineNum = int(args["lineNum"])

		self.runLoadSourceCode()

	# def loadStacktrace(self):
	# 	self.process = self.driver.target.GetProcess()
	# 	self.thread = self.process.GetThreadAtIndex(0)
	#
	# 	idx = 0
	# 	if self.thread:
	# 		# self.clear()
	# 		# self.processNode = QTreeWidgetItem(self, ["#0 " + str(self.process.GetProcessID()),
	# 		# 										  hex(self.process.GetProcessID()) + "",
	# 		# 										  self.process.GetTarget().GetExecutable().GetFilename(), '', ''])
	# 		# self.threadNode = QTreeWidgetItem(self.processNode, ["#" + str(idx) + " " + str(self.thread.GetThreadID()),
	# 		# 													 hex(self.thread.GetThreadID()) + "",
	# 		# 													 self.thread.GetQueueName(), '', ''])
	# 		numFrames = self.thread.GetNumFrames()
	#
	# 		for idx2 in range(numFrames):
	# 			frame = self.thread.GetFrameAtIndex(idx2)
	# 			print(f"frame {idx2}: {frame} ...")
	# 			# frameNode = QTreeWidgetItem(self.threadNode,
	# 			# 							["#" + str(frame.GetFrameID()), "", str(frame.GetPCAddress()),
	# 			# 							 str(hex(frame.GetPC())), GuessLanguage(frame)])
	# 			idx += 1
	#
	# 		# self.processNode.setExpanded(True)
	# 		# self.threadNode.setExpanded(True)
	# 	# QApplication.processEvents()

	def runLoadSourceCode(self):
		if self.isLoadSourceCodeActive:
			return

		self.isLoadSourceCodeActive = True

		# self.sourceFile = sourcefileToUse = filename if filename != "" else self.sourceFile
		# print(f"RUN LOAD SOURCECODE: {self.sourceFile} ...")
		frame = self.driver.target.GetProcess().GetThreadAtIndex(0).GetFrameAtIndex(0)
		lineEntry = frame.GetLineEntry()
		self.sourceFile = lineEntry.GetFileSpec().fullpath

		# context = frame.GetSymbolContext(lldb.eSymbolContextEverything)
		self.lineNum = lineEntry.GetLine()  # context.GetLineEntry().GetLine()
		print(f"SOURCECODE filepath: {self.sourceFile}, line: {self.lineNum} ...")
		# self.loadStacktrace()

		filespec = lldb.SBFileSpec(self.sourceFile, False)
		source_mgr = self.debugger.GetSourceManager()

		linesOfCode = count_lines_of_code(self.sourceFile)
		# print(f"linesOfCode: {linesOfCode} / {linesOfCode - self.lineNum}")
		if self.lineNum < 0 or self.lineNum > linesOfCode:
			return

		stream = lldb.SBStream()
		source_mgr.DisplaySourceLinesWithLineNumbers(filespec, self.lineNum, self.lineNum, linesOfCode - self.lineNum,
													 '=>', stream)

		self.finishedLoadSourcecodeCallback.emit(stream.GetData())
		self.isLoadSourceCodeActive = False
