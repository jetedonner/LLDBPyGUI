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
from dbg.fileInfos import *

class LLDBListener(QtCore.QObject, Thread):
	
	should_quit = False
	
	gotEvent = pyqtSignal(object)
	
	processEvent = pyqtSignal(object)
	breakpointEvent = pyqtSignal(object)
	stdoutEvent = pyqtSignal(object)
	setHelper = None
	
	def __init__(self, process, debugger):
		super(LLDBListener, self).__init__()
		Thread.__init__(self)
		print('INITING LISTENER!!!!')
		self.listener = lldb.SBListener('LLDBPyGUI event listener')
		self.process = process
		self.debugger = debugger
		
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
		self._broadcast_process_state(self.process)
#		self._add_listener_to_target(self.process.target)
#		self._add_commandline_interpreter(self.debugger)
		self.setHelper.beginReadArray("listener_Target")
		setKey = "lldb.target_eBroadcastBitBreakpointChanged" #SBTarget.eBroadcastBitBreakpointChanged #self.treListener.getKeyForBroadcastBitData([type, bit])
		# print(f"====>> Listener-Config (listener_Target) => Key: {setKey} is: {self.setHelper.getArrayValue(setKey)}")
		if self.setHelper.getArrayValue(setKey) == "true":
			self._add_listener(lldb.SBTarget, lldb.SBTarget.eBroadcastBitBreakpointChanged)
		#subSectionNode.setCheckState(0, Qt.CheckState.Checked if self.setHelper.getArrayValue(setKey) == "true" else Qt.CheckState.Unchecked)
		self.setHelper.endArray()
		pass
		
	def _add_commandline_interpreter(self, debugger):
		if not self.should_quit:
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
		
	def _remove_listener(self, type, bitMask = lldb.SBTarget.eBroadcastBitWatchpointChanged):
		if not self.should_quit:
			# print(f"=====================>>>>>>>>> self.debugger (REMOVE): {self.debugger} / {self.listener}")
			if type == lldb.SBTarget:
				self.listener.StopListeningForEventClass(self.debugger,                                                  lldb.SBTarget.GetBroadcasterClassName(),
					lldb.SBTarget.eBroadcastBitWatchpointChanged
					#| lldb.SBTarget.eBroadcastBitModuleLoaded
					#| lldb.SBTarget.eBroadcastBitModuleUnloaded
					#| lldb.SBTarget.eBroadcastBitWatchpointChanged)
				)

				success = self.debugger.GetSelectedTarget().GetBroadcaster().RemoveListener(self.listener, bitMask)
				# print(f"Removed Listener with {success} (LISTENER)")
			elif type == lldb.SBProcess:
				self.listener.StopListeningForEventClass(self.debugger,                                                  type.GetBroadcasterClassName(),
					bitMask
					#| lldb.SBTarget.eBroadcastBitModuleLoaded
					#| lldb.SBTarget.eBroadcastBitModuleUnloaded
					#| lldb.SBTarget.eBroadcastBitWatchpointChanged)
				)

				success = self.debugger.GetSelectedTarget().GetProcess().GetBroadcaster().RemoveListener(self.listener, bitMask)
				# print(f"Removed Listener with {success} (LISTENER)")
		pass
	
	def _add_listener(self, type, bitMask = lldb.SBTarget.eBroadcastBitWatchpointChanged):
		if not self.should_quit:
			# print(f"=====================>>>>>>>>> self.debugger (ADD): {self.debugger} / {self.listener}")
			if type == lldb.SBTarget:
				self.listener.StartListeningForEventClass(self.debugger,                                                  type.GetBroadcasterClassName(),
						bitMask
						#| lldb.SBTarget.eBroadcastBitModuleLoaded
						#| lldb.SBTarget.eBroadcastBitModuleUnloaded
						#| lldb.SBTarget.eBroadcastBitWatchpointChanged)
					)
	#		bitMask = lldb.SBTarget.eBroadcastBitWatchpointChanged
				success = self.debugger.GetSelectedTarget().GetBroadcaster().AddListener(self.listener, bitMask)
				# print(f"Added Listener with {success} (LISTENER)")
			elif type == lldb.SBProcess:
				self.listener.StartListeningForEventClass(self.debugger,                                                  type.GetBroadcasterClassName(),
					bitMask
					#| lldb.SBTarget.eBroadcastBitModuleLoaded
					#| lldb.SBTarget.eBroadcastBitModuleUnloaded
					#| lldb.SBTarget.eBroadcastBitWatchpointChanged)
				)
				#		bitMask = lldb.SBTarget.eBroadcastBitWatchpointChanged
				success = self.debugger.GetSelectedTarget().GetProcess().GetBroadcaster().AddListener(self.listener, bitMask)
				# print(f"Added Listener with {success} (LISTENER)")
		pass
		
	def _add_listener_to_target(self, target):
		if not self.should_quit:
			# Listen for breakpoint/watchpoint events (Added/Removed/Disabled/etc).
			#  | SBTarget.eBroadcastBitWatchpointChanged
			broadcaster = target.GetBroadcaster()
			mask = SBTarget.eBroadcastBitBreakpointChanged | SBTarget.eBroadcastBitWatchpointChanged | SBTarget.eBroadcastBitModulesLoaded | SBTarget.eBroadcastBitModulesUnloaded | SBTarget.eBroadcastBitSymbolsLoaded #SBThread.eBroadcastBitThreadSuspended
			broadcaster.AddListener(self.listener, mask)
		
	def _add_listener_to_process(self, process):
		if not self.should_quit:
			# Listen for process events (Start/Stop/Interrupt/etc).
			broadcaster = process.GetBroadcaster()
			mask = SBProcess.eBroadcastBitStateChanged | SBProcess.eBroadcastBitSTDOUT
			broadcaster.AddListener(self.listener, mask)
		
	def _broadcast_process_state(self, process, event = None):
		if not self.should_quit:
			print(f"===============>>>>>>>>>>>>>>>> INSIDE _broadcast_process_state")
			state = 'stopped'

			if event is not None and event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
				stdout = process.GetSTDOUT(1024)
				if stdout is not None and len(stdout) > 0:
					print(f"=============>>>>>>>>>>>>>>>>>> NEW STDOUT: {stdout}")
				else:
					print(f"=============>>>>>>>>>>>>>>>>>> NOOOOOOOOO NEW STDOUT!!!!!")
				return
			else:
				print(f"=============>>>>>>>>>>>>>>>>>> NOOOOOOOOO EVENT!!!!!")

			if process.state == eStateStepping or process.state == eStateRunning:
				state = 'running'
			elif process.state == eStateExited:
				state = 'exited'
				self.should_quit = True
			thread = process.selected_thread
			# print('Process event: %s, reason: %d' % (state, thread.GetStopReason()))
			if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
				# print(f'REASON BP RFEACHED (listener) Event: {event} => Continuing...')
				self.suspended = True
			elif thread.GetStopReason() == lldb.eStopReasonWatchpoint:
				# print(f'REASON WATCHPOINT RFEACHED (listener) Event: {event} => Continuing...')
				pass

			# print(f"======================== IN HEA ========================")
			self.processEvent.emit(process)
			QCoreApplication.processEvents()
			# print(f"====================== IN HEA END ======================")

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
		if not self.should_quit:
			# print(f"_breakpoint_event")
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
		logDbgC(f'STARTING LISTENER!!!! ======>>>>>> Is it only ONE TIME?')
		while not self.should_quit:
			event = SBEvent()
			# print("GOING to WAIT 4 EVENT...")
			logDbgC(f"################# ====>>>>> WaitForEvent (1)")
			if self.listener.WaitForEvent(lldb.UINT32_MAX, event):
				if not self.should_quit:
					print("self.gotEvent.emit(event)!!!")
					self.gotEvent.emit(event)
					# print("GOT NEW EVENT LISTENER!!")
					if SBCommandInterpreter.EventIsCommandInterpreterEvent(event):
						print("GOT COMMANDLINE EVENT!!!")
					elif event.GetType() == SBThread.eBroadcastBitThreadSuspended:
						print('THREAD SUSPENDED: %s' % str(event))
					elif event.GetType() == SBThread.eBroadcastBitThreadResumed:
						# print("RESUMED!!")
						if self.suspended:
							# print("RESUMED AFTER BP!!")
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
						if event is None:
							print(f"EVEWNT ISSSSSSSSSS NOOOOOOONNNNNNNNEEEEEEE!!!!!!")
						else:
							print((f"EVENT IOS OK!!!!!!!"))
						self._broadcast_process_state(SBProcess.GetProcessFromEvent(event), event)
	#					self.processEvent.emit(SBProcess.GetProcessFromEvent(event))
	#					QCoreApplication.processEvents()
						# print("STD OUT EVENT ALT!!!")
						# pass
					elif SBBreakpoint.EventIsBreakpointEvent(event):
						# print("GOT BREAKPOINT EVENT YESSSSS!!!")
						self._breakpoint_event(event)
					elif event.GetType() == lldb.SBTarget.eBroadcastBitWatchpointChanged:
						wp = lldb.SBWatchpoint.GetWatchpointFromEvent(event)
					else:
						pass
				else:
					break