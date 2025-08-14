import lldb
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

from config import JMP_MNEMONICS, JMP_MNEMONICS_EXCLUDE
from dbg.fileInfos import is_objc_app, detect_language_by_symbols, detect_objc, GetFileHeader, is_hex_string
from dbg.listener import LLDBListener
from dbg.memoryHelper import getMemoryValueAtAddress
from lib.settings import SettingsHelper
from lib.utils import random_qcolor
from ui.customQt.QControlFlowWidget import QControlFlowWidget
from ui.helper.dbgOutputHelper import DebugLevel


class AttachWorker(QObject):

    show_dialog = pyqtSignal()
    finished = pyqtSignal()
    logDbg = pyqtSignal(str)
    logDbgC = pyqtSignal(str, object)
    loadModulesCallback = pyqtSignal(object, object)
    loadInstructionCallback = pyqtSignal(object)
    loadInstructionsCallback = pyqtSignal(object, object)
    loadStringCallback = pyqtSignal(str, int, str)
    loadSymbolCallback = pyqtSignal(str)
    loadCurrentPC = pyqtSignal(str)
    loadJSONCallback = pyqtSignal(str)
    loadFileInfosCallback = pyqtSignal(object, object)
    loadRegisterCallback = pyqtSignal(str)
    loadRegisterValueCallback = pyqtSignal(int, str, str, str)
    loadVariableValueCallback = pyqtSignal(str, str, str, str, str)
    finishedLoadInstructionsCallback = pyqtSignal(object, str, object)


    # Load Listener
    handle_breakpointEvent = None
    handle_processEvent = None
    handle_gotNewEvent = None

    attachThread = None
    _should_stop = False

    mainWin = None
    debugger = None
    pid = None
    name = None
    process = None
    target = None
    thread = None
    frame = None
    connections = []

    allInstructions = []
    allModsAndInstructions = {}
    initTable = True

    startAddr = 0x0
    endAddr = 0x10000000

    def __init__(self, debugger, pid=None, name=None, mainWin=None):
        super().__init__()
        self.mainWin = mainWin
        self.attachThread = None
        self._should_stop = False
        self.debugger = debugger
        self.pid = pid
        self.name = name
        self.process = None
        self.target = None
        self.thread = None
        self.frame = None
        self.exe = ""
        self.connections = []

        self.allInstructions = []
        self.allModsAndInstructions = {}
        self.initTable = True

    def run(self):
        self._should_stop = False
        self.show_dialog.emit()
        # Reset before starting
        self.attach_to_process()
        if self.process:

            # if self.process:
            self.listener = LLDBListener(self.process, self.debugger)
            self.listener.setHelper = SettingsHelper()# self.mainWin.setHelper
            self.listener.breakpointEvent.connect(self.handle_breakpointEvent)
            self.listener.processEvent.connect(self.handle_processEvent)
            self.listener.gotEvent.connect(self.handle_gotNewEvent)
            self.listener.addListenerCalls()
            self.listener.start()


            self.thread = self.process.GetThreadAtIndex(0)
            if self.thread:
                self.isInsideTextSectionGetRangeVarsReady()
                # for z in range(self.thread.GetNumFrames()):
                self.frame = self.thread.GetFrameAtIndex(0)
                self.loadModulesCallback.emit(self.frame, self.target.modules)

                self.disassemble_entire_target()

                self.logDbgC.emit(f"self.target.GetExecutable().GetFilename(): {self.target.GetExecutable().GetDirectory()}/{self.target.GetExecutable().GetFilename()}", DebugLevel.Verbose)
                self.exe = self.target.GetExecutable().GetDirectory() + "/" + self.target.GetExecutable().GetFilename()
                # self.targetBasename = os.path.basename(exe)
                mach_header = GetFileHeader(self.exe)
                self.logDbgC.emit(f"mach_header = GetFileHeader(exe): {mach_header}", DebugLevel.Verbose)
                self.loadFileInfosCallback.emit(mach_header, self.target)
                self.logDbgC.emit(f"after self.loadFileInfosCallback.emit(...)", DebugLevel.Verbose)
                QApplication.processEvents()

                self.loadRegisters()

                self.loadFileStats()

                self.finished.emit()

    def startWithPID(self, pid=-1, attachThread=None):
        self.pid = pid
        self.attachThread = attachThread
        self.attachThread.start()
        # self.attach_to_process()
        # if self.process:
        #     self.thread = self.process.GetThreadAtIndex(0)
        #     if self.thread:
        #         # for z in range(self.thread.GetNumFrames()):
        #         self.frame = self.thread.GetFrameAtIndex(0)
        #         self.loadModulesCallback.emit(self.frame, self.target.modules)

    def attach_to_process(self):#, debugger, pid=None, name=None):
        self.target = self.debugger.CreateTarget(None)
        if not self.target.IsValid():
            print("❌ Failed to create target.")
            return None

        error = lldb.SBError()
        self.process = None

        if self.pid:
            self.process = self.target.AttachToProcessWithID(self.debugger.GetListener(), self.pid, error)
        elif self.name:
            self.process = self.target.AttachToProcessWithName(self.debugger.GetListener(), self.name, False, error)
        else:
            print("⚠️ Provide either a PID or process name.")
            return None

        if error.Success() and self.process.IsValid():
            print(f"✅ Attached to process: {self.process.GetProcessID()}")
            return self.process
        else:
            print(f"❌ Failed to attach: {error.GetCString()}")
            return None

    def disassemble_entire_target(self):
        # self.list_external_symbols(self.target)
        self.logDbgC.emit(f"============ NEW DISASSEMBLER ===============", DebugLevel.Verbose)
        idx = 0
        self.connections = []
        self.allInstructions = []
        self.allModsAndInstructions = {}
        for module in self.target.module_iter():
            # self.logDbgC.emit(f"\n📦 Module: {module.file}", DebugLevel.Verbose)
            if module.file.GetFilename() == self.target.executable.GetFilename():  # "a_hello_world_test":
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
                                symName = subsec.GetName()
                                if isObjC and subsec.GetName() == "__stubs":
                                    self.loadSymbolCallback.emit(subsec.GetName())
                                    # symName = subsec.GetName()

                                for smbl in lstSym:
                                    # self.logDbgC.emit(f"===========>>>>>>>>>>> symbl: {smbl}", DebugLevel.Verbose)
                                    # .GetStartAddress().GetFunction()
                                    if isObjC and not subsec.GetName() == "__stubs":
                                        self.loadSymbolCallback.emit(smbl.GetName())
                                        symName = subsec.GetName()
                                    instructions = smbl.GetStartAddress().GetFunction().GetInstructions(self.target)
                                    self.allModsAndInstructions[smbl.GetStartAddress().GetFunction().GetName()] = instructions
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
                                    # self.allModsAndInstructions[subsec.GetName()] = [instructions]
                                    # instructions = subsec.addr.GetFunction().GetInstructions(self.target)
                                    # insts = target.ReadInstructions(lldb.SBAddress(start_addr, target), lldb.SBAddress(end_addr, target))
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
                                addr = subsec.GetLoadAddress(self.target)  # .GetStartAddress()
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
                                    self.logDbgC.emit(f"Failed to read memory: {error.GetCString()}",
                                                      DebugLevel.Verbose)
                                pass
                        break
                break
            # else:
            # 	break
            idx += 1
        print(f"self.loadInstructionsCallback() => {self.allModsAndInstructions} ...")
        # for key, value in self.allModsAndInstructions:
        #     print(f"key: {key} => value: {value}")
        #
        self.checkLoadConnection(self.allInstructions)
        # print("Callback returned:", repr(self.allModsAndInstructions))
        self.loadInstructionsCallback.emit(self.connections, self.allModsAndInstructions)
        self.loadCurrentPC.emit(hex(self.frame.GetPC()))
        self.logDbgC.emit(f"============ END DISASSEMBLER ===============", DebugLevel.Verbose)

        # for inst in self.allInstructions:

        #
        # for con in self.connections:
        #     self.logDbgC.emit(
        #         f"===>>> Connection: {hex(con.origAddr)} / {hex(con.destAddr)} => {con.origRow} / {con.destRow}",
        #         DebugLevel.Verbose)
        # # pass
        # # self.progressUpdateCallback.emit(35, f"Read disassembly and created control flow connections ...")
        # QApplication.processEvents()
        # self.connections.sort(key=lambda x: abs(x.jumpDist), reverse=True)
        # self.finishedLoadInstructionsCallback.emit(self.connections, self.target.GetExecutable().GetFilename(),
        #                                            self.allModsAndInstructions)
        # QApplication.processEvents()

    def checkLoadConnection(self, instructions):
        sAddrJumpFrom = 0x0
        rowStart = 0x0
        rowEnd = 0x0
        self.radius = 15

        for instruction in self.allInstructions:
            sMnemonic = instruction.GetMnemonic(self.target)
            self.logDbgC.emit(f"checkLoadConnection()... => instruction: {instruction}", DebugLevel.Verbose)
            # if sMnemonic is None or sMnemonic == "":
            # 	return

            if sMnemonic is not None and sMnemonic.startswith(JMP_MNEMONICS) and not sMnemonic.startswith(
                    JMP_MNEMONICS_EXCLUDE):
                sAddrJumpTo = instruction.GetOperands(self.target)
                self.logDbgC.emit(f"checkLoadConnection()..... {instruction} ===>>> JumpTo: {sAddrJumpTo}", DebugLevel.Verbose)

                if sAddrJumpTo is None or not is_hex_string(sAddrJumpTo):
                    self.logDbgC.emit(f"checkLoadConnection() RETURN OF ERROR ..... sAddrJumpTo: {sAddrJumpTo}", DebugLevel.Verbose)
                    continue

                bOver = self.startAddr < int(sAddrJumpTo, 16) < self.endAddr

                if self.isInsideTextSection(sAddrJumpTo) or bOver:
                    if self.isInsideTextSection(sAddrJumpTo):
                        self.logDbgC.emit(f"IS NOT OVER CONNECTION!!!!", DebugLevel.Verbose)
                        sAddrStartInt = int(str(instruction.GetAddress().GetLoadAddress(self.target)), 10)
                        sAddrJumpFrom = hex(sAddrStartInt)
                        rowStart = int(self.get_line_number(
                            sAddrStartInt))  # idxInstructions#int(self.get_line_number(int(sAddrJumpFrom, 16)))
                        # lineEnd = self.get_line_number(int(sAddrJumpTo, 16))
                        lineEnd = None
                        idx = 0
                        for inst in self.allInstructions:
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
                        self.logDbgC.emit(f"IS OVER CONNECTION!!!!", DebugLevel.Verbose)
                        sAddrStartInt = int(str(instruction.GetAddress().GetLoadAddress(self.target)),
                                            10)  # int(str(instruction.GetAddress().GetLoadAddress(self.target)), 10)
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
                        self.logDbgC.emit(
                            f"Found connection from line: {rowStart} to: {rowEnd} ({sAddrJumpFrom} / {sAddrJumpTo})",
                            DebugLevel.Verbose)

                    if rowStart < rowEnd:
                        newConObj = QControlFlowWidget.draw_flowConnectionNG(rowStart, rowEnd, int(sAddrJumpFrom, 16),
                                                                             int(sAddrJumpTo, 16), None,
                                                                             random_qcolor(), self.radius, 1,
                                                                             False)  # self.window().txtMultiline.table
                    else:
                        newConObj = QControlFlowWidget.draw_flowConnectionNG(rowStart, rowEnd, int(sAddrJumpFrom, 16),
                                                                             int(sAddrJumpTo, 16), None,
                                                                             random_qcolor(), self.radius, 1, True)

                    # newConObj.mnemonic = sMnemonic
                    # self.logDbgC.emit(f"Connection (Branch) is a: {newConObj.mnemonic} / {sMnemonic})", DebugLevel.Verbose)
                    if abs(newConObj.jumpDist / 2) <= (newConObj.radius / 2):
                        newConObj.radius = newConObj.jumpDist / 2
                    self.connections.append(newConObj)
                    if self.radius <= 130:
                        self.radius += 15
                else:
                    self.logDbgC.emit(f"checkLoadConnection()..... sAddrJumpTo NOT IN TARGET", DebugLevel.Verbose)
                # self.connections.sort(key=lambda x: abs(x.jumpDist), reverse=True)

    def get_line_number(self, address_int):
        # target = debugger.GetSelectedTarget()
        addr = lldb.SBAddress(address_int, self.target)

        # Resolve symbol context with line entry info
        context = self.target.ResolveSymbolContextForAddress(
            addr,
            lldb.eSymbolContextEverything
        )

        line_entry = context.GetLineEntry()
        if line_entry.IsValid():
            file_spec = line_entry.GetFileSpec()
            line = line_entry.GetLine()
            # print(f"📍 Address 0x{address_int:x} maps to {file_spec.GetFilename()}:{line}")
            return line  # file_spec.GetFilename(),
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

    def loadFileStats(self):
        self.logDbgC.emit(f"def loadFileStats(...)", DebugLevel.Verbose)
        statistics = self.target.GetStatistics()
        self.logDbgC.emit(f"def loadFileStats(...) => after statistics = self.driver.getTarget().GetStatistics()", DebugLevel.Verbose)
        stream = lldb.SBStream()
        success = statistics.GetAsJSON(stream)
        self.logDbgC.emit(f"def loadFileStats(...) => after success = statistics.GetAsJSON(stream)", DebugLevel.Verbose)

        if success:
            self.loadJSONCallback.emit(str(stream.GetData()))
            self.logDbgC.emit(f"def loadFileStats(...) => after self.loadJSONCallback.emit(str(stream.GetData()))", DebugLevel.Verbose)
            QApplication.processEvents()

    def loadRegisters(self):
        # super(LoadRegisterWorker, self).workerFunc()

        # self.sendStatusBarUpdate("Reloading registers ...")
        # target = self.driver.getTarget()
        # process = target.GetProcess()
        if self.process:
            # thread = process.GetThreadAtIndex(0)
            if self.thread:
                # self.frame = self.frame
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
                                                                    getMemoryValueAtAddress(self.target, self.process, child.GetValue()))
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

    def char_array_to_string(self, char_array_value):
        byte_array = char_array_value.GetPointeeData(0, char_array_value.GetByteSize())
        error = lldb.SBError()
        sRet = byte_array.GetString(error, 0)
        return "" if sRet == 0 else sRet

    # def loadStacktrace(self):
    #     # self.process = self.driver.getTarget().GetProcess()
    #     # self.thread = self.process.GetThreadAtIndex(0)
    #     #		from lldbutil import print_stacktrace
    #     #		st = get_stacktrace(self.thread)
    #     ##			print(f'{st}')
    #     #		self.txtOutput.setText(st)
    #
    #     idx = 0
    #     if self.thread:
    #         #			self.treThreads.doubleClicked.connect()
    #         self.treThreads.clear()
    #         self.processNode = QTreeWidgetItem(self.treThreads, ["#0 " + str(self.process.GetProcessID()),
    #                                                              hex(self.process.GetProcessID()) + "",
    #                                                              self.process.GetTarget().GetExecutable().GetFilename(),
    #                                                              '', ''])
    #
    #         self.threadNode = QTreeWidgetItem(self.processNode,
    #                                           ["#" + str(idx) + " " + str(self.thread.GetThreadID()),
    #                                            hex(self.thread.GetThreadID()) + "", self.thread.GetQueueName(), '',
    #                                            ''])
    #
    #         numFrames = self.thread.GetNumFrames()
    #
    #         for idx2 in range(numFrames):
    #             self.setProgressValue(idx2 / numFrames)
    #             frame = self.thread.GetFrameAtIndex(idx2)
    #             # logDbgC(f"frame.GetFunction(): {frame.GetFunction()}")
    #             frameNode = QTreeWidgetItem(self.threadNode,
    #                                         ["#" + str(frame.GetFrameID()), "", str(frame.GetPCAddress()),
    #                                          str(hex(frame.GetPC())), self.GuessLanguage(frame)])
    #             idx += 1
    #
    #         self.processNode.setExpanded(True)
    #         self.threadNode.setExpanded(True)
