import lldb

import time
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from config import *
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


	startLoadControlFlowSignal = pyqtSignal()
	runControlFlow_loadConnections = pyqtSignal()
	endLoadControlFlowCallback = pyqtSignal(bool)


	# def do_work(self):
	# 	self.request_text.emit()  # Ask main thread for text


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
		self.allInstructions = []
		self.finishedLoadControlFlow = False
		self.endLoadControlFlowCallback.connect(self.handle_endLoadControlFlowCallback)

	def run(self):
		self._should_stop = False  # Reset before starting
		self.show_dialog.emit()

		self.logDbg.emit(f"loadNewExecutableFile({self.fileToLoad})...")
		self.targetBasename = os.path.basename(self.fileToLoad)
		self.loadNewExecutableFile(self.fileToLoad)
		self.logDbgC.emit(f"self.mainWin.driver.debugger.GetNumTargets() (baseWorkerNG): {self.mainWin.driver.debugger.GetNumTargets()}")
		if self.mainWin.driver.debugger.GetNumTargets() > 0:
			for i in range(self.mainWin.driver.debugger.GetNumTargets()):
				self.logDbgC.emit(f"self.mainWin.driver.debugger.GetTargetAtIndex({i}) (baseWorkerNG): {self.mainWin.driver.debugger.GetTargetAtIndex(i)}")

			self.target = self.mainWin.driver.getTarget()
			self.logDbgC.emit(f"self.target (baseWorkerNG): {self.target}")
			if self.target:
				logDbgC(f"self.target.GetExecutable().GetFilename(): {self.target.GetExecutable().GetFilename()}")
				exe = self.target.GetExecutable().GetDirectory() + "/" + self.target.GetExecutable().GetFilename()
				# self.targetBasename = os.path.basename(exe)
				mach_header = GetFileHeader(exe)
				self.loadFileInfosCallback.emit(mach_header, self.target)
				self.mainWin.devHelper.setupDevHelper()
				self.loadFileStats()

		self.finished.emit()

	def stop(self):
		self._should_stop = True

	def handle_endLoadControlFlowCallback(self, success):
		# self.logDbg.emit(f"Result load control flow: {success}")
		self.finishedLoadControlFlow = True

	def runLoadControlFlow(self):
		self.logDbg.emit(f"runLoadControlFlow ... ")
		while not self.finishedLoadControlFlow:
			self.logDbg.emit(f"... ")
			time.sleep(0.5)
		self.logDbg.emit(f"Finished loading control flow ... continuing ...")

		# if self.setHelper.getChecked(SettingsValues.BreakpointAtMainFunc):
		# 	self.bpHelper.enableBP(hex(addrObj2), True, False)
		# self.txtMultiline.viewAddress(hex(addrObj2))
		# self.setProgressValue(95)
		# QApplication.processEvents()
		# self.window().wdtControlFlow.view.verticalScrollBar().setValue(self.window().txtMultiline.table.verticalScrollBar().value())
		pass

	def runLoadSourceCode(self):
		if self.isLoadSourceCodeActive:
			interruptLoadSourceCode = True
			return
		else:
			interruptLoadSourceCode = False
		self.isLoadSourceCodeActive = True

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
		self.finishedLoadControlFlow = False
		self.finishedLoadingSourceCodeCallback.emit(stream.GetData())
		# startLoadControlFlowSignal
		self.runControlFlow_loadConnections.emit()
		# QCoreApplication.processEvents()
		# QApplication.processEvents()
		self.runLoadControlFlow()

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
		self.runLoadSourceCode()
		self.runLoadControlFlow()

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
								self.allInstructions += sym.GetStartAddress().GetFunction().GetInstructions(self.target)
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
		self.logDbgC.emit(f"createTarget({filename})")
		self.target = self.driver.createTarget(filename)

		if self.target.IsValid():
			self.mainWin.target = self.target
			self.logDbgC.emit(f"target: {self.target}")
			
			if self.mainWin.setHelper.getValue(SettingsValues.BreakpointAtMainFunc):
				# self.driver.debugger.SetAsync(True)

				self.driver.debugger.HandleCommand('process launch --stop-at-entry')

				# main_bp2 = self.enableBPCallback.emit("0x100000ab0", True, False)

				if len(self.driver.getTarget().modules) > 0:
					self.logDbg.emit(f"self.driver.getTarget().GetModuleAtIndex(0) (len: {len(self.driver.getTarget().modules)}): {self.driver.getTarget().GetModuleAtIndex(0)}")
					for idxMod in range(len(self.driver.getTarget().modules)):
						self.logDbg.emit(
							f"- self.driver.getTarget().GetModuleAtIndex({idxMod}): {self.driver.getTarget().GetModuleAtIndex(idxMod)}")

				main_oep = find_main(self.driver.debugger)
				self.driver.debugger.HandleCommand(f'breakpoint set -a {hex(main_oep)} -N kimon')

				# Set breakpoint on scanf
				if	self.mainWin.setHelper.getValue(SettingsValues.AutoBreakpointForScanf):
					bp = self.driver.getTarget().BreakpointCreateByName("scanf")
					for bl in bp:
						logDbgC(f"bl.location: {bl}")
						
					self.driver.scanfID = bp.GetID()
					self.driver.debugger.HandleCommand(f'br name add -N scanf {bp.GetID()}')
					bp.SetScriptCallbackFunction("on_scanf_hit")
					self.logDbgC.emit(f'breakpoint set "scanf": {bp}')

				self.driver.debugger.HandleCommand('breakpoint set --name main')
				self.driver.debugger.HandleCommand(f'br list')
				self.driver.debugger.HandleCommand('process continue')

			self.loadTarget()
		else:
			print(f"Error creating target!!!")