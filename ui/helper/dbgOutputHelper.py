from enum import Enum
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow

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
    return mainWindowNG

settingHelper = SettingsHelper()

def logDbg(logMsg="", alsoPrintToConsole = False, dbgLevel = DebugLevel.Info):

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

def logDbgC(logMsg="", dbgLevel = DebugLevel.Info):
    logDbg(logMsg, True, dbgLevel)

def getAddrStr(addrIn, getIntAlso=True):
    sRet = f"{hex(addrIn)}"
    if getIntAlso:
        sRet += f" / {addrIn}"
    return sRet