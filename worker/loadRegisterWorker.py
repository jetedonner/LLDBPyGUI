#!/usr/bin/env python3
from worker.baseWorker import *
from dbg.memoryHelper import *
#from helper.dbgHelper import *

#class LoadRegisterWorkerReceiver(BaseWorkerReceiver):
#	interruptWorker = pyqtSignal()
	
class LoadRegisterWorkerSignals(BaseWorkerSignals):
	loadRegister = pyqtSignal(str)
	loadRegisterValue = pyqtSignal(int, str, str, str)
	updateRegisterValue = pyqtSignal(int, str, str, str)
	loadVariableValue = pyqtSignal(str, str, str, str, str)
	updateVariableValue = pyqtSignal(str, str, str, str, str)
	

class LoadRegisterWorker(BaseWorker):
	
	initTabs = True
	
	def __init__(self, driver, initTabs = True):
		super(LoadRegisterWorker, self).__init__(driver)
		self.initTabs = initTabs
		
		self.signals = LoadRegisterWorkerSignals()
		
	def workerFunc(self):
		super(LoadRegisterWorker, self).workerFunc()
		
		self.sendStatusBarUpdate("Reloading registers ...")
		target = self.driver.getTarget()
		process = target.GetProcess()
		if process:
			thread = process.GetThreadAtIndex(0)
			if thread:
				frame = self.driver.getFrame()
#				frame = thread.GetFrameAtIndex(0)
				if frame:
					registerList = thread.GetFrameAtIndex(0).GetRegisters()
					numRegisters = registerList.GetSize()
					numRegSeg = 100 / numRegisters
					currReg = 0
					for value in registerList:
						currReg += 1
						currRegSeg = 100 / numRegisters * currReg
						self.sendProgressUpdate(100 / numRegisters * currReg, f'Loading registers for {value.GetName()} ...')
						if self.initTabs:
							self.signals.loadRegister.emit(value.GetName())
							
						numChilds = len(value)
						idx = 0
						for child in value:
							idx += 1
							self.sendProgressUpdate((100 / numRegisters * currReg) + (numRegSeg / numChilds * idx), f'Loading registers value {child.GetName()} ...')
							if self.initTabs:
								self.signals.loadRegisterValue.emit(currReg - 1, child.GetName(), child.GetValue(), getMemoryValueAtAddress(target, process, child.GetValue()))
							else:
								self.signals.updateRegisterValue.emit(currReg - 1, child.GetName(), child.GetValue(), getMemoryValueAtAddress(target, process, child.GetValue()))
					
					QCoreApplication.processEvents()
					
					
					# Load VARIABLES
					idx = 0
					vars = frame.GetVariables(True, True, True, False)  # type of SBValueList
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
							if(var.GetValue() == None):
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
							
						if self.initTabs:
#							if idx == 2:
#								error = lldb.SBError()
#								wp = var.Watch(False, True, False, error)
#								print(f'wp({idx}) => {wp}')
							
							self.signals.loadVariableValue.emit(str(var.GetName()), str(string_value), str(data), str(var.GetTypeName()), hex(var.GetLoadAddress()))
						else:
							self.signals.updateVariableValue.emit(str(var.GetName()), str(string_value), str(data), str(var.GetTypeName()), hex(var.GetLoadAddress()))
						idx += 1
					
					QCoreApplication.processEvents()
						
		pass
		
	def char_array_to_string(self, char_array_value):
		byte_array = char_array_value.GetPointeeData(0, char_array_value.GetByteSize())
		error = lldb.SBError()
		sRet = byte_array.GetString(error, 0)
		return "" if sRet == 0 else sRet