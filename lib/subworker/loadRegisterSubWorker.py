import lldb
from PyQt6.QtCore import pyqtSignal

from helper.memoryHelper import getMemoryValueAtAddress
from lib.subworker.baseSubWorker import BaseSubWorker, SubWorkerType, SubWorkerCommands


class LoadRegisterSubWorker(BaseSubWorker):
	subwkrType = SubWorkerType.LOAD_REGISTER_SUBWORKER

	loadRegisterCallback = pyqtSignal(str)
	loadRegisterValueCallback = pyqtSignal(int, str, str, str)
	updateRegisterValueCallback = pyqtSignal(int, str, str, str)
	loadVariableValueCallback = pyqtSignal(str, str, str, str, str)
	updateVariableValueCallback = pyqtSignal(str, str, str, str, str)

	def __init__(self, driver):
		super(LoadRegisterSubWorker, self).__init__(driver)

		self.subwkrCmds = {SubWorkerCommands.LOAD_REGISTER_SUBWORKER_CMD: self.loadRegister}

	def runSubWorker(self, driver, *argv, **args):
		super().runSubWorker(driver, *argv, **args)
		# self.target = self.driver.debugger.GetSelectedTarget()
		# self.process = self.target.GetProcess()
		# self.thread = self.process.GetThreadAtIndex(0)
		# print(driver)
		# self.logDbgC.emit(f"loadRegister runSubWorker => args: {args} ...", DebugLevel.Verbose)
		initTabs = True
		if args:  # and args["initTabs"]:
			initTabs = bool(args["initTabs"])
		self.loadRegister(initTabs)

	def loadRegister(self, initTabs=True):
		# if not initTabs:
		#     self.initSubWorker(self.driver)

		# self.logDbgC.emit(f"loadRegister({initTabs}) (2) ...", DebugLevel.Verbose)
		if self.process:
			# self.logDbgC.emit(f"loadRegister({initTabs}) => if self.process: ...", DebugLevel.Verbose)
			if self.thread:
				# self.logDbgC.emit(f"loadRegister({initTabs}) => if self.thread: ...", DebugLevel.Verbose)
				self.frame = self.thread.GetFrameAtIndex(0)
				if self.frame:
					# self.logDbgC.emit(f"loadRegister({initTabs}) => if self.frame: ...", DebugLevel.Verbose)

					registerList = self.frame.GetRegisters()
					# numRegisters = registerList.GetSize()
					# numRegSeg = 100 / numRegisters
					currReg = 0
					for value in registerList:
						currReg += 1
						# currRegSeg = 100 / numRegisters * currReg
						if initTabs:
							self.loadRegisterCallback.emit(value.GetName())

						# numChilds = len(value)
						idx = 0
						for child in value:
							idx += 1
							if initTabs:
								# self.logDbgC.emit(f"Try to load registers (1) idx: {idx} ... ", DebugLevel.Verbose)
								self.loadRegisterValueCallback.emit(currReg - 1, child.GetName(), child.GetValue(),
																	getMemoryValueAtAddress(self.target, self.process,
																							child.GetValue()))
							else:
								# self.logDbgC.emit(f"Try to update registers (1) idx: {idx} => {getMemoryValueAtAddress(self.target, self.process, child.GetValue())} / {child.GetValue()}... ", DebugLevel.Verbose)
								self.updateRegisterValueCallback.emit(currReg, child.GetName(), child.GetValue(),
																	  getMemoryValueAtAddress(self.target, self.process,
																							  child.GetValue()))

					# Load VARIABLES
					idx = 0
					# frame.GetVariables(True, True, False, True)
					vars = self.frame.GetVariables(True, True, True, False)  # type of SBValueList
					for var in vars:
						data = ""
						string_value = var.GetValue()
						if var.GetTypeName() == "int":
							if (var.GetValue() == None):
								continue
							string_value = str(string_value)
							data = hex(int(var.GetValue()))
						if var.GetTypeName().startswith("char"):
							string_value = self.char_array_to_string(var)
							data = var.GetPointeeData(0, var.GetByteSize())

						if initTabs:
							# self.logDbgC.emit(f"Try to load variable (2) ... ", DebugLevel.Verbose)
							self.loadVariableValueCallback.emit(str(var.GetName()), str(string_value), str(data),
																str(var.GetTypeName()), hex(var.GetLoadAddress()))
						else:
							# self.logDbgC.emit(f"Try to update variable (2) ... ", DebugLevel.Verbose)
							self.updateVariableValueCallback.emit(str(var.GetName()), str(string_value), str(data),
																  str(var.GetTypeName()), hex(var.GetLoadAddress()))
						idx += 1
		pass

	def char_array_to_string(self, char_array_value):
		byte_array = char_array_value.GetPointeeData(0, char_array_value.GetByteSize())
		error = lldb.SBError()
		sRet = byte_array.GetString(error, 0)
		return "" if sRet == 0 else sRet
