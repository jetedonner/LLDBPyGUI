from re import split

import lldb

from helper.debugHelper import logDbgC


class BreakpointManager():

	def __init__(self, driver):
		self.driver = driver

	def addBPByAddr(self, bpAddr, modName="", bpName=""):
		self.driver.debugger.HandleCommand(f"br set -a {bpAddr}{' -s ' + modName if modName else ''}{' -N ' + bpName if bpName else ''}")

	def deleteNameFromBP(self, bpID, bpName=""):
		self.driver.debugger.HandleCommand(
			f'br name delete -N {bpName} {str(bpID)}')

	def addNameToBP(self, bpID, bpName=""):
		self.driver.debugger.HandleCommand(
			f'br name add -N {bpName} {str(bpID)}')

	def addBPByName(self, symName, modName="", bpName=""):
		self.driver.debugger.HandleCommand(f"br set -n {symName}{' -s ' + modName if modName else ''}{' -N ' + bpName if bpName else ''}")

	def enableBPByID(self, bpID, enable=True):

		if "." in bpID:
			self.enableBPByID(bpID.split(".")[0], enable)

		res = lldb.SBCommandReturnObject()
		ci = self.driver.debugger.GetCommandInterpreter()

		if enable:
			ci.HandleCommand(f'br enable {bpID}', res)
		else:
			ci.HandleCommand(f"br disable {bpID}", res)

		logDbgC(f"BP-ENABLE RESULT: {res} ...")

	def deleteBPByAddr(self, bpAddr, force=False):
		print(f'deleteBPByAddr: {bpAddr} => force: {force}')
		target = self.driver.target
		for bp in target.breakpoint_iter():
			if bp.GetNumLocations() > 0:
				bl = bp.GetLocationAtIndex(0)
				if bl:
					if bpAddr == hex(bl.GetAddress().GetLoadAddress(target)):
						self.deleteBPByID(bp.GetID(), force)

	def deleteBPByID(self, bpID, force=False):
		self.driver.debugger.HandleCommand(f"br delete {'-f ' if force else ''}{bpID}")

	def deleteAllBPs(self):
		res = lldb.SBCommandReturnObject()
		ci = self.driver.debugger.GetCommandInterpreter()

		ci.HandleCommand(f'br delete -f', res)
		logDbgC(f"Delete all BPs res: {res} ...")
