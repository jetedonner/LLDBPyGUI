import lldb
from PyQt6.QtCore import pyqtSignal

from constants import JMP_MNEMONICS, JMP_MNEMONICS_EXCLUDE
from helper.debugHelper import DebugLevel
from lib.fileInfos import detect_objc, is_hex_string
from lib.listener import LLDBListener
from lib.settings import SettingsHelper
from lib.subworker.baseSubWorker import BaseSubWorker, SubWorkerType, SubWorkerCommands
from lib.thirdParty.lldbutil import value_type_to_str
from lib.utils import random_qcolor
from ui.customQt.QControlFlowWidget import QControlFlowWidget


class AnalyzeCompleteFileSubWorker(BaseSubWorker):
	subwkrType = SubWorkerType.ANALYZE_COMPLETE_FILE_SUBWORKER

	loadModulesCallback = pyqtSignal(object, object)
	loadModulesCallback2 = pyqtSignal(object)
	loadInstructionCallback = pyqtSignal(object, object)
	loadStringCallback = pyqtSignal(str, int, str)
	loadSymbolCallback = pyqtSignal(str)
	loadActionCallback = pyqtSignal(object)
	loadSymbolCallbackNG = pyqtSignal(dict)
	finishedLoadInstructionsCallback = pyqtSignal(object, str, object, int, list)

	handle_processEvent = None

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

	# main_oep = 0x0

	def __init__(self, driver):
		super(AnalyzeCompleteFileSubWorker, self).__init__(driver)

		self.subwkrCmds = {SubWorkerCommands.ANALYZE_COMPLETE_FILE_SUBWORKER_CMD: self.analyzeCompleteFile}

		# self.allSubWorkers = {}
		self.allInstructions = []
		self.allModsAndInstructions = {}
		self.connections = []
		self.radius = 15
		# self.main_oep = 0x0

	def runSubWorker(self, driver, *argv, **args):
		super().runSubWorker(driver, *argv, **args)
		# self.getFileInfos()
		self.analyzeCompleteFile(False, "")
		if driver:
			self.driver = driver
		self.driver.target = self.target
		self.driver.process = self.process
		self.driver.thread = self.thread
		self.driver.module = self.module
		self.driver.frame = self.frame

	def analyzeCompleteModule(self, reloadModuleName=""):
		self.logDbgC.emit(f"ANALYZE_COMPLETE_MODULE_SUBWORKER_CMD INSIDE: {reloadModuleName} ...")
		self.analyzeCompleteFile(True, reloadModuleName)
		# if driver:
		#     self.driver = driver
		self.driver.target = self.target
		self.driver.process = self.process
		self.driver.thread = self.thread
		self.driver.module = self.module
		self.driver.frame = self.frame
		pass

	def analyzeCompleteFile(self, reloadASM=False, reloadASMFilename=""):
		self.allSymbols.clear()
		idx = 0
		print(f"============ NEW DISASSEMBLER ===============")
		self.logDbgC.emit(f"============ NEW DISASSEMBLER ===============", DebugLevel.Verbose)
		self.logDbgC.emit(f"loadTarget() => Target: {self.target} ...", DebugLevel.Verbose)
		if self.target:
			self.process = self.target.GetProcess()
			self.logDbgC.emit(f"PROCESS IS: {self.process}", DebugLevel.Verbose)

			if self.process:
				self.listener = LLDBListener(self.process, self.driver.debugger)
				self.listener.setHelper = SettingsHelper()  # self.setHelper
				# self.listener.breakpointEvent.connect(self.handle_breakpointEvent)
				self.listener.processEvent.connect(self.handle_processEvent)
				# self.listener.gotEvent.connect(self.handle_gotNewEvent)
				self.listener.addListenerCalls()
				self.listener.start()

				self.thread = self.process.GetThreadAtIndex(0)

				if self.thread:
					self.isInsideTextSectionGetRangeVarsReady()
					for z in range(self.thread.GetNumFrames()):
						frame = self.thread.GetFrameAtIndex(z)
						if reloadASM:
							if frame.GetModule().GetFileSpec().GetFilename() == reloadASMFilename:
								self.logDbgC.emit(
									f"Reload ASM called with filename: {reloadASMFilename} / frame: {frame}",
									DebugLevel.Verbose)
								break
						else:
							self.logDbgC.emit(f"Reload ASM called with filename: {reloadASMFilename} / frame: {frame}",
											  DebugLevel.Verbose)
						self.loadModulesCallback.emit(frame, self.target.modules)
						if frame.GetModule().GetFileSpec().GetFilename() != self.target.GetExecutable().GetFilename():
							continue
						else:
							self.module = frame.GetModule()
							self.loadModulesCallback2.emit(self.module)
							for var in frame.GetVariables(True,  # arguments
														  True,  # locals
														  False,  # statics
														  False):  # in_scope_only
								print(
									f"============>>>>>>>>>>>> Name: {var.GetName()}, Type: {var.GetType().GetName()}, ValueType: {value_type_to_str(var.GetValueType())}")
							# for cu in self.module.compile_unit_iter():
							#     for line_entry in cu:
							#         sc = self.target.ResolveSymbolContextForAddress(line_entry.GetStartAddress(), lldb.eSymbolContextVariable)
							#         for var in sc.GetVariables():
							#             print(f"===========>>>>>>>>>>>> Variable: {var.GetName()}, Type: {var.GetType().GetName()} !!!!!!!!!!!!!")

							# isObjectiveCFile = is_objc_app(self.target)
							# lang = detect_language_by_symbols(self.target, self.module)

							isObjC = detect_objc(self.module)

							for section in self.module.section_iter():
								# self.logDbgC.emit(f"section.GetName(): {section.GetName()}", DebugLevel.Verbose)
								if section.GetName() == "__TEXT":  # or  section.GetName() == "__PAGEZERO":
									idxInstructions = 0

									for subsec in section:
										# self.logDbgC.emit(f"subsec.GetName(): {subsec.GetName()}", DebugLevel.Verbose)
										if subsec.GetName() == "__text" or subsec.GetName() == "__stubs" or subsec.GetName() == "__objc_stubs":
											idxSym = 0
											lstSym = self.module.symbol_in_section_iter(subsec)
											if subsec.GetName() == "":
												continue

											if subsec.GetName() == "__text" or subsec.GetName() == "__stubs" or subsec.GetName() == "__objc_stubs":
												self.loadSymbolCallback.emit(subsec.GetName())
												idxSym += 1

											print(f"lstSym: {lstSym} ...")
											for smbl in lstSym:
												print(f"smbl: {smbl} ...")
												symblInIns = {"symbol": smbl.GetName(), "addSym": True,
															  "row": smbl.GetStartAddress().GetLoadAddress(self.target)}
												self.allSymbols.append(symblInIns)
												self.loadSymbolCallbackNG.emit(symblInIns)
												# self.logDbgC.emit(f"===========>>>>>>>>>>> symbl: {smbl}", DebugLevel.Verbose)
												if isObjC and (
														not subsec.GetName() == "__stubs" and not subsec.GetName() == "__objc_stubs"):
													self.loadSymbolCallback.emit(smbl.GetName())
												elif not subsec.GetName() == "__stubs" and not subsec.GetName() == "__objc_stubs":
													self.loadSymbolCallback.emit(smbl.GetName())
													# self.logDbgC.emit(f"smbl.GetName(): {smbl.GetName()} ...", DebugLevel.Verbose)
													# self.loadSymbolCallbackNG.emit({"symbol": smbl.GetName(), "addSym": True})

												instructions = smbl.GetStartAddress().GetFunction().GetInstructions(
													self.target)
												self.allInstructions += instructions
												self.allModsAndInstructions[subsec.GetName()] = instructions
												for instruction in instructions:
													actCall = self.checkForSetActionCall(instruction)
													print(f"actCall: {actCall}")

													if actCall["result"]:
														self.actionCalls.append(actCall["data"])
														self.loadActionCallback.emit(actCall["data"])

													self.loadInstructionCallback.emit(instruction, self.target)
													idxInstructions += 1
												idxSym += 1

											if subsec.GetName() == "__stubs" or subsec.GetName() == "__objc_stubs":
												start_addr = subsec.GetLoadAddress(self.target)
												size = subsec.GetByteSize()
												estimated_count = size // 4
												instructions = self.target.ReadInstructions(
													lldb.SBAddress(start_addr, self.target),
													int(estimated_count))
												self.allInstructions += instructions
												idxStubInsts = 0
												oldSymbolName = ""
												for instruction in instructions:
													if idxStubInsts == 0:
														oldSymbolName = instruction.GetAddress().symbol.GetName()
														self.loadSymbolCallback.emit(oldSymbolName)
													else:
														if instruction.GetAddress().symbol.GetName() is None:
															continue

														# print(f"if oldSymbolName != instruction.GetAddress().symbol.GetName():: {instruction.GetAddress().symbol.GetName():} ...")
														if oldSymbolName != instruction.GetAddress().symbol.GetName():
															oldSymbolName = instruction.GetAddress().symbol.GetName()
															self.loadSymbolCallback.emit(oldSymbolName)

													actCall = self.checkForSetActionCall(instruction)
													print(f"actCall: {actCall}")
													if actCall["result"]:
														self.actionCalls.append(actCall["data"])
														self.loadActionCallback.emit(actCall["data"])
													self.loadInstructionCallback.emit(instruction, self.target)
													idxStubInsts += 1
													idxInstructions += 1
												continue
										elif subsec.GetName() == "__cstring":
											# if isObjC:
											self.loadSymbolCallback.emit(subsec.GetName())
											# addr = subsec.GetLoadAddress(self.target)  # .GetStartAddress()
											# start_addr = subsec.GetStartAddress()
											addr = subsec.GetLoadAddress(self.target)
											# addr = start_addr.GetLoadAddress(self.target)

											if addr == lldb.LLDB_INVALID_ADDRESS:
												self.logDbgC.emit("Invalid load address for __cstring",
																  DebugLevel.Verbose)
												# return
												continue

											# Double check !!!
											# resolved_addr = self.target.ResolveLoadAddress(addr)
											# print(f"Resolved __cstring address: {resolved_addr}")

											size = subsec.GetByteSize()
											error = lldb.SBError()
											data = self.target.GetProcess().ReadMemory(addr, size, error)

											if error.Success():
												offset = 0
												while offset < len(data):
													end = data.find(b'\x00', offset)
													if end == -1:
														break
													raw = data[offset:end]
													try:
														if raw == b'' or raw == b'\x00':
															continue
														decoded = raw.decode('utf-8')
														string_addr = addr + offset
														self.loadStringCallback.emit(hex(string_addr), idxInstructions,
																					 decoded)
														idxInstructions += 1
													except UnicodeDecodeError:
														pass
													offset = end + 1
												# # print(f"data: {data} ...")
												# # print(data)
												# strings = data.split(b'\x00')
												# curAddr = addr
												# print(f"len(strings): {strings} ...")
												# for i, s in enumerate(strings):
												#     print(f"for {i}, {s} in enumerate(strings): ...")
												#     if i + 1 >= len(strings):
												#         break
												#     # idxInstructions += 1
												#     try:
												#         decoded = s.decode('utf-8')
												#         print(f"for {i}, {s} in enumerate(strings): => decoded: {decoded} ...")
												#         # if decoded == "":
												#         #     curAddr += len(decoded) + 1
												#         #     continue
												#         # self.logDbgC.emit(f"{hex(curAddr)}: [{i}] {decoded}", DebugLevel.Verbose)
												#         self.loadStringCallback.emit(hex(curAddr), idxInstructions + i,
												#                                      decoded)
												#         curAddr += len(decoded) + 1
												#     except UnicodeDecodeError:
												#         continue
											else:
												self.logDbgC.emit(f"Failed to read memory: {error.GetCString()}",
																  DebugLevel.Verbose)
											pass
									break
						idx += 1
					self.logDbgC.emit(f"============ END DISASSEMBLER ===============", DebugLevel.Verbose)
					print(f"self.actionCalls: {self.actionCalls}")
					self.checkLoadConnection(self.allInstructions, self.actionCalls)

					for con in self.connections:
						self.logDbgC.emit(
							f"===>>> Connection: {hex(con.origAddr)} / {hex(con.destAddr)} => {con.origRow} / {con.destRow}",
							DebugLevel.Verbose)

					self.connections.sort(key=lambda x: abs(x.jumpDist), reverse=True)
					self.finishedLoadInstructionsCallback.emit(self.connections,
															   self.target.GetExecutable().GetFilename(),
															   self.allModsAndInstructions, self.getPC(),
															   self.allSymbols)

	oldComment = ""
	oldAction = ""
	actionCalls = []
	allSymbols = []
	allValidActiopnCalls = {}

	def checkForSetActionCall(self, instruction):
		comment = str(instruction.GetComment(self.target)).strip('"').strip(":")
		if comment == 'setAction' or comment == "objc_msgSend$setAction":
			self.oldAction = comment
			return {"result": False, "comment (1)": comment}
		if self.oldAction == "setAction" or self.oldAction == "objc_msgSend$setAction":
			newOldComment = self.oldComment
			self.logDbgC.emit(f"FOUND SETACTION: {newOldComment} !!!!", DebugLevel.Verbose)
			self.oldComment = ""
			newCallType = self.oldAction
			self.oldAction = ""
			print({"result": True, "data": {"callType": newCallType, "calledFunction": newOldComment,
											"callAddr": instruction.GetAddress().GetLoadAddress(self.target)}})
			return {"result": True, "data": {"callType": newCallType, "calledFunction": newOldComment,
											 "callAddr": instruction.GetAddress().GetLoadAddress(self.target)}}
		# else:
		self.oldAction = ""
		# else:
		self.oldComment = comment
		return {"result": False, "comment (2)": comment}

	def isInsideTextSectionGetRangeVarsReady(self, mod=None):
		self.thread = self.process.GetThreadAtIndex(0)
		if mod:
			module = mod
		else:
			module = self.thread.GetFrameAtIndex(0).GetModule()
		found = False
		for sec in module.section_iter():
			for idx3 in range(sec.GetNumSubSections()):
				subSec = sec.GetSubSectionAtIndex(idx3)
				if subSec.GetName() == "__text":
					self.startAddr = subSec.GetLoadAddress(self.target)  # .GetFileAddress()
				elif subSec.GetName() == "__stubs":
					self.endAddr = subSec.GetLoadAddress(
						self.target) + subSec.GetByteSize()  # .GetFileAddress() + subSec.GetByteSize()
					found = True
					# break
				elif subSec.GetName() == "__objc_stubs":
					self.endAddr = subSec.GetLoadAddress(
						self.target) + subSec.GetByteSize()  # .GetFileAddress() + subSec.GetByteSize()
					found = True
					# break
			if found:
				break
		print(
			f"self.startAddr: {hex(self.startAddr)} ({self.startAddr}) / self.endAddr: {hex(self.endAddr)} ({self.endAddr}) ...")

	def isInsideTextSection(self, addr):
		addrInt = int(addr, 16)
		# print(f"isInsideTextSection => addr: {addr} ({addrInt}) ...")
		try:
			isInside = self.endAddr > addrInt >= self.startAddr
			# print(f"isInsideTextSection => addr: {addr} ({addrInt}) > isInside: {isInside} ...")
			return isInside
		except Exception as e:
			self.logDbgC.emit(f"Exception: {e}", DebugLevel.Error)
			return False

	def getPC(self, asHex=False):
		if self.frame:
			if asHex:
				return hex(self.frame.GetPC())
			else:
				return self.frame.GetPC()
		return ""

	def checkLoadConnection(self, instructions, actionCalls):
		print(f"actionCalls: {actionCalls} DEBUGME!!!!")
		if len(actionCalls) > 0:
			# for callType, callFunc in actionCalls:
			for actSym in actionCalls:
				if actSym["callType"] == "setAction" or actSym["callType"] == "objc_msgSend$setAction":
					for symb in self.allSymbols:
						if symb["symbol"] == f'-[AppDelegate {actSym["calledFunction"]}:]':
							rowInSym = symb['row']
							rowInSym2 = actSym['callAddr']
							print(
								f"FOUND {actSym['calledFunction']} / {rowInSym2} / {hex(rowInSym2)} / {rowInSym} / {hex(rowInSym)} => SYMBOLCALLADDRESS!!!!!")
							sAddrStartInt = rowInSym2
							sAddrJumpFrom = hex(rowInSym2)
							rowStart = int(self.get_line_number(
								sAddrStartInt))

							sAddrJumpTo = hex(rowInSym)
							lineEnd = None
							idx = 0
							for inst in instructions:  # self.allInstructions:
								if inst.GetAddress().GetLoadAddress(
										self.target) == rowInSym:
									lineEnd = idx
									break
								idx += 1
							if lineEnd is None:
								# self.logDbgC.emit(f"IS NOT OVER CONNECTION!!!! ==>> RETURN", DebugLevel.Verbose)
								continue
							# pass
							rowEnd = int(lineEnd)

							if (rowStart < rowEnd):
								newConObj = QControlFlowWidget.draw_flowConnection(rowStart, rowEnd,
																				   int(sAddrJumpFrom, 16),
																				   int(sAddrJumpTo, 16), None,
																				   random_qcolor(), self.radius, 1,
																				   False)  # self.window().txtMultiline.table
							else:
								newConObj = QControlFlowWidget.draw_flowConnection(rowStart, rowEnd,
																				   int(sAddrJumpFrom, 16),
																				   int(sAddrJumpTo, 16), None,
																				   random_qcolor(), self.radius, 1,
																				   True)
							newConObj.mnemonic = "callq"
							# self.logDbgC.emit(f"Connection (Branch) is a: {newConObj.mnemonic} / {sMnemonic})", DebugLevel.Verbose)
							if abs(newConObj.jumpDist / 2) <= (newConObj.radius / 2):
								newConObj.radius = newConObj.jumpDist / 2
							self.connections.append(newConObj)
							if self.radius <= 130:
								self.radius += 15
							break

		for instruction in instructions:  # self.allInstructions:
			sMnemonic = instruction.GetMnemonic(self.target)

			if sMnemonic is not None and sMnemonic.startswith(JMP_MNEMONICS) and not sMnemonic.startswith(
					JMP_MNEMONICS_EXCLUDE):
				sAddrJumpTo = instruction.GetOperands(self.target)
				# self.logDbgC.emit(f"checkLoadConnection()..... {instruction} ===>>> JumpTo: {sAddrJumpTo}", DebugLevel.Verbose)

				# Handling special case for "cbnz" and "cbz" where operands are like "w8, 0x100003e2c"
				if sMnemonic == "cbnz" or sMnemonic == "cbz":
					sAddrJumpTo = sAddrJumpTo.split(",")[1].strip()

				if sAddrJumpTo is None or not is_hex_string(sAddrJumpTo):
					self.logDbgC.emit(f"checkLoadConnection() sAddrJumpTo not valid ... sAddrJumpTo: {sAddrJumpTo}",
									  DebugLevel.Verbose)
					continue

				bOver = self.startAddr < int(sAddrJumpTo, 16) < self.endAddr
				# if bOver:
				# 	self.logDbgC.emit(
				# 		f"checkLoadConnection()..... sAddrJumpTo IS INSIDE ALTERNATIVE: {sAddrJumpTo} / end: {hex(self.endAddr)} / start: {hex(self.startAddr)}", DebugLevel.Verbose)
				# 	# pass

				addr = instruction.GetAddress()
				load_addr = addr.GetLoadAddress(self.target)
				file_addr = addr.GetFileAddress()
				delta_addr = load_addr - file_addr
				delta_addrHex = hex(delta_addr)
				# print(
				# 	f"Delta (slide): {delta_addrHex} / {delta_addr} / addr: {addr} / load_addr: {load_addr} ({hex(load_addr)}) / sAddrJumpTo: {sAddrJumpTo} ====>>>>> DELTAADDR")


				# print(f"Load Address: {hex(load_addr)}")
				# print(f"File Address: {hex(file_addr)}")
				# print(f"Delta (slide): {hex(load_addr - file_addr)}")

				isInside = self.isInsideTextSection(sAddrJumpTo)
				if isInside or bOver:
					if isInside:
						# self.logDbgC.emit(f"IS NOT OVER CONNECTION!!!!", DebugLevel.Verbose)
						sAddrStartInt = int(str(instruction.GetAddress().GetLoadAddress(self.target)), 10)
						sAddrJumpFrom = hex(sAddrStartInt)
						lineNum = self.get_line_number(sAddrStartInt)
						if not lineNum:
							continue
						rowStart = int()  # idxInstructions#int(self.get_line_number(int(sAddrJumpFrom, 16)))
						# lineEnd = self.get_line_number(int(sAddrJumpTo, 16))
						lineEnd = None
						idx = 0
						for inst in instructions:  # self.allInstructions:
							if inst.GetAddress().GetLoadAddress(self.target) == instruction.GetAddress().GetLoadAddress(
									self.target):
								lineEnd = idx
								break
							idx += 1
						if lineEnd is None:
							# self.logDbgC.emit(f"IS NOT OVER CONNECTION!!!! ==>> RETURN", DebugLevel.Verbose)
							continue
						# pass
						rowEnd = int(lineEnd)
						self.logDbgC.emit(
							f"Found connection from line: {rowStart} to: {rowEnd} ({sAddrJumpFrom} / {sAddrJumpTo})",
							DebugLevel.Verbose)
					elif bOver:
						# self.logDbgC.emit(f"IS OVER CONNECTION!!!!", DebugLevel.Verbose)
						sAddrStartInt = int(str(instruction.GetAddress().GetLoadAddress(self.target)),
											10)  # int(str(instruction.GetAddress().GetLoadAddress(self.target)), 10)
						sAddrJumpFrom = hex(sAddrStartInt)
						rowStart = int(self.get_line_number(
							sAddrStartInt))  # idxInstructions#int(self.get_line_number(int(sAddrJumpFrom, 16)))
						# # lineEnd = self.get_line_number(int(sAddrJumpTo, 16))
						# lineEnd = self.txtMultiline.table.getLineNum(sAddrJumpTo)
						# if lineEnd is None:
						#     # self.logDbgC.emit(f"IS OVER CONNECTION!!!! ==>> RETURN", DebugLevel.Verbose)
						#     continue
						# # pass
						# DIRTY LITTLE HACK ==>>> Amend asap!!!
						continue
						rowEnd = int(lineEnd)
						self.logDbgC.emit(
							f"Found connection from line: {rowStart} to: {rowEnd} ({sAddrJumpFrom} / {sAddrJumpTo})",
							DebugLevel.Verbose)

					if (rowStart < rowEnd):
						newConObj = QControlFlowWidget.draw_flowConnection(rowStart, rowEnd, int(sAddrJumpFrom, 16),
																		   int(sAddrJumpTo, 16), None,
																		   random_qcolor(), self.radius, 2,
																		   False)  # self.window().txtMultiline.table
					else:
						newConObj = QControlFlowWidget.draw_flowConnection(rowStart, rowEnd, int(sAddrJumpFrom, 16),
																		   int(sAddrJumpTo, 16), None,
																		   random_qcolor(), self.radius, 2, True)
					newConObj.deltaAddr = delta_addr
					# newConObj.origAddr += delta_addrHex
					newConObj.destAddr += delta_addr
					if newConObj.destAddr >= 0x200033E84:
						newConObj.destAddr -= delta_addr
					newConObj.mnemonic = sMnemonic
					# self.logDbgC.emit(f"Connection (Branch) is a: {newConObj.mnemonic} / {sMnemonic})", DebugLevel.Verbose)
					if abs(newConObj.jumpDist / 2) <= (newConObj.radius / 2):
						newConObj.radius = newConObj.jumpDist / 2
					self.connections.append(newConObj)
					if self.radius <= 130:
						self.radius += 15
				else:
					self.logDbgC.emit(f"checkLoadConnection()..... sAddrJumpTo '{sAddrJumpTo}' NOT in target",
									  DebugLevel.Verbose)
				# self.connections.sort(key=lambda x: abs(x.jumpDist), reverse=True)

	def get_line_number(self, address_int):
		addr = lldb.SBAddress(address_int, self.target)

		context = self.target.ResolveSymbolContextForAddress(
			addr,
			lldb.eSymbolContextEverything
		)

		line_entry = context.GetLineEntry()
		if line_entry.IsValid():
			# file_spec = line_entry.GetFileSpec()
			line = line_entry.GetLine()
			# print(f"📍 Address 0x{address_int:x} maps to {file_spec.GetFilename()}:{line}")
			return line  # file_spec.GetFilename(),
		else:
			print("❌ No line info found for this address.")
		return None
