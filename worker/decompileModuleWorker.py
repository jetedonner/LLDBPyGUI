from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

from ui.helper.lldbutil import symbol_type_to_str


class DecompileModuleWorker(QObject):

    # finished = pyqtSignal()
    show_dialog = pyqtSignal()
    logDbg = pyqtSignal(str)
    # logDbgC = pyqtSignal(str)
    logDbgC = pyqtSignal(str, object)

    loadInstructionCallback = pyqtSignal(object)
    # loadStringCallback = pyqtSignal(str, int, str)
    loadSymbolCallback = pyqtSignal(str)

    finishedLoadInstructionsCallback = pyqtSignal(object, str, object)

    driver = None
    target = None
    modulePath = ""
    initTable = True

    allModsAndInstructions = {}

    def __init__(self,  driver, modulePath, initTable):
        super().__init__()
        self.driver = driver
        self.target = self.driver.getTarget()
        self.modulePath = modulePath
        self.initTable = initTable

    def run(self):
        self._should_stop = False  # Reset before starting

        self.show_dialog.emit()

        self.logDbg.emit(f"Decompiling module: {self.modulePath}...")

        # self.target = self.driver.getTarget()

        self.disassemble_entire_target(self.target)

    def disassemble_entire_target(self, target):
        """Disassembles instructions for the entire target.

        Args:
            target: The SBTarget object representing the debugged process.
        """
        # for module in self.target.module_iter():
        # 	if module.GetFileSpec().fullpath != self.moduleName:
        # 		continue
        # 	for compile_unit in module.compile_unit_iter():
        # 		for func in compile_unit:
        # 			if func.IsValid():
        # 				print(f"Objective-C Function: {func.GetName()}")

        print(f"LoadDisassemblyWorkerNG.disassemble_entire_target() ....")
        # thread = self.target.GetProcess().GetSelectedThread()
        idxOuter = 0
        INDENT = "    "
        INDENT2 = INDENT + INDENT
        self.allInstructions = []
        idxInstructions = 0
        idxSym = 0
        for module in self.target.module_iter():
            if module.GetFileSpec().fullpath != self.modulePath:
                # print(
                #     f"LoadDisassemblyWorkerNG.disassemble_entire_target() => module.GetFileSpec().fullpath: {module.GetFileSpec().fullpath} / {self.modulePath}....")
                continue
            else:
                print('Number of sections: %d' % module.GetNumSections())
                for sec in module.section_iter():
                    print(sec)

                    # Iterates the text section and prints each symbols within each sub-section.
                    for subsec in sec:
                        print(INDENT + repr(subsec))
                        for sym in module.symbol_in_section_iter(subsec):
                            print(INDENT2 + repr(sym))
                            print(INDENT2 + 'symbol type: %s' % symbol_type_to_str(sym.GetType()))

                        lstSym = module.symbol_in_section_iter(subsec)
                        # if isObjC and subsec.GetName() == "__stubs":
                        #     self.loadSymbolCallback.emit(subsec.GetName())

                        for smbl in lstSym:    
                            # self.logDbgC.emit(f"===========>>>>>>>>>>> symbl: {smbl}", DebugLevel.Verbose)
                            # .GetStartAddress().GetFunction()
                            # if isObjC and not subsec.GetName() == "__stubs":

                            self.loadSymbolCallback.emit(smbl.GetName())
                            symName = smbl.GetName()
                            instructions = smbl.GetStartAddress().GetFunction().GetInstructions(target)
                            # self.allModsAndInstructions[symName] = instructions
                            # self.allModsAndInstructions[symName] = instructions
                            print(f"len(instructions): {len(instructions)} ...")
                            if len(instructions) > 0:
                                self.allModsAndInstructions[symName] = instructions
                                self.allInstructions += instructions
                                for instruction in instructions:
                                    # self.logDbgC.emit(f"----------->>>>>>>>>>> INSTRUCTION: {instruction.GetMnemonic(self.target)} ... ", DebugLevel.Verbose)
                                    self.loadInstructionCallback.emit(instruction)
                                    QApplication.processEvents()
                                    idxInstructions += 1
                                    # self.checkLoadConnection(instruction, idxInstructions + (idxSym + 1))
                            else:
                                instructions = smbl.GetInstructions(target)
                                if instructions.GetSize() == 0:
                                    continue

                                self.allModsAndInstructions[symName] = instructions
                                self.allInstructions += instructions
                                for inst in instructions:
                                    self.loadInstructionCallback.emit(inst)
                                    QApplication.processEvents()
                                    idxInstructions += 1
                            idxSym += 1




                # # Iterate over all functions in the module
                # for sym in module:
                #     if not sym.IsValid():
                #         continue
                #
                #     print(f"\n🔧 Function: {sym.GetName()}")
                #     self.loadSymbolCallback.emit(sym.GetName())
                #     QApplication.processEvents()
                #
                #     instructions = sym.GetInstructions(target)
                #     if instructions.GetSize() == 0:
                #         continue
                #
                #     for inst in instructions:
                #         self.loadInstructionCallback.emit(inst)
                #         QApplication.processEvents()
                #     # print(f"Address: {inst.GetAddress()}")
                #     # print(f"Instruction: {inst}")
                #     # print(f'sym.GetName() => {sym.GetName()} / instruction.GetAddress().GetFunction().GetName() => {inst.GetAddress().GetFunction().GetName()}')
                #     # print(f'COMMENT => {inst.GetComment(self.target)}')
                #     # self.signals.loadInstruction.emit(instruction)

                # self.allInstructions
                self.finishedLoadInstructionsCallback.emit([], module.GetFileSpec().GetFilename(), self.allModsAndInstructions)
                QApplication.processEvents()
                break
    pass