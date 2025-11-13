from datetime import datetime
from enum import Enum

from PyQt6.QtWidgets import QApplication, QMainWindow

from constants import JMP_MNEMONICS_ADDRISSECONDARG
from lib.settings import SettingsHelper, SettingsValues


class DebugLevel(Enum):
    Info = 1
    Warnings = 2
    Error = 3
    Verbose = 4


currentDebugLevel = DebugLevel.Verbose
# global mainWindowNG
mainWindowNG = None


def get_main_window():
    global mainWindowNG
    if mainWindowNG is None:
        app = QApplication.instance()
        if app is not None:
            for widget in app.topLevelWidgets():
                if isinstance(widget, QMainWindow):
                    # return widget
                    mainWindowNG = widget
                    break
    return mainWindowNG


settingHelper = SettingsHelper()


def logDbg(logMsg="", alsoPrintToConsole=False, dbgLevel=DebugLevel.Info):
    if currentDebugLevel.value < dbgLevel.value:
        return

    sDateTimeFormat = "%H:%M:%S"
    if settingHelper.getValue(SettingsValues.ShowDateInLogView):
        sDateTimeFormat = "%Y-%m-%d %H:%M:%S"
    now = datetime.now()
    timestamp = now.strftime(sDateTimeFormat)  # Format as 'YYYY-MM-DD HH:MM:SS'
    logMsgNG = f"{timestamp}: {logMsg}"

    # global currentDebugLevel
    mainWin = get_main_window()
    if mainWin is not None:
        mainWin.wdtDbg.logDbg(logMsgNG)

    if alsoPrintToConsole:
        print(logMsgNG)


def logDbgC(logMsg="", dbgLevel=DebugLevel.Info):
    logDbg(logMsg, True, dbgLevel)


def getAddrStr(addrIn, getIntAlso=True):
    sRet = f"{hex(addrIn)}"
    if getIntAlso:
        sRet += f" / {addrIn}"
    return sRet


def getAddrFromOperands(sMnemonic, sOperand):
    if sMnemonic in JMP_MNEMONICS_ADDRISSECONDARG:
        sAddrJumpTo = sOperand.split(",")[1].strip()
    else:
        sAddrJumpTo = str(sOperand)
    return sAddrJumpTo


def getAddrDelta(instruction, target):
    addr = instruction.GetAddress()
    load_addr = addr.GetLoadAddress(target)
    file_addr = addr.GetFileAddress()
    delta_addr = load_addr - file_addr
    delta_addrHex = hex(delta_addr)
    return delta_addr, delta_addrHex

def printStacktrace(driver):
    process = driver.target.GetProcess()
    thread = process.GetThreadAtIndex(0)

    idx = 0
    if thread:
        # self.clear()
        # self.processNode = QTreeWidgetItem(self, ["#0 " + str(self.process.GetProcessID()),
        # 										  hex(self.process.GetProcessID()) + "",
        # 										  self.process.GetTarget().GetExecutable().GetFilename(), '', ''])
        # self.threadNode = QTreeWidgetItem(self.processNode, ["#" + str(idx) + " " + str(self.thread.GetThreadID()),
        # 													 hex(self.thread.GetThreadID()) + "",
        # 													 self.thread.GetQueueName(), '', ''])

        print(process)
        numFrames = thread.GetNumFrames()

        for idx2 in range(numFrames):
            frame = thread.GetFrameAtIndex(idx2)
            print(frame)
            # frameNode = QTreeWidgetItem(self.threadNode,
            # 							["#" + str(frame.GetFrameID()), "", str(frame.GetPCAddress()),
            # 							 str(hex(frame.GetPC())), GuessLanguage(frame)])
            idx += 1

    # 	self.processNode.setExpanded(True)
    # 	self.threadNode.setExpanded(True)
    # QApplication.processEvents()

import traceback

def debug_stack():
    print("Call stack:")
    traceback.print_stack()