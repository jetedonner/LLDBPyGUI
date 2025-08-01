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

import subprocess

def bring_app_to_front(frame, bp_loc, dict):
	# Replace 'MyAppName' with the actual name of your app
	script = '''
	tell application "System Events"
		set frontmost of process "cocoa_windowed_objc2" to true
	end tell
	'''
	subprocess.run(['osascript', '-e', script])

def on_scanf_hit(frame, bp_loc, dict):
	print("✅ Breakpoint hit at scanf!")
	return True  # Returning True tells LLDB to stop here	# return

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
	ci.HandleCommand(f'settings set prompt \"({PROMPT_TEXT}) \"', res)
	ci.HandleCommand("settings set stop-disassembly-count 0", res)

	ci.HandleCommand(f'settings set target.process.stop-on-exec true', res)
	# set the log level - must be done on startup?
#   ci.HandleCommand("settings set target.process.extra-startup-command QSetLogging:bitmask=" + CONFIG_LOG_LEVEL + ";", res)
	if CONFIG_USE_CUSTOM_DISASSEMBLY_FORMAT == 1:
			ci.HandleCommand("settings set disassembly-format " + CUSTOM_DISASSEMBLY_FORMAT, res)
		
	# the hook that makes everything possible :-)
	ci.HandleCommand(f"command script add -h '({PROMPT_TEXT}) Start the {APP_NAME}.' -f LLDBPyGUI.StartLLDBPyGUI pyg", res)

	ci.HandleCommand(f"command script add -h '({PROMPT_TEXT}) Display {APP_NAME} banner.' --function LLDBPyGUI.cmd_banner banner", res)
	ci.HandleCommand(
		f"command script add -h '({PROMPT_TEXT}) Display (LLDBs) Python path and version.' --function LLDBPyGUI.cmd_pyvers pyvers",
		res)

	ci.HandleCommand('command script add -f LLDBPyGUI.feed_input feedinput', res)
	ci.HandleCommand('command script add -f LLDBPyGUI.launchtest launchtest', res)
	ci.HandleCommand("process launch --stop-at-entry", res)


	return

def break_at_main(debugger, command, result, internal_dict):
	target = debugger.GetSelectedTarget()
	if not target:
		result.PutCString("No target loaded.")
		return

	# Find the symbol context for 'main'
	matches = target.FindFunctions("main")
	if matches.GetSize() == 0:
		result.PutCString("Could not find 'main' function.")
		return

	# Get the start address of the first match
	symbol_context = matches.GetContextAtIndex(0)
	start_addr = symbol_context.GetSymbol().GetStartAddress()
	load_addr = start_addr.GetLoadAddress(target)

	# Create a breakpoint at the exact address
	bp = target.BreakpointCreateByAddress(load_addr)
	result.PutCString(f"Breakpoint set at main's first instruction: 0x{load_addr:x}")

def find_main(debugger):
	target = debugger.GetSelectedTarget()
	if not target:
		print("No target loaded.")
		return

	main_symbol = target.FindFunctions("main")
	if main_symbol.GetSize() == 0:
		print("Could not find 'main' function.")
		return

	symbol_context = main_symbol.GetContextAtIndex(0)
	address = symbol_context.GetSymbol().GetStartAddress()
	print(f"Main entry point address: {address.GetLoadAddress(target)} / 0x{hex(address.GetLoadAddress(target))}")
	# setHelper = SettingsHelper()
	# if setHelper.getChecked(SettingsValues.BreakpointAtMainFunc):
	#

	return address.GetLoadAddress(target)

def launchtest(debugger, command, result, internal_dict):
	# debugger = lldb.SBDebugger.Create()
	print(f"HELLO FROM SCRIPT!!!!")
	# debugger.SetAsync(False)
	#
	# target = debugger.CreateTarget("./testtarget/amicable_numbers")
	# main_func = find_main(debugger)
	# print(f"MAIN FUNCTION: {hex(main_func)}")
	# launch_info = lldb.SBLaunchInfo([])
	# # launch_info.SetStopAtEntry(True)
	# # launch_info.SetLaunchFlags(lldb.eLaunchFlagDisableASLR and lldb.eLaunchFlagStopAtEntry)# and lldb.eLaunchFlagDebug) #lldb.eLaunchFlagStopAtEntry)
	# error = lldb.SBError()
	# process = target.Launch(launch_info, error)
	# import lldb

	# debugger = lldb.SBDebugger.Create()
	debugger.SetAsync(False)

	# Step 1: Create target from executable
	target = debugger.CreateTarget("./_testtarget/amicable_numbers")
	if not target.IsValid():
		print("Failed to create target.")
		exit(1)

	debugger.HandleCommand("process launch --stop-at-entry")

	# Step 2: Find the 'main' function symbol
	matches = target.FindFunctions("main")
	if matches.GetSize() == 0:
		print("Could not find 'main' function.")
		exit(1)

	# Step 3: Get the start address of 'main'
	symbol_context = matches.GetContextAtIndex(0)
	start_addr = symbol_context.GetSymbol().GetStartAddress()
	load_addr = start_addr.GetLoadAddress(target)

	# Step 4: Set breakpoint at exact address
	bp = target.BreakpointCreateByAddress(load_addr)
	print(f"Breakpoint set at main: 0x{load_addr:x}")

	# Step 5: Launch the process
	# launch_info = lldb.SBLaunchInfo([])
	launch_info = lldb.SBLaunchInfo(["--stop-at-entry"])  # Pass as launch argument
	# process = target.Launch(launch_info, lldb.SBError())
	# debugger.HandleCommand("process launch --stop-at-entry")


def feed_input(debugger, command, result, internal_dict):
	target = debugger.GetSelectedTarget()
	process = target.GetProcess()

	# Simulate input for scanf
	process.PutSTDIN(command + "\n")
	# process.flush()
	result.PutCString(f"Injected input: {command}")
	import time
	time.sleep(0.1)
	stdo = process.GetSTDOUT(1024)
	if stdo:
		print(f"================== >>>>>>>>>>>>>>> STDO: {stdo}")
	else:
		print(f"NO STDOUT AVAILABLE")

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

def cmd_pyvers(debugger,command,result,dict):
	import sys
	print(f"Python path: {sys.executable} ...")
	print(f"System version: {sys.version} ...")
	pass
	
def close_application():
#	global driver

	print("close_application()")
#	Stop all running tasks in the thread pool
	print("KILLING PROCESS")
	# os._exit(1)

	global driver
	driver.getTarget().GetProcess().Kill()
	if SettingsHelper().getValue(SettingsValues.ExitLLDBOnAppExit):
		driver.debugger.Terminate()


	
def StartLLDBPyGUI(debugger, command, result, dict):
	
	cmd_banner(debugger, command, result, dict)
	
	debugger.SetAsync(False)
	
#		debugger.SetAsync(True)
	# pyGUIApp = QApplication([])
	pyGUIApp = QApplication(sys.argv)  # Pass sys.argv explicitly!
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
	# sys.exit(pyGUIApp.exec())
	# pyGUIApp.exec()
	try:
		sys.exit(pyGUIApp.exec())
	except SystemExit:
		print("PyQt application exited cleanly.")
	