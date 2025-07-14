import time
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from config import *

class Worker(QObject):
    finished = pyqtSignal()
    show_dialog = pyqtSignal()

    mainWin = None

    def __init__(self, mainWinToUse):
        super().__init__()
        self._should_stop = False
        self.mainWin = mainWinToUse

    def run(self):
        self._should_stop = False  # Reset before starting
        self.show_dialog.emit()
        self.mainWin.loadNewExecutableFile(ConfigClass.testTarget)
        for i in range(10):  # Simulate long task
            if self._should_stop:
                print("Worker interrupted.")
                break
            # Simulate work
            time.sleep(1)
            print(f"Working... {i}")
        self.finished.emit()

    def stop(self):
        self._should_stop = True

    # def run(self):
    #     # Simulate heavy work
    #     # time.sleep(0.1)
    #
    #     # Signal to show modal dialog
    #     self.show_dialog.emit()
    #
    #     # More work...
    #     time.sleep(20)
    #     self.finished.emit()
