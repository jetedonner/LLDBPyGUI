#!/usr/bin/env python3
import lldb
import re
import codecs
import struct
from enum import Enum
#import re
#from helper.dbgHelper import *

class RegisterNames(Enum):
	RAX = ("rax", 0x1)
	RBX = ("rbx", 0x2)
	RCX = ("rcx", 0x4)
	RDX = ("rdx", 0x8)
	RDI = ("rdi", 0x10)
	RSI = ("rsi", 0x20)
	RBP = ("rbp", 0x40)
	RSP = ("rsp", 0x80)
	RIP = ("rip", 0x100)
	
	EAX = ("eax", 0x200)
	EBX = ("ebx", 0x400)
	ECX = ("ecx", 0x800)
	EDX = ("edx", 0x1000)
	CS = ("cs", 0x2000)
	FS = ("fs", 0x4000)
	GS = ("gs", 0x8000)
	EDI = ("edi", 0x10000)
	ESI = ("esi", 0x20000)
	EBP = ("ebp", 0x40000)
	ESP = ("esp", 0x80000)
	
	AX = ("ax", 0x100000)
	BX = ("bx", 0x200000)
	CX = ("cx", 0x400000)
	DX = ("dx", 0x800000)
	DI = ("di", 0x1000000)
	SI = ("si", 0x2000000)
	BP = ("bp", 0x4000000)
	SP = ("sp", 0x8000000)
	
	AH = ("ah", 0x10000000)
	BH = ("bh", 0x20000000)
	CH = ("ch", 0x40000000)
	DH = ("dh", 0x80000000)
	
	AL = ("al", 0x100000000)
	BL = ("bl", 0x200000000)
	CL = ("cl", 0x400000000)
	DL = ("dl", 0x800000000)
	
	DIL = ("dil", 0x1000000000)
	SIL = ("sil", 0x2000000000)
	BPL = ("bpl", 0x4000000000)
	SPL = ("spl", 0x8000000000)
	
	
	
	def hasMember(name):
		for member in RegisterNames:
			if member.value[0] == name:
				return True
		return False
	
	def startswith(name):
		for member in RegisterNames:
			if name.startswith(member.value[0]):
				return True
		return False
	
class SizeDirPtrs(Enum):
	BYTEPTR = ("byte ptr", 1)
	WORDPTR = ("word ptr", 2)
	DWORDPTR = ("dword ptr", 4)
	QWORDPTR = ("qword ptr", 8)
	BRACKET = ("[", 16)
	
	def hasMember(name):
		for member in SizeDirPtrs:
			if member.value[0] == name:
				return True
		return False
	
	def startswith(name):
		for member in SizeDirPtrs:
			if name.startswith(member.value[0]):
				return True
		return False
			
#	def has_member_name(enum_class, name):
#		return any(member.name == name for member in enum_class)
	
#	def getString(value):
#		flagRet = 0
#		# Check if the bitmask includes a specific enum value
#		if value & SizeDirPtrs.BYTEPTR.value:
#			return "byte ptr"
#		elif value & SizeDirPtrs.WORDPTR.value:
#			return "word ptr"
#		elif value & SizeDirPtrs.WORDPTR.value:
#			return "dword ptr"
#		elif value & SizeDirPtrs.WORDPTR.value:
#			return "qword ptr"
#		else:
#			return "unknown"

class QuickToolTip:
#	operandMemPrefixes = ("qword ptr", "dword ptr", "word ptr", "byte ptr", "[")
		
	def get_memory_addressAndOperands(self, debugger, operands):
		strOp = self.extractOperand(operands)
		return self.get_memory_address(debugger, strOp), strOp

	def get_memory_address(self, debugger, expression):
		target = debugger.GetSelectedTarget()
		process = target.GetProcess()
		thread = process.GetSelectedThread()
		frame = thread.GetSelectedFrame()
		
		isMinus = True
		isSolo = False
		parts = expression.split("-")
		if len(parts) <= 1:
			parts = expression.split("+")
			isMinus = False
			if len(parts) <= 1:
#				print("ISSOLO")
#				log("SOLO menemonic!!!")
				isSolo = True
			
#		if len(parts) == 2:
		rbp_value = frame.EvaluateExpression(f"${parts[0]}").GetValueAsUnsigned()
#		print(f"rbp_value: {rbp_value} / {hex(rbp_value)}")
		# Calculate the desired memory address
		if isMinus:
			offset_value = int(parts[1].replace("0x", ""), 16)
			address = rbp_value - offset_value
		elif isSolo:
			address = rbp_value
		else:
			offset_value = int(parts[1].replace("0x", ""), 16)
			address = rbp_value + offset_value
				
#		print(f"Memory address: 0x{address:X}")
		return address

	def extractOperand(self, string):
#		string = "dword ptr [rbp - 0x8]"
		pattern = r"\[([^\]]+)\]"  # Match anything within square brackets, excluding the brackets themselves
		match = re.search(pattern, string)
		
		if match:
			extracted_text = match.group(1)  # Access the captured group
#			print(extracted_text)  # Output: rbp - 0x8
			return extracted_text.replace(" ", "")
		else:
			print("No match found")
			return ""

	def splitOperands(self, openrands):
		parts = openrands.split(",")
		if len(parts) >= 2:
			return parts[0].strip(), parts[1].strip()
		else:
			return parts[0].strip(), ""
	
	def getOperandsText(self, openrands):
		operandsText = ""
		
		part1, part2 = self.splitOperands(openrands)
#		print(f"getOperandsText->part1: {part1}")
#		print(f"getOperandsText->part2: {part2}")
		if SizeDirPtrs.startswith(part1):
			operandsText = self.extractOperand(part1)
		elif SizeDirPtrs.startswith(part2):
			operandsText = self.extractOperand(part2)
		else:
			pass
			
#		if RegisterNames.startswith(part1):
##			operandsText = self.extractOperand(part1)
#			print(f"REGISTER FOUND!!!!")
##			return "REGISTER FOUND!!!"
#			operandsText += "\n" + part1 + ": " + part2
#		elif RegisterNames.startswith(part2):
##			operandsText = self.extractOperand(part2)
#			print(f"REGISTER FOUND!!!!")
##			return "REGISTER FOUND!!!"
#			operandsText += "\n" + part2 + ": " + part1
#		else:
#			pass
			
		return operandsText
	
	def getOperandsText2(self, debugger, openrands):
		operandsText = ""
		
		part1, part2 = self.splitOperands(openrands)
#		print(f"getOperandsText->part1: {part1}")
#		print(f"getOperandsText->part2: {part2}")
#		if SizeDirPtrs.startswith(part1):
#			operandsText = self.extractOperand(part1)
#		elif SizeDirPtrs.startswith(part2):
#			operandsText = self.extractOperand(part2)
#		else:
#			pass
		target = debugger.GetSelectedTarget()
		process = target.GetProcess()
		thread = process.GetSelectedThread()
		frame = thread.GetSelectedFrame()
			
		if RegisterNames.startswith(part1):
##			operandsText = self.extractOperand(part1)
#			print(f"REGISTER FOUND!!!!")
##			return "REGISTER FOUND!!!"
			rbp_value = frame.EvaluateExpression(f"${part1}").GetValueAsUnsigned()
			operandsText = part1 + ":\t" + hex(rbp_value) + " (" + str(rbp_value) + ")"
		elif RegisterNames.startswith(part2):
##			operandsText = self.extractOperand(part2)
#			print(f"REGISTER FOUND!!!!")
##			return "REGISTER FOUND!!!"
			rbp_value = frame.EvaluateExpression(f"${part2}").GetValueAsUnsigned()
			operandsText = part2 + ":\t" + hex(rbp_value) + " (" + str(rbp_value) + ")"
		else:
			pass
			
		return operandsText
	
	def doReadMemory(self, address, size = 0x100):
#		self.window().tabWidgetDbg.setCurrentWidget(self.window().tabMemory)
##		self.txtMemoryAddr = QLineEdit("0x100003f50")
##		self.txtMemorySize = QLineEdit("0x100")
#		self.window().txtMemoryAddr.setText(hex(address))
#		self.window().txtMemorySize.setText(hex(size))
#		try:
##           global debugger
#			self.handle_readMemory(self.driver.debugger, int(self.window().txtMemoryAddr.text(), 16), int(self.window().txtMemorySize.text(), 16))
#		except Exception as e:
#			print(f"Error while reading memory from process: {e}")
		pass
			
	def getQuickToolTip(self, openrands, debugger):
		tooltip = ""				
		
		checkVal = SizeDirPtrs.DWORDPTR
		
#		if SizeDirPtrs.hasMember("dword ptr"):
#			print("Member with name 'dword ptr' exists")
#		else:
#			print("NOT EXISTING!!!")
			
		address = 0
		operandsText = self.getOperandsText(openrands)
		if operandsText != "":
			address = self.get_memory_address(debugger, operandsText)

		if address != 0:
			
#			operandsText2 = self.getOperandsText2(debugger, openrands)
			tooltip = self.getOperandsText2(debugger, openrands)
			if tooltip != "":
				tooltip += f'\n----------------------\n'
#				tooltip = f'{operandsText2}'
#			else:
#				tooltip = ""
			tooltip += f'OpStr:\t{operandsText}'
			tooltip += f'\nAddr:\t{hex(address)}'
			if len(hex(address)) >= 11:
				try:
					error_ref = lldb.SBError()
					process = debugger.GetSelectedTarget().GetProcess()
					memory = process.ReadMemory(address, 0x20, error_ref)
					if error_ref.Success():
						dataTillNull = self.extract_data_until_null(memory)
						string = codecs.decode(dataTillNull, 'utf-8', errors='ignore')
						if dataTillNull != b'\x00' and string != '': # and not isNum:
							tooltip += f'\nString:\t{string}'
							
						try:
							value = struct.unpack('<H', dataTillNull)[0]
							tooltip += f'\nInt:\t{hex(value)} ({value})'
						except Exception as e:
		#					print(f'Error extracting INT: {e}')
							pass
							
		#				if len(dataTillNull) <= 1:
						tooltip += f'\nBytes:\t{dataTillNull}'
		#				else:
		#					tooltip += f'\nBytes:\t{dataTillNull[:-1]}'
					else:
						print(str(error_ref))
						tooltip = str(error_ref)
				except Exception as e:
					print(f"Error in generating QUICK-TOOLTIP: {e}")
					pass
		return tooltip
	
	def extract_data_until_null(self, byte_data):
		null_index = byte_data.find(b'\x00')
		if null_index != -1:
			return byte_data[:null_index + 1]
		else:
			return None