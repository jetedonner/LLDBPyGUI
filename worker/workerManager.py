#!/usr/bin/env python3

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6 import uic, QtWidgets, QtCore

from worker.loadDisassemblyWorker import *
from worker.loadDisassemblyWorkerNG import LoadDisassemblyWorkerNG
from worker.loadRegisterWorker import *
from worker.loadBreakpointsWorker import *
from worker.loadWatchpointsWorker import *
from worker.execCommandWorker import *
from worker.debugWorker import *
from worker.loadSourceWorker import *

class WorkerManager(QObject):
	
	driver = None
	threadpool = None
	workerDebug = None
	
	def __init__(self, driver):
		super().__init__()
		self.driver = driver
		self.threadpool = QThreadPool()
	
	
	def start_debugWorker(self, driver, kind, handle_debugStepCompleted):
		if self.workerDebug == None or not self.workerDebug.isRunning:
#			self.setResumeActionIcon(ConfigClass.iconPause)
			self.workerDebug = DebugWorker(driver, kind)
			self.workerDebug.signals.debugStepCompleted.connect(handle_debugStepCompleted)
#			self.workerDebug.signals.setPC.connect(self.handle_debugSetPC)
			
			self.threadpool.start(self.workerDebug)
			print(f"After self.threadpool.start(self.workerDebug)")
			return True
		else:
			return False
			
	def start_loadDisassemblyWorker(self, handle_loadInstruction, handle_workerFinished, initTable = True):
		self.loadDisassemblyWorker = LoadDisassemblyWorker(self.driver, initTable)
		self.loadDisassemblyWorker.signals.finished.connect(handle_workerFinished)
#		self.loadDisassemblyWorker.signals.sendStatusBarUpdate.connect(self.handle_statusBarUpdate)
#		self.loadDisassemblyWorker.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
		self.loadDisassemblyWorker.signals.loadInstruction.connect(handle_loadInstruction)
		self.threadpool.start(self.loadDisassemblyWorker)

	def start_loadDisassemblyWorkerNG(self, show_dialog,  handle_loadSymbol, handle_loadInstruction, handle_workerFinished, modulePath, initTable=True):
		self.loadDisassemblyWorkerNG = LoadDisassemblyWorkerNG(self.driver, modulePath, initTable)
		self.loadDisassemblyWorkerNG.signals.show_dialog.connect(show_dialog)
		self.loadDisassemblyWorkerNG.signals.finishedLoadModuleCallback.connect(handle_workerFinished)
		#		self.loadDisassemblyWorker.signals.sendStatusBarUpdate.connect(self.handle_statusBarUpdate)
		#		self.loadDisassemblyWorker.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
		self.loadDisassemblyWorkerNG.signals.loadInstruction.connect(handle_loadInstruction)
		self.loadDisassemblyWorkerNG.signals.loadSymbolCallback.connect(handle_loadSymbol)
		self.threadpool.start(self.loadDisassemblyWorkerNG)
		logDbgC(f"self.threadpool.start(self.loadDisassemblyWorkerNG)")
		
	def start_loadRegisterWorker(self, handle_loadRegister, handle_loadRegisterValue, handle_updateRegisterValue, handle_loadVariableValue, handle_updateVariableValue, handle_workerFinished, initTabs = True):
		self.loadRegisterWorker = LoadRegisterWorker(self.driver, initTabs)
		self.loadRegisterWorker.signals.finished.connect(handle_workerFinished)
#		self.loadRegisterWorker.signals.sendStatusBarUpdate.connect(handle_statusBarUpdate)
#		self.loadRegisterWorker.signals.sendProgressUpdate.connect(handle_progressUpdate)
		
		self.loadRegisterWorker.signals.loadRegister.connect(handle_loadRegister)
		self.loadRegisterWorker.signals.loadRegisterValue.connect(handle_loadRegisterValue)
		self.loadRegisterWorker.signals.updateRegisterValue.connect(handle_updateRegisterValue)
		
		self.loadRegisterWorker.signals.loadVariableValue.connect(handle_loadVariableValue)
		self.loadRegisterWorker.signals.updateVariableValue.connect(handle_updateVariableValue)
		self.threadpool.start(self.loadRegisterWorker)
		
	def start_loadBreakpointsWorker(self, handle_loadBreakpointsFinished, handle_loadBreakpointValue, handle_updateBreakpointValue, initTable = True):
		self.loadBreakpointsWorker = LoadBreakpointsWorker(self.driver, initTable)
		self.loadBreakpointsWorker.signals.finished.connect(handle_loadBreakpointsFinished)
#		self.loadBreakpointsWorker.signals.sendStatusBarUpdate.connect(self.handle_statusBarUpdate)
#		self.loadBreakpointsWorker.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
		self.loadBreakpointsWorker.signals.loadBreakpointsValue.connect(handle_loadBreakpointValue)
		self.loadBreakpointsWorker.signals.updateBreakpointsValue.connect(handle_updateBreakpointValue)
#		self.loadBreakpointsWorker.signals.loadWatchpointsValue.connect(self.handle_loadWatchpointsLoadBreakpointValue)
#		self.loadBreakpointsWorker.signals.updateWatchpointsValue.connect(self.handle_updateWatchpointsLoadBreakpointValue)
		self.threadpool.start(self.loadBreakpointsWorker)
		
	def start_loadWatchpointsWorker(self, handle_loadWatchpointsFinished, handle_loadWatchpointValue, handle_updateWatchpointValue, initTable = True):
		self.loadWatchpointsWorker = LoadWatchpointsWorker(self.driver, initTable)
		self.loadWatchpointsWorker.signals.finished.connect(handle_loadWatchpointsFinished)
		#		self.loadWatchpointsWorker.signals.sendStatusBarUpdate.connect(self.handle_statusBarUpdate)
		#		self.loadWatchpointsWorker.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
		self.loadWatchpointsWorker.signals.loadWatchpointsValue.connect(handle_loadWatchpointValue)
		self.loadWatchpointsWorker.signals.updateWatchpointsValue.connect(handle_updateWatchpointValue)
#			self.loadWatchpointsWorker.signals.loadWatchpointsValue.connect(handle_loadWatchpointValue)
#			self.loadWatchpointsWorker.signals.updateWatchpointsValue.connect(handle_updateWatchpointValue)
		self.threadpool.start(self.loadWatchpointsWorker)
		
		
	def start_execCommandWorker(self, command, handle_commandFinished):
		self.workerExecCommand = ExecCommandWorker(self.driver, command)
		self.workerExecCommand.signals.commandCompleted.connect(handle_commandFinished)
		self.threadpool.start(self.workerExecCommand)
		
	def start_loadSourceWorker(self, debugger, sourceFile, handle_loadSourceFinished, lineNum = 1):
		print(f"start_loadSourceWorker({sourceFile})")
		self.workerLoadSource = LoadSourceCodeWorker(debugger, sourceFile, lineNum)
		self.workerLoadSource.signals.finished.connect(handle_loadSourceFinished)
		
		self.threadpool.start(self.workerLoadSource)