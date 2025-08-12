#!/usr/bin/env python3
import lldb
import os
import io
import contextlib

from threading import Thread

import lib.utils
from ui.consoleWidget import ConsoleWidget
from ui.customQt.QControlFlowWidget import QControlFlowWidget
from ui.dialogs.createTargetDialog import CreateTargetDialog
from ui.dialogs.userActionNeededDialog import UserActionNeededDialog
from ui.hexToStringWidget import HexToStringWidget
from ui.rememberLocationsTableWidget import RememberLocationsTableWidget
from ui.rflagTableWidget import RFlagTableWidget, RFlagWidget
from ui.stopHookWidget import StopHookWidget
from worker.baseWorkerAttach import AttachWorker
from worker.decompileModuleWorker import DecompileModuleWorker

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

	isAttached = False
	isProcessRunning = False
	modulesAndInstructions = {}

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
		level_name = lldb.SBDebugger.GetLogMessageLevelName(log_level)
		logDbgC(f"=========================>>>>>>>>>>>>>>>>>>>> {level_name} ({log_level}) => {message} (my_custom_log_callback)")

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

	def stopWorkerAndQuitThreadAttach(self):
		# self.attachWorker.stop()
		# os.path.basename(self.attachWorker.process)
		self.addToFiles(self.get_main_module_filename(self.attachWorker.process))
		self.threadAttach.quit()
		self.finish_startup()
		self.isAttached = True

	def addToFiles(self, filename, selectItem=True):
		if self.cmbFiles.findText(filename) == -1:
			self.cmbFiles.addItem(filename)

		if selectItem:
			idxFile = self.cmbFiles.findText(filename)
			if idxFile != -1:
				self.cmbFiles.setCurrentIndex(idxFile)

	def get_main_module_filename(self, process):
		if not process.IsValid():
			print("❌ Invalid SBProcess.")
			return None

		target = process.GetTarget()
		if not target.IsValid():
			print("❌ Invalid SBTarget.")
			return None

		# The first module is usually the main executable
		main_module = target.GetModuleAtIndex(0)
		if not main_module.IsValid():
			print("❌ No valid module found.")
			return None

		filename = main_module.GetFileSpec().GetFilename()
		# full_path = main_module.GetFileSpec().GetPath()
		print(f"📦 Main module filename: {filename}")
		# print(f"📁 Full path: {full_path}")
		return filename

	def stopWorkerAndQuitThreadNG(self):
		# self.workerDecomp.stop()
		self.threadDecompMod.quit()
		self.finish_startup()

	debugger = None
	driver = None
	# targetBasename = ""

	def __init__(self, driver = None, debugger=None, loadExec2=False):
		super().__init__()

		# self.start_operation()
		self.debugger = debugger
		self.driver = driver

		self.symFuncName = ""

		self.threadLoad = QThread()
		self.threadAttach = QThread()

		if ConfigClass.startTestTarget:
			if not loadExec2:
				self.worker = Worker(self, ConfigClass.testTarget, True, ConfigClass.testTargetSource, ConfigClass.testTargetArch) #, ConfigClass.testTargetArgs)
			else:
				self.worker = Worker(self, ConfigClass.testTarget2, True, ConfigClass.testTargetSource2)

			self.worker.arch = ConfigClass.testTargetArch
			self.worker.args = ConfigClass.testTargetArgs

		else:
			self.worker = Worker(self)
			self.attachWorker = AttachWorker(self.debugger)
			self.attachWorker.loadModulesCallback.connect(self.loadModulesCallback)
			self.attachWorker.logDbg.connect(logDbg)
			self.attachWorker.logDbgC.connect(logDbgC)
			self.attachWorker.moveToThread(self.threadAttach)
			self.threadAttach.started.connect(self.attachWorker.run)
			self.attachWorker.show_dialog.connect(self.start_operation)

			self.attachWorker.loadInstructionCallback.connect(self.handle_loadInstruction)
			self.attachWorker.loadInstructionsCallback.connect(self.handle_loadInstructions)
			self.attachWorker.loadStringCallback.connect(self.handle_loadString)
			self.attachWorker.loadSymbolCallback.connect(self.handle_loadSymbol)
			self.attachWorker.loadCurrentPC.connect(self.handle_loadCurrentPC)
			self.attachWorker.finished.connect(self.stopWorkerAndQuitThreadAttach)

			# self.attachWorker.finished.connect(self.stopWorkerAndQuitThread)

		self.worker.logDbg.connect(logDbg)
		self.worker.logDbgC.connect(logDbgC)
		# self.worker.logDbgC.connect(logDbgC)
		# self.worker.loadFileInfosCallback.connect(self.loadFileInfosCallback)
		# self.worker.loadJSONCallback.connect(self.treStats.loadJSONCallback)

		self.worker.moveToThread(self.threadLoad)
		self.threadLoad.started.connect(self.worker.run)
		self.worker.show_dialog.connect(self.start_operation)
		self.worker.finished.connect(self.stopWorkerAndQuitThread)
		self.worker.progressUpdateCallback.connect(self.handle_progressUpdate)

		# self.threadLoad.start()

		# lib.utils.main_window = self  # inside MainWindow __init__


		# Set the custom logging callback
		self.driver.debugger.SetLoggingCallback(self.my_custom_log_callback)

		# self.targetBasename = "NG"

		# self.spinner_overlay = SpinnerOverlay(self)
		# self.spinner_overlay.show()

		# self.dialog = SpinnerDialog()
		# self.dialog.show()

		# QTimer.singleShot(3000, self.finish_startup)  # Simulate startup delay


		self.setHelper = SettingsHelper()
		self.workerManager = WorkerManager(self.driver)
		self.bpHelper = BreakpointHelperNG(self.driver)
		self.devHelper = DevHelper(self.driver, self.bpHelper)

		self.setWinTitleWithState("Started")
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
		self.load_resume.setStatusTip('Resume (Ctrl+O)')
		self.load_resume.setShortcut('Ctrl+O')
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
		self.settings_action.setShortcut('Ctrl+T')
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
		self.test_action.setShortcut('Ctrl+1')
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
		self.splitter.setStretchFactor(0, 70)
		self.splitter.setStretchFactor(1, 30)
		self.splitter.setSizes([500, 200])

		self.tabWidgetReg = QTabWidget()
		self.tabWidgetReg.setContentsMargins(0, 0, 0, 0)
		self.tabWidgetDbg.addTab(self.tabWidgetReg, "Registers")

		self.tblVariables = VariablesTableWidget(self.driver)
		self.tabWidgetDbg.addTab(self.tblVariables, "Variables")

		self.wdtBPsWPs = BPsWPsWidget(self.driver, self.workerManager, self.bpHelper)

		self.tabWidgetDbg.addTab(self.wdtBPsWPs, "Breakpoints")

		self.tabWatchpoints = WatchpointsWidget(self.driver, self.workerManager)

		self.tabWidgetDbg.addTab(self.tabWatchpoints, "Watchpoints")

		# self.wdtStopHook = StopHookWidget(self.workerManager)
		# self.tabWidgetDbg.addTab(self.wdtStopHook, "Stop-Hook")

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
		# self.main_layout = QVBoxLayout(self)
		# self.main_layout.setContentsMargins(10, 10, 10, 10)
		# self.main_layout.setSpacing(5)

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
		self.idxDbgTab = self.tabWidgetMain.addTab(self.splitter, "Debugger")
		# self.tabWidgetMain.setTabText(idxDbgTab, f"Debugger - <module>")
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

		# self.tabTools = QWidget()
		# self.tabTools.setLayout(QVBoxLayout())
		# # self.tabTools.layout().addWidget(self.tblHex)
		#
		# # self.tabWidgetMain.addTab(self.tabTools, "Tools")
		#
		# self.splitterTools = QSplitter()
		# self.splitterTools.setContentsMargins(0, 0, 0, 0)
		# self.splitterTools.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		# self.splitterTools.setOrientation(Qt.Orientation.Vertical)
		# self.txtHexToStringInput = QTextEdit("00 00 00")
		# self.txtHexToStringInput.textChanged.connect(self.handle_txtHexToStringChnaged)
		# self.splitterTools.addWidget(self.txtHexToStringInput)
		# self.txtAsciiStringOutput = QTextEdit("xyz ...")
		# # self.txtAsciiStringOutput.setPlaceholderText("Enter a hex value above t")
		# self.splitterTools.addWidget(self.txtAsciiStringOutput)
		# self.splitterTools.setStretchFactor(0, 60)
		# self.splitterTools.setStretchFactor(1, 40)
		# self.splitterDbgMain.addWidget(self.wdtDbg)
		# self.tabTools.layout().addWidget(self.splitterTools)
		self.wdtDbg = DbgOutputWidget()

		self.wdtHexToString = HexToStringWidget()
		self.tabWidgetTools = QTabWidget(self.tabWidgetMain)
		self.tabWidgetTools.addTab(self.wdtHexToString, "HEX <-> ASCII")
		self.tabWidgetMain.addTab(self.tabWidgetTools, "Tools")

		self.wdtSearch = SearchWidget(self.driver)
		# self.tabWidgetMain.addTab(self.wdtSearch, "Search")

		self.tabWidgetDbg.addTab(self.wdtSearch, "Search")

		self.wdtCommands = CommandsWidget(self.workerManager)
		self.tabWidgetConsoles.addTab(self.wdtCommands, "LLDB")
		self.tabWidgetConsoles.addTab(self.tabWidgetConsole, "Python")
		self.tabWidgetConsoles.addTab(self.output_text_edit, "System shell")

		self.tabWidgetMain.addTab(self.tabWidgetConsoles, "Consoles")

		self.splitterDbgMain = QSplitter()
		self.splitterDbgMain.setContentsMargins(0, 0, 0, 0)
		self.splitterDbgMain.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.splitterDbgMain.setOrientation(Qt.Orientation.Vertical)
		self.cmbFiles = QComboBox()
		self.cmbFiles.currentIndexChanged.connect(self.handle_modules_changed)
		self.splitterDbgMain.addWidget(self.cmbFiles)
		# self.cmbFiles.setVisible(False)
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
		self.worker.loadStringCallback.connect(self.handle_loadString)
		self.worker.loadSymbolCallback.connect(self.handle_loadSymbol)

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
		self.worker.loadStacktraceCallback.connect(self.handle_loadStacktrace)
		self.worker.runControlFlow_loadConnections.connect(self.runControlFlow_loadConnections)

		self.attachWorker.handle_breakpointEvent = self.handle_breakpointEvent
		self.attachWorker.handle_processEvent = self.handle_processEvent
		self.attachWorker.handle_gotNewEvent = self.treListener.handle_gotNewEvent
		self.attachWorker.loadJSONCallback.connect(self.treStats.loadJSONCallback)
		self.attachWorker.loadFileInfosCallback.connect(self.loadFileInfosCallback)
		self.attachWorker.loadRegisterCallback.connect(self.handle_loadRegister)
		self.attachWorker.loadRegisterValueCallback.connect(self.handle_loadRegisterValue)
		self.attachWorker.loadVariableValueCallback.connect(self.handle_loadVariableValue)

		# ======== DEV CMDs ##########
		self.tabWidgetDbg.setCurrentIndex(2)

		self.updateStatusBar(f"{APP_NAME} loaded successfully!")

		self._restore_size()

	def handle_modules_changed(self, idx):
		logDbgC(f"handle_modules_changed({idx})")
		if len(self.modulesAndInstructions.keys()) > 0 and self.modulesAndInstructions.keys().__contains__(self.cmbFiles.currentText()) and self.modulesAndInstructions[self.cmbFiles.currentText()] is not None:
			self.txtMultiline.resetContent()
			self.handle_loadInstruction(self.modulesAndInstructions[self.cmbFiles.currentText()])
			self.setDbgTabLbl(self.cmbFiles.currentText())


	def setDbgTabLbl(self, moduleName=""):
		self.tabWidgetMain.setTabText(self.idxDbgTab, f"Debugger{' - ' + moduleName if moduleName != '' else '' }")
		if moduleName != "":
			self.addToFiles(moduleName)

	def handle_loadStacktrace(self):
		self.loadStacktrace()

	def start_operation(self):
		self.symFuncName = ""
		self.dialog = SpinnerDialog()
		self.dialog.show()

	def perform_step(self):
		if self.progress.wasCanceled():
			self.timer.stop()
			print("Operation canceled.")

	def finish_startup(self):
		self.dialog.close()
		logDbg(f"finish_startup called ... trying to close progress dialog ...")
		self.wdtControlFlow.view.verticalScrollBar().setValue(int(self.txtMultiline.table.verticalScrollBar().value()))


	def closeEvent(self, event):
		if self.isAttached:
			dlg = ConfirmDialog("Attached to Process - QUIT?",
								f"{APP_NAME} is still attached to a process. If you quit now, the attached process will aborted as well. Do you really want to quit {APP_NAME} and target now?")
			if dlg.exec() and dlg.button_clicked == QDialogButtonBox.StandardButton.Ok:
				print(f"Quitting {APP_NAME} (attached) now YESSS ...")
				self.driver.setDone()
				# self.driver.terminate()
				event.accept()
			# self.driver.terminate()
			else:
				print(f"if dlg.exec() and dlg.button_clicked == QDialogButtonBox.StandardButton.Ok: ELSE ...")
				if dlg.button_clicked == QDialogButtonBox.StandardButton.Abort:
					print(f"if dlg.button_clicked == QDialogButtonBox.StandardButton.Abort: ...")
					self.detachFromTarget()
					event.accept()
				else:
					print(f"if dlg.button_clicked == QDialogButtonBox.StandardButton.Abort: ELSE ...")
					event.ignore()
		else:
			if self.setHelper.getValue(SettingsValues.ConfirmQuitApp):
				dlg = ConfirmDialog(f"Quit {APP_NAME}?", f"Do you really want to quit {APP_NAME} and discard all unsaved changes?")
				if dlg.exec() and dlg.button_clicked == QDialogButtonBox.StandardButton.Ok:
					print(f"Quitting {APP_NAME} now YESSS ...")
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
		logDbgC(f"{strOut}")
		QApplication.processEvents()


	def cmbModules_changed(self, index):
		# print(f"cmbModules_changed => {index}")
		self.loadFileStruct(index)

	def setWinTitleWithState(self, state):
		# " - " + APP_RELEASE_DATE +
		self.setWindowTitle(APP_NAME + " " + APP_VERSION + " - " + os.path.basename(self.worker.fileToLoad) + " - " + state)
		# QCoreApplication.processEvents()
		# QApplication.processEvents()

	def handle_showMemoryFor(self):
		sender = self.sender()  # get the sender object
		if isinstance(sender, QAction):
			action = sender  # it's the QAction itself
		else:
			action = sender.findChild(QAction)

		addr = self.quickToolTip.get_memory_address(self.driver.debugger, action.data())

		self.doReadMemory(addr)

	def doReadMemory(self, address, size = 0x100):
		self.tabWidgetMain.setCurrentWidget(self.tabMemory)
		self.tblHex.doReadMemory(address, size)

	def handle_progressUpdate(self, value, statusTxt):
		self.setProgressValue(value)
		self.updateStatusBar(statusTxt)
		QApplication.processEvents()
		# QCoreApplication.processEvents()

	def setProgressValue(self, newValue):
		self.progressbar.setValue(newValue)
		QCoreApplication.processEvents()

	def updateStatusBar(self, msg, autoTimeout = True, timeoutMs = -1):
		self.statusBar.showMessage(msg)
		if self.tmrResetStatusBar.isActive():
			self.tmrResetStatusBar.stop()

		if autoTimeout:
			if timeoutMs == -1:
				self.tmrResetStatusBar.setInterval(self.setHelper.getValue(SettingsValues.StatusBarMsgTimeout))
			else:
				self.tmrResetStatusBar.setInterval(timeoutMs)
			self.tmrResetStatusBar.start()


	def resetStatusBar(self):
		self.statusBar.showMessage("")

	def goep_clicked(self):
		logDbg(f"Goto OEP clickediclicked!")
		addrObj = get_oep(self.driver.debugger)
		addrObjHex = f"{hex(addrObj)}"
		print(f"OEP2 (load addr): ")
		logDbg(f"OEP2 (load addr): {addrObjHex}")
		self.txtMultiline.viewAddress(addrObjHex)

	def goep2_clicked(self):
		logDbg(f"Goto OEP 2 clickediclicked!")
		addrObj2, main_symbol = find_main(self.driver.debugger)
		addrObj2Hex = f"{hex(addrObj2)}"
		print(f"OEP2 (load addr): ")
		logDbg(f"OEP2 (load addr): {addrObj2Hex}")
		self.txtMultiline.viewAddress(addrObj2Hex)

	def goep3_clicked(self):
		logDbg(f"Goto OEP 3 clickediclicked!")
		self.txtMultiline.viewCurrentAddress()

	def restart_debug_session(self, debugger, old_target, new_app_path):
		process = old_target.GetProcess()
		if process.IsValid():
			process.Kill()
		debugger.DeleteTarget(old_target)

		new_target = debugger.CreateTarget(new_app_path)
		if new_target.IsValid():
			launch_info = lldb.SBLaunchInfo(None)
			process = new_target.Launch(launch_info, lldb.SBError())
			return new_target, process
		return None, None

	def load_clicked(self):
		ctd = CreateTargetDialog()
		res = ctd.exec()
		sSelectedTarget = ctd.txtTarget.text()
		if res and sSelectedTarget is not None and sSelectedTarget != "":
			self.instCnt = 0
			self.stubsLoading = False
			self.symFuncName = ""
			self.threadLoad = QThread()
			self.worker = Worker(self, sSelectedTarget, True)#, ConfigClass.testTargetSource)
			self.worker.fileToLoad = sSelectedTarget
			self.worker.loader = ctd.cmbLoader.currentText()
			self.worker.arch = ctd.cmbArch.currentText()
			self.worker.args = ctd.txtArgs.text()
			self.worker.loadSourceCode = ctd.loadSourceCode
			# logDbgC(f"*************>>>> load_clicked => 2.....")
			self.worker.moveToThread(self.threadLoad)

			self.threadLoad.started.connect(self.worker.run)
			self.worker.show_dialog.connect(self.start_operation)
			self.worker.finished.connect(self.stopWorkerAndQuitThread)
			self.worker.progressUpdateCallback.connect(self.handle_progressUpdate)
			# logDbgC(f"*************>>>> load_clicked => 3.....")
			# Setup CALLBACKS
			self.worker.loadFileInfosCallback.connect(self.loadFileInfosCallback)
			self.worker.loadJSONCallback.connect(self.treStats.loadJSONCallback)
			self.worker.loadModulesCallback.connect(self.loadModulesCallback)
			self.worker.enableBPCallback.connect(self.enableBPCallback)
			self.worker.loadInstructionCallback.connect(self.handle_loadInstruction)
			self.worker.loadStringCallback.connect(self.handle_loadString)
			self.worker.loadSymbolCallback.connect(self.handle_loadSymbol)

			self.worker.finishedLoadInstructionsCallback.connect(self.handle_workerFinished)
			self.worker.handle_breakpointEvent = self.handle_breakpointEvent
			self.worker.handle_processEvent = self.handle_processEvent
			self.worker.handle_gotNewEvent = self.treListener.handle_gotNewEvent
			self.worker.loadRegisterCallback.connect(self.handle_loadRegister)
			self.worker.loadRegisterValueCallback.connect(self.handle_loadRegisterValue)
			self.worker.loadVariableValueCallback.connect(self.handle_loadVariableValue)
			# logDbgC(f"*************>>>> load_clicked => 4.....")
			self.worker.loadBreakpointsValueCallback.connect(self.wdtBPsWPs.handle_loadBreakpointValue)
			self.worker.updateBreakpointsValueCallback.connect(self.wdtBPsWPs.handle_updateBreakpointValue)
			self.worker.loadWatchpointsValueCallback.connect(
				self.tabWatchpoints.tblWatchpoints.handle_loadWatchpointValue)
			self.worker.updateWatchpointsValueCallback.connect(
				self.tabWatchpoints.tblWatchpoints.handle_updateWatchpointValue)
			self.worker.finishedLoadingSourceCodeCallback.connect(self.handle_loadSourceFinished)
			self.worker.loadStacktraceCallback.connect(self.handle_loadStacktrace)
			self.worker.runControlFlow_loadConnections.connect(self.runControlFlow_loadConnections)
			# logDbgC(f"*************>>>> load_clicked => 5.....")
			self.txtMultiline.resetContent()
			self.bpHelper.deleteAllBPs()
			self.wdtBPsWPs.treBPs.clear()
			self.tabWatchpoints.tblWatchpoints.resetContent()
			self.wdtControlFlow.resetContent()
			self.setResumeActionIcon(True)
			self.tabWidgetReg.clear()
			self.rflagsLoaded = 0
			# logDbgC(f"*************>>>> load_clicked => 6.....")
			self.should_quit = False
			# logDbgC(f"*************>>>> load_clicked => 7.....")
			# global driver
			# driver = dbg.debuggerdriver.createDriver(self.driver.debugger, event_queue)
			# self.driver = driver
			# self.driver.setDone(False)
			# self.txtMultiline.table.bpHelper.driver = self.driver
			# logDbgC(f"*************>>>> load_clicked => 8.....")
			# self.driver.start()
			# logDbgC(f"*************>>>> load_clicked => 9.....")
			self.threadLoad.start()
			# logDbgC(f"*************>>>> load_clicked => 10.....")

	def handle_tabWidgetMainCurrentChanged(self, idx):
		if idx == 2:
			self.wdtCommands.txtCmd.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
			# print(f"self.wdtCommands.txtCmd.setFocus(Qt.FocusReason.ActiveWindowFocusReason)")
#		elif idx == 3:
#			self.tblHex.cmbGrouping.setCurrentIndex(self.setHelper.getValue(SettingsValues.HexGrouping))
#			pass
		pass


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
					self.attachWorker.startWithPID(int(proc.pid), self.threadAttach)
					self.attach_action.setIcon(ConfigClass.iconGearsGrey)
					self.attach_action.setToolTip("Detach from process: {proc.pid} ({proc.name()})")
					self.setHelper.setValue(SettingsValues.TestAttachPID, int(proc.pid))
					self.isAttached = True
				except Exception as e:
					sError = f"Error while attaching to process: {e}"
					self.updateStatusBar(sError)
					print(sError)
		else:
			self.detachFromTarget()
			# error = self.driver.getTarget().GetProcess().Detach()
			# if error.Success():
			# 	self.resetGUI()
			# 	self.attach_action.setIcon(ConfigClass.iconGears)
			# 	self.attach_action.setToolTip("Attach to process")
			# 	self.isAttached = False


	def detachFromTarget(self):
		error = self.driver.getTarget().GetProcess().Detach()
		if error.Success():
			self.resetGUI()
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
				print(f"self.worker.listener.should_quit = True (1)")
				self.worker.listener.should_quit = True
				errKill = process.Kill()
				if not errKill.Success():
					logDbgC(f'Error killing process: {errKill}')
				else:
					# lldb.debugger.Terminate()
					logDbgC(f"Debugged app killed, cleaning up ...")
					# self.driver.debugger.DeleteTarget(target)
					# self.driver.debugger.Terminate()
					# lldb.SBDebugger.Destroy(self.driver.debugger)
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
		logDbgC(f"resume_clicked() => self.isProcessRunning: {self.isProcessRunning}")
		if self.isProcessRunning:
			self.isProcessRunning = False
			print(f"self.isProcessRunning => Trying to Suspend()")
			self.debugger.HandleCommand("process interrupt")
			self.debugger.HandleCommand("dis")
		else:
			self.driver.debugger.SetAsync(True)
			self.start_debugWorker(self.driver, StepKind.Continue)

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
			self.tblHex.cmbGrouping.setCurrentIndex(self.setHelper.getValue(SettingsValues.HexGrouping))
			self.tmrResetStatusBar.setInterval(int(self.setHelper.getValue(SettingsValues.StatusBarMsgTimeout)))

	def help_clicked(self):
		pass

	def credits_clicked(self):
		if not self.isAttached:
			pd = CreditsDialog(f"{APP_NAME} - Credits", "This are the Credits with the resources used for the realisation of LLDBPyGUI")
			pd.exec()

	def test2_clicked(self):
		os.system('clear')  # Unix/Linux/macOS
		statusTxt = "Console cleared"
		if self.setHelper.getValue(SettingsValues.ClearConsoleComplete):
			os.system('clear')  # Unix/Linux/macOS
			statusTxt += " (completely)"

		self.updateStatusBar(statusTxt)

		self.wdtBPsWPs.treBPs.show_notification("REST Notification => From Action (side actionbar)")


	def test_clicked(self):
		# self.wdtControlFlow.logViewportHeight()
		# self.wdtControlFlow.loadConnections()
		# logDbgC(f"self.wdtControlFlow.scene.sceneRect(): {self.wdtControlFlow.scene.sceneRect()}")
		self.usrAct = UserActionNeededDialog()
		self.usrAct.show()

		# $.ajax({
		# 	type: "POST",
		# 	url: url,
		# 	data: data,
		# 	success: success,
		# 	dataType: dataType
		# });
		pass

	def stopTarget(self):
		# self.driver
		process  = self.driver.getTarget().GetProcess()
		if process:
			self.driver.setDone()
			if hasattr(self, "listener"):
				print(f"self.worker.listener.should_quit = True (2)")
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

	def setProgressValue(self, newValue):
		self.progressbar.setValue(int(newValue))

	def onQApplicationStarted(self):
		if self.setHelper.getValue(SettingsValues.LoadTestTarget) and ConfigClass.startTestTarget:
			self.threadLoad.start()

	def loadNewExecutableFile(self, filename):
		return

		global event_queue
		event_queue = queue.Queue()
#
#				#				global driver
		self.inited = False
		self.worker.listener.should_quit = False
		self.stubsLoading = False
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
				addrObj2, main_symbol = find_main(self.driver.debugger)
				main_bp2 = self.bpHelper.enableBP(hex(addrObj2), True, False)
				# print(f"main_bp2 (@{addrObj2}): {main_bp2}")
				logDbgC(f"main_bp2 (@{addrObj2}): {main_bp2}")
				target.GetProcess().Continue()

			self.loadTarget()
			self.setWinTitleWithState("Target loaded")

	def handle_event_queued(self, event):
		print(f"EVENT-QUEUED: {event}")
		print(f'GUI-GOT-EVENT: {event} / {event.GetType()} ====>>> THATS DA ONE')
		desc = get_description(event)
		print('GUI-Event description:', desc)
		print('GUI-Event data flavor:', event.GetDataFlavor())
		if str(event.GetDataFlavor()) == "ProgressEventData": # and not self.should_quit:
			self.treListener.handle_gotNewEvent(event)
			pass

	def handle_breakpointEvent(self, event):
		print(f"handle_breakpointEvent: {event}")
		self.isProcessRunning = False
		pass

	#################################### START NEW CALLBACKS ########################################

	def enableBPCallback(self, address, enabled=True, updateUI=True):
		logDbgC(f"enableBPCallback...")
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
		self.tblFileInfos.resetContent()
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
		QApplication.processEvents()
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
								logDbgC(f"Module for FileStruct IS NOT equal executable => continuing ...")
								continue
							else:
								logDbgC(f"Module for FileStruct IS equal executable => scanning ...")
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
		self.updateStatusBar(f"Resetting GUI ...")
		self.txtMultiline.clearPC()
		self.tblFileInfos.resetContent()
		self.tabWidgetStruct.resetContent()
		self.treStats.clear()
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
		# logDbgC(f"handle_processEvent ...")
		state = 'stopped'
		if process.state == lldb.eStateStepping or process.state == lldb.eStateRunning:
			state = 'running'
		elif process.state == lldb.eStateExited:
			logDbg(f"PROCESS EXITED!!!!!")
			self.setWinTitleWithState("Exited")
			self.resetGUI()
			state = 'exited'
			print(f"self.worker.listener.should_quit = True (3)")
			self.should_quit = True
			self.worker.listener.should_quit = True
			return
		elif process.state == lldb.eStateStopped:
			thread = process.selected_thread

			# print('Process event: %s, reason: %d' % (state, thread.GetStopReason()))
			if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
				# logDbgC(f"handle_processEvent ...")
				self.isProcessRunning = False
				frame = thread.GetFrameAtIndex(0)
				if frame:
					# logDbgC(
					# 	f"====>>>> Module: {frame.GetModule().GetFileSpec().GetFilename()}")
					if not self.inited:
						return
					if thread.GetFrameAtIndex(0).register["rip"] is not None:
						self.handle_debugStepCompleted(StepKind.Continue, True, thread.GetFrameAtIndex(0).register["rip"].value, frame)
					else:
						self.handle_debugStepCompleted(StepKind.Continue, True, "", frame)

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
		nFoundRef = 0
		for module in self.target.module_iter():
			# print(f"In module: {idxOuter}")
			if idxOuter != 0:
				idxOuter += 1
				continue
			idx = 0
			for section in module.section_iter():
				if section.GetName() == "__TEXT":
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
		pass


	def start_debugWorker(self, driver, kind):
		# logDbgC(f"start_debugWorker (TESET) self.isProcessRunning: {self.isProcessRunning } .....")
		self.isProcessRunning = True
		self.wdtBPsWPs.treBPs.clearPC()
		self.txtMultiline.clearPC()
		# logDbgC(f"start_debugWorker (TESET 2) self.isProcessRunning: {self.isProcessRunning} .....")
		if True:
			driver.target = self.attachWorker.target
		if self.workerManager.start_debugWorker(driver, kind, self.handle_debugStepCompleted):
			# logDbgC(f"start_debugWorker (TESET 3) self.isProcessRunning: {self.isProcessRunning} .....")
			self.setWinTitleWithState("Running")
			self.setResumeActionIcon(False)
		else:
			self.setResumeActionIcon()
			self.isProcessRunning = False
		# logDbgC(f"start_debugWorker (TESET 4) self.isProcessRunning: {self.isProcessRunning} .....")
	rip = ""


	def handle_debugStepCompleted(self, kind, success, rip, frm):
		logDbgC(f"handle_debugStepCompleted => success: {success}, rip: {rip} ....")
		self.isProcessRunning = False
		# logDbgC(f"handle_debugStepCompleted({kind}, {success}, {rip}, {frm}) ====>>>> Module: {frm.GetModule().GetFileSpec().GetFilename()}")
		if success:
			self.rip = rip
			if self.rip != "":
				self.txtMultiline.setPC(int(str(self.rip), 16))
				self.wdtBPsWPs.treBPs.setPC(self.rip)
			self.start_loadRegisterWorker(False)
			self.wdtBPsWPs.reloadBreakpoints(False)
			# self.tabWatchpoints.reloadWatchpoints(False)
			self.loadStacktrace()

			context = frm.GetSymbolContext(lldb.eSymbolContextEverything)
			self.workerManager.start_loadSourceWorker(self.driver.debugger, self.worker.sourceFile, self.handle_loadSourceFinished, context.GetLineEntry().GetLine())
			if len(self.tblRegs) > 0:
				self.tblRegs[0].loadRFlags(self.driver.debugger)
#			self.setResumeActionIcon()
			self.setWinTitleWithState("Interrupted")
			self.setResumeActionIcon()
			self.isProcessRunning = False
		else:
			# print(f"Debug STEP ({kind}) FAILED!!!")
			self.setResumeActionIcon()
		self.isProcessRunning = False
		pass

	threadDecompMod = None

	def start_loadDisassemblyWorkerNG(self, modulePath, initTable = True):
		self.instCnt = 1
		# self.start_operation()
		# self.symFuncName = ""
		# import pdb; pdb.set_trace()
		# print(f'start_loadDisassemblyWorker')
		# logDbgC(f"start_loadDisassemblyWorkerNG({modulePath}, {initTable})")
		if initTable:
			self.txtMultiline.resetContent()
			self.wdtControlFlow.resetContent()
		# self.workerManager.start_loadDisassemblyWorkerNG(self.start_operation, self.handle_loadSymbol, self.handle_loadInstruction, self.handle_workerFinished, modulePath, initTable)

		self.threadDecompMod = QThread()
		# self.targetBasename = sSelectedTarget
		self.workerDecomp = DecompileModuleWorker(self.driver, modulePath, initTable)  # , ConfigClass.testTargetSource)
		# self.workerDecomp.fileToLoad = sSelectedTarget
		# self.workerDecomp.loader = ctd.cmbLoader.currentText()
		# self.workerDecomp.arch = ctd.cmbArch.currentText()
		# self.workerDecomp.args = ctd.txtArgs.text()
		# self.workerDecomp.loadSourceCode = ctd.loadSourceCode
		# logDbgC(f"*************>>>> load_clicked => 2.....")
		self.workerDecomp.moveToThread(self.threadDecompMod)

		self.threadDecompMod.started.connect(self.workerDecomp.run)
		self.workerDecomp.show_dialog.connect(self.start_operation)
		self.workerDecomp.loadSymbolCallback.connect(self.handle_loadSymbol)
		self.workerDecomp.loadInstructionCallback.connect(self.handle_loadInstructionNG)
		self.workerDecomp.finishedLoadInstructionsCallback.connect(self.handle_workerFinishedNG)
		self.workerDecomp.logDbg.connect(logDbg)
		self.workerDecomp.logDbgC.connect(logDbgC)
		# self.worker.progressUpdateCallback.connect(self.handle_progressUpdate)
		self.threadDecompMod.start()

	def start_loadDisassemblyWorker(self, initTable = True):
		self.symFuncName = ""
		# import pdb; pdb.set_trace()
		# print(f'start_loadDisassemblyWorker')
		self.workerManager.start_loadDisassemblyWorker(self.handle_loadInstruction, self.handle_workerFinished, initTable)

	def start_loadRegisterWorker(self, initTabs = True):
		self.workerManager.start_loadRegisterWorker(self.handle_loadRegister, self.handle_loadRegisterValue, self.handle_updateRegisterValue, self.handle_loadVariableValue, self.handle_updateVariableValue, self.handle_loadRegisterFinished, initTabs)

	def handle_loadSymbol(self, symbol):
		self.txtMultiline.appendAsmSymbol(0x0, str(symbol))
		# QApplication.processEvents()

	def handle_loadString(self, addr, idx, string):
		self.txtMultiline.appendString(addr, idx, string)
		# QApplication.processEvents()
		pass

	def handle_loadCurrentPC(self, pc):
		self.txtMultiline.setPC(pc, True)
		pass

	def handle_loadInstructions(self, instructions):
		self.txtMultiline.resetContent()
		# if sym in instructions:
		# 	self.txtMultiline.appendAsmSymbol(0x0, sym)

		for key, value in instructions:
			print(f"🔑 Key: {key}, 📦 Value: {value}")
			# self.txtMultiline.appendAsmSymbol(0x0, key)
			# for inst in value:
			# 	self.handle_loadInstruction(inst)

	instCnt = 0
	stubsLoading = False
	def handle_loadInstruction(self, instruction):
		self.instCnt += 1
		target = self.driver.getTarget()
		# print(instruction)
		# logDbgC(f"handle_loadInstruction({instruction}) ... => {self.symFuncName} / {instruction.GetAddress().GetFunction().GetName()}")
		stubsFunctName = None
		if self.symFuncName != instruction.GetAddress().GetFunction().GetName():
			self.symFuncName = instruction.GetAddress().GetFunction().GetName()

			if self.symFuncName is None and not self.stubsLoading:
				# Assuming you have an SBInstruction object called 'instruction'
				address = instruction.GetAddress()
				symbol = address.GetSymbol()
				# logDbgC(f"==========>>>>>>> symbol: {symbol}")
				# self.symFuncName = symbol.name
				stubsFunctName = symbol.name
				self.symFuncName = "__stubs"
				# if not self.stubsLoading:
				self.stubsLoading = True
				self.txtMultiline.appendAsmSymbol(str(instruction.GetAddress().GetLoadAddress(target)), self.symFuncName)
			else:
				if not self.stubsLoading:
					self.txtMultiline.appendAsmSymbol(str(instruction.GetAddress().GetLoadAddress(target)),
												  self.symFuncName)
					self.instCnt += 1
				# else:
				# 	address = instruction.GetAddress()
				# 	stubsFunctName = address.GetSymbol().name

		if self.symFuncName is None and self.stubsLoading:
			# self.txtMultiline.appendAsmSymbol(str(instruction.GetAddress().GetLoadAddress(target)), self.symFuncName)
			address = instruction.GetAddress()
			stubsFunctName = address.GetSymbol().name

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
		# logDbgC(f"!!!!!!!!!!!!!!!!¨ALREADY HERE !!!!!!!!!!!!!!!!!!")
		comment = stubsFunctName or instruction.GetComment(target)
		self.txtMultiline.appendAsmText(hex(int(str(instruction.GetAddress().GetLoadAddress(target)), 10)), instruction.GetMnemonic(target),  instruction.GetOperands(target), comment, daHex, "".join(str(daDataNg).split()), True, "", self.instCnt - 1)
		# QApplication.processEvents()
		# pass
		# QApplication.processEvents()

	def handle_loadInstructionNG(self, instruction):
		self.instCnt += 1
		target = self.driver.getTarget()
		# # print(instruction)
		# # logDbgC(f"handle_loadInstruction({instruction}) ... => {self.symFuncName} / {instruction.GetAddress().GetFunction().GetName()}")
		# stubsFunctName = None
		# if self.symFuncName != instruction.GetAddress().GetFunction().GetName():
		# 	self.symFuncName = instruction.GetAddress().GetFunction().GetName()
		#
		# 	if self.symFuncName is None and not self.stubsLoading:
		# 		# Assuming you have an SBInstruction object called 'instruction'
		# 		address = instruction.GetAddress()
		# 		symbol = address.GetSymbol()
		# 		# logDbgC(f"==========>>>>>>> symbol: {symbol}")
		# 		# self.symFuncName = symbol.name
		# 		stubsFunctName = symbol.name
		# 		self.symFuncName = "__stubs"
		# 		# if not self.stubsLoading:
		# 		self.stubsLoading = True
		# 		self.txtMultiline.appendAsmSymbol(str(instruction.GetAddress().GetLoadAddress(target)),
		# 										  self.symFuncName)
		# 	else:
		# 		if not self.stubsLoading:
		# 			self.txtMultiline.appendAsmSymbol(str(instruction.GetAddress().GetLoadAddress(target)),
		# 											  self.symFuncName)
		# 			self.instCnt += 1
		# # else:
		# # 	address = instruction.GetAddress()
		# # 	stubsFunctName = address.GetSymbol().name
		#
		# if self.symFuncName is None and self.stubsLoading:
		# 	# self.txtMultiline.appendAsmSymbol(str(instruction.GetAddress().GetLoadAddress(target)), self.symFuncName)
		# 	address = instruction.GetAddress()
		# 	stubsFunctName = address.GetSymbol().name
		#
		# #		print(f'instruction.GetComment(target) => {instruction.GetComment(target)}')

		daData = str(instruction.GetData(target))
		idx = daData.find("                             ")
		if idx == -1:
			idx = daData.find("		            ")
			if idx == -1:
				idx = daData.find("		         ")
				if idx == -1:
					idx = daData.find("		      ")
		if idx != -1:
			daHex = daData[:idx]
			daDataNg = daData[idx:]
		else:
			daHex = ""
			daDataNg = ""
		comment = instruction.GetComment(target)
		self.txtMultiline.appendAsmText(hex(int(str(instruction.GetAddress().GetLoadAddress(target)), 10)),
										instruction.GetMnemonic(target), instruction.GetOperands(target), comment,
										daHex, "".join(str(daDataNg).split()), True, "", self.instCnt - 1)

	def handle_workerFinished(self, connections = [], moduleName="<no name>", instructions={}):
		self.modulesAndInstructions = instructions
		QApplication.processEvents()
		self.txtMultiline.setPC(self.driver.getPC(), True)
		# if(len(connections) > 0):
		if connections != [] and (len(connections) > 0):
			self.wdtControlFlow.draw_instructions()
			self.wdtControlFlow.loadConnectionsFromWorker(connections)
		self.setDbgTabLbl(f"{moduleName}")
		self.dialog.close()

	def handle_workerFinishedNG(self, connections = [], moduleName="<no name>", instructions={}):
		self.modulesAndInstructions = instructions
		QApplication.processEvents()
		self.threadDecompMod.quit()

		self.txtMultiline.setPC(self.driver.getPC(), True)
		if connections != [] and (len(connections) > 0):
			self.wdtControlFlow.draw_instructions()
			self.wdtControlFlow.loadConnectionsFromWorker(connections)
		self.setDbgTabLbl(f"{moduleName}")
		self.dialog.close()

		return
		self.start_loadRegisterWorker()
		self.setProgressValue(50)
		QApplication.processEvents()
		self.wdtBPsWPs.treBPs.clear()
		self.wdtBPsWPs.reloadBreakpoints(True)
		self.loadStacktrace()
		self.setProgressValue(70)
		QApplication.processEvents()

		frame = self.driver.getTarget().GetProcess().GetThreadAtIndex(0).GetFrameAtIndex(0)
		context = frame.GetSymbolContext(lldb.eSymbolContextEverything)
		self.workerManager.start_loadSourceWorker(self.driver.debugger, ConfigClass.testTargetSource, self.handle_loadSourceFinished, context.GetLineEntry().GetLine())

		logDbg(f"Finished loading disassembly ... loading GUI-FlowControl")
		self.wdtControlFlow.loadConnections()
		self.setProgressValue(90)
		QApplication.processEvents()

		addrObj2, main_symbol = find_main(self.driver.debugger)

		if self.setHelper.getChecked(SettingsValues.LoadTestBPs):
			self.bpHelper.enableBP(f"0x100000a40", True, False)

		if self.setHelper.getChecked(SettingsValues.BreakpointAtMainFunc):
			self.bpHelper.enableBP(hex(addrObj2), True, False)
		self.txtMultiline.viewAddress(hex(addrObj2))
		self.setProgressValue(95)
		QApplication.processEvents()
		self.window().wdtControlFlow.view.verticalScrollBar().setValue(self.window().txtMultiline.table.verticalScrollBar().value())

	def handle_loadRegisterFinished(self):
		self.setProgressValue(100)

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
		QApplication.processEvents()

	def handle_loadRFlags(self):
		tblReg2 = RFlagWidget(parent=None, driver=self.driver)
		self.tblRegs.insert(0, tblReg2.tblRFlag)
		self.tabWidgetReg.insertTab(0, tblReg2, "rFlags/eFlags")

	def handle_loadRegisterValue(self, idx, type, register, value):
		self.currTblDet.addRow(type, register, value)
		QApplication.processEvents()

	def handle_updateRegisterValue(self, idx, type, register, value):
		tblWdgt = self.tabWidgetReg.widget(idx).tblWdgt
		for i in range(tblWdgt.rowCount()):
			if tblWdgt.item(i, 0).text() == type:
				tblWdgt.item(i, 1).setText(register)
				tblWdgt.item(i, 2).setText(value)
				break

	def handle_loadRememberLocation(self, name, value, data, valType, address, comment):
		pass

	def handle_loadVariableValue(self, name, value, data, valType, address):
		self.inited = True
		self.tblVariables.addRow(name, value, valType, address, data)
		QApplication.processEvents()

	def handle_updateVariableValue(self, name, value, data, valType, address):
		if self.isAttached:
			self.tblVariables.updateOrAddRow(name, value, valType, address, data)
		else:
			self.tblVariables.updateRow(name, value, valType, address, data)

	def handle_loadSourceFinished(self, sourceCode, autoScroll = True):
		if sourceCode != "":
			horizontal_value = self.txtSource.horizontalScrollBar().value()
			vertical_value = 0
			if not autoScroll:
				vertical_value = self.txtSource.verticalScrollBar().value()

			self.txtSource.setEscapedText(sourceCode)
			logDbgC(f"Sourcecode '{self.worker.sourceFile}' for target '{self.worker.fileToLoad}' reloaded!")
			currTabIdx = self.tabWidgetDbg.currentIndex()
			self.tabWidgetDbg.setCurrentWidget(self.txtSource)
			self.txtSource.horizontalScrollBar().setValue(horizontal_value)
			if not autoScroll:
				self.txtSource.verticalScrollBar().setValue(vertical_value)
			else:
				frame = self.driver.getTarget().GetProcess().GetThreadAtIndex(0).GetFrameAtIndex(0)
				line_number = frame.GetLineEntry().GetLine()
				if line_number != 0xFFFFFFFF and line_number >= 0:
					self.txtSource.scroll_to_lineNG(line_number)
				self.tabWidgetDbg.setCurrentIndex(currTabIdx)
		else:
			self.txtSource.setText("")

	def runControlFlow_loadConnections(self):
		self.worker.endLoadControlFlowCallback.emit(True)
		oepMain, symbol = find_main(self.driver.debugger)
		self.txtMultiline.viewAddress(hex(oepMain))
		self.wdtControlFlow.view.verticalScrollBar().setValue(self.txtMultiline.table.verticalScrollBar().value())
		QApplication.processEvents()

	def loadStacktrace(self):
		self.process = self.driver.getTarget().GetProcess()
		self.thread = self.process.GetThreadAtIndex(0)

		idx = 0
		if self.thread:
			self.treThreads.clear()
			self.processNode = QTreeWidgetItem(self.treThreads, ["#0 " + str(self.process.GetProcessID()), hex(self.process.GetProcessID()) + "", self.process.GetTarget().GetExecutable().GetFilename(), '', ''])
			self.threadNode = QTreeWidgetItem(self.processNode, ["#" + str(idx) + " " + str(self.thread.GetThreadID()), hex(self.thread.GetThreadID()) + "", self.thread.GetQueueName(), '', ''])
			numFrames = self.thread.GetNumFrames()

			for idx2 in range(numFrames):
				self.setProgressValue(idx2 / numFrames)
				frame = self.thread.GetFrameAtIndex(idx2)
				frameNode = QTreeWidgetItem(self.threadNode, ["#" + str(frame.GetFrameID()), "", str(frame.GetPCAddress()), str(hex(frame.GetPC())), GuessLanguage(frame)])
				idx += 1

			self.processNode.setExpanded(True)
			self.threadNode.setExpanded(True)
		QApplication.processEvents()