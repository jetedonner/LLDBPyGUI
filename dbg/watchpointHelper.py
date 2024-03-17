#!/usr/bin/env python3

import lldb

from dbg.debuggerdriver import *

from enum import Enum

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from config import *


#read | write | modify | read_write

class WatchpointAccessMod(Enum):
	Read = ("read", "r")
	Write = ("w", "w")
	Modify = ("modify", "w")
	Read_Write = ("read_write", "rw")

class WatchpointHelper(QObject):
	
	driver = None
	
	def __init__(self, driver):
		super().__init__()
		
		self.driver = driver
		
	
#	def setDevWatchpoints(self):
#		print(f"==========>>>>>>>>> SETTING DEV-WATCHPOINT!!!")
#		error = lldb.SBError()
#		wp = self.driver.getTarget().WatchAddress(0x304112ea8, 0x4, True, True, error)
#		if wp != None:
#			print(f"=========>>>>>> DEV-WATCHPOINT: {wp}")
#		pass
	
	def setWatchpointForVariable(self, varName, type = WatchpointAccessMod.Write):
		print(f"==========>>>>>>>>> SETTING WATCHPOINT For Variable {varName}!!!")
		res = lldb.SBCommandReturnObject()
		ci = self.driver.debugger.GetCommandInterpreter()
		
		ci.HandleCommand('command script import "/Volumes/Data/dev/_reversing/disassembler/LLDBPyGUI/LLDBPyGUI/LLDBPyGUIWindow.py"', res)
		# settings
		ci.HandleCommand(f"w s v -w read_write {varName}", res)
		ci.HandleCommand("watchpoint command add -F LLDBPyGUIWindow.wpcallback 1", res)
#	debugger.HandleCommand("watchpoint command add -F myfile.callback %s" % mywatchpoint.GetID())
#	read | write | modify | read_write
	def setWatchpointForExpression(self, expression, type = WatchpointAccessMod.Modify):
		print(f"==========>>>>>>>>> SETTING WATCHPOINT For Expression {expression}!!!")
		res = lldb.SBCommandReturnObject()
		ci = self.driver.debugger.GetCommandInterpreter()
		
		# settings
		ci.HandleCommand('command script import "/Volumes/Data/dev/_reversing/disassembler/LLDBPyGUI/LLDBPyGUI/LLDBPyGUIWindow.py"', res)
		ci.HandleCommand(f"w s e {expression}", res)
		ci.HandleCommand("watchpoint command add -F LLDBPyGUIWindow.wpcallback 1", res)
	
#		return _lldb.SBTarget_DeleteAllWatchpoints(self) 
#	10056   
#	10057 -    def WatchAddress(self, *args): 
#	10058          """WatchAddress(SBTarget self, lldb::addr_t addr, size_t size, bool read, bool write, SBError error) -> SBWatchpoint""" 
#	10059          return _lldb.SBTarget_WatchAddress(self, *args) 