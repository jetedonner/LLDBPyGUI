#!/usr/bin/env python3

import lldb

from worker.baseWorker import *

interruptExecCommand = False


# class ExecCommandReceiver(BaseWorkerSignals):
#	interruptExecCommand = pyqtSignal()

class ExecCommandWorkerSignals(BaseWorkerSignals):
	commandCompleted = pyqtSignal(object)


class ExecCommandWorker(BaseWorker):
	debugger = None

	def __init__(self, driver, command):
		super(ExecCommandWorker, self).__init__(driver)
		self.isExecCommandActive = False
		self.debugger = driver.debugger
		self.command = command
		self.signals = ExecCommandWorkerSignals()

	def workerFunc(self):
		super(ExecCommandWorker, self).workerFunc()
		res = lldb.SBCommandReturnObject()
		bCurrIsAsync = self.debugger.GetAsync()
		self.debugger.SetAsync(True)
		# Get the command interpreter
		command_interpreter = self.debugger.GetCommandInterpreter()

		# Execute the 'frame variable' command
		command_interpreter.HandleCommand(self.command, res)
		self.isExecCommandActive = False
		self.debugger.SetAsync(bCurrIsAsync)
		self.signals.commandCompleted.emit(res)
		QCoreApplication.processEvents()
