import lldb

import time
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from config import *
from dbg.listener import LLDBListener

try:
	import queue
except ImportError:
	import Queue as queue

import dbg.debuggerdriver
from dbg.fileInfos import *

class Worker(QObject):

	finished = pyqtSignal()
	show_dialog = pyqtSignal()
	logDbg = pyqtSignal(str)

	# updateProgress = pyqtSignal(int)

	# Load-Callbacks
	loadFileInfosCallback = pyqtSignal(object, object)
	loadJSONCallback = pyqtSignal(str)
	loadModulesCallback = pyqtSignal(object)
	enableBPCallback = pyqtSignal(str, bool, bool)

	# Main Vars
	mainWin = None
	fileToLoad = ""
	targetBasename = ""

	def __init__(self, mainWinToUse, filename):
		super().__init__()
		self._should_stop = False
		self.mainWin = mainWinToUse
		self.fileToLoad = filename
		self.driver = None
		self.target = None
		self.process = None
		self.listener = None

	def run(self):
		self._should_stop = False  # Reset before starting
		self.show_dialog.emit()

		self.logDbg.emit(f"loadNewExecutableFile({self.fileToLoad})...")
		self.targetBasename = os.path.basename(self.fileToLoad)
		self.loadNewExecutableFile(self.fileToLoad)
		if self.mainWin.driver.debugger.GetNumTargets() > 0:
			self.target = self.mainWin.driver.getTarget()
			# print(f"loadTarget => {target}")
			if self.target:
				exe = self.target.GetExecutable().GetDirectory() + "/" + self.target.GetExecutable().GetFilename()
				# self.targetBasename = os.path.basename(exe)
				mach_header = GetFileHeader(exe)
				self.loadFileInfosCallback.emit(mach_header, self.target)
				self.mainWin.devHelper.setupDevHelper()
				self.loadFileStats()

				# for i in range(10):  # Simulate long task
				#     if self._should_stop:
				#         print("Worker interrupted.")
				#         break
				#     # Simulate work
				#     time.sleep(1)
				#     print(f"Working... {i}")
				#     self.logDbg.emit(f"Working... {i}")
		self.finished.emit()

	def stop(self):
		self._should_stop = True

	def loadTarget(self):
		# return
		# self.logDbg.emit(f"loadTarget() started Num Targets: {self.driver.debugger.GetNumTargets()} ...")
		# if self.driver.debugger.GetNumTargets() > 0:
			# self.target = self.driver.getTarget()
		self.logDbg.emit(f"loadTarget() => Target: {self.target} ...")
		if self.target:
			self.process = self.target.GetProcess()
			self.logDbg.emit(f"loadTarget() => Process: {self.process} ...")
			if self.process:
				self.listener = LLDBListener(self.process, self.driver.debugger)
				self.listener.setHelper = self.mainWin.setHelper
				# self.listener.breakpointEvent.connect(self.handle_breakpointEvent)
				# self.listener.processEvent.connect(self.handle_processEvent)
				# self.listener.gotEvent.connect(self.treListener.handle_gotNewEvent)
				# self.listener.addListenerCalls()
				# self.listener.start()

				self.thread = self.process.GetThreadAtIndex(0)
				self.logDbg.emit(f"loadTarget() => Thread: {self.thread} ...")
				if self.thread:
					self.logDbg.emit(f"loadTarget() => Thread.GetNumFrames(): {self.thread.GetNumFrames()} ...")
					for z in range(self.thread.GetNumFrames()):
						frame = self.thread.GetFrameAtIndex(z)
						self.loadModulesCallback.emit(frame)
						# self.tabWidgetStruct.cmbModules.addItem(
						# 	frame.GetModule().GetFileSpec().GetFilename() + " (" + str(
						# 		frame.GetFrameID()) + ")")
						self.logDbg.emit(f"loadTarget() => Frame: {frame} ...")
						if frame.GetModule().GetFileSpec().GetFilename() != self.target.GetExecutable().GetFilename():
							self.logDbg.emit(f"Module for FileStzuct IS NOT equal executable => continuing ...")
							continue
						else:
							self.logDbg.emit(f"Module for FileStzuct IS equal executable => scanning ...")
						if frame:
							self.logDbg.emit(f"BEFORE DISASSEMBLE!!!!")
							# self.start_loadDisassemblyWorker(True)
							# context = frame.GetSymbolContext(lldb.eSymbolContextEverything)

	def loadFileStats(self):
		statistics = self.driver.getTarget().GetStatistics()
		stream = lldb.SBStream()
		success = statistics.GetAsJSON(stream)
		if success:
			self.loadJSONCallback.emit(str(stream.GetData()))

	def loadNewExecutableFile(self, filename):
		# return

		# logDbg(f"loadNewExecutableFile({filename})...")
		# self.targetBasename = os.path.basename(filename)
		# self.stopTarget()

		global event_queue
		self.mainWin.event_queue = queue.Queue()
		#
		#				#				global driver
		self.mainWin.inited = False
		self.driver = dbg.debuggerdriver.createDriver(self.mainWin.driver.debugger, self.mainWin.event_queue)
		#		self.driver.debugger.SetLoggingCallback(self.my_custom_log_callback)
		self.driver.debugger.SetAsync(False)
		#			self.driver.aborted = False

		#			self.driver.createTarget(filename)
		self.driver.signals.event_queued.connect(self.mainWin.handle_event_queued)
		self.driver.start()
		self.driver.createTarget(filename)
		# logDbg(f"self.driver.createTarget({filename}) => self.driver.debugger.GetNumTargets() = {self.driver.debugger.GetNumTargets()}")
		if self.driver.debugger.GetNumTargets() > 0:
			# self.mainWin.target = self.mainWin.driver.debugger.GetSelectedTarget()


			self.target = self.driver.getTarget()
			self.mainWin.target = self.target
			self.logDbg.emit(f"target: {self.target}")
			# return

			# if self.mainWin.setHelper.getValue(SettingsValues.BreakAtMainFunc):
			#     main_bp = self.mainWin.bpHelper.addBPByName(self.mainWin.setHelper.getValue(SettingsValues.MainFuncName))
			#     print(main_bp)
			#     for bl in main_bp:
			#         logDbg(f"bl.GetAddress(): {hex(bl.GetAddress().GetLoadAddress(target))}")
			#     logDbg(f"main_bp: {main_bp}")
			#
			if self.mainWin.setHelper.getValue(SettingsValues.BreakpointAtMainFunc):
				self.driver.debugger.HandleCommand("process launch --stop-at-entry")
				addrObj2 = find_main(self.driver.debugger)
				# main_bp2 = self.bpHelper.enableBP(hex(addrObj2), True, False)
				main_bp2 = self.enableBPCallback.emit(hex(addrObj2), True, False)
				# print(f"main_bp2 (@{addrObj2}): {main_bp2}")
				self.logDbg.emit(f"main_bp2 (@{hex(addrObj2)}): {main_bp2}")
				self.target.GetProcess().Continue()

			# setHelper = SettingsHelper()
			# if self.setHelper.getChecked(SettingsValues.BreakpointAtMainFunc):
			# 	addrObj2 = find_main(self.driver.debugger)
			# 	logDbg(f"Enabling EntryPoint Breakpoint @ {hex(addrObj2)}")
			# 	self.bpHelper.enableBP(hex(addrObj2), True, True)

			# launch_info = target.GetLaunchInfo()

			#########
			# print("AFTER GETLAUNCHINFO!!!!")
			# Create a temporary file to capture output
			# output_path = "/tmp/lldb_output.txt"
			# output_file = open(output_path, "w")
			# output_fd = output_file.fileno()

			# stdout_action = lldb.SBFileAction()
			# stdout_action.Open(output_path, True, False)  # append=False, read=False
			# launch_info.SetFileAction(lldb.eLaunchFlagStdout, stdout_action)
			#########
			# Create a pipe to capture the output
			# read_fd, write_fd = os.pipe()
			# launch_info.SetStandardOutput(write_fd)  # Redirect stdout
			# launch_info.SetStandardError(write_fd)  # (optional) Redirect stderr too

			# if self.setHelper.getValue(SettingsValues.StopAtEntry):
			# 	launch_info.SetLaunchFlags(lldb.eLaunchFlagDisableASLR + lldb.eLaunchFlagStopAtEntry)# lldb.eLaunchFlagDisableASLR +
			# 	logDbg(f"launch_info.SetLaunchFlags(lldb.eLaunchFlagDisableASLR + lldb.eLaunchFlagStopAtEntry)")
			# else:
			# 	launch_info.SetLaunchFlags(lldb.eLaunchFlagDebug)
			# 	logDbg(f"launch_info.SetLaunchFlags(lldb.eLaunchFlagDebug)")

			# if self.setHelper.getValue(SettingsValues.StopAtEntry):
			# 	launch_info.SetLaunchFlags(lldb.eLaunchFlagDisableASLR and lldb.eLaunchFlagStopAtEntry)# lldb.eLaunchFlagDisableASLR +
			# # else:
			# # 	launch_info.SetLaunchFlags(lldb.eLaunchFlagStopAtEntry)
			# # 	launch_info.SetLaunchFlags(lldb.eLaunchFlagDisableASLR and lldb.eLaunchFlagStopAtEntry and lldb.eLaunchFlagDebug)

			# error = lldb.SBError()
			# # SBProcess
			# self.break_at_main(self.driver.debugger, "", "", "")
			# self.process = target.Launch(stop_at_entry=True, error=error)
			# self.break_at_main(self.driver.debugger, "", "", "")
			# self.process.Stop()
			# # output = io.StringIO()

			#########
			# Close the write end in your script so you can read from the read end
			# os.close(write_fd)

			# Read the output
			# output = os.read(read_fd, 4096).decode("utf-8")
			# print(f"Captured output:\n{output}")

			# Read output from file
			# output_file.close()
			# with open(output_path, "r") as f:
			# 	captured_output = f.read()

			# print(f"Captured output:\n{captured_output}")
			#########

			#			target.Launch(self.driver.debugger.GetListener(), None, None, None, output.fileno(), None, None, 0, False, error)
			##			'/tmp/stdout.txt'
			self.loadTarget()
			# self.setWinTitleWithState("Target loaded")
