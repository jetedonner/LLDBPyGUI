import os

from PyQt6.QtGui import QColor
import random
import time

from config import ConfigClass
from ui.helper.dbgOutputHelper import DebugLevel, logDbgC

def global_function():
    print("This function is available everywhere!")

def setStatusBar(msg):
    logDbgC(f"setStausBar was removed ... message is: {msg}", DebugLevel.Info)
    #     main_window.updateStatusBar(msg)
    pass

def random_qcolor():
    random.seed(time.time())
    r = random.randint(127, 255)
    g = random.randint(127, 255)
    b = random.randint(127, 255)
    return QColor(r, g, b)

def find_source_file(executable_path):
    base_name = os.path.splitext(os.path.basename(executable_path))[0]
    dir_path = os.path.dirname(executable_path)
    matches = []

    # Extensions to look for
    # extensions = ['.c', '.cpp', '.m']
    extensions = ConfigClass.autofindSourcecodeFileExts

    # Walk through directory and subfolders
    for root, _, files in os.walk(dir_path):
        for file in files:
            name, ext = os.path.splitext(file)
            if name == base_name and ext in extensions:
                full_path = os.path.join(root, file)
                matches.append(full_path)

    return matches

    # # Example usage
    # exe_path = "/path/to/your/app/executable"
    # sources = find_source_file(exe_path)
    # print("Found source files:", sources)

def hex_to_string(hex_values):
    # Convert each hex value to an integer, then to its ASCII character
    return ''.join(chr(int(h, 16)) for h in hex_values)

# # Example usage
# hex_input = ['73', '68', '6f', '77']
# result = hex_to_string(hex_input)
# print("The result is:", result)