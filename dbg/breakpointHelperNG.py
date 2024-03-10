#!/usr/bin/env python3

import lldb
import os
import sys
import re
import pyperclip

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets
from config import *

class BreakpointHelperNG():
	
	def __init__(self, driver):
		self.driver = driver
		
	def setCtrls(self, txtMultiline, treBPs):
		self.txtDis = txtMultiline
		self.treBP = treBPs
		
	def checkBPExists(self, address):
		bpRet = None
		blRet = None
		target = self.driver.getTarget()
		found = False
		for i in range(target.GetNumBreakpoints()):
			bp = target.GetBreakpointAtIndex(i)
			for j in range(bp.GetNumLocations()):
				bl = bp.GetLocationAtIndex(j)
				if hex(bl.GetAddress().GetLoadAddress(target)) == address:
					bpRet = bp
					blRet = bl
					found = True
					break
			if found:
				break
		return [bpRet, blRet]
	
	def addBPByName(self, name):
		target = self.driver.getTarget()
		bp = target.BreakpointCreateByName(name, target.GetExecutable().GetFilename())
		bp.AddName(name)
		bp.SetEnabled(True)
		self.setCommandLineCommands(bp, ["banner"])
		return bp
		
	def enableBP(self, address, enabled = True):
		print(f'enableBP: {address} => {enabled}')
		target = self.driver.getTarget()
		found = False
		bpRet = self.checkBPExists(address)
		if bpRet[0] != None:
			bpRet[0].SetEnabled(enabled)
			bpRet[1].SetEnabled(enabled)
			self.txtDis.enableBP(address, enabled)
			self.treBP.enableBP(address, enabled)
		else:
			bp = target.BreakpointCreateByAddress(int(address, 16))
			bp.SetEnabled(enabled)
			self.setCommandLineCommands(bp, ["banner"])
			self.txtDis.enableBP(address, enabled)
			self.treBP.addBP(bp)

	def deleteBP(self, address):
		target = self.driver.getTarget()
		found = False
		bpRet = self.checkBPExists(address)
		if bpRet[0] != None:
			target.BreakpointDelete(bpRet[0].GetID())
			id = bpRet[0].GetID()
			id2 = bpRet[1].GetID()
			print(f"Deleting BP by address: {address} => {id} / {id2}")
			
			self.txtDis.deleteBP(address)
			self.treBP.deleteBP(id)
			
			
	def saveBPs(self, filepath):
		target = self.driver.getTarget()
		path_spec = lldb.SBFileSpec(filepath)
		target.BreakpointsWriteToFile(path_spec)
		pass
		
	def setCommandLineCommands(self, bp, commands):
		sl = lldb.SBStringList()
		for command in commands:
			sl.AppendString(command)
		bp.SetCommandLineCommands(sl)
		
	def changeName(self, bp, newName):
#		AddName
		pass