#!/usr/bin/env python3
# import lief

import sys
from datetime import datetime

import lldb
from PyQt6 import QtCore
# from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication

from MainWindow import MainWindow

if __name__ == "__main__":
	print("Run only as script from LLDB... Not as standalone program!")

from constants import *
from config import *

pyGUIApp = None

# import lldb
import struct

import os



def bring_app_to_front_on_dialog(frame, bp_loc, internal_dict):
	"""
	Breakpoint command script that brings the app to the front when a dialog appears.
	"""

	target = lldb.debugger.GetSelectedTarget()
	if not target:
		return

	thread = target.GetProcess().GetThreadAtIndex(0)
	if not thread:
		return
	thread.StepOut()
	# Get the name of the debugged process
	app_name = os.path.basename(target.GetExecutable().GetDirectory())

	# Construct and execute the AppleScript to bring the app to the front
	applescript_command = f'tell application "{app_name}" to activate'
	print(f"Brought '{app_name}' to the foreground for user input.")
	os.system(f"osascript -e '{applescript_command}'")


def extract_code_signature(path):
	# Load binary with LLDB (optional, for introspection)
	debugger = lldb.SBDebugger.Create()
	debugger.SetAsync(False)
	target = debugger.CreateTarget(path)

	if not target.IsValid():
		print("Failed to create LLDB target.")
		return

	# Read binary file directly
	with open(path, "rb") as f:
		data = f.read()

	# Mach-O header offset (skip fat header if needed)
	offset = 0
	magic = struct.unpack_from("<I", data, offset)[0]

	if magic == 0xcafebabe:
		print("Fat binary detected. Skipping to appropriate architecture...")
		nfat_arch = struct.unpack_from(">I", data, 4)[0]
		for i in range(nfat_arch):
			arch_offset = 8 + i * 20
			cpu_type, cpu_subtype, offset_arch = struct.unpack_from(">III", data, arch_offset)
			print(f"Arch {i}: CPU type={cpu_type}, offset={offset_arch}")
			offset = offset_arch
			break  # You can refine this to pick the right arch

	# Parse Mach-O header
	ncmds = struct.unpack_from("<I", data, offset + 16)[0]
	cmd_offset = offset + 32  # Start of load commands

	for i in range(ncmds):
		cmd, cmdsize = struct.unpack_from("<II", data, cmd_offset)
		if cmd == 0x1d:  # LC_CODE_SIGNATURE
			dataoff, datasize = struct.unpack_from("<II", data, cmd_offset + 8)
			print(f"Found LC_CODE_SIGNATURE at offset {dataoff}, size {datasize}")
			break
		cmd_offset += cmdsize
	else:
		print("LC_CODE_SIGNATURE not found.")
		return

	# Extract and parse signature blob
	blob = data[dataoff:dataoff + datasize]
	magic, length, count = struct.unpack_from(">III", blob, 0)
	print(f"SuperBlob: magic=0x{magic:x}, length={length}, count={count}")

	for i in range(count):
		index_offset = 12 + i * 8
		blob_type, blob_offset = struct.unpack_from(">II", blob, index_offset)
		print(f"Blob {i}: type=0x{blob_type:x}, offset={blob_offset}")

		if blob_type == 0xfade0c02:  # CSSLOT_CODEDIRECTORY
			cd_blob = blob[blob_offset:]
			version, flags, hash_offset = struct.unpack_from(">III", cd_blob, 0)
			print(f"CodeDirectory: version={version}, flags=0x{flags:x}, hash_offset={hash_offset}")
			# Add hash validation here if needed


# # Example usage
# extract_code_signature("/path/to/YourExecutable")


def __lldb_init_module(debugger, internal_dict):
	# print(f"Init my LLDB ...")
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
	ci.HandleCommand(
		f"command script add -h '({PROMPT_TEXT}) Start the {APP_NAME}.' -f LLDBPyGUING.startLLDBPyGUING pygng",
		res)
	# ci.HandleCommand(f"command script add -h '({PROMPT_TEXT}) Start the {APP_NAME}.' -f LLDBPyGUI.startLLDBPyGUI2 pyg2",
	#                  res)
	#
	ci.HandleCommand(
		f"command script add -h '({PROMPT_TEXT}) Display {APP_NAME} banner.' --function LLDBPyGUING.cmd_intro intro",
		res)

	# strMgr = StringManager()
	# print(f'{strMgr.format_with_args("{1} scored higher than {0}.", "Alice", "Kim-David")}')
	# strMgr.getString(StringPatterns.listener_pfx)
	# print(get_string(StringPatterns.teset, "Kim", "Jete"))


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


def exit_lldb():
	print("🛑 Quitting LLDB...")
	# (lldb.SBDebugger.
	global debgr
	debgr.Terminate()
	sys.exit(0)


global debgr


def startLLDBPyGUING(debugger, command, result, dict):
	# # debugger = lldb.SBDebugger.Create()
	# debugger.SetAsync(False)
	#
	# binary_path = "/Applications/SoundSource.app/Contents/MacOS/SoundSource"
	# target = debugger.CreateTargetWithFileAndArch(binary_path, "arm64")
	#
	# if not target.IsValid():
	#     print("Failed to create target.")
	#
	# funcs = target.FindFunctions("main")
	# print(f"funcs: {len(funcs)} => {funcs}")
	# if funcs.GetSize() > 0:
	#     symbol = funcs.GetContextAtIndex(0).GetSymbol()
	#
	#     print("Resolved symbol name:", symbol.GetName())
	#     print("Start address (file):", symbol.GetStartAddress().GetFileAddress())
	#     print("Start address (load):", symbol.GetStartAddress().GetLoadAddress(target))
	#     print("Symbol size:", symbol.GetSize())
	#
	#     size = symbol.GetSize()
	#     estimated_count = size // 4
	#     print(f"symbol.GetStartAddress(): {symbol.GetStartAddress()}, {symbol.GetStartAddress().GetLoadAddress(target)}, estimated_count: {estimated_count} ...")
	#     insts = target.ReadInstructions(symbol.GetStartAddress(), int(estimated_count))
	#     for inst in insts:
	#         print(inst)
	# return

	# trySwift = TrySwift(debugger)
	# trySwift.tryswift()
	# return
	# import PyQt6.QtCore.QCoreApplication
	# from bultinThreadTest import  startTest
	# startTest()
	# return

	from macholib.MachO import MachO

	macho = MachO("/Volumes/Data/dev/python/LLDBGUI/_testtarget/cocoa_windowed_objc2")
	print(f"macho.headers: {macho.headers} / {len(macho.headers)}")
	for header in macho.headers:
		print(f"header.commands: {header.commands} / {len(header.commands)}")
		for cmd in header.commands:
			print(f"cmd[0].cmd: {cmd[0].cmd}")
			if cmd[0].cmd == 0x1d:  # LC_CODE_SIGNATURE
				print("Found LC_CODE_SIGNATURE:", cmd[1])

	# # ELF
	# binary = lief.parse("/usr/bin/ls")
	# for section in binary.sections:
	#     print(section.name, section.virtual_address)
	#
	# # PE
	# binary = lief.parse("C:\\Windows\\explorer.exe")
	#
	# if rheader := pe.rich_header:
	#     print(rheader.key)

	# Mach-O
	# binary = lief.parse("/usr/bin/ls")
	# print(f"LIEF STARTED ... ")
	# for fixup in binary.dyld_chained_fixups:
	#     print(fixup)
	# print(f"LIEF ENDED!!!")

	global debgr
	debgr = debugger
	cmd_intro(debugger, command, result, dict)

	debugger.SetAsync(False)

	# debugger.SetAsync(True)

	# print(sys.argv)
	# print(sys)
	global pyGUIApp
	if pyGUIApp is None:
		pyGUIApp = QApplication(sys.argv)  # Pass sys.argv explicitly!

	# global pyCoreGUIApp
	# if pyCoreGUIApp is None:
	# 	pyCoreGUIApp = QCoreApplication(sys.argv)

	pyGUIApp.aboutToQuit.connect(exit_lldb)
	ConfigClass.initIcons()
	pyGUIApp.setWindowIcon(ConfigClass.iconBugGreen)

	# driver = DebugDriver(debugger)
	pyGUIWindow = MainWindow(None, debugger)
	pyGUIWindow.app = pyGUIApp
	pyGUIWindow.show()

	tmrAppStarted = QtCore.QTimer()
	tmrAppStarted.singleShot(1, pyGUIWindow.onQApplicationStarted)

	try:
		sys.exit(pyGUIApp.exec())
	except SystemExit:
		print("PyQt application exited cleanly.")

# Example usage
# extract_code_signature("/Volumes/Data/dev/python/LLDBGUI/_testtarget/cocoa_windowed_objc2")

# def exit_lldb():
#     print("🛑 Quitting LLDB...")
#     lldb.SBDebugger.Terminate()
#     sys.exit(0)
#
# def run_gui():
#     app = QApplication(sys.argv)
#     window = QMainWindow()
#     window.setWindowTitle("LLDB PyQt6 GUI")
#     window.resize(400, 300)
#     window.show()
#
#     # Connect the app's quit signal to LLDB termination
#     app.aboutToQuit.connect(exit_lldb)
#
#     app.exec()
#
# # Call this from your LLDB Python script
# run_gui()
