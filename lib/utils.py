from PyQt6.QtGui import QColor
import random
import time

from ui.helper.dbgOutputHelper import DebugLevel, logDbgC

def global_function():
    print("This function is available everywhere!")

def setStatusBar(msg):
    logDbgC(f"setStausBAr was removed ... message is: {msg}", DebugLevel.Info)
    #     main_window.updateStatusBar(msg)
    pass

def random_qcolor():
    random.seed(time.time())
    r = random.randint(127, 255)
    g = random.randint(127, 255)
    b = random.randint(127, 255)
    return QColor(r, g, b)