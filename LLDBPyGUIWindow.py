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
from ui.rflagTableWidget import RFlagTableWidget, RFlagWidget

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
from ui.dialogs.spinnerOverlay import *
from worker.workerManager import *
from worker.baseWorkerNG import *
from config import *

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


def wpcallbackng(frame, wp, dict):
	# print(f"================>>>>>>>>>>>>> YES WATCHPOINT HIT <<<<<<<<<<<=================")
	# wp.SetEnabled(True)
	# print(frame)
	# print(wp)
# 	res = lldb.sbcommandreturnobject()
# 	ci = frame.getthread().getprocess().gettarget().getdebugger().getcommandinterpreter()
# 	ci.handlecommand('command script import "./lldbpyguiwindow.py"', res)
# 	# settings
# #	ci.handlecommand(f"w s v {varname}", res)
# 	ci.handlecommand(f"watchpoint command add -f lldbpyguiwindow.wpcallback {wp.getid()}", res)
# 	print(wp)
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

	# def wpcallbackng(self):
	# 	print(f"================>>>>>>>>>>>>> YES WATCHPOINT CALLBACK NG <<<<<<<<<<<=================")
	# 	pass

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

	def stopWorkerAndQuitThread(self):
		self.worker.stop()
		self.threadLoad.quit()
		self.finish_startup()
		pass

	def __init__(self, driver = None):
		super().__init__()

		# self.start_operation()

		self.driver = driver

		self.threadLoad = QThread()
		self.worker = Worker(self, ConfigClass.testTarget, True, ConfigClass.testTargetSource)
		self.worker.logDbg.connect(logDbg)
		self.worker.logDbgC.connect(logDbgC)
		# self.worker.logDbgC.connect(logDbgC)
		# self.worker.loadFileInfosCallback.connect(self.loadFileInfosCallback)
		# self.worker.loadJSONCallback.connect(self.treStats.loadJSONCallback)

		self.worker.moveToThread(self.threadLoad)
		self.threadLoad.started.connect(self.worker.run)
		self.worker.show_dialog.connect(self.start_operation)
		self.worker.finished.connect(self.stopWorkerAndQuitThread)


		# self.threadLoad.start()

		# lib.utils.main_window = self  # inside MainWindow __init__


		# Set the custom logging callback
		self.driver.debugger.SetLoggingCallback(self.my_custom_log_callback)

		self.targetBasename = "NG"

		# self.spinner_overlay = SpinnerOverlay(self)
		# self.spinner_overlay.show()

		# self.dialog = SpinnerDialog()
		# self.dialog.show()

		# QTimer.singleShot(3000, self.finish_startup)  # Simulate startup delay


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

		# self.goep_action = QAction(ConfigClass.iconBug, 'Go OE&P', self)
		# self.goep_action.setStatusTip('Goto OEP (original entry point)')
		# self.goep_action.setShortcut('Ctrl+E')
		# self.goep_action.triggered.connect(self.goep_clicked)

		self.goep2_action = QAction(ConfigClass.iconBug, 'Goto OE&P', self)
		self.goep2_action.setStatusTip('Goto OEP (original entry point)')
		self.goep2_action.setShortcut('Ctrl+E')
		self.goep2_action.triggered.connect(self.goep2_clicked)

		self.goep3_action = QAction(ConfigClass.iconBug, 'Goto current PC', self)
		self.goep3_action.setStatusTip('Goto current PC (Current instruction)')
		self.goep3_action.setShortcut('Ctrl+I')
		self.goep3_action.triggered.connect(self.goep3_clicked)



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

		self.test2_action = QAction(ConfigClass.iconTest, '&Test 2', self)
		self.test2_action.setStatusTip('Test 2')
		self.test2_action.setShortcut('Ctrl+2')
		self.test2_action.triggered.connect(self.test2_clicked)
		self.toolbar.addAction(self.test2_action)

		self.menu = self.menuBar()

		self.main_menu = self.menu.addMenu("Main")
		self.main_menu.addAction(self.settings_action)

		self.file_menu = self.menu.addMenu("&Load Action")
		self.file_menu.addAction(self.load_action)

		self.file_menu.addSeparator()
		self.oep_menu = self.file_menu.addMenu("&GoTo ...")
		self.oep_menu.addAction(self.goep2_action)
		self.oep_menu.addAction(self.goep3_action)

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

		self.splitterAsm = QSplitter()
		self.splitterAsm.setContentsMargins(0, 0, 0, 0)
		self.splitterAsm.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.splitterAsm.setOrientation(Qt.Orientation.Horizontal)

		self.txtMultiline = AssemblerTextEdit(self.driver, self.bpHelper)
		self.wdtControlFlow = QControlFlowWidget(self.txtMultiline, self.driver)
		self.wdtControlFlow.setContentsMargins(0, 0, 0, 0)
		self.wdtControlFlowLeft = QWidget()
		self.wdtControlFlowLeft.setContentsMargins(0, 30, 0, 0)
		self.layControlFlowLeft = QVBoxLayout(self.wdtControlFlowLeft)
		self.layControlFlowLeft.setContentsMargins(0, 0, 0, 0)
		self.layControlFlowLeft.addWidget(self.wdtControlFlow)
		self.splitterAsm.addWidget(self.wdtControlFlowLeft)

		self.wdtControlFlowLeft.setMaximumWidth(80)
		self.wdtControlFlow.setMaximumWidth(80)

		self.splitterAsm.addWidget(self.txtMultiline)

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

		# self.tblRememberLoc = RememberLocationsTableWidget(self.driver, self.bpHelper)

		# self.tabWidgetDbg.addTab(self.tblRememberLoc, "Remember Locations")

		self.treListener = ListenerWidget(self.driver, self.setHelper)
		self.treListener.treEventLog.sigSTDOUT.connect(self.testSTDOUT)
		self.treListener.setContentsMargins(0, 0, 0, 0)
		# self.treListener.listener.signals.processEvent.connect(self.handle_processEvent)

		self.tabWidgetDbg.addTab(self.treListener, "Listeners")

		self.tabWidgetMain = QTabWidget()

		self.tabWidgetConsoles = QTabWidget()
		self.tabWidgetConsole = QTabWidget()
		self.tabWidgetConsole.setContentsMargins(0, 0, 0, 0)
		self.tabWidgetConsole.setLayout(QVBoxLayout())
		# self.consoleWidget = ConsoleWidget(self.workerManager)
		# self.consoleWidget.setContentsMargins(0, 0, 0, 0)
		self.tabWidgetConsole.layout().setContentsMargins(0, 0, 0, 0)
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

		# self.output_text_edit = QTextEdit()
		# ConsoleWidget()
		self.output_text_edit = ConsoleWidget() #.setReadOnly(True)

		# self.tabWidgetConsolePrompt.setLayout(QVBoxLayout())
		# self.tabWidgetConsoles.addTab(self.tabWidgetConsolePrompt, "Prompt")

		# Create and add the console widget
		self.console_widget = PyQtConsoleWidget(locals_dict=exposed_variables)
		self.tabWidgetConsole.layout().addWidget(self.console_widget)
		# self.tabWidgetDbg.addTab(self.tabWidgetConsoles, "Consoles")

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
		self.tabWidgetConsoles.addTab(self.tabWidgetConsole, "Python")
		self.tabWidgetConsoles.addTab(self.output_text_edit, "System shell")


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
		# self.dbgWidgetMain = QWidget()
		# self.dbgWidgetMain.setLayout(QVBoxLayout())
		# self.dbgWidgetMain.setContentsMargins(0, 0, 0, 0)
		# # self.dbgWidgetMain.layout().addWidget(self.tabWidgetMain)
		self.wdtDbg = DbgOutputWidget()

		self.splitterDbgMain = QSplitter()
		self.splitterDbgMain.setContentsMargins(0, 0, 0, 0)
		self.splitterDbgMain.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.splitterDbgMain.setOrientation(Qt.Orientation.Vertical)
		self.splitterDbgMain.addWidget(self.tabWidgetMain)
		self.splitterDbgMain.addWidget(self.wdtDbg)
		self.setCentralWidget(self.splitterDbgMain)
		self.bpHelper.setCtrls(self.txtMultiline, self.wdtBPsWPs.treBPs)

		self.threadpool = QThreadPool()

		self.tmrResetStatusBar.setInterval(int(self.setHelper.getValue(SettingsValues.StatusBarMsgTimeout)))
		self.tmrResetStatusBar.setSingleShot(True)
		self.tmrResetStatusBar.timeout.connect(self.resetStatusBar)
#		self.tmrResetStatusBar.start()

		# Setup CALLBACKS
		self.worker.loadFileInfosCallback.connect(self.loadFileInfosCallback)
		self.worker.loadJSONCallback.connect(self.treStats.loadJSONCallback)
		self.worker.loadModulesCallback.connect(self.loadModulesCallback)
		self.worker.enableBPCallback.connect(self.enableBPCallback)
		self.worker.loadInstructionCallback.connect(self.handle_loadInstruction)
		self.worker.finishedLoadInstructionsCallback.connect(self.handle_workerFinished)
		self.worker.handle_breakpointEvent = self.handle_breakpointEvent
		self.worker.handle_processEvent = self.handle_processEvent
		self.worker.handle_gotNewEvent = self.treListener.handle_gotNewEvent
		self.worker.loadRegisterCallback.connect(self.handle_loadRegister)
		self.worker.loadRegisterValueCallback.connect(self.handle_loadRegisterValue)
		self.worker.loadVariableValueCallback.connect(self.handle_loadVariableValue)

		self.worker.loadBreakpointsValueCallback.connect(self.wdtBPsWPs.handle_loadBreakpointValue)
		self.worker.updateBreakpointsValueCallback.connect(self.wdtBPsWPs.handle_updateBreakpointValue)
		self.worker.loadWatchpointsValueCallback.connect(self.tabWatchpoints.tblWatchpoints.handle_loadWatchpointValue)
		self.worker.updateWatchpointsValueCallback.connect(self.tabWatchpoints.tblWatchpoints.handle_updateWatchpointValue)
		self.worker.finishedLoadingSourceCodeCallback.connect(self.handle_loadSourceFinished)

		self.worker.runControlFlow_loadConnections.connect(self.runControlFlow_loadConnections)

		# loadBreakpointsValueCallback = pyqtSignal(object, bool)
		# updateBreakpointsValueCallback = pyqtSignal(object)
		# loadWatchpointsValueCallback = pyqtSignal(object)
		# updateWatchpointsValueCallback = pyqtSignal(object)




		# ======== DEV CMDs ##########
		self.tabWidgetDbg.setCurrentIndex(2)

		self.updateStatusBar("LLDBPyGUI loaded successfully!")

		self._restore_size()

	def start_operation(self):
		self.symFuncName = ""
		self.dialog = SpinnerDialog()
		self.dialog.show()

		# num_steps = 100
		# self.progress = QProgressDialog("Processing...", "Cancel", 0, num_steps, self)
		# self.progress.setWindowModality(Qt.WindowModality.WindowModal)
		# self.progress.setMinimumDuration(0)  # Show immediately
		# # self.progress.setValue(0)
		# self.progress.setValue(5)
		#
		# # self.current_step = 0
		# self.timer = QTimer()
		# self.timer.timeout.connect(self.perform_step)
		# self.timer.start(500)  # Simulate work every 500ms

	def perform_step(self):
		if self.progress.wasCanceled():
			self.timer.stop()
			print("Operation canceled.")
			return

		# self.current_step += 1
		# self.progress.setValue(self.current_step)

		# if self.current_step >= self.progress.maximum():
		# 	self.timer.stop()
		# 	print("Operation completed.")

	def finish_startup(self):
		self.dialog.close()
		# self.spinner_overlay.close()
		# self.dialog.close()
		# self.timer.stop()
		# self.progress.cancel()
		# self.timer.stop()
		logDbg(f"finish_startup called ... trying to close progress dialog ...")
		self.wdtControlFlow.view.verticalScrollBar().setValue(int(self.txtMultiline.table.verticalScrollBar().value()))
		# self.progress.setValue(10)
		# self.progress.hide()

	# Continue initializing your app


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

	def testSTDOUT(self, strOut):
		print(f'HEEEEEELLLLLLLOOOOOO FROM STDOUT => {strOut}')
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

		# lib.utils.setStatusBar(f"Showing memory for address: {addr}")

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

	def goep_clicked(self):
		logDbg(f"Goto OEP clickediclicked!")
		addrObj = get_oep(self.driver.debugger)
		addrObjHex = f"{hex(addrObj)}"
		print(f"OEP2 (load addr): ")
		logDbg(f"OEP2 (load addr): {addrObjHex}")

		# lib.utils.setStatusBar(f"Go to address: {addrObjHex}")

		self.txtMultiline.viewAddress(addrObjHex)
		pass

	def goep2_clicked(self):
		logDbg(f"Goto OEP 2 clickediclicked!")
		# addrObj = get_oep(self.driver.debugger)
		# print(f"OEP (load addr): 0x{hex(addrObj)}")
		# logDbg(f"OEP (load addr): 0x{hex(addrObj)}")

		addrObj2 = find_main(self.driver.debugger)
		addrObj2Hex = f"{hex(addrObj2)}"
		print(f"OEP2 (load addr): ")
		logDbg(f"OEP2 (load addr): {addrObj2Hex}")

		# lib.utils.setStatusBar(f"Go to address: {addrObj2Hex}")

		self.txtMultiline.viewAddress(addrObj2Hex)
		pass

	def goep3_clicked(self):
		logDbg(f"Goto OEP 3 clickediclicked!")
		self.txtMultiline.viewCurrentAddress()
		pass



	def load_clicked(self):
		filename = showOpenFileDialog()
		if filename != None and filename != "":
			self.txtMultiline.resetContent()
			self.wdtBPsWPs.treBPs.clear()
			self.tabWatchpoints.tblWatchpoints.resetContent()
			self.wdtControlFlow.resetContent()
			self.setResumeActionIcon(True)

			# self.wdtBPsWPs.treBPs.clear()
			global event_queue
			event_queue = queue.Queue()
			self.should_quit = False
			global driver
			driver = dbg.debuggerdriver.createDriver(self.driver.debugger, event_queue)
			self.driver = driver
			self.txtMultiline.table.bpHelper.driver = self.driver
			self.driver.setDone(False)
			self.driver.start()
			# print(f"Loading new target: '{filename}")
			# self.loadNewExecutableFile(filename)
			# self.worker.loadNewExecutableFile(filename)
			self.threadLoad.start()

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
		logDbgC(f"Trying to kill debugged app ...")
		target = self.driver.getTarget()
		if target:
			process = target.GetProcess()
			if process:
				# Now that we are done dump the stdout and stderr
				# process_stdout = process.GetSTDOUT(1024)
				# if process_stdout:
				# 	print(f"=============>>>>>>>>>>>> STDOUT: {process_stdout}")
				# 	print("Process STDOUT:\n%s" % (process_stdout))
				# 	while process_stdout:
				# 		process_stdout = process.GetSTDOUT(1024)
				# 		print(f"=============>>>>>>>>>>>> STDOUT: {process_stdout}")
				# 		print(process_stdout)
				# process_stderr = process.GetSTDERR(1024)
				# if process_stderr:
				# 	print(f"=============>>>>>>>>>>>> STDERR: {process_stderr}")
				# 	print("Process STDERR:\n%s" % (process_stderr))
				# 	while process_stderr:
				# 		process_stderr = process.GetSTDERR(1024)
				# 		print(f"=============>>>>>>>>>>>> STDERR: {process_stderr}")
				# 		print(process_stderr)
				# # process.Kill()  # kill the process
				# lldb.debugger.Terminate()
				# self.driver.debugger.Terminate()
				# lldb.debugger.Terminate()
				# if self.listener is not None:
				# 	self.listener.should_quit = True
				self.worker.listener.should_quit = True
				errKill = process.Kill()
				if not errKill.Success():
					logDbgC(f'Error killing process: {errKill}')
				else:
					# lldb.debugger.Terminate()
					logDbgC(f"Debugged app killed, cleaning up ...")
					self.driver.debugger.DeleteTarget(target)
					self.driver.debugger.Terminate()
					logDbgC(f"Debugger terminated, cleaning up ...")
					self.resetGUI()
			else:
				logDbgC(f"No valid process found ...")
				pass
		else:
			logDbgC(f"No valid target found ...")
			pass



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

	def test2_clicked(self):
		os.system('clear')  # Unix/Linux/macOS
		statusTxt = "Console cleared"
		if self.setHelper.getValue(SettingsValues.ClearConsoleComplete):
			os.system('clear')  # Unix/Linux/macOS
			statusTxt += " (completely)"

		self.updateStatusBar(statusTxt)

		self.wdtBPsWPs.treBPs.show_notification("REST Notification => From Action (side actionbar)")


	def test_clicked(self):
		self.wdtControlFlow.loadConnections()

	def stopTarget(self):
		# self.driver
		process  = self.driver.getTarget().GetProcess()
		if process:
			self.driver.setDone()
			if hasattr(self, "listener"):
				self.listener.should_quit = True

			# # Now that we are done dump the stdout and stderr
			# process_stdout = process.GetSTDOUT(1024)
			# if process_stdout:
			# 	print(f"=============>>>>>>>>>>>> STDOUT: {process_stdout}")
			# 	print("Process STDOUT:\n%s" % (process_stdout))
			# 	while process_stdout:
			# 		process_stdout = process.GetSTDOUT(1024)
			# 		print(f"=============>>>>>>>>>>>> STDOUT: {process_stdout}")
			# 		print(process_stdout)
			# process_stderr = process.GetSTDERR(1024)
			# if process_stderr:
			# 	print(f"=============>>>>>>>>>>>> STDERR: {process_stderr}")
			# 	print("Process STDERR:\n%s" % (process_stderr))
			# 	while process_stderr:
			# 		process_stderr = process.GetSTDERR(1024)
			# 		print(f"=============>>>>>>>>>>>> STDERR: {process_stderr}")
			# 		print(process_stderr)
			# # process.Kill()  # kill the process

			process.Kill()
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
			# self.loadNewExecutableFile(ConfigClass.testTarget)
			# self.loadNewExecutableFile(ConfigClass.testTarget)
			self.threadLoad.start()

	def loadNewExecutableFile(self, filename):
		return

		# logDbg(f"loadNewExecutableFile({filename})...")
		# self.targetBasename = os.path.basename(filename)
		# self.stopTarget()

		global event_queue
		event_queue = queue.Queue()
#
#				#				global driver
		self.inited = False
		self.worker.listener.should_quit = False
		self.driver = dbg.debuggerdriver.createDriver(self.driver.debugger, event_queue)
#		self.driver.debugger.SetLoggingCallback(self.my_custom_log_callback)
		self.driver.debugger.SetAsync(False)
#			self.driver.aborted = False

#			self.driver.createTarget(filename)
		self.driver.signals.event_queued.connect(self.handle_event_queued)
		self.driver.start()
		self.driver.createTarget(filename)
		# logDbg(f"self.driver.createTarget({filename}) => self.driver.debugger.GetNumTargets() = {self.driver.debugger.GetNumTargets()}")
		if self.driver.debugger.GetNumTargets() > 0:
			target = self.driver.getTarget()
			print(target)
			return

			if self.setHelper.getValue(SettingsValues.BreakAtMainFunc):
				main_bp = self.bpHelper.addBPByName(self.setHelper.getValue(SettingsValues.MainFuncName))
				print(main_bp)
				for bl in main_bp:
					logDbg(f"bl.GetAddress(): {hex(bl.GetAddress().GetLoadAddress(target))}")
				logDbg(f"main_bp: {main_bp}")

			if self.setHelper.getValue(SettingsValues.BreakpointAtMainFunc):
				self.driver.debugger.HandleCommand("process launch --stop-at-entry")
				addrObj2 = find_main(self.driver.debugger)
				main_bp2 = self.bpHelper.enableBP(hex(addrObj2), True, False)
				# print(f"main_bp2 (@{addrObj2}): {main_bp2}")
				logDbgC(f"main_bp2 (@{addrObj2}): {main_bp2}")
				target.GetProcess().Continue()

			# setHelper = SettingsHelper()
			# if self.setHelper.getChecked(SettingsValues.BreakpointAtMainFunc):
			# 	addrObj2 = find_main(self.driver.debugger)
			# 	logDbg(f"Enabling EntryPoint Breakpoint @ {hex(addrObj2)}")
			# 	self.bpHelper.enableBP(hex(addrObj2), True, True)

			# launch_info = target.GetLaunchInfo()

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

			# if self.setHelper.getValue(SettingsValues.StopAtEntry):
			# 	launch_info.SetLaunchFlags(lldb.eLaunchFlagDisableASLR + lldb.eLaunchFlagStopAtEntry)# lldb.eLaunchFlagDisableASLR +
			# 	logDbg(f"launch_info.SetLaunchFlags(lldb.eLaunchFlagDisableASLR + lldb.eLaunchFlagStopAtEntry)")
			# else:
			# 	launch_info.SetLaunchFlags(lldb.eLaunchFlagDebug)
			# 	logDbg(f"launch_info.SetLaunchFlags(lldb.eLaunchFlagDebug)")

			# if self.setHelper.getValue(SettingsValues.StopAtEntry):
			# 	launch_info.SetLaunchFlags(lldb.eLaunchFlagDisableASLR and lldb.eLaunchFlagStopAtEntry)# lldb.eLaunchFlagDisableASLR +
			# # else:
			# # 	launch_info.SetLaunchFlags(lldb.eLaunchFlagStopAtEntry)
			# # 	launch_info.SetLaunchFlags(lldb.eLaunchFlagDisableASLR and lldb.eLaunchFlagStopAtEntry and lldb.eLaunchFlagDebug)

			# error = lldb.SBError()
			# # SBProcess
			# self.break_at_main(self.driver.debugger, "", "", "")
			# self.process = target.Launch(stop_at_entry=True, error=error)
			# self.break_at_main(self.driver.debugger, "", "", "")
			# self.process.Stop()
			# # output = io.StringIO()

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

	# def break_at_main(self, debugger, command, result, internal_dict):
	# 	target = debugger.GetSelectedTarget()
	# 	if not target:
	# 		# result.PutCString("No target loaded.")
	# 		print("No target loaded.")
	# 		return
	#
	# 	# Find the symbol context for 'main'
	# 	matches = target.FindFunctions("main")
	# 	if matches.GetSize() == 0:
	# 		# result.PutCString("Could not find 'main' function.")
	# 		print("Could not find 'main' function.")
	# 		return
	#
	# 	# Get the start address of the first match
	# 	symbol_context = matches.GetContextAtIndex(0)
	# 	start_addr = symbol_context.GetSymbol().GetStartAddress()
	# 	load_addr = start_addr.GetLoadAddress(target)
	#
	# 	# Create a breakpoint at the exact address
	# 	bp = target.BreakpointCreateByAddress(load_addr)
	# 	print(f"Breakpoint set at main's first instruction: 0x{load_addr:x}")

	def handle_event_queued(self, event):
		# print(f"EVENT-QUEUED: {event}")
		# print(f'GUI-GOT-EVENT: {event} / {event.GetType()} ====>>> THATS DA ONE')
		desc = get_description(event)
		# print('GUI-Event description:', desc)
		# print('GUI-Event data flavor:', event.GetDataFlavor())
		if str(event.GetDataFlavor()) == "ProgressEventData": # and not self.should_quit:
			self.treListener.handle_gotNewEvent(event)
			pass

	def handle_breakpointEvent(self, event):
		# print(f"handle_breakpointEvent: {event}")
		pass

	#################################### START NEW CALLBACKS ########################################

	def enableBPCallback(self, address, enabled=True, updateUI=True):
		main_bp2 = self.bpHelper.enableBP(address, enabled, updateUI)
		return main_bp2

	def loadModulesCallback(self, frame, modules=None):
		self.tabWidgetStruct.cmbModules.clear()
		if modules is not None and len(modules) > 0:
			for i in range(len(modules)):
				self.tabWidgetStruct.cmbModules.addItem(
					modules[i].GetFileSpec().GetFilename() + " (" + str(i) + ")")
		else:
			self.tabWidgetStruct.cmbModules.addItem(frame.GetModule().GetFileSpec().GetFilename() + " (" + str(frame.GetFrameID()) + ")")
		pass

	def loadFileInfosCallback(self, mach_header, targetRet):

		self.tblFileInfos.addRow("Magic", MachoMagic.to_str(MachoMagic.create_magic_value(mach_header.magic)),
					 hex(mach_header.magic))
		self.tblFileInfos.addRow("CPU Type", MachoCPUType.to_str(MachoCPUType.create_cputype_value(mach_header.cputype)),
					 hex(mach_header.cputype))
		self.tblFileInfos.addRow("CPU SubType", str(mach_header.cpusubtype), hex(mach_header.cpusubtype))
		self.tblFileInfos.addRow("File Type", MachoFileType.to_str(MachoFileType.create_filetype_value(mach_header.filetype)),
					 hex(mach_header.filetype))
		self.tblFileInfos.addRow("Num CMDs", str(mach_header.ncmds), hex(mach_header.ncmds))
		self.tblFileInfos.addRow("Size CMDs", str(mach_header.sizeofcmds), hex(mach_header.sizeofcmds))
		self.tblFileInfos.addRow("Flags", MachoFlag.to_str(MachoFlag.create_flag_value(mach_header.flags)), hex(mach_header.flags))

		self.tblFileInfos.addRow("----", str("-----"), '-----')
		self.tblFileInfos.addRow("Triple", str(targetRet.GetTriple()), '-')

		# self.progress.setValue(2)

	#################################### END NEW CALLBACKS ########################################

	def loadTarget(self):
		return
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
								logDbgC(f"Module for FileStzuct IS NOT equal executable => continuing ...")
								continue
							else:
								logDbgC(f"Module for FileStzuct IS equal executable => scanning ...")
#							print(f"frame.GetModule() => {frame.GetModule().GetFileSpec().GetFilename()}")
#							frame = self.thread.GetFrameAtIndex(z)
							if frame:
#								print(frame)
#								print(f"frame.GetPC() => {frame.GetPC()}")
#								self.rip = frame.GetPC()
								print(f"BEFORE DISASSEMBLE!!!!")
								self.start_loadDisassemblyWorker(True)

								context = frame.GetSymbolContext(lldb.eSymbolContextEverything)
#								self.workerManager.start_loadSourceWorker(self.driver.debugger, ConfigClass.testTargetSource, self.handle_loadSourceFinished, context.GetLineEntry().GetLine())

	def resetGUI(self):
#		print(f"Resetting GUI")
		self.updateStatusBar(f"Resetting GUI ...")
		# self.txtMultiline.resetContent()
		self.txtMultiline.clearPC()
		self.tblFileInfos.resetContent()
		self.tabWidgetStruct.resetContent()
		self.treStats.clear()
#		self.tblReg.resetContent()
		for tbl in self.tblRegs:
			tbl.resetContent()
		self.tblRegs.clear()
		self.tabWidgetReg.clear()
		self.rflagsLoaded = 0
		self.tblVariables.resetContent()
		self.wdtBPsWPs.treBPs.clear()
		self.tabWatchpoints.tblWatchpoints.resetContent()
		self.tblHex.resetContent()
		self.txtSource.clear()
		self.treThreads.clear()
		self.treListener.treEventLog.clear()
		self.wdtDbg.cmdClear_clicked()
		self.wdtCommands.resetContent(False, True)

	inited = False
	def handle_processEvent(self, process):
		state = 'stopped'
		if process.state == eStateStepping or process.state == eStateRunning:
			state = 'running'
		elif process.state == eStateExited:
			logDbg(f"PROCESS EXITED!!!!!")
			self.setWinTitleWithState("Exited")
			self.resetGUI()
			state = 'exited'
			self.should_quit = True
			return
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
	def setResumeActionIcon(self, iconResume=True):
		if iconResume:
			iconToUse = ConfigClass.iconResume
		else:
			iconToUse = ConfigClass.iconPause
		self.load_resume.setIcon(iconToUse)
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
			self.setResumeActionIcon(False)
			self.isProcessRunning = True
		else:
			self.setResumeActionIcon()
			self.isProcessRunning = False

	rip = ""

	def handle_debugStepCompleted(self, kind, success, rip, frm):
		if success:
			self.rip = rip
			self.txtMultiline.setPC(int(str(self.rip), 16))
			self.wdtBPsWPs.treBPs.setPC(self.rip)
			self.start_loadRegisterWorker(False)
			self.wdtBPsWPs.reloadBreakpoints(False)
			# self.tabWatchpoints.reloadWatchpoints(False)
			self.loadStacktrace()

			context = frm.GetSymbolContext(lldb.eSymbolContextEverything)
			self.workerManager.start_loadSourceWorker(self.driver.debugger, ConfigClass.testTargetSource, self.handle_loadSourceFinished, context.GetLineEntry().GetLine())
			self.tblRegs[3].loadRFlags(self.driver.debugger)
#			self.setResumeActionIcon()
			self.setWinTitleWithState("Interrupted")
			self.setResumeActionIcon()
		else:
			# print(f"Debug STEP ({kind}) FAILED!!!")
			self.setResumeActionIcon()
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
		else:
			# print(f"idx == -1")
			daHex = ""
			daDataNg = ""
#		self.txtMultiline.appendAsmText(hex(int(str(instruction.GetAddress().GetLoadAddress(target)), 10)), instruction.GetMnemonic(target),  instruction.GetOperands(target), instruction.GetComment(target), str(instruction.GetData(target)).replace("                             ", "\t\t").replace("		            ", "\t\t\t").replace("		         ", "\t\t").replace("		      ", "\t\t").replace("			   ", "\t\t\t"), True)

		self.txtMultiline.appendAsmText(hex(int(str(instruction.GetAddress().GetLoadAddress(target)), 10)), instruction.GetMnemonic(target),  instruction.GetOperands(target), instruction.GetComment(target), daHex, "".join(str(daDataNg).split()), True)

		pass

	def handle_workerFinished(self):
#		print(f"Current RIP: {self.rip} / {hex(self.rip)} / DRIVER: {self.driver.getPC()} / {self.driver.getPC(True)}")
		QApplication.processEvents()
		self.txtMultiline.setPC(self.driver.getPC(), True)
		logDbg(f"self.driver.getPC(): {hex(self.driver.getPC())} / {self.driver.getPC()}")
		return
		self.start_loadRegisterWorker()
		self.setProgressValue(50)
		QApplication.processEvents()
#		self.reloadBreakpoints(True)
		self.wdtBPsWPs.treBPs.clear()
		self.wdtBPsWPs.reloadBreakpoints(True)
		# self.tabWatchpoints.reloadWatchpoints(True)
		self.loadStacktrace()
		self.setProgressValue(70)
		# QApplication.processEvents()
#		print(f'self.rip => {self.rip}')

		QApplication.processEvents()

		frame = self.driver.getTarget().GetProcess().GetThreadAtIndex(0).GetFrameAtIndex(0)
		context = frame.GetSymbolContext(lldb.eSymbolContextEverything)
		self.workerManager.start_loadSourceWorker(self.driver.debugger, ConfigClass.testTargetSource, self.handle_loadSourceFinished, context.GetLineEntry().GetLine())

		logDbg(f"Finished loading disassembly ... loading GUI-FlowControl")
		# self.wdtControlFlow.loadInstructions()
		self.wdtControlFlow.loadConnections()
		self.setProgressValue(90)
		QApplication.processEvents()
#		self.txtMulriline.locationStack.pushLocation(hex(self.driver.getPC()).lower())
#		print(f"self.txtMultiline.table.rowCount() => {self.txtMultiline.table.rowCount()}")

		addrObj2 = find_main(self.driver.debugger)
		# addrObj2Hex = f"{hex(addrObj2)}"

		if self.setHelper.getChecked(SettingsValues.LoadTestBPs):
			self.bpHelper.enableBP(f"0x100000a40", True, False)

		# setHelper = SettingsHelper()
		# logDbg(f"addrObj2: {hex(addrObj2)}")
		if self.setHelper.getChecked(SettingsValues.BreakpointAtMainFunc):
			self.bpHelper.enableBP(hex(addrObj2), True, False)
		self.txtMultiline.viewAddress(hex(addrObj2))
		self.setProgressValue(95)
		QApplication.processEvents()
		self.window().wdtControlFlow.view.verticalScrollBar().setValue(self.window().txtMultiline.table.verticalScrollBar().value())
		# self.window().txtMultiline.table.verticalScrollBar().setValue(scrollOrig)
		# self.finish_startup()

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
	rflagsLoaded = 0
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
		if self.rflagsLoaded == 2:
			self.rflagsLoaded = not self.rflagsLoaded
			self.handle_loadRFlags()
		self.rflagsLoaded += 1
#		pass

	def handle_loadRFlags(self):
		# tabDet2 = QWidget()
		# tabDet2.setContentsMargins(0, 0, 0, 0)
		tblReg2 = RFlagWidget(parent=None, driver=self.driver)
		# tabDet2.tblWdgt = tblReg2
		self.tblRegs.append(tblReg2.tblRFlag)
		# tabDet2.setLayout(QVBoxLayout())
		# tabDet2.layout().addWidget(tblReg2)
		# tabDet2.layout().setContentsMargins(0, 0, 0, 0)
		self.tabWidgetReg.addTab(tblReg2, "rFlags/eFlags")
		# tblReg2.loadRFlags(self.driver.debugger)

	# self.currTblDet = tblReg2
		# tabDet = QWidget()
		# tabDet.setContentsMargins(0, 0, 0, 0)
		# tblReg = RFlagTableWidget()
		# tabDet.tblWdgt = tblReg
		# self.tblRegs.append(tblReg)
		# tabDet.setLayout(QVBoxLayout())
		# tabDet.layout().addWidget(tblReg)
		# tabDet.layout().setContentsMargins(0, 0, 0, 0)
		# self.tabWidgetReg.addTab(tabDet, "rFlags/eFlags")
		# self.currTblDet = tblReg
		# # tblReg.

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
		# self.tblRememberLoc.addRow(name, value, valType, address, data, comment)
		pass

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
			logDbg(f"Sourcecode '{ConfigClass.testTargetSource}' for target '{ConfigClass.testTarget}' reloaded!")
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
				if line_number != 0xFFFFFFFF and line_number >= 0:
					self.txtSource.scroll_to_lineNG(line_number)
				self.tabWidgetDbg.setCurrentIndex(currTabIdx)
		else:
			self.txtSource.setText("<Source code NOT available>")

		logDbgC(f"Calling 'self.wdtControlFlow.loadConnections()' from 'handle_loadSourceFinished'")
		# self.wdtControlFlow.loadConnections()
		# self.worker.endLoadControlFlowCallback.emit(True)

	def runControlFlow_loadConnections(self):
		self.wdtControlFlow.loadConnections()
		self.worker.endLoadControlFlowCallback.emit(True)
		oepMain = find_main(self.driver.debugger)
		logDbgC(f"OEP: {hex(oepMain)} / {oepMain}")
		# logDbgC(f"Going to OEP: {oepMain} / {hex(oepMain)}")
		self.txtMultiline.viewAddress(hex(oepMain))
		logDbgC(f"self.txtMultiline.table.verticalScrollBar().value(): {self.txtMultiline.table.verticalScrollBar().value()} / self.wdtControlFlow.view.verticalScrollBar().value(): {self.wdtControlFlow.view.verticalScrollBar().value()}")
		self.wdtControlFlow.view.verticalScrollBar().setValue(self.txtMultiline.table.verticalScrollBar().value())
		QApplication.processEvents()
		# logDbgC(
		# 	f"=> self.txtMultiline.table.verticalScrollBar().value(): {self.txtMultiline.table.verticalScrollBar().value()} / self.wdtControlFlow.view.verticalScrollBar().value(): {self.wdtControlFlow.view.verticalScrollBar().value()}")
		# self.wdtControlFlow.view.verticalScrollBar().setValue(self.txtMultiline.table.verticalScrollBar().value())

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
				# logDbgC(f"frame.GetFunction(): {frame.GetFunction()}")
				frameNode = QTreeWidgetItem(self.threadNode, ["#" + str(frame.GetFrameID()), "", str(frame.GetPCAddress()), str(hex(frame.GetPC())), self.GuessLanguage(frame)])
				idx += 1

			self.processNode.setExpanded(True)
			self.threadNode.setExpanded(True)
#			self.devHelper.setDevWatchpoints()

	def GuessLanguage(self, frame):
		return lldb.SBLanguageRuntime.GetNameForLanguageType(frame.GuessLanguage())