#!/usr/bin/env python3
from enum import Enum

import lldb
from PyQt6.QtCore import QObject, pyqtSignal


# from PyQt6.QtCore import *
#
#
# class BaseWorkerReceiver(QObject):
#     interruptWorker = pyqtSignal()
#
#
# class BaseWorkerSignals(QObject):
#     finished = pyqtSignal()
#     sendStatusBarUpdate = pyqtSignal(str)
#     sendProgressUpdate = pyqtSignal(int, str)

class SubWorkerType(Enum):
	BASE_SUBWORKER = 1
	LOAD_REGISTER_SUBWORKER = 4
	LOAD_FILEINFOS_SUBWORKER = 5
	LOAD_FILESTATS_SUBWORKER = 6
	LOAD_SOURCECODE_SUBWORKER = 7
	ANALYZE_COMPLETE_FILE_SUBWORKER = 8
	DECOMPILE_MODULE_SUBWORKER = 9


class SubWorkerCommands(Enum):
	IDLE_CMD = 0
	INTERRUPT_DBG_SUBWORKER_CMD = 1
	RESUME_DBG_SUBWORKER_CMD = 2
	STEP_OVER_DBG_SUBWORKER_CMD = 3
	STEP_INTO_DBG_SUBWORKER_CMD = 4
	STEP_OUT_DBG_SUBWORKER_CMD = 5
	LOAD_REGISTER_SUBWORKER_CMD = 10
	LOAD_FILEINFOS_SUBWORKER_CMD = 11
	LOAD_FILESTATS_SUBWORKER_CMD = 12
	LOAD_SOURCECODE_SUBWORKER_CMD = 13
	ANALYZE_COMPLETE_FILE_SUBWORKER_CMD = 14
	DECOMPILE_MODULE_SUBWORKER_CMD = 15


class BaseSubWorker(QObject):
	logDbgC = pyqtSignal(str, object)
	sendProgressUpdate = pyqtSignal(float, str)
	sendProgress = pyqtSignal(int)

	driver = None
	isRunning = False

	target = None
	process = None
	thread = None
	frame = None

	subwkrType = SubWorkerType.BASE_SUBWORKER
	subwkrCmds = {SubWorkerCommands.IDLE_CMD: None}

	def __init__(self, driver):
		super().__init__()

		self.driver = driver

	def canExecCmd(self, cmd):
		return cmd in self.subwkrCmds.keys()

	def execCmd(self, cmd, *argv, **args):
		if self.canExecCmd(cmd):
			# func = self.subwkrCmds[cmd]
			self.subwkrCmds[cmd](*argv, **args)

	# def execCmd(self, cmd, *argv, **args):
	#     if self.canExecCmd(cmd):
	#         for cmdKey, cmdValue in self.subwkrCmds.items():
	#             if cmdKey == cmd:
	#                 cmdValue(*argv, **args)
	#                 break
	#         pass
	#     pass

	def initSubWorker(self, driver=None):
		if driver:
			self.driver = driver
		self.target = self.driver.target
		self.process = self.driver.process
		self.thread = self.driver.thread
		# self.frame = self.thread.GetFrameAtIndex(0)

	def runSubWorker(self, driver, *argv, **args):
		# if driver:
		self.initSubWorker(driver)
