import lldb
import os
from os.path import dirname, realpath

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap

APP_NAME = "LLDBPyGUI"
APP_VERSION = "0.0.5"
APP_VERSION_DESC = "Complete new base, rebuilt and cleaned version"
APP_BUILD = "DEV PREVIEW (nightly build)"
APP_VERSION_AND_BUILD = APP_VERSION + " - " + APP_BUILD
APP_RELEASE_DATE = "2025-10-22 - 12:52:28"
APP_BUILD = "0.0.5.01"
PROMPT_TEXT = "LLDBPyGUI"
WINDOW_SIZE = 680


class ConfigClass():
	companyName = "DaVe_inc"
	appName = "LLDBPyGUI"

	initialCommand = "w s v idx"  # "breakpoint set -a 0x100003f6a" # re read
	fontStr = "Courier New"
	font = QFont(fontStr)  # ("Monaco") #("Courier New")
	fontStr12 = "'Courier New' 12px"
	font12 = QFont(fontStr12)  # ("Monaco") #("Courier New")

	fontBold = font
	fontBold.setBold(True)
	#	font.setFixedPitch(True)
	fontSize = "12"
	fontSizePx = fontSize + "px"
	fontStrComplete = f"font: {fontSizePx} '{fontStr}';"

	fontTitle = QFont()
	fontTitle.setPointSize(18)

	autofindSourcecodeFileExts = ['.c', '.cpp', '.m', '.x', '.xm', '.swift']

	supportURL = "https://pylldbgui.kimhauser.ch/support"
	githubURL = "https://github.com/jetedonner/pyLLDBGUI"
	githubPagesURL = "https://jetedonner.github.io/"

	lldbConsoleCmdHistory = "./resources/histories/lldb_console_history.json"

	testBPsFilename = "/Volumes/Data/dev/python/LLDBPyGUI/breakpoints-hello_library_exec.bpson"  # "/Volumes/Data/dev/python/LLDBPyGUI/resources/bps/testbps_withSubFunc5.json" # "/Volumes/Data/dev/_reversing/disassembler/LLDBPyGUI/pyLLDBGUI/LLDBPyGUI/testtarget/testbps_withSubFunc5.json"
	#	testTarget = "/Volumes/Data/dev/_reversing/disassembler/LLDBPyGUI/pyLLDBGUI/LLDBPyGUI/testtarget/hello_world_test"
	#	testTargetSource = "/Volumes/Data/dev/_reversing/disassembler/LLDBPyGUI/pyLLDBGUI/LLDBPyGUI/testtarget/hello_world_test.c"

	# # SIMPLE
	# testTarget =  "./_testtarget/a_hello_world_test" #amicable_numbers" #a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
	# testTargetSource = "./_testtarget/a_hello_world_test.c" #amicable_numbers.c" #a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"
	# testTargetArch = "x86_64-apple-macosx15.1.1"
	# testTargetArgs = ""

	#
	# testTarget2 =  "./_testtarget/a_hello_world_test" #amicable_numbers" #a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
	# testTargetSource2 = "./_testtarget/a_hello_world_test.c" #amicable_numbers.c" #a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"

	# EXTENDED
	# testTarget = "./_testtarget/a_hello_world_test_ext"  # amicable_numbers" #a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
	# testTargetSource = "./_testtarget/a_hello_world_test_ext.c"  # amicable_numbers.c" #a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"

	# # SIMPLE WITH LIB / DYLIB
	# testTarget = "./_testtarget/hello_library_exec"  # amicable_numbers" #a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
	# testTargetSource = "./_testtarget/hello_library_exec.c"  # amicable_numbers.c" #a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"
	# testTargetArch = "arm64-apple-macosx15.1.0"
	# testTargetArgs = ""

	# # # # SIMPLE WITH TWO LIBs / DYLIBs --- 222 !!!!!
	testTarget = "./_testtarget/hello_library_exec2"  # amicable_numbers" #a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
	testTargetSource = "./_testtarget/hello_library_exec2.c"  # amicable_numbers.c" #a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"
	testTargetArch = "arm64-apple-macosx15.1.0"
	# testTargetArgs = ""

	# testTarget = "./_testtarget/SwiftTestApp4LLDBGUI/SwiftTestApp4LLDBGUI.app/Contents/MacOS/SwiftTestApp4LLDBGUI"  # amicable_numbers" #a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
	# testTargetSource = "./_testtarget/SwiftTestApp4LLDBGUI/SwiftTestApp4LLDBGUI/ViewController.swift"  # amicable_numbers.c" #a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"
	# testTargetArch = lldb.LLDB_ARCH_DEFAULT # "arm64-apple-macosx15.1.0"


	# testTarget = "/Applications/SoundSource.app/Contents/MacOS/SoundSource"  # amicable_numbers" #a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
	# testTargetSource = "" # "./_testtarget/hello_library_exec2.c"  # amicable_numbers.c" #a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"
	# testTargetArch = "arm64"
	# testTargetTriple = "arm64-apple-macosx11.0.0"

	# testTarget = "./_testtarget/LLDBGUISwiftTestApp/Build/Products/Debug/LLDBGUISwiftTestApp.app/Contents/MacOS/LLDBGUISwiftTestApp"  # amicable_numbers" #a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
	# testTargetSource = "./_testtarget/LLDBGUISwiftTestApp/LLDBGUISwiftTestApp/ViewController.swift"  # amicable_numbers.c" #a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"
	# testTargetArch = "arm64-apple-macosx15.1.0"

	# / Volumes / Data / dev / python / LLDBGUI / _testtarget / LLDBGUISwiftTestApp / LLDBGUISwiftTestApp / ViewController.swift

	testTarget2 = "./_testtarget/a_hello_world_test"  # amicable_numbers" #a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
	testTargetSource2 = "./_testtarget/a_hello_world_test.c"  # amicable_numbers.c" #a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"

	# testTarget = "./_testtarget/cocoa_windowed_objc2"
	# testTargetSource = "./_testtarget/cocoa_windowed_objc2.m"
	# testTargetArch = "x86_64-apple-macosx15.1.1"

	# testTarget = "/Volumes/Data/dev/python/LLDBGUI/_testtarget/ObjectiveCInputBox/Build/Products/Debug/ObjectiveCInputBox.app/Contents/MacOS/ObjectiveCInputBox" # "/Users/dave/Library/Developer/Xcode/DerivedData/ObjectiveCInputBox-ceppdxmjceebymdsshdrpjammbuo/Build/Products/Debug/ObjectiveCInputBox.app/Contents/MacOS/ObjectiveCInputBox"
	# testTargetSource = "/Volumes/Data/dev/python/LLDBGUI/_testtarget/ObjectiveCInputBox/ObjectiveCInputBox/AppDelegate.m"
	# # testTargetArch = "x86_64-apple-macosx15.1.1"
	# testTargetArch = "arm64-apple-macosx15.1.0"

	# SCANF / AMICABLE
	# testTarget = "./_testtarget/amicable_numbers" #a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
	# testTargetSource = "./_testtarget/amicable_numbers.c" #a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"
	# testTargetArch = "x86_64-apple-macosx15.1.1"
	# testTargetArgs = ""

	# GUI
	# testTarget = "./_testtarget/cocoa_windowed_objc2"  # a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
	# testTargetSource = "./_testtarget/cocoa_windowed_objc2.m"  # a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"

	# SWIFT (NOT SWIFTUI)
	# testTarget = "./_testtarget/xcode_projects/SwiftREPLTestApp/Debug/SwiftREPLTestApp.app/Contents/MacOS/SwiftREPLTestApp"  # a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
	# testTargetSource = "./_testtarget/xcode_projects/SwiftREPLTestApp/SwiftREPLTestApp/ViewController.swift"  # a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"

	# testTargetArch = "x86_64-apple-macosx15.1.1"
	# testTargetArgs = ""

	startTestTarget = True
	settingsFilename = "./LLDBPyGUI_Settings.ini"
	recentFilesFilename = "./LLDBPyGUI_RecentFiles.ini"

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
	pixOpen = None
	pixLoad = None
	pixReload = None
	pixTrash = None

	pixName = None
	pixSearch = None
	pixUp = None
	pixFunction = None
	pixClose = None

	pixSystemInt = None
	pixString = None
	pixYingYang = None

	iconEyeRed = None
	iconEyeGrey = None
	iconEyeGreen = None

	iconBug = None
	iconBugGreen = None
	iconStd = None
	iconBPEnabled = None
	iconBPDisabled = None
	iconName = None

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
	iconClose = None
	iconFunction = None
	iconLog = None
	iconLogBW = None

	colorGreen = QColor(0, 255, 0, 128)
	colorBurgundy = QColor(115, 0, 57, 255)
	colorTransparent = QColor(0, 0, 0, 0)
	colorSelected = QColor("#68000a")

	controlFlowLineWidth = 1
	controlFlowLineWidthHover = 2

	resRootDir = "./"

	defaultMemJumpDist = 0x100

	@staticmethod
	def initIcons():
		project_root = dirname(realpath(__file__))
		resources_root = os.path.join(project_root, 'resources', 'img')
		ConfigClass.resRootDir = resources_root

		ConfigClass.iconStd = QIcon()

		ConfigClass.pixGears = QPixmap(os.path.join(resources_root, 'gears.png')).scaled(QSize(48, 48))
		ConfigClass.pixGearsGrey = QPixmap(os.path.join(resources_root, 'gears_grey.png')).scaled(QSize(48, 48))
		ConfigClass.pixBug = QPixmap(os.path.join(resources_root, 'bug.png')).scaled(QSize(18, 18))
		ConfigClass.pixBugLg = QPixmap(os.path.join(resources_root, 'bug.png')).scaled(QSize(48, 48))
		ConfigClass.pixBugGreen = QPixmap(os.path.join(resources_root, 'bug_green.png')).scaled(QSize(18, 18))
		ConfigClass.pixDelete = QPixmap(os.path.join(resources_root, 'delete.png')).scaled(QSize(48, 48))
		ConfigClass.pixSave = QPixmap(os.path.join(resources_root, 'save.png')).scaled(QSize(48, 48))
		ConfigClass.pixOpen = QPixmap(os.path.join(resources_root, 'open-folder.png')).scaled(QSize(48, 48))

		ConfigClass.pixName = QPixmap(os.path.join(resources_root, 'id-card.png')).scaled(QSize(48, 48))
		ConfigClass.pixSearch = QPixmap(os.path.join(resources_root, 'magnifying-glass-64x64.png')).scaled(
			QSize(32, 32))
		ConfigClass.pixUp = QPixmap(os.path.join(resources_root, 'upload.png')).scaled(QSize(32, 32))
		ConfigClass.pixFunction = QPixmap(os.path.join(resources_root, 'function.png')).scaled(QSize(18, 18))
		ConfigClass.pixClose = QPixmap(os.path.join(resources_root, 'close.png')).scaled(QSize(18, 18))
		ConfigClass.pixSystemInt = QPixmap(os.path.join(resources_root, 'system-integration.png')).scaled(QSize(18, 18))
		ConfigClass.pixString = QPixmap(os.path.join(resources_root, 'html.png')).scaled(QSize(18, 18))
		ConfigClass.pixYingYang = QPixmap(os.path.join(resources_root, 'YinYang_RedBlack_Roses_35percent.png')).scaled(
			QSize(300, 300))

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

		ConfigClass.iconInfo = QIcon(os.path.join(resources_root, 'info.png'))
		#
		ConfigClass.iconEyeRed = QIcon(os.path.join(resources_root, 'eye_red.png'))
		ConfigClass.iconEyeGrey = QIcon(os.path.join(resources_root, 'eye_grey.png'))
		ConfigClass.iconEyeGreen = QIcon(os.path.join(resources_root, 'eye_green.png'))

		ConfigClass.iconBug = QIcon(os.path.join(resources_root, 'bug.png'))
		ConfigClass.iconBugGreen = QIcon(os.path.join(resources_root, 'bug_green.png'))
		ConfigClass.iconBPEnabled = ConfigClass.iconBug  # QIcon(os.path.join(resources_root, 'bug.png'))
		ConfigClass.iconBPDisabled = QIcon(os.path.join(resources_root, 'bug_bw_greyscale.png'))
		ConfigClass.iconPause = QIcon(os.path.join(resources_root, 'Pause_first.png'))
		ConfigClass.iconSettings = QIcon(os.path.join(resources_root, 'settings.png'))
		ConfigClass.iconTrash = QIcon(os.path.join(resources_root, 'delete.png'))
		#
		ConfigClass.iconResume = QIcon(os.path.join(resources_root, 'resume.png'))
		ConfigClass.iconStepOver = QIcon(os.path.join(resources_root, 'stepOver.png'))
		ConfigClass.iconStepInto = QIcon(os.path.join(resources_root, 'stepInto.png'))
		ConfigClass.iconStepOut = QIcon(os.path.join(resources_root, 'stepOut.png'))
		ConfigClass.iconStop = QIcon(os.path.join(resources_root, 'stop.png'))

		ConfigClass.iconName = QIcon(os.path.join(resources_root, 'id-card.png'))
		ConfigClass.iconClose = QIcon(os.path.join(resources_root, 'close.png'))
		ConfigClass.iconFunction = QIcon(os.path.join(resources_root, 'function.png'))
		ConfigClass.iconLog = QIcon(os.path.join(resources_root, 'log-file.png'))
		ConfigClass.iconLogBW = QIcon(os.path.join(resources_root, 'log-file-bw.png'))
