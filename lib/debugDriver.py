import enum
import queue
# import lldb
import struct
from pprint import pprint

import lldb
from PyQt6.QtCore import QObject, pyqtSlot

from lib.eventListener import EventListener
from lib.fileInfos import find_main
from lib.projectData import ProjectData
from lib.subworker.analyzeCompleteFileSubWorker import AnalyzeCompleteFileSubWorker
from lib.subworker.baseSubWorker import SubWorkerType, SubWorkerCommands
from lib.subworker.decompileModuleSubWorker import DecompileModuleSubWorker
from lib.subworker.loadFileInfosSubWorker import LoadFileInfosSubWorker
from lib.subworker.loadFileStatsSubWorker import LoadFileStatsSubWorker
from lib.subworker.loadRegisterSubWorker import LoadRegisterSubWorker
from lib.subworker.loadSourcecodeSubWorker import LoadSourcecodeSubWorker
from lib.thirdParty.breakpointManager import BreakpointManager
from ui.customQt.QControlFlowWidget import *


# class ProjectData():
#
#     target = None
#
#     mainModule = ""
#     allModules = {}
#     allBPs = {}
#
#     # def __init__(self, mainModule):
#     def __init__(self):
#         super().__init__()
#
#         # self.mainModule = mainModule
#         # self.allModules.update({mainModule: {}})
#
#     def addModule(self, module, isMainModule=False):
#         filename = os.path.basename(module)
#         if isMainModule:
#             self.mainModule = {"file": filename, "path": module}
#         self.allModules.update({len(self.allModules): {"file": filename, "path": module}})
#
#     def addBreakpoint(self, bp):
#         # len(self.allBPs)
#         locs = []
#         for bl in bp:
#             locs.append({"blId": str(bp.GetID()) + "." + str(bl.GetID()), "addr": hex(bl.GetAddress().GetLoadAddress(self.target))})
#         self.allBPs.update({bp.GetID(): {"bpId": bp.GetID(), "name": "Dummy Name", "enabled": bp.IsEnabled(), "locations": locs}}) # bp.GetName()
#
#     def updateBreakpoint(self, bp):
#         locs = []
#         for bl in bp:
#             locs.append({"blId": str(bp.GetID()) + "." + str(bl.GetID()),
#                          "addr": hex(bl.GetAddress().GetLoadAddress(self.target))})
#         self.allBPs.update(
#             {bp.GetID(): {"bpId": bp.GetID(), "name": "Dummy Name", "enabled": bp.IsEnabled(), "locations": locs}})  # bp.GetName()
#
#     def removeBreakpoint(self, bp):
#         self.allBPs.pop(bp.GetID())
#
#     def to_dict(self):
#         return {
#             "mainModule": self.mainModule,
#             "allModules": self.allModules,
#             "allBPs": self.allBPs
#         }

class DebugDriver(QObject):
	thread = None
	worker = None
	debugger = None
	target = None

	show_dialog = pyqtSignal()
	loadingFinished = pyqtSignal()
	finishedCleanUp = pyqtSignal()
	sendProgressUpdate = pyqtSignal(float, str)
	sendProgress = pyqtSignal(int)

	logDbgC = pyqtSignal(str, object)

	loadFileInfosCallback = pyqtSignal(object, object)
	loadJSONCallback = pyqtSignal(str)
	loadModulesCallback = pyqtSignal(object, object)
	loadModulesCallback2 = pyqtSignal(object)

	loadRegisterCallback = pyqtSignal(str)
	loadRegisterValueCallback = pyqtSignal(int, str, str, str)
	updateRegisterValueCallback = pyqtSignal(int, str, str, str)

	loadVariableValueCallback = pyqtSignal(str, str, str, str, str)
	updateVariableValueCallback = pyqtSignal(str, str, str, str, str)

	loadInstructionCallback = pyqtSignal(object, object)
	loadStringCallback = pyqtSignal(str, int, str)
	loadSymbolCallback = pyqtSignal(str)
	loadSymbolCallbackNG = pyqtSignal(dict)
	loadActionCallback = pyqtSignal(object)
	finishedLoadInstructionsCallback = pyqtSignal(object, str, object, int)
	finishedLoadModuleCallback = pyqtSignal(object, str, list)
	finishedLoadSourcecodeCallback = pyqtSignal(str)

	handle_event_listener = pyqtSignal(object)

	handle_processEvent = None
	sourceFileName = ""
	regSubWkr = None
	decSubWkr = None
	acfSubWkr = None

	bpMgr = None
	projectData = None

	event_queue = queue.Queue()

	def __init__(self, debugger, sourceFileName=""):
		super().__init__()

		self.debugger = debugger
		self.sourceFileName = sourceFileName

		self.bpMgr = BreakpointManager(self)
		self.projectData = ProjectData()
		self.listener = self.debugger.GetListener() # lldb.SBListener()
		self.eventListener = EventListener(self.listener, self.event_queue)

		if self.worker is not None:
			self.worker.aborted = False
			self.worker.isDone = False
			self.worker.isRunning = False
			self.worker.isProcessRunning = False
			self.thread = QThread()

	def poll_events(self):
		while not self.event_queue.empty():
			event = self.event_queue.get()
			# self.handle_event(event)
			print(f"event: {event}")
			# self.handle_processEvent(event)
			self.handle_event_listener.emit(event)

	def initWorker(self):
		self.worker = DebugDriverWorker(self.debugger, self.sourceFileName, self)
		self.worker.aborted = False

		self.thread = QThread()
		self.worker.moveToThread(self.thread)
		self.thread.started.connect(self.worker.run)

		self.worker.show_dialog.connect(self.show_dialog)
		self.worker.loadingFinished.connect(self.loadingFinished)
		self.worker.finishedCleanUp.connect(self.finishedCleanUp)
		self.worker.finishedCleanUp.connect(self.thread.quit)
		self.worker.finishedCleanUp.connect(self.worker.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)
		# self.worker.sendProgressUpdate.connect(self.sendProgressUpdate) # = self.sendProgressUpdate #.connect(self.sendProgressUpdate)
		# self.worker.sendProgress.connect(self.sendProgress) # = self.sendProgress #.connect(self.sendProgress)
		self.worker.connectSignals(self.sendProgressUpdate)
		self.worker.logDbgC = self.logDbgC

		fileStatsSubWkr = self.worker.getSubWorker(SubWorkerType.LOAD_FILESTATS_SUBWORKER)
		fileStatsSubWkr.loadJSONCallback.connect(self.loadJSONCallback)

		fileInfoSubWkr = self.worker.getSubWorker(SubWorkerType.LOAD_FILEINFOS_SUBWORKER)
		fileInfoSubWkr.loadFileInfosCallback.connect(self.loadFileInfosCallback)

		regSubWkr = self.worker.getSubWorker(SubWorkerType.LOAD_REGISTER_SUBWORKER)
		regSubWkr.loadRegisterCallback.connect(self.loadRegisterCallback)
		regSubWkr.loadRegisterValueCallback.connect(self.loadRegisterValueCallback)
		regSubWkr.updateRegisterValueCallback.connect(self.updateRegisterValueCallback)
		regSubWkr.loadVariableValueCallback.connect(self.loadVariableValueCallback)
		regSubWkr.updateVariableValueCallback.connect(self.updateVariableValueCallback)
		self.regSubWkr = regSubWkr

		analyzeCompFileSubWkr = self.worker.getSubWorker(SubWorkerType.ANALYZE_COMPLETE_FILE_SUBWORKER)
		analyzeCompFileSubWkr.loadSymbolCallback.connect(self.loadSymbolCallback)
		analyzeCompFileSubWkr.loadSymbolCallbackNG.connect(self.loadSymbolCallbackNG)
		analyzeCompFileSubWkr.loadInstructionCallback.connect(self.loadInstructionCallback)
		analyzeCompFileSubWkr.loadStringCallback.connect(self.loadStringCallback)
		analyzeCompFileSubWkr.loadActionCallback.connect(self.loadActionCallback)
		
		analyzeCompFileSubWkr.finishedLoadInstructionsCallback.connect(self.finishedLoadInstructionsCallback)
		analyzeCompFileSubWkr.handle_processEvent = self.handle_processEvent
		analyzeCompFileSubWkr.loadModulesCallback.connect(self.loadModulesCallback)
		analyzeCompFileSubWkr.loadModulesCallback2.connect(self.loadModulesCallback2)
		self.acfSubWkr = analyzeCompFileSubWkr

		decompileModuöeSubWkr = self.worker.getSubWorker(SubWorkerType.DECOMPILE_MODULE_SUBWORKER)
		decompileModuöeSubWkr.loadSymbolCallback.connect(self.loadSymbolCallback)
		decompileModuöeSubWkr.loadInstructionCallback.connect(self.loadInstructionCallback)
		decompileModuöeSubWkr.loadModulesCallback2.connect(self.loadModulesCallback2)
		decompileModuöeSubWkr.loadStringCallback.connect(self.loadStringCallback)
		decompileModuöeSubWkr.finishedLoadModuleCallback.connect(self.finishedLoadModuleCallback)
		decompileModuöeSubWkr.show_dialog.connect(self.show_dialog)
		self.decSubWkr = decompileModuöeSubWkr

		loadSourcecodeSubWkr = self.worker.getSubWorker(SubWorkerType.LOAD_SOURCECODE_SUBWORKER)
		loadSourcecodeSubWkr.finishedLoadSourcecodeCallback.connect(self.finishedLoadSourcecodeCallback)

		# self.eventListener.starListener()
		# # Timer to poll event queue
		# self.timer = QTimer()
		# self.timer.timeout.connect(self.poll_events)
		# self.timer.start(100)

	target_image = ""

	def loadTarget(self, target_image, arch="x86_64-apple-macosx15.1.1", args=None):
		self.target_image = target_image
		self.projectData.addModule(target_image, True)

		if self.isWorkerRunning():
			self.stopWorker()

		self.initWorker()
		self.target = self.createTarget(target_image, arch, args)
		self.projectData.target = self.target
		# self.worker.set_up_dialog_breakpoint(self.debugger, None, None, None)

		# Example usage
		# self.debugger.SetAsync(True)
		# self.extract_code_signature(target_image, self.target)
		# self.debugger.SetAsync(False)
		# self.target.getLoadAddress = getLoadAddress
		self.worker.target = self.target
		self.thread.start()
		# self.extract_code_signature(target_image, self.target)

	def extract_code_signature(self, path, target):
		# Load binary with LLDB
		# debugger = lldb.SBDebugger.Create()
		# debugger.SetAsync(False)
		# target = debugger.CreateTarget(path)

		if not target.IsValid():
			print("Failed to create LLDB target.")
			return

		# Read binary file directly
		with open(path, "rb") as f:
			data = f.read()

			# Mach-O header offset (skip fat header if needed)
		offset = 0
		magic = struct.unpack_from("<I", data, offset)[0]

		if magic == 0xcafebabe:
			print("Fat binary detected. Skipping to appropriate architecture...")
			nfat_arch = struct.unpack_from(">I", data, 4)[0]
			for i in range(nfat_arch):
				arch_offset = 8 + i * 20
				cpu_type, cpu_subtype, offset_arch = struct.unpack_from(">III", data, arch_offset)
				print(f"Arch {i}: CPU type={cpu_type}, offset={offset_arch}")
				offset = offset_arch
				break  # You can refine this to pick the right arch

		# Parse Mach-O header
		ncmds = struct.unpack_from("<I", data, offset + 16)[0]
		cmd_offset = offset + 32  # Start of load commands

		for i in range(ncmds):
			cmd, cmdsize = struct.unpack_from("<II", data, cmd_offset)
			if cmd == 0x1d:  # LC_CODE_SIGNATURE
				dataoff, datasize = struct.unpack_from("<II", data, cmd_offset + 8)
				print(f"Found LC_CODE_SIGNATURE at offset {dataoff}, size {datasize}")
				break
			cmd_offset += cmdsize
		else:
			print("LC_CODE_SIGNATURE not found.")
			return

		# Extract and parse signature blob
		blob = data[dataoff:dataoff + datasize]
		magic, length, count = struct.unpack_from(">III", blob, 0)
		print(f"SuperBlob: magic=0x{magic:x}, length={length}, count={count}")

		print(f"SuperBlob Blobs count: {count} ...")
		for i in range(count):
			index_offset = 12 + i * 8
			blob_type, blob_offset = struct.unpack_from(">II", blob, index_offset)
			print(f"Blob {i}: type=0x{blob_type:x}, offset={blob_offset}")

			if blob_type == 0xfade0c02:  # CSSLOT_CODEDIRECTORY
				cd_blob = blob[blob_offset:]
				version, flags, hash_offset = struct.unpack_from(">III", cd_blob, 0)
				print(f"CodeDirectory: version={version}, flags=0x{flags:x}, hash_offset={hash_offset}")
				# Add hash validation here if needed

	def createTarget(self, target_image, arch="x86_64-apple-macosx15.1.1", args=None):

		self.target = self.debugger.CreateTargetWithFileAndArch(target_image, arch)  # , lldb.LLDB_ARCH_DEFAULT)
		# self.target = self.debugger.CreateTargetWithFileAndTargetTriple(target_image, args)
		# self.target.getLoadAddress = getLoadAddress
		return self.target

	def isWorkerRunning(self):
		return self.thread is not None and self.thread.isRunning() and not self.worker.aborted

	def stopWorker(self):
		logDbgC(f"stopWorker() ... before")
		if self.thread.isRunning() or True:  # self.worker.isRunning: # or self.worker.isRunning:
			logDbgC(f"stopWorker() ... if self.thread.isRunning():")
			self.setDone(True)
			logDbgC(f"stopWorker() ... after self.setDone(True)")
			idx = 0
			# self.worker.isRunning / self.thread.isRunning()
			while self.worker.isRunning and idx < 200:
				time.sleep(0.25)
				idx += 1
			self.thread.quit()
			self.thread.wait()
			logDbgC(f"stopWorker() ... after self.thread.quit()")
			return True
		return False

	def setDone(self, isDone=True):
		self.worker.setDone(isDone)

	def getPC(self, asHex=False):
		return self.worker.getPCNG(asHex)

	def continueProcess(self):
		return self.worker.continueProcess()

	def stopProcess(self):
		return self.worker.stopProcess()

	def isProcessRunning(self):
		return self.worker.isProcessRunning()

	def setProcessRunning(self, isRunning=True):
		self.worker.setProcessRunning(isRunning)

	def handleDbgCmd(self, cmd="process launch --stop-at-entry"):
		return self.worker.handleDbgCmd(cmd)


class PredefinedCommand(enum.Enum):
	ProcessLaunchStopAtEntry = (f"process launch --stop-at-entry", 1)
	ProcessContinue = (f"process continue", 2)
	SetBPAddNameByID = ('br name add -N {bpName} {bpID}', 4)

	@staticmethod
	def GetCmdStr(cmd):
		return cmd.value[0]

	@staticmethod
	def GetFormatedCommand(cmd, args):
		return cmd.format(**args)


class DebugDriverWorker(QObject):
	show_dialog = pyqtSignal()
	loadingFinished = pyqtSignal()
	finishedCleanUp = pyqtSignal()
	logDbg = pyqtSignal(str)
	# logDbgC = pyqtSignal(str)
	logDbgC = pyqtSignal(str, object)
	sendProgressUpdate = pyqtSignal(float, str)
	sendProgress = pyqtSignal(int)

	loadFileInfosCallback = pyqtSignal(object, object)
	loadJSONCallback = pyqtSignal(str)
	loadModulesCallback = pyqtSignal(object, object)

	loadRegisterCallback = pyqtSignal(str)
	loadRegisterValueCallback = pyqtSignal(int, str, str, str)
	updateRegisterValueCallback = pyqtSignal(int, str, str, str)

	loadInstructionCallback = pyqtSignal(object, object)
	loadStringCallback = pyqtSignal(str, int, str)
	loadSymbolCallback = pyqtSignal(str)
	loadActionCallback = pyqtSignal(object)
	finishedLoadInstructionsCallback = pyqtSignal(object, str, object, int)
	finishedLoadSourcecodeCallback = pyqtSignal(str)

	handle_breakpointEvent = None
	handle_processEvent = None
	handle_gotNewEvent = None

	loadRegisterSubWorker = None

	debugger = None
	target = None
	process = None
	thread = None
	frame = None
	module = None

	aborted = False
	done = False

	prg = 0

	allSubWorkers = {}

	main_oep = 0x0

	# shouldLoadRegister = False
	shouldContinueProcess = False
	shouldStopProcess = False
	isRunning = False

	currentCMD = SubWorkerCommands.IDLE_CMD
	lstLoadedMods = []

	parentDriver = None


	def __init__(self, debugger, sourceFileName="", parentDriver=None):
		super().__init__()

		self.setHelper = SettingsHelper()
		self.debugger = debugger
		self.parentDriver = parentDriver

		self.aborted = False
		self.allSubWorkers = {}
		# self.allInstructions = []
		# self.allModsAndInstructions = {}
		# self.connections = []
		# self.radius = 15
		self.main_oep = 0x0
		self.moduleName = ""
		self.sourceFileName = sourceFileName
		self.lineNum = 1

		self.addSubWorker(LoadFileInfosSubWorker(self))
		self.addSubWorker(LoadFileStatsSubWorker(self))
		self.addSubWorker(AnalyzeCompleteFileSubWorker(self))
		self.addSubWorker(DecompileModuleSubWorker(self))
		self.addSubWorker(LoadRegisterSubWorker(self))
		self.addSubWorker(LoadSourcecodeSubWorker(self))

	def connectSignals(self, sendProgressUpdate):
		self.sendProgressUpdate.connect(sendProgressUpdate)
		for wkr in self.allSubWorkers.values():
			wkr.sendProgressUpdate.connect(sendProgressUpdate)

	def addSubWorker(self, subwkr):
		# if self.allSubWorkers[subwkr.subwkrType.name] is None:
		if not subwkr.subwkrType.name in self.allSubWorkers.keys():
			subwkr.logDbgC.connect(self.logDbgC)
			# subwkr.sendProgressUpdate.connect(self.sendProgressUpdate)
			# subwkr.sendProgress.connect(self.sendProgress)

			self.allSubWorkers[subwkr.subwkrType.name] = subwkr

	def getSubWorker(self, subwkrType):
		if subwkrType.name in self.allSubWorkers.keys():
			return self.allSubWorkers[subwkrType.name]
		else:
			return None

	def setDone(self, isDone=True):
		self.done = isDone
		self.aborted = isDone

	def isDone(self):
		return self.done

	def isAborted(self):
		return self.aborted

	def disassembleModule(self, moduleName):
		# self.shouldLoadRegister = True
		print(f"debugDriver.disassembleModule({moduleName}) ...")
		self.moduleName = moduleName  # "/Voqlumes/Data/dev/python/LLDBGUI/_testtarget/libexternal.dylib" # moduleName
		# self.currentCMD = SubWorkerCommands.DECOMPILE_MODULE_SUBWORKER_CMD
		self.addCommandToQueueOrExecute(SubWorkerCommands.DECOMPILE_MODULE_SUBWORKER_CMD)

	initTabs = True

	def loadRegister(self, initTabs=True):
		# self.shouldLoadRegister = True
		# logDbgC(f"loadRegister({initTabs}) (1) ... ")
		self.initTabs = initTabs
		# self.getSubWorker(SubWorkerType.LOAD_REGISTER_SUBWORKER).initTabs = initTabs # .runSubWorker(self, initTabs=True)
		# self.currentCMD = SubWorkerCommands.LOAD_REGISTER_SUBWORKER_CMD
		self.addCommandToQueueOrExecute(SubWorkerCommands.LOAD_REGISTER_SUBWORKER_CMD)

	def continueProcess(self):
		self.shouldContinueProcess = True
		# self.currentCMD = SubWorkerCommands.RESUME_DBG_SUBWORKER_CMD
		self.addCommandToQueueOrExecute(SubWorkerCommands.RESUME_DBG_SUBWORKER_CMD)
		self.isRunning = True
		return self.isRunning

	def stopProcess(self):
		self.shouldStopProcess = True
		# self.currentCMD = SubWorkerCommands.INTERRUPT_DBG_SUBWORKER_CMD
		self.addCommandToQueueOrExecute(SubWorkerCommands.INTERRUPT_DBG_SUBWORKER_CMD)
		self.isRunning = False
		return self.isRunning

	def loadSourcecode(self):
		# self.shouldStopProcess = True
		# self.currentCMD = SubWorkerCommands.LOAD_SOURCECODE_SUBWORKER_CMD
		# self.isRunning = False
		# return self.isRunning
		self.addCommandToQueueOrExecute(SubWorkerCommands.LOAD_SOURCECODE_SUBWORKER_CMD)

	def getPCNG(self, asHex=False):
		rip = ''
		if self.thread:
			frame = self.thread.GetFrameAtIndex(0)
			pprint(frame)
			print(f"GOT IT ....")
			if frame:
				registerList = frame.GetRegisters()
				numRegisters = registerList.GetSize()
				# print(f"numRegisters: {numRegisters}")
				if numRegisters > 0:
					GPRs = frame.registers[0]
					# print('%s (number of children = %d):' % (GPRs.name, GPRs.num_children))
					for reg in GPRs:
						# print('Name: ', reg.name, ' Value: ', reg.value)
						if reg.name == "pc":
							print(f'GetPCAddress => {reg.value}')
							rip = reg.value
		return rip

	def getPC(self, asHex=False):
		target = self.target
		if target:
			process = target.GetProcess()
			if process:
				thread = process.GetThreadAtIndex(0)
				if thread:
					for z in range(thread.GetNumFrames()):
						frame = thread.GetFrameAtIndex(z)
						if frame.GetModule().GetFileSpec().GetFilename() != target.GetExecutable().GetFilename():
							continue
						if frame:
							if asHex:
								return hex(frame.GetPC())
							else:
								return frame.GetPC()
		return ""

	# driver = None
	# modulePath = ""
	#
	# def loadOrDecompileModule(self, driver, modulePath=""):
	#     self.driver = driver
	#     self.modulePath = modulePath
	#     self.addCommandToQueueOrExecute(SubWorkerCommands.DECOMPILE_MODULE_SUBWORKER_CMD)

	def isProcessRunning(self):
		return self.isRunning

	def setProcessRunning(self, isRunning=True):
		self.isRunning = isRunning
		# if self.isProcessRunning():
		#     self.shouldStopProcess = True
		# else:
		#     self.shouldContinueProcess = True

	cmdQueue = []

	def addCommandToQueueOrExecute(self, cmd):
		if self.currentCMD != SubWorkerCommands.IDLE_CMD:
			if not cmd in self.cmdQueue:
				self.cmdQueue.append(cmd)
		else:
			if self.currentCMD != cmd:
				self.currentCMD = cmd

	def getNextCommand(self):
		if len(self.cmdQueue) > 0:
			return self.cmdQueue.pop(0)
		else:
			return SubWorkerCommands.IDLE_CMD

	@pyqtSlot()
	def run(self):
		logDbgC(f"GetAsync(): {self.debugger.GetAsync()}")
		self.isRunning = True
		self.extract_code_signature()
		self.prg = 0
		self.show_dialog.emit()
		# self.target
		# self..extract_code_signature(target_image, self.target)
		self.updateProgress(5, f"Launching process (stop at entry)")
		self.handleDbgCmd(PredefinedCommand.GetCmdStr(
			PredefinedCommand.ProcessLaunchStopAtEntry))  # f"process launch --stop-at-entry")
		self.updateProgress(35, f"Launching process (stop at entry) => DONE!!!")
		self.main_oep, symbol = find_main(self.debugger,
										  "main")  # "___debug_blank_executor_main")  # , "___debug_blank_executor_main")
		if self.main_oep != 0 and (True or self.setHelper.getValue(SettingsValues.BreakpointAtMainFunc)):
			# self.driver.debugger.HandleCommand(f'breakpoint set -a {hex(main_oep)} -N kimon')
			bp = self.target.BreakpointCreateByAddress(self.main_oep)  # .BreakpointCreateByName("main")
			# for bl in bp:
			# 	self.logDbgC.emit(f"bl.location: {bl}", DebugLevel.Verbose)
			bp.SetOneShot(True)
			self.mainID = bp.GetID()
			self.handleDbgCmd(
				PredefinedCommand.GetFormatedCommand(PredefinedCommand.GetCmdStr(PredefinedCommand.SetBPAddNameByID),
													 {"bpName": "main",  # "___debug_blank_executor_main", # "main",
													  "bpID": bp.GetID()}))  # f'br name add -N main {bp.GetID()}')
			bp.SetScriptCallbackFunction("main_hit")

		#     # self.logDbgC.emit(f'breakpoint set "main": {bp}', DebugLevel.Verbose)
		# # self.driver.debugger.HandleCommand('breakpoint set --name main')
		logDbgC(f"GetAsync(): {self.debugger.GetAsync()}")
		self.updateProgress(35, f"Continuing process ...")
		self.handleDbgCmd(PredefinedCommand.GetCmdStr(PredefinedCommand.ProcessContinue))  # 'process continue')
		self.updateProgress(45, f"Get file infos ...")
		self.getSubWorker(SubWorkerType.LOAD_FILEINFOS_SUBWORKER).runSubWorker(self)
		self.updateProgress(55, f"Get file statistics ...")
		self.getSubWorker(SubWorkerType.LOAD_FILESTATS_SUBWORKER).runSubWorker(self)
		self.updateProgress(65, f"Analyzing modules ...")
		self.getSubWorker(SubWorkerType.ANALYZE_COMPLETE_FILE_SUBWORKER).runSubWorker(self)
		self.updateProgress(75, f"Loading registers and variables ...")
		self.getSubWorker(SubWorkerType.LOAD_REGISTER_SUBWORKER).runSubWorker(self, initTabs=True)
		self.updateProgress(85, f"Loading sourcecode ...")
		self.getSubWorker(SubWorkerType.LOAD_SOURCECODE_SUBWORKER).runSubWorker(self, sourceFile=self.sourceFileName,
																				lineNum=self.lineNum)

		self.updateProgress(95, f"Target {self.getTargetFilename()} successfully loaded!")
		prg = 100
		if prg == 100:
			self.sendProgressUpdate.emit(prg, f"New progress value is: {prg}")
			# prg += 2.5
			self.loadingFinished.emit()

		while not self.aborted and not self.done:

			if self.shouldContinueProcess:
				self.process.Continue()
				self.isRunning = True
				self.shouldContinueProcess = False

			elif self.shouldStopProcess:
				self.process.Stop()
				self.isRunning = False
				self.shouldStopProcess = False

			# print(f"Before: if self.currentCMD != SubWorkerCommands.IDLE_CMD: ...")
			if self.currentCMD != SubWorkerCommands.IDLE_CMD:
				# print(f"if self.currentCMD ({self.currentCMD}) != SubWorkerCommands.IDLE_CMD ({self.currentCMD} / {SubWorkerCommands.LOAD_REGISTER_SUBWORKER_CMD}): ...")
				if self.currentCMD == SubWorkerCommands.LOAD_REGISTER_SUBWORKER_CMD:
					# self.logDbgC.emit(f"if self.currentCMD == SubWorkerCommands.LOAD_REGISTER_SUBWORKER_CMD: ...", DebugLevel.Verbose)
					self.getSubWorker(SubWorkerType.LOAD_REGISTER_SUBWORKER).execCmd(
						SubWorkerCommands.LOAD_REGISTER_SUBWORKER_CMD, initTabs=False)
				elif self.currentCMD == SubWorkerCommands.DECOMPILE_MODULE_SUBWORKER_CMD:
					# self.logDbgC.emit(f"DECOMPILE_MODULE_SUBWORKER_CMD: {self.moduleName} ...", DebugLevel.Verbose)
					if not self.moduleName in self.lstLoadedMods:
						self.lstLoadedMods.append(self.moduleName)
						print(f"DECOMPILE_MODULE_SUBWORKER_CMD: {self.moduleName} ...")
						self.getSubWorker(SubWorkerType.DECOMPILE_MODULE_SUBWORKER).execCmd(
							SubWorkerCommands.DECOMPILE_MODULE_SUBWORKER_CMD, self, modulePath=self.moduleName)
					# else:
					#     continue

				elif self.currentCMD == SubWorkerCommands.LOAD_SOURCECODE_SUBWORKER_CMD:
					self.getSubWorker(SubWorkerType.LOAD_SOURCECODE_SUBWORKER).execCmd(
						SubWorkerCommands.LOAD_SOURCECODE_SUBWORKER_CMD, self,
						sourceFile=self.sourceFileName,
						lineNum=self.lineNum)
				self.currentCMD = self.getNextCommand()  # SubWorkerCommands.IDLE_CMD

			time.sleep(0.1)

		if self.aborted:
			if self.process:
				self.process.Kill()

		self.done = True
		self.isRunning = False
		self.finishedCleanUp.emit()
		# self.finished.emit()

	# def set_up_dialog_breakpoint(self, debugger, command, result, internal_dict):
	#     """
	#     Sets a breakpoint on a function that shows a dialog and attaches a Python command.
	#     """
	#     # Set a breakpoint on the Objective-C method for showing an alert on macOS
	#     target = debugger.GetSelectedTarget()
	#     if not target:
	#         print("Error: No target is selected.")
	#         return
	#
	#     # Find the breakpoint that we've already set, or create it
	#     alert_bp = target.BreakpointCreateByName("runModal")# BreakpointCreateByLocation("NSAlert.m", 112, 1)
	#
	#     # Or, if you know the symbol, use this:
	#     # alert_bp = target.BreakpointCreateByName("-[NSAlert runModal]", "MyProject")
	#
	#     if not alert_bp.IsValid():
	#         print("Error: Could not create breakpoint.")
	#         return
	#
	#     # Add the Python command to the breakpoint
	#     alert_bp.AddNameCommandScript(
	#         "LLDBPyGUING.bring_app_to_front_on_dialog(frame, bp_loc, internal_dict)"
	#     )
	#     print("Breakpoint set and configured to bring app to front on dialogs.")

	def set_up_dialog_breakpoint(self, debugger, command, result, internal_dict):
		"""
		Sets a breakpoint and attaches a Python callback function.
		"""
		target = debugger.GetSelectedTarget()
		if not target:
			print("Error: No target is selected.")
			return

		# Create the breakpoint by its name
		alert_bp = target.BreakpointCreateByName("-[NSAlert runModal]")

		if not alert_bp.IsValid():
			print("Error: Could not create breakpoint.")
			return

		# Set the Python callback function
		alert_bp.SetScriptCallbackFunction("LLDBPyGUING.bring_app_to_front_on_dialog")

		print("Breakpoint set and configured to bring app to front on dialogs.")

	def updateProgress(self, prg, msg=""):
		self.prg = prg
		self.sendProgressUpdate.emit(float(self.prg), str(msg))

	def handleDbgCmd(self, cmd="process launch --stop-at-entry"):
		self.debugger.HandleCommand(cmd)

	def getTargetFilename(self, targetWithFilename=None):
		if targetWithFilename is None:
			targetToUse = self.target
		else:
			targetToUse = targetWithFilename

		if targetToUse is not None and targetToUse.IsValid():
			filename = targetToUse.GetExecutable().GetFilename()
			if filename is not None and filename != "":
				return filename
		return ""

	def extract_code_signature(self, path="/Volumes/Data/dev/python/LLDBGUI/_testtarget/cocoa_windowed_objc2"):
		# Load binary with LLDB (optional, for introspection)
		debugger = lldb.SBDebugger.Create()
		debugger.SetAsync(False)
		target = debugger.CreateTarget(path)

		if not target.IsValid():
			print("Failed to create LLDB target.")
			return

		# Read binary file directly
		with open(path, "rb") as f:
			data = f.read()

		# Mach-O header offset (skip fat header if needed)
		offset = 0
		magic = struct.unpack_from("<I", data, offset)[0]

		if magic == 0xcafebabe:
			print("Fat binary detected. Skipping to appropriate architecture...")
			nfat_arch = struct.unpack_from(">I", data, 4)[0]
			for i in range(nfat_arch):
				arch_offset = 8 + i * 20
				cpu_type, cpu_subtype, offset_arch = struct.unpack_from(">III", data, arch_offset)
				print(f"Arch {i}: CPU type={cpu_type}, offset={offset_arch}")
				offset = offset_arch
				break  # You can refine this to pick the right arch

		# Parse Mach-O header
		ncmds = struct.unpack_from("<I", data, offset + 16)[0]
		cmd_offset = offset + 32  # Start of load commands

		for i in range(ncmds):
			cmd, cmdsize = struct.unpack_from("<II", data, cmd_offset)
			if cmd == 0x1d:  # LC_CODE_SIGNATURE
				dataoff, datasize = struct.unpack_from("<II", data, cmd_offset + 8)
				print(f"Found LC_CODE_SIGNATURE at offset {dataoff}, size {datasize}")
				break
			cmd_offset += cmdsize
		else:
			print("LC_CODE_SIGNATURE not found.")
			return

		# Extract and parse signature blob
		blob = data[dataoff:dataoff + datasize]
		magic, length, count = struct.unpack_from(">III", blob, 0)
		print(f"SuperBlob: magic=0x{magic:x}, length={length}, count={count}")

		for i in range(count):
			index_offset = 12 + i * 8
			blob_type, blob_offset = struct.unpack_from(">II", blob, index_offset)
			print(f"Blob {i}: type=0x{blob_type:x}, offset={blob_offset}")

			if blob_type == 0xfade0c02:  # CSSLOT_CODEDIRECTORY
				cd_blob = blob[blob_offset:]
				version, flags, hash_offset = struct.unpack_from(">III", cd_blob, 0)
				print(f"CodeDirectory: version={version}, flags=0x{flags:x}, hash_offset={hash_offset}")
				# Add hash validation here if needed
