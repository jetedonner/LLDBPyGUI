#!/usr/bin/env python3

import lldb
from lldb import *
import sys
from threading import Thread

import sys
import os
import subprocess
from sys import stdin, stdout
from threading import Thread

from PyQt6.QtCore import *
from PyQt6 import *

class LLDBListener(QtCore.QObject, Thread):
	
	should_quit = False
	
	gotEvent = pyqtSignal(object)
	
	processEvent = pyqtSignal(object)
	breakpointEvent = pyqtSignal(object)
	stdoutEvent = pyqtSignal(object)
	
	def __init__(self, process, debugger):
		super(LLDBListener, self).__init__()
		Thread.__init__(self)
		print('INITING LISTENER!!!!')
		self.listener = lldb.SBListener('Chrome Dev Tools Listener')
		self.process = process
		self.debugger = debugger
		
	def addListenerCalls(self):
		self._add_listener_to_process(self.process)
		self._broadcast_process_state(self.process)
		self._add_listener_to_target(self.process.target)
		self._add_commandline_interpreter(self.debugger)
		
	def _add_commandline_interpreter(self, debugger):
		broadcaster = debugger.GetCommandInterpreter().GetBroadcaster()
		mask = SBCommandInterpreter.eBroadcastBitAsynchronousErrorData | SBCommandInterpreter.eBroadcastBitAsynchronousOutputData | SBCommandInterpreter.eBroadcastBitQuitCommandReceived | SBCommandInterpreter.eBroadcastBitResetPrompt | SBCommandInterpreter.eBroadcastBitThreadShouldExit
		broadcaster.AddListener(self.listener, mask)
		self.listener.StartListeningForEventClass(self.debugger,
			lldb.SBCommandInterpreter.GetBroadcasterClass(),
			lldb.SBCommandInterpreter.eBroadcastBitThreadShouldExit
			| lldb.SBCommandInterpreter.eBroadcastBitResetPrompt
			| lldb.SBCommandInterpreter.eBroadcastBitQuitCommandReceived
			| lldb.SBCommandInterpreter.eBroadcastBitAsynchronousOutputData
			| lldb.SBCommandInterpreter.eBroadcastBitAsynchronousErrorData
		)
		pass
		
	def _add_listener_to_target(self, target):
		# Listen for breakpoint/watchpoint events (Added/Removed/Disabled/etc).
		broadcaster = target.GetBroadcaster()
		mask = SBTarget.eBroadcastBitBreakpointChanged | SBTarget.eBroadcastBitWatchpointChanged | SBTarget.eBroadcastBitModulesLoaded | SBThread.eBroadcastBitThreadSuspended 
		broadcaster.AddListener(self.listener, mask)
		
	def _add_listener_to_process(self, process):
		# Listen for process events (Start/Stop/Interrupt/etc).
		broadcaster = process.GetBroadcaster()
		mask = SBProcess.eBroadcastBitStateChanged | SBProcess.eBroadcastBitSTDOUT
		broadcaster.AddListener(self.listener, mask)
		
	def _broadcast_process_state(self, process, event = None):
		state = 'stopped'
		if process.state == eStateStepping or process.state == eStateRunning:
			state = 'running'
		elif process.state == eStateExited:
			state = 'exited'
			self.should_quit = True
		thread = process.selected_thread
		print('Process event: %s, reason: %d' % (state, thread.GetStopReason()))
		if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
			print(f'REASON BP RFEACHED (listener) Event: {event} => Continuing...')
			self.suspended = True
		elif thread.GetStopReason() == lldb.eStopReasonWatchpoint:
			print(f'REASON WATCHPOINT RFEACHED (listener) Event: {event} => Continuing...')
#			pass
			
		print(f"======================== IN HEA ========================")
		self.processEvent.emit(process)
		QCoreApplication.processEvents()
		print(f"====================== IN HEA END ======================")
		
#		if event != None and event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
#			print("STD OUT EVENT LISTENER!!!")
#			stdout = SBProcess.GetProcessFromEvent(event).GetSTDOUT(256)
#			print(SBProcess.GetProcessFromEvent(event))
#			print(stdout)
#			if stdout is not None and len(stdout) > 0:
#				message = {"status":"event", "type":"stdout", "output": "".join(["%02x" % ord(i) for i in stdout])}
#				print(message)
#				print("".join(["%02x" % ord(i) for i in stdout]))
##				self.stdoutEvent.emit("".join(["%02x" % ord(i) for i in stdout]))
##             self.signals.event_output.emit("".join(["%02x" % ord(i) for i in stdout]))
#				QCoreApplication.processEvents()
				
#			self.breakpointEvent.emit(event)
#     error = lldb.SBError()
#     thread.Resume(error)
#     process.Continue()
			
			
			
			
	def _breakpoint_event(self, event):
		print(f"_breakpoint_event")
		breakpoint = SBBreakpoint.GetBreakpointFromEvent(event)
		bpEventType = SBBreakpoint.GetBreakpointEventTypeFromEvent(event)
		self.breakpointEvent.emit(event)
		QCoreApplication.processEvents()
#		print(event)
#		print(f'EVENTTYPE: {SBBreakpoint.GetBreakpointEventTypeFromEvent(event)}')
#		print(dir(event))
#		print(breakpoint)
#		print(dir(breakpoint))
#		print(f'==========>>>>>>>> ISENABLED: {breakpoint.IsEnabled()}')
#		print('Breakpoint event: %s' % str(breakpoint))
		
	suspended = False
	def run(self):
		print('STARTING LISTENER!!!!')
		while not self.should_quit:
			event = SBEvent()
			print("GOING to WAIT 4 EVENT...")
			if self.listener.WaitForEvent(lldb.UINT32_MAX, event):
				self.gotEvent.emit(event)
				print("GOT NEW EVENT LISTENER!!")
				if SBCommandInterpreter.EventIsCommandInterpreterEvent(event):
					print("GOT COMMANDLINE EVENT!!!")
				elif event.GetType() == SBThread.eBroadcastBitThreadSuspended:
					print('THREAD SUSPENDED: %s' % str(event))
				elif event.GetType() == SBThread.eBroadcastBitThreadResumed:
					print("RESUMED!!")
					if self.suspended:
						print("RESUMED AFTER BP!!")
						self.suspended = False
				elif event.GetType() == SBTarget.eBroadcastBitModulesLoaded:
					print('Module load: %s' % str(event))
					
				
#				elif event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
#					print("STD OUT EVENT LISTENER!!!")
#					stdout = SBProcess.GetProcessFromEvent(event).GetSTDOUT(256)
#					print(SBProcess.GetProcessFromEvent(event))
#					print(stdout)
#					if stdout is not None and len(stdout) > 0:
#						message = {"status":"event", "type":"stdout", "output": "".join(["%02x" % ord(i) for i in stdout])}
#						print(message)
#						print("".join(["%02x" % ord(i) for i in stdout]))
#						self.stdoutEvent.emit("".join(["%02x" % ord(i) for i in stdout]))
##             self.signals.event_output.emit("".join(["%02x" % ord(i) for i in stdout]))
#						QCoreApplication.processEvents()
				elif SBProcess.EventIsProcessEvent(event):
					self._broadcast_process_state(SBProcess.GetProcessFromEvent(event), event)
#					self.processEvent.emit(SBProcess.GetProcessFromEvent(event))
#					QCoreApplication.processEvents()
					print("STD OUT EVENT ALT!!!")
				elif SBBreakpoint.EventIsBreakpointEvent(event):
					print("GOT BREAKPOINT EVENT YESSSSS!!!")
					self._breakpoint_event(event)
				elif event.GetType() == lldb.SBTarget.eBroadcastBitWatchpointChanged:
					wp = lldb.SBWatchpoint.GetWatchpointFromEvent(event)
					print(f"WATCHPOINT CHANGED!!!! => {wp}")
				else:
					print("OTHER EVENT!!!!")
		print("END LISTENER!!!")