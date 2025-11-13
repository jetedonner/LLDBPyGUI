import json
import queue

import lldb
from PyQt6.QtCore import Qt, QThreadPool, QSettings
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QSplitter, QSizePolicy, QTabWidget, QWidget, QDialogButtonBox, QDockWidget
from lldb import *

from lldb import SBProcess, SBBreakpoint, SBWatchpoint

from PexpectConsole import PexpectConsole
from helper.debugHelper import *
from helper.devHelper import DevHelper
from helper.stylesheetHelper import StylesheetHelper
from helper.variableHelper import ensure_suffix
from helper.watchpointHelper import WatchpointHelper, WatchpointAccessMod
from lib.debugDriver import DebugDriver
from lib.fileInfos import FileInfos, get_description, is_hex_string
from lib.thirdParty.breakpointManager import BreakpointManager
from ui.base.customDockViewTitleBar import CustomDockViewTitleBar
from ui.consoles.commandsWidget import CommandsWidget
from ui.consoles.consoleTextEdit import ConsoleWidget
from ui.consoles.consoleWidget import PyQtConsoleWidget
from ui.customQt.QMemoryViewer import QMemoryViewer
from ui.dbgOutputTextEdit import DbgOutputWidget
from ui.debugger.assemblyTableWidget import DisassemblyWidget
from ui.debugger.breakpointTreeWidget import BreakpointWidget
from ui.debugger.listenerTreeView import ListenerWidget
from ui.debugger.sourceTextEdit import SourceTextEdit
from ui.debugger.watchpointWidget import WatchpointsWidget
from ui.dialogs.dialogHelper import *
from ui.dialogs.settingsDialog import SettingsDialog
from ui.dialogs.spinnerDialog import SpinnerDialog
from ui.fileinfo.fileInfosTabWidget import FileInfosTabWidget
from ui.fileinfo.fileStructureTreeView import FileStructureWidget
from ui.menuToolbarManager import MenuToolbarManager
from ui.registers.registerTableWidget import RegisterTableWidget
from ui.registers.rflagTableWidget import RFlagWidget
from ui.registers.variablesTableWidget import VariablesTableWidget
from ui.statusBarManager import StatusBarManager
from ui.threadFrameTreeView import ThreadFrameTreeWidget
from ui.tipsAndTricks.tipsAndTricksWizard import TipsAndTricksDialog
from ui.tools.addressCalculator import AddressClaculatorWidget
from ui.tools.arm64InstructionReference import Arm64InstructionReferenceWidget
from ui.tools.toolsMainWidget import ToolsMainWidget
from ui.widgetModules import WidgetModules
from ui.wizard.decompileExecWizard import DecompileExecWizard
from worker.debugWorker import DebugWorker, StepKind

global event_queue
event_queue = queue.Queue()


class MainWindow(QMainWindow):
	event_queue.put("(1) HELLO QUEUE !!!")
	event_queue.put("(2) HELLO QUEUE  1w21 !!!")
	event_queue.put("(3) HELLO QUEUE sdfsdf  !!!")
	event_queue.put("(4) HELLO QUEUE a<sef3sdfs asdasd !!!")
	for i in range(event_queue.qsize(), 0):
		print(
			f"Return of queue => qsoize-before: {event_queue.qsize()} / {event_queue.get()} / qsoize: {event_queue.qsize()}")
	menuToolbarManager = None
	statusBarManager = None

	is_second_section_hidden = False
	workerDebug = None

	driver = None

	currTreDet = None
	tblRegs = []
	rflagsLoaded = 0

	decompileWizard = None

	devHelper = None

	def __init__(self, driver=None, debugger=None):
		super().__init__()

		if driver is not None:
			self.driver = driver
		else:
			self.driver = DebugDriver(debugger, ConfigClass.testTargetSource)

		self.bpMgr = BreakpointManager(self.driver)
		self.setHelper = SettingsHelper()
		self.devHelper = DevHelper(self)

		self.setDockOptions(QMainWindow.DockOption.AllowNestedDocks or QMainWindow.DockOption.AnimatedDocks)

		self.settings = QSettings("DaVeInc", "LLDBGUI")

		self.dock_right = None

		self.menuToolbarManager = MenuToolbarManager(self)
		self.menuToolbarManager.exit_action.triggered.connect(self.handle_close_clicked)
		self.menuToolbarManager.load_action.triggered.connect(self.handle_loadTarget)
		self.menuToolbarManager.attached_action.triggered.connect(self.handle_attachToPID)
		self.menuToolbarManager.settings_action.triggered.connect(self.handle_showSettings)
		self.menuToolbarManager.resume_action.triggered.connect(self.handle_resume)
		self.menuToolbarManager.step_over_action.triggered.connect(self.stepOver_clicked)
		self.menuToolbarManager.step_out_action.triggered.connect(self.stepOut_clicked)
		self.menuToolbarManager.step_into_action.triggered.connect(self.stepInto_clicked)
		self.menuToolbarManager.goBack_action.triggered.connect(self.back_clicked)
		self.menuToolbarManager.goForward_action.triggered.connect(self.forward_clicked)
		self.menuToolbarManager.gotoPC_action.triggered.connect(self.gotoPC_clicked)
		self.menuToolbarManager.gotoOEP_action.triggered.connect(self.gotoOEP_clicked)
		self.menuToolbarManager.gotoAddr_action.triggered.connect(self.gotoAddr_clicked)
		self.menuToolbarManager.about_action.triggered.connect(self.about_clicked)
		self.menuToolbarManager.show_tipsandtricks_action.triggered.connect(self.show_tipsandtricks_clicked)
		self.menuToolbarManager.open_app_action.triggered.connect(self.open_app_clicked)
		self.menuToolbarManager.save_action.triggered.connect(self.save_project_clicked)
		self.menuToolbarManager.save_as_action.triggered.connect(self.save_project_as_clicked)
		# self.menuToolbarManager.showSymbolsPanel_action.triggered.connect(self.showSymbolsPanel_clicked)
		# self.actShowSymbolsPanel
		# self.menuToolbarManager.test_action.triggered.connect(self.test_clicked)

		# self.gotoPC_action.triggered.connect()

		self.statusBarManager = StatusBarManager(self)

		self.stylesheetHelper = StylesheetHelper(self)

		self.splitterMain = QSplitter()
		self.splitterMain.setContentsMargins(0, 0, 0, 0)
		self.splitterMain.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.splitterMain.setOrientation(Qt.Orientation.Vertical)

		self.wdtFiles = WidgetModules()
		# self.wdtFiles.cmbFiles.currentIndexChanged.connect(self.handle_modules_changed)
		self.splitterMain.addWidget(self.wdtFiles)

		self.tabWidgetMain = QTabWidget()
		self.tabWidgetMain.setContentsMargins(0, 0, 0, 0)

		self.tabWidgetFileInfos = FileInfosTabWidget(self.driver)

		self.splitterDbg = QSplitter()
		self.splitterDbg.setOrientation(Qt.Orientation.Horizontal)
		self.wdtDisassembly = DisassemblyWidget(self.driver, None, self)

		# self.wdtFunctionList = FunctionsListViewWidget(self.driver)
		# self.splitterDbgFunc = QSplitter()
		# self.splitterDbgFunc.setOrientation()
		self.splitterDbg.addWidget(self.wdtDisassembly)
		# self.splitterDbg.addWidget(self.wdtFunctionList)

		self.splitterDbgOuter = QSplitter()
		self.splitterDbgOuter.setContentsMargins(0, 0, 0, 0)
		self.splitterDbgOuter.setOrientation(Qt.Orientation.Vertical)
		self.splitterDbgOuter.addWidget(self.splitterDbg)
		self.idxDbgTab = self.tabWidgetMain.addTab(self.splitterDbgOuter, "Disassembly")

		self.tabWidgetStruct = FileStructureWidget(self.driver)
		self.tabWidgetStruct.setContentsMargins(0, 0, 0, 0)
		self.tabWidgetMain.addTab(self.tabWidgetStruct, "Structure")

		self.idxInfoTab = self.tabWidgetMain.addTab(self.tabWidgetFileInfos, "File Infos")

		self.tblHex = QMemoryViewer(self.driver)
		self.tblHex.cmbGrouping.setCurrentIndex(self.setHelper.getValue(SettingsValues.HexGrouping))

		self.idxMemTab = self.tabWidgetMain.addTab(self.tblHex, "Memory")

		self.tabWidgetMain.currentChanged.connect(self.handle_tabWidgetMainCurrentChanged)

		self.tabWidgetConsoles = QTabWidget()

		self.wdtLLDBCmd = CommandsWidget(self.driver)

		self.tabWidgetConsoles.addTab(self.wdtLLDBCmd, "LLDB")

		self.wdtPythonCmd = PyQtConsoleWidget()
		self.tabWidgetConsoles.addTab(self.wdtPythonCmd, "Python")

		self.wdtSystemShell = PexpectConsole() # ConsoleWidget()
		self.wdtSystemShell.eofReachedCallback.connect(self.eofReachedCallback)
		self.tabWidgetConsoles.addTab(self.wdtSystemShell, "System shell")

		self.idxConsolesTab = self.tabWidgetMain.addTab(self.tabWidgetConsoles, "Consoles")

		self.tabWidgetTools = QTabWidget()
		self.idxToolsTab = self.tabWidgetMain.addTab(self.tabWidgetTools, "Tools")

		self.wdtMainTools = ToolsMainWidget()
		self.tabWidgetTools.addTab(self.wdtMainTools, "Converter")

		self.wdtAddresses = AddressClaculatorWidget(self.driver)
		# self.wdtAddreasses = QLabel("Address calculations")
		self.tabWidgetTools.addTab(self.wdtAddresses, "Calculator")

		self.wdtARM64Reference = Arm64InstructionReferenceWidget()
		# self.wdtAddreasses = QLabel("Address calculations")
		self.tabWidgetTools.addTab(self.wdtARM64Reference, "ARM64 Instruction Reference")

		self.splitterMain.addWidget(self.tabWidgetMain)

		self.wdtListener = ListenerWidget(self.driver, self.setHelper)

		self.tabTools = QTabWidget(self)

		self.tabWidgetReg = QTabWidget()
		self.tabWidgetReg.setContentsMargins(0, 0, 0, 0)
		self.tabTools.addTab(self.tabWidgetReg, "Registers")

		self.tblVariables = VariablesTableWidget(self.driver)
		self.tabTools.addTab(self.tblVariables, "Variables")

		self.treBreakpoints = BreakpointWidget(self.driver)  # BreakpointTreeWidget(self.driver)
		self.tabTools.addTab(self.treBreakpoints, "Breakpoints")

		self.treWatchpoints = WatchpointsWidget(self.driver)  # BreakpointTreeWidget(self.driver)
		self.tabTools.addTab(self.treWatchpoints, "Watchpoints")

		self.txtSource = SourceTextEdit(self.driver)
		self.tabTools.addTab(self.txtSource, "Sourcecode")

		self.tabTools.addTab(self.wdtListener, "Listeners")

		self.treThreads = ThreadFrameTreeWidget(self.driver)
		self.tabTools.addTab(self.treThreads, "Threads/Frames")

		self.splitterDbgOuter.addWidget(self.tabTools)

		self.wdtDbg = DbgOutputWidget()
		# self.splitterMain.addWidget(self.wdtDbg)

		self.dock_bottom = QDockWidget()  # ("Bottom Panel", self)
		self.toggleBottomAction = self.dock_bottom.toggleViewAction()
		self.toggleBottomAction.setIcon(ConfigClass.iconLog)
		self.toggleBottomAction.triggered.connect(self.toggleBottomAction_clicked)
		self.menuToolbarManager.toolbar.addAction(self.toggleBottomAction)

		self.menuToolbarManager.nav_menu.addSeparator()
		# Create a disabled action to act as a section title
		sectionTitleAction = QAction('Toggle panels', self)
		sectionTitleAction.setDisabled(True)
		self.menuToolbarManager.nav_menu.addAction(sectionTitleAction)

		self.menuToolbarManager.nav_menu.addAction(self.toggleBottomAction)
		self.toggleRightAction = self.dock_right.toggleViewAction()
		self.menuToolbarManager.nav_menu.addAction(self.toggleRightAction)

		# # self.dock_top = QDockWidget()  # ("Bottom Panel", self)
		# # self.toggleTopAction = self.dock_top.toggleViewAction()
		# # self.toggleTopAction.setIcon(ConfigClass.iconLog)
		# # self.toggleTopAction.triggered.connect(self.wdtFiles.handle_hideModulesSection)
		# # self.menuToolbarManager.toolbar.addAction(self.toggleTopAction)
		# # self.dock_top.setWidget(self.wdtFiles)
		# # self.dock_top.setWindowTitle("Modules")
		# # self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.dock_top)
		# # self.menuToolbarManager.nav_menu.addAction(self.toggleTopAction)

		# self.toggleModulesAction = self.wdtFiles.toggleViewAction()
		# self.menuToolbarManager.nav_menu.addAction(self.toggleModulesAction)

		self.toggleToolbarAction = self.menuToolbarManager.toolbar.toggleViewAction()
		self.menuToolbarManager.nav_menu.addAction(self.toggleToolbarAction)

		self.dock_bottom.setWidget(self.wdtDbg)
		self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_bottom)
		self.menuToolbarManager.test_action.triggered.connect(self.test_clicked)
		self.menuToolbarManager.test_action2.triggered.connect(self.test2_clicked)
		self.menuToolbarManager.openRecentFileCallback = self.tryOpenFile

		# self.wdtTitle = QWidget()
		# self.wdtTitle.setFixedHeight(20)
		# self.wdtTitle.setMinimumHeight(20)
		# dock_bottom.setTitleBarWidget(self.wdtTitle)
		# dock_bottom.setContentsMargins(0, 0, 0, 0)
		self.dock_bottom.setWindowTitle("Debug log")
		# self.dock_bottom.saveGeometry()
		self.dock_bottom.setObjectName("Debug log")
		self.dock_bottom.setTitleBarWidget(CustomDockViewTitleBar(self.dock_bottom, "Debug log"))
		self.dock_right.setTitleBarWidget(CustomDockViewTitleBar(self.dock_right, ""))
		# self.dock_top.setTitleBarWidget(CustomDockViewTitleBar(self.dock_right, "Modules"))

		for dock in [self.dock_bottom,
					 self.dock_right]:  # dock_left, dock_right, QDockWidget.DockWidgetFeature.NoDockWidgetFeatures |
			dock.setFeatures(
				QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetClosable)

		self.tabWidgetFileInfos.tblFileInfos.testMachofile()

		self.splitterMain.setSizes([15, 340, 200, 60])

		self.setCentralWidget(self.splitterMain)

		self.driver.show_dialog = self.show_spinnerDialog
		self.driver.loadingFinished = self.loadingFinished
		self.driver.sendProgressUpdate = self.sendProgressUpdate
		self.driver.sendProgress = self.statusBarManager.progressbar.setValue
		self.driver.logDbgC = logDbgC
		self.driver.loadFileInfosCallback = self.tabWidgetFileInfos.tblFileInfos.loadFileInfos
		self.driver.loadJSONCallback = self.tabWidgetFileInfos.treStats.loadJSONCallback
		self.driver.loadModulesCallback = self.loadModulesCallback
		self.driver.loadModulesCallback2 = self.loadModulesCallback2

		self.driver.loadRegisterCallback.connect(self.handle_loadRegister)
		self.driver.loadRegisterValueCallback.connect(self.handle_loadRegisterValue)
		self.driver.updateRegisterValueCallback.connect(self.handle_updateRegisterValue)
		self.driver.loadVariableValueCallback.connect(self.handle_loadVariableValue)
		self.driver.updateVariableValueCallback.connect(self.handle_updateVariableValue)

		self.driver.loadSymbolCallback = self.handle_loadSymbol
		self.driver.loadSymbolCallbackNG = self.handle_loadSymbolNG
		self.driver.loadActionCallback = self.handle_loadAction
		self.driver.loadStringCallback = self.wdtDisassembly.handle_loadString
		self.driver.loadInstructionCallback = self.wdtDisassembly.handle_loadInstruction
		self.driver.finishedLoadInstructionsCallback = self.handle_workerFinished
		self.driver.finishedLoadModuleCallback = self.handle_workerFinished2
		self.driver.finishedLoadSourcecodeCallback = self.txtSource.handle_loadSourceFinished

		self.driver.handle_processEvent = self.handle_processEvent
		# self.driver.handle_event_listener.connect(self.handle_event_listener)

		self.tabWidgetFileInfos.treSignature.loadSignatureInfo()

		# if self.setHelper.getValue(SettingsValues.SaveWindowStateOnExit):
		self.restoreStateAndGeometry(self.setHelper.getValue(SettingsValues.SaveWindowStateOnExit))

		self.statusBarManager.setStatusMsg(f"LLDBGUI started successfully ...")
		# self.statusBarManager.setProgress(100)
		self.setWinTitleWithState(f"Initialized")

		self.decompileWizard = DecompileExecWizard()

		# self.decompileWizard.exec()

		# DEV ONLY - LOAD TEST TARGET
		# self.handle_loadTarget()

	def handle_event_listener(self, event):
		# self.handle_processEvent(event)
		self.wdtListener.handle_gotNewEvent(event)

		# SBTarget.eBroadcastBitBreakpointChanged | SBTarget.eBroadcastBitWatchpointChanged | SBTarget.eBroadcastBitModulesLoaded | SBTarget.eBroadcastBitModulesUnloaded | SBTarget.eBroadcastBitSymbolsLoaded
		# if SBTarget.EventIsTargetEvent(event):
		#     target = SBTarget.GetTargetFromEvent(event)
		#     logDbgC(f"handle_processEvent = Target: {target} ...")
		#     desc = get_description(event)
		#     logDbgC(f"{desc} ...")
		#     if event.GetType() == lldb.SBTarget.eBroadcastBitBreakpointChanged:
		#         logDbgC(f"BP changed: {desc} ...")
		#
		#         pass
		#     pass
		if SBWatchpoint.EventIsWatchpointEvent(event):
			eventType = SBWatchpoint.GetWatchpointEventTypeFromEvent(event)
			wp = SBWatchpoint.GetWatchpointFromEvent(event)
			logDbgC(f"handle_processEvent = WatchpointEvent: {event} => {wp} ...")
			desc = get_description(event)
			logDbgC(f"{desc} ...")
			if event.GetType() == lldb.SBTarget.eBroadcastBitWatchpointChanged:
				logDbgC(f"Watchpoint changed: {desc} ...")
				if eventType == lldb.eWatchpointEventTypeAdded:
					self.treWatchpoints.tblWatchpoints.handle_loadWatchpointValue(wp)  # .addWatchpoint(wp)
			# self.driver.projectData.addBreakpoint(wp)
		elif SBBreakpoint.EventIsBreakpointEvent(event):
			eventType = SBBreakpoint.GetBreakpointEventTypeFromEvent(event)
			bp = SBBreakpoint.GetBreakpointFromEvent(event)
			logDbgC(f"handle_processEvent = eventType: {eventType} / BP: {bp} ...")
			desc = get_description(event)
			logDbgC(f"{desc} ...")
			if event.GetType() == lldb.SBTarget.eBroadcastBitBreakpointChanged:
				logDbgC(f"BP changed: {desc} ...")

				if eventType == lldb.eBreakpointEventTypeRemoved:
					# logDbgC(f"BP removed @ {addrX} / {bp.GetID()} ...")
					# tblDisassembly.deleteBP(hex(addr))
					self.treBreakpoints.removeBreakpoint(str(bp.GetID()))

				if bp.GetNumLocations() > 0:
					addr = bp.GetLocationAtIndex(0).GetAddress().GetLoadAddress(self.driver.target)
					addrX = hex(addr)

					tblDisassembly = self.wdtDisassembly.tblDisassembly
					if eventType == lldb.eBreakpointEventTypeAdded or eventType == lldb.eBreakpointEventTypeEnabled:
						logDbgC(f"BP added / enabled @ {addrX} / {addr} ...")
						# if eventType == lldb.eBreakpointEventTypeAdded:
						#     self.driver.projectData.addBreakpoint(bp)

						tblDisassembly.enableBP(hex(addr), True)
						if eventType == lldb.eBreakpointEventTypeAdded:
							self.treBreakpoints.addBreakpoint(bp)
							self.driver.projectData.addBreakpoint(bp)
						else:
							self.treBreakpoints.enableBreakpoint(bp, True)
							self.driver.projectData.updateBreakpoint(bp)
					# self.treBreakpoints.enableBreakpoint()
					elif eventType == lldb.eBreakpointEventTypeDisabled:
						logDbgC(f"BP disabled @ {addrX} / {addr} ...")
						tblDisassembly.enableBP(hex(addr), False)
						self.treBreakpoints.enableBreakpoint(bp, False)
						self.driver.projectData.updateBreakpoint(bp)
					elif eventType == lldb.eBreakpointEventTypeRemoved:
						logDbgC(f"BP removed @ {addrX} / {bp.GetID()} ...")
						tblDisassembly.deleteBP(hex(addr))
						self.treBreakpoints.removeBreakpoint(str(bp.GetID()))
						self.driver.projectData.removeBreakpoint(bp)

		# sectionNode.setIcon(0, ConfigClass.iconBPEnabled)
		# eventType = SBBreakpoint.GetBreakpointEventTypeFromEvent(event)
		#
		# subSectionNode = QTreeWidgetItem(sectionNode, ["EventType: ",
		#                                                BreakpointEventTypeString(eventType) + " (" + str(
		#                                                    eventType) + ")"])
		# bp = SBBreakpoint.GetBreakpointFromEvent(event)
		# bp_id = bp.GetID()
		#
		# thread = self.driver.target.GetProcess().GetThreadAtIndex(0)
		# print(thread)
		# frame = thread.GetFrameAtIndex(0)
		# print(frame)
		elif SBProcess.EventIsProcessEvent(event):
			process = SBProcess.GetProcessFromEvent(event)
			logDbgC(f"handle_processEvent: {process} ...")
			desc = get_description(event)
			logDbgC(f"{desc} ...")
			if event.GetType() == SBProcess.eBroadcastBitStateChanged:
				thread = process.selected_thread
				# print('Process event: %s, reason: %d' % (state, thread.GetStopReason()))
				# if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
				#     logDbgC(f"handle_processEvent: {process} ===>>> IS A STOP REASON BREAKKPOINT EVENT --->>> YES !!!  ...")
				if process.state == lldb.eStateStopped:
					self.menuToolbarManager.resume_action.setIcon(ConfigClass.iconResume)
					process = SBProcess.GetProcessFromEvent(event)
					thread = process.GetSelectedThread()
					frame = thread.GetSelectedFrame()
					pc_address = frame.GetPC()  # This returns the program counter as an integer
					# if event.GetType() == lldb.SBProcess.eBroadcastBitStateChanged:
					#     thread = process.selected_thread
					# print('Process event: %s, reason: %d' % (state, thread.GetStopReason()))

					if thread.GetStopReason() == lldb.eStopReasonWatchpoint:
						num_locs = thread.GetStopReasonDataCount()
						for i in range(num_locs):
							wp_id = thread.GetStopReasonDataAtIndex(i)
							watchpoint = process.GetTarget().FindWatchpointByID(wp_id)
							self.treWatchpoints.tblWatchpoints.handle_updateWatchpointValue(watchpoint)
							if watchpoint.IsValid() and watchpoint.IsEnabled() and watchpoint.GetHitCount() > 0:
								# for bl in watchpoint:
								# 	if bl.GetLoadAddress() == pc_address:
								# 		self.treBreakpoints.updateBreakpointValues(bl)
								logDbgC(f"=========>>>>>>>>>> Watchpoint hit: {watchpoint} ...")

					elif thread.GetStopReason() == lldb.eStopReasonBreakpoint:
						# Get the number of breakpoint locations hit
						num_locs = thread.GetStopReasonDataCount()
						# for i in range(num_locs):
						#     bp_id = thread.GetStopReasonDataAtIndex(i)
						#     breakpoint = process.GetTarget().FindBreakpointByID(bp_id)
						#     if breakpoint.IsValid():
						#         print(f"Hit breakpoint: {breakpoint.GetID()} at {breakpoint.GetLocationAtIndex(0).GetAddress()}")
						for i in range(num_locs):
							bp_id = thread.GetStopReasonDataAtIndex(i)
							breakpoint = process.GetTarget().FindBreakpointByID(bp_id)

							if breakpoint.IsValid() and breakpoint.IsEnabled() and breakpoint.GetHitCount() > 0:
								for bl in breakpoint:
									if bl.GetLoadAddress() == pc_address:
										self.treBreakpoints.updateBreakpointValues(bl)
						# print(
						#     f"Actually hit breakpoint: {breakpoint.GetID()} at {breakpoint.GetLocationAtIndex(0).GetLoadAddress()}, HitCount: {breakpoint.GetHitCount()}")
						# if breakpoint.GetLocationAtIndex(0).GetLoadAddress() == pc_address:
						#     self.treBreakpoints.updateBreakpointValues(breakpoint)

						newModFileSpec = frame.GetModule().GetFileSpec()
						newModName = newModFileSpec.GetFilename()
						newModPath = newModFileSpec.fullpath
						logDbgC(f"BP HIT => {pc_address} / {newModName} / {newModPath} / num_locs: {num_locs} !!!!!!!")
						# process.GetTarget()
						self.treThreads.loadStacktrace()
						# length = len(self.tblRegs)
						# for idx in range(1, length):
						#     self.tblRegs[idx].clearRedDelegate()
						# self.clearRegisterHighlighting()
						self.driver.worker.loadRegister()
						self.driver.worker.loadSourcecode()
						# if success:
						#     self.rip = rip
						# if self.rip != "":
						# self.wdtDisassembly.setPC(self.driver.getPC())
						# print(f'REASON BP RFEACHED (listener) Event: {event} => Continuing...')
						# self.suspended = True

						# if self.wdtDisassembly.getCurrentModule() != newModName:
						#     self.wdtDisassembly.setCurrentModule(newModName)
						# if self.wdtDisassembly.disassemblies[newModName] is None:
						print("\033[H\033[J", end="")
						print("\033c", end="")
						self.checkLoadModule(newModFileSpec)
					# newModFileSpec = frame.GetModule().GetFileSpec()
					# newModName = newModFileSpec.GetFilename()
					# newModPath = newModFileSpec.fullpath

					# if not newModName in self.wdtDisassembly.disassemblies:
					#     logDbgC(f"if self.wdtDisassembly.disassemblies[{newModName}] is None: ====>>>> NEED TO INITIALI LOAD MODULE !!!!!")
					#     # import lldb
					#
					#     # Get the current debugger and target
					#     # debugger = lldb.SBDebugger.Create()
					#     self.driver.debugger.SetAsync(False)
					#     target = self.driver.debugger.GetSelectedTarget()
					#     process = target.GetProcess()
					#     thread = process.GetSelectedThread()
					#
					#     # Print stack trace
					#     print(f"Stack trace for thread #{thread.GetIndexID()}:")
					#     for frame in thread:
					#         print(
					#             f"  frame #{frame.GetFrameID()}: {frame.GetFunctionName()} at {frame.GetLineEntry().GetFileSpec().GetFilename()}:{frame.GetLineEntry().GetLine()}")
					#
					#     # self.driver.worker.disassembleModule(newModName)
					#     self.wdtDisassembly.lastModuleKey = None  # Add this to your class init or setup
					#     self.wdtDisassembly.lastSymbolKey = None
					#     self.wdtDisassembly.lastSubSymbolKey = None
					#
					#     if True:
					#         self.wdtDisassembly.resetContent()
					#     # if not self.moduleLoaded:
					#         self.driver.worker.disassembleModule(newModPath) # "/Volumes/Data/dev/python/LLDBGUI/_testtarget/libexternal2.dylib")
					#         # print("\033[H\033[J", end="")
					#         # print("\033c", end="")
					#         # print(self.wdtDisassembly.disassemblies)
					#         self.moduleLoaded = True
					#         return
					#     # else:
					#     #     self.driver.worker.disassembleModule(
					#     #         "/Volumes/Data/dev/python/LLDBGUI/_testtarget/hello_library_exec")
					#
					#     # self.moduleLoaded = not self.moduleLoaded
					# else:
					#     self.wdtFiles.select_module(newModName, False)
					elif thread.GetStopReason() == lldb.eStopReasonWatchpoint:
						logDbgC(f"WP HIT !!!!!!!")
					# print(f'REASON WATCHPOINT RFEACHED (listener) Event: {event} => Continuing...')

					# print(f"🧭 Current PC address: 0x{pc_address:x}")

					# self.wdtDisassembly.setPC(pc_address)
					# # self.treBreakpoints.updateBreakpointValues(bp)
					# self.treBreakpoints.setPC(pc_address)
					self.setPC(pc_address)


				elif process.state == lldb.eStateStepping or process.state == lldb.eStateRunning:
					logDbgC(f"elif process.state == eStateStepping or process.state == eStateRunning: ...")
					self.menuToolbarManager.resume_action.setIcon(ConfigClass.iconPause)
					# self.wdtDisassembly.clearPC()
					# self.treBreakpoints.clearPC()
					self.clearPC()


			elif event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
				logDbgC(
					f"================>>>>>>>>>>>>>>>>>> elif event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT: ...")
				# pass
				# stdoutNG = lldb.SBProcess.GetProcessFromEvent(event).GetSTDOUT(1024)
				# if process.GetSelectedThread().Suspend():
				# if process.GetSelectedThread().Suspend():
				stdoutNG = self.readSTDOUT(process)
				# print(f"stdoutNG: START ====>>>  {stdoutNG} ====>>> END (0)")
				# self.should_quit
				if event and stdoutNG and stdoutNG != "":
					# stdoutNG = lldb.SBProcess.GetProcessFromEvent(event).GetSTDOUT(1024)
					stdoutNG = self.readSTDOUT(process)
					print(f"stdoutNG: {stdoutNG} (1)")
			# event = lldb.SBEvent()
			# result = self.listener.GetNextEvent(event)
			# print(f"WaitForEvent() => GetNextEvent: {result}")
			# if not self.should_quit and event is not None:
			#     stdoutNG = lldb.SBProcess.GetProcessFromEvent(event).GetSTDOUT(1024)
			#     print(f"stdoutNG: {stdoutNG}")
			# if event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
			#     print(f"GOT STDOUT EVENT!!!")
			#     # # continue
			#     # import sys
			#     # sys.stdout.flush()
			#     # print("STD OUT EVENT LISTENER!!! (XXX)")
			#     # # sys.stdout.flush()
			#     # stdoutTxt = process.GetSTDOUT(2048)
			#     # # print(SBProcess.GetProcessFromEvent(event))
			#     # print(f"STDOUT IS: {stdoutTxt}")
			#     # self.wdtSystemShell.append_text(stdoutTxt)
			#     # Now that we are done dump the stdout and stderr
			#     # if process.state != eStateStopped:
			#     #     # self.driver.worker.handleDbgCmd(f"process interrupt")
			#     #     process.Stop()
			#     process_stdout = process.GetSTDOUT(1024)
			#     if process_stdout:
			#         print("Process STDOUT:\n%s" % (process_stdout))
			#         while process_stdout:
			#             process_stdout = process.GetSTDOUT(1024)
			#             print(process_stdout)
			# else:
			if process.state == lldb.eStateStepping or process.state == lldb.eStateRunning:
				logDbgC(f"if process.state == eStateStepping or process.state == eStateRunning: ...")
				state = 'running'
			elif process.state == lldb.eStateExited:
				state = 'exited'
				logDbgC(f"self.worker.listener.should_quit = True (4)")
			# self.should_quit = True
			elif process.state == lldb.eStateStopped:
				# isWaiting4Input = self.is_waiting_for_input(process)
				# if isWaiting4Input:
				#     print(f"IS WAITING FOR INPUT: {isWaiting4Input} !!!")
				pass

	def eofReachedCallback(self):
		self.close()

	def toggleBottomAction_clicked(self):
		self.toggleBottomAction.setIcon(ConfigClass.iconLog if self.dock_bottom.isVisible() else ConfigClass.iconLogBW)

	def test_clicked(self):
		self.saveAllGeometryAndState()

	def saveGeometryForWidget(self, wwidget, key):
		geo = wwidget.saveGeometry()
		logDbgC(f"{key}: {geo}")
		self.settings.setValue(key, geo)

	def saveGStateForWidget(self, wwidget, key):
		geo = wwidget.saveState()
		logDbgC(f"{key}: {geo}")
		self.settings.setValue(key, geo)

	def saveAllGeometryAndState(self):

		self.saveGeometryForWidget(self.dock_bottom, "bottomDockGeometry")
		self.saveGeometryForWidget(self.dock_right, "rightDockGeometry")
		# self.saveGeometryForWidget(self.splitterDbgOuter, "splitterDbgOuterGeometry")
		self.saveGeometryForWidget(self.tabTools, "tabToolsGeometry")
		self.saveGeometryForWidget(self.splitterDbg, "splitterDbgGeometry")

		# self.splitterDbg

		# self.restoreGeometryForWidget(self.tabTools, "tabToolsGeometry")

		self.saveGStateForWidget(self.splitterDbgOuter, "splitterState")
		# splitterState = self.splitterDbgOuter.saveState()
		# logDbgC(f"self.splitterDbgOuter.saveState(): {splitterState}")
		# self.settings.setValue("splitterState", splitterState)

		self.saveGStateForWidget(self, "windowState")
		# winState = self.saveState()
		# logDbgC(f"self.saveState(): {winState}")
		# self.settings.setValue("windowState", winState)

	def test2_clicked(self):
		# geo = self.saveGeometry()
		# logDbgC(f"self.saveGeometry(): {geo}")
		# self.settings.setValue("bottomDockGeometry", geo)
		# self.wdtDisassembly.wdtControlFlow.resetContent()
		# self.wdtDisassembly.wdtControlFlow.loadConnectionsFromWorker(self.wdtDisassembly.wdtControlFlow.workerConnections)

		# self.restoreAllWindowAndControlStates()

		# self.ttd = TipsAndTricksDialog()
		# self.ttd.show()
		# self.show_tipsandtricks_clicked()

		# self.decompileWizard.showWizard()
		# logDbgC(
		# 	f"self.wdtDisassembly.lastModuleKey: {self.wdtDisassembly.lastModuleKey}, self.wdtDisassembly.disassemblies: {self.wdtDisassembly.disassemblies}")
		# Find variable address
		# frame = self.driver.target.process.GetSelectedThread().GetSelectedFrame()
		# var = frame.FindVariable("idx")
		# addr = var.GetLoadAddress()
		#
		# # Set watchpoint
		# error = lldb.SBError()
		# watchpoint = self.driver.target.WatchAddress(addr, var.GetByteSize(), True, True, error)
		# logDbgC(f"watchpoint: {watchpoint} => error: {error} ...")
		# # Configure watchpoint
		# watchpoint.SetCondition("idx != 12")
		# # watchpoint.SetIgnoreCount(2)
		# watchpoint.SetEnabled(True)

		WatchpointHelper(self.driver).setWatchpointForVariable("idx", WatchpointAccessMod.Read_Write)

	def show_tipsandtricks_clicked(self):
		TipsAndTricksDialog.showTipsAndTricksDialog()

	def restoreGeometryForWidget(self, wwidget, key):
		geometry = self.settings.value(key)
		if geometry:
			logDbgC(f"{key}: {geometry}")
			wwidget.restoreGeometry(geometry)

	def restoreStateForWidget(self, wwidget, key):
		state = self.settings.value(key)
		if state:
			logDbgC(f"{key}: {state}")
			wwidget.restoreState(state)

	def restoreAllWindowAndControlStates(self):
		# self.wdtDisassembly.wdtControlFlow.checkHideOverflowConnections()
		# pass

		self.restoreGeometryForWidget(self.dock_bottom, "bottomDockGeometry")
		self.restoreGeometryForWidget(self.dock_right, "rightDockGeometry")
		# self.restoreGeometryForWidget(self.tabTools.widget(0), "tabToolsGeometry")
		# self.restoreGeometryForWidget(self.splitterDbgOuter, "splitterDbgOuterGeometry")
		self.restoreGeometryForWidget(self.tabTools, "tabToolsGeometry")
		self.restoreGeometryForWidget(self.splitterDbg, "splitterDbgGeometry")

		self.restoreStateForWidget(self.splitterDbgOuter, "splitterState")
		# splitterState = self.settings.value("splitterState")
		# if splitterState:
		#     logDbgC(f"self.splitterDbgOuter.restoreState({splitterState}) ...")
		#     self.splitterDbgOuter.restoreState(splitterState)

		self.restoreStateForWidget(self, "windowState")

		# winState = self.settings.value("windowState")
		# if winState:
		#     logDbgC(f"self.restoreState({winState}) ...")
		#     self.restoreState(winState)

	def handle_loadSymbolNG(self, params):
		# self.wdtDisassembly.handle_loadSymbol(params["symbol"])
		# if loadInSymbolList:
		print(f"params: {params} ...")
		if bool(params["addSym"]):  # and params["symbol"] != "__stubs":
			self.wdtDisassembly.wdtFunctionList.addSymbol(params["symbol"], params["row"])

	def handle_loadAction(self, params):
		# self.wdtDisassembly.handle_loadSymbol(params["symbol"])
		# if loadInSymbolList:
		print(f"params: {params} ...")
		# if bool(params["addSym"]):  # and params["symbol"] != "__stubs":
		self.wdtDisassembly.wdtFunctionList.addAction(params["calledFunction"], params["callAddr"])

	def handle_loadSymbol(self, symbol, loadDisassembly=True):
		logDbgC(f"handle_loadSymbol({symbol}, {loadDisassembly}) ...")
		if symbol != "":
			self.wdtDisassembly.handle_loadSymbol(symbol, loadDisassembly)
		# if loadInSymbolList:
		# self.wdtDisassembly.wdtFunctionList.addSymbol(symbol)

	def onQApplicationStarted(self):
		# QApplication.processEvents()

		if SettingsHelper().getValue(SettingsValues.ShowTipsAtStartup):
			TipsAndTricksDialog.showTipsAndTricksDialog()

		if self.setHelper.getValue(SettingsValues.LoadTestTarget) and ConfigClass.startTestTarget:
			self.handle_loadTarget()

		logDbgC(f"onQApplicationStarted() ...")

	def open_app_clicked(self):
		filenameOpenApp = showOpenFileDialog()
		logDbgC(f"filenameOpenApp: {filenameOpenApp} ...")
		self.tryOpenFile(filenameOpenApp, "arm64-apple-macosx15.1.0")

	def tryOpenFile(self, filepath, arch="x86_64-apple-macosx15.1.1"):
		if filepath is not None and filepath != "":
			self.wdtDisassembly.disassemblies = {}
			self.wdtDisassembly.resetContent()
			# self.rflagsLoaded =
			self.tblRegs.clear()
			# self.tblRegs.clear()
			self.tabWidgetReg.clear()
			# if "/" in ConfigClass.testTarget:
			#     print(f"STRING HAS SLASH!!!!!")
			# last_part = ConfigClass.testTarget.rsplit("/", 1)[-1]
			self.menuToolbarManager.add_recent_file(filepath)
			self.driver.loadTarget(filepath, arch)  # , ConfigClass.testTargetArch)

	def save_project_clicked(self):
		saveAsFilename = showSaveFileDialog(None, "LLDBGUI-Project (*.ldbg)")
		if saveAsFilename:
			saveAsFilenameWithSuffix = ensure_suffix(saveAsFilename, ".ldbg")
			logDbgC(f"Saving project as: {saveAsFilenameWithSuffix} ...")

			# # Check if file exists
			# if not os.path.exists(saveAsFilenameWithSuffix):
			#     with open(saveAsFilenameWithSuffix, "w", encoding="utf-8") as f:
			#         fileContent = json.dumps(self.driver.projectData.to_dict(), indent=2) #json.dumps(self.driver.projectData)
			#         f.write(fileContent)
			#     print(f"Saved JSON to {saveAsFilenameWithSuffix}")
			# else:
			#     print(f"File {saveAsFilenameWithSuffix} already exists. Skipping save.")
			with open(saveAsFilenameWithSuffix, "w", encoding="utf-8") as f:
				fileContent = json.dumps(self.driver.projectData.to_dict(),
										 indent=2)  # json.dumps(self.driver.projectData)
				f.write(fileContent)
			print(f"Saved JSON to {saveAsFilenameWithSuffix}")

	def save_project_as_clicked(self):
		saveAsFilename = showSaveFileDialog(None, "LLDBGUI-Project (*.ldbg)")
		if saveAsFilename:
			saveAsFilenameWithSuffix = ensure_suffix(saveAsFilename, ".ldbg")
			logDbgC(f"Saving project as: {saveAsFilenameWithSuffix} ...")

			with open(saveAsFilenameWithSuffix, "w", encoding="utf-8") as f:
				fileContent = json.dumps(self.driver.projectData.to_dict(),
										 indent=2)  # json.dumps(self.driver.projectData)
				f.write(fileContent)
			logDbgC(f"Saved JSON to {saveAsFilenameWithSuffix} ...")

	moduleLoaded = False

	def about_clicked(self):
		# AboutDialog().exec()
		# wizard.setWindowTitle("Trivial Wizard");
		# wizard.show();
		DecompileExecWizard().showWizard()
		pass
		# self.wdtDisassembly.lastModuleKey = None  # Add this to your class init or setup
		# self.wdtDisassembly.lastSymbolKey = None
		# self.wdtDisassembly.lastSubSymbolKey = None
		#
		# if True:
		#     self.wdtDisassembly.resetContent()
		# if not self.moduleLoaded:
		#     self.driver.worker.disassembleModule("/Volumes/Data/dev/python/LLDBGUI/_testtarget/libexternal.dylib")
		# else:
		#     self.driver.worker.disassembleModule("/Volumes/Data/dev/python/LLDBGUI/_testtarget/hello_library_exec")
		# self.moduleLoaded = not self.moduleLoaded

	def handle_showMemory(self, address):
		logDbgC(f"Show Memory => address: {address} ...")
		# self.tabWidgetReg.setTabVisible()
		# self.window().idxMemTab.setTabVisible(2, True)
		self.tabWidgetMain.setCurrentIndex(self.idxMemTab)  # , True
		self.tblHex.doReadMemory(int(address, 16))
		# self.window().idxMemTab.setTabVisible(2, True)
		# self.idxMemTab = self.tabWidgetMain.addTab(self.tblHex, "Memory")

	def showSymbolsPanel_clicked(self):
		# self.dock_right.show()
		pass

	def stepOver_clicked(self):
		self.clearRegisterHighlighting()
		self.treBreakpoints.clearPC()
		self.driver.debugger.SetAsync(False)
		self.start_debugWorker(self.driver, StepKind.StepOver, self.handle_debugStepCompleted)
		self.setWinTitleWithState("Step-Over")

	def stepInto_clicked(self):
		self.clearRegisterHighlighting()
		self.treBreakpoints.clearPC()
		self.driver.debugger.SetAsync(False)
		self.start_debugWorker(self.driver, StepKind.StepInto, self.handle_debugStepCompleted)
		self.setWinTitleWithState("Step-Into")

	def stepOut_clicked(self):
		self.clearRegisterHighlighting()
		self.treBreakpoints.clearPC()
		self.driver.debugger.SetAsync(False)
		self.start_debugWorker(self.driver, StepKind.StepOut, self.handle_debugStepCompleted)
		self.setWinTitleWithState("Step-Out")

	def handle_debugStepCompleted(self, kind, success, rip, frm):
		self.setWinTitleWithState("Interrupted")
		# self.driver.setProcessRunning(False)
		# logDbgC(f"handle_debugStepCompleted({kind}, {success}, {rip}, {frm}) ====>>>> Module: {frm.GetModule().GetFileSpec().GetFilename()}")
		if success:
			self.rip = rip
			if self.rip != "":
				# logDbgC(f"GOTCHA RIP: {self.rip} ...")
				# logDbgC(f"GOTCHA RIP CONVERTED: {convert_64_to_32(self.rip)} ...")
				# logDbgC(f"GOTCHA RIP strip_leading_zeros: {strip_leading_zeros(self.rip)} ...")

				# self.wdtDisassembly.setPC(int(str(self.rip), 16))
				self.setPC(int(str(self.rip), 16))
				self.treThreads.loadStacktrace()
				# self.clearRegisterHighlighting()
				self.driver.worker.loadRegister()
				self.driver.worker.loadSourcecode()

		#         self.wdtBPsWPs.treBPs.setPC(self.rip)
		#     self.start_loadRegisterWorker(False)
		#     self.wdtBPsWPs.reloadBreakpoints(False)
		#     # self.tabWatchpoints.reloadWatchpoints(False)
		#     self.loadStacktrace()
		#
		#     context = frm.GetSymbolContext(lldb.eSymbolContextEverything)
		#     self.workerManager.start_loadSourceWorker(self.driver.debugger, self.worker.sourceFile,
		#                                               self.handle_loadSourceFinished,
		#                                               context.GetLineEntry().GetLine())
		#     if len(self.tblRegs) > 0:
		#         self.tblRegs[0].loadRFlags(self.driver.debugger)
		#     #			self.setResumeActionIcon()
		#     self.setWinTitleWithState("Interrupted")
		#     self.setResumeActionIcon()
		#     self.isProcessRunning = False
		# else:
		#     # print(f"Debug STEP ({kind}) FAILED!!!")
		#     self.setResumeActionIcon()
		# self.isProcessRunning = False
		pass

	def clearRegisterHighlighting(self):
		length = len(self.tblRegs)
		if (length >= 4):
			for idx in range(1, length):
				self.tblRegs[idx].clearRedDelegate()
		self.tblVariables.clearRedDelegate()

	def handle_resume(self):
		# logDbgC(f"self.driver.worker.process.GetState(): {self.driver.worker.process.GetState()} => SBDebugger.StateIsRunningState(self.driver.worker.process.GetState()): {SBDebugger.StateIsRunningState(self.driver.worker.process.GetState())}")
		# if SBDebugger.StateIsRunningState(self.driver.worker.process.GetState()):
		#     self.driver.stopProcess()
		#     self.menuToolbarManager.resume_action.setIcon(ConfigClass.iconResume)
		# else:
		#     self.driver.continueProcess()
		#     self.menuToolbarManager.resume_action.setIcon(ConfigClass.iconPause)
		logDbgC(f"handle_resume() => self.driver.isProcessRunning(): {self.driver.isProcessRunning()}")
		# if self.driver.isProcessRunning():
		if SBDebugger.StateIsRunningState(self.driver.worker.process.GetState()):
			self.driver.setProcessRunning(False)
			print(f"self.isProcessRunning => Trying to Suspend()")
			# # self.debugger.HandleCommand("process interrupt")
			# self.driver.handleDbgCmd(f"process interrupt")
			# self.driver.handleDbgCmd(f"dis")
			# self.debugger.HandleCommand("dis")
		else:
			# self.driver.setProcessRunning(True)
			self.treBreakpoints.clearPC()
			self.clearRegisterHighlighting()

			self.driver.debugger.SetAsync(True)
			self.start_debugWorker(self.driver, StepKind.Continue, self.handle_debugStepCompleted)

	def start_debugWorker(self, driver, kind, handle_debugStepCompleted):
		if self.workerDebug == None or not self.workerDebug.isRunning:
			#			self.setResumeActionIcon(ConfigClass.iconPause)
			self.workerDebug = DebugWorker(driver, kind)
			self.workerDebug.signals.debugStepCompleted.connect(handle_debugStepCompleted)
			#			self.workerDebug.signals.setPC.connect(self.handle_debugSetPC)

			QThreadPool.globalInstance().start(self.workerDebug)
			print(f"After self.threadpool.start(self.workerDebug)")
			return True
		# else:
		return False

	def back_clicked(self):
		tblDisassembly = self.wdtDisassembly.tblDisassembly
		newLoc = tblDisassembly.locationStack.backLocation()
		if newLoc:
			# print(f"GOING BACK to {newLoc} ... {self.txtMultiline.locationStack.currentLocation}")
			tblDisassembly.viewAddress(newLoc, False)
		self.menuToolbarManager.goForward_action.setEnabled(not tblDisassembly.locationStack.currentIsLast())
		self.menuToolbarManager.goBack_action.setEnabled(not tblDisassembly.locationStack.currentIsFirst())

	def forward_clicked(self):
		tblDisassembly = self.wdtDisassembly.tblDisassembly
		newLoc = tblDisassembly.locationStack.forwardLocation()
		if newLoc:
			# print(f"GOING FORWARD to {newLoc} ... {self.txtMultiline.locationStack.currentLocation}")
			tblDisassembly.viewAddress(newLoc, False)
		self.menuToolbarManager.goForward_action.setEnabled(not tblDisassembly.locationStack.currentIsLast())
		self.menuToolbarManager.goBack_action.setEnabled(not tblDisassembly.locationStack.currentIsFirst())

	def gotoPC_clicked(self):
		self.wdtDisassembly.tblDisassembly.selectAndViewRow()

	def gotoOEP_clicked(self):
		self.wdtDisassembly.tblDisassembly.viewAddress(hex(self.driver.worker.main_oep), True)

	def gotoAddr_clicked(self):
		gotoAddrDlg = GotoAddressDialog()
		gotoAddrDlg.exec()
		newAddr = gotoAddrDlg.txtInput.text()
		if newAddr != "" and is_hex_string(newAddr):
			self.wdtDisassembly.tblDisassembly.viewAddress(newAddr, True)

	def get_breakpoints_for_module(self, target, module):
		"""
		Returns a list of SBBreakpoint objects that are located within a given SBModule.
		"""
		if not isinstance(target, lldb.SBTarget):  # or not isinstance(module, lldb.SBModule):
			print("Invalid target or module object.")
			return []

		breakpoints = []

		# Iterate through all breakpoints in the target
		for breakpoint in target.breakpoint_iter():

			# Iterate through all locations within the current breakpoint
			for location in breakpoint.locations:

				# Get the module associated with the breakpoint location's address
				# This is a bit indirect, but necessary
				address_module = location.GetAddress().GetModule()

				# Check if the module of the location matches the target module
				if address_module and address_module.GetFileSpec().GetFilename() == module:
					# Add the parent breakpoint object to our list
					# breakpoints.append(breakpoint)
					# Break the inner loop to avoid adding the same breakpoint multiple times
					self.wdtDisassembly.tblDisassembly.enableBP(hex(location.GetAddress().GetLoadAddress(target)),
																location.IsEnabled())
					break

		return breakpoints

	@pyqtSlot(object)
	def handle_processEvent(self, event):
		self.wdtListener.handle_gotNewEvent(event)

		# SBTarget.eBroadcastBitBreakpointChanged | SBTarget.eBroadcastBitWatchpointChanged | SBTarget.eBroadcastBitModulesLoaded | SBTarget.eBroadcastBitModulesUnloaded | SBTarget.eBroadcastBitSymbolsLoaded
		# if SBTarget.EventIsTargetEvent(event):
		#     target = SBTarget.GetTargetFromEvent(event)
		#     logDbgC(f"handle_processEvent = Target: {target} ...")
		#     desc = get_description(event)
		#     logDbgC(f"{desc} ...")
		#     if event.GetType() == lldb.SBTarget.eBroadcastBitBreakpointChanged:
		#         logDbgC(f"BP changed: {desc} ...")
		#
		#         pass
		#     pass
		if SBWatchpoint.EventIsWatchpointEvent(event):
			eventType = SBWatchpoint.GetWatchpointEventTypeFromEvent(event)
			wp = SBWatchpoint.GetWatchpointFromEvent(event)
			logDbgC(f"handle_processEvent = WatchpointEvent: {event} => {wp} ...")
			desc = get_description(event)
			logDbgC(f"{desc} ...")
			if event.GetType() == lldb.SBTarget.eBroadcastBitWatchpointChanged:
				logDbgC(f"Watchpoint changed: {desc} ...")
				if eventType == lldb.eWatchpointEventTypeAdded:
					self.treWatchpoints.tblWatchpoints.handle_loadWatchpointValue(wp) # .addWatchpoint(wp)
					# self.driver.projectData.addBreakpoint(wp)
		elif SBBreakpoint.EventIsBreakpointEvent(event):
			eventType = SBBreakpoint.GetBreakpointEventTypeFromEvent(event)
			bp = SBBreakpoint.GetBreakpointFromEvent(event)
			logDbgC(f"handle_processEvent = eventType: {eventType} / BP: {bp} ...")
			desc = get_description(event)
			logDbgC(f"{desc} ...")
			if event.GetType() == lldb.SBTarget.eBroadcastBitBreakpointChanged:
				logDbgC(f"BP changed: {desc} ...")

				if eventType == lldb.eBreakpointEventTypeRemoved:
					# logDbgC(f"BP removed @ {addrX} / {bp.GetID()} ...")
					# tblDisassembly.deleteBP(hex(addr))
					self.treBreakpoints.removeBreakpoint(str(bp.GetID()))

				if bp.GetNumLocations() > 0:
					addr = bp.GetLocationAtIndex(0).GetAddress().GetLoadAddress(self.driver.target)
					addrX = hex(addr)

					tblDisassembly = self.wdtDisassembly.tblDisassembly
					if eventType == lldb.eBreakpointEventTypeAdded or eventType == lldb.eBreakpointEventTypeEnabled:
						logDbgC(f"BP added / enabled @ {addrX} / {addr} ...")
						# if eventType == lldb.eBreakpointEventTypeAdded:
						#     self.driver.projectData.addBreakpoint(bp)

						tblDisassembly.enableBP(hex(addr), True)
						if eventType == lldb.eBreakpointEventTypeAdded:
							self.treBreakpoints.addBreakpoint(bp)
							self.driver.projectData.addBreakpoint(bp)
						else:
							self.treBreakpoints.enableBreakpoint(bp, True)
							self.driver.projectData.updateBreakpoint(bp)
							# self.treBreakpoints.enableBreakpoint()
					elif eventType == lldb.eBreakpointEventTypeDisabled:
						logDbgC(f"BP disabled @ {addrX} / {addr} ...")
						tblDisassembly.enableBP(hex(addr), False)
						self.treBreakpoints.enableBreakpoint(bp, False)
						self.driver.projectData.updateBreakpoint(bp)
					elif eventType == lldb.eBreakpointEventTypeRemoved:
						logDbgC(f"BP removed @ {addrX} / {bp.GetID()} ...")
						tblDisassembly.deleteBP(hex(addr))
						self.treBreakpoints.removeBreakpoint(str(bp.GetID()))
						self.driver.projectData.removeBreakpoint(bp)

			# sectionNode.setIcon(0, ConfigClass.iconBPEnabled)
			# eventType = SBBreakpoint.GetBreakpointEventTypeFromEvent(event)
			#
			# subSectionNode = QTreeWidgetItem(sectionNode, ["EventType: ",
			#                                                BreakpointEventTypeString(eventType) + " (" + str(
			#                                                    eventType) + ")"])
			# bp = SBBreakpoint.GetBreakpointFromEvent(event)
			# bp_id = bp.GetID()
			#
			# thread = self.driver.target.GetProcess().GetThreadAtIndex(0)
			# print(thread)
			# frame = thread.GetFrameAtIndex(0)
			# print(frame)
		elif SBProcess.EventIsProcessEvent(event):
			process = SBProcess.GetProcessFromEvent(event)
			logDbgC(f"handle_processEvent: {process} ...")
			desc = get_description(event)
			logDbgC(f"{desc} ...")
			if event.GetType() == SBProcess.eBroadcastBitStateChanged:
				thread = process.selected_thread
				# print('Process event: %s, reason: %d' % (state, thread.GetStopReason()))
				# if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
				#     logDbgC(f"handle_processEvent: {process} ===>>> IS A STOP REASON BREAKKPOINT EVENT --->>> YES !!!  ...")
				if process.state == lldb.eStateStopped:
					self.menuToolbarManager.resume_action.setIcon(ConfigClass.iconResume)
					process = SBProcess.GetProcessFromEvent(event)
					thread = process.GetSelectedThread()
					frame = thread.GetSelectedFrame()
					pc_address = frame.GetPC()  # This returns the program counter as an integer
					# if event.GetType() == lldb.SBProcess.eBroadcastBitStateChanged:
					#     thread = process.selected_thread
					# print('Process event: %s, reason: %d' % (state, thread.GetStopReason()))

					if thread.GetStopReason() == lldb.eStopReasonWatchpoint:
						num_locs = thread.GetStopReasonDataCount()
						for i in range(num_locs):
							wp_id = thread.GetStopReasonDataAtIndex(i)
							watchpoint = process.GetTarget().FindWatchpointByID(wp_id)
							self.treWatchpoints.tblWatchpoints.handle_updateWatchpointValue(watchpoint)
							if watchpoint.IsValid() and watchpoint.IsEnabled() and watchpoint.GetHitCount() > 0:
								# for bl in watchpoint:
								# 	if bl.GetLoadAddress() == pc_address:
								# 		self.treBreakpoints.updateBreakpointValues(bl)
								logDbgC(f"=========>>>>>>>>>> Watchpoint hit: {watchpoint} ...")

					elif thread.GetStopReason() == lldb.eStopReasonBreakpoint:

						thread1 = process.GetThreadAtIndex(0)
						frame1 = thread1.GetFrameAtIndex(0)
						instructions = frame1.Disassemble()
						print(f"instructions: {instructions} ....")

						# Get the number of breakpoint locations hit
						num_locs = thread.GetStopReasonDataCount()
						# for i in range(num_locs):
						#     bp_id = thread.GetStopReasonDataAtIndex(i)
						#     breakpoint = process.GetTarget().FindBreakpointByID(bp_id)
						#     if breakpoint.IsValid():
						#         print(f"Hit breakpoint: {breakpoint.GetID()} at {breakpoint.GetLocationAtIndex(0).GetAddress()}")
						for i in range(num_locs):
							bp_id = thread.GetStopReasonDataAtIndex(i)
							breakpoint = process.GetTarget().FindBreakpointByID(bp_id)

							if breakpoint.IsValid() and breakpoint.IsEnabled() and breakpoint.GetHitCount() > 0:
								for bl in breakpoint:
									if bl.GetLoadAddress() == pc_address:
										self.treBreakpoints.updateBreakpointValues(bl)
								# print(
								#     f"Actually hit breakpoint: {breakpoint.GetID()} at {breakpoint.GetLocationAtIndex(0).GetLoadAddress()}, HitCount: {breakpoint.GetHitCount()}")
								# if breakpoint.GetLocationAtIndex(0).GetLoadAddress() == pc_address:
								#     self.treBreakpoints.updateBreakpointValues(breakpoint)

						newModFileSpec = frame.GetModule().GetFileSpec()
						newModName = newModFileSpec.GetFilename()
						newModPath = newModFileSpec.fullpath
						logDbgC(f"BP HIT => {pc_address} / {newModName} / {newModPath} / num_locs: {num_locs} !!!!!!!")
						# process.GetTarget()
						self.treThreads.loadStacktrace()
						# length = len(self.tblRegs)
						# for idx in range(1, length):
						#     self.tblRegs[idx].clearRedDelegate()
						# self.clearRegisterHighlighting()
						self.driver.worker.loadRegister()
						self.driver.worker.loadSourcecode()
						# if success:
						#     self.rip = rip
						# if self.rip != "":
						# self.wdtDisassembly.setPC(self.driver.getPC())
						# print(f'REASON BP RFEACHED (listener) Event: {event} => Continuing...')
						# self.suspended = True

						# if self.wdtDisassembly.getCurrentModule() != newModName:
						#     self.wdtDisassembly.setCurrentModule(newModName)
						# if self.wdtDisassembly.disassemblies[newModName] is None:
						print("\033[H\033[J", end="")
						print("\033c", end="")
						self.checkLoadModule(newModFileSpec)
						# newModFileSpec = frame.GetModule().GetFileSpec()
						# newModName = newModFileSpec.GetFilename()
						# newModPath = newModFileSpec.fullpath

						# if not newModName in self.wdtDisassembly.disassemblies:
						#     logDbgC(f"if self.wdtDisassembly.disassemblies[{newModName}] is None: ====>>>> NEED TO INITIALI LOAD MODULE !!!!!")
						#     # import lldb
						#
						#     # Get the current debugger and target
						#     # debugger = lldb.SBDebugger.Create()
						#     self.driver.debugger.SetAsync(False)
						#     target = self.driver.debugger.GetSelectedTarget()
						#     process = target.GetProcess()
						#     thread = process.GetSelectedThread()
						#
						#     # Print stack trace
						#     print(f"Stack trace for thread #{thread.GetIndexID()}:")
						#     for frame in thread:
						#         print(
						#             f"  frame #{frame.GetFrameID()}: {frame.GetFunctionName()} at {frame.GetLineEntry().GetFileSpec().GetFilename()}:{frame.GetLineEntry().GetLine()}")
						#
						#     # self.driver.worker.disassembleModule(newModName)
						#     self.wdtDisassembly.lastModuleKey = None  # Add this to your class init or setup
						#     self.wdtDisassembly.lastSymbolKey = None
						#     self.wdtDisassembly.lastSubSymbolKey = None
						#
						#     if True:
						#         self.wdtDisassembly.resetContent()
						#     # if not self.moduleLoaded:
						#         self.driver.worker.disassembleModule(newModPath) # "/Volumes/Data/dev/python/LLDBGUI/_testtarget/libexternal2.dylib")
						#         # print("\033[H\033[J", end="")
						#         # print("\033c", end="")
						#         # print(self.wdtDisassembly.disassemblies)
						#         self.moduleLoaded = True
						#         return
						#     # else:
						#     #     self.driver.worker.disassembleModule(
						#     #         "/Volumes/Data/dev/python/LLDBGUI/_testtarget/hello_library_exec")
						#
						#     # self.moduleLoaded = not self.moduleLoaded
						# else:
						#     self.wdtFiles.select_module(newModName, False)
					elif thread.GetStopReason() == lldb.eStopReasonWatchpoint:
						logDbgC(f"WP HIT !!!!!!!")
						# print(f'REASON WATCHPOINT RFEACHED (listener) Event: {event} => Continuing...')

					# print(f"🧭 Current PC address: 0x{pc_address:x}")

					# self.wdtDisassembly.setPC(pc_address)
					# # self.treBreakpoints.updateBreakpointValues(bp)
					# self.treBreakpoints.setPC(pc_address)
					self.setPC(pc_address)


				elif process.state == lldb.eStateStepping or process.state == lldb.eStateRunning:
					logDbgC(f"elif process.state == eStateStepping or process.state == eStateRunning: ...")
					self.menuToolbarManager.resume_action.setIcon(ConfigClass.iconPause)
					# self.wdtDisassembly.clearPC()
					# self.treBreakpoints.clearPC()
					self.clearPC()


			elif event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
				logDbgC(
					f"================>>>>>>>>>>>>>>>>>> elif event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT: ...")
				# pass
				# stdoutNG = lldb.SBProcess.GetProcessFromEvent(event).GetSTDOUT(1024)
				# if process.GetSelectedThread().Suspend():
				# if process.GetSelectedThread().Suspend():
				stdoutNG = self.readSTDOUT(process)
				print(f"stdoutNG: START ====>>>  {stdoutNG} ====>>> END (0)")
				# self.should_quit
				if event and stdoutNG and stdoutNG != "":
					# stdoutNG = lldb.SBProcess.GetProcessFromEvent(event).GetSTDOUT(1024)
					stdoutNG = self.readSTDOUT(process)
					print(f"stdoutNG: {stdoutNG} (1)")
				# event = lldb.SBEvent()
				# result = self.listener.GetNextEvent(event)
				# print(f"WaitForEvent() => GetNextEvent: {result}")
				# if not self.should_quit and event is not None:
				#     stdoutNG = lldb.SBProcess.GetProcessFromEvent(event).GetSTDOUT(1024)
				#     print(f"stdoutNG: {stdoutNG}")
			# if event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
			#     print(f"GOT STDOUT EVENT!!!")
			#     # # continue
			#     # import sys
			#     # sys.stdout.flush()
			#     # print("STD OUT EVENT LISTENER!!! (XXX)")
			#     # # sys.stdout.flush()
			#     # stdoutTxt = process.GetSTDOUT(2048)
			#     # # print(SBProcess.GetProcessFromEvent(event))
			#     # print(f"STDOUT IS: {stdoutTxt}")
			#     # self.wdtSystemShell.append_text(stdoutTxt)
			#     # Now that we are done dump the stdout and stderr
			#     # if process.state != eStateStopped:
			#     #     # self.driver.worker.handleDbgCmd(f"process interrupt")
			#     #     process.Stop()
			#     process_stdout = process.GetSTDOUT(1024)
			#     if process_stdout:
			#         print("Process STDOUT:\n%s" % (process_stdout))
			#         while process_stdout:
			#             process_stdout = process.GetSTDOUT(1024)
			#             print(process_stdout)
			# else:
			if process.state == lldb.eStateStepping or process.state == lldb.eStateRunning:
				logDbgC(f"if process.state == eStateStepping or process.state == eStateRunning: ...")
				state = 'running'
			elif process.state == lldb.eStateExited:
				state = 'exited'
				logDbgC(f"self.worker.listener.should_quit = True (4)")
				# self.should_quit = True
			elif process.state == lldb.eStateStopped:
				# isWaiting4Input = self.is_waiting_for_input(process)
				# if isWaiting4Input:
				#     print(f"IS WAITING FOR INPUT: {isWaiting4Input} !!!")
				pass

	def checkLoadModule(self, newModFileSpec, resetNextAddr=True):

		newModName = newModFileSpec.GetFilename()
		newModPath = newModFileSpec.fullpath

		if not newModName in self.wdtDisassembly.disassemblies:
			logDbgC(
				f"if self.wdtDisassembly.disassemblies[{newModName}] IS None: ====>>>> NEED TO INITIALIZE AND LOAD MODULE !!!")

			self.driver.debugger.SetAsync(False)
			# target = self.driver.debugger.GetSelectedTarget()
			# process = target.GetProcess()
			# thread = process.GetSelectedThread()

			# # Print stack trace
			# print(f"Stack trace for thread #{thread.GetIndexID()}:")
			# for frame in thread:
			# 	print(
			# 		f"  frame #{frame.GetFrameID()}: {frame.GetFunctionName()} at {frame.GetLineEntry().GetFileSpec().GetFilename()}: {frame.GetLineEntry().GetLine()}")

			# self.driver.worker.disassembleModule(newModName)
			# self.wdtDisassembly.lastModuleKey = None  # Add this to your class init or setup
			# self.wdtDisassembly.lastSymbolKey = None
			# self.wdtDisassembly.lastSubSymbolKey = None

			self.wdtDisassembly.resetContent()
			# if not self.moduleLoaded:
			self.driver.worker.disassembleModule(newModPath)
			self.moduleLoaded = True
			return
		else:
			logDbgC(f"Module already loaded => newModName: {newModName} @{self.treBreakpoints.treBP.nextViewAddress} ...")
			bChanged = self.wdtFiles.select_module(newModName, False)
			if self.treBreakpoints.treBP.nextViewAddress:
				self.wdtDisassembly.tblDisassembly.viewAddress(self.treBreakpoints.treBP.nextViewAddress)
				# if resetNextAddr:
				self.treBreakpoints.treBP.nextViewAddress = None

	def setPC(self, pc_address, pushLocation=False):
		# self.wdtDisassembly.setPC(pc_address, pushLocation)
		# self.treBreakpoints.updateBreakpointValues(bp)
		self.treBreakpoints.setPC(pc_address)
		return self.wdtDisassembly.setPC(pc_address, pushLocation)

	def clearPC(self):
		self.wdtDisassembly.clearPC()
		self.treBreakpoints.clearPC()

	# def disassemble_dylib(debugger, command, result, internal_dict):
	def disassemble_dylib(self, dylib_path="/usr/lib/system/libsystem_c.dylib"):
		# Load the dylib as a target
		# dylib_path = "/usr/lib/system/libsystem_c.dylib"
		# self.window().start_loadDisassemblyWorkerNG(dylib_path, True)
		self.driver.worker.loadRegister()
		self.driver.worker.loadSourcecode()
		pass

	def readSTDOUT(self, proc):
		# QApplication.processEvents()
		# proc.GetTarget().debugger.SetAsync(False)
		# QApplication.processEvents()
		stdout = proc.GetSTDOUT(1024)
		# print(f"proc.GetSTDOUT(1024): {stdout}")
		result_string = ""
		if stdout is not None and len(stdout) > 0:
			# print(stdout)
			message = {"status": "event", "type": "stdout", "output": "".join(["%02x" % ord(i) for i in stdout])}
			print(message)
			print(f"message: {message}")
			byte_values = bytes.fromhex("".join(["%02x" % ord(i) for i in stdout]))
			print(f"byte_values: {byte_values}")
			result_string = byte_values.decode('utf-8')
			print(f"result_string: {result_string}")
			# logDbg(f"Reading STDOUT after Event: {result_string}")
		# proc.GetTarget().debugger.SetAsync(True)
		# QApplication.processEvents()
		# proc.GetTarget().debugger.SetAsync(True)
		return result_string

	def handle_loadRegister(self, type):
		tabDet = QWidget()
		tabDet.setContentsMargins(0, 0, 0, 0)
		print(f"self.driver: {self.driver} ... ")
		tblReg = RegisterTableWidget(self.driver, type)
		tabDet.tblWdgt = tblReg
		self.tblRegs.append(tblReg)
		tabDet.setLayout(QVBoxLayout())
		tabDet.layout().addWidget(tblReg)
		tabDet.layout().setContentsMargins(0, 0, 0, 0)
		self.tabWidgetReg.addTab(tabDet, type)
		self.currTblDet = tblReg
		if self.rflagsLoaded == 2:
			# self.rflagsLoaded = not self.rflagsLoaded
			self.rflagsLoaded = 0
			self.handle_loadRFlags()
			return
		self.rflagsLoaded += 1
		# QApplication.processEvents()

	def handle_loadRFlags(self):
		logDbgC(f"handle_loadRFlags")
		tblReg2 = RFlagWidget(parent=None, driver=self.driver)
		self.tblRegs.insert(0, tblReg2.tblRFlag)
		self.tabWidgetReg.insertTab(0, tblReg2, "rFlags/eFlags")
		self.tabWidgetReg.setTabText(0, f"CPSR/Flags")

	def handle_loadRegisterValue(self, idx, type, register, value):
		self.currTblDet.addRow(type, register, value)
		QApplication.processEvents()

	def handle_updateRegisterValue(self, idx, type, register, value):
		# logDbgC(f"handle_updateRegisterValue({idx}, {type}, {registers}, {value}) ...")
		tblWdgt = self.tabWidgetReg.widget(idx).tblWdgt
		for i in range(tblWdgt.rowCount()):
			if tblWdgt.item(i, 0).text() == type:
				if tblWdgt.item(i, 1).text() != register:
					tblWdgt.suspendChangeHandler = True
					tblWdgt.item(i, 1).setText(register)
					tblWdgt.item(i, 2).setText(value)
					tblWdgt.setRedDelegate(i)
					tblWdgt.suspendChangeHandler = False
				break

	def handle_loadVariableValue(self, name, value, data, valType, address):
		self.tblVariables.addRow(name, value, valType, address, data)

	def handle_updateVariableValue(self, name, value, data, valType, address):
		# if self.isAttached:
		#     self.tblVariables.updateOrAddRow(name, value, valType, address, data)
		# else:
		self.tblVariables.updateRow(name, value, valType, address, data)

	def handle_workerFinished2(self, connections=[], moduleName="<no name>",
							   allSymbols=[]):  # , instructions={}, newPC=0x0):
		# TESET
		# self.driver.projectData.addModule(moduleName)

		# if connections:
		# 	print(f"handle_workerFinished2 => moduleName: {moduleName} / len(connections): {len(connections)} ...")
		# self.setDbgTabLbl(f"{moduleName}")
		self.spinnerDialog.close()
		# bFound = self.wdtDisassembly.setPC(self.driver.getPC(), True)
		bFound = self.setPC(self.driver.getPC(), True)
		# if connections:
		# 	print(
		# 		f"len(connections): {len(connections)} / moduleName: {moduleName} / connections: {connections}  (2) ...")
		if connections is not None and connections != [] and len(
				connections) > 0:  # and len(self.wdtDisassembly.disassemblies[moduleName]["connections"]) <= 0:
			# print(f"connections: {connections} / moduleName: {moduleName} ...")
			logDbgC(f"Setting connections (2) ...")
			# self.wdtDisassembly.disassemblies[moduleName]["connections"] = connections
			# # self.wdtDisassembly.wdtControlFlow.draw_invisibleHeight()
			# self.wdtDisassembly.wdtControlFlow.loadConnectionsFromWorker(connections)
			self.wdtDisassembly.handle_workerFinished(connections, moduleName, {}, 0x0, True)
		if allSymbols != [] and len(allSymbols) > 0:
			self.wdtDisassembly.disassemblies[moduleName]["symbols"] = allSymbols
			self.wdtDisassembly.wdtFunctionList.resetContent()
			# print(allSymbols)
			for symbol in allSymbols:
				# for key, value in symbol.items():
				# print(f"key: {symbol.get('symbol')} / value: {hex(symbol.get('row'))} / {symbol.get('row')} ...")
				self.wdtDisassembly.wdtFunctionList.addSymbol(symbol.get('symbol'), symbol.get('row'))
		# logDbgC(f"self.driver.getPC(): {self.driver.getPC()} (Found: {bFound}) ...")
		self.get_breakpoints_for_module(self.driver.target, moduleName)

		# HERE GOES VIEWADDRESS
		if self.treBreakpoints.treBP.nextViewAddress:
			logDbgC(f"self.treBreakpoints.treBP.nextViewAddress: {self.treBreakpoints.treBP.nextViewAddress} ...")
			self.wdtDisassembly.tblDisassembly.viewAddress(self.treBreakpoints.treBP.nextViewAddress)
			self.treBreakpoints.treBP.nextViewAddress = None

	def handle_workerFinished(self, connections=[], moduleName="<no name>", instructions={}, newPC=0x0, allSymbols=[]):
		self.modulesAndInstructions = instructions
		print(f"len(connections): {len(connections)} / moduleName: {moduleName} / connections: {connections} (3) ...")
		if connections != [] and (len(connections) > 0):
			self.wdtDisassembly.disassemblies[moduleName]["connections"] = connections
			logDbgC(f"Setting connections (3) ...")
			print(f"self.wdtDisassembly.disassemblies[moduleName]: {self.wdtDisassembly.disassemblies[moduleName]} ...")
			# self.wdtDisassembly.wdtControlFlow.draw_invisibleHeight()

			self.wdtDisassembly.wdtControlFlow.loadConnectionsFromWorker(connections)
		if allSymbols != [] and (len(allSymbols) > 0):
			self.wdtDisassembly.disassemblies[moduleName]["symbols"] = allSymbols
			self.wdtDisassembly.wdtFunctionList.resetContent()
			print(allSymbols)
			for symbol in allSymbols:
				# for key, value in symbol.items():
				print(f"key: {symbol.get('symbol')} / value: {hex(symbol.get('row'))} / {symbol.get('row')} ...")
				self.wdtDisassembly.wdtFunctionList.addSymbol(symbol.get('symbol'), symbol.get('row'))

		pcNG = self.driver.worker.main_oep
		# logDbgC(f"self.driver.getPC() (int): {pcNG} ...")
		# logDbgC(f"self.driver.getPC() (hex): {hex(pcNG)} ...")
		# self.wdtDisassembly.setPC(hex(pcNG), True)
		self.setPC(hex(pcNG), True)
		self.treThreads.loadStacktrace()
		# self.setDbgTabLbl(f"{moduleName}")
		self.spinnerDialog.close()

		self.devHelper.loadStartup()

	def setDbgTabLbl(self):
		self.tabWidgetMain.setTabText(self.idxDbgTab, f"Disassembly")

	@pyqtSlot(object, object)
	def loadModulesCallback(self, frame, modules=None):
		self.tabWidgetStruct.loadModulesCallback(frame, modules)
		self.tabWidgetFileInfos.tabWidgetStruct.loadModulesCallback(frame, modules)
		if frame.GetModule().GetFileSpec().GetFilename() == self.driver.target.GetExecutable().GetFilename():
			self.wdtFiles.loadModulesCallback(frame, [frame.GetModule()])

	@pyqtSlot(object)
	def loadModulesCallback2(self, module):
		idxFound = -1
		for i in range(self.wdtFiles.cmbFiles.count()):
			if self.wdtFiles.cmbFiles.itemText(i).startswith(module.GetFileSpec().GetFilename()):
				idxFound = i
				break
		if idxFound == -1:
			self.wdtFiles.cmbFiles.addItem(
				module.GetFileSpec().GetFilename() + " (" + str(self.wdtFiles.cmbFiles.count()) + ")")
			idxFound = self.wdtFiles.cmbFiles.count() - 1

		self.wdtFiles.cmbFiles.setCurrentIndex(idxFound)
		self.wdtDisassembly.handle_loadModule(module.GetFileSpec().GetFilename())

	def show_spinnerDialog(self):
		self.spinnerDialog = SpinnerDialog()
		self.spinnerDialog.show()

	def loadingFinished(self):
		self.spinnerDialog.close()
		self.statusBarManager.setStatusMsg(f"Successfully loaded target: {self.driver.worker.getTargetFilename()}",
										   3500)
		self.setWinTitleWithState(f"Target loaded")
		self.get_breakpoints_for_module(self.driver.worker.target, self.driver.worker.getTargetFilename())

		filename = os.path.basename(ConfigClass.testTarget)
		self.window().wdtFiles.select_module(filename, False)

		self.bpMgr.addBPByName("buttonClicked")

	def viewMemoryAtAddress(self, addr):
		self.wdtDisassembly.tblDisassembly.viewAddress(addr)

	def updateStatusBar(self, msg, timeoutMs=2500):
		self.statusBarManager.setStatusMsg(msg, timeoutMs)

	@pyqtSlot(float, str)
	def sendProgressUpdate(self, prg, msg):
		self.statusBarManager.setProgress(prg)
		self.statusBarManager.setStatusMsg(msg)

	def handle_tabWidgetMainCurrentChanged(self, idx):
		if idx == self.idxConsolesTab:
			self.wdtLLDBCmd.focusTxtCmd()

	def handle_showSettings(self):
		settingsWindow = SettingsDialog(self.setHelper)
		if settingsWindow.exec():
			# self.tblHex.cmbGrouping.setCurrentIndex(self.setHelper.getValue(SettingsValues.HexGrouping))
			# self.tmrResetStatusBar.setInterval(int(self.setHelper.getValue(SettingsValues.StatusBarMsgTimeout)))
			pass

	def handle_loadTarget(self):
		# logDbgC(f"handle_loadTarget() ...")
		# self.driver.stopWorker()
		self.wdtDisassembly.disassemblies = {}
		self.wdtDisassembly.resetContent()
		self.tblRegs.clear()
		self.tabWidgetReg.clear()
		# if "/" in ConfigClass.testTarget:
		#     print(f"STRING HAS SLASH!!!!!")
		# last_part = ConfigClass.testTarget.rsplit("/", 1)[-1]
		self.menuToolbarManager.add_recent_file(ConfigClass.testTarget)
		self.driver.loadTarget(ConfigClass.testTarget,
							   ConfigClass.testTargetArch)  # , ConfigClass.testTargetTriple) # "./_testtarget/hello_library_exec", "ARM64")
		# QApplication.processEvents()

	def handle_attachToPID(self):
		if self.driver.isWorkerRunning():
			if self.driver.stopWorker():
				self.tabWidgetFileInfos.resetContent()
				self.wdtFiles.resetContent()

	def handle_close_clicked(self):
		self.close()

	def closeEvent(self, event):

		if self.driver.isWorkerRunning() and bool(self.setHelper.getValue(SettingsValues.ConfirmDetachOnQuit)):
			dlg = ConfirmDialog("Target running - QUIT?",
								f"{APP_NAME} is still attached to a process. If you quit now, the attached process will aborted as well. Do you really want to quit {APP_NAME} and target now?",
								"Detach")
			if dlg.exec() and dlg.button_clicked == QDialogButtonBox.StandardButton.Ok:
				pass
			else:
				if dlg.button_clicked == QDialogButtonBox.StandardButton.Abort:  # Detach clicked
					pass
				else:
					logDbgC(f"if dlg.button_clicked == QDialogButtonBox.StandardButton.Cancel ...")
					event.ignore()
					return

		global mainWindowNG
		mainWindowNG = None

		if self.setHelper.getValue(SettingsValues.SaveWindowStateOnExit):
			self.saveAllGeometryAndState()

		if self.driver.isWorkerRunning():
			self.driver.stopWorker()

		# 1. Terminate any running process/target
		if self.driver.target and self.driver.target.IsValid():
			process = self.driver.target.GetProcess()
			if process and process.IsValid():
				print("Terminating lldb process...")
				process.Kill()
				# Or process.Detach() if appropriate

		event.accept()
		# super().closeEvent(event)

	def setWinTitleWithState(self, state):
		self.setWindowTitle(
			APP_NAME + " " + APP_VERSION + " - " + os.path.basename(
				FileInfos.getTargetFilename(self.driver.target)) + " - " + state)

	def restoreStateAndGeometry(self, loadAllState=False):
		size = self.setHelper.getValue(SettingsValues.WindowSize)  # , QSize(800, 600)
		if isinstance(size, QSize):
			self.resize(size)

		if loadAllState:
			self.restoreAllWindowAndControlStates()

	def resizeEvent(self, event):
		self.setHelper.setValue(SettingsValues.WindowSize, self.size())
		super().resizeEvent(event)

	def start_loadDisassemblyWorkerNG(self, modulePath, initTable=True):
		self.instCnt = 1
		if initTable:
			self.wdtDisassembly.resetContent()

if __name__ == "__main__":
	MainWindow()