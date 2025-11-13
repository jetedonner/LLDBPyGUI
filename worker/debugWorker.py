#!/usr/bin/env python3
from enum import Enum

import lldb
from lldb import *

from worker.baseWorker import *


# from helper.dbgHelper import *
# class DebugWorkerReceiver(BaseWorkerReceiver):
#	interruptWorker = pyqtSignal()


# import re

class StepKind(Enum):
	StepOver = 1
	StepInto = 2
	StepOut = 4
	Continue = 8


class DebugWorkerSignals(BaseWorkerSignals):
	debugStepCompleted = pyqtSignal(object, bool, str, object)


#	updateRegisterValue = pyqtSignal(int, str, str, str)

class DebugWorker(BaseWorker):
	kind = StepKind.StepOver
	isRunning = False

	def __init__(self, driver, kind):
		super(DebugWorker, self).__init__(driver)
		self.kind = kind
		self.signals = DebugWorkerSignals()

	def workerFunc(self):
		super(DebugWorker, self).workerFunc()
		if not self.isRunning:
			self.isRunning = True
		else:
			return

		self.sendStatusBarUpdate("Debug step ...")
		target = self.driver.target
		process = target.GetProcess()
		if process:
			thread = process.GetThreadAtIndex(0)
			if thread:
				if self.kind == StepKind.StepInto:
					# print("Trying to StepInto ...")
					thread.StepInstruction(False)
				# if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
				# 	print(f'GOT if thread.GetStopReason() == lldb.eStopReasonBreakpoint:')
				# 	self.isRunning = False
				# print("After StepInto ...")
				elif self.kind == StepKind.StepOut:
					# print("Trying to StepOut ...")
					thread.StepOut()
				# if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
				# 	print(f'GOT if thread.GetStopReason() == lldb.eStopReasonBreakpoint:')
				# 	self.isRunning = False
				# # print("After StepOut ...")
				elif self.kind == StepKind.StepOver:
					# print("Trying to StepOver ...")
					thread.StepInstruction(True)
				# print("After StepOver ...")
				#					ID = thread.GetThreadID()
				# 					if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
				# 						print(f'GOT if thread.GetStopReason() == lldb.eStopReasonBreakpoint:')
				# #						print(f'GOT if thread.GetStopReason() == lldb.eStopReasonBreakpoint:')
				# #						frame = thread.GetFrameAtIndex(0)
				# #						self.signals.setPC.emit(frame.registers["rip"].value)
				# #						QCoreApplication.processEvents()
				#
				# #						from lldbutil import print_stacktrace
				# #						print_stacktrace(thread)
				# 						self.isRunning = False
				# #					print("After StepOver ...")
				elif self.kind == StepKind.Continue:
					# print("Trying to Continue ...")
					if thread.IsSuspended():
						# print("thread.IsSuspended() => Trying to Resume ...")
						thread.Resume()
					error = process.Continue()
					# print("After Continue ...")
					if error:
						print(error)

				# if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
				# 	print(f'GOT if thread.GetStopReason() == lldb.eStopReasonBreakpoint:')
				# 	self.isRunning = False
				else:
					# print("Trying to StepOver ...")
					thread.StepInstruction(True)

				# if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
				# 	print(f'GOT if thread.GetStopReason() == lldb.eStopReasonBreakpoint:')
				# 	self.isRunning = False

				if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
					print(f'GOT if thread.GetStopReason() == lldb.eStopReasonBreakpoint:')
					self.isRunning = False

				frame = thread.GetFrameAtIndex(0)
				# pprint(frame)
				# print(f"GOT IT ....")
				if frame:
					registerList = frame.GetRegisters()
					numRegisters = registerList.GetSize()
					# print(f"numRegisters: {numRegisters}")
					if numRegisters > 0:
						rip = ''
						GPRs = frame.registers[0]
						# print('%s (number of children = %d):' % (GPRs.name, GPRs.num_children))
						for reg in GPRs:
							# print('Name: ', reg.name, ' Value: ', reg.value)
							if reg.name == "pc" or reg.name == "rip":
								print(f'GetPCAddress => {reg.value}')
								rip = reg.value
								break
						# print(f"frame.registers['pc']: {rip}")
						if rip:  # frame.registers["rip"]:
							self.signals.debugStepCompleted.emit(self.kind, True, rip, frame)
						else:
							self.signals.debugStepCompleted.emit(self.kind, True, "", frame)
						self.isRunning = False
					else:
						self.signals.debugStepCompleted.emit(self.kind, False, '', frame)
						self.isRunning = False
				else:
					pass
			else:
				pass
		else:
			pass
		#		self.signals.finished.emit()
		self.isRunning = False
#		pass
