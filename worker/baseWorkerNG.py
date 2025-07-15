import lldb

import time
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from config import *
from dbg.listener import LLDBListener
from worker.loadDisassemblyWorker import LoadDisassemblyWorker

try:
	import queue
except ImportError:
	import Queue as queue

import dbg.debuggerdriver
from dbg.fileInfos import *
from dbg.memoryHelper import *

class Worker(QObject):

	finished = pyqtSignal()
	show_dialog = pyqtSignal()
	logDbg = pyqtSignal(str)
	logDbgC = pyqtSignal(str)

	# updateProgress = pyqtSignal(int)

	# Load Callbacks
	loadFileInfosCallback = pyqtSignal(object, object)
	loadJSONCallback = pyqtSignal(str)
	loadModulesCallback = pyqtSignal(object, object)
	enableBPCallback = pyqtSignal(str, bool, bool)
	loadInstructionCallback = pyqtSignal(object)
	finishedLoadInstructionsCallback = pyqtSignal()
	loadRegisterCallback = pyqtSignal(str)
	loadRegisterValueCallback = pyqtSignal(int, str, str, str)
	loadVariableValueCallback = pyqtSignal(str, str, str, str, str)
	# loadBreakpointsValueCallback = pyqtSignal(str, str, str, str, str)
	loadBreakpointsValueCallback = pyqtSignal(object, bool)
	updateBreakpointsValueCallback = pyqtSignal(object)
	loadWatchpointsValueCallback = pyqtSignal(object)
	updateWatchpointsValueCallback = pyqtSignal(object)
	finishedLoadingSourceCodeCallback = pyqtSignal(str)

	# Load Listener
	handle_breakpointEvent = None
	handle_processEvent = None
	handle_gotNewEvent = None

	# Main Vars
	mainWin = None
	fileToLoad = ""
	targetBasename = ""

	def __init__(self, mainWinToUse, filename, initTable=True, sourceFile=""):
		super().__init__()

		# self.threadpool = QThreadPool(self)
		self.initTable = initTable
		self._should_stop = False
		self.mainWin = mainWinToUse
		self.fileToLoad = filename
		self.driver = None
		self.target = None
		self.process = None
		self.thread = None
		self.frame = None
		self.listener = None
		self.stoppedAtOEP = False
		self.isLoadSourceCodeActive = False
		self.sourceFile = sourceFile
		self.lineNum = 0

	def run(self):
		self._should_stop = False  # Reset before starting
		self.show_dialog.emit()

		self.logDbg.emit(f"loadNewExecutableFile({self.fileToLoad})...")
		self.targetBasename = os.path.basename(self.fileToLoad)
		self.loadNewExecutableFile(self.fileToLoad)
		if self.mainWin.driver.debugger.GetNumTargets() > 0:
			self.target = self.mainWin.driver.getTarget()
			# print(f"loadTarget => {target}")
			if self.target:
				exe = self.target.GetExecutable().GetDirectory() + "/" + self.target.GetExecutable().GetFilename()
				# self.targetBasename = os.path.basename(exe)
				mach_header = GetFileHeader(exe)
				self.loadFileInfosCallback.emit(mach_header, self.target)
				self.mainWin.devHelper.setupDevHelper()
				self.loadFileStats()

				# for i in range(10):  # Simulate long task
				#     if self._should_stop:
				#         print("Worker interrupted.")
				#         break
				#     # Simulate work
				#     time.sleep(1)
				#     print(f"Working... {i}")
				#     self.logDbg.emit(f"Working... {i}")
		self.finished.emit()

	def stop(self):
		self._should_stop = True

	def runLoadSourceCode(self):
		if self.isLoadSourceCodeActive:
			interruptLoadSourceCode = True
			return
		else:
			interruptLoadSourceCode = False
		# QCoreApplication.processEvents()
		self.isLoadSourceCodeActive = True

		# frame = self.driver.getTarget().GetProcess().GetThreadAtIndex(0).GetFrameAtIndex(0)
		context = self.frame.GetSymbolContext(lldb.eSymbolContextEverything)
		self.lineNum = context.GetLineEntry().GetLine()
		# Create the filespec for 'main.c'.
		filespec = lldb.SBFileSpec(self.sourceFile, False)
		source_mgr = self.driver.debugger.GetSourceManager()
		# Use a string stream as the destination.
		linesOfCode = self.count_lines_of_code(self.sourceFile)
		print(f"linesOfCode: {linesOfCode} / {linesOfCode - self.lineNum}")
		stream = lldb.SBStream()
		source_mgr.DisplaySourceLinesWithLineNumbers(filespec, self.lineNum, self.lineNum,
													 linesOfCode - self.lineNum, '=>', stream)
		#		print(stream.GetData())

		self.isLoadSourceCodeActive = False
		self.finishedLoadingSourceCodeCallback.emit(stream.GetData())
		# QCoreApplication.processEvents()
		# QApplication.processEvents()

	def count_lines_of_code(self, file_path):
		with open(file_path, 'r') as file:
			lines = file.readlines()

		# code_lines = [
		# 	line for line in lines
		# 	if line.strip() # and not line.strip().startswith('//') and not line.strip().startswith('/*')
		# ]
		return len(lines)

	def loadBPsWPs(self):
		# super(LoadBreakpointsWorker, self).workerFunc()

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

		for wp_loc in self.target.watchpoint_iter():
			if self.initTable:
				self.loadWatchpointsValueCallback.emit(wp_loc)  # , self.initTable)
			else:
				self.updateWatchpointsValueCallback.emit(wp_loc)

		self.runLoadSourceCode()
		# self.finishedLoadInstructionsCallback.emit()
		# pass

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

						numChilds = len(value)
						idx = 0
						for child in value:
							idx += 1
							# self.sendProgressUpdate((100 / numRegisters * currReg) + (numRegSeg / numChilds * idx),
							# 						f'Loading registers value {child.GetName()} ...')
							if self.initTable:
								self.loadRegisterValueCallback.emit(currReg - 1, child.GetName(), child.GetValue(),
																	getMemoryValueAtAddress(target, process,
																							child.GetValue()))
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
						# else:
						# 	self.signals.updateVariableValue.emit(str(var.GetName()), str(string_value), str(data),
						# 										  str(var.GetTypeName()), hex(var.GetLoadAddress()))
						idx += 1

					# QCoreApplication.processEvents()
		self.loadBPsWPs()
		# pass

	def char_array_to_string(self, char_array_value):
		byte_array = char_array_value.GetPointeeData(0, char_array_value.GetByteSize())
		error = lldb.SBError()
		sRet = byte_array.GetString(error, 0)
		return "" if sRet == 0 else sRet

	def disassemble_entire_target(self):
		"""Disassembles instructions for the entire target.

		Args:
			target: The SBTarget object representing the debugged process.
		"""

		# self.thread = self.target.GetProcess().GetSelectedThread()
		self.logDbgC.emit(f"Starting to disassemble => continuing ...")
		# print(f"Starting to disassemble => continuing ...")
		idxOuter = 0
		for module in self.target.module_iter():
			if idxOuter != 0:
				idxOuter += 1
				# self.logDbg.emit(f"Starting to disassemble => idxOuter != 0 continuing ...")
				# print(f"Starting to disassemble => idxOuter != 0 continuing ...")
				continue
			idx = 0
			for section in module.section_iter():
				# Check if the section is readable
				#				if not section.IsReadable():
				#					continue
				self.logDbgC.emit(f"section.GetName(): {section.GetName()}")
				if section.GetName() == "__TEXT":  # or  section.GetName() == "__PAGEZERO":
					# if idx != 1:
					# 	idx += 1
					# 	continue

					for subsec in section:
						self.logDbgC.emit(f"subsec.GetName(): {subsec.GetName()}")
						if subsec.GetName() == "__text" or subsec.GetName() == "__stubs":

							idxSym = 0
							lstSym = module.symbol_in_section_iter(subsec)
							# {len(lstSym)}
							self.logDbgC.emit(f"lstSym: {lstSym} / subsec.GetName(): {subsec.GetName()}")

							if subsec.GetName() == "__stubs":
								start_addr = subsec.GetLoadAddress(self.target)
								size = subsec.GetByteSize()
								self.logDbgC.emit(f"size of __stubs: {hex(size)} / {hex(start_addr)}")
								# Disassemble instructions
								end_addr = start_addr + size
								# func_start = subsec.GetStartAddress()
								# func_end = subsec.GetEndAddress()
								estimated_count = size // 6
								insts = self.target.ReadInstructions(lldb.SBAddress(start_addr, self.target),
																int(estimated_count))
								# insts = target.ReadInstructions(lldb.SBAddress(start_addr, target), lldb.SBAddress(end_addr, target))
								for inst in insts:
									# result.PutCString(str(inst))
									self.logDbgC.emit(str(inst))
									self.loadInstructionCallback.emit(inst)
								continue
							# return

							secLen = module.num_symbols  # len(lstSym)
							for sym in lstSym:
								self.logDbgC.emit(f"sym: {sym}")
								#								print(f'get_instructions_from_current_target => {sym.get_instructions_from_current_target()}')
								#								if idxSym != 0:
								#									idxSym += 1
								#									continue
								#								print(sym)
								#							continue
								#								start_address = sym.GetStartAddress().GetLoadAddress(self.target)
								#								end_address = sym.GetEndAddress().GetLoadAddress(self.target)
								#								size = end_address - start_address
								#								print(f'start_address => {start_address} / {hex(start_address)}, end_address => {end_address} / {hex(end_address)}  => SIZE: {size}')
								#								print(sym)
								symFuncName = sym.GetStartAddress().GetFunction().GetName()
								#								print(f'sym.GetName() => {sym.GetName()} / sym.GetStartAddress().GetFunction().GetName() => {sym.GetStartAddress().GetFunction().GetName()}')
								###								start_address = subsec.GetLoadAddress(self.target)
								###								print(f'start_address => {start_address} / {hex(start_address)}')
								###								size = subsec.GetByteSize()
								##
								###								print(f'start_address => {start_address} / {hex(start_address)} => SIZE: {size}')
								##								# Disassemble instructions in chunks
								#								chunk_size = 1024
								#								remaining_bytes = size
								##								while remaining_bytes > 0:  and start_address <= end_address:
								#								while start_address < end_address:
								#									# Read a chunk of data
								#									data_size = min(remaining_bytes, chunk_size)
								#									print(f'sym.GetName() => {sym.GetName()} / SBAddress(start_address, self.target).GetFunction().GetName() => {SBAddress(start_address, self.target).GetFunction().GetName()}')
								#									instructions = self.target.ReadInstructions(SBAddress(start_address, self.target), data_size)
								#									print(f'instructions-Len {len(instructions)}')
								##									# Disassemble and handle instructions
								#									for instruction in instructions:
								#										if symFuncName == instruction.GetAddress().GetFunction().GetName():
								#											print(f"Address: {instruction.GetAddress()}")
								#											print(f"Instruction: {instruction}")
								#											print(f'sym.GetName() => {sym.GetName()} / instruction.GetAddress().GetFunction().GetName() => {instruction.GetAddress().GetFunction().GetName()}')
								#											self.signals.loadInstruction.emit(instruction)
								#
								#									# Update addresses and remaining bytes
								#									start_address += data_size
								#									remaining_bytes -= data_size
								#									print(f'start_address => {start_address} / remaining_bytes => {remaining_bytes} / data_size => {data_size}')
								##								(50*100)/200
								#								print(f'sym.GetStartAddress().GetFunction() => {sym.GetStartAddress().GetFunction()}')
								self.logDbgC.emit(
									f"Analyzing instructions: {len(sym.GetStartAddress().GetFunction().GetInstructions(self.target))}")
								if len(sym.GetStartAddress().GetFunction().GetInstructions(self.target)) <= 0:
									self.logDbgC.emit(f"{sym.GetStartAddress().GetFunction()}")

								# logDbg(f"Analyzing instructions: {len(sym.GetStartAddress().GetFunction().GetInstructions(self.target))}")
								for instruction in sym.GetStartAddress().GetFunction().GetInstructions(self.target):
									# print(f"{instruction}")
									#
									# if (hex(instruction.GetAddress().GetLoadAddress(target)) == "0x100000d39"):
									# 	print(f"IS ATTTT THHHHHEEEEEEE PPPPPOOOOOOIIIIINNNNTTTTTT  !!!!!!!!!!!!!")

									if symFuncName == instruction.GetAddress().GetFunction().GetName():
										#										print(f"Address: {instruction.GetAddress()}")
										#										print(f"Instruction: {instruction}")
										#										print(f'sym.GetName() => {sym.GetName()} / instruction.GetAddress().GetFunction().GetName() => {instruction.GetAddress().GetFunction().GetName()}')
										#										print(f'COMMENT => {instruction.GetComment(self.target)}')
										self.loadInstructionCallback.emit(instruction)
								# else:
								# 	print(f"symFuncName != instr....GetName()")
								idxSym += 1
								# self.sendProgressUpdate((idxSym * 100) / secLen, "Disassembling executable ...")
					# break
					break
				idx += 1
			idxOuter += 1
		self.finishedLoadInstructionsCallback.emit()
		self.loadRegisters()

	# def start_loadDisassemblyWorker(self, handle_loadInstruction, handle_workerFinished, initTable=True):
	# 	self.loadDisassemblyWorker = LoadDisassemblyWorker(self.driver, initTable, self.mainWin)
	# 	# self.loadDisassemblyWorker.signals.finished.connect(handle_workerFinished)
	# 	self.loadDisassemblyWorker.signals.loadInstruction.connect(handle_loadInstruction)
	# 	# self.loop = QEventLoop(self.mainWin)
	# 	self.loadDisassemblyWorker.signals.finished.connect(self.handle_workerFinished())
	# 	self.loadDisassemblyWorker.workerFunc()
	# 	# self.threadpool.start(self.loadDisassemblyWorker)
	# 	# self.loop.exec()  # Blocks until loop.quit() is calleself.threadpool.start(self.loadDisassemblyWorker)
	#
	# def handle_workerFinished(self):
	# 	self.loop.quit()
	# 	self.finishedLoadInstructionsCallback.emit()
	# 	pass

	def disassembleTarget(self):
		self.logDbg.emit(f"HELLO WORLD DISASSEBLE ;-=")
		pass

	def loadTarget(self):
		# return
		# self.logDbg.emit(f"loadTarget() started Num Targets: {self.driver.debugger.GetNumTargets()} ...")
		# if self.driver.debugger.GetNumTargets() > 0:
			# self.target = self.driver.getTarget()
		self.logDbg.emit(f"loadTarget() => Target: {self.target} ...")
		if self.target:
			self.process = self.target.GetProcess()
			self.logDbg.emit(f"loadTarget() => Process: {self.process} ...")
			if self.process:
				self.listener = LLDBListener(self.process, self.driver.debugger)
				self.listener.setHelper = self.mainWin.setHelper
				self.listener.breakpointEvent.connect(self.handle_breakpointEvent)
				self.listener.processEvent.connect(self.handle_processEvent)
				self.listener.gotEvent.connect(self.handle_gotNewEvent)
				self.listener.addListenerCalls()
				self.listener.start()

				self.thread = self.process.GetThreadAtIndex(0)
				self.logDbg.emit(f"loadTarget() => Thread: {self.thread} ...")
				if self.thread:
					self.logDbg.emit(f"loadTarget() => Thread.GetNumFrames(): {self.thread.GetNumFrames()} ...")
					for z in range(self.thread.GetNumFrames()):
						frame = self.thread.GetFrameAtIndex(z)
						self.loadModulesCallback.emit(frame, self.target.modules)
						# self.tabWidgetStruct.cmbModules.addItem(
						# 	frame.GetModule().GetFileSpec().GetFilename() + " (" + str(
						# 		frame.GetFrameID()) + ")")
						self.logDbg.emit(f"loadTarget() => Frame: {frame} ...")
						if frame.GetModule().GetFileSpec().GetFilename() != self.target.GetExecutable().GetFilename():
							self.logDbg.emit(f"Module for FileStzuct IS NOT equal executable => continuing ...")
							continue
						else:
							self.logDbg.emit(f"Module for FileStzuct IS equal executable => scanning ...")
						if frame:
							self.logDbg.emit(f"BEFORE DISASSEMBLE!!!!")
							# self.start_loadDisassemblyWorker(self.loadInstructionCallback, self.finishedLoadInstructionsCallback, True)
							# self.disassembleTarget()
							self.disassemble_entire_target()
							# self.start_loadDisassemblyWorker(True)
							# context = frame.GetSymbolContext(lldb.eSymbolContextEverything)

	def loadFileStats(self):
		statistics = self.driver.getTarget().GetStatistics()
		stream = lldb.SBStream()
		success = statistics.GetAsJSON(stream)
		if success:
			self.loadJSONCallback.emit(str(stream.GetData()))


	def loadNewExecutableFile(self, filename):
		# return

		# logDbg(f"loadNewExecutableFile({filename})...")
		# self.targetBasename = os.path.basename(filename)
		# self.stopTarget()

		global event_queue
		self.mainWin.event_queue = queue.Queue()
		#
		#				#				global driver
		self.mainWin.inited = False
		self.driver = dbg.debuggerdriver.createDriver(self.mainWin.driver.debugger, self.mainWin.event_queue)
		#		self.driver.debugger.SetLoggingCallback(self.my_custom_log_callback)
		self.driver.debugger.SetAsync(False)
		#			self.driver.aborted = False

		#			self.driver.createTarget(filename)
		self.driver.signals.event_queued.connect(self.mainWin.handle_event_queued)
		self.driver.start()
		self.driver.createTarget(filename)
		# logDbg(f"self.driver.createTarget({filename}) => self.driver.debugger.GetNumTargets() = {self.driver.debugger.GetNumTargets()}")
		if self.driver.debugger.GetNumTargets() > 0:
			# self.mainWin.target = self.mainWin.driver.debugger.GetSelectedTarget()


			self.target = self.driver.getTarget()
			self.mainWin.target = self.target
			self.logDbg.emit(f"target: {self.target}")
			# return

			# if self.mainWin.setHelper.getValue(SettingsValues.BreakAtMainFunc):
			#     main_bp = self.mainWin.bpHelper.addBPByName(self.mainWin.setHelper.getValue(SettingsValues.MainFuncName))
			#     print(main_bp)
			#     for bl in main_bp:
			#         logDbg(f"bl.GetAddress(): {hex(bl.GetAddress().GetLoadAddress(target))}")
			#     logDbg(f"main_bp: {main_bp}")
			#
			if self.mainWin.setHelper.getValue(SettingsValues.BreakpointAtMainFunc):
				# self.driver.debugger.SetAsync(True)

				# self.driver.debugger.HandleCommand("process launch --stop-at-entry")
				self.driver.debugger.HandleCommand('process launch --stop-at-entry')

				# main_bp2 = self.enableBPCallback.emit("0x100000ab0", True, False)

				if len(self.driver.getTarget().modules) > 0:
					self.logDbg.emit(f"self.driver.getTarget().GetModuleAtIndex(0) (len: {len(self.driver.getTarget().modules)}): {self.driver.getTarget().GetModuleAtIndex(0)}")
					for idxMod in range(len(self.driver.getTarget().modules)):
						self.logDbg.emit(
							f"- self.driver.getTarget().GetModuleAtIndex({idxMod}): {self.driver.getTarget().GetModuleAtIndex(idxMod)}")

				main_oep = find_main(self.driver.debugger)
				self.driver.debugger.HandleCommand(f'breakpoint set -a {hex(main_oep)}')

				# self.logDbgC.emit(f"find_main(self.driver.debugger) => {hex(main_oep)}")
				# main_bp2 = self.enableBPCallback.emit(hex(main_oep), True, False)
				# self.logDbgC.emit(f"main_bp2 (@ {hex(main_oep)}): {main_bp2}")
				# # print(f"main_bp2 (@ {hex(main_oep)}): {main_bp2}")
				#
				# addrObj2 = find_main(self.driver.debugger)
				# # main_bp2 = self.bpHelper.enableBP(hex(addrObj2), True, False)
				#
				# main_bp2 = self.enableBPCallback.emit(hex(addrObj2), True, False)
				# # self.enableBPCallback.emit(hex(addrObj2), True, False)
				# # print(f"main_bp2 (@{addrObj2}): {main_bp2}")
				# self.logDbgC.emit(f"main_bp2 (@{hex(addrObj2)}): {main_bp2}")

				self.driver.debugger.HandleCommand('breakpoint set --name main')
				self.driver.debugger.HandleCommand(f'br list')
				self.driver.debugger.HandleCommand('process continue')


				# import time
				# time.sleep(5)
				# self.target.GetProcess().Continue()

			# setHelper = SettingsHelper()
			# if self.setHelper.getChecked(SettingsValues.BreakpointAtMainFunc):
			# 	addrObj2 = find_main(self.driver.debugger)
			# 	logDbg(f"Enabling EntryPoint Breakpoint @ {hex(addrObj2)}")
			# 	self.bpHelper.enableBP(hex(addrObj2), True, True)

			# launch_info = target.GetLaunchInfo()

			#########
			# print("AFTER GETLAUNCHINFO!!!!")
			# Create a temporary file to capture output
			# output_path = "/tmp/lldb_output.txt"
			# output_file = open(output_path, "w")
			# output_fd = output_file.fileno()

			# stdout_action = lldb.SBFileAction()
			# stdout_action.Open(output_path, True, False)  # append=False, read=False
			# launch_info.SetFileAction(lldb.eLaunchFlagStdout, stdout_action)
			#########
			# Create a pipe to capture the output
			# read_fd, write_fd = os.pipe()
			# launch_info.SetStandardOutput(write_fd)  # Redirect stdout
			# launch_info.SetStandardError(write_fd)  # (optional) Redirect stderr too

			# if self.setHelper.getValue(SettingsValues.StopAtEntry):
			# 	launch_info.SetLaunchFlags(lldb.eLaunchFlagDisableASLR + lldb.eLaunchFlagStopAtEntry)# lldb.eLaunchFlagDisableASLR +
			# 	logDbg(f"launch_info.SetLaunchFlags(lldb.eLaunchFlagDisableASLR + lldb.eLaunchFlagStopAtEntry)")
			# else:
			# 	launch_info.SetLaunchFlags(lldb.eLaunchFlagDebug)
			# 	logDbg(f"launch_info.SetLaunchFlags(lldb.eLaunchFlagDebug)")

			# if self.setHelper.getValue(SettingsValues.StopAtEntry):
			# 	launch_info.SetLaunchFlags(lldb.eLaunchFlagDisableASLR and lldb.eLaunchFlagStopAtEntry)# lldb.eLaunchFlagDisableASLR +
			# # else:
			# # 	launch_info.SetLaunchFlags(lldb.eLaunchFlagStopAtEntry)
			# # 	launch_info.SetLaunchFlags(lldb.eLaunchFlagDisableASLR and lldb.eLaunchFlagStopAtEntry and lldb.eLaunchFlagDebug)

			# error = lldb.SBError()
			# # SBProcess
			# self.break_at_main(self.driver.debugger, "", "", "")
			# self.process = target.Launch(stop_at_entry=True, error=error)
			# self.break_at_main(self.driver.debugger, "", "", "")
			# self.process.Stop()
			# # output = io.StringIO()

			#########
			# Close the write end in your script so you can read from the read end
			# os.close(write_fd)

			# Read the output
			# output = os.read(read_fd, 4096).decode("utf-8")
			# print(f"Captured output:\n{output}")

			# Read output from file
			# output_file.close()
			# with open(output_path, "r") as f:
			# 	captured_output = f.read()

			# print(f"Captured output:\n{captured_output}")
			#########

			#			target.Launch(self.driver.debugger.GetListener(), None, None, None, output.fileno(), None, None, 0, False, error)
			##			'/tmp/stdout.txt'
			self.loadTarget()
			# self.setWinTitleWithState("Target loaded")
