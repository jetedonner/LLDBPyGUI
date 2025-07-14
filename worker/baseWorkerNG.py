import lldb

import time
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from config import *
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

	# Main Vars
	mainWin = None
	fileToLoad = ""
	targetBasename = ""

	def __init__(self, mainWinToUse, filename):
		super().__init__()
		self._should_stop = False
		self.mainWin = mainWinToUse
		self.fileToLoad = filename

	def run(self):
		self._should_stop = False  # Reset before starting
		self.show_dialog.emit()

		self.logDbg.emit(f"loadNewExecutableFile({self.fileToLoad})...")
		self.targetBasename = os.path.basename(self.fileToLoad)
		self.loadNewExecutableFile(self.fileToLoad)
		if self.mainWin.driver.debugger.GetNumTargets() > 0:
			target = self.mainWin.driver.getTarget()
			# print(f"loadTarget => {target}")
			if target:
				exe = target.GetExecutable().GetDirectory() + "/" + target.GetExecutable().GetFilename()
				# self.targetBasename = os.path.basename(exe)

				mach_header = GetFileHeader(exe)
				self.loadFileInfosCallback.emit(mach_header, target)
				# fileInfos = FileInfos()
				# fileInfos.loadFileInfo(target, self.tblFileInfos)
				# #				self.devHelper.bpHelper = self.bpHelper
				self.mainWin.devHelper.setupDevHelper()
				#				self.devHelper.setDevBreakpoints()
				# self.devHelper.setDevWatchpointsNG()
				self.loadFileStats()
		# self.mainWin.loadNewExecutableFile(ConfigClass.testTarget)
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

	# def run(self):
	#     # Simulate heavy work
	#     # time.sleep(0.1)
	#
	#     # Signal to show modal dialog
	#     self.show_dialog.emit()
	#
	#     # More work...
	#     time.sleep(20)
	#     self.finished.emit()

	def loadFileStats(self):
		statistics = self.mainWin.driver.getTarget().GetStatistics()
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
		self.mainWin.driver = dbg.debuggerdriver.createDriver(self.mainWin.driver.debugger, self.mainWin.event_queue)
		#		self.driver.debugger.SetLoggingCallback(self.my_custom_log_callback)
		self.mainWin.driver.debugger.SetAsync(False)
		#			self.driver.aborted = False

		#			self.driver.createTarget(filename)
		self.mainWin.driver.signals.event_queued.connect(self.mainWin.handle_event_queued)
		self.mainWin.driver.start()
		self.mainWin.driver.createTarget(filename)
		# logDbg(f"self.driver.createTarget({filename}) => self.driver.debugger.GetNumTargets() = {self.driver.debugger.GetNumTargets()}")
		if self.mainWin.driver.debugger.GetNumTargets() > 0:
			# self.mainWin.target = self.mainWin.driver.debugger.GetSelectedTarget()


			self.mainWin.target = self.mainWin.driver.getTarget()
			self.logDbg.emit(f"target: {self.mainWin.target}")
			return

			# if self.mainWin.setHelper.getValue(SettingsValues.BreakAtMainFunc):
			#     main_bp = self.mainWin.bpHelper.addBPByName(self.mainWin.setHelper.getValue(SettingsValues.MainFuncName))
			#     print(main_bp)
			#     for bl in main_bp:
			#         logDbg(f"bl.GetAddress(): {hex(bl.GetAddress().GetLoadAddress(target))}")
			#     logDbg(f"main_bp: {main_bp}")
			#
			# if self.setHelper.getValue(SettingsValues.BreakpointAtMainFunc):
			#     self.driver.debugger.HandleCommand("process launch --stop-at-entry")
			#     addrObj2 = find_main(self.driver.debugger)
			#     main_bp2 = self.bpHelper.enableBP(hex(addrObj2), True, False)
			#     # print(f"main_bp2 (@{addrObj2}): {main_bp2}")
			#     logDbgC(f"main_bp2 (@{addrObj2}): {main_bp2}")
			#     target.GetProcess().Continue()

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
			# self.loadTarget()
			# self.setWinTitleWithState("Target loaded")
