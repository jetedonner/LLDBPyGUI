from enum import Enum

from PyQt6.QtWidgets import QApplication, QMainWindow

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
    return mainWindowNG

def logDbg(logMsg="", alsoPrintToConsole = False, dbgLevel = DebugLevel.Info):
    # global currentDebugLevel
    if currentDebugLevel.value < dbgLevel.value:
        return
    mainWin = get_main_window()
    if mainWin is not None:
        mainWin.wdtDbg.logDbg(logMsg)
    if alsoPrintToConsole:
        print(logMsg)

def logDbgC(logMsg="", dbgLevel = DebugLevel.Info):
    logDbg(logMsg, True, dbgLevel)

def getAddrStr(addrIn, getIntAlso=True):
    sRet = f"{hex(addrIn)}"
    if getIntAlso:
        sRet += f" / {addrIn}"
    return sRet