import lldb

from lib.thirdParty.breakpointManager import BreakpointManager


class DevHelper():
	mainWindow = None

	def __init__(self, mainWindow):
		super().__init__()

		self.mainWindow = mainWindow
		self.bpMgr = BreakpointManager(self.mainWindow.driver)

	def loadStartup(self):
		try:
			self.mainWindow.tabTools.setCurrentWidget(self.mainWindow.treBreakpoints)
			# self.mainWindow.treBreakpoints.load_breakpoints_from_file(self.mainWindow.driver.target,
			#
			# self.bpMgr.addBPByName("buttonClicked")
			# breakpoint = target.BreakpointCreateByName("buttonClicked")										  "/Volumes/Data/dev/python/LLDBGUI/1st_project_kim_hello_library_exec2_mybps_14.bpson")
		except Exception as e:
			print(f"Exception occurred: {e} ...")
