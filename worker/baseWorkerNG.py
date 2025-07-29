import lldb
import os
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
	loadSymbolCallback = pyqtSignal(str)
	finishedLoadInstructionsCallback = pyqtSignal(object)
	loadRegisterCallback = pyqtSignal(str)
	loadRegisterValueCallback = pyqtSignal(int, str, str, str)
	loadVariableValueCallback = pyqtSignal(str, str, str, str, str)
	# loadBreakpointsValueCallback = pyqtSignal(str, str, str, str, str)
	loadBreakpointsValueCallback = pyqtSignal(object, bool)
	updateBreakpointsValueCallback = pyqtSignal(object)
	loadWatchpointsValueCallback = pyqtSignal(object)
	updateWatchpointsValueCallback = pyqtSignal(object)
	finishedLoadingSourceCodeCallback = pyqtSignal(str)
	progressUpdateCallback = pyqtSignal(int, str)

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
	arch = ""
	args = ""
	targetBasename = ""
	startAddr = 0x0
	endAddr = 0x0


	def __init__(self, mainWinToUse, filename, initTable=True, sourceFile=""):
		super().__init__()

		# self.threadpool = QThreadPool(self)
		self.initTable = initTable
		self._should_stop = False
		self.mainWin = mainWinToUse
		self.fileToLoad = filename
		self.arch = ""
		self.args = ""
		self.loadSourceCode = True
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
		self.startAddr = 0x0
		self.endAddr = 0x0
		self.allInstructions = []
		self.finishedLoadControlFlow = False
		self.endLoadControlFlowCallback.connect(self.handle_endLoadControlFlowCallback)

	def run(self):
		self._should_stop = False  # Reset before starting
		self.show_dialog.emit()

		self.logDbg.emit(f"loadNewExecutableFile({self.fileToLoad})...")
		self.targetBasename = os.path.basename(self.fileToLoad)
		self.loadNewExecutableFile(self.fileToLoad)
		self.logDbgC.emit(f"self.mainWin.driver.debugger.GetNumTargets() (baseWorkerNG): {self.mainWin.driver.debugger.GetNumTargets()}", DebugLevel.Verbose)
		if self.mainWin.driver.debugger.GetNumTargets() > 0:
			# for i in range(self.mainWin.driver.debugger.GetNumTargets()):
			# 	self.logDbgC.emit(f"self.mainWin.driver.debugger.GetTargetAtIndex({i}) (baseWorkerNG): {self.mainWin.driver.debugger.GetTargetAtIndex(i)}", DebugLevel.Verbose)

			self.target = self.mainWin.driver.getTarget()
			self.logDbgC.emit(f"self.target (baseWorkerNG): {self.target}", DebugLevel.Verbose)
			if self.target:
				logDbgC(f"self.target.GetExecutable().GetFilename(): {self.target.GetExecutable().GetFilename()}", DebugLevel.Verbose)
				exe = self.target.GetExecutable().GetDirectory() + "/" + self.target.GetExecutable().GetFilename()
				# self.targetBasename = os.path.basename(exe)
				mach_header = GetFileHeader(exe)
				self.logDbgC.emit(f"mach_header = GetFileHeader(exe): {mach_header}", DebugLevel.Verbose)
				self.loadFileInfosCallback.emit(mach_header, self.target)
				self.logDbgC.emit(f"after self.loadFileInfosCallback.emit(...)", DebugLevel.Verbose)
				# self.mainWin.devHelper.setupDevHelper()
				self.loadFileStats()

		self.finished.emit()

	def stop(self):
		self._should_stop = True

	def handle_endLoadControlFlowCallback(self, success):
		# self.logDbg.emit(f"Result load control flow: {success}")
		self.finishedLoadControlFlow = True

	def runLoadControlFlow(self):
		self.logDbgC.emit(f"runLoadControlFlow ... ", DebugLevel.Info)
		while not self.finishedLoadControlFlow:
			# self.logDbg.emit(f"... ")
			time.sleep(0.5)
		self.logDbgC.emit(f"Finished loading control flow ... continuing ...", DebugLevel.Verbose)

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
		context = self.frame.GetSymbolContext(lldb.eSymbolContextEverything)
		self.lineNum = context.GetLineEntry().GetLine()
		# Create the filespec for 'main.c'.
		filespec = lldb.SBFileSpec(sourcefileToUse, False)
		source_mgr = self.driver.debugger.GetSourceManager()
		# Use a string stream as the destination.
		linesOfFileContent = self.linesOfFileContent(sourcefileToUse)
		linesOfCode = len(linesOfFileContent)
		self.logDbgC.emit(f"linesOfCode: {linesOfCode} / {linesOfCode - self.lineNum}", DebugLevel.Verbose)
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

		self.logDbgC.emit(f"BEFORE self.runLoadControlFlow() => runLoadSourceCode()", DebugLevel.Info)
		if loadFlowControl:
			self.runControlFlow_loadConnections.emit()
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
			logDbgC(f"The source code file: {file_path} could not be found!")

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
			logDbgC(f"The file: {file_path} could not be found!")

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
		if self.loadSourceCode:
			sourceFilesFound = find_source_file(self.fileToLoad)
			if len(sourceFilesFound) > 0:
				logDbgC(f"Tried to auto-find sourcefile => Found: {len(sourceFilesFound)}: {sourceFilesFound[0]}! Loading file ...")
				self.runLoadSourceCode(sourceFilesFound[0])
			else:
				logDbgC(f"Tried to auto-find sourcefile => NOTHING Found!!!")
		else:
			self.runControlFlow_loadConnections.emit()
			# QCoreApplication.processEvents()
			# QApplication.processEvents()
			self.logDbgC.emit(f"BEFORE self.runLoadControlFlow() => runLoadSourceCode()", DebugLevel.Info)
			self.runLoadControlFlow()
		# self.logDbgC.emit(f"BEFORE self.runLoadControlFlow() => loadRegisters()", DebugLevel.Info)
		# self.runLoadControlFlow()

	def char_array_to_string(self, char_array_value):
		byte_array = char_array_value.GetPointeeData(0, char_array_value.GetByteSize())
		error = lldb.SBError()
		sRet = byte_array.GetString(error, 0)
		return "" if sRet == 0 else sRet

	def disassemble_entire_target(self):
		self.logDbgC.emit(f"============ NEW DISASSEMBLER ===============", DebugLevel.Verbose)
		idx = 0
		for module in self.target.module_iter():
			self.logDbgC.emit(f"\n📦 Module: {module.file}", DebugLevel.Verbose)
			# /Volumes/Data/dev/python/LLDBPyGUI/_testtarget/
			if module.file.GetFilename() == self.target.executable.GetFilename(): # "a_hello_world_test":
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
					self.logDbgC.emit(f"section.GetName(): {section.GetName()}", DebugLevel.Verbose)
					if section.GetName() == "__TEXT":  # or  section.GetName() == "__PAGEZERO":
						# if idx != 1:
						# 	idx += 1
						# 	continue
						idxInstructions = 0
						for subsec in section:
							self.logDbgC.emit(f"subsec.GetName(): {subsec.GetName()}", DebugLevel.Verbose)
							if subsec.GetName() == "__text" or subsec.GetName() == "__stubs":

								idxSym = 0
								lstSym = module.symbol_in_section_iter(subsec)
								for smbl in lstSym:
									self.logDbgC.emit(f"===========>>>>>>>>>>> symbl: {smbl}", DebugLevel.Verbose)
									# .GetStartAddress().GetFunction()
									# self.loadSymbolCallback.emit(smbl.GetName())
									instructions = smbl.GetStartAddress().GetFunction().GetInstructions(self.target)
									self.allInstructions += instructions
									for instruction in instructions:
										self.loadInstructionCallback.emit(instruction)
										idxInstructions += 1
										self.checkLoadConnection(instruction, idxInstructions + (idxSym + 1))
									idxSym += 1


								if subsec.GetName() == "__stubs":
									start_addr = subsec.GetLoadAddress(self.target)
									size = subsec.GetByteSize()
									self.logDbgC.emit(f"size of __stubs: {hex(size)} / {hex(start_addr)}", DebugLevel.Verbose)
									# Disassemble instructions
									end_addr = start_addr + size
									# func_start = subsec.GetStartAddress()
									# func_end = subsec.GetEndAddress()
									logDbgC(f"__stubs: start_addr: {start_addr} / end_addr: {end_addr}")
									estimated_count = size // 6
									instructions = self.target.ReadInstructions(lldb.SBAddress(start_addr, self.target),
																	int(estimated_count))
									# insts = target.ReadInstructions(lldb.SBAddress(start_addr, target), lldb.SBAddress(end_addr, target))
									for instruction in instructions:
										# result.PutCString(str(inst))
										self.logDbgC.emit(str(instruction), DebugLevel.Verbose)
										self.loadInstructionCallback.emit(instruction)
										idxInstructions += 1
										self.checkLoadConnection(instruction, idxInstructions + (idxSym + 1))
									continue
								# return
				# num_symbols = module.GetNumSymbols()
				#
				# for i in range(num_symbols):
				# 	symbol = module.GetSymbolAtIndex(i)
				# 	if not symbol.IsValid():
				# 		continue
				#
				# 	# Only disassemble code symbols
				# 	if symbol.GetType() == lldb.eSymbolTypeCode:
				# 		name = symbol.GetName()
				# 		start_addr = symbol.GetStartAddress()
				# 		end_addr = symbol.GetEndAddress()
				#
				# 		self.logDbgC.emit(f"\n🔧 Symbol: {name}", DebugLevel.Verbose)
				# 		self.logDbgC.emit(f"   Range: {start_addr} - {end_addr}", DebugLevel.Verbose)
				#
				# 		addrStart = start_addr #lldb.SBAddress(start_addr, self.target)
				# 		addrEnd = end_addr.GetLoadAddress(self.target) # lldb.SBAddress(end_addr, self.target)
				#
				# 		# instructions = self.target.ReadInstructions(addrStart, addrEnd)
				# 		# # instructions = self.target.ReadInstructions(start_addr, end_addr.GetLoadAddress(self.target))
				# 		# for inst in instructions:
				# 		# 	self.logDbgC.emit(f"   {inst}")
				# # break
						break
				break
			# else:
			# 	break
			idx += 1
		self.logDbgC.emit(f"============ END DISASSEMBLER ===============", DebugLevel.Verbose)
		# """Disassembles instructions for the entire target.
		#
		# Args:
		# 	target: The SBTarget object representing the debugged process.
		# """
		#
		# # self.thread = self.target.GetProcess().GetSelectedThread()
		# self.logDbgC.emit(f"Starting to disassemble => continuing ...", DebugLevel.Verbose)
		# # print(f"Starting to disassemble => continuing ...")
		# idxOuter = 0
		# for module in self.target.module_iter():
		# 	if idxOuter != 0:
		# 		idxOuter += 1
		# 		# self.logDbg.emit(f"Starting to disassemble => idxOuter != 0 continuing ...")
		# 		# print(f"Starting to disassemble => idxOuter != 0 continuing ...")
		# 		continue
		# 	idx = 0
		#
		# 	# for module in self.target.module_iter():
		# 	# for compile_unit in module.compile_unit_iter():
		# 	# 	for func in compile_unit:
		# 	# 		if func.IsValid():
		# 	# 			self.logDbgC.emit(f"Objective-C Function: {func.GetName()}")
		#
		# 	for section in module.section_iter():
		# 		# Check if the section is readable
		# 		#				if not section.IsReadable():
		# 		#					continue
		# 		self.logDbgC.emit(f"section.GetName(): {section.GetName()}", DebugLevel.Verbose)
		# 		if section.GetName() == "__TEXT":  # or  section.GetName() == "__PAGEZERO":
		# 			# if idx != 1:
		# 			# 	idx += 1
		# 			# 	continue
		# 			idxInstructions = 0
		# 			for subsec in section:
		# 				self.logDbgC.emit(f"subsec.GetName(): {subsec.GetName()}", DebugLevel.Verbose)
		# 				if subsec.GetName() == "__text" or subsec.GetName() == "__stubs":
		#
		# 					idxSym = 0
		# 					lstSym = module.symbol_in_section_iter(subsec)
		# 					for smbl in lstSym:
		# 						self.logDbgC.emit(f"===========>>>>>>>>>>> symbl: {smbl}", DebugLevel.Verbose)
		# 						self.loadSymbolCallback.emit(smbl.GetStartAddress().GetFunction().GetName())
		# 						# if symFuncName == instruction.GetAddress().GetFunction().GetName():
		# 						#										print(f"Address: {instruction.GetAddress()}")
		# 						#										print(f"Instruction: {instruction}")
		# 						#										print(f'sym.GetName() => {sym.GetName()} / instruction.GetAddress().GetFunction().GetName() => {instruction.GetAddress().GetFunction().GetName()}')
		# 						#										print(f'COMMENT => {instruction.GetComment(self.target)}')
		# 						instructions = smbl.GetStartAddress().GetFunction().GetInstructions(self.target)
		# 						for instruction in instructions:
		# 							self.loadInstructionCallback.emit(instruction)
		# 						# if  instruction.GetMnemonic(self.target) is None:
		# 						# 	continue
		# 						idxInstructions += 1
		# 						self.checkLoadConnection(instruction, idxInstructions + (idxSym + 1))
		# 						break
		# 					# idxInstructions = 0
		# 					# {len(lstSym)}
		# 					self.logDbgC.emit(f"lstSym: {lstSym} / subsec.GetName(): {subsec.GetName()}", DebugLevel.Verbose)
		#
		# 					if subsec.GetName() == "__stubs":
		# 						start_addr = subsec.GetLoadAddress(self.target)
		# 						size = subsec.GetByteSize()
		# 						self.logDbgC.emit(f"size of __stubs: {hex(size)} / {hex(start_addr)}", DebugLevel.Verbose)
		# 						# Disassemble instructions
		# 						end_addr = start_addr + size
		# 						# func_start = subsec.GetStartAddress()
		# 						# func_end = subsec.GetEndAddress()
		# 						logDbgC(f"__stubs: start_addr: {start_addr} / end_addr: {end_addr}")
		# 						estimated_count = size // 6
		# 						insts = self.target.ReadInstructions(lldb.SBAddress(start_addr, self.target),
		# 														int(estimated_count))
		# 						# insts = target.ReadInstructions(lldb.SBAddress(start_addr, target), lldb.SBAddress(end_addr, target))
		# 						for inst in insts:
		# 							# result.PutCString(str(inst))
		# 							self.logDbgC.emit(str(inst), DebugLevel.Verbose)
		# 							self.loadInstructionCallback.emit(inst)
		# 							idxInstructions += 1
		# 							self.checkLoadConnection(inst, idxInstructions + (idxSym + 1))
		# 						continue
		# 					# return
		#
		# 					secLen = module.num_symbols  # len(lstSym)
		# 					for sym in lstSym:
		# 						self.logDbgC.emit(f"sym: {sym}", DebugLevel.Verbose)
		# 						# if sym.addr <=
		# 						# if subsec.GetName() == "__text":
		# 							# if sym.GetName() == "main":
		# 							# 	self.logDbgC.emit(f"========>>>>>>>> main function hit ...", DebugLevel.Verbose)
		# 							# 	for module in self.target.module_iter():
		# 							# 		# 	for section in module.section_iter():
		# 							# 		if hasattr(subsec, 'symbol_in_section_iter'):
		# 							# 			for symbol in module.symbol_in_section_iter(section):
		# 							# 				if symbol.IsValid():
		# 							# 					name = symbol.GetName()
		# 							# 					# start_addr = symbol.GetStartAddress().GetLoadAddress(self.target)
		# 							# 					self.logDbgC(f"------->>>>>>>>> Symbol name: {name}")
		# 							# 					self.loadInstructionCallback.emit(
		# 							# 						sym.GetStartAddress().GetFunction().GetInstructions()[0])
		# 							# 					return
		# 							# if hasattr(subsec, 'symbol_in_section_iter'):
		# 							# 	for symbol in module.symbol_in_section_iter(section):
		# 							# 		if symbol.IsValid():
		# 							# 			name = symbol.GetName()
		# 							# 			# start_addr = symbol.GetStartAddress().GetLoadAddress(self.target)
		# 							# 			self.logDbgC(f"------->>>>>>>>> Symbol name: {name}")
		# 							# 			self.loadInstructionCallback.emit(sym.GetStartAddress().GetFunction().GetInstructions()[0])
		# 						#								print(f'get_instructions_from_current_target => {sym.get_instructions_from_current_target()}')
		# 						#								if idxSym != 0:
		# 						#									idxSym += 1
		# 						#									continue
		# 						#								print(sym)
		# 						#							continue
		# 						#								start_address = sym.GetStartAddress().GetLoadAddress(self.target)
		# 						#								end_address = sym.GetEndAddress().GetLoadAddress(self.target)
		# 						#								size = end_address - start_address
		# 						#								print(f'start_address => {start_address} / {hex(start_address)}, end_address => {end_address} / {hex(end_address)}  => SIZE: {size}')
		# 						#								print(sym)
		# 						symFuncName = sym.GetStartAddress().GetFunction().GetName()
		# 						self.logDbgC.emit(f"symFuncName: {symFuncName}", DebugLevel.Verbose)
		# 						# if symFuncName == "main":
		# 						# 	# for module in self.target.module_iter():
		# 						# 	# 	for section in module.section_iter():
		# 						# 	# if module.
		# 						# 	if hasattr(subsec, 'symbol_in_section_iter'):
		# 						# 		for symbol in module.symbol_in_section_iter(subsec):
		# 						# 			if symbol.IsValid():
		# 						# 				name = symbol.GetName()
		# 						# 				start_addr = symbol.GetStartAddress().GetLoadAddress(self.target)
		# 						# 				self.logDbgC(f"------->>>>>>>>> Symbol name: {name}")
		# 						# 				self.loadInstructionCallback.emit(sym.GetStartAddress().GetFunction().GetInstructions()[0])
		# 						# 	# # for module in self.target.module_iter():
		# 						# 	# for compile_unit in module.compile_unit_iter():
		# 						# 	# 	for func in compile_unit:
		# 						# 	# 		if func.IsValid():
		# 						# 	# 			self.logDbgC.emit(f"Objective-C Function: {func.GetName()}")
		# 						# 	pass
		# 						#								print(f'sym.GetName() => {sym.GetName()} / sym.GetStartAddress().GetFunction().GetName() => {sym.GetStartAddress().GetFunction().GetName()}')
		# 						###								start_address = subsec.GetLoadAddress(self.target)
		# 						###								print(f'start_address => {start_address} / {hex(start_address)}')
		# 						###								size = subsec.GetByteSize()
		# 						##
		# 						###								print(f'start_address => {start_address} / {hex(start_address)} => SIZE: {size}')
		# 						##								# Disassemble instructions in chunks
		# 						#								chunk_size = 1024
		# 						#								remaining_bytes = size
		# 						##								while remaining_bytes > 0:  and start_address <= end_address:
		# 						#								while start_address < end_address:
		# 						#									# Read a chunk of data
		# 						#									data_size = min(remaining_bytes, chunk_size)
		# 						#									print(f'sym.GetName() => {sym.GetName()} / SBAddress(start_address, self.target).GetFunction().GetName() => {SBAddress(start_address, self.target).GetFunction().GetName()}')
		# 						#									instructions = self.target.ReadInstructions(SBAddress(start_address, self.target), data_size)
		# 						#									print(f'instructions-Len {len(instructions)}')
		# 						##									# Disassemble and handle instructions
		# 						#									for instruction in instructions:
		# 						#										if symFuncName == instruction.GetAddress().GetFunction().GetName():
		# 						#											print(f"Address: {instruction.GetAddress()}")
		# 						#											print(f"Instruction: {instruction}")
		# 						#											print(f'sym.GetName() => {sym.GetName()} / instruction.GetAddress().GetFunction().GetName() => {instruction.GetAddress().GetFunction().GetName()}')
		# 						#											self.signals.loadInstruction.emit(instruction)
		# 						#
		# 						#									# Update addresses and remaining bytes
		# 						#									start_address += data_size
		# 						#									remaining_bytes -= data_size
		# 						#									print(f'start_address => {start_address} / remaining_bytes => {remaining_bytes} / data_size => {data_size}')
		# 						##								(50*100)/200
		# 						#								print(f'sym.GetStartAddress().GetFunction() => {sym.GetStartAddress().GetFunction()}')
		# 						self.logDbgC.emit(
		# 							f"Analyzing instructions: {len(sym.GetStartAddress().GetFunction().GetInstructions(self.target))}", DebugLevel.Verbose)
		# 						if len(sym.GetStartAddress().GetFunction().GetInstructions(self.target)) <= 0:
		# 							self.logDbgC.emit(f"{sym.GetStartAddress().GetFunction()}")
		#
		# 						# logDbg(f"Analyzing instructions: {len(sym.GetStartAddress().GetFunction().GetInstructions(self.target))}")
		# 						self.allInstructions += sym.GetStartAddress().GetFunction().GetInstructions(self.target)
		# 						for instruction in sym.GetStartAddress().GetFunction().GetInstructions(self.target):
		#
		# 							# print(f"{instruction}")
		# 							#
		# 							# if (hex(instruction.GetAddress().GetLoadAddress(target)) == "0x100000d39"):
		# 							# 	print(f"IS ATTTT THHHHHEEEEEEE PPPPPOOOOOOIIIIINNNNTTTTTT  !!!!!!!!!!!!!")
		#
		# 							if symFuncName == instruction.GetAddress().GetFunction().GetName():
		# 								#										print(f"Address: {instruction.GetAddress()}")
		# 								#										print(f"Instruction: {instruction}")
		# 								#										print(f'sym.GetName() => {sym.GetName()} / instruction.GetAddress().GetFunction().GetName() => {instruction.GetAddress().GetFunction().GetName()}')
		# 								#										print(f'COMMENT => {instruction.GetComment(self.target)}')
		# 								self.loadInstructionCallback.emit(instruction)
		# 								# if  instruction.GetMnemonic(self.target) is None:
		# 								# 	continue
		# 								idxInstructions += 1
		# 								self.checkLoadConnection(instruction, idxInstructions + (idxSym + 1))
		#
		# 								# doFlowControl
		# 						# else:
		# 						# 	print(f"symFuncName != instr....GetName()")
		# 						idxSym += 1
		# 						# self.sendProgressUpdate((idxSym * 100) / secLen, "Disassembling executable ...")
		# 			# break
		# 			break
		# 		idx += 1
		# 	idxOuter += 1
		#
		#
		idxInst = 0
		for inst in self.allInstructions:
			for con in self.connections:
				if con.destAddr == int(str(inst.GetAddress().GetLoadAddress(self.target)), 10):
					if (idxInst < con.origRow):
						con.destRow = con.origRow
						con.origRow = idxInst
						con.jumpDistInRows = abs(con.destRow - con.origRow) * -1
					else:
						con.destRow = idxInst
						con.jumpDistInRows = abs(con.destRow - con.origRow)
			idxInst += 1

		for con in self.connections:
			logDbgC(f"===>>> Connection: {hex(con.origAddr)} / {hex(con.destAddr)} => {con.origRow} / {con.destRow}")
			# pass
		self.progressUpdateCallback.emit(35, f"Read disassembly and created control flow connections ...")
		QApplication.processEvents()
		self.connections.sort(key=lambda x: abs(x.jumpDist), reverse=True)
		self.finishedLoadInstructionsCallback.emit(self.connections)
		self.loadRegisters()

	radius = 15
	connections = []

	def get_line_number(self, address_int):
		# target = debugger.GetSelectedTarget()
		addr = lldb.SBAddress(address_int, self.target)
		                            
		# Resolve symbol context with line entry info
		context = self.target.ResolveSymbolContextForAddress(
	        addr,
	        lldb.eSymbolContextLineEntry
		)

		line_entry = context.GetLineEntry()
		if line_entry.IsValid():
			file_spec = line_entry.GetFileSpec()
			line = line_entry.GetLine()
			print(f"📍 Address 0x{address_int:x} maps to {file_spec.GetFilename()}:{line}")
			return line # file_spec.GetFilename(), 
		else:
			print("❌ No line info found for this address.")
		return None

	def isInsideTextSectionGetRangeVarsReady(self):
		self.thread = self.process.GetThreadAtIndex(0)
		module = self.thread.GetFrameAtIndex(0).GetModule()
		for sec in module.section_iter():
			for idx3 in range(sec.GetNumSubSections()):
				subSec = sec.GetSubSectionAtIndex(idx3)
				if subSec.GetName() == "__text":
					self.startAddr = subSec.GetFileAddress()
					self.endAddr = subSec.GetFileAddress() + subSec.GetByteSize()
				# elif subSec.GetName() == "__stubs":
				# 	logDbgC(f"GOT __stubs: {subSec.GetName()} => subSec.GetFileAddress(): {subSec.GetFileAddress()}, subSec.GetByteSize(): {subSec.GetByteSize()}, self.endAddr: {self.endAddr}")
				# 	self.endAddr = subSec.GetFileAddress() + subSec.GetByteSize()

	def isInsideTextSection(self, addr):
		try:
			return self.endAddr > int(addr, 16) >= self.startAddr
		except Exception as e:
			logDbgC(f"Exception: {e}", DebugLevel.Error)
			return False

	
	def checkLoadConnection(self, instruction, idxInstructions):
		sMnemonic = instruction.GetMnemonic(self.target)
		# if sMnemonic is None or sMnemonic == "":
		# 	return

		if sMnemonic is not None and sMnemonic.startswith(JMP_MNEMONICS) and not sMnemonic.startswith(JMP_MNEMONICS_EXCLUDE):
			sAddrJumpTo = instruction.GetOperands(self.target)
			if self.isInsideTextSection(sAddrJumpTo):
				sAddrJumpFrom = hex(int(str(instruction.GetAddress().GetLoadAddress(self.target)), 10))
				rowStart = idxInstructions#int(self.get_line_number(int(sAddrJumpFrom, 16)))
				rowEnd = int(self.get_line_number(int(sAddrJumpTo, 16)))
				logDbgC(f"Found connection from line: {rowStart} to: {rowEnd} ({sAddrJumpFrom} / {sAddrJumpTo})")
		# pass
		# 	sAddrJumpTo = tblDisassembly.item(row, 4).text()
        #     if self.isInsideTextSection(sAddrJumpTo):
        #         sAddrJumpFrom = tblDisassembly.item(row, 2).text()
        #         # logDbg(f"Found instruction with jump @: {sAddrJumpFrom} / isInside: {sAddrJumpTo}!")
        #         rowStart = int(tblDisassembly.getRowForAddress(sAddrJumpFrom))
        #         rowEnd = int(tblDisassembly.getRowForAddress(sAddrJumpTo))
		#		rad = self.radius
				if (rowStart < rowEnd):
					newConObj = QControlFlowWidget.draw_flowConnectionNG(rowStart, rowEnd, int(sAddrJumpFrom, 16), int(sAddrJumpTo, 16), None, QColor("lightblue"), self.radius) # self.window().txtMultiline.table
				else:
					newConObj = QControlFlowWidget.draw_flowConnectionNG(rowStart, rowEnd, int(sAddrJumpFrom, 16), int(sAddrJumpTo, 16), None, QColor("lightgreen"), self.radius, 1, True)
				# newConObj.parentControlFlow = self
				# self.addConnection(newConObj)
				newConObj.mnemonic = sMnemonic
				logDbgC(f"Connection (Branch) is a: {newConObj.mnemonic} / {sMnemonic})")
				if abs(newConObj.jumpDist / 2) <= (newConObj.radius / 2):
					newConObj.radius = newConObj.jumpDist / 2
				self.connections.append(newConObj)
				if self.radius <= 130:
					self.radius += 15
				# self.connections.sort(key=lambda x: abs(x.jumpDist), reverse=True)
				#
				# idx = 1
				# radius = 10
				# con = newConObj
				# # for con in self.connections:
				# y_position = self.mainWin.txtMultiline.table.rowViewportPosition(con.origRow)
				# y_position2 = self.mainWin.txtMultiline.table.rowViewportPosition(con.destRow)
				#
				# nRowHeight = 21
				# nOffsetAdd = 23
				# xOffset = (controlFlowWidth / 2) + (((controlFlowWidth - radius) / 2)) # + (radius / 2)
				#
				# self.yPosStart = y_position + (nRowHeight / 2) + (radius / 2)
				# self.yPosEnd = y_position2 + (nRowHeight / 2) - (radius / 2)
				# line = HoverLineItem(xOffset, self.yPosStart, xOffset,
				# 					 self.yPosEnd, con)  # 1260)
				# line.setPen(QPen(con.color, con.lineWidth))
				# self.scene.addItem(line)
				#
				# ellipse_rect = QRectF(xOffset, y_position + (nRowHeight / 2), radius, radius)
				#
				# # Create a painter path and draw a 90° arc
				# path = QPainterPath()
				# path.arcMoveTo(ellipse_rect, 90)  # Start at 0 degrees
				# path.arcTo(ellipse_rect, 90, 90)  # Draw 90-degree arc clockwise
				#
				# # Add the path to the scene
				# arc_item = HoverPathItem(path, con)
				# arc_item.setPen(QPen(con.color, con.lineWidth))
				# self.scene.addItem(arc_item)
				# con.topArc = arc_item
				#
				# ellipse_rect2 = QRectF(xOffset, y_position2 + (nRowHeight / 2) - (radius), radius,
				# 					   radius)
				# # Create a painter path and draw a 90° arc
				# path2 = QPainterPath()
				# path2.arcMoveTo(ellipse_rect2, 180)  # Start at 0 degrees
				# path2.arcTo(ellipse_rect2, 180, 90)  # Draw 90-degree arc clockwise
				#
				# # Add the path to the scene
				# arc_item2 = HoverPathItem(path2, con)
				# arc_item2.setPen(QPen(con.color, con.lineWidth))
				# self.scene.addItem(arc_item2)
				# con.bottomArc = arc_item2
				#
				# if con.switched:
				# 	arrowStart = QPointF(xOffset + (radius / 2) - 6 + 2, y_position + (
				# 			nRowHeight / 2))
				# 	arrowEnd = QPointF(xOffset + (radius / 2) + 2, y_position + (nRowHeight / 2))
				# 	con.startArrow = self.draw_arrowNG(arrowStart, arrowEnd)
				# else:
				# 	arrowEnd = QPointF(xOffset + (radius / 2) - 6 + 2, y_position + (
				# 			nRowHeight / 2))
				# 	arrowStart = QPointF(xOffset + (radius / 2) + 2,
				# 						 y_position + (nRowHeight / 2))
				# 	con.endArrow = self.draw_arrowNG(arrowStart, arrowEnd)
				#
				# if con.switched:
				# 	arrowEnd = QPointF(xOffset + (radius / 2) - 6 + 2, y_position2 + (
				# 			nRowHeight / 2))
				# 	arrowStart = QPointF(xOffset + (radius / 2) + 2,
				# 						 y_position2 + (nRowHeight / 2))
				# 	con.endArrow = self.draw_arrowNG(arrowStart, arrowEnd)
				# else:
				# 	arrowStart = QPointF(xOffset + (radius / 2) - 6 + 2, y_position2 + (
				# 			nRowHeight / 2))
				# 	arrowEnd = QPointF(xOffset + (radius / 2) + 2,
				# 					   y_position2 + (nRowHeight / 2))
				# 	con.startArrow = self.draw_arrowNG(arrowStart, arrowEnd)
				#
				# con.setToolTip(f"Branch\n-from: {hex(con.origAddr)}\n-to: {hex(con.destAddr)}\n-distance: {hex(con.jumpDist)}")
				# if radius <= 130:
				# 	radius += 15
				# idx += 1

				

	def disassembleTarget(self):
		self.logDbg.emit(f"HELLO WORLD DISASSEBLE ;-=")
		pass

	def loadTarget(self):
		self.logDbgC.emit(f"loadTarget() => Target: {self.target} ...", DebugLevel.Verbose)
		if self.target:
			self.process = self.target.GetProcess()
			self.logDbgC.emit(f"loadTarget() => Process: {self.process} ...", DebugLevel.Verbose)

			if self.process:
				self.listener = LLDBListener(self.process, self.driver.debugger)
				self.listener.setHelper = self.mainWin.setHelper
				self.listener.breakpointEvent.connect(self.handle_breakpointEvent)
				self.listener.processEvent.connect(self.handle_processEvent)
				self.listener.gotEvent.connect(self.handle_gotNewEvent)
				self.listener.addListenerCalls()
				self.listener.start()

				self.thread = self.process.GetThreadAtIndex(0)
				self.logDbgC.emit(f"loadTarget() => Thread: {self.thread} ...", DebugLevel.Verbose)
				if self.thread:
					self.isInsideTextSectionGetRangeVarsReady()
					self.logDbgC.emit(f"loadTarget() => Thread.GetNumFrames(): {self.thread.GetNumFrames()} ...", DebugLevel.Verbose)
					for z in range(self.thread.GetNumFrames()):
						frame = self.thread.GetFrameAtIndex(z)
						self.loadModulesCallback.emit(frame, self.target.modules)
						# self.tabWidgetStruct.cmbModules.addItem(
						# 	frame.GetModule().GetFileSpec().GetFilename() + " (" + str(
						# 		frame.GetFrameID()) + ")")
						self.logDbgC.emit(f"loadTarget() => Frame: {frame} ...", DebugLevel.Verbose)
						if frame.GetModule().GetFileSpec().GetFilename() != self.target.GetExecutable().GetFilename():
							self.logDbgC.emit(f"Module for FileStruct IS NOT equal executable => continuing ...", DebugLevel.Verbose)
							continue
						else:
							self.logDbgC.emit(f"Module for FileStruct IS equal executable => scanning ...", DebugLevel.Verbose)

						if frame:
							self.logDbgC.emit(f"BEFORE DISASSEMBLE!!!!", DebugLevel.Verbose)
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
		self.target = self.driver.createTarget(filename, self.arch, self.args)

		if self.target.IsValid():
			self.mainWin.target = self.target
			self.logDbgC.emit(f"target: {self.target}", DebugLevel.Verbose)

			# for module in self.target.module_iter():
			# 	for compile_unit in module.compile_unit_iter():
			# 		for func in compile_unit:
			# 			if func.IsValid():
			# 				self.logDbgC.emit(f"Objective-C Function: {func.GetName()}")
			# for module in self.target.module_iter():
			# 	for section in module.section_iter():
			# 		if hasattr(section, 'symbol_in_section_iter'):
			# 			for symbol in module.symbol_in_section_iter(section):
			# 				if symbol.IsValid():
			# 					name = symbol.GetName()
			# 					start_addr = symbol.GetStartAddress().GetLoadAddress(self.target)
			# 					self.logDbgC.emit(f"------------------>>>>>>>>>>>>>Symbol: {name}, Address: {hex(start_addr)}", DebugLevel.Verbose)

			if self.mainWin.setHelper.getValue(SettingsValues.BreakpointAtMainFunc):
				self.driver.debugger.HandleCommand('process launch --stop-at-entry')

				# if len(self.driver.getTarget().modules) > 0:
				# 	self.logDbg.emit(f"self.driver.getTarget().GetModuleAtIndex(0) (len: {len(self.driver.getTarget().modules)}): {self.driver.getTarget().GetModuleAtIndex(0)}")
				# 	for idxMod in range(len(self.driver.getTarget().modules)):
				# 		self.logDbg.emit(
				# 			f"- self.driver.getTarget().GetModuleAtIndex({idxMod}): {self.driver.getTarget().GetModuleAtIndex(idxMod)}")

				# for module in self.target.module_iter():
				# 	for section in module.section_iter():
				# 		for symbol in section.symbol_in_section_iter(section):
				#
				# 			if symbol.IsValid():
				# 				# self.logDbgC.emit(f"Symbol: {symbol.GetName()}, Address: {hex(symbol.GetStartAddress().GetLoadAddress(self.target))}",DebugLevel.Verbose)
				# 				name = symbol.GetName()
				# 				# start_addr = symbol.GetStartAddress().GetLoadAddress(self.target)
				# 				self.logDbgC.emit(f"===================>>>>>>>>>>>>> Symbol: {name}, Address: hex(start_addr)", DebugLevel.Verbose)
				# for module in self.target.module_iter():
				# 	for section in module.section_iter():
				# 		if hasattr(section, 'symbol_in_section_iter'):
				# 			for symbol in module.symbol_in_section_iter(section):
				# 				if symbol.IsValid():
				# 					name = symbol.GetName()
				# 					start_addr = symbol.GetStartAddress().GetLoadAddress(self.target)
				# 					self.logDbgC.emit(
				# 						f"------------------>>>>>>>>>>>>>Symbol: {name}, Address: {hex(start_addr)}",
				# 						DebugLevel.Verbose)

				main_oep, symbol = find_main(self.driver.debugger)
				if self.mainWin.setHelper.getValue(SettingsValues.BreakpointAtMainFunc):
					# self.driver.debugger.HandleCommand(f'breakpoint set -a {hex(main_oep)} -N kimon')
					bp = self.driver.getTarget().BreakpointCreateByAddress(main_oep) # .BreakpointCreateByName("main")
					for bl in bp:
						self.logDbgC.emit(f"bl.location: {bl}", DebugLevel.Verbose)
					self.driver.mainID = bp.GetID()
					self.driver.debugger.HandleCommand(f'br name add -N main {bp.GetID()}')
					bp.SetScriptCallbackFunction("main_hit")
					self.logDbgC.emit(f'breakpoint set "main": {bp}', DebugLevel.Verbose)
					# self.driver.debugger.HandleCommand('breakpoint set --name main')

				# Set breakpoint on scanf
				if	self.mainWin.setHelper.getValue(SettingsValues.AutoBreakpointForScanf):
					bp = self.driver.getTarget().BreakpointCreateByName("scanf")
					for bl in bp:
						self.logDbgC(f"bl.location: {bl}", DebugLevel.Verbose)
						
					self.driver.scanfID = bp.GetID()
					self.driver.debugger.HandleCommand(f'br name add -N scanf {bp.GetID()}')
					bp.SetScriptCallbackFunction("on_scanf_hit")
					self.logDbgC.emit(f'breakpoint set "scanf": {bp}', DebugLevel.Verbose)

				self.driver.debugger.HandleCommand('breakpoint set --name main')
				# self.driver.debugger.HandleCommand(f'br list')
				self.driver.debugger.HandleCommand('process continue')

			self.loadTarget()
		else:
			self.logDbgC.emit(f"Error creating target!!!", DebugLevel.Verbose)