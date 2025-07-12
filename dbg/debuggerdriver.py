##===-- debuggerdriver.py ------------------------------------*- Python -*-===##
##
# Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
##
##===----------------------------------------------------------------------===##


import lldb
from lldb import *

import sys
import os
from sys import *
from threading import Thread

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6 import uic, QtWidgets, QtCore

from dbg.fileInfos import *
from config import *

class DebuggerDriverSignals(QObject):
    event_queued = QtCore.pyqtSignal(object)
    event_output = QtCore.pyqtSignal(str)
  
class DebuggerDriver(Thread):
    """ Drives the debugger and responds to events. """
    
    aborted = False
    signals = None
    
    def breakpointHandlerDriver(self, dummy, frame, bpno, err):
    #   print(dummy)
    #   print(frame)
    #   print(bpno)
    #   print(err)
        global pymobiledevice3GUIWindow
        pymobiledevice3GUIWindow.bpcp("YESSSSS!!!!!")
    #   print("MLIR debugger attaching...")
    #   print("IIIIIIIIINNNNNNNN CCCCAAQALLLLLLBBBAAACCKKKK")
    
    def __init__(self, debugger, event_queue):
        Thread.__init__(self)
        self.signals = DebuggerDriverSignals()
        self.event_queue = event_queue
        # This is probably not great because it does not give liblldb a chance
        # to clean up
        self.daemon = True
        self.initialize(debugger)

    def initialize(self, debugger):
        # print("INITIALISING DRIVER!!!")
        self.done = False
        self.debugger = debugger
        self.listener = debugger.GetListener()
        if not self.listener.IsValid():
            raise "Invalid listener"

        # print(f"=====================>>>>>>>>> self.debugger (ADD): {self.debugger} / {self.listener}")
        self.listener.StartListeningForEventClass(self.debugger,
                                                  lldb.SBTarget.GetBroadcasterClassName(),
                                                  lldb.SBTarget.eBroadcastBitBreakpointChanged
                                                  #| lldb.SBTarget.eBroadcastBitModuleLoaded
                                                  #| lldb.SBTarget.eBroadcastBitModuleUnloaded
                                                  #| lldb.SBTarget.eBroadcastBitWatchpointChanged
                                                  #| lldb.SBTarget.eBroadcastBitSymbolLoaded
                                                  )

        self.listener.StartListeningForEventClass(self.debugger,
                                                  lldb.SBThread.GetBroadcasterClassName(),
                                                  lldb.SBThread.eBroadcastBitStackChanged
                                                  #  lldb.SBThread.eBroadcastBitBreakpointChanged
                                                  | lldb.SBThread.eBroadcastBitThreadSuspended
                                                  | lldb.SBThread.eBroadcastBitThreadResumed
                                                  | lldb.SBThread.eBroadcastBitSelectedFrameChanged
                                                  | lldb.SBThread.eBroadcastBitThreadSelected
                                                  )

        self.listener.StartListeningForEventClass(self.debugger,
                                                  lldb.SBProcess.GetBroadcasterClassName(),
                                                  lldb.SBProcess.eBroadcastBitStateChanged
                                                  | lldb.SBProcess.eBroadcastBitInterrupt
                                                  | lldb.SBProcess.eBroadcastBitSTDOUT
                                                  | lldb.SBProcess.eBroadcastBitSTDERR
                                                  | lldb.SBProcess.eBroadcastBitProfileData
                                                  )
        self.listener.StartListeningForEventClass(self.debugger,
                                                  lldb.SBCommandInterpreter.GetBroadcasterClass(),
                                                  lldb.SBCommandInterpreter.eBroadcastBitThreadShouldExit
                                                  | lldb.SBCommandInterpreter.eBroadcastBitResetPrompt
                                                  | lldb.SBCommandInterpreter.eBroadcastBitQuitCommandReceived
                                                  | lldb.SBCommandInterpreter.eBroadcastBitAsynchronousOutputData
                                                  | lldb.SBCommandInterpreter.eBroadcastBitAsynchronousErrorData
                                                )
    
    def addListener(self, type = lldb.SBTarget, bitMask = SBTarget.eBroadcastBitWatchpointChanged):
  #		self.target = self.debugger.GetSelectedTarget()
  #		self.process = self.target.GetProcess()
  #		print(f"self.target => {self.target}")
  #		self.broadcasterTarget = self.target.GetBroadcaster()
  #		global bt
  #		self.broadcasterTarget = bt
  #		print(f"self.target => {self.target} / self.process => {self.process} / self.broadcasterTarget => {self.broadcasterTarget}")
  #		self.maskTarget = bitMask # SBTarget.eBroadcastBitBreakpointChanged # | SBTarget.eBroadcastBitWatchpointChanged | SBTarget.eBroadcastBitModulesLoaded | SBThread.eBroadcastBitThreadSuspended 
  #		global lt
  #		self.listenerTarget = lt
      # print(f"==============>>>>>>>>>>>>> ADDING LISTENER: {self.debugger} / {self.listener}")
      self.listener.StopListeningForEventClass(self.debugger,                                                  lldb.SBTarget.GetBroadcasterClassName(),
        lldb.SBTarget.eBroadcastBitBreakpointChanged
        #| lldb.SBTarget.eBroadcastBitModuleLoaded
        #| lldb.SBTarget.eBroadcastBitModuleUnloaded
        | lldb.SBTarget.eBroadcastBitWatchpointChanged)
#     success = self.broadcasterTarget.AddListener(self.listenerTarget, bitMask)
  #		print(f"Added Listener with {success} / self.broadcasterTarget => {self.broadcasterTarget} / self.listenerTarget  => {self.listenerTarget} / self.maskTarget => {self.maskTarget}")
      pass
  
    def removeListener(self, type = lldb.SBTarget, bitMask = SBTarget.eBroadcastBitWatchpointChanged):
  #		self.target = self.debugger.GetSelectedTarget()
  #		self.process = self.target.GetProcess()
  #		print(f"self.target => {self.target}")
  #		self.broadcasterTarget = self.target.GetBroadcaster()
  #		global bt
  #		self.broadcasterTarget = bt
  #		print(f"self.target => {self.target} / self.process => {self.process} / self.broadcasterTarget => {self.broadcasterTarget}")
  #		self.maskTarget = bitMask #SBTarget.eBroadcastBitBreakpointChanged # | SBTarget.eBroadcastBitWatchpointChanged | SBTarget.eBroadcastBitModulesLoaded | SBThread.eBroadcastBitThreadSuspended 
  #		global lt
  #		self.listenerTarget = lt
      # print(f"=====================>>>>>>>>> self.debugger (REMOVE): {self.debugger} / {self.listener}")
      self.listener.StopListeningForEventClass(self.debugger,                                                  lldb.SBTarget.GetBroadcasterClassName(),
        lldb.SBTarget.eBroadcastBitBreakpointChanged
        #| lldb.SBTarget.eBroadcastBitModuleLoaded
        #| lldb.SBTarget.eBroadcastBitModuleUnloaded
        #| lldb.SBTarget.eBroadcastBitWatchpointChanged)
      )
      
      success = self.debugger.GetSelectedTarget().GetBroadcaster().RemoveListener(self.listener, bitMask)
      # print(f"Removed Listener with {success}")
      #.RemoveListener(self.listenerTarget, bitMask)
  #		print(f"Removed Listener with {success} / self.broadcasterTarget => {self.broadcasterTarget} / self.listenerTarget  => {self.listenerTarget} / self.maskTarget => {self.maskTarget}")

    def createTarget(self, target_image, args=None):
        print(f"createTarget({target_image})....")
        self.handleCommand("target create %s" % target_image)
        if args is not None:
            self.handleCommand("settings set target.run-args %s" % args)

        # # Define paths for stdout and stderr redirection
        # stdout_path = "/tmp/console_app_stdout.log"
        # stderr_path = "/tmp/console_app_stderr.log"
        #
        # # Set the standard output and error paths for the target
        # self.handleCommand(f"settings set target.standard-output-path {stdout_path}")
        # self.handleCommand(f"settings set target.standard-error-path {stderr_path}")
        # # print(f"Stdout redirected to: {stdout_path}")
        # # print(f"Stderr redirected to: {stderr_path}")

    def attachProcess(self, pid):
        self.handleCommand("process attach -p %d" % pid)
        pass

    def loadCore(self, corefile):
        self.handleCommand("target create -c %s" % corefile)
        pass

    def setDone(self, isDone=True):
        self.done = isDone
        self.aborted = isDone

    def isDone(self):
        return self.done

    def getPrompt(self):
        return self.debugger.GetPrompt()

    def getCommandInterpreter(self):
        return self.debugger.GetCommandInterpreter()

    def getSourceManager(self):
        return self.debugger.GetSourceManager()

    def setSize(self, width, height):
        # FIXME: respect height
        self.debugger.SetTerminalWidth(width)

    def getTarget(self):
        return self.debugger.GetTargetAtIndex(0)

    def handleCommand(self, cmd):
        ret = lldb.SBCommandReturnObject()
        self.getCommandInterpreter().HandleCommand(cmd, ret)
        return ret
  
    def eventLoop(self):
#       global process
        while not self.isDone() and not self.aborted:
            event = lldb.SBEvent()
            got_event = self.listener.WaitForEvent(lldb.UINT32_MAX, event)
            # print(f'GOT-EVENT: {event} / {event.GetType()} ====>>> THATS DA ONE')
#           desc = get_description(event)
#           print('Event description:', desc)
#           print('Event data flavor:', event.GetDataFlavor())
#           if str(event.GetDataFlavor()) == "ProgressEventData":
#             self.event_queue.put(event)
#             pass
###           if event.GetDataFlavor() == "Breakpoint::BreakpointEventData":
###             print("GOT BREAKPOINT CHANGE!!!")
###           global process
###           print('Process state:', lldbutil.state_type_to_str(process.GetState()))
##           print()
#           
#           # eBroadcastBitSTDOUT
#           if SBProcess.EventIsProcessEvent(event):
#           #             self._broadcast_process_state(SBProcess.GetProcessFromEvent(event), event)
#           #             self.processEvent.emit(event)
#           #             QCoreApplication.processEvents()
#             print("PROCESS EVENT!!!")
##           elif event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
##             print(">>>>> WE GOT STDOUT")
##             stdout = self.getTarget().GetProcess().GetSTDOUT(256)
##             if stdout is not None and len(stdout) > 0:
##               message = {"status":"event", "type":"stdout", "output": "".join(["%02x" % ord(i) for i in stdout])}
##               print(message)
##               self.signals.event_output.emit("".join(["%02x" % ord(i) for i in stdout]))
##               QCoreApplication.processEvents()
###                 continue
##             else:
##               continue
##             while stdout:
##               stdout = self.getTarget().GetProcess().GetSTDOUT(256)
##               if stdout is not None and len(stdout) > 0:
##                 message = {"status":"event", "type":"stdout", "output": "".join(["%02x" % ord(i) for i in stdout])}
##                 print(message)
##                 self.signals.event_output.emit("".join(["%02x" % ord(i) for i in stdout]))
##                 QCoreApplication.processEvents()
###                 continue
##               else:
##                 break
##             continue
# #           if got_event and not event.IsValid():
# ##               self.winAddStr("Warning: Invalid or no event...")
# #               continue
# ##             elif not event.GetBroadcaster().IsValid():
# ##                 continue
#           
#           self.event_queue.put(event)
#           self.signals.event_queued.emit(event)
#           QCoreApplication.processEvents()
        # print(f"TERMINATING DRIVER EVENT-LOOP ===>>> TERMINATE")
        self.terminate()
        # print(f"TERMINATING DRIVER EVENT-LOOP ===>>> EXITED")
        
    def run(self):
        self.eventLoop()

    def terminate(self):
        lldb.SBDebugger.Terminate()
        sys.exit(0)
        
    def getPC(self, asHex = False):
      target = self.getTarget()
      if target:
        process = target.GetProcess()
        if process:
          thread = process.GetThreadAtIndex(0)
          if thread:
            for z in range(thread.GetNumFrames()):
              frame = thread.GetFrameAtIndex(z)
              if frame.GetModule().GetFileSpec().GetFilename() != target.GetExecutable().GetFilename():
                continue
              if frame:
                if asHex:
                  return hex(frame.GetPC())
                else:
                  return frame.GetPC()
      return ""
  
    def getThread(self, index = 0):
      target = self.getTarget()
      if target:
        process = target.GetProcess()
        if process:
          thread = process.GetThreadAtIndex(index)
          if thread:
            return thread
#         els
#           for z in range(thread.GetNumFrames()):
#             frame = thread.GetFrameAtIndex(z)
#             if frame.GetModule().GetFileSpec().GetFilename() != target.GetExecutable().GetFilename():
#               continue
#             return frame
      return None
  
    def getFrame(self):
#     target = self.getTarget()
#     if target:
#       process = target.GetProcess()
#       if process:
#         thread = process.GetThreadAtIndex(0)
      thread = self.getThread()
      if thread:
        for z in range(thread.GetNumFrames()):
          frame = thread.GetFrameAtIndex(z)
          if frame.GetModule().GetFileSpec().GetFilename() != self.getTarget().GetExecutable().GetFilename():
            continue
          return frame
#         if thread:
#           for z in range(thread.GetNumFrames()):
#             frame = thread.GetFrameAtIndex(z)
#             if frame.GetModule().GetFileSpec().GetFilename() != target.GetExecutable().GetFilename():
#               continue
#             return frame
      return None
  
# SBThread

def createDriver(debugger, event_queue):
    driver = DebuggerDriver(debugger, event_queue)
    # driver.start()
    # if pid specified:
    # - attach to pid
    # else if core file specified
    # - create target from corefile
    # else
    # - create target from file
    # - settings append target.run-args <args-from-cmdline>
    # source .lldbinit file

    return driver