from PyQt6.QtWidgets import QApplication, QMainWindow

def get_main_window():
    app = QApplication.instance()
    if app is not None:
        for widget in app.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                return widget
    return None

def logDbg(logMsg="", alsoPrintToConsole = False):
    mainWin = get_main_window()
    if mainWin is not None:
        mainWin.wdtDbg.logDbg(logMsg)
    if alsoPrintToConsole:
        print(logMsg)

def logDbgC(logMsg=""):
    logDbg(logMsg, True)