#!/usr/bin/env python3
import lldb
import os
import io
import contextlib

from threading import Thread

import lib.utils
from ui.consoleWidget import ConsoleWidget
from ui.customQt.QControlFlowWidget import QControlFlowWidget
from ui.rememberLocationsTableWidget import RememberLocationsTableWidget

try:
	import queue
except ImportError:
	import Queue as queue
	
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from lib.settings import *
from lib.devHelper import *

import dbg.debuggerdriver
from dbg.debuggerdriver import *

from dbg.breakpointHelperNG import *
from dbg.listener import *
from dbg.fileInfos import *

from ui.dialogs.settingsDialog import *
from ui.dialogs.processesDialog import *
from ui.dialogs.creditsDialog import *
from ui.dialogs.spinnerDialog import *
from ui.dialogs.dialogHelper import *
from ui.assemblerTextEdit import *
from ui.variablesTableWidget import *
from ui.registerTableWidget import *
from ui.fileInfoTableWidget import *
from ui.statisticsTreeWidget import *
from ui.fileStructureTreeView import *
from ui.commandsWidget import *
from ui.consoleWidget import *
from ui.breakpointWidget import *
from ui.watchpointWidget import *
from ui.threadFrameTreeView import *
from ui.sourceTextEdit import *
from ui.listenerTreeView import *
from ui.searchTableWidget import *
from ui.consoleTextEdit import *
from ui.customQt.QHexTableWidget import *
from ui.customQt.QMemoryViewer import *
from ui.dbgOutputTextEdit import *


from worker.workerManager import *

from config import *

# main.py
from lib import utils


#class SBStreamForwarder(io.StringIO):
#	def __init__(self):
#		super().__init__()
#		self.sb_stream = None
#		
#	def write(self, data):
#		super().write(data)
#		if self.sb_stream is None:
#			self.sb_stream = lldb.SBStream()
#			self.sb_stream.Write(self.getvalue().encode())
#			self.truncate(0)  # Clear the buffer for subsequent writes
			

# myfile.py
def wpcallbackng(frame, wp, dict):
	print(f"================>>>>>>>>>>>>> YES WATCHPOINT HIT <<<<<<<<<<<=================")
	wp.SetEnabled(True)
	print(frame)
	print(wp)
	res = lldb.SBCommandReturnObject()
	ci = frame.GetThread().GetProcess().GetTarget().GetDebugger().GetCommandInterpreter()
	ci.HandleCommand('command script import "./LLDBPyGUIWindow.py"', res)
	# settings
#	ci.HandleCommand(f"w s v {varName}", res)
	ci.HandleCommand(f"watchpoint command add -F LLDBPyGUIWindow.wpcallback {wp.GetID()}", res)
	print(wp)
#	print(dict)
	pass
	
class LoadTargetThread(Thread):
	should_quit = False
	
	testSignal = pyqtSignal(bool)
	win = None
	
	def __init__(self, win):
		Thread.__init__(self)
		self.win = win
#		self.listener = lldb.SBListener('Chrome Dev Tools Listener')
#		self._add_listener_to_process(process)
#		self._broadcast_process_state(process)
#		self._add_listener_to_target(process.target)
#		
#	def _add_listener_to_target(self, target):
#		# Listen for breakpoint/watchpoint events (Added/Removed/Disabled/etc).
#		broadcaster = target.GetBroadcaster()
#		mask = SBTarget.eBroadcastBitBreakpointChanged | SBTarget.eBroadcastBitWatchpointChanged | SBTarget.eBroadcastBitModulesLoaded | SBThread.eBroadcastBitThreadSuspended 
#		broadcaster.AddListener(self.listener, mask)
#		
#	def _add_listener_to_process(self, process):
#		# Listen for process events (Start/Stop/Interrupt/etc).
#		broadcaster = process.GetBroadcaster()
#		mask = SBProcess.eBroadcastBitStateChanged | SBProcess.eBroadcastBitSTDOUT
#		broadcaster.AddListener(self.listener, mask)
#		
#	def _broadcast_process_state(self, process):
#		state = 'stopped'
#		if process.state == eStateStepping or process.state == eStateRunning:
#			state = 'running'
#		elif process.state == eStateExited:
#			state = 'exited'
#			self.should_quit = True
#		thread = process.selected_thread
#		print('Process event: %s, reason: %d' % (state, thread.GetStopReason()))
#		if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
#			print(f'REASON BP RFEACHED (driver) => Continuing...')
##     error = lldb.SBError()
##     thread.Resume(error)
##     process.Continue()
#			
#			
#			
#			
#	def _breakpoint_event(self, event):
#		breakpoint = SBBreakpoint.GetBreakpointFromEvent(event)
#		print('Breakpoint event: %s' % str(breakpoint))
		
	def run(self):
		while not self.should_quit:
#			event = SBEvent()
#			print("GOING to WAIT 4 EVENT...")
#			if self.listener.WaitForEvent(lldb.UINT32_MAX, event):
#				print("GOT NEW EVENT DRIVER!!")
#				if event.GetType() == SBTarget.eBroadcastBitModulesLoaded:
#					print('Module load: %s' % str(event))
#				elif event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
#					print("STD OUT EVENT")
#					stdout = SBProcess.GetProcessFromEvent(event).GetSTDOUT(256)
#					print(SBProcess.GetProcessFromEvent(event))
#					print(stdout)
#					if stdout is not None and len(stdout) > 0:
#						message = {"status":"event", "type":"stdout", "output": "".join(["%02x" % ord(i) for i in stdout])}
#						print(message)
#						print("".join(["%02x" % ord(i) for i in stdout]))
##             self.signals.event_output.emit("".join(["%02x" % ord(i) for i in stdout]))
##             QCoreApplication.processEvents()
#				elif SBProcess.EventIsProcessEvent(event):
#					self._broadcast_process_state(SBProcess.GetProcessFromEvent(event))
#					print("STD OUT EVENT ALT!!!")
#				elif SBBreakpoint.EventIsBreakpointEvent(event):
#					self._breakpoint_event(event)
#				elif event.GetType() == lldb.SBTarget.eBroadcastBitWatchpointChanged:
#					wp = lldb.SBWatchpoint.GetWatchpointFromEvent(event)
#					print(f"WATCHPOINT CHANGED!!!! => {wp}")
#				else:
#					print("OTHER EVENT!!!!")
			pass
					
		print("END LOADTARGET THREAD!!!")
		
class LLDBPyGUIWindow(QMainWindow):

	def wpcallbackng(self):
		print(f"================>>>>>>>>>>>>> YES WATCHPOINT CALLBACK NG <<<<<<<<<<<=================")
		pass

	def wpcallback(self, frame, wp, dict):
		print(f"================>>>>>>>>>>>>> YES WATCHPOINT HIT <<<<<<<<<<<=================")
		pass
	
	def my_custom_log_callback(self, log_level, message):
		"""Custom callback function for LLDB logging.
	
		Args:
				log_level: Integer representing the log level (e.g., lldb.eLevelDebug).
				message: String containing the actual log message.
		"""
#		level_name = lldb.SBDebugger.GetLogMessageLevelName(log_level)
		# print(f"=========================>>>>>>>>>>>>>>>>>>>> [{log_level}] => {message}")
		
	tmrResetStatusBar = QtCore.QTimer()
	bpHelper = None

	# def __init__(self):
	# 	super().__init__()
	# 	self.settings = QSettings("MyCompany", "MyApp")  # Use your org/app name
	# 	self._restore_size()

	def _restore_size(self):
		size = self.setHelper.getValue(SettingsValues.WindowSize) # , QSize(800, 600)
		if isinstance(size, QSize):
			self.resize(size)

	def resizeEvent(self, event):
		self.setHelper.setValue(SettingsValues.WindowSize, self.size())
		# self.settings.setValue("window_size", self.size())
		super().resizeEvent(event)

	def __init__(self, driver = None):
		super().__init__()


		lib.utils.main_window = self  # inside MainWindow __init__

		self.driver = driver
		# Set the custom logging callback
		self.driver.debugger.SetLoggingCallback(self.my_custom_log_callback)
		
		self.targetBasename = "NG"
		
		self.setHelper = SettingsHelper()
		self.workerManager = WorkerManager(self.driver)
		self.bpHelper = BreakpointHelperNG(self.driver)
		self.devHelper = DevHelper(self.driver, self.bpHelper)
		
		self.setWinTitleWithState("GUI Started")
		self.setBaseSize(WINDOW_SIZE * 2, WINDOW_SIZE)
		self.setMinimumSize(WINDOW_SIZE * 2, WINDOW_SIZE + 72)
		self.move(1200, 200)
		
		self.toolbar = QToolBar('Main ToolBar')
		self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)
		self.toolbar.setIconSize(QSize(ConfigClass.toolbarIconSize, ConfigClass.toolbarIconSize))
		self.toolbar.setContentsMargins(0, 0, 0, 0)
		
		# new menu item
		self.load_action = QAction(ConfigClass.iconBug, '&Load Target', self)
		self.load_action.setStatusTip('Load Target')
		self.load_action.setShortcut('Ctrl+L')
		self.load_action.triggered.connect(self.load_clicked)
		self.toolbar.addAction(self.load_action)
		
		self.attach_action = QAction(ConfigClass.iconGears, '&Attach Process', self)
		self.attach_action.setStatusTip('Attach Process')
		self.attach_action.setShortcut('Ctrl+A')
		self.attach_action.triggered.connect(self.attach_clicked)
		self.toolbar.addAction(self.attach_action)
		
		self.toolbar.addSeparator()
		
		self.load_resume = QAction(ConfigClass.iconResume, '&Resume', self)
		self.load_resume.setStatusTip('Resume (Ctrl+I)')
		self.load_resume.setShortcut('Ctrl+I')
		self.load_resume.triggered.connect(self.resume_clicked)
		self.toolbar.addAction(self.load_resume)

		self.stop = QAction(ConfigClass.iconStop, 'S&top', self)
		self.stop.setStatusTip('Stop')
		#		self.load_resume.setShortcut('Ctrl+L')
		self.stop.triggered.connect(self.stop_clicked)
		self.toolbar.addAction(self.stop)
		
		self.step_over = QAction(ConfigClass.iconStepOver, '&Step Over', self)
		self.step_over.setStatusTip('Step Over')
#		self.load_resume.setShortcut('Ctrl+L')
		self.step_over.triggered.connect(self.stepOver_clicked)
		self.toolbar.addAction(self.step_over)
		
		self.step_into = QAction(ConfigClass.iconStepInto, '&Step Into', self)
		self.step_into.setStatusTip('Step Into')
#		self.load_resume.setShortcut('Ctrl+L')
		self.step_into.triggered.connect(self.stepInto_clicked)
		self.toolbar.addAction(self.step_into)
		
		self.step_out = QAction(ConfigClass.iconStepOut, '&Step Out', self)
		self.step_out.setStatusTip('Step Out')
#		self.load_resume.setShortcut('Ctrl+L')
		self.step_out.triggered.connect(self.stepOut_clicked)
		self.toolbar.addAction(self.step_out)
		
#		self.step_restart = QAction(ConfigClass.iconRestart, '&Restart', self)
#		self.step_restart.setStatusTip('Restart')
#		self.load_resume.setShortcut('Ctrl+R')
#		self.step_restart.triggered.connect(self.restart_clicked)
#		self.toolbar.addAction(self.step_restart)
		
#		self.stop = QAction(ConfigClass.iconStop, '&Stop', self)
#		self.stop.setStatusTip('Stop')
##		self.load_resume.setShortcut('Ctrl+L')
#		self.stop.triggered.connect(self.handle_stopThread)
#		self.toolbar.addAction(self.stop)
		
		self.toolbar.addSeparator()
		
		self.back = QAction(ConfigClass.iconLeft, '&Back', self)
		self.back.setStatusTip('Back')
#		self.load_resume.setShortcut('Ctrl+L')
		self.back.triggered.connect(self.back_clicked)
		self.toolbar.addAction(self.back)
		
		self.forward = QAction(ConfigClass.iconRight, '&Forward', self)
		self.forward.setStatusTip('Forward')
#		self.load_resume.setShortcut('Ctrl+L')
		self.forward.triggered.connect(self.forward_clicked)
		self.forward.setEnabled(False)
		self.toolbar.addAction(self.forward)
		
		self.toolbar.addSeparator()
		
		self.settings_action = QAction(ConfigClass.iconSettings, 'Settings', self)
		self.settings_action.setStatusTip('Settings')
		self.settings_action.setShortcut('Ctrl+O')
		self.settings_action.triggered.connect(self.settings_clicked)
		self.toolbar.addAction(self.settings_action)
#		self.toolbar.addAction(self.settings_action)
		
		self.help_action = QAction(ConfigClass.iconInfo, '&Show Help (DaVe)', self)
		self.help_action.setStatusTip('Show Help')
		self.help_action.setShortcut('Ctrl+H')
		self.help_action.triggered.connect(self.help_clicked)
		self.toolbar.addAction(self.help_action)

		self.credits_action = QAction(ConfigClass.iconMarkdown, 'Show C&REDITS', self)
		self.credits_action.setStatusTip('Show Credits')
		self.credits_action.setShortcut('Ctrl+R')
		self.credits_action.triggered.connect(self.credits_clicked)
		self.toolbar.addAction(self.credits_action)
		
		self.toolbar.addSeparator()
		
		self.test_action = QAction(ConfigClass.iconTest, '&Test', self)
		self.test_action.setStatusTip('Test')
		self.test_action.setShortcut('Ctrl+T')
		self.test_action.triggered.connect(self.test_clicked)
		self.toolbar.addAction(self.test_action)
		
		self.menu = self.menuBar()
		
		self.main_menu = self.menu.addMenu("Main")
		self.main_menu.addAction(self.settings_action)

		self.file_menu = self.menu.addMenu("&Load Action")
		self.file_menu.addAction(self.load_action)
#		file_menu.addAction(self.settings_action)

#		self.help_action = QAction(ConfigClass.iconInfo, '&Show Help', self)
#		self.help_action.setStatusTip('Show Help')
#		self.help_action.setShortcut('Ctrl+H')
#		self.help_action.triggered.connect(self.click_help)

		self.about_menu = self.menu.addMenu("&About")

#		help_menu = about_menu.addMenu("&Show Help")
		self.about_menu.addAction(self.help_action)
		
		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
		
		self.progressbar = QProgressBar()
		self.progressbar.setMinimum(0)
		self.progressbar.setMaximum(100)
		self.progressbar.setValue(0)
		self.progressbar.setFixedWidth(100)
		
		self.statusBar.addPermanentWidget(self.progressbar)
		
		# self.layout = QVBoxLayout()
		# self.layout.setContentsMargins(0, 0, 0, 0)

		self.splitterAsm = QSplitter()
		self.splitterAsm.setContentsMargins(0, 0, 0, 0)
		self.splitterAsm.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.splitterAsm.setOrientation(Qt.Orientation.Horizontal)

		self.txtMultiline = AssemblerTextEdit(self.driver, self.bpHelper)
		self.wdtControlFlow = QControlFlowWidget(self.txtMultiline, self.driver)
		self.wdtControlFlow.setContentsMargins(0, 0, 0, 0)
		self.wdtControlFlowLeft = QWidget()
		self.wdtControlFlowLeft.setContentsMargins(0, 30, 0, 0)
		# self.wdtControlFlowLeft.setMin
		self.layControlFlowLeft = QVBoxLayout(self.wdtControlFlowLeft)
		self.layControlFlowLeft.setContentsMargins(0, 0, 0, 0)
		# self.layControlFlowLeft.addStretch(1)
		self.layControlFlowLeft.addWidget(self.wdtControlFlow)
		self.splitterAsm.addWidget(self.wdtControlFlowLeft)
		# self.splitterAsm.set
		self.wdtControlFlowLeft.setMaximumWidth(80)
		self.wdtControlFlow.setMaximumWidth(80)


		self.splitterAsm.addWidget(self.txtMultiline)
#		self.txtMultiline.table.sigEnableBP.connect(self.handle_enableBP)
#		self.txtMultiline.table.sigBPOn.connect(self.handle_BPOn)
		
		self.txtMultiline.setContentsMargins(0, 0, 0, 0)
		
		self.splitter = QSplitter()
		self.splitter.setContentsMargins(0, 0, 0, 0)
		self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.splitter.setOrientation(Qt.Orientation.Vertical)
		
		self.splitter.addWidget(self.splitterAsm)
		
		self.tabWidgetDbg = QTabWidget()
		self.tabWidgetDbg.setContentsMargins(0, 0, 0, 0)
		self.splitter.addWidget(self.tabWidgetDbg)
		self.splitter.setStretchFactor(0, 60)
		self.splitter.setStretchFactor(1, 40)
		
		self.tabWidgetReg = QTabWidget()
		self.tabWidgetReg.setContentsMargins(0, 0, 0, 0)
		self.tabWidgetDbg.addTab(self.tabWidgetReg, "Registers")
		
		self.tblVariables = VariablesTableWidget(self.driver)
		self.tabWidgetDbg.addTab(self.tblVariables, "Variables")
		
		self.wdtBPsWPs = BPsWPsWidget(self.driver, self.workerManager, self.bpHelper)
		
		self.tabWidgetDbg.addTab(self.wdtBPsWPs, "Breakpoints")
		
		self.tabWatchpoints = WatchpointsWidget(self.driver, self.workerManager)
		
		self.tabWidgetDbg.addTab(self.tabWatchpoints, "Watchpoints")
		
		self.txtSource = SourceTextEdit()
		self.tabWidgetDbg.addTab(self.txtSource, "Sourcecode")
		
		self.treThreads = ThreadFrameTreeWidget()
		
		self.tabWidgetDbg.addTab(self.treThreads, "Threads/Frames")

		self.tblRememberLoc = RememberLocationsTableWidget(self.driver, self.bpHelper)

		self.tabWidgetDbg.addTab(self.tblRememberLoc, "Remember Locations")
		
		self.treListener = ListenerWidget(self.driver, self.setHelper)
		self.treListener.treEventLog.sigSTDOUT.connect(self.testSTDOUT)
		self.treListener.setContentsMargins(0, 0, 0, 0)
#		self.treListener.listener.signals.processEvent.connect(self.handle_processEvent)
		
		self.tabWidgetDbg.addTab(self.treListener, "Listeners")

		self.tabWidgetMain = QTabWidget()

		self.tabWidgetConsoles = QTabWidget()
		self.tabWidgetConsole = QTabWidget()
		self.tabWidgetConsole.setContentsMargins(0, 0, 0, 0)
		self.tabWidgetConsole.setLayout(QVBoxLayout())
		# self.consoleWidget = ConsoleWidget(self.workerManager)
		# self.consoleWidget.setContentsMargins(0, 0, 0, 0)
		self.tabWidgetConsole.layout().setContentsMargins(0, 0, 0, 0)
		# self.tabWidgetConsoles.addTab(self.tabWidgetConsole, "Python Console")
		# self.tabWidgetConsole.layout().addWidget(self.consoleWidget)
		# --- IMPORTANT: Expose application variables/objects to the console ---
		# Create a dictionary to pass as the interpreter's local namespace.
		# This makes 'app_object' available in the console's scope.
		# You can add any variables or objects you want to expose.
		exposed_variables = {
			'app_object': self,  # Expose the MainWindow instance itself
			'QApplication': QApplication,  # Expose QApplication if needed
			'os': __import__('os'),  # Example: expose a module
			'my_data': "This is a string from the main app."
		}
		self.tabWidgetConsolePrompt = QTabWidget()
		self.tabWidgetConsolePrompt.setContentsMargins(0, 0, 0, 0)
		"""
		        Sets up the graphical user interface for the console.
		        """
		self.main_layout = QVBoxLayout(self)
		self.main_layout.setContentsMargins(10, 10, 10, 10)
		self.main_layout.setSpacing(5)

		# Output TextEdit
		# self.output_text_edit = QTextEdit()
		# ConsoleWidget()
		self.output_text_edit = ConsoleWidget() #.setReadOnly(True)
		# self.output_text_edit.setFontPointSize(12)
		# self.output_text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
		# self.output_text_edit.setStyleSheet("""
		#             QTextEdit {
		#                 background-color: #282c34; /* Dark background */
		#                 color: #abb2bf; /* Light grey text */
		#                 border: 1px solid #3e4452;
		#                 border-radius: 5px;
		#                 padding: 10px;
		#             }
		#         """)
		# self.output_text_edit.setText("dave@Mia /:")
		# self.main_layout.addWidget(self.output_text_edit)

		#self.tabWidgetMain.addTab(self.wdtCommands, "Commands")
		#self.tabWidgetConsoles.addTab(self.wdtCommands, "Commands")
		self.tabWidgetConsoles.addTab(self.output_text_edit, "System shell")
		self.tabWidgetConsoles.addTab(self.tabWidgetConsole, "Python")



		# self.tabWidgetConsolePrompt.setLayout(QVBoxLayout())
		# self.tabWidgetConsoles.addTab(self.tabWidgetConsolePrompt, "Prompt")

		# Create and add the console widget
		self.console_widget = PyQtConsoleWidget(locals_dict=exposed_variables)
		self.tabWidgetConsole.layout().addWidget(self.console_widget)
		# self.tabWidgetDbg.addTab(self.tabWidgetConsoles, "Consoles")

		# self.tabWidgetDbg.addTab(self.wdtSearch, "Search")

		
		self.tabWidgetMain = QTabWidget()
		self.tabWidgetMain.setContentsMargins(0, 0, 0, 0)
		self.tabWidgetMain.addTab(self.splitter, "Debugger")
		self.tabWidgetMain.setContentsMargins(0, 0, 0, 0)
		self.tabWidgetMain.currentChanged.connect(self.handle_tabWidgetMainCurrentChanged)
		
		self.tblFileInfos = FileInfosTableWidget()
		self.tabWidgetFileInfos = QWidget()
		self.tabWidgetFileInfos.setLayout(QVBoxLayout())
		
		self.tabWidgetFileInfo = QTabWidget()
		
		self.tabWidgetFileInfo.addTab(self.tblFileInfos, "File Header")
		
		self.tabWidgetFileInfos.layout().addWidget(self.tabWidgetFileInfo)

		self.tabWidgetStruct = FileStructureWidget(self.driver)		
		self.tabWidgetFileInfo.addTab(self.tabWidgetStruct	, "File Structure")
		
		self.treStats = StatisticsTreeWidget(self.driver)
		self.tabWidgetStats = QWidget()
		self.tabWidgetStats.setLayout(QVBoxLayout())
		self.tabWidgetStats.layout().addWidget(self.treStats)
		
		self.tabWidgetFileInfo.addTab(self.tabWidgetStats, "File Statistics")
		
		self.tabWidgetMain.addTab(self.tabWidgetFileInfos, "File Info")
		
		self.tblHex = QMemoryViewer(self.driver)
		self.tblHex.cmbGrouping.setCurrentIndex(self.setHelper.getValue(SettingsValues.HexGrouping))
		
		self.tabMemory = QWidget()
		self.tabMemory.setLayout(QVBoxLayout())
		self.tabMemory.layout().addWidget(self.tblHex)
		
		self.tabWidgetMain.addTab(self.tabMemory, "Memory")
		
		self.wdtSearch = SearchWidget(self.driver)
		# self.tabWidgetMain.addTab(self.wdtSearch, "Search")

		self.tabWidgetDbg.addTab(self.wdtSearch, "Search")
		
		self.wdtCommands = CommandsWidget(self.workerManager)
		self.tabWidgetConsoles.addTab(self.wdtCommands, "LLDB")

		self.tabWidgetDbg.addTab(self.tabWidgetConsoles, "Consoles")
		# self.tabWidgetMain.addTab(self.wdtCommands, "Commands")
		#
		# self.layoutMainWin = QVBoxLayout()
		# self.layoutMainWin.setContentsMargins(0, 0, 0, 0)
		#
		# self.layoutMainWin.addWidget(self.tabWidgetMain)
		#
		# self.centralWidget = QWidget(self)
		# self.centralWidget.setLayout(self.layoutMainWin)
		# self.setCentralWidget(self.centralWidget)
		#
		self.dbgWidgetMain = QWidget()
		self.dbgWidgetMain.setLayout(QVBoxLayout())
		self.dbgWidgetMain.setContentsMargins(0, 0, 0, 0)
		# self.dbgWidgetMain.layout().addWidget(self.tabWidgetMain)
		self.wdtDbg = DbgOutputWidget()
		# self.dbgTxt = DbgOutputTextEdit()
		# self.dbgTxt.setStyleSheet("""
		# 			QTextEdit {
		# 				/* background-color: #f0f0f0;
		# 				gridline-color: #ccc;
		# 				font: 12px 'Courier New';*/
		# 				background-color: #282c34; /* Dark background */
		# 				color: #abb2bf; /* Light grey text */
		# 				font: 12px 'Courier New';
		# 				/*border: 1px solid #3e4452;*/
		# 				border-radius: 5px;
		# 				/*padding: 10px;*/
		# 			}
		# 		""")
		# self.dbgWidgetMain.layout().addWidget(self.dbgTxt)

		self.splitterDbgMain = QSplitter()
		self.splitterDbgMain.setContentsMargins(0, 0, 0, 0)
		self.splitterDbgMain.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.splitterDbgMain.setOrientation(Qt.Orientation.Vertical)
		self.splitterDbgMain.addWidget(self.tabWidgetMain)
		self.splitterDbgMain.addWidget(self.wdtDbg)
		self.setCentralWidget(self.splitterDbgMain)
		self.bpHelper.setCtrls(self.txtMultiline, self.wdtBPsWPs.treBPs)
	
		self.threadpool = QThreadPool()
		
	#	tmrResetStatusBarActive = False
		
#		def updateStatusBar(self, msg):
#		self.statusBar.showMessage(msg)
#		if self.tmrResetStatusBar.isActive():
#			self.tmrResetStatusBar.stop()
#		self.tmrResetStatusBar = QtCore.QTimer()
		self.tmrResetStatusBar.setInterval(int(self.setHelper.getValue(SettingsValues.StatusBarMsgTimeout)))
		self.tmrResetStatusBar.setSingleShot(True)
		self.tmrResetStatusBar.timeout.connect(self.resetStatusBar)
#		self.tmrResetStatusBar.start()
			
		# ======== DEV CMDs ##########
		self.tabWidgetDbg.setCurrentIndex(2)

		self.updateStatusBar("LLDBPyGUI loaded successfully!")

		self._restore_size()

		# import pdb; pdb.set_trace()

	def closeEvent(self, event):
		# reply = QMessageBox.question(self,
	    #     "Confirm Exit"
	    #     "Are you sure you want to quit?",
	    #     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) # , QMessageBox.StandardButton.No
		#
		# if reply == QMessageBox.StandardButton.Yes:
		# 	event.accept()
		# else:
		# 	event.ignore()

		# msgBox = QMessageBox()
		# msgBox.setText("The document has been modified.")
		# msgBox.setInformativeText("Do you want to save your changes?")
		# # msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.StandardButton.Cancel)
		# msgBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
		# msgBox.setDefaultButton(QMessageBox.StandardButton.Yes)
		# msgBox.setIcon(QMessageBox.Icon.Question)
		# ret = msgBox.exec()
		# if ret == QMessageBox.StandardButton.Yes:
		# 	event.accept()
		# else:
		# 	event.ignore()

		if self.setHelper.getValue(SettingsValues.ConfirmQuitApp):
			dlg = ConfirmDialog("Quit LLDBPyGUI?", "Do you really want to quit LLDBPyGUI and discard all unsaved changes?")
			if dlg.exec() and dlg.button_clicked == QDialogButtonBox.StandardButton.Ok:
				print(f"Quitting LLDBPyGUI now YESSS ...")
				self.driver.setDone()
				# self.driver.terminate()
				event.accept()
				# self.driver.terminate()
			else:
				event.ignore()
		else:
			event.accept()
			
	def clearCompleteUI(self):
		self.tblVariables.resetContent()
		pass

	def testSTDOUT(self, strOut):
		# print(f'HEEEEEELLLLLLLOOOOOO FROM STDOUT => {strOut}')
		self.output_text_edit.append(f'{strOut}\n')


	def cmbModules_changed(self, index):
		# print(f"cmbModules_changed => {index}")
		self.loadFileStruct(index)
		
	def setWinTitleWithState(self, state):
		self.setWindowTitle(APP_NAME + " " + APP_VERSION + " - " + APP_RELEASE_DATE + " - " + self.targetBasename + " - " + state)
		
	def handle_showMemoryFor(self):
		sender = self.sender()  # get the sender object
		if isinstance(sender, QAction):
			action = sender  # it's the QAction itself
		else:
			# Find the QAction within the sender (e.g., QMenu or QToolBar)
			action = sender.findChild(QAction)


		# print(f"action ===============>>>>>>>>>>>> {action.data()}")
		addr = self.quickToolTip.get_memory_address(self.driver.debugger, action.data())
		# print(f"GETTING MEMORY: {addr}")
		# self.updateStatusBar(f"Showing memory for address: {addr}")
		# self.statusBar.showMessage(f"Showing memory for address: {addr}")
		lib.utils.setStatusBar(f"Showing memory for address: {addr}")
		self.doReadMemory(addr)
#		print(f"Triggering QAction: {action.text()}")
		
	def doReadMemory(self, address, size = 0x100):
		self.tabWidgetMain.setCurrentWidget(self.tabMemory)
		self.tblHex.doReadMemory(address, size)
#		self.window().tblHex.txtMemAddr.setText(hex(address))
#		self.window().tblHex.txtMemSize.setText(hex(size))
#		try:
##           global debugger
##			self.handle_readMemory(self.driver.debugger, int(self.window().tblHex.txtMemAddr.text(), 16), int(self.window().tblHex.txtMemSize.text(), 16))
#			self.window().tblHex.handle_readMemory(self.driver.debugger, int(self.window().tblHex.txtMemAddr.text(), 16), int(self.window().tblHex.txtMemSize.text(), 16))
#		except Exception as e:
#			print(f"Error while reading memory from process: {e}")
			
		
	def handle_progressUpdate(self, value, statusTxt):
		self.setProgressValue(value)
		self.updateStatusBar(statusTxt)
		
	def setProgressValue(self, newValue):
		self.progressbar.setValue(newValue)
		QCoreApplication.processEvents()
	
#	tmrResetStatusBar = QtCore.QTimer()
#	tmrResetStatusBarActive = False
	
	def updateStatusBar(self, msg, autoTimeout = True, timeoutMs = -1):
		self.statusBar.showMessage(msg)
		# return msg
		# pass
		if self.tmrResetStatusBar.isActive():
			self.tmrResetStatusBar.stop()
#		self.tmrResetStatusBar = QtCore.QTimer()
#		self.tmrResetStatusBar.setInterval(1500)
#		self.tmrResetStatusBar.setSingleShot(True)
#		self.tmrResetStatusBar.timeout.connect(self.resetStatusBar)
		if autoTimeout:
			if timeoutMs == -1:
				self.tmrResetStatusBar.setInterval(self.setHelper.getValue(SettingsValues.StatusBarMsgTimeout))
			else:
				self.tmrResetStatusBar.setInterval(timeoutMs)
			self.tmrResetStatusBar.start()
			
	
	def resetStatusBar(self):
#		self.tmrResetStatusBarActive = False
#		print(f"RESETING STATUSBAR MSG...")
		self.statusBar.showMessage("")
		
	def load_clicked(self):
		filename = showOpenFileDialog()
		if filename != None and filename != "":
			# print(f"Loading new target: '{filename}")
			self.loadNewExecutableFile(filename)
	
	def handle_tabWidgetMainCurrentChanged(self, idx):
		if idx == 2:
			self.wdtCommands.txtCmd.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
			# print(f"self.wdtCommands.txtCmd.setFocus(Qt.FocusReason.ActiveWindowFocusReason)")
#		elif idx == 3:
#			self.tblHex.cmbGrouping.setCurrentIndex(self.setHelper.getValue(SettingsValues.HexGrouping))
#			pass
		pass
		
	isAttached = False
	def attach_clicked(self):
		if not self.isAttached:
#			print(f"Attaching to process ...")
			pd = ProcessesDialog("Select process to debug", "Select a process to attach to and load for debugging.")
			pd.txtPID.setText(str(self.setHelper.getValue(SettingsValues.TestAttachPID)))
			if pd.exec():
				self.resetGUI()
				try:
					proc = pd.getSelectedProcess()
					# print(proc)
					# print(f"Process Idx: '{pd.cmbPID.currentIndex()}' / PID: '{proc.pid}' / Name: '{proc.name()}' selected")
					self.setWinTitleWithState(f"PID: {proc.pid} ({proc.name()})")
					self.driver.attachProcess(proc.pid)
					self.loadTarget()
					self.attach_action.setIcon(ConfigClass.iconGearsGrey)
					self.attach_action.setToolTip("Detach from process: {proc.pid} ({proc.name()})")
					self.setHelper.setValue(SettingsValues.TestAttachPID, int(proc.pid))
					self.isAttached = True	
				except Exception as e:
					sError = f"Error while attaching to process: {e}"
					self.updateStatusBar(sError)
					print(sError)
		else:
			error = self.driver.getTarget().GetProcess().Detach()
			if error.Success():
				self.resetGUI()
				# print(f"Detached from process returned with result: {error}")
				self.attach_action.setIcon(ConfigClass.iconGears)
				self.attach_action.setToolTip("Attach to process")
				self.isAttached = False
				
		
	def execCommand_clicked(self):
		pass
		
	def clear_clicked(self):
		pass

	def stop_clicked(self):
		target = self.driver.getTarget()
		if target:
			process = target.GetProcess()
			if process:
				errKill = process.Kill()
				if errKill:
					print(f'{errKill}')
				else:
					self.clearCompleteUI()


		# if self.isProcessRunning:
		# 	print(f"self.isProcessRunning => Trying to Suspend()")
		# 	thread = self.driver.getThread()

	def resume_clicked(self):
		if self.isProcessRunning:
			# print(f"self.isProcessRunning => Trying to Suspend()")
			thread = self.driver.getThread()
			if thread:
				self.isProcessRunning = False
				self.driver.debugger.SetAsync(False)
				thread.Suspend()
			else:
				print(f"self.isProcessRunning => Thread is NONE")
				self.driver.getTarget().GetProcess().GetThreadAtIndex(0).Suspend()
				print(f"self.driver.getTarget().GetProcess().GetThreadAtIndex(0) => {self.driver.getTarget().GetProcess().GetThreadAtIndex(0)}")
				thread = self.driver.getTarget().GetProcess().GetThreadAtIndex(0)
				if thread:
					print(f"self.isProcessRunning => TRYING TO SUSPEND SECOND")
					self.isProcessRunning = False
					self.driver.debugger.SetAsync(False)
					thread.Suspend()
				else:
					print(f"self.isProcessRunning => Thread is NONE SECOND")
					pass
#				self.driver.debugger.SetAsync(False)
		else:
			self.driver.debugger.SetAsync(True)
			self.start_debugWorker(self.driver, StepKind.Continue)
		pass
		
	def stepOver_clicked(self):
		self.driver.debugger.SetAsync(False)
		self.start_debugWorker(self.driver, StepKind.StepOver)
		self.setWinTitleWithState("Interrupted")
		pass
		
	def stepInto_clicked(self):
		self.driver.debugger.SetAsync(False)
		self.start_debugWorker(self.driver, StepKind.StepInto)
		self.setWinTitleWithState("Interrupted")
		pass
		
	def stepOut_clicked(self):
		self.driver.debugger.SetAsync(False)
		self.start_debugWorker(self.driver, StepKind.StepOut)
		self.setWinTitleWithState("Interrupted")
		pass
		
	def back_clicked(self):
		newLoc = self.txtMultiline.locationStack.backLocation()
		if newLoc:
			# print(f"GOING BACK to {newLoc} ... {self.txtMultiline.locationStack.currentLocation}")
			self.txtMultiline.viewAddress(newLoc, False)
		self.forward.setEnabled(not self.txtMultiline.locationStack.currentIsLast())
		self.back.setEnabled(not self.txtMultiline.locationStack.currentIsFirst())
		
	def forward_clicked(self):
		newLoc = self.txtMultiline.locationStack.forwardLocation()
		if newLoc:
			# print(f"GOING FORWARD to {newLoc} ... {self.txtMultiline.locationStack.currentLocation}")
			self.txtMultiline.viewAddress(newLoc, False)
		self.forward.setEnabled(not self.txtMultiline.locationStack.currentIsLast())
		self.back.setEnabled(not self.txtMultiline.locationStack.currentIsFirst())
	
	def settings_clicked(self):
		settingsWindow = SettingsDialog(self.setHelper)
		if settingsWindow.exec():
			# print(f'Settings saved')
			self.tblHex.cmbGrouping.setCurrentIndex(self.setHelper.getValue(SettingsValues.HexGrouping))
			self.tmrResetStatusBar.setInterval(int(self.setHelper.getValue(SettingsValues.StatusBarMsgTimeout)))
			
	def help_clicked(self):
		pass

	def credits_clicked(self):
		print(f'Credits clicked ...')
		if not self.isAttached:
#			print(f"Attaching to process ...")
			pd = CreditsDialog("Credits for LLDBPyGUI", "This are the Credits with the resourses used for the realisation of LLDBPyGUI")
			pd.exec()
			# pd.txtPID.setText(str(self.setHelper.getValue(SettingsValues.TestAttachPID)))
			# if pd.exec():
			# 	self.resetGUI()
			# 	try:
			# 		proc = pd.getSelectedProcess()
			# 		print(proc)
			# 		print(f"Process Idx: '{pd.cmbPID.currentIndex()}' / PID: '{proc.pid}' / Name: '{proc.name()}' selected")
			# 		self.setWinTitleWithState(f"PID: {proc.pid} ({proc.name()})")
			# 		self.driver.attachProcess(proc.pid)
			# 		self.loadTarget()
			# 		self.attach_action.setIcon(ConfigClass.iconGearsGrey)
			# 		self.attach_action.setToolTip("Detach from process: {proc.pid} ({proc.name()})")
			# 		self.setHelper.setValue(SettingsValues.TestAttachPID, int(proc.pid))
			# 		self.isAttached = True	
			# 	except Exception as e:
			# 		sError = f"Error while attaching to process: {e}"
			# 		self.updateStatusBar(sError)
			# 		print(sError)
		# else:
		# 	error = self.driver.getTarget().GetProcess().Detach()
		# 	if error.Success():
		# 		self.resetGUI()
		# 		print(f"Detached from process returned with result: {error}")
		# 		self.attach_action.setIcon(ConfigClass.iconGears)
		# 		self.attach_action.setToolTip("Attach to process")
		# 		self.isAttached = False
		pass
		
	def test_clicked(self):
#		self.resetGUI()
#		QAppl
#		self.txtSource.scroll_to_line("=>")
#		self.txtMultiline.table.testBG()
#		self.dialog = SpinnerDialog()
#		self.dialog.show()
#		if self.dialog != None:
#			self.dialog.close()
#			self.dialog = None
#		else:
		
#		self.dialog = SpinnerDialog()
#		self.dialog.show()
#		self.driver.removeListener(lldb.SBTarget, SBTarget.eBroadcastBitBreakpointChanged)
		
		
#		self.tabWatchpoints.tblWatchpoints.resetContent()
#		self.tabWatchpoints.reloadWatchpoints(True)
#		self.stopTarget()

		# This was current
		# self.loadNewExecutableFile(ConfigClass.testTarget)
		# self.tabWidgetMain.setCurrentIndex(2)
		# target = lldb.debugger.GetSelectedTarget()
		# self.target
		self.wdtControlFlow.loadInstructions()
		# objCon = self.wdtControlFlow.draw_flowConnection(0, 45)
		# objCon.setToolTip(f"FIRST TOOLTIP!!!")
		# objCon2 = self.wdtControlFlow.draw_flowConnection(37, 57, QColor("orange"), 25, 1, 21)
		# objCon2.setToolTip(f"SECOND TOOLTIP!!!")
		# objCon3 = self.wdtControlFlow.draw_flowConnection(42, 46, QColor("green"), 15, 1, 29)
		# objCon3.setToolTip(f"THIRD TOOLTIP!!!")
		# self.wdtDbg.logDbg("QMainWindow HELLO from wdtDbg")
		# self.dbgTxt.logDbg("QMainWindow HELLO")
		# breakpoint = self.driver.getTarget().BreakpointCreateByName("subfunc")  # or any breakpoint creation methodpass
		# breakpoint.SetCondition("$rax == 0x0000000000000001")
		
	def stopTarget(self):
		# self.driver
		if self.driver.getTarget().GetProcess():
			self.driver.setDone()
			if hasattr(self, "listener"):
				self.listener.should_quit = True

			self.driver.getTarget().GetProcess().Kill()
#			self.driver.debugger.DeleteTarget(self.driver.getTarget())
			# print("Process killed")
			self.resetGUI()
		pass

#	def updateStatusBar(self, msg):
#		self.statusBar.showMessage(msg)
		
	def setProgressValue(self, newValue):
		self.progressbar.setValue(int(newValue))
		
	def onQApplicationStarted(self):
		# print('onQApplicationStarted started')
		
#		self.dialog = SpinnerDialog()
#		self.dialog.show()
		
		if self.setHelper.getValue(SettingsValues.LoadTestTarget):
			# print(f"Loading target: {ConfigClass.testTarget}")
			self.loadNewExecutableFile(ConfigClass.testTarget)
			
	def loadNewExecutableFile(self, filename):
#		self.resetGUI()
		self.targetBasename = os.path.basename(filename)
		# import pdb; pdb.set_trace()
#		if self.driver.getTarget().GetProcess(): #pymobiledevice3GUIWindow.process:
#			print("KILLING PROCESS")
#	
#			self.driver.aborted = True
#			print("Aborted sent")
#			#					os._exit(1)
#			#       sys.exit(0)
#			#       pymobiledevice3GUIWindow.process.Kill()
#			#       global driver
#			#       driver.terminate()
#			#       pymobiledevice3GUIWindow.driver.getTarget().GetProcess().Stop()
#			#       print("Process stopped")        
#			self.driver.getTarget().GetProcess().Kill()
#			print("Process killed")
#			self.resetGUI()
		self.stopTarget()
		
		global event_queue
		event_queue = queue.Queue()
#				
#				#				global driver
		self.inited = False
		self.driver = dbg.debuggerdriver.createDriver(self.driver.debugger, event_queue)
#		self.driver.debugger.SetLoggingCallback(self.my_custom_log_callback)
		self.driver.debugger.SetAsync(False)
#			self.driver.aborted = False
			
#			self.driver.createTarget(filename)
		self.driver.signals.event_queued.connect(self.handle_event_queued)
		self.driver.start()
		self.driver.createTarget(filename)
		if self.driver.debugger.GetNumTargets() > 0:
			target = self.driver.getTarget()
			print(target)
			if self.setHelper.getValue(SettingsValues.BreakAtMainFunc):
				main_bp = self.bpHelper.addBPByName(self.setHelper.getValue(SettingsValues.MainFuncName))
				print(main_bp)

			launch_info = target.GetLaunchInfo()

			#########
			# print("AFTER GETLAUNCHINFO!!!!")
			# Create a temporary file to capture output
			# output_path = "/tmp/lldb_output.txt"
			# output_file = open(output_path, "w")
			# output_fd = output_file.fileno()

			# stdout_action = lldb.SBFileAction()
			# stdout_action.Open(output_path, True, False)  # append=False, read=False
			# launch_info.SetFileAction(lldb.eLaunchFlagStdout, stdout_action)
			#########
			# Create a pipe to capture the output
			# read_fd, write_fd = os.pipe()
			# launch_info.SetStandardOutput(write_fd)  # Redirect stdout
			# launch_info.SetStandardError(write_fd)  # (optional) Redirect stderr too

			if self.setHelper.getValue(SettingsValues.StopAtEntry):
				launch_info.SetLaunchFlags(lldb.eLaunchFlagDisableASLR + lldb.eLaunchFlagStopAtEntry)# lldb.eLaunchFlagDisableASLR + 
			error = lldb.SBError()
			# SBProcess
			self.process = target.Launch(launch_info, error)
			output = io.StringIO()

			#########
			# Close the write end in your script so you can read from the read end
			# os.close(write_fd)

			# Read the output
			# output = os.read(read_fd, 4096).decode("utf-8")
			# print(f"Captured output:\n{output}")

			# Read output from file
			# output_file.close()
			# with open(output_path, "r") as f:
			# 	captured_output = f.read()

			# print(f"Captured output:\n{captured_output}")
			#########

#			target.Launch(self.driver.debugger.GetListener(), None, None, None, output.fileno(), None, None, 0, False, error)
##			'/tmp/stdout.txt'
			self.loadTarget()
			self.setWinTitleWithState("Target loaded")
			
			
		
		
	def handle_event_queued(self, event):
		# print(f"EVENT-QUEUED: {event}")
		# print(f'GUI-GOT-EVENT: {event} / {event.GetType()} ====>>> THATS DA ONE')
		desc = get_description(event)
		# print('GUI-Event description:', desc)
		# print('GUI-Event data flavor:', event.GetDataFlavor())
		if str(event.GetDataFlavor()) == "ProgressEventData":
			self.treListener.handle_gotNewEvent(event)
			pass
		
	def handle_breakpointEvent(self, event):
		# print(f"handle_breakpointEvent: {event}")
		pass

	def loadTarget(self):
		
		if self.driver.debugger.GetNumTargets() > 0:
			target = self.driver.getTarget()
			# print(f"loadTarget => {target}")
			if target:
				
				fileInfos = FileInfos()
				fileInfos.loadFileInfo(target, self.tblFileInfos)
#				self.devHelper.bpHelper = self.bpHelper
				self.devHelper.setupDevHelper()
#				self.devHelper.setDevBreakpoints()
				# self.devHelper.setDevWatchpointsNG()
				self.treStats.loadFileStats()
#					
				self.process = target.GetProcess()
				if self.process:
					self.listener = LLDBListener(self.process, self.driver.debugger)
					self.listener.setHelper = self.setHelper
					self.listener.breakpointEvent.connect(self.handle_breakpointEvent)
					self.listener.processEvent.connect(self.handle_processEvent)
					self.listener.gotEvent.connect(self.treListener.handle_gotNewEvent)
					self.listener.addListenerCalls()
					self.listener.start()
					
#					
#					idx = 0
					# print(f"self.process.GetNumThreads() => {self.process.GetNumThreads()}")
					self.thread = self.process.GetThreadAtIndex(0)
#					print(self.thread)
#					print(self.thread.GetNumFrames())
					if self.thread:
#						
						# print(f"self.thread.GetNumFrames() => {self.thread.GetNumFrames()}")
#						
						for z in range(self.thread.GetNumFrames()):
							frame = self.thread.GetFrameAtIndex(z)
							self.tabWidgetStruct.cmbModules.addItem(frame.GetModule().GetFileSpec().GetFilename() + " (" + str(frame.GetFrameID()) + ")")
							if frame.GetModule().GetFileSpec().GetFilename() != target.GetExecutable().GetFilename():
#								self.process.Continue()
								continue
#							print(f"frame.GetModule() => {frame.GetModule().GetFileSpec().GetFilename()}")
#							frame = self.thread.GetFrameAtIndex(z)
							if frame:
#								print(frame)
#								print(f"frame.GetPC() => {frame.GetPC()}")
#								self.rip = frame.GetPC()
								self.start_loadDisassemblyWorker(True)

								context = frame.GetSymbolContext(lldb.eSymbolContextEverything)
#								self.workerManager.start_loadSourceWorker(self.driver.debugger, ConfigClass.testTargetSource, self.handle_loadSourceFinished, context.GetLineEntry().GetLine())

	def resetGUI(self):
#		print(f"Resetting GUI")
		self.updateStatusBar(f"Resetting GUI ...")
		self.txtMultiline.resetContent()
		self.tblFileInfos.resetContent()
		self.tabWidgetStruct.resetContent()
		self.treStats.clear()
#		self.tblReg.resetContent()
		for tbl in self.tblRegs:
			tbl.resetContent()
		self.tblRegs.clear()
		self.tabWidgetReg.clear()
		self.tblVariables.resetContent()
		self.wdtBPsWPs.treBPs.clear()
		self.tabWatchpoints.tblWatchpoints.resetContent()
#		self.wdtBPsWPs.tblWPs.resetContent()
#		self.txtSource.setText("")
#		self.treThreads.clear()
#		self.wdtSearch.resetContent()
		self.tblHex.resetContent()
##		self.wdtBPsWPs.treWPs.clear()
		
	inited = False
	def handle_processEvent(self, process):
		state = 'stopped'
		if process.state == eStateStepping or process.state == eStateRunning:
			state = 'running'
		elif process.state == eStateExited:
			state = 'exited'
			self.should_quit = True
		thread = process.selected_thread
		# print('Process event: %s, reason: %d' % (state, thread.GetStopReason()))
		if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
#			for z in range(thread.GetNumFrames()):
			frame = thread.GetFrameAtIndex(0)
#				if frame.GetModule().GetFileSpec().GetFilename() != self.driver.getTarget().GetExecutable().GetFilename():
##					process.Continue()
#					continue
#				print(f"frame.GetModule() => {frame.GetModule().GetFileSpec().GetFilename()}")
#							frame = self.thread.GetFrameAtIndex(z)
			if frame:
				# print(frame)
				if not self.inited:
					return
				self.handle_debugStepCompleted(StepKind.Continue, True, thread.GetFrameAtIndex(0).register["rip"].value, frame)
#								self.rip = lldbHelper.convert_address(frame.register["rip"].value)
#					self.rip = ""
#					self.start_loadDisassemblyWorker(True)
		pass
	def setResumeActionIcon(self, icon):
		self.load_resume.setIcon(icon)
		pass

	def start_findReferencesWorker(self, address):
		
		self.updateStatusBar(f"Finding references to {address} in code...")
		self.wdtSearch.resetContent()
		self.target = lldb.debugger.GetSelectedTarget()
		idxOuter = 0
		# import pdb; pdb.set_trace()
		# bFoundRef = False
		nFoundRef = 0
		for module in self.target.module_iter():
			# print(f"In module: {idxOuter}")
			if idxOuter != 0:
				idxOuter += 1
				continue
			idx = 0
			for section in module.section_iter():
				# print(f"In module: {idxOuter}, section: {idx}, section-name: {section.GetName()}")
				if section.GetName() == "__TEXT":
					# if idx != 1:
					# 	idx += 1
					# 	continue
					
#					print('Number of subsections: %d' % section.GetNumSubSections())
					for subsec in section:
						# print(f"In module: {idxOuter}, section: {idx}, section-name: {section.GetName()}, subsec-name: {subsec.GetName()}")
						if subsec.GetName() == "__text" or subsec.GetName() == "__stubs":
							idxSym = 0
							lstSym = module.symbol_in_section_iter(subsec)
							secLen = module.num_symbols #len(lstSym)
							for sym in lstSym:
								# print(f"In symFuncName: {sym.GetStartAddress().GetFunction().GetName()}")
								symFuncName = sym.GetStartAddress().GetFunction().GetName()
								for instruction in sym.GetStartAddress().GetFunction().GetInstructions(self.target):
									if symFuncName == instruction.GetAddress().GetFunction().GetName():
										# self.signals.loadInstruction.emit(instruction)
										print(instruction)
										if(str(instruction.GetOperands(self.target)) == address):
											# print(f"==========>>>>>>>>>>> YES We got REFERENCE to: {address} @: {hex(int(str(instruction.GetAddress().GetLoadAddress(self.target)), 10))}...")
											# bFoundRef = True
											nFoundRef += 1;
											daData = str(instruction.GetData(self.target))
											idxNG = daData.find("                             ")
											if idxNG == -1:
												idxNG = daData.find("		            ")
												if idxNG == -1:
													idxNG = daData.find("		         ")
													if idxNG == -1:
														idxNG = daData.find("		      ")
									#					if idxNG == -1:
									#						idxNG = daData.find("		      ")
											if  idxNG != -1:
												daHex = daData[:idxNG]
												daDataNg = daData[idxNG:]
											# self.txtMultiline.appendAsmText(hex(int(str(instruction.GetAddress().GetLoadAddress(target)), 10)), instruction.GetMnemonic(target),  instruction.GetOperands(target), instruction.GetComment(target), daHex, "".join(str(daDataNg).split()), True)
											self.wdtSearch.table.addRow(str(nFoundRef), hex(int(str(instruction.GetAddress().GetLoadAddress(self.target)), 10)), section.GetName() + "." + subsec.GetName(), instruction.GetMnemonic(self.target) + " " + instruction.GetOperands(self.target), daHex) # "".join(str(daDataNg).split()) # data[string_index:end_index].decode(), self.bytearray_to_hex(data[string_index:end_index]))
								idxSym += 1
		if(nFoundRef > 0):
			# self.wdtSearch.resetContent()
			self.tabWidgetDbg.setCurrentWidget(self.wdtSearch)
			self.wdtSearch.table.horizontalHeaderItem(3).setText(f"Instruction")
			self.wdtSearch.cmbSearchType.setCurrentIndex(2)
			self.updateStatusBar(f"{nFoundRef} references to {address} found in code!")
		else:
			self.updateStatusBar(f"No references to {address} found in code!")
			pass



		# # target = lldb.debugger.GetSelectedTarget()
		# # address_to_find = 0xdeadbeef  # your target address
		# address_to_find = int(address, 16) #hex(address)
		# module = self.driver.getTarget().module[0]  # assuming first module; adjust if needed

		# for sym in module:
		#     if not sym.IsValid() or not sym.GetStartAddress().IsValid():
		#         continue

		#     func_start = sym.GetStartAddress()
		#     func_end = sym.GetEndAddress()
		#     insts = target.ReadInstructions(func_start, func_end.GetOffset() - func_start.GetOffset())

		#     for inst in insts:
		#         if address_hex in inst.GetOperands(target):
		#             print(f"Reference to {address_hex} found at {inst.GetAddress()}: {inst}")





		# # target = lldb.debugger.GetSelectedTarget()
		# # process = target.GetProcess()

		# address_to_find = int(address, 16) #hex(address)  # The address you're looking for
		# search_bytes = address_to_find.to_bytes(8, 'big')  # Use 'little' or 'big' based on target arch
		# error = lldb.SBError()

		# # Pick a region to search, you could iterate over memory regions too
		# start_addr = 0x100000000  # Adjust based on your target
		# size = 0x10000

		# memory = self.process.ReadMemory(start_addr, size, error)
		# if error.Success():
		#     offset = memory.find(search_bytes)
		#     if offset != -1:
		#         found_addr = start_addr + offset
		#         print(f"Found reference at 0x{found_addr:x}")
		#     else:
		#         print("Reference not found in searched region.")
		# else:
		#     print("Failed to read memory:", error.GetCString())

		pass

	isProcessRunning = False
	def start_debugWorker(self, driver, kind):
		self.wdtBPsWPs.treBPs.clearPC()
		self.txtMultiline.clearPC()
		if self.workerManager.start_debugWorker(driver, kind, self.handle_debugStepCompleted):
			self.setWinTitleWithState("Running")
			self.setResumeActionIcon(ConfigClass.iconPause)
			self.isProcessRunning = True
		else:
			self.setResumeActionIcon(ConfigClass.iconResume)
			self.isProcessRunning = False

	rip = ""

	def handle_debugStepCompleted(self, kind, success, rip, frm):
		if success:
			self.rip = rip
			self.txtMultiline.setPC(int(str(self.rip), 16))
			self.wdtBPsWPs.treBPs.setPC(self.rip)
			self.start_loadRegisterWorker(False)
			self.wdtBPsWPs.reloadBreakpoints(False)
			self.tabWatchpoints.reloadWatchpoints(False)
			self.loadStacktrace()
			
			context = frm.GetSymbolContext(lldb.eSymbolContextEverything)
			self.workerManager.start_loadSourceWorker(self.driver.debugger, ConfigClass.testTargetSource, self.handle_loadSourceFinished, context.GetLineEntry().GetLine())
#			self.setResumeActionIcon(ConfigClass.iconResume)
			self.setWinTitleWithState("Interrupted")
			self.setResumeActionIcon(ConfigClass.iconResume)
		else:
			# print(f"Debug STEP ({kind}) FAILED!!!")
			self.setResumeActionIcon(ConfigClass.iconResume)
		self.isProcessRunning = False
		pass
		
	def start_loadDisassemblyWorker(self, initTable = True):
		self.symFuncName = ""
		# import pdb; pdb.set_trace()
		# print(f'start_loadDisassemblyWorker')
		self.workerManager.start_loadDisassemblyWorker(self.handle_loadInstruction, self.handle_workerFinished, initTable)

	def start_loadRegisterWorker(self, initTabs = True):
		self.workerManager.start_loadRegisterWorker(self.handle_loadRegister, self.handle_loadRegisterValue, self.handle_updateRegisterValue, self.handle_loadVariableValue, self.handle_updateVariableValue, self.handle_loadRegisterFinished, initTabs)
		
	def handle_loadInstruction(self, instruction):
		target = self.driver.getTarget()
		
		if self.symFuncName != instruction.GetAddress().GetFunction().GetName():
			self.symFuncName = instruction.GetAddress().GetFunction().GetName()
			
			self.txtMultiline.appendAsmSymbol(str(instruction.GetAddress().GetLoadAddress(target)), self.symFuncName)
			
#		print(f'instruction.GetComment(target) => {instruction.GetComment(target)}')
			
		daData = str(instruction.GetData(target))
		idx = daData.find("                             ")
		if idx == -1:
			idx = daData.find("		            ")
			if idx == -1:
				idx = daData.find("		         ")
				if idx == -1:
					idx = daData.find("		      ")
#					if idx == -1:
#						idx = daData.find("		      ")
		if  idx != -1:
			daHex = daData[:idx]
			daDataNg = daData[idx:]
#		self.txtMultiline.appendAsmText(hex(int(str(instruction.GetAddress().GetLoadAddress(target)), 10)), instruction.GetMnemonic(target),  instruction.GetOperands(target), instruction.GetComment(target), str(instruction.GetData(target)).replace("                             ", "\t\t").replace("		            ", "\t\t\t").replace("		         ", "\t\t").replace("		      ", "\t\t").replace("			   ", "\t\t\t"), True)
			
			self.txtMultiline.appendAsmText(hex(int(str(instruction.GetAddress().GetLoadAddress(target)), 10)), instruction.GetMnemonic(target),  instruction.GetOperands(target), instruction.GetComment(target), daHex, "".join(str(daDataNg).split()), True)
		pass
		
	def handle_workerFinished(self):
#		print(f"Current RIP: {self.rip} / {hex(self.rip)} / DRIVER: {self.driver.getPC()} / {self.driver.getPC(True)}")
		QApplication.processEvents()
		self.txtMultiline.setPC(self.driver.getPC(), True)
		self.start_loadRegisterWorker()
#		self.reloadBreakpoints(True)
		self.wdtBPsWPs.treBPs.clear()
		self.wdtBPsWPs.reloadBreakpoints(True)
		self.tabWatchpoints.reloadWatchpoints(True)
		self.loadStacktrace()
#		print(f'self.rip => {self.rip}')
		QApplication.processEvents()
#		self.txtMulriline.locationStack.pushLocation(hex(self.driver.getPC()).lower())
#		print(f"self.txtMultiline.table.rowCount() => {self.txtMultiline.table.rowCount()}")
		
	def handle_loadRegisterFinished(self):
		self.setProgressValue(100)
		# self.updateStatusBar("handle_loadRegisterFinished")
#		self.driver.debugger.SetAsync(True)
		pass
		
#	def handle_statusBarUpdate(self, txt):
#		self.updateStatusBar(txt)
#		
#	def handle_progressUpdate(self, value, statusTxt):
#		self.setProgressValue(value)
#		self.updateStatusBar(statusTxt)
		
	currTreDet = None
	tblRegs = []
	def handle_loadRegister(self, type):
		tabDet = QWidget()
		tabDet.setContentsMargins(0, 0, 0, 0)
		tblReg = RegisterTableWidget()
		tabDet.tblWdgt = tblReg
		self.tblRegs.append(tblReg)
		tabDet.setLayout(QVBoxLayout())
		tabDet.layout().addWidget(tblReg)
		tabDet.layout().setContentsMargins(0, 0, 0, 0)
		self.tabWidgetReg.addTab(tabDet, type)
		self.currTblDet = tblReg
#		pass
		
	def handle_loadRegisterValue(self, idx, type, register, value):
#		target = self.driver.getTarget()
#		process = target.GetProcess()
		self.currTblDet.addRow(type, register, value)
		
	def handle_updateRegisterValue(self, idx, type, register, value):
		tblWdgt = self.tabWidgetReg.widget(idx).tblWdgt
		for i in range(tblWdgt.rowCount()):
			if tblWdgt.item(i, 0).text() == type:
				tblWdgt.item(i, 1).setText(register)
				tblWdgt.item(i, 2).setText(value)
				break

	def handle_loadRememberLocation(self, name, value, data, valType, address, comment):
		# self.inited = True
		self.tblRememberLoc.addRow(name, value, valType, address, data, comment)

	def handle_loadVariableValue(self, name, value, data, valType, address):
		self.inited = True
		self.tblVariables.addRow(name, value, valType, address, data)
		
	def handle_updateVariableValue(self, name, value, data, valType, address):
		if self.isAttached:
			self.tblVariables.updateOrAddRow(name, value, valType, address, data)
		else:
			self.tblVariables.updateRow(name, value, valType, address, data)
		
	def handle_loadSourceFinished(self, sourceCode, autoScroll = True):
		if sourceCode != "":
			horizontal_value = self.txtSource.horizontalScrollBar().value()
			
			if not autoScroll:
				vertical_value = self.txtSource.verticalScrollBar().value()
				
			self.txtSource.setEscapedText(sourceCode)
			currTabIdx = self.tabWidgetDbg.currentIndex()
			self.tabWidgetDbg.setCurrentWidget(self.txtSource)
			self.txtSource.horizontalScrollBar().setValue(horizontal_value)
			if not autoScroll:
				self.txtSource.verticalScrollBar().setValue(vertical_value)
			else:
				
#				QApplication.processEvents()
#				currTabIdx = self.tabWidgetDbg.currentIndex()
#				self.tabWidgetDbg.setCurrentIndex(3)
#				line_text = "=>"
#				self.txtSource.scroll_to_line(line_text)
#				self.tabWidgetDbg.setCurrentIndex(currTabIdx)
				
				frame = self.driver.getTarget().GetProcess().GetThreadAtIndex(0).GetFrameAtIndex(0)
				line_entry = frame.GetLineEntry()
				line_number = line_entry.GetLine()
				# print(f"line_entry: {line_entry} / line_number: {line_number}")
				if line_number != 0xFFFFFFFF:
					self.txtSource.scroll_to_lineNG(line_number)
				self.tabWidgetDbg.setCurrentIndex(currTabIdx)
		else:
			self.txtSource.setText("<Source code NOT available>")
			
	def loadStacktrace(self):
		self.process = self.driver.getTarget().GetProcess()
		self.thread = self.process.GetThreadAtIndex(0)
#		from lldbutil import print_stacktrace
#		st = get_stacktrace(self.thread)
##			print(f'{st}')
#		self.txtOutput.setText(st)
		
		idx = 0
		if self.thread:
#			self.treThreads.doubleClicked.connect()
			self.treThreads.clear()
			self.processNode = QTreeWidgetItem(self.treThreads, ["#0 " + str(self.process.GetProcessID()), hex(self.process.GetProcessID()) + "", self.process.GetTarget().GetExecutable().GetFilename(), '', ''])
			
			self.threadNode = QTreeWidgetItem(self.processNode, ["#" + str(idx) + " " + str(self.thread.GetThreadID()), hex(self.thread.GetThreadID()) + "", self.thread.GetQueueName(), '', ''])
			
			numFrames = self.thread.GetNumFrames()
			
			for idx2 in range(numFrames):
				self.setProgressValue(idx2 / numFrames)
				frame = self.thread.GetFrameAtIndex(idx2)
				frameNode = QTreeWidgetItem(self.threadNode, ["#" + str(frame.GetFrameID()), "", str(frame.GetPCAddress()), str(hex(frame.GetPC())), self.GuessLanguage(frame)])
				idx += 1
				
			self.processNode.setExpanded(True)
			self.threadNode.setExpanded(True)
#			self.devHelper.setDevWatchpoints()
			
	def GuessLanguage(self, frame):
		return lldb.SBLanguageRuntime.GetNameForLanguageType(frame.GuessLanguage())