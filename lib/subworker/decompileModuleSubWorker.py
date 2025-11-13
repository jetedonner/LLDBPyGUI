import lldb
from PyQt6.QtCore import pyqtSignal

from helper.debugHelper import DebugLevel
from lib.subworker.baseSubWorker import BaseSubWorker, SubWorkerType, SubWorkerCommands


class DecompileModuleSubWorker(BaseSubWorker):
	subwkrType = SubWorkerType.DECOMPILE_MODULE_SUBWORKER

	loadStringCallback = pyqtSignal(str, int, str)

	show_dialog = pyqtSignal()
	loadInstructionCallback = pyqtSignal(object, object)
	loadSymbolCallback = pyqtSignal(str)
	loadModulesCallback2 = pyqtSignal(object)
	finishedLoadModuleCallback = pyqtSignal(object, str, list)

	# handle_processEvent = None

	debugger = None
	target = None
	process = None
	thread = None
	frame = None
	module = None

	startAddr = 0
	endAddr = 0
	rowStart = 0
	rowEnd = 0

	allInstructions = []
	allModsAndInstructions = {}
	connections = []
	radius = 15

	def __init__(self, driver):
		super(DecompileModuleSubWorker, self).__init__(driver)

		self.subwkrCmds = {SubWorkerCommands.DECOMPILE_MODULE_SUBWORKER_CMD: self.runSubWorker}

		# self.allSubWorkers = {}
		self.allInstructions = []
		self.allModsAndInstructions = {}
		self.connections = []
		self.radius = 15
		self.modulePath = ""
		# self.main_oep = 0x0

	def runSubWorker(self, driver, *argv, **args):
		super().runSubWorker(driver, *argv, **args)
		self.modulePath = ""
		if args:  # and args["initTabs"]:
			self.modulePath = str(args["modulePath"])
		self.disassemble_entire_target(driver.target)

	allSymbols = []

	def disassemble_entire_target(self, target):

		self.show_dialog.emit()
		self.allSymbols = []
		self.allInstructions = []
		self.allModsAndInstructions = {}
		self.connections = []
		self.radius = 15

		print(f"DecompileModuleSubWorker.disassemble_entire_target() => self.modulePath: {self.modulePath} ...")
		for module in self.target.module_iter():
			if module.GetFileSpec().fullpath != self.modulePath:
				continue
			else:
				print(
					f"DecompileModuleSubWorker.disassemble_entire_target() => module.GetFileSpec().fullpath: {module.GetFileSpec().fullpath} / {self.modulePath}....")
				self.driver.parentDriver.projectData.addModule(module.GetFileSpec().fullpath)
				self.loadModulesCallback2.emit(module)
				for section in module.section_iter():
					if section.GetName() == "__TEXT":  # or  section.GetName() == "__PAGEZERO":
						idxInstructions = 0

						for subsec in section:
							if subsec.GetName() == "__text" or subsec.GetName() == "__stubs":  # or subsec.GetName() == "__cstring":
								self.loadSymbolCallback.emit(subsec.GetName())

								# idxSym = 0
								lstSym = module.symbol_in_section_iter(subsec)
								for sym in lstSym:
									if not sym.IsValid():
										continue
									symblInIns = {"symbol": sym.GetName(), "addSym": True,
												  "row": sym.GetStartAddress().GetLoadAddress(self.target)}
									self.allSymbols.append(symblInIns)
									instructions = sym.GetInstructions(self.target)
									if instructions.GetSize() == 0:
										continue
									self.allInstructions += instructions

									self.loadSymbolCallback.emit(sym.GetName())
									for inst in instructions:
										comment = inst.GetComment(self.target)
										print(f"comment (1): {comment} / {self.target} ...")
										print(f"inst: {inst} ...")
										self.loadInstructionCallback.emit(inst, self.target)
								# pass
							elif subsec.GetName() == "__cstring":
								# if isObjC:
								self.loadSymbolCallback.emit(subsec.GetName())
								addr = subsec.GetLoadAddress(self.target)  # .GetStartAddress()
								size = subsec.GetByteSize()
								error = lldb.SBError()
								data = self.target.GetProcess().ReadMemory(addr, size, error)

								if error.Success():
									strings = data.split(b'\x00')
									curAddr = addr
									for i, s in enumerate(strings):
										if i >= len(strings) - 1:
											break
										# idxInstructions += 1
										try:
											if s == b'' or s == b'\x00':
												continue
											decoded = s.decode('utf-8')
											# self.logDbgC.emit(f"{hex(curAddr)}: [{i}] {decoded}", DebugLevel.Verbose)
											self.loadStringCallback.emit(hex(curAddr), idxInstructions + i,
																		 decoded)
											curAddr += len(decoded) + 1
										except UnicodeDecodeError:
											continue
								else:
									self.logDbgC.emit(f"Failed to read memory: {error.GetCString()}",
													  DebugLevel.Verbose)

				print(f"self.allInstructions=> {len(self.allInstructions)}")
				print(self.allInstructions)
				# self.driver.acfSubWkr.
				# acfsw = AnalyzeCompleteFileSubWorker(self.driver)
				# acfsw.driver = self.driver
				# acfsw.target = self.target
				# acfsw.process = self.process
				# acfsw.logDbgC = self.logDbgC
				# acfsw.isInsideTextSectionGetRangeVarsReady()
				# acfsw.checkLoadConnection(self.allInstructions, [])
				acfsw = self.driver.parentDriver.acfSubWkr  # AnalyzeCompleteFileSubWorker(self.driver)
				acfsw.driver = self.driver
				acfsw.target = self.target
				acfsw.process = self.process
				# acfsw.logDbgC = self.logDbgC
				acfsw.connections = []
				acfsw.radius = 15
				acfsw.isInsideTextSectionGetRangeVarsReady(module)
				acfsw.checkLoadConnection(self.allInstructions, [])
				print(f"len(acfsw.connections): {len(acfsw.connections)}")
				self.finishedLoadModuleCallback.emit(acfsw.connections, module.GetFileSpec().GetFilename(),
													 self.allSymbols)
				break
