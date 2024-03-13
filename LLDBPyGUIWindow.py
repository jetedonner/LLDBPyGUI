#!/usr/bin/env python3
import lldb
import os
import io
import contextlib

from threading import Thread

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
from ui.dialogs.spinnerDialog import *
from ui.dialogs.dialogHelper import *
from ui.assemblerTextEdit import *
from ui.variablesTableWidget import *
from ui.registerTableWidget import *
from ui.fileInfoTableWidget import *
from ui.statisticsTreeWidget import *
from ui.fileStructureTreeView import *
from ui.commandsWidget import *
from ui.breakpointWidget import *
from ui.watchpointWidget import *
from ui.threadFrameTreeView import *
from ui.sourceTextEdit import *
from ui.listenerTreeView import *
from ui.searchTableWidget import *
from ui.customQt.QHexTableWidget import *
from ui.customQt.QMemoryViewer import *


from worker.workerManager import *

from config import *

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
def wpcallback(frame, wp, dict):
	print(f"================>>>>>>>>>>>>> YES WATCHPOINT HIT <<<<<<<<<<<=================")
	wp.SetEnabled(True)
	print(frame)
	print(wp)
	res = lldb.SBCommandReturnObject()
	ci = frame.GetThread().GetProcess().GetTarget().GetDebugger().GetCommandInterpreter()
	ci.HandleCommand('command script import "/Volumes/Data/dev/_reversing/disassembler/LLDBPyGUI/LLDBPyGUI/LLDBPyGUIWindow.py"', res)
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
	
	def wpcallback(self, frame, wp, dict):
		print(f"================>>>>>>>>>>>>> YES WATCHPOINT HIT <<<<<<<<<<<=================")
		pass
		
	bpHelper = None
	
	def __init__(self, driver = None):
		super().__init__()
		
		self.driver = driver
		self.targetBasename = "NG"
		
		self.setHelper = SettingsHelper()
		self.workerManager = WorkerManager(self.driver)
		self.bpHelper = BreakpointHelperNG(self.driver)
		self.devHelper = DevHelper(self.driver)
		
		self.setWinTitleWithState("GUI Started")
		self.setBaseSize(WINDOW_SIZE * 2, WINDOW_SIZE)
		self.setMinimumSize(WINDOW_SIZE * 2, WINDOW_SIZE + 72)
		self.move(1200, 200)
		
		self.toolbar = QToolBar('Main ToolBar')
		self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)
		self.toolbar.setIconSize(QSize(ConfigClass.toolbarIconSize, ConfigClass.toolbarIconSize))
		
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
		
		self.help_action = QAction(ConfigClass.iconInfo, '&Show Help', self)
		self.help_action.setStatusTip('Show Help')
		self.help_action.setShortcut('Ctrl+H')
		self.help_action.triggered.connect(self.help_clicked)
		self.toolbar.addAction(self.help_action)
		
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
		
		self.layout = QVBoxLayout()
		
		self.txtMultiline = AssemblerTextEdit(self.driver, self.bpHelper)
#		self.txtMultiline.table.sigEnableBP.connect(self.handle_enableBP)
#		self.txtMultiline.table.sigBPOn.connect(self.handle_BPOn)
		
		self.txtMultiline.setContentsMargins(0, 0, 0, 0)
		
		self.splitter = QSplitter()
		self.splitter.setContentsMargins(0, 0, 0, 0)
		self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.splitter.setOrientation(Qt.Orientation.Vertical)
		
		self.splitter.addWidget(self.txtMultiline)
		
		self.tabWidgetDbg = QTabWidget()
#		self.tabWidgetDbg.setContentsMargins(0, 0, 0, 0)
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
		self.tabWidgetDbg.addTab(self.txtSource, "Source")
		
		self.treThreads = ThreadFrameTreeWidget()
		
		self.tabWidgetDbg.addTab(self.treThreads, "Threads/Frames")
		
		self.treListener = ListenerWidget(self.driver)
#		self.treListener.listener.signals.processEvent.connect(self.handle_processEvent)
		
		self.tabWidgetDbg.addTab(self.treListener, "Listeners")
		
		self.tabWidgetMain = QTabWidget()
		self.tabWidgetMain.setContentsMargins(0, 0, 0, 0)
		self.tabWidgetMain.addTab(self.splitter, "Debugger")
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
		self.tabWidgetMain.addTab(self.wdtSearch, "Search")
		
		self.wdtCommands = CommandsWidget(self.workerManager)
		self.tabWidgetMain.addTab(self.wdtCommands, "Commands")
		
		
		
		self.layout.addWidget(self.tabWidgetMain)
		
		self.centralWidget = QWidget(self)
		self.centralWidget.setLayout(self.layout)
		self.setCentralWidget(self.centralWidget)

		self.bpHelper.setCtrls(self.txtMultiline, self.wdtBPsWPs.treBPs)
	
		self.threadpool = QThreadPool()
		
		# ======== DEV CMDs ##########
		self.tabWidgetDbg.setCurrentIndex(2)

		self.updateStatusBar("LLDBPyGUI loaded successfully!")
		
	def cmbModules_changed(self, index):
		print(f"cmbModules_changed => {index}")
		self.loadFileStruct(index)
		
	def setWinTitleWithState(self, state):
		self.setWindowTitle(APP_NAME + " " + APP_VERSION + " - " + self.targetBasename + " - " + state)
		
	def handle_showMemoryFor(self):
		sender = self.sender()  # get the sender object
		if isinstance(sender, QAction):
			action = sender  # it's the QAction itself
		else:
			# Find the QAction within the sender (e.g., QMenu or QToolBar)
			action = sender.findChild(QAction)
			
		self.doReadMemory(self.quickToolTip.get_memory_address(self.driver.debugger, action.data()))
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
	
	def updateStatusBar(self, msg):
		self.statusBar.showMessage(msg)
		
	def load_clicked(self):
		filename = showOpenFileDialog()
		if filename != None and filename != "":
			print(f"Loading new target: '{filename}")
			self.loadNewExecutableFile(filename)
	
	def handle_tabWidgetMainCurrentChanged(self, idx):
		if idx == 2:
			self.wdtCommands.txtCmd.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
			print(f"self.wdtCommands.txtCmd.setFocus(Qt.FocusReason.ActiveWindowFocusReason)")
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
					print(proc)
					print(f"Process Idx: '{pd.cmbPID.currentIndex()}' / PID: '{proc.pid}' / Name: '{proc.name()}' selected")
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
				print(f"Detached from process returned with result: {error}")
				self.attach_action.setIcon(ConfigClass.iconGears)
				self.attach_action.setToolTip("Attach to process")
				self.isAttached = False
				
		
	def execCommand_clicked(self):
		pass
		
	def clear_clicked(self):
		pass
		
	def resume_clicked(self):
		if self.isProcessRunning:
			print(f"self.isProcessRunning => Trying to Suspend()")
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
			print(f"GOING BACK to {newLoc} ... {self.txtMultiline.locationStack.currentLocation}")
			self.txtMultiline.viewAddress(newLoc, False)
		self.forward.setEnabled(not self.txtMultiline.locationStack.currentIsLast())
		self.back.setEnabled(not self.txtMultiline.locationStack.currentIsFirst())
		
	def forward_clicked(self):
		newLoc = self.txtMultiline.locationStack.forwardLocation()
		if newLoc:
			print(f"GOING FORWARD to {newLoc} ... {self.txtMultiline.locationStack.currentLocation}")
			self.txtMultiline.viewAddress(newLoc, False)
		self.forward.setEnabled(not self.txtMultiline.locationStack.currentIsLast())
		self.back.setEnabled(not self.txtMultiline.locationStack.currentIsFirst())
	
	def settings_clicked(self):
		settingsWindow = SettingsDialog(self.setHelper)
		if settingsWindow.exec():
			print(f'Settings saved')
			self.tblHex.cmbGrouping.setCurrentIndex(self.setHelper.getValue(SettingsValues.HexGrouping))
		
	def help_clicked(self):
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
		self.tabWatchpoints.tblWatchpoints.resetContent()
		self.tabWatchpoints.reloadWatchpoints(True)
		pass
		
	def updateStatusBar(self, msg):
		self.statusBar.showMessage(msg)
		
	def setProgressValue(self, newValue):
		self.progressbar.setValue(int(newValue))
		
	def onQApplicationStarted(self):
		print('onQApplicationStarted started')
		
#		self.dialog = SpinnerDialog()
#		self.dialog.show()
		
		if self.setHelper.getValue(SettingsValues.LoadTestTarget):
			self.loadNewExecutableFile(ConfigClass.testTarget)
			
	def loadNewExecutableFile(self, filename):
#		self.resetGUI()
		self.targetBasename = os.path.basename(filename)
		if self.driver.getTarget().GetProcess(): #pymobiledevice3GUIWindow.process:
			print("KILLING PROCESS")
	
			self.driver.aborted = True
			print("Aborted sent")
			#					os._exit(1)
			#       sys.exit(0)
			#       pymobiledevice3GUIWindow.process.Kill()
			#       global driver
			#       driver.terminate()
			#       pymobiledevice3GUIWindow.driver.getTarget().GetProcess().Stop()
			#       print("Process stopped")        
			self.driver.getTarget().GetProcess().Kill()
			print("Process killed")
			self.resetGUI()
	
		global event_queue
		event_queue = queue.Queue()
#				
#				#				global driver
		self.inited = False
		self.driver = dbg.debuggerdriver.createDriver(self.driver.debugger, event_queue)
#			self.driver.aborted = False
			
#			self.driver.createTarget(filename)
		self.driver.signals.event_queued.connect(self.handle_event_queued)
		self.driver.start()
		self.driver.createTarget(filename)
		if self.driver.debugger.GetNumTargets() > 0:
			target = self.driver.getTarget()
			
			if self.setHelper.getValue(SettingsValues.BreakAtMainFunc):
				main_bp = self.bpHelper.addBPByName(self.setHelper.getValue(SettingsValues.MainFuncName))
				print(main_bp)

			launch_info = target.GetLaunchInfo()
			if self.setHelper.getValue(SettingsValues.StopAtEntry):
				launch_info.SetLaunchFlags(lldb.eLaunchFlagDisableASLR + lldb.eLaunchFlagStopAtEntry)# lldb.eLaunchFlagDisableASLR + 
			error = lldb.SBError()
			target.Launch(launch_info, error)
			output = io.StringIO()
			
#			target.Launch(self.driver.debugger.GetListener(), None, None, None, output.fileno(), None, None, 0, False, error)
##			'/tmp/stdout.txt'
			self.loadTarget()
			self.setWinTitleWithState("Target loaded")
			
			
		
		
	def handle_event_queued(self, event):
		print(f"EVENT-QUEUED: {event}")
		print(f'GUI-GOT-EVENT: {event} / {event.GetType()} ====>>> THATS DA ONE')
		desc = get_description(event)
		print('GUI-Event description:', desc)
		print('GUI-Event data flavor:', event.GetDataFlavor())
		if str(event.GetDataFlavor()) == "ProgressEventData":
			self.treListener.handle_gotNewEvent(event)
			pass
		
	def handle_breakpointEvent(self, event):
		print(f"handle_breakpointEvent: {event}")
		
	def loadTarget(self):
		
		if self.driver.debugger.GetNumTargets() > 0:
			target = self.driver.getTarget()
			print(f"loadTarget => {target}")
			if target:
				
				fileInfos = FileInfos()
				fileInfos.loadFileInfo(target, self.tblFileInfos)
				self.devHelper.bpHelper = self.bpHelper
				self.devHelper.setDevBreakpoints()
				self.devHelper.setDevWatchpointsNG()
				self.treStats.loadFileStats()
#					
				self.process = target.GetProcess()
				if self.process:
					self.listener = LLDBListener(self.process, self.driver.debugger)
					self.listener.breakpointEvent.connect(self.handle_breakpointEvent)
					self.listener.processEvent.connect(self.handle_processEvent)
					self.listener.gotEvent.connect(self.treListener.handle_gotNewEvent)
					self.listener.addListenerCalls()
					self.listener.start()
					
#					
#					idx = 0
					print(f"self.process.GetNumThreads() => {self.process.GetNumThreads()}")
					self.thread = self.process.GetThreadAtIndex(0)
#					print(self.thread)
#					print(self.thread.GetNumFrames())
					if self.thread:
#						
						print(f"self.thread.GetNumFrames() => {self.thread.GetNumFrames()}")
#						
						for z in range(self.thread.GetNumFrames()):
							frame = self.thread.GetFrameAtIndex(z)
							self.tabWidgetStruct.cmbModules.addItem(frame.GetModule().GetFileSpec().GetFilename())
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
								self.workerManager.start_loadSourceWorker(self.driver.debugger, ConfigClass.testTargetSource, self.handle_loadSourceFinished, context.GetLineEntry().GetLine())

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
		print('Process event: %s, reason: %d' % (state, thread.GetStopReason()))
		if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
#			for z in range(thread.GetNumFrames()):
			frame = thread.GetFrameAtIndex(0)
#				if frame.GetModule().GetFileSpec().GetFilename() != self.driver.getTarget().GetExecutable().GetFilename():
##					process.Continue()
#					continue
#				print(f"frame.GetModule() => {frame.GetModule().GetFileSpec().GetFilename()}")
#							frame = self.thread.GetFrameAtIndex(z)
			if frame:
				print(frame)
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
			print(f"Debug STEP ({kind}) FAILED!!!")
			self.setResumeActionIcon(ConfigClass.iconResume)
		self.isProcessRunning = False
		pass
		
	def start_loadDisassemblyWorker(self, initTable = True):
		self.symFuncName = ""
		self.workerManager.start_loadDisassemblyWorker(self.handle_loadInstruction, self.handle_workerFinished, initTable)

	def start_loadRegisterWorker(self, initTabs = True):
		self.workerManager.start_loadRegisterWorker(self.handle_loadRegister, self.handle_loadRegisterValue, self.handle_updateRegisterValue, self.handle_loadVariableValue, self.handle_updateVariableValue, self.handle_loadRegisterFinished, initTabs)
		
	def handle_loadInstruction(self, instruction):
		target = self.driver.getTarget()
		
		if self.symFuncName != instruction.GetAddress().GetFunction().GetName():
			self.symFuncName = instruction.GetAddress().GetFunction().GetName()
			
			self.txtMultiline.appendAsmSymbol(str(instruction.GetAddress().GetLoadAddress(target)), self.symFuncName)
			
#		print(f'instruction.GetComment(target) => {instruction.GetComment(target)}')
		self.txtMultiline.appendAsmText(hex(int(str(instruction.GetAddress().GetLoadAddress(target)), 10)), instruction.GetMnemonic(target),  instruction.GetOperands(target), instruction.GetComment(target), str(instruction.GetData(target)).replace("                             ", "\t\t").replace("		            ", "\t\t\t").replace("		         ", "\t\t").replace("		      ", "\t\t").replace("			   ", "\t\t\t"), True)
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
		self.updateStatusBar("handle_loadRegisterFinished")
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
		tblReg = RegisterTableWidget()
		tabDet.tblWdgt = tblReg
		self.tblRegs.append(tblReg)
		tabDet.setLayout(QVBoxLayout())
		tabDet.layout().addWidget(tblReg)
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
				line_text = "=>"
				self.txtSource.scroll_to_line(line_text)
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