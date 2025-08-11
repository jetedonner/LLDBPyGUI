import lldb
from PyQt6.QtCore import QObject, pyqtSignal


class AttachWorker(QObject):

    show_dialog = pyqtSignal()
    logDbg = pyqtSignal(str)
    logDbgC = pyqtSignal(str, object)
    loadModulesCallback = pyqtSignal(object, object)

    attachThread = None
    _should_stop = False

    debugger = None
    pid = None
    name = None
    process = None
    target = None
    thread = None
    frame = None


    def __init__(self, debugger, pid=None, name=None):
        super().__init__()
        self.attachThread = None
        self._should_stop = False
        self.debugger = debugger
        self.pid = pid
        self.name = name
        self.process = None
        self.target = None
        self.thread = None
        self.frame = None

    def run(self):
        self._should_stop = False  # Reset before starting
        self.attach_to_process()
        if self.process:
            self.thread = self.process.GetThreadAtIndex(0)
            if self.thread:
                # for z in range(self.thread.GetNumFrames()):
                self.frame = self.thread.GetFrameAtIndex(0)
                self.loadModulesCallback.emit(self.frame, self.target.modules)

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
        self.logDbgC.emit(f"============ END DISASSEMBLER ===============", DebugLevel.Verbose)
