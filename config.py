#!/usr/bin/env python3

import os
import sys
import enum

from os.path import abspath
from os.path import dirname, realpath
from os import getcwd, path

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

APP_NAME = "LLDBPyGUI"
APP_VERSION = "0.0.2 - DEV PREVIEW"
APP_RELEASE_DATE = "2025-06-25 - 09:16:18"
APP_BUILD = "002.01"
PROMPT_TEXT = "LLDBPyGUI"
#WINDOW_SIZE = 512
WINDOW_SIZE = 680

#
# User configurable options
#
CONFIG_ENABLE_COLOR = 1
# light or dark mode
CONFIG_APPEARANCE = "light"
# display the instruction bytes in disassembler output
CONFIG_DISPLAY_DISASSEMBLY_BYTES = 1
# the maximum number of lines to display in disassembler output
CONFIG_DISASSEMBLY_LINE_COUNT = 8
# x/i and disas output customization - doesn't affect context disassembler output
CONFIG_USE_CUSTOM_DISASSEMBLY_FORMAT = 1
# enable all the register command shortcuts
CONFIG_ENABLE_REGISTER_SHORTCUTS = 1
# display stack contents on context stop
CONFIG_DISPLAY_STACK_WINDOW = 0
CONFIG_DISPLAY_FLOW_WINDOW = 0
# display data contents on context stop - an address for the data must be set with "datawin" command
CONFIG_DISPLAY_DATA_WINDOW = 0
# disassembly flavor 'intel' or 'att' - default is Intel unless AT&T syntax is your cup of tea
CONFIG_FLAVOR = "intel"

# setup the logging level, which is a bitmask of any of the following possible values (don't use spaces, doesn't seem to work)
#
# LOG_VERBOSE LOG_PROCESS LOG_THREAD LOG_EXCEPTIONS LOG_SHLIB LOG_MEMORY LOG_MEMORY_DATA_SHORT LOG_MEMORY_DATA_LONG LOG_MEMORY_PROTECTIONS LOG_BREAKPOINTS LOG_EVENTS LOG_WATCHPOINTS
# LOG_STEP LOG_TASK LOG_ALL LOG_DEFAULT LOG_NONE LOG_RNB_MINIMAL LOG_RNB_MEDIUM LOG_RNB_MAX LOG_RNB_COMM  LOG_RNB_REMOTE LOG_RNB_EVENTS LOG_RNB_PROC LOG_RNB_PACKETS LOG_RNB_ALL LOG_RNB_DEFAULT
# LOG_DARWIN_LOG LOG_RNB_NONE
#
# to see log (at least in macOS)
# $ log stream --process debugserver --style compact
# (or whatever style you like)
CONFIG_LOG_LEVEL = "LOG_NONE"

# removes the offsets and modifies the module name position
# reference: https://lldb.llvm.org/formats.html
CUSTOM_DISASSEMBLY_FORMAT = "\"{${function.initial-function}{${function.name-without-args}} @ {${module.file.basename}}:\n}{${function.changed}\n{${function.name-without-args}} @ {${module.file.basename}}:\n}{${current-pc-arrow} }${addr-file-or-load}: \""

# the colors definitions - don't mess with this
if CONFIG_ENABLE_COLOR:
		RESET =     "\033[0m"
		BOLD =      "\033[1m"
		UNDERLINE = "\033[4m"
		BLINK =		"\033[5m"
		REVERSE =   "\033[7m"
		NORMAL =    "\033[22m"
		BLACK =     "\033[30m"
		RED =       "\033[31m"
		GREEN =     "\033[32m"
		YELLOW =    "\033[33m"
		BLUE =      "\033[34m"
		MAGENTA =   "\033[35m"
		CYAN =      "\033[36m"
		WHITE =     "\033[37m"
else:
		RESET =     ""
		BOLD =      ""
		UNDERLINE = ""
		REVERSE =   ""
		BLACK =     ""
		RED =       ""
		GREEN =     ""
		YELLOW =    ""
		BLUE =      ""
		MAGENTA =   ""
		CYAN =      ""
		WHITE =     ""
	
# default colors - modify as you wish
# since these are just strings modes can be combined
if CONFIG_APPEARANCE == "light":
		COLOR_REGVAL           = BLACK
		COLOR_REGNAME          = GREEN
		COLOR_CPUFLAGS         = BOLD + UNDERLINE + MAGENTA
		COLOR_SEPARATOR        = BOLD + BLUE
		COLOR_HIGHLIGHT_LINE   = RED
		COLOR_REGVAL_MODIFIED  = RED
		COLOR_SYMBOL_NAME      = BLUE
		COLOR_CURRENT_PC       = RED
		COLOR_CONDITIONAL_YES  = REVERSE + GREEN
		COLOR_CONDITIONAL_NO   = REVERSE + RED
		COLOR_HEXDUMP_HEADER   = BLUE
		COLOR_HEXDUMP_ADDR     = BLACK
		COLOR_HEXDUMP_DATA     = BLACK
		COLOR_HEXDUMP_ASCII    = BLACK
		COLOR_COMMENT          = GREEN
elif CONFIG_APPEARANCE == "dark":
		COLOR_REGVAL           = WHITE
		COLOR_REGNAME          = GREEN
		COLOR_CPUFLAGS         = BOLD + UNDERLINE + MAGENTA
		COLOR_SEPARATOR        = CYAN
		COLOR_HIGHLIGHT_LINE   = RED
		COLOR_REGVAL_MODIFIED  = RED
		COLOR_SYMBOL_NAME      = BLUE
		COLOR_CURRENT_PC       = RED
		COLOR_CONDITIONAL_YES  = REVERSE + GREEN
		COLOR_CONDITIONAL_NO   = REVERSE + RED
		COLOR_HEXDUMP_HEADER   = BLUE
		COLOR_HEXDUMP_ADDR     = WHITE
		COLOR_HEXDUMP_DATA     = WHITE
		COLOR_HEXDUMP_ASCII    = WHITE
		COLOR_COMMENT          = GREEN # XXX: test and change
else:
		print("[-] Invalid CONFIG_APPEARANCE value.")
		

g_current_target = ""
g_target_hash = ""
g_home = ""
g_db = ""
g_dbdata = {}

JMP_MNEMONICS = ("call", "jmp", "jne", "jz", "je", "jnz", "jle", "jl", "jge", "jg")
JMP_MNEMONICS_EXCLUDE = ("jmpq")


class ConfigClass():
	
	companyName = "DaVe_inc"
	appName = "LLDBPyGUI"
	
	initialCommand = "w s v idx" # "breakpoint set -a 0x100003f6a" # re read
	fontStr = "Courier New"
	font = QFont(fontStr) # ("Monaco") #("Courier New")
	fontSize = "12"
	fontSizePx = fontSize + "px"

#	font.setFixedPitch(True)
	
	supportURL = "https://pylldbgui.kimhauser.ch/support"
	githubURL = "https://github.com/jetedonner/pyLLDBGUI"
	testBPsFilename = "/Volumes/Data/dev/python/LLDBPyGUI/resources/bps/testbps_withSubFunc5.json" # "/Volumes/Data/dev/_reversing/disassembler/LLDBPyGUI/pyLLDBGUI/LLDBPyGUI/testtarget/testbps_withSubFunc5.json"
#	testTarget = "/Volumes/Data/dev/_reversing/disassembler/LLDBPyGUI/pyLLDBGUI/LLDBPyGUI/testtarget/hello_world_test"
#	testTargetSource = "/Volumes/Data/dev/_reversing/disassembler/LLDBPyGUI/pyLLDBGUI/LLDBPyGUI/testtarget/hello_world_test.c"
	# testTarget =  "./_testtarget/a_hello_world_test" #amicable_numbers" #a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
	# testTargetSource = "./_testtarget/a_hello_world_test.c" #amicable_numbers.c" #a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"

	testTarget = "./_testtarget/amicable_numbers" #a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
	testTargetSource = "./_testtarget/amicable_numbers.c" #a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"

	testTargetArch = "x86_64-apple-macosx15.1.1"
	testTargetArgs = ""
	settingsFilename = "./LLDBPyGUI_Settings.ini"

	githubPagesURL = "https://jetedonner.github.io/"
	
	toolbarIconSize = 24
	currentDebuggerSubTab = 1
	
	iconLeft = None
	iconRight = None
	
	iconTest = None
	iconGears = None
	iconGearsGrey = None
	iconAdd = None
	iconSave = None
	iconLoad = None
	iconReload = None
	iconInfo = None
	iconShrink = None
	iconClear = None
	
	pixGears = None
	pixGearsGrey = None
	pixBug = None
	pixBugLg = None
	pixBugGreen = None
	pixDelete = None
	pixAdd = None
	pixInfo = None
	pixSave = None
	pixLoad = None
	pixReload = None
	pixTrash = None
	
	iconEyeRed = None
	iconEyeGrey = None
	iconEyeGreen = None
	
	iconBug = None
	iconBugGreen = None
	iconStd = None
	iconBPEnabled = None
	iconBPDisabled = None
	iconBin = None
	iconPause = None
	iconPlay = None
	iconSettings = None
	iconTrash = None
	iconTerminal = None
	iconProcess = None
	iconAnon = None
	iconGlasses = None
	iconMarkdown = None
	
	iconStepOver = None
	iconStepInto = None
	iconStepOut = None
	
	iconResume = None
	
	iconRestart = None
	iconStop = None
	
	iconGithub = None
	
	colorGreen = QColor(0, 255, 0, 128)
	colorTransparent = QColor(0, 0, 0, 0)
	
	@staticmethod
	def initIcons():
		project_root = dirname(realpath(__file__))
		resources_root = os.path.join(project_root, 'resources', 'img')
		
		ConfigClass.iconStd = QIcon()
		
		ConfigClass.pixGears = QPixmap(os.path.join(resources_root, 'gears.png')).scaled(QSize(48, 48))
		ConfigClass.pixGearsGrey = QPixmap(os.path.join(resources_root, 'gears_grey.png')).scaled(QSize(48, 48))
		ConfigClass.pixBug = QPixmap(os.path.join(resources_root, 'bug.png')).scaled(QSize(18, 18))
		ConfigClass.pixBugLg = QPixmap(os.path.join(resources_root, 'bug.png')).scaled(QSize(48, 48))
		ConfigClass.pixBugGreen = QPixmap(os.path.join(resources_root, 'bug_green.png')).scaled(QSize(18, 18))
		ConfigClass.pixDelete = QPixmap(os.path.join(resources_root, 'delete.png')).scaled(QSize(48, 48))
#		ConfigClass.pixAdd = QPixmap(os.path.join(resources_root, 'add.png')).scaled(QSize(18, 18))
		ConfigClass.pixSave = QPixmap(os.path.join(resources_root, 'save.png')).scaled(QSize(48, 48))
#		ConfigClass.pixLoad = QPixmap(os.path.join(resources_root, 'folder.png')).scaled(QSize(18, 18))
#		ConfigClass.pixReload = QPixmap(os.path.join(resources_root, 'reload.png')).scaled(QSize(18, 18))
#		ConfigClass.pixInfo = QPixmap(os.path.join(resources_root, 'info.png')).scaled(QSize(18, 18))
#		ConfigClass.pixTrash = QPixmap(os.path.join(resources_root, 'delete.png')).scaled(QSize(18, 18))
#		ui->label->setStyleSheet("border-image:url(:/2.png);");
#		ui->label->setPixmap(pix);

		ConfigClass.iconClear = QIcon(os.path.join(resources_root, 'clear.png'))
		ConfigClass.iconShrink = QIcon(os.path.join(resources_root, 'shrink.png'))
		ConfigClass.iconMarkdown = QIcon(os.path.join(resources_root, 'markdown.png'))
		ConfigClass.iconGlasses = QIcon(os.path.join(resources_root, 'glasses.png'))
		ConfigClass.iconAnon = QIcon(os.path.join(resources_root, 'hacker.png'))
		ConfigClass.iconProcess = QIcon(os.path.join(resources_root, 'process.png'))
		ConfigClass.iconTerminal = QIcon(os.path.join(resources_root, 'terminal.png'))
		ConfigClass.iconTest = QIcon(os.path.join(resources_root, 'test.png'))
		ConfigClass.iconLeft = QIcon(os.path.join(resources_root, 'left-arrow_blue.png'))
		ConfigClass.iconRight = QIcon(os.path.join(resources_root, 'right-arrow_blue.png'))
#		
		ConfigClass.iconGears = QIcon(os.path.join(resources_root, 'gears.png'))
		ConfigClass.iconGearsGrey = QIcon(os.path.join(resources_root, 'gears_grey.png'))
#		
#		ConfigClass.iconAdd = QIcon(os.path.join(resources_root, 'add.png'))
#		ConfigClass.iconSave = QIcon(os.path.join(resources_root, 'save.png'))
#		ConfigClass.iconLoad = QIcon(os.path.join(resources_root, 'folder.png'))
		ConfigClass.iconInfo = QIcon(os.path.join(resources_root, 'info.png'))
#		
		ConfigClass.iconEyeRed = QIcon(os.path.join(resources_root, 'eye_red.png'))
		ConfigClass.iconEyeGrey = QIcon(os.path.join(resources_root, 'eye_grey.png'))
		ConfigClass.iconEyeGreen = QIcon(os.path.join(resources_root, 'eye_green.png'))
		
		ConfigClass.iconBug = QIcon(os.path.join(resources_root, 'bug.png'))
		ConfigClass.iconBugGreen = QIcon(os.path.join(resources_root, 'bug_green.png'))
		ConfigClass.iconBPEnabled = ConfigClass.iconBug #QIcon(os.path.join(resources_root, 'bug.png'))
		ConfigClass.iconBPDisabled = QIcon(os.path.join(resources_root, 'bug_bw_greyscale.png'))
#		ConfigClass.iconBin = QIcon(os.path.join(resources_root, 'recyclebin.png'))
		ConfigClass.iconPause = QIcon(os.path.join(resources_root, 'Pause_first.png'))
#		ConfigClass.iconPlay = QIcon(os.path.join(resources_root, 'play-circular-button.png'))
		ConfigClass.iconSettings = QIcon(os.path.join(resources_root, 'settings.png'))
		ConfigClass.iconTrash = QIcon(os.path.join(resources_root, 'delete.png'))
#		
#		ConfigClass.iconStepOver = QIcon(os.path.join(resources_root, 'step_over_ng2.png'))
#		ConfigClass.iconStepInto = QIcon(os.path.join(resources_root, 'step_into.png'))
#		ConfigClass.iconStepOut = QIcon(os.path.join(resources_root, 'step_out_ng.png'))
#		
		ConfigClass.iconResume = QIcon(os.path.join(resources_root, 'resume.png'))
		ConfigClass.iconStepOver = QIcon(os.path.join(resources_root, 'stepOver.png'))
		ConfigClass.iconStepInto = QIcon(os.path.join(resources_root, 'stepInto.png'))
		ConfigClass.iconStepOut = QIcon(os.path.join(resources_root, 'stepOut.png'))
#		ConfigClass.iconRestart = QIcon(os.path.join(resources_root, 'Restart.png'))
		ConfigClass.iconStop = QIcon(os.path.join(resources_root, 'stop.png'))
#		
#		ConfigClass.iconGithub = QIcon(os.path.join(resources_root, 'github.png'))
		
class ByteGrouping(enum.Enum):
	NoGrouping = ("No Grouping", 1) #"No grouping"
	TwoChars = ("Two", 2) #"Two characters"
	FourChars = ("Four", 4) #"Four characters"
	EightChars = ("Eight", 8) #"Four characters"