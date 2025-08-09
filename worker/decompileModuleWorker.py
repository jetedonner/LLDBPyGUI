from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication


class DecompileModuleWorker(QObject):

    # finished = pyqtSignal()
    show_dialog = pyqtSignal()
    logDbg = pyqtSignal(str)
    # logDbgC = pyqtSignal(str)
    logDbgC = pyqtSignal(str, object)

    loadInstructionCallback = pyqtSignal(object)
    # loadStringCallback = pyqtSignal(str, int, str)
    loadSymbolCallback = pyqtSignal(str)

    finishedLoadInstructionsCallback = pyqtSignal(object, str)

    driver = None
    target = None
    modulePath = ""
    initTable = True

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
        for module in self.target.module_iter():
            if module.GetFileSpec().fullpath != self.modulePath:
                # print(
                #     f"LoadDisassemblyWorkerNG.disassemble_entire_target() => module.GetFileSpec().fullpath: {module.GetFileSpec().fullpath} / {self.modulePath}....")
                continue
            else:
                # if idxOuter != 0:
                # 	idxOuter += 1
                # 	continue

                # Iterate over all functions in the module
                for sym in module:
                    if not sym.IsValid():
                        continue
                    instructions = sym.GetInstructions(target)
                    if instructions.GetSize() == 0:
                        continue

                    # print(f"\n🔧 Function: {sym.GetName()}")
                    self.loadSymbolCallback.emit(sym.GetName())
                    for inst in instructions:
                        self.loadInstructionCallback.emit(inst)
                        QApplication.processEvents()
                    # print(f"Address: {inst.GetAddress()}")
                    # print(f"Instruction: {inst}")
                    # print(f'sym.GetName() => {sym.GetName()} / instruction.GetAddress().GetFunction().GetName() => {inst.GetAddress().GetFunction().GetName()}')
                    # print(f'COMMENT => {inst.GetComment(self.target)}')
                    # self.signals.loadInstruction.emit(instruction)

                self.finishedLoadInstructionsCallback.emit([], module.GetFileSpec().GetFilename())
                break
    pass