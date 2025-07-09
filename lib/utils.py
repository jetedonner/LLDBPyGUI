from PyQt6.QtGui import QColor
import random
import time
# utils.py

# # app_context.py
main_window = None

def global_function():
    print("This function is available everywhere!")

def do_magic():
    main_window.updateStatusBar("Boom!")

def setStatusBar(msg):
    main_window.updateStatusBar(msg)

def random_qcolor():
    random.seed(time.time())
    r = random.randint(127, 255)
    g = random.randint(127, 255)
    b = random.randint(127, 255)
    return QColor(r, g, b)