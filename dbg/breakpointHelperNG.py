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

# import SBBreakpointList

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
		# self.setCommandLineCommands(bp, ["banner"])
		return bp
		
	def enableBP(self, address, enabled = True, updateUI = True):
		target = self.driver.getTarget()
		print(f'enableBP: {address} => {enabled}, target: {target}')

		found = False
		bpRet = self.checkBPExists(address)
		if bpRet[0] != None:
			bpRet[0].SetEnabled(enabled)
			bpRet[1].SetEnabled(enabled)
			# if updateUI:
			self.txtDis.enableBP(address, enabled)
			self.treBP.enableBP(address, enabled)
			return bpRet[0]
		else:
			bp = target.BreakpointCreateByAddress(int(address, 16))
			bp.SetEnabled(enabled)
			# self.setCommandLineCommands(bp, ["banner"])
			self.txtDis.enableBP(address, enabled)
			if updateUI:
				self.treBP.addBP(bp)
			return bp

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

	# BreakpointsCreateFromFile(SBTarget
	# self, SBFileSpec
	# source_file, SBBreakpointList
	# bkpt_list) -> SBError

	def loadBPs(self, filepath):
		target = self.driver.getTarget()
		path_spec = lldb.SBFileSpec(filepath)
		bkpt_list = lldb.SBBreakpointList(target)
		# Load breakpoints from the file
		# error = lldb.SBError()
		error = target.BreakpointsCreateFromFile(path_spec, bkpt_list)
		if error is not None and not error.Success():
			print(f"Error while getting the Breakpoints from file ({filepath}): {error}")
		else:
			print(f"LOADED BPs FROM FILE!!!!")
			print(f"{bkpt_list}")
			dir(bkpt_list)
			print(dir(bkpt_list))
			for brIdx in range(bkpt_list.GetSize()):
				for bl in bkpt_list.GetBreakpointAtIndex(brIdx):
					print(f"bl.GetAddress(): {bl.GetAddress()}")
		pass

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