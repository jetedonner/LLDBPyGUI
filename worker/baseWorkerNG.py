import lldb
import os
import time
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from config import *
from dbg.debuggerdriverNG import EventListenerController
from dbg.listener import LLDBListener
from ui.helper.dbgOutputHelper import logDbgC
from worker.loadDisassemblyWorker import LoadDisassemblyWorker

try:
	import queue
except ImportError:
	import Queue as queue

import dbg.debuggerdriver
from dbg.fileInfos import *
from dbg.memoryHelper import *
from ui.customQt.QControlFlowWidget import *

class Worker(QObject):

	finished = pyqtSignal()
	show_dialog = pyqtSignal()
	logDbg = pyqtSignal(str)
	# logDbgC = pyqtSignal(str)
	logDbgC = pyqtSignal(str, object)

	# = pyqtSignal(str)

	# updateProgress = pyqtSignal(int)

	# Load Callbacks
	loadFileInfosCallback = pyqtSignal(object, object)
	loadJSONCallback = pyqtSignal(str)
	loadModulesCallback = pyqtSignal(object, object)
	enableBPCallback = pyqtSignal(str, bool, bool)
	loadInstructionCallback = pyqtSignal(object)
	loadStringCallback = pyqtSignal(str, int, str)
	loadSymbolCallback = pyqtSignal(str)
	finishedLoadInstructionsCallback = pyqtSignal(object, str, object)
	loadRegisterCallback = pyqtSignal(str)
	loadRegisterValueCallback = pyqtSignal(int, str, str, str)
	loadVariableValueCallback = pyqtSignal(str, str, str, str, str)
	# loadBreakpointsValueCallback = pyqtSignal(str, str, str, str, str)
	loadBreakpointsValueCallback = pyqtSignal(object, bool)
	updateBreakpointsValueCallback = pyqtSignal(object)
	loadWatchpointsValueCallback = pyqtSignal(object)
	updateWatchpointsValueCallback = pyqtSignal(object)
	finishedLoadingSourceCodeCallback = pyqtSignal(str)
	loadStacktraceCallback = pyqtSignal()
	progressUpdateCallback = pyqtSignal(int, str)

	startLoadControlFlowSignal = pyqtSignal()
	runControlFlow_loadConnections = pyqtSignal()
	endLoadControlFlowCallback = pyqtSignal(bool)

	eventListener = None

	# Load Listener
	handle_breakpointEvent = None
	handle_processEvent = None
	handle_gotNewEvent = None

	# Main Vars
	mainWin = None
	fileToLoad = ""
	arch = ""
	args = ""
	# targetBasename = ""
	startAddr = 0x0
	endAddr = 0x0


	def __init__(self, mainWinToUse, filename="", initTable=True, sourceFile="", arch="", args=""):
		super().__init__()

		# self.threadpool = QThreadPool(self)
		self.initTable = initTable
		self._should_stop = False
		self.mainWin = mainWinToUse
		self.fileToLoad = filename
		self.loader = ""
		self.arch = arch
		self.args = args
		self.loadSourceCode = True
		self.driver = None
		self.target = None
		self.process = None
		self.thread = None
		self.frame = None
		self.listener = None
		self.eventListener = None
		self.stoppedAtOEP = False
		self.isLoadSourceCodeActive = False
		self.sourceFile = sourceFile
		self.lineNum = 0
		self.startAddr = 0x0
		self.endAddr = 0x0
		self.allInstructions = []
		self.finishedLoadControlFlow = False
		self.endLoadControlFlowCallback.connect(self.handle_endLoadControlFlowCallback)

		# self.eventListener = EventListenerController(self.parent, self.mainWin.driver.debugger)
		# self.eventListener.worker.progress.connect(self.reportProgress)
		# self.eventListener.startEventListener()

	def run(self):
		self._should_stop = False  # Reset before starting
		# import lldb

		# # Create debugger instance
		# debugger = self.mainWin.driver.debugger
		# # debugger = lldb.SBDebugger.Create()
		# debugger.SetAsync(False)
		#
		# # Create a target from the Swift executable inside the .app bundle
		# target = debugger.CreateTarget("./_testtarget/xcode_projects/SwiftREPLTestApp/Debug/SwiftREPLTestApp.app/Contents/MacOS/SwiftREPLTestApp")
		#
		# if target:
		# 	# Launch the process
		# 	launch_info = lldb.SBLaunchInfo(None)
		# 	breakpoint = target.BreakpointCreateByName("main")
		# 	print(f"breakpoint: {breakpoint}")
		# 	process = target.Launch(launch_info, lldb.SBError())
		#
		# 	if process.IsValid():
		# 		print("Process launched with PID:", process.GetProcessID())
		# 	else:
		# 		print("Failed to launch process.")
		# else:
		# 	print("Failed to create target.")
		#
		# return
		self.show_dialog.emit()

		arch = get_arch_from_macholib(self.fileToLoad)[0]
		self.logDbg.emit(f"MACH-O Header: {arch} => {MachoCPUType.to_str(MachoCPUType.create_cputype_value(arch))}")
		# if (arch & MachoCPUType.CPU_TYPE_ARM64.value) == MachoCPUType.CPU_TYPE_ARM64.value:
		if arch & MachoCPUType.CPU_TYPE_ARM64.value:
			self.logDbg.emit(f"MACH-O Header: {MachoCPUType.to_str(MachoCPUType.create_cputype_value(arch))} is ARM64 .... YESSSSS!!!!!!")

		self.logDbg.emit(f"loadNewExecutableFile({self.fileToLoad})...")
		# self.targetBasename = os.path.basename(self.fileToLoad)
		self.loadNewExecutableFile(self.fileToLoad)
		self.logDbgC.emit(f"self.mainWin.driver.debugger.GetNumTargets() (baseWorkerNG): {self.mainWin.driver.debugger.GetNumTargets()}", DebugLevel.Verbose)
		if self.mainWin.driver.debugger.GetNumTargets() > 0:
			# for i in range(self.mainWin.driver.debugger.GetNumTargets()):
			# 	self.logDbgC.emit(f"self.mainWin.driver.debugger.GetTargetAtIndex({i}) (baseWorkerNG): {self.mainWin.driver.debugger.GetTargetAtIndex(i)}", DebugLevel.Verbose)

			self.target = self.mainWin.driver.getTarget()
			self.logDbgC.emit(f"self.target (baseWorkerNG): {self.target}", DebugLevel.Verbose)
			if self.target:
				self.logDbgC.emit(f"self.target.GetExecutable().GetFilename(): {self.target.GetExecutable().GetFilename()}", DebugLevel.Verbose)
				exe = self.target.GetExecutable().GetDirectory() + "/" + self.target.GetExecutable().GetFilename()
				# self.targetBasename = os.path.basename(exe)
				mach_header = GetFileHeader(exe)
				self.logDbgC.emit(f"mach_header = GetFileHeader(exe): {mach_header}", DebugLevel.Verbose)
				self.loadFileInfosCallback.emit(mach_header, self.target)
				self.logDbgC.emit(f"after self.loadFileInfosCallback.emit(...)", DebugLevel.Verbose)
				QApplication.processEvents()
				# self.mainWin.devHelper.setupDevHelper()
				self.loadFileStats()

		# if self.listener is not None:
		# 	self.listener.gotEvent.disconnect(self.handle_gotNewEvent)
		self.finished.emit()

	def stop(self):
		self._should_stop = True
		if self.listener is not None:
			# print(f"self.worker.listener.should_quit = True (5)")
			# self.listener.should_quit = True
			pass

	def handle_endLoadControlFlowCallback(self, success):
		# self.logDbg.emit(f"Result load control flow: {success}")
		self.finishedLoadControlFlow = True

	def runLoadControlFlow(self):
		# self.logDbgC.emit(f"runLoadControlFlow ... ", DebugLevel.Info)
		while not self.finishedLoadControlFlow:
			# self.logDbg.emit(f"... ")
			time.sleep(0.5)
		# self.logDbgC.emit(f"Finished loading control flow ... continuing ...", DebugLevel.Verbose)

		# if self.setHelper.getChecked(SettingsValues.BreakpointAtMainFunc):
		# 	self.bpHelper.enableBP(hex(addrObj2), True, False)
		# self.txtMultiline.viewAddress(hex(addrObj2))
		# self.setProgressValue(95)
		# QApplication.processEvents()
		# self.window().wdtControlFlow.view.verticalScrollBar().setValue(self.window().txtMultiline.table.verticalScrollBar().value())
		pass

	def runLoadSourceCode(self, filename="", loadFlowControl=True):
		# self.sourceFile = filename
		if self.isLoadSourceCodeActive:
			# self.interruptLoadSourceCode = True
			return
		# else:
		# 	self.interruptLoadSourceCode = False
		self.isLoadSourceCodeActive = True

		self.sourceFile = sourcefileToUse = filename if filename != "" else self.sourceFile
		# print(f"RUN LOAD SOURCECODE: {self.sourceFile} ...")
		context = self.frame.GetSymbolContext(lldb.eSymbolContextEverything)
		self.lineNum = context.GetLineEntry().GetLine()
		# Create the filespec for 'main.c'.
		filespec = lldb.SBFileSpec(sourcefileToUse, False)
		source_mgr = self.driver.debugger.GetSourceManager()
		# Use a string stream as the destination.
		linesOfFileContent = self.linesOfFileContent(sourcefileToUse)
		linesOfCode = len(linesOfFileContent)
		# self.logDbgC.emit(f"linesOfCode: {linesOfCode} / {linesOfCode - self.lineNum}", DebugLevel.Verbose)
		stream = None
		if linesOfCode > 0:
			stream = lldb.SBStream()
			source_mgr.DisplaySourceLinesWithLineNumbers(filespec, self.lineNum, self.lineNum, linesOfCode - self.lineNum, '=>', stream)

		self.isLoadSourceCodeActive = False
		self.finishedLoadControlFlow = False
		if linesOfCode > 0:
			if stream != None:
				fileContent = stream.GetData()
				self.finishedLoadingSourceCodeCallback.emit(fileContent)
				QApplication.processEvents()

		# self.logDbgC.emit(f"BEFORE self.runLoadControlFlow() => runLoadSourceCode()", DebugLevel.Info)
		if loadFlowControl:
			self.runControlFlow_loadConnections.emit()
			QApplication.processEvents()
		# QCoreApplication.processEvents()
		# QApplication.processEvents()
			self.runLoadControlFlow()

	@PendingDeprecationWarning
	def count_lines_of_code(self, file_path):
		lines = []
		if os.path.exists(file_path):
			with open(file_path, 'r') as file:
				lines = file.readlines()
		else:
			self.logDbgC.emit(f"The source code file: {file_path} could not be found!", DebugLevel.Verbose)

		# code_lines = [
		# 	line for line in lines
		# 	if line.strip() # and not line.strip().startswith('//') and not line.strip().startswith('/*')
		# ]
		return len(lines)

	def linesOfFileContent(self, file_path):
		lines = []
		if os.path.exists(file_path):
			with open(file_path, 'r') as file:
				lines = file.readlines()
		else:
			self,logDbgC.emit(f"The file: {file_path} could not be found!", DebugLevel.Verbose)

		# code_lines = [
		# 	line for line in lines
		# 	if line.strip() # and not line.strip().startswith('//') and not line.strip().startswith('/*')
		# ]
		return lines

	def loadBPsWPs(self):
		# super(LoadBreakpointsWorker, self).workerFunc()
		self.progressUpdateCallback.emit(50, "Test progress Update ...")
		# self.sendStatusBarUpdate("Reloading breakpoints ...")
		# target = self.driver.getTarget()
		idx = 0
		for i in range(self.target.GetNumBreakpoints()):
			idx += 1
			bp_cur = self.target.GetBreakpointAtIndex(i)
			# Make sure the name list has the remaining name:
			name_list = lldb.SBStringList()
			bp_cur.GetNames(name_list)
			num_names = name_list.GetSize()
			name = name_list.GetStringAtIndex(0)

			if self.initTable:
				self.loadBreakpointsValueCallback.emit(bp_cur, self.initTable)
			else:
				self.updateBreakpointsValueCallback.emit(bp_cur)
			QApplication.processEvents()

		for wp_loc in self.target.watchpoint_iter():
			if self.initTable:
				self.loadWatchpointsValueCallback.emit(wp_loc)  # , self.initTable)
			else:
				self.updateWatchpointsValueCallback.emit(wp_loc)
		QApplication.processEvents()

	def loadRegisters(self):
		# super(LoadRegisterWorker, self).workerFunc()

		# self.sendStatusBarUpdate("Reloading registers ...")
		# target = self.driver.getTarget()
		# process = target.GetProcess()
		if self.process:
			# thread = process.GetThreadAtIndex(0)
			if self.thread:
				self.frame = self.driver.getFrame()
				#				frame = thread.GetFrameAtIndex(0)
				if self.frame:
					registerList = self.thread.GetFrameAtIndex(0).GetRegisters()
					numRegisters = registerList.GetSize()
					numRegSeg = 100 / numRegisters
					currReg = 0
					for value in registerList:
						currReg += 1
						currRegSeg = 100 / numRegisters * currReg
						# self.sendProgressUpdate(100 / numRegisters * currReg,
						# 						f'Loading registers for {value.GetName()} ...')
						if self.initTable:
							self.loadRegisterCallback.emit(value.GetName())
							QApplication.processEvents()

						numChilds = len(value)
						idx = 0
						for child in value:
							idx += 1
							# self.sendProgressUpdate((100 / numRegisters * currReg) + (numRegSeg / numChilds * idx),
							# 						f'Loading registers value {child.GetName()} ...')
							if self.initTable:
								# print(f"self.loadRegisterValueCallback.emit({currReg - 1}, {child.GetName()}, {child.GetValue()}, ...)")
								self.loadRegisterValueCallback.emit(currReg - 1, child.GetName(), child.GetValue(),
																	getMemoryValueAtAddress(target, process,
																							child.GetValue()))
								QApplication.processEvents()
								# self.loadRegisterValue.emit(currReg - 1, child.GetName(), child.GetValue(),
								# 									getMemoryValueAtAddress(target, process,
								# 															child.GetValue()))
							# else:
							# 	self.signals.updateRegisterValue.emit(currReg - 1, child.GetName(),
							# 										  child.GetValue(),
							# 										  getMemoryValueAtAddress(target, process,
							# 																  child.GetValue()))
						# continue
					# QCoreApplication.processEvents()

					# Load VARIABLES
					idx = 0
					vars = self.frame.GetVariables(True, True, True, False)  # type of SBValueList
					#					print(f"GETTING VARIABLES: vars => {vars}")
					for var in vars:
						#						hexVal = ""
						#						print(dir(var))
						#						print(var)
						#						print(hex(var.GetLoadAddress()))
						#						if not var.IsValid():
						#							print(f'{var.GetName()} var.IsValid() ==> FALSE!!!!')

						data = ""
						#						if var.GetValue() == None:
						#							print(f'{var.GetName()} var.GetValue() ==> NONE!!!!')
						#							string_value = "<Not initialized>"
						#						else:
						string_value = var.GetValue()
						if var.GetTypeName() == "int":
							if (var.GetValue() == None):
								continue
							string_value = str(string_value)
							# print(dir(var))
							# print(var)
							# print(var.GetValue())
							data = hex(int(var.GetValue()))
						#							hexVal = " (" + hex(int(var.GetValue())) + ")"
						if var.GetTypeName().startswith("char"):
							string_value = self.char_array_to_string(var)
							data = var.GetPointeeData(0, var.GetByteSize())

						if self.initTable:
							#							if idx == 2:
							#								error = lldb.SBError()
							#								wp = var.Watch(False, True, False, error)
							#								print(f'wp({idx}) => {wp}')

							self.loadVariableValueCallback.emit(str(var.GetName()), str(string_value), str(data),
																str(var.GetTypeName()), hex(var.GetLoadAddress()))
							QApplication.processEvents()
						# else:
						# 	self.signals.updateVariableValue.emit(str(var.GetName()), str(string_value), str(data),
						# 										  str(var.GetTypeName()), hex(var.GetLoadAddress()))
						idx += 1

					# QCoreApplication.processEvents()
		self.loadBPsWPs()
		if self.loadSourceCode:
			if self.sourceFile != "":
				self.runLoadSourceCode(self.sourceFile)
			else:
				sourceFilesFound = find_source_file(self.fileToLoad) # self.sourceFile if self.sourceFile != "" else
				if len(sourceFilesFound) > 0:
					self.logDbgC.emit(f"Tried to auto-find sourcefile => Found: {len(sourceFilesFound)}: {sourceFilesFound[0]}! Loading file ...", DebugLevel.Verbose)
					self.runLoadSourceCode(sourceFilesFound[0])
				else:
					self.logDbgC.emit(f"Tried to auto-find sourcefile => NOTHING Found!!!", DebugLevel.Verbose)
		else:
			self.runControlFlow_loadConnections.emit()
			# QCoreApplication.processEvents()
			# QApplication.processEvents()
			self.logDbgC.emit(f"BEFORE self.runLoadControlFlow() => runLoadSourceCode()", DebugLevel.Info)
			self.runLoadControlFlow()
		# self.logDbgC.emit(f"BEFORE self.runLoadControlFlow() => loadRegisters()", DebugLevel.Info)
		# self.runLoadControlFlow()

		self.loadStacktraceCallback.emit()
		QApplication.processEvents()

	def char_array_to_string(self, char_array_value):
		byte_array = char_array_value.GetPointeeData(0, char_array_value.GetByteSize())
		error = lldb.SBError()
		sRet = byte_array.GetString(error, 0)
		return "" if sRet == 0 else sRet

	def loadStacktrace(self):
		self.process = self.driver.getTarget().GetProcess()
		self.thread = self.process.GetThreadAtIndex(0)
		#		from lldbutil import print_stacktrace
		#		st = get_stacktrace(self.thread)
		##			print(f'{st}')
		#		self.txtOutput.setText(st)

		idx = 0
		if self.thread:
			#			self.treThreads.doubleClicked.connect()
			self.treThreads.clear()
			self.processNode = QTreeWidgetItem(self.treThreads, ["#0 " + str(self.process.GetProcessID()),
																 hex(self.process.GetProcessID()) + "",
																 self.process.GetTarget().GetExecutable().GetFilename(),
																 '', ''])

			self.threadNode = QTreeWidgetItem(self.processNode,
											  ["#" + str(idx) + " " + str(self.thread.GetThreadID()),
											   hex(self.thread.GetThreadID()) + "", self.thread.GetQueueName(), '',
											   ''])

			numFrames = self.thread.GetNumFrames()

			for idx2 in range(numFrames):
				self.setProgressValue(idx2 / numFrames)
				frame = self.thread.GetFrameAtIndex(idx2)
				# logDbgC(f"frame.GetFunction(): {frame.GetFunction()}")
				frameNode = QTreeWidgetItem(self.threadNode,
											["#" + str(frame.GetFrameID()), "", str(frame.GetPCAddress()),
											 str(hex(frame.GetPC())), self.GuessLanguage(frame)])
				idx += 1

			self.processNode.setExpanded(True)
			self.threadNode.setExpanded(True)

#			self.devHelper.setDevWatchpoints()

	# import lldb

	def dump_cstring_section(self, target):
		for module in target.module_iter():
			for section in module.section_iter():
				if section.GetName() == "__TEXT" and section.GetSubSectionName() == "__cstring":
					addr = section.GetStartAddress()
					size = section.GetByteSize()
					error = lldb.SBError()
					data = target.GetProcess().ReadMemory(addr, size, error)

					if error.Success():
						strings = data.split(b'\x00')
						for i, s in enumerate(strings):
							try:
								decoded = s.decode('utf-8')
								print(f"[{i}] {decoded}")
							except UnicodeDecodeError:
								continue
					else:
						print("Failed to read memory:", error.GetCString())

	def list_external_symbols(self, target):
		main_exe = target.GetExecutable().GetFilename()

		for module in target.module_iter():
			module_name = module.file.GetFilename()
			if module_name != main_exe:  # Skip main executable
				print(f"\n📦 External Module: {module_name}")
				for i in range(module.GetNumSymbols()):
					symbol = module.GetSymbolAtIndex(i)
					if symbol.IsValid():
						print(f"🔧 Symbol: {symbol.GetName()}")


	def disassemble_entire_target(self):
		# self.list_external_symbols(self.target)
		self.logDbgC.emit(f"============ NEW DISASSEMBLER ===============", DebugLevel.Verbose)
		idx = 0
		for module in self.target.module_iter():
			# self.logDbgC.emit(f"\n📦 Module: {module.file}", DebugLevel.Verbose)
			if module.file.GetFilename() == self.target.executable.GetFilename(): # "a_hello_world_test":
				isObjectiveCFile = is_objc_app(self.target)
				# self.logDbgC.emit(f"App: {module.file.GetFilename()} is objective-c: {isObjectiveCFile}...", DebugLevel.Verbose)
				lang = detect_language_by_symbols(self.target, module)
				# self.logDbgC.emit(f"App: {module.file.GetFilename()} is language: {lang}...", DebugLevel.Verbose)

				isObjC = detect_objc(module)
				# self.logDbgC.emit(f"App: {module.file.GetFilename()} is objective-c: {isObjC}...", DebugLevel.Verbose)
			# if idx == 0:
			# 	for symbol in module:
			# 		name = symbol.GetName()
			# 		saddr = symbol.GetStartAddress()
			# 		eaddr = symbol.GetEndAddress()
			# 		self.logDbgC.emit(f"symbol.name: {name}, start: {saddr}, end: {eaddr}", DebugLevel.Verbose)

				for section in module.section_iter():
					# Check if the section is readable
					# if not section.IsReadable():
					# 	continue
					# self.logDbgC.emit(f"section.GetName(): {section.GetName()}", DebugLevel.Verbose)
					if section.GetName() == "__TEXT":  # or  section.GetName() == "__PAGEZERO":
						# if idx != 1:
						# 	idx += 1
						# 	continue
						idxInstructions = 0
						for subsec in section:
							# self.logDbgC.emit(f"subsec.GetName(): {subsec.GetName()}", DebugLevel.Verbose)
							if subsec.GetName() == "__text" or subsec.GetName() == "__stubs":
								idxSym = 0
								lstSym = module.symbol_in_section_iter(subsec)
								if isObjC and subsec.GetName() == "__stubs":
									self.loadSymbolCallback.emit(subsec.GetName())

								for smbl in lstSym:
									# self.logDbgC.emit(f"===========>>>>>>>>>>> symbl: {smbl}", DebugLevel.Verbose)
									# .GetStartAddress().GetFunction()
									if isObjC and not subsec.GetName() == "__stubs":
										self.loadSymbolCallback.emit(smbl.GetName())
									instructions = smbl.GetStartAddress().GetFunction().GetInstructions(self.target)
									self.allInstructions += instructions
									for instruction in instructions:
										# self.logDbgC.emit(f"----------->>>>>>>>>>> INSTRUCTION: {instruction.GetMnemonic(self.target)} ... ", DebugLevel.Verbose)
										self.loadInstructionCallback.emit(instruction)
										QApplication.processEvents()
										idxInstructions += 1
										# self.checkLoadConnection(instruction, idxInstructions + (idxSym + 1))
									idxSym += 1

								if subsec.GetName() == "__stubs":
									start_addr = subsec.GetLoadAddress(self.target)
									size = subsec.GetByteSize()
									# self.logDbgC.emit(f"size of __stubs: {hex(size)} / {hex(start_addr)}", DebugLevel.Verbose)
									# Disassemble instructions
									end_addr = start_addr + size
									# func_start = subsec.GetStartAddress()
									# func_end = subsec.GetEndAddress()
									# logDbgC(f"__stubs: start_addr: {start_addr} / end_addr: {end_addr}")
									estimated_count = size // 4
									instructions = self.target.ReadInstructions(lldb.SBAddress(start_addr, self.target),
																	int(estimated_count))
									# instructions = subsec.addr.GetFunction().GetInstructions(self.target)
									# insts = target.ReadInstructions(lldb.SBAddress(start_addr, target), lldb.SBAddress(end_addr, target))
									self.allInstructions += instructions
									for instruction in instructions:
										# result.PutCString(str(inst))
										# self.logDbgC.emit(str(instruction), DebugLevel.Verbose)
										self.loadInstructionCallback.emit(instruction)
										QApplication.processEvents()
										idxInstructions += 1
										# self.checkLoadConnection(instruction, idxInstructions + (idxSym + 1))
									continue
							elif subsec.GetName() == "__cstring":
								# if isObjC:
								self.loadSymbolCallback.emit(subsec.GetName())
								QApplication.processEvents()
								addr = subsec.GetLoadAddress(self.target) #.GetStartAddress()
								size = subsec.GetByteSize()
								error = lldb.SBError()
								data = self.target.GetProcess().ReadMemory(addr, size, error)

								if error.Success():
									strings = data.split(b'\x00')
									curAddr = addr
									for i, s in enumerate(strings):
										try:
											decoded = s.decode('utf-8')
											# self.logDbgC.emit(f"{hex(curAddr)}: [{i}] {decoded}", DebugLevel.Verbose)
											self.loadStringCallback.emit(hex(curAddr), i, decoded)
											QApplication.processEvents()
											curAddr += len(decoded) + 1
										except UnicodeDecodeError:
											continue
								else:
									self.logDbgC.emit(f"Failed to read memory: {error.GetCString()}", DebugLevel.Verbose)
								pass
						break
				break
			# else:
			# 	break
			idx += 1
		self.logDbgC.emit(f"============ END DISASSEMBLER ===============", DebugLevel.Verbose)

		# for inst in self.allInstructions:
		self.checkLoadConnection(self.allInstructions)

		for con in self.connections:
			self.logDbgC.emit(f"===>>> Connection: {hex(con.origAddr)} / {hex(con.destAddr)} => {con.origRow} / {con.destRow}", DebugLevel.Verbose)
			# pass
		self.progressUpdateCallback.emit(35, f"Read disassembly and created control flow connections ...")
		QApplication.processEvents()
		self.connections.sort(key=lambda x: abs(x.jumpDist), reverse=True)
		self.finishedLoadInstructionsCallback.emit(self.connections, self.target.GetExecutable().GetFilename())
		QApplication.processEvents()
		self.loadRegisters()

	radius = 15
	connections = []

	def get_line_number(self, address_int):
		# target = debugger.GetSelectedTarget()
		addr = lldb.SBAddress(address_int, self.driver.getTarget())
		                            
		# Resolve symbol context with line entry info
		context = self.driver.getTarget().ResolveSymbolContextForAddress(
	        addr,
	        lldb.eSymbolContextEverything
		)

		line_entry = context.GetLineEntry()
		if line_entry.IsValid():
			file_spec = line_entry.GetFileSpec()
			line = line_entry.GetLine()
			# print(f"📍 Address 0x{address_int:x} maps to {file_spec.GetFilename()}:{line}")
			return line # file_spec.GetFilename(), 
		else:
			print("❌ No line info found for this address.")
		return None

	def isInsideTextSectionGetRangeVarsReady(self):
		self.thread = self.process.GetThreadAtIndex(0)
		module = self.thread.GetFrameAtIndex(0).GetModule()
		found = False
		for sec in module.section_iter():
			for idx3 in range(sec.GetNumSubSections()):
				subSec = sec.GetSubSectionAtIndex(idx3)
				if subSec.GetName() == "__text":
					self.startAddr = subSec.GetFileAddress()
				elif subSec.GetName() == "__stubs":
					self.endAddr = subSec.GetFileAddress() + subSec.GetByteSize()
					# self.logDbgC.emit(f"self.endAddr: {hex(self.endAddr)} / {self.endAddr}", DebugLevel.Verbose)
					found = True
					break
			if found:
				break
				# elif subSec.GetName() == "__stubs":
				# 	logDbgC(f"GOT __stubs: {subSec.GetName()} => subSec.GetFileAddress(): {subSec.GetFileAddress()}, subSec.GetByteSize(): {subSec.GetByteSize()}, self.endAddr: {self.endAddr}")
				# 	self.endAddr = subSec.GetFileAddress() + subSec.GetByteSize()

	def isInsideTextSection(self, addr):
		try:
			return self.endAddr > int(addr, 16) >= self.startAddr
		except Exception as e:
			self.logDbgC.emit(f"Exception: {e}", DebugLevel.Error)
			return False

	
	def checkLoadConnection(self, instructions):
		for instruction in self.allInstructions:
			sMnemonic = instruction.GetMnemonic(self.target)
			# logDbgC(f"checkLoadConnection()..... {instruction}")
			# if sMnemonic is None or sMnemonic == "":
			# 	return

			if sMnemonic is not None and sMnemonic.startswith(JMP_MNEMONICS) and not sMnemonic.startswith(JMP_MNEMONICS_EXCLUDE):
				sAddrJumpTo = instruction.GetOperands(self.target)
				# self.logDbgC.emit(f"checkLoadConnection()..... {instruction} ===>>> JumpTo: {sAddrJumpTo}", DebugLevel.Verbose)

				if sAddrJumpTo is None or not is_hex_string(sAddrJumpTo):
					# self.logDbgC.emit(f"checkLoadConnection() RETURN OF ERROR ..... sAddrJumpTo: {sAddrJumpTo}", DebugLevel.Verbose)
					continue

				# self.logDbgC.emit(f"checkLoadConnection()..... sAddrJumpTo: {sAddrJumpTo} / end: {hex(self.endAddr)} / start: {hex(self.startAddr)}", DebugLevel.Verbose)

				bOver = self.startAddr < int(sAddrJumpTo, 16) < self.endAddr
				# if bOver:
				# 	self.logDbgC.emit(
				# 		f"checkLoadConnection()..... sAddrJumpTo IS INSIDE ALTERNATIVE: {sAddrJumpTo} / end: {hex(self.endAddr)} / start: {hex(self.startAddr)}", DebugLevel.Verbose)
				# 	# pass

				if self.isInsideTextSection(sAddrJumpTo) or bOver:
					if self.isInsideTextSection(sAddrJumpTo):
						# self.logDbgC.emit(f"IS NOT OVER CONNECTION!!!!", DebugLevel.Verbose)
						sAddrStartInt = int(str(instruction.GetAddress().GetLoadAddress(self.target)), 10)
						sAddrJumpFrom = hex(sAddrStartInt)
						rowStart = int(self.get_line_number(sAddrStartInt))# idxInstructions#int(self.get_line_number(int(sAddrJumpFrom, 16)))
						# lineEnd = self.get_line_number(int(sAddrJumpTo, 16))
						lineEnd = None
						idx = 0
						for inst in self.allInstructions:
							if inst.GetAddress().GetLoadAddress(self.target) == instruction.GetAddress().GetLoadAddress(self.target):
								lineEnd = idx
								break
							idx += 1
						if lineEnd is None:
							# self.logDbgC.emit(f"IS NOT OVER CONNECTION!!!! ==>> RETURN", DebugLevel.Verbose)
							continue
							# pass
						rowEnd = int(lineEnd)
						self.logDbgC.emit(f"Found connection from line: {rowStart} to: {rowEnd} ({sAddrJumpFrom} / {sAddrJumpTo})", DebugLevel.Verbose)
					elif bOver:
						# self.logDbgC.emit(f"IS OVER CONNECTION!!!!", DebugLevel.Verbose)
						sAddrStartInt = int(str(instruction.GetAddress().GetLoadAddress(self.target)), 10)# int(str(instruction.GetAddress().GetLoadAddress(self.target)), 10)
						sAddrJumpFrom = hex(sAddrStartInt)
						rowStart = int(self.get_line_number(
							sAddrStartInt))  # idxInstructions#int(self.get_line_number(int(sAddrJumpFrom, 16)))
						# lineEnd = self.get_line_number(int(sAddrJumpTo, 16))
						lineEnd = self.mainWin.txtMultiline.table.getLineNum(sAddrJumpTo)
						if lineEnd is None:
							# self.logDbgC.emit(f"IS OVER CONNECTION!!!! ==>> RETURN", DebugLevel.Verbose)
							continue
							# pass
						rowEnd = int(lineEnd)
						self.logDbgC.emit(f"Found connection from line: {rowStart} to: {rowEnd} ({sAddrJumpFrom} / {sAddrJumpTo})", DebugLevel.Verbose)

					if (rowStart < rowEnd):
						newConObj = QControlFlowWidget.draw_flowConnectionNG(rowStart, rowEnd, int(sAddrJumpFrom, 16), int(sAddrJumpTo, 16), None, random_qcolor(), self.radius, 1, False) # self.window().txtMultiline.table
					else:
						newConObj = QControlFlowWidget.draw_flowConnectionNG(rowStart, rowEnd, int(sAddrJumpFrom, 16), int(sAddrJumpTo, 16), None, random_qcolor(), self.radius, 1, True)

					newConObj.mnemonic = sMnemonic
					# self.logDbgC.emit(f"Connection (Branch) is a: {newConObj.mnemonic} / {sMnemonic})", DebugLevel.Verbose)
					if abs(newConObj.jumpDist / 2) <= (newConObj.radius / 2):
						newConObj.radius = newConObj.jumpDist / 2
					self.connections.append(newConObj)
					if self.radius <= 130:
						self.radius += 15
				else:
					self.logDbgC.emit(f"checkLoadConnection()..... sAddrJumpTo NOT IN TARGET", DebugLevel.Verbose)
					# self.connections.sort(key=lambda x: abs(x.jumpDist), reverse=True)

	def disassembleTarget(self):
		self.logDbg.emit(f"HELLO WORLD DISASSEBLE ;-=")

	def reportProgress(self, prg):
		self.logDbg.emit(f"------------ reportProgress({prg}) ------------")
		pass

	def loadTarget(self):
		# self.logDbgC.emit(f"HERE WE ARE !!!!!!", DebugLevel.Verbose)

		# self.logDbgC.emit(f"loadTarget() => Target: {self.target} ...", DebugLevel.Verbose)
		if self.target:
			self.process = self.target.GetProcess()
			# self.logDbgC.emit(f"loadTarget() => Process: {self.process} ...", DebugLevel.Verbose)

			if self.process:
				self.listener = LLDBListener(self.process, self.driver.debugger)
				self.listener.setHelper = self.mainWin.setHelper
				self.listener.breakpointEvent.connect(self.handle_breakpointEvent)
				self.listener.processEvent.connect(self.handle_processEvent)
				self.listener.gotEvent.connect(self.handle_gotNewEvent)
				self.listener.addListenerCalls()
				self.listener.start()

				# self.eventListener = EventListenerController(self.parent, self.driver.debugger)
				# self.eventListener.worker.progress.connect(self.reportProgress)
				# self.eventListener.worker.gotSTDOUT.connect(self.mainWin.testSTDOUT)
				# self.eventListener.startEventListener()

				self.thread = self.process.GetThreadAtIndex(0)
				# self.logDbgC.emit(f"loadTarget() => Thread: {self.thread} ...", DebugLevel.Verbose)

				if self.thread:
					self.isInsideTextSectionGetRangeVarsReady()
					# self.logDbgC.emit(f"loadTarget() => Thread.GetNumFrames(): {self.thread.GetNumFrames()} ...", DebugLevel.Verbose)
					for z in range(self.thread.GetNumFrames()):
						frame = self.thread.GetFrameAtIndex(z)

						# self.logDbgC.emit(f"frame.register: {frame.GetRegisters()}", DebugLevel.Verbose)

						self.loadModulesCallback.emit(frame, self.target.modules)
						QApplication.processEvents()
						# self.tabWidgetStruct.cmbModules.addItem(
						# 	frame.GetModule().GetFileSpec().GetFilename() + " (" + str(
						# 		frame.GetFrameID()) + ")")
						# self.logDbgC.emit(f"loadTarget() => Frame: {frame} ...", DebugLevel.Verbose)
						if frame.GetModule().GetFileSpec().GetFilename() != self.target.GetExecutable().GetFilename():
							# self.logDbgC.emit(f"Module for FileStruct IS NOT equal executable => continuing ...", DebugLevel.Verbose)
							continue
						# else:
						# 	self.logDbgC.emit(f"Module for FileStruct IS equal executable => scanning ...", DebugLevel.Verbose)

						if frame:
							# self.logDbgC.emit(f"BEFORE DISASSEMBLE!!!!", DebugLevel.Verbose)
							# self.start_loadDisassemblyWorker(self.loadInstructionCallback, self.finishedLoadInstructionsCallback, True)
							# self.disassembleTarget()
							self.disassemble_entire_target()
							# self.start_loadDisassemblyWorker(True)
							# context = frame.GetSymbolContext(lldb.eSymbolContextEverything)

	def loadFileStats(self):
		self.logDbgC.emit(f"def loadFileStats(...)", DebugLevel.Verbose)
		statistics = self.driver.getTarget().GetStatistics()
		self.logDbgC.emit(f"def loadFileStats(...) => after statistics = self.driver.getTarget().GetStatistics()", DebugLevel.Verbose)
		stream = lldb.SBStream()
		success = statistics.GetAsJSON(stream)
		self.logDbgC.emit(f"def loadFileStats(...) => after success = statistics.GetAsJSON(stream)", DebugLevel.Verbose)
		if success:
			self.loadJSONCallback.emit(str(stream.GetData()))
			self.logDbgC.emit(f"def loadFileStats(...) => after self.loadJSONCallback.emit(str(stream.GetData()))", DebugLevel.Verbose)
			QApplication.processEvents()

	def on_scanf_hit(frame, bp_loc, dict):
		print("✅ Breakpoint hit at scanf!")
		return True  # Returning True tells LLDB to stop here	# return

	def loadNewExecutableFile(self, filename):

		global event_queue
		self.mainWin.event_queue = queue.Queue()
		self.mainWin.driver.should_quit = False
		self.mainWin.inited = False
		self.driver = dbg.debuggerdriver.createDriver(self.mainWin.driver.debugger, self.mainWin.event_queue)
		self.mainWin.driver = self.driver
		self.driver.debugger = self.mainWin.driver.debugger
		self.driver.debugger.SetAsync(False)
		self.driver.signals.event_queued.connect(self.mainWin.handle_event_queued)
		self.driver.start()
		self.logDbgC.emit(f"createTarget({filename})", DebugLevel.Info)

		if is_swift_binary(filename):
			self.target = self.driver.launch_with_breakpoint(self.driver.debugger, filename)  #.createTargetSWIFT(filename)
		else:
			self.target = self.driver.createTarget(filename, self.arch, self.args)

		self.logDbgC.emit(f"createTarget({filename}) finished ...", DebugLevel.Verbose)

		if self.target.IsValid():
			self.mainWin.target = self.target
			self.logDbgC.emit(f"target: {self.target}", DebugLevel.Verbose)

			if self.mainWin.setHelper.getValue(SettingsValues.BreakpointAtMainFunc):
				self.driver.debugger.HandleCommand('process launch --stop-at-entry')

				main_oep, symbol = find_main(self.driver.debugger)#, "___debug_blank_executor_main")
				if main_oep != 0 and self.mainWin.setHelper.getValue(SettingsValues.BreakpointAtMainFunc):
					# self.driver.debugger.HandleCommand(f'breakpoint set -a {hex(main_oep)} -N kimon')
					bp = self.driver.getTarget().BreakpointCreateByAddress(main_oep) # .BreakpointCreateByName("main")
					# for bl in bp:
					# 	self.logDbgC.emit(f"bl.location: {bl}", DebugLevel.Verbose)
					self.driver.mainID = bp.GetID()
					self.driver.debugger.HandleCommand(f'br name add -N main {bp.GetID()}')
					bp.SetScriptCallbackFunction("main_hit")
					self.logDbgC.emit(f'breakpoint set "main": {bp}', DebugLevel.Verbose)
					# self.driver.debugger.HandleCommand('breakpoint set --name main')

				# Set breakpoint on scanf
				if	self.mainWin.setHelper.getValue(SettingsValues.AutoBreakpointForScanf):
					bp = self.driver.getTarget().BreakpointCreateByName("scanf")
					# for bl in bp:
					# 	self.logDbgC.emit(f"bl.location: {bl}", DebugLevel.Verbose)

					self.driver.scanfID = bp.GetID()
					self.driver.debugger.HandleCommand(f'br name add -N scanf {bp.GetID()}')
					bp.SetScriptCallbackFunction("on_scanf_hit")
					self.logDbgC.emit(f'breakpoint set "scanf": {bp}', DebugLevel.Verbose)

				self.driver.debugger.HandleCommand('breakpoint set --name main')
				# self.driver.debugger.HandleCommand(f'br list')
				self.driver.debugger.HandleCommand('process continue')
			# self.driver.debugger.HandleCommand('process continue')
			self.loadTarget()
		else:
			self.logDbgC.emit(f"Error creating target!!!", DebugLevel.Verbose)