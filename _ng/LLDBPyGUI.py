#!/usr/bin/env python3
import sys
from datetime import datetime

from PyQt6.QtWidgets import QApplication
from _ng.MainWindow import MainWindow
from _ng.config import *
if __name__ == "__main__":
    print("Run only as script from LLDB... Not as standalone program!")

import lldb
# import sys
import os

# from config import *
from constants import *
#
# import subprocess

def __lldb_init_module(debugger, internal_dict):
    ''' we can execute lldb commands using debugger.HandleCommand() which makes all output to default
    lldb console. With SBDebugger.GetCommandinterpreter().HandleCommand() we can consume all output
    with SBCommandReturnObject and parse data before we send it to output (eg. modify it);

    in practice there is nothing here in initialization or anywhere else that we want to modify
    '''

    # don't load if we are in Xcode since it is not compatible and will block Xcode
    if os.getenv('PATH').startswith('/Applications/Xcode'):
        return

    # global g_home
    # if g_home == "":
    #     g_home = os.getenv('HOME')

    res = lldb.SBCommandReturnObject()
    ci = debugger.GetCommandInterpreter()

    # settings
    # ci.HandleCommand("settings set target.x86-disassembly-flavor " + CONFIG_FLAVOR, res)
    ci.HandleCommand(f'settings set prompt \"({PROMPT_TEXT}) \"', res)
    # ci.HandleCommand("settings set stop-disassembly-count 0", res)
    #
    # ci.HandleCommand(f'settings set target.process.stop-on-exec true', res)
    # # set the log level - must be done on startup?
    # #   ci.HandleCommand("settings set target.process.extra-startup-command QSetLogging:bitmask=" + CONFIG_LOG_LEVEL + ";", res)
    # if CONFIG_USE_CUSTOM_DISASSEMBLY_FORMAT == 1:
    #     ci.HandleCommand("settings set disassembly-format " + CUSTOM_DISASSEMBLY_FORMAT, res)
    #
    # the hook that makes everything possible :-)
    ci.HandleCommand(f"command script add -h '({PROMPT_TEXT}) Start the {APP_NAME}.' -f LLDBPyGUI.startLLDBPyGUI pyg",
                     res)
    # ci.HandleCommand(f"command script add -h '({PROMPT_TEXT}) Start the {APP_NAME}.' -f LLDBPyGUI.startLLDBPyGUI2 pyg2",
    #                  res)
    #
    ci.HandleCommand(
        f"command script add -h '({PROMPT_TEXT}) Display {APP_NAME} banner.' --function LLDBPyGUI.cmd_intro intro",
        res)
    # ci.HandleCommand(
    #     f"command script add -h '({PROMPT_TEXT}) Display (LLDBs) Python path and version.' --function LLDBPyGUI.cmd_pyvers pyvers",
    #     res)
    #
    # ci.HandleCommand('type summary add --summary-string "these are more words" MyProjectClass', res)
    #
    # ci.HandleCommand('command script add -f LLDBPyGUI.feed_input feedinput', res)
    # ci.HandleCommand('command script add -f LLDBPyGUI.disassemble_current_function dsf', res)
    # ci.HandleCommand('command script add -f LLDBPyGUI.launchtest launchtest', res)
    # ci.HandleCommand("process launch --stop-at-entry", res)
    #
    # return

def cmd_intro(debugger, command, result, dict):

    current_year = str(datetime.now().year)

    print(BOLD + RED)
    print("#=================================================================================#")
    print(f"| TEST ENVIRONMENT for {APP_NAME} (ver. {APP_VERSION}, build {APP_BUILD})                     |")
    print(f"|                                                                                 |")
    print(f"| This python script is for development and testing while evaluating              |")
    print(f"| the LLDB python GUI (LLDBPyGUI.py) - use at own risk! No Warranty!              |")
    print(f"|                                                                                 |")
    print(f"| jetedonner, (C.) by kimhauser.ch 1991-{current_year}                                      |")
    print(f"#=================================================================================#" + RESET)


def startLLDBPyGUI(debugger, command, result, dict):
    # sys.setrecursionlimit(1000000)

    cmd_intro(debugger, command, result, dict)

    debugger.SetAsync(False)

    #		debugger.SetAsync(True)
    # pyGUIApp = QApplication([])
    pyGUIApp = QApplication(sys.argv)  # Pass sys.argv explicitly!
    # pyGUIApp.aboutToQuit.connect(close_application)

    ConfigClass.initIcons()
    pyGUIApp.setWindowIcon(ConfigClass.iconBugGreen)

    # #	driver = None
    # global event_queue
    # event_queue = queue.Queue()
    #
    # global driver
    # driver = dbg.debuggerdriver.createDriver(debugger, event_queue)
    #
    # pyGUIWindow = LLDBPyGUIWindow(driver, debugger)  # QConsoleTextEditWindow(debugger)
    # pyGUIWindow.app = pyGUIApp
    # #	pymobiledevice3GUIWindow.loadTarget()
    pyGUIWindow = MainWindow()
    pyGUIWindow.app = pyGUIApp
    pyGUIWindow.show()
    #
    # tmrAppStarted = QtCore.QTimer()
    # tmrAppStarted.singleShot(500, pyGUIWindow.onQApplicationStarted)
    # # sys.exit(pyGUIApp.exec())
    # # pyGUIApp.exec()
    try:
        sys.exit(pyGUIApp.exec())
    except SystemExit:
        print("PyQt application exited cleanly.")