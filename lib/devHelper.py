#!/usr/bin/env python3

import lldb

from dbg.debuggerdriver import *

from enum import Enum

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from config import *
from dbg.watchpointHelper import *
from dbg.breakpointHelperNG import *

class DevHelper(QObject):
	
	driver = None
	wpHelper = None
	bpHelper = None
	
	def __init__(self, driver, bpHelper = None):
		super().__init__()
		
		self.driver = driver
		self.wpHelper = WatchpointHelper(self.driver)
		if bpHelper is None:
			self.bpHelper = BreakpointHelperNG(self.driver)
		else:
			self.bpHelper = bpHelper
	
	def setupDevHelper(self):
		# self.setDevBreakpoints()
#		self.setDevWatchpointsNG()
		pass
		
	def setDevWatchpoints(self):
		print(f"==========>>>>>>>>> SETTING DEV-WATCHPOINT!!!")
		error = lldb.SBError()
		wp = self.driver.getTarget().WatchAddress(0x304112ea8, 0x4, True, True, error)
		if wp != None:
			print(f"=========>>>>>> DEV-WATCHPOINT: {wp}")
		pass
	
	def setDevBreakpoints(self):
		print(f"==========>>>>>>>>> SETTING DEV-BREAKPOINTS-NG!!!")
		self.bpHelper.enableBP("0x100003f5d")
		pass
	
	def setDevWatchpointsNG(self):
		print(f"==========>>>>>>>>> SETTING DEV-WATCHPOINTS-NG!!!")
		self.wpHelper.setWatchpointForVariable("idx")
#		self.wpHelper.setWatchpointForExpression("0x304112ea4")#("0x0000000304112e80")
		
#		res = lldb.SBCommandReturnObject()
#		ci = self.driver.debugger.GetCommandInterpreter()
#		
#		# settings
#		ci.HandleCommand("w s v idx", res)
	
#		return _lldb.SBTarget_DeleteAllWatchpoints(self) 
		pass
#	10056   
#	10057 -    def WatchAddress(self, *args): 
#	10058          """WatchAddress(SBTarget self, lldb::addr_t addr, size_t size, bool read, bool write, SBError error) -> SBWatchpoint""" 
#	10059          return _lldb.SBTarget_WatchAddress(self, *args) 