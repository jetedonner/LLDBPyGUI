#!/usr/bin/env python3

if __name__ == "__main__":
		print("Run only as script from LLDB... Not as standalone program!")
	
import lldb
import sys
import os

try:
	import queue
except ImportError:
	import Queue as queue
	
from PyQt6.QtWidgets import *

#from dbg import *
import dbg.debuggerdriver
from dbg.debuggerdriver import *
from LLDBPyGUIWindow import *
from config import *

def __lldb_init_module(debugger, internal_dict):
	''' we can execute lldb commands using debugger.HandleCommand() which makes all output to default
	lldb console. With SBDebugger.GetCommandinterpreter().HandleCommand() we can consume all output
	with SBCommandReturnObject and parse data before we send it to output (eg. modify it);

	in practice there is nothing here in initialization or anywhere else that we want to modify
	'''

	# don't load if we are in Xcode since it is not compatible and will block Xcode
	if os.getenv('PATH').startswith('/Applications/Xcode'):
			return

	global g_home
	if g_home == "":
			g_home = os.getenv('HOME')
		
	res = lldb.SBCommandReturnObject()
	ci = debugger.GetCommandInterpreter()

	# settings
	ci.HandleCommand("settings set target.x86-disassembly-flavor " + CONFIG_FLAVOR, res)
	ci.HandleCommand(f"settings set prompt \"({PROMPT_TEXT}) \"", res)
	ci.HandleCommand("settings set stop-disassembly-count 0", res)
	# set the log level - must be done on startup?
#   ci.HandleCommand("settings set target.process.extra-startup-command QSetLogging:bitmask=" + CONFIG_LOG_LEVEL + ";", res)
	if CONFIG_USE_CUSTOM_DISASSEMBLY_FORMAT == 1:
			ci.HandleCommand("settings set disassembly-format " + CUSTOM_DISASSEMBLY_FORMAT, res)
		
	# the hook that makes everything possible :-)
	ci.HandleCommand(f"command script add -h '({PROMPT_TEXT}) Start the {APP_NAME}.' -f LLDBPyGUI.StartLLDBPyGUI pyg", res)

	ci.HandleCommand(f"command script add -h '({PROMPT_TEXT}) Display {APP_NAME} banner.' --function LLDBPyGUI.cmd_banner banner", res)

	return
	
def cmd_banner(debugger,command,result,dict): 
	print(f"" + BOLD + "" + RED + "#=================================================================================#")
	print(f"| Starting TEST ENVIRONMENT for {APP_NAME} (ver. {APP_VERSION})            |")
	print(f"|                                                                                 |")
	print(f"| Desc:                                                                           |")
	print(f"| This python script is for development and testing while development             |")
	print(f"| of the LLDB python GUI (LLDBPyGUI.py) - use at own risk! No Warranty!           |")
	print(f"|                                                                                 |")
	print(f"| Credits:                                                                        |")
	print(f"| - LLDB                                                                          |")
	print(f"| - lldbutil.py                                                                   |")
	print(f"| - lui.py                                                                        |")
	print(f"|                                                                                 |")
	print(f"| Author / Copyright:                                                             |")
	print(f"| Kim David Hauser (JeTeDonner), (C.) by kimhauser.ch 1991-2024                   |")
	print(f"#=================================================================================#" + RESET)
#   return(sys.stdout)
	
	
def close_application():
#	global driver

	print("close_application()")
#	Stop all running tasks in the thread pool
	print("KILLING PROCESS")
	os._exit(1)
	
def StartLLDBPyGUI(debugger, command, result, dict):
	
	cmd_banner(debugger, command, result, dict)
	
	debugger.SetAsync(False)
	
#		debugger.SetAsync(True)
	pyGUIApp = QApplication([])
	pyGUIApp.aboutToQuit.connect(close_application)
	
	ConfigClass.initIcons()
	pyGUIApp.setWindowIcon(ConfigClass.iconBugGreen)

#	driver = None
	global event_queue
	event_queue = queue.Queue()
	
	global driver
	driver = dbg.debuggerdriver.createDriver(debugger, event_queue)
	
	pyGUIWindow = LLDBPyGUIWindow(driver) # QConsoleTextEditWindow(debugger)
	pyGUIWindow.app = pyGUIApp
#	pymobiledevice3GUIWindow.loadTarget()
	pyGUIWindow.show()
	
	tmrAppStarted = QtCore.QTimer()
	tmrAppStarted.singleShot(500, pyGUIWindow.onQApplicationStarted)
	
	sys.exit(pyGUIApp.exec())
	