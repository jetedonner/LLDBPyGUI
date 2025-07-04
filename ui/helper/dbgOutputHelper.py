from PyQt6.QtWidgets import QApplication, QMainWindow

def get_main_window():
    app = QApplication.instance()
    if app is not None:
        for widget in app.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                return widget
    return None

def logDbg(logMsg=""):
    mainWin = get_main_window()
    if mainWin is not None:
        mainWin.wdtDbg.logDbg(logMsg)