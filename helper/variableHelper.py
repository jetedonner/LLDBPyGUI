#!/usr/bin/env python3

import lldb


def ensure_suffix(s, suffix):
	if not s.endswith(suffix):
		s += suffix
	return s


# @staticmethod
def is_float(s):
	try:
		float(s)
		return True
	except ValueError:
		return False


# @staticmethod
def is_int(s):
	try:
		int(s)
		return True
	except ValueError:
		return False


def is_hex_with_prefix(s):
	if s.lower().startswith("0x"):
		s = s[2:]
	try:
		int(s, 16)
		return True
	except ValueError:
		return False


def convert_64_to_32(hex64):
	value = int(hex64, 16)
	lower_32 = value & 0xFFFFFFFF
	return hex(lower_32)


def strip_leading_zeros(hex_str):
	# Convert hex string to integer
	value = int(hex_str, 16)
	# Convert back to hex string without leading zeros
	return hex(value)


class VariablesHelper():
	driver = None

	def __init__(self, driver):
		self.driver = driver

	@staticmethod
	def GetVariable(driver, varName):
		return VariablesHelper(driver).getVariable(varName)

	def getVariable(self, varName):
		# Get the frame object from the current debugging session
		# frame = self.driver.frame # self.driver.target.GetProcess().GetThreadAtIndex(0).GetFrameAtIndex(0)

		# Get the variable you want to modify by name
		var = self.driver.worker.process.GetThreadAtIndex(0).GetFrameAtIndex(0).FindVariable(varName)
		return var

	@staticmethod
	def SetVariableDataInt(driver, varName, data, byteOrder=lldb.eByteOrderLittle):
		return VariablesHelper(driver).setVariableDataInt(varName, data, byteOrder)

	def setVariableDataInt(self, varName, data, byteOrder=lldb.eByteOrderLittle):
		var = self.getVariable(varName)
		if var:
			error = lldb.SBError()
			if var.GetType().GetBasicType() == lldb.eBasicTypeInt:
				var.SetData(lldb.SBData().CreateDataFromSInt32Array(byteOrder, var.GetByteSize(), [data]), error)

			if error.Success():
				successMsg = f"Variable '{varName}' with type: '{var.GetType()}' ('{var.GetType().GetBasicType()}') updated to: {data}"
				print(successMsg)
				#				self.window().updateStatusBar(successMsg)
				#			self.window().updateStatusBar(successMsg)
				return True
			else:
				print(f"ERROR: {error}")

		return False
