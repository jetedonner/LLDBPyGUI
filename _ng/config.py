import os
from os.path import dirname, realpath

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap

APP_NAME = "LLDBPyGUI"
APP_VERSION = "0.0.3"
APP_VERSION_DESC = "Complete new, rebuilt and clean version"
APP_BUILD = "DEV PREVIEW (clean)"
APP_VERSION_AND_BUILD = APP_VERSION + " - " + APP_BUILD
APP_RELEASE_DATE = "2025-08-14 - 19:34:10"
APP_BUILD = "0.0.3.01"
PROMPT_TEXT = "LLDBPyGUI"
WINDOW_SIZE = 680


class ConfigClass():
    companyName = "DaVe_inc"
    appName = "LLDBPyGUI"

    initialCommand = "w s v idx"  # "breakpoint set -a 0x100003f6a" # re read
    fontStr = "Courier New"
    font = QFont(fontStr)  # ("Monaco") #("Courier New")
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
    testTarget = "hello_library_exec"  # amicable_numbers" #a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
    testTargetSource = "hello_library_exec.c"  # amicable_numbers.c" #a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"
    testTargetArch = "arm64-apple-macosx15.1.0"
    testTargetArgs = ""

    testTarget2 = "./_testtarget/a_hello_world_test"  # amicable_numbers" #a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
    testTargetSource2 = "./_testtarget/a_hello_world_test.c"  # amicable_numbers.c" #a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"

    # SCANF / AMICABLE
    # testTarget = "./_testtarget/amicable_numbers" #a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
    # testTargetSource = "./_testtarget/amicable_numbers.c" #a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"

    # GUI
    # testTarget = "./_testtarget/cocoa_windowed_objc2"  # a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
    # testTargetSource = "./_testtarget/cocoa_windowed_objc2.m"  # a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"

    # SWIFT (NOT SWIFTUI)
    # testTarget = "./_testtarget/xcode_projects/SwiftREPLTestApp/Debug/SwiftREPLTestApp.app/Contents/MacOS/SwiftREPLTestApp"  # a_hello_world_test" #amicable_numbers" #cocoa_windowed_objc2" #amicable_numbers" #a_hello_world_test" # "./testtarget/hello_world_test" # "/bin/ls" #/Users/dave/Library/Developer/Xcode/DerivedData/iOSNibbler-amppozfenucykfawuysrpwctoxnw/Build/Products/Debug/iOSNibblerApp.app/Contents/MacOS/iOSNibblerApp" # "./testtarget/hello_world_test"
    # testTargetSource = "./_testtarget/xcode_projects/SwiftREPLTestApp/SwiftREPLTestApp/ViewController.swift"  # a_hello_world_test.c" #amicable_numbers.c" #cocoa_windowed_objc2.m" #amicable_numbers.c" #a_hello_world_test.c"

    # testTargetArch = "x86_64-apple-macosx15.1.1"
    # testTargetArgs = ""

    startTestTarget = False
    settingsFilename = "./LLDBPyGUI_Settings.ini"

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

    pixName = None
    pixSearch = None
    pixUp = None

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

    colorGreen = QColor(0, 255, 0, 128)
    colorTransparent = QColor(0, 0, 0, 0)

    resRootDir = "./"

    @staticmethod
    def initIcons():
        project_root = dirname(realpath(__file__))
        resources_root = os.path.join(project_root, '..', 'resources', 'img')
        ConfigClass.resRootDir = resources_root

        ConfigClass.iconStd = QIcon()

        ConfigClass.pixGears = QPixmap(os.path.join(resources_root, 'gears.png')).scaled(QSize(48, 48))
        ConfigClass.pixGearsGrey = QPixmap(os.path.join(resources_root, 'gears_grey.png')).scaled(QSize(48, 48))
        ConfigClass.pixBug = QPixmap(os.path.join(resources_root, 'bug.png')).scaled(QSize(18, 18))
        ConfigClass.pixBugLg = QPixmap(os.path.join(resources_root, 'bug.png')).scaled(QSize(48, 48))
        ConfigClass.pixBugGreen = QPixmap(os.path.join(resources_root, 'bug_green.png')).scaled(QSize(18, 18))
        ConfigClass.pixDelete = QPixmap(os.path.join(resources_root, 'delete.png')).scaled(QSize(48, 48))
        ConfigClass.pixSave = QPixmap(os.path.join(resources_root, 'save.png')).scaled(QSize(48, 48))

        ConfigClass.pixName = QPixmap(os.path.join(resources_root, 'id-card.png')).scaled(QSize(48, 48))
        ConfigClass.pixSearch = QPixmap(os.path.join(resources_root, 'magnifying-glass-64x64.png')).scaled(
            QSize(32, 32))
        ConfigClass.pixUp = QPixmap(os.path.join(resources_root, 'upload.png')).scaled(QSize(32, 32))

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