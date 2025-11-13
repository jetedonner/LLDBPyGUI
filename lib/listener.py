#!/usr/bin/env python3

from threading import Thread

import lldb
from lldb import *

from lib.fileInfos import *


# from lib.fileInfos import BroadcastBitString


class LLDBListener(QObject, Thread):
	should_quit = False

	# gotEvent = pyqtSignal(object)

	processEvent = pyqtSignal(object)
	breakpointEvent = pyqtSignal(object)
	stdoutEvent = pyqtSignal(object)
	setHelper = None

	def __init__(self, process, debugger):
		super(LLDBListener, self).__init__()
		Thread.__init__(self)
		self.listener = lldb.SBListener(f'{APP_NAME} event listener')
		self.process = process
		self.debugger = debugger
		self.target = process.GetTarget()

	def getKeyForBroadcastBitData(self, type, bit):
		if not self.should_quit:
			setKey = ""
			if type != None and bit != None:
				if isinstance(type, str):
					setKey = str(type) + "_" + str(BroadcastBitString(type, bit))
				elif type == lldb.SBCommandInterpreter:
					setKey = str("lldb.commandinterpreter") + "_" + str(BroadcastBitString(type, bit))
				else:
					setKey = str(type.GetBroadcasterClassName()) + "_" + str(BroadcastBitString(type, bit))
			return setKey
		else:
			return ""

	def addListenerCalls(self):
		self._add_listener_to_process(self.process)
		self._add_listener_to_target(self.target)

	def _add_listener_to_target(self, target):
		if not self.should_quit:
			# Listen for breakpoint/watchpoint events (Added/Removed/Disabled/etc).
			#  | SBTarget.eBroadcastBitWatchpointChanged
			broadcaster = target.GetBroadcaster()
			mask = SBTarget.eBroadcastBitBreakpointChanged | SBTarget.eBroadcastBitWatchpointChanged | SBTarget.eBroadcastBitModulesLoaded | SBTarget.eBroadcastBitModulesUnloaded | SBTarget.eBroadcastBitSymbolsLoaded  # SBThread.eBroadcastBitThreadSuspended
			broadcaster.AddListener(self.listener, mask)

	def _add_listener_to_process(self, process):
		# return
		if not self.should_quit:
			# Listen for process events (Start/Stop/Interrupt/etc).
			broadcaster = process.GetBroadcaster()
			mask = SBProcess.eBroadcastBitStateChanged | SBProcess.eBroadcastBitSTDOUT
			broadcaster.AddListener(self.listener, mask)

	suspended = False

	def run(self):
		# return
		# self.logDbgC.emit(f'STARTING LISTENER!!!! ======>>>>>> Is it only ONE TIME?', DebugLevel.Verbose)
		# while not self.should_quit:
		#     sRet = ""
		#     output = self.process.GetSTDOUT(sRet)
		#     if sRet:
		#         print(f"OUTPUT: {output} / {sRet} END!")
		#     # You can also check stderr:
		#     # error = self.process.GetSTDERR()
		#     # if error:
		#     #     self.outputReady.emit(error)
		#     import time
		#     time.sleep(0.1)  # avoid busy loop

		while not self.should_quit:
			event = lldb.SBEvent()
			# print("GOING to WAIT 4 EVENT...")
			# self.logDbgC.emit(f"################# ====>>>>> WaitForEvent (1)", DebugLevel.Verbose)
			result = self.listener.WaitForEvent(lldb.UINT32_MAX, event)
			# print(f"WaitForEvent() => result: {result}")
			# self.logDbgC.emit(f"self.should_quit: {self.should_quit} => result: {result} event: {event}", DebugLevel.Verbose)
			# result and
			if not self.should_quit and event is not None:
				logDbgC(f"GetAsync(): {self.debugger.GetAsync()}")
				# desc = get_description(event)
				# # self.logDbgC.emit(f'GOT-NEW-EVENT: {event}\nEvent data flavor: {event.GetDataFlavor()}\nEvent description: {desc}\n- {event.GetType()} / {lldb.SBProcess.eBroadcastBitSTDOUT} ====>>> OLD LISTENER', DebugLevel.Verbose)
				#
				# # logDbgC(f'Event description: {desc}')
				# # logDbgC(f'Event data flavor: {event.GetDataFlavor()}')
				#
				# # logDbgC(f"self.gotEvent.emit(event)!!!")
				# self.gotEvent.emit(event)
				# # print("GOT NEW EVENT LISTENER!!")
				# proc = lldb.SBProcess.GetProcessFromEvent(event)
				# if event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
				#     proc = lldb.SBProcess.GetProcessFromEvent(event)
				#     # stdoutNG = lldb.SBProcess.GetProcessFromEvent(event).GetSTDOUT(1024)
				#     if proc.GetSelectedThread().Suspend():
				#         stdoutNG = self.readSTDOUT(proc)
				#         print(f"stdoutNG: {stdoutNG} (2)")
				# #         if not self.should_quit and event is not None and stdoutNG is not None and stdoutNG != "":
				# #             # stdoutNG = lldb.SBProcess.GetProcessFromEvent(event).GetSTDOUT(1024)
				# #             stdoutNG = self.readSTDOUT(proc)
				# #             print(f"stdoutNG: {stdoutNG} (3)")
				# #     # event = lldb.SBEvent()
				# #     # result = self.listener.GetNextEvent(event)
				# #     # print(f"WaitForEvent() => GetNextEvent: {result}")
				# #     # if not self.should_quit and event is not None:
				# #     #     stdoutNG = lldb.SBProcess.GetProcessFromEvent(event).GetSTDOUT(1024)
				# #     #     print(f"stdoutNG: {stdoutNG}")
				#
				# #     # continue
				# #     # p (event)
				# #     print("STD OUT EVENT LISTENER!!! (1)")
				# #     sys.stdout.flush()
				# #     stdoutNG = lldb.SBProcess.GetProcessFromEvent(event).GetSTDOUT(2048)
				# #     # print(SBProcess.GetProcessFromEvent(event))
				# #     print(f"############# ===========>>>>>>>>>>>>> stdoutNG IS: {stdoutNG}")
				# #
				# #     continue
				# # elif SBCommandInterpreter.EventIsCommandInterpreterEvent(event):
				# #     print("GOT COMMANDLINE EVENT!!!")
				# # elif event.GetType() == SBThread.eBroadcastBitThreadSuspended:
				# #     print('THREAD SUSPENDED: %s' % str(event))
				# # elif event.GetType() == SBThread.eBroadcastBitThreadResumed:
				# #     # print("RESUMED!!")
				# #     if self.suspended:
				# #         # print("RESUMED AFTER BP!!")
				# #         self.suspended = False
				# # elif event.GetType() == SBTarget.eBroadcastBitModulesLoaded:
				# #     print('Module load: %s' % str(event))
				# # elif event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
				# #     # continue
				# #     print("STD OUT EVENT LISTENER!!! (2)")
				# #     # sys.stdout.flush()
				# #     stdout = SBProcess.GetProcessFromEvent(event).GetSTDOUT(2048)
				# #     print(SBProcess.GetProcessFromEvent(event))
				# #     print(f"STDOUT IS: {stdout}")
				# # #					if stdout is not None and len(stdout) > 0:
				# # #						message = {"status":"event", "type":"stdout", "output": "".join(["%02x" % ord(i) for i in stdout])}
				# # #						print(message)
				# # #						print("".join(["%02x" % ord(i) for i in stdout]))
				# # #						self.stdoutEvent.emit("".join(["%02x" % ord(i) for i in stdout]))
				# # ##             self.signals.event_output.emit("".join(["%02x" % ord(i) for i in stdout]))
				# # #						QCoreApplication.processEvents()
				#
				# # if SBProcess.EventIsProcessEvent(event):
				self.processEvent.emit(event)
				# while self.listener.GetNextEvent(1, event):
				# 	self.processEvent.emit(event)


	def readSTDOUT(self, proc):
		# pass
		stdoutNG = proc.GetSTDOUT(1024)
		# print(f"proc.GetSTDOUT(1024): {stdoutNG}")
		if stdoutNG is not None and len(stdoutNG) > 0:
			# print(stdout)
			message = {"status": "event", "type": "stdout", "output": "".join(["%02x" % ord(i) for i in stdoutNG])}
			print(message)
			print(f"message: {message}")
			byte_values = bytes.fromhex("".join(["%02x" % ord(i) for i in stdoutNG]))
			print(f"byte_values: {byte_values}")
			result_string = byte_values.decode('utf-8')
			print(f"result_string: {result_string}")
			# logDbg(f"Reading STDOUT after Event: {result_string}")
