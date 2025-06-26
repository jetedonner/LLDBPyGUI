		#!/usr/bin/env python3

import lldb
import enum

import os

from ctypes import *
from struct import *
from binascii import *

exec2Dbg = None
debugger = None
target = None
process = None
thread = None

from enum import Enum
#
#class MyEnum(Enum):
#	VALUE_A = 1
#	VALUE_B = 2
#	VALUE_C = 4
#	VALUE_D = 8
#	
## Example bitmask, representing a combination of VALUE_A and VALUE_C
#bitmask = 5
#
## Check if the bitmask includes a specific enum value
#if bitmask & MyEnum.VALUE_A.value:
#	print("Bitmask includes VALUE_A")
#	
#if bitmask & MyEnum.VALUE_B.value:
#	print("Bitmask includes VALUE_B")
#	
#if bitmask & MyEnum.VALUE_C.value:
#	print("Bitmask includes VALUE_C")
#	
#if bitmask & MyEnum.VALUE_D.value:
#	print("Bitmask includes VALUE_D")

class MachoFlag(enum.Enum):
	MH_NONE = 0x0
	# Mach haeder "flag" constant bits
	MH_NOUNDEFS = 0x00000001
	MH_INCRLINK = 0x00000002
	MH_DYLDLINK = 0x00000004
	MH_BINDATLOAD = 0x00000008
	MH_PREBOUND = 0x00000010
	MH_SPLIT_SEGS = 0x00000020
	MH_LAZY_INIT = 0x00000040
	MH_TWOLEVEL = 0x00000080
	MH_FORCE_FLAT = 0x00000100
	MH_NOMULTIDEFS = 0x00000200
	MH_NOFIXPREBINDING = 0x00000400
	MH_PREBINDABLE = 0x00000800
	MH_ALLMODSBOUND = 0x00001000
	MH_SUBSECTIONS_VIA_SYMBOLS = 0x00002000
	MH_CANONICAL = 0x00004000
	MH_WEAK_DEFINES = 0x00008000
	MH_BINDS_TO_WEAK = 0x00010000
	MH_ALLOW_STACK_EXECUTION = 0x00020000
	MH_ROOT_SAFE = 0x00040000
	MH_SETUID_SAFE = 0x00080000
	MH_NO_REEXPORTED_DYLIBS = 0x00100000
	MH_PIE = 0x00200000
	MH_DEAD_STRIPPABLE_DYLIB = 0x00400000
	MH_HAS_TLV_DESCRIPTORS = 0x00800000
	MH_NO_HEAP_EXECUTION = 0x01000000
	
	def create_flag_value(value):
		flagRet = 0
		# Check if the bitmask includes a specific enum value
		if value & MachoFlag.MH_NOUNDEFS.value:
			flagRet = flagRet | MachoFlag.MH_NOUNDEFS.value
			
		if value & MachoFlag.MH_INCRLINK.value:
			flagRet = flagRet | MachoFlag.MH_INCRLINK.value
			
		if value & MachoFlag.MH_DYLDLINK.value:
			flagRet = flagRet | MachoFlag.MH_DYLDLINK.value
			
		if value & MachoFlag.MH_BINDATLOAD.value:
			flagRet = flagRet | MachoFlag.MH_BINDATLOAD.value
			
		if value & MachoFlag.MH_PREBOUND.value:
			flagRet = flagRet | MachoFlag.MH_PREBOUND.value
			
		if value & MachoFlag.MH_SPLIT_SEGS.value:
			flagRet = flagRet | MachoFlag.MH_SPLIT_SEGS.value
			
		if value & MachoFlag.MH_LAZY_INIT.value:
			flagRet = flagRet | MachoFlag.MH_LAZY_INIT.value
			
		if value & MachoFlag.MH_TWOLEVEL.value:
			flagRet = flagRet | MachoFlag.MH_TWOLEVEL.value
			
		if value & MachoFlag.MH_FORCE_FLAT.value:
			flagRet = flagRet | MachoFlag.MH_FORCE_FLAT.value
			
		if value & MachoFlag.MH_NOMULTIDEFS.value:
			flagRet = flagRet | MachoFlag.MH_NOMULTIDEFS.value
			
		if value & MachoFlag.MH_NOFIXPREBINDING.value:
			flagRet = flagRet | MachoFlag.MH_NOFIXPREBINDING.value
			
		if value & MachoFlag.MH_PREBINDABLE.value:
			flagRet = flagRet | MachoFlag.MH_PREBINDABLE.value
			
		if value & MachoFlag.MH_ALLMODSBOUND.value:
			flagRet = flagRet | MachoFlag.MH_ALLMODSBOUND.value
			
		if value & MachoFlag.MH_SUBSECTIONS_VIA_SYMBOLS.value:
			flagRet = flagRet | MachoFlag.MH_SUBSECTIONS_VIA_SYMBOLS.value
			
		if value & MachoFlag.MH_CANONICAL.value:
			flagRet = flagRet | MachoFlag.MH_CANONICAL.value
			
		if value & MachoFlag.MH_WEAK_DEFINES.value:
			flagRet = flagRet | MachoFlag.MH_WEAK_DEFINES.value
			
		if value & MachoFlag.MH_BINDS_TO_WEAK.value:
			flagRet = flagRet | MachoFlag.MH_BINDS_TO_WEAK.value
			
		if value & MachoFlag.MH_ALLOW_STACK_EXECUTION.value:
			flagRet = flagRet | MachoFlag.MH_ALLOW_STACK_EXECUTION.value
			
		if value & MachoFlag.MH_ROOT_SAFE.value:
			flagRet = flagRet | MachoFlag.MH_ROOT_SAFE.value
			
		if value & MachoFlag.MH_SETUID_SAFE.value:
			flagRet = flagRet | MachoFlag.MH_SETUID_SAFE.value
			
		if value & MachoFlag.MH_NO_REEXPORTED_DYLIBS.value:
			flagRet = flagRet | MachoFlag.MH_NO_REEXPORTED_DYLIBS.value
			
		if value & MachoFlag.MH_PIE.value:
			flagRet = flagRet | MachoFlag.MH_PIE.value
			
		if value & MachoFlag.MH_DEAD_STRIPPABLE_DYLIB.value:
			flagRet = flagRet | MachoFlag.MH_DEAD_STRIPPABLE_DYLIB.value
			
		if value & MachoFlag.MH_HAS_TLV_DESCRIPTORS.value:
			flagRet = flagRet | MachoFlag.MH_HAS_TLV_DESCRIPTORS.value
			
		if value & MachoFlag.MH_NO_HEAP_EXECUTION.value:
			flagRet = flagRet | MachoFlag.MH_NO_HEAP_EXECUTION.value
			
#		print(f'flagRet: {flagRet} / {hex(flagRet)}')
		return flagRet
	
	@classmethod
	def to_str(cls, flag):
		flags = ""
		if flag & MachoFlag.MH_NOUNDEFS.value:
			flags = flags + "MH_NOUNDEFS | "
			
		if flag & MachoFlag.MH_INCRLINK.value:
			flags = flags + "MH_INCRLINK | "
			
		if flag & MachoFlag.MH_DYLDLINK.value:
			flags = flags + "MH_DYLDLINK | "
			
		if flag & MachoFlag.MH_BINDATLOAD.value:
			flags = flags + "MH_BINDATLOAD | "
			
		if flag & MachoFlag.MH_PREBOUND.value:
			flags = flags + "MH_PREBOUND | "
			
		if flag & MachoFlag.MH_SPLIT_SEGS.value:
			flags = flags + "MH_SPLIT_SEGS | "
			
		if flag & MachoFlag.MH_LAZY_INIT.value:
			flags = flags + "MH_LAZY_INIT | "
			
		if flag & MachoFlag.MH_TWOLEVEL.value:
			flags = flags + "MH_TWOLEVEL | "
			
		if flag & MachoFlag.MH_FORCE_FLAT.value:
			flags = flags + "MH_FORCE_FLAT | "
			
		if flag & MachoFlag.MH_NOMULTIDEFS.value:
			flags = flags + "MH_NOMULTIDEFS | "
			
		if flag & MachoFlag.MH_NOFIXPREBINDING.value:
			flags = flags + "MH_NOFIXPREBINDING | "
			
		if flag & MachoFlag.MH_PREBINDABLE.value:
			flags = flags + "MH_PREBINDABLE | "
			
		if flag & MachoFlag.MH_ALLMODSBOUND.value:
			flags = flags + "MH_ALLMODSBOUND | "
			
		if flag & MachoFlag.MH_SUBSECTIONS_VIA_SYMBOLS.value:
			flags = flags + "MH_SUBSECTIONS_VIA_SYMBOLS | "
			
		if flag & MachoFlag.MH_CANONICAL.value:
			flags = flags + "MH_CANONICAL | "
			
		if flag & MachoFlag.MH_WEAK_DEFINES.value:
			flags = flags + "MH_WEAK_DEFINES | "
			
		if flag & MachoFlag.MH_BINDS_TO_WEAK.value:
			flags = flags + "MH_BINDS_TO_WEAK | "
			
		if flag & MachoFlag.MH_ALLOW_STACK_EXECUTION.value:
			flags = flags + "MH_ALLOW_STACK_EXECUTION | "
			
		if flag & MachoFlag.MH_ROOT_SAFE.value:
			flags = flags + "MH_ROOT_SAFE | "
			
		if flag & MachoFlag.MH_SETUID_SAFE.value:
			flags = flags + "MH_SETUID_SAFE | "
			
		if flag & MachoFlag.MH_NO_REEXPORTED_DYLIBS.value:
			flags = flags + "MH_NO_REEXPORTED_DYLIBS | "
			
		if flag & MachoFlag.MH_PIE.value:
			flags = flags + "MH_PIE | "
			
		if flag & MachoFlag.MH_DEAD_STRIPPABLE_DYLIB.value:
			flags = flags + "MH_DEAD_STRIPPABLE_DYLIB | "
			
		if flag & MachoFlag.MH_HAS_TLV_DESCRIPTORS.value:
			flags = flags + "MH_HAS_TLV_DESCRIPTORS | "
			
		if flag & MachoFlag.MH_NO_HEAP_EXECUTION.value:
			flags = flags + "MH_NO_HEAP_EXECUTION | "
			
		return flags.rstrip(" | ")
	
class MachoCPUType(enum.Enum):
	# Mach CPU constants
	CPU_ARCH_MASK = 0xFF000000
	CPU_ARCH_ABI64 = 0x01000000
	CPU_TYPE_ANY = 0xFFFFFFFF
	CPU_TYPE_VAX = 1
	CPU_TYPE_MC680X0 = 6
	CPU_TYPE_I386 = 7
	CPU_TYPE_X86_64 = CPU_TYPE_I386 | CPU_ARCH_ABI64
	CPU_TYPE_MIPS = 8
	CPU_TYPE_MC98000 = 10
	CPU_TYPE_HPPA = 11
	CPU_TYPE_ARM = 12
	CPU_TYPE_MC88000 = 13
	CPU_TYPE_SPARC = 14
	CPU_TYPE_I860 = 15
	CPU_TYPE_ALPHA = 16
	CPU_TYPE_POWERPC = 18
	CPU_TYPE_POWERPC64 = CPU_TYPE_POWERPC | CPU_ARCH_ABI64
	CPU_TYPE_UNKNOWN = 0x100000C
	CPU_TYPE_UNKNOWN2 = 0x2000000
	
	def create_cputype_value(value):
		# Create an enum value from an integer
		return MachoCPUType.__new__(MachoCPUType, value)
	
	@classmethod
	def to_str(cls, magic):
		if magic == cls.CPU_ARCH_MASK:
			return "CPU_ARCH_MASK"
		elif magic == cls.CPU_ARCH_ABI64:
			return "CPU_ARCH_ABI64"
		elif magic == cls.CPU_TYPE_ANY:
			return "CPU_TYPE_ANY"
		elif magic == cls.CPU_TYPE_VAX:
			return "CPU_TYPE_VAX"
		elif magic == cls.CPU_TYPE_MC680X0:
			return "CPU_TYPE_MC680x0"
		elif magic == cls.CPU_TYPE_I386:
			return "CPU_TYPE_I386"
		elif magic == cls.CPU_TYPE_X86_64:
			return "CPU_TYPE_X86_64"
		elif magic == cls.CPU_TYPE_MIPS:
			return "CPU_TYPE_MIPS"
		elif magic == cls.CPU_TYPE_MC98000:
			return "CPU_TYPE_MC98000"
		elif magic == cls.CPU_TYPE_HPPA:
			return "CPU_TYPE_HPPA"
		elif magic == cls.CPU_TYPE_ARM:
			return "CPU_TYPE_ARM"
		elif magic == cls.CPU_TYPE_MC88000:
			return "CPU_TYPE_MC88000"
		elif magic == cls.CPU_TYPE_SPARC:
			return "CPU_TYPE_SPARC"
		elif magic == cls.CPU_TYPE_I860:
			return "CPU_TYPE_I860"
		elif magic == cls.CPU_TYPE_ALPHA:
			return "CPU_TYPE_ALPHA"
		elif magic == cls.CPU_TYPE_POWERPC:
			return "CPU_TYPE_POWERPC"
		elif magic == cls.CPU_TYPE_POWERPC64:
			return "CPU_TYPE_POWERPC64"
		elif magic == cls.CPU_TYPE_UNKNOWN:
			return "CPU_TYPE_UNKNOWN"
		elif magic == cls.CPU_TYPE_UNKNOWN2:
			return "CPU_TYPE_UNKNOWN2"
		else:
			return "UNKNOWN"
		
class MachoFileType(enum.Enum):
	# Mach haeder "filetype" constants
	MH_OBJECT = 0x00000001
	MH_EXECUTE = 0x00000002
	MH_FVMLIB = 0x00000003
	MH_CORE = 0x00000004
	MH_PRELOAD = 0x00000005
	MH_DYLIB = 0x00000006
	MH_DYLINKER = 0x00000007
	MH_BUNDLE = 0x00000008
	MH_DYLIB_STUB = 0x00000009
	MH_DSYM = 0x0000000A
	MH_KEXT_BUNDLE = 0x0000000B
	MH_UNKNOWN = 0x3000000
	
	def create_filetype_value(value):
		# Create an enum value from an integer
		return MachoFileType.__new__(MachoFileType, value)
	
	@classmethod
	def to_str(cls, magic):
		if magic == cls.MH_OBJECT:
			return "MH_OBJECT"
		elif magic == cls.MH_EXECUTE:
			return "MH_EXECUTE"
		elif magic == cls.MH_FVMLIB:
			return "MH_FVMLIB"
		elif magic == cls.MH_CORE:
			return "MH_CORE"
		elif magic == cls.MH_PRELOAD:
			return "MH_PRELOAD"
		elif magic == cls.MH_DYLIB:
			return "MH_DYLIB"
		elif magic == cls.MH_DYLINKER:
			return "MH_DYLINKER"
		elif magic == cls.MH_BUNDLE:
			return "MH_BUNDLE"
		elif magic == cls.MH_DYLIB_STUB:
			return "MH_DYLIB_STUB"
		elif magic == cls.MH_DSYM:
			return "MH_DSYM"
		elif magic == cls.MH_KEXT_BUNDLE:
			return "MH_KEXT_BUNDLE"
		elif magic == cls.MH_UNKNOWN:
			return "MH_UNKNOWN"
		else:
			return "UNKNOWN"
		
		
class MachoMagic(enum.Enum):	
	# Mach header "magic" constants
	MH_MAGIC = 0xfeedface
	MH_CIGAM = 0xcefaedfe
	MH_MAGIC_64 = 0xfeedfacf
	MH_CIGAM_64 = 0xcffaedfe
	FAT_MAGIC = 0xcafebabe
	FAT_CIGAM = 0xbebafeca
	
#	@classmethod
	def create_magic_value(value):
		# Create an enum value from an integer
		return MachoMagic.__new__(MachoMagic, value)
	
	@classmethod
	def to_str(cls, magic):
		if magic == cls.MH_MAGIC:
			return "MH_MAGIC"
		elif magic == cls.MH_CIGAM:
			return "MH_CIGAM"
		elif magic == cls.MH_MAGIC_64:
			return "MH_MAGIC_64"
		elif magic == cls.MH_CIGAM_64:
			return "MH_CIGAM_64"
		elif magic == cls.FAT_MAGIC:
			return "FAT_MAGIC"
		elif magic == cls.FAT_CIGAM:
			return "FAT_CIGAM"
		else:
			return "UNKNOWN"
		
# Thanks for MACH* part of the code - Jonathan Salwan
class MACH_HEADER(Structure):
	_fields_ = [
		("magic",           c_uint),
		("cputype",         c_uint),
		("cpusubtype",      c_uint),
		("filetype",        c_uint),
		("ncmds",           c_uint),
		("sizeofcmds",      c_uint),
		("flags",           c_uint)
	]
	
def GetFileHeader(exe):
	with open(exe,'rb') as fopen:
		data = bytearray(fopen.read())
		mach_header = MACH_HEADER.from_buffer_copy(data)
		return mach_header
	return None

def GuessLanguage(frame):
	return lldb.SBLanguageRuntime.GetNameForLanguageType(frame.GuessLanguage())

#class lldbHelper():
#	
#	def GuessLanguage(self, frame):
#		return lldb.SBLanguageRuntime.GetNameForLanguageType(frame.GuessLanguage())

def SectionTypeString(secType):
	if secType == lldb.eSectionTypeInvalid: # = _lldb.eSectionTypeInvalid
		return "Invalid"
	elif secType == lldb.eSectionTypeCode:
		return "Code"
	elif secType == lldb.eSectionTypeContainer:
		return "Container"
	elif secType == lldb.eSectionTypeData:
		return "Data"
	elif secType == lldb.eSectionTypeDataCString:
		return "DataCString"
	elif secType == lldb.eSectionTypeDataCStringPointers:
		return "DataCStringPointers"
	elif secType == lldb.eSectionTypeDataSymbolAddress:
		return "DataSymbolAddress"
	elif secType == lldb.eSectionTypeData4:
		return "Data4"
	elif secType == lldb.eSectionTypeData8:
		return "Data8"
	elif secType == lldb.eSectionTypeData16:
		return "Data16"
	elif secType == lldb.eSectionTypeDataPointers:
		return "DataPointers"
	elif secType == lldb.eSectionTypeDebug:
		return "Debug"
	elif secType == lldb.eSectionTypeZeroFill:
		return "ZeroFill"
	elif secType == lldb.eSectionTypeDataObjCMessageRefs: 
		return 'DataObjCMessageRefs'
	elif secType == lldb.eSectionTypeDataObjCCFStrings: 
		return 'DataObjCCFStrings'
	elif secType == lldb.eSectionTypeDWARFDebugAbbrev: 
		return 'DWARFDebugAbbrev'	
	elif secType == lldb.eSectionTypeDWARFDebugAddr: 
		return 'DWARFDebugAddr'	
	elif secType == lldb.eSectionTypeDWARFDebugAranges: 
		return 'DWARFDebugAranges'
	elif secType == lldb.eSectionTypeDWARFDebugCuIndex: 
		return 'DWARFDebugCuIndex'
	elif secType == lldb.eSectionTypeDWARFDebugFrame: 
		return 'DWARFDebugFrame'
	elif secType == lldb.eSectionTypeDWARFDebugInfo: 
		return 'DWARFDebugInfo'
	elif secType == lldb.eSectionTypeDWARFDebugLine: 
		return 'DWARFDebugLine'
	elif secType == lldb.eSectionTypeDWARFDebugLoc: 
		return 'DWARFDebugLoc'
	elif secType == lldb.eSectionTypeDWARFDebugMacInfo: 
		return 'DWARFDebugMacInfo'
	elif secType == lldb.eSectionTypeDWARFDebugMacro: 
		return 'DWARFDebugMacro'
	elif secType == lldb.eSectionTypeDWARFDebugPubNames: 
		return 'DWARFDebugPubNames'
	elif secType == lldb.eSectionTypeDWARFDebugPubTypes: 
		return 'DWARFDebugPubTypes'
	elif secType == lldb.eSectionTypeDWARFDebugRanges: 
		return 'DWARFDebugRanges'
	elif secType == lldb.eSectionTypeDWARFDebugStr: 
		return 'DWARFDebugStr'
	elif secType == lldb.eSectionTypeDWARFDebugStrOffsets: 
		return 'DWARFDebugStrOffsets'
	elif secType == lldb.eSectionTypeDWARFAppleNames: 
		return 'DWARFAppleNames'
	elif secType == lldb.eSectionTypeDWARFAppleTypes: 
		return 'DWARFAppleTypes'
	elif secType == lldb.eSectionTypeDWARFAppleNamespaces: 
		return 'DWARFAppleNamespaces'
	elif secType == lldb.eSectionTypeDWARFAppleObjC: 
		return 'DWARFAppleObjC'
	elif secType == lldb.eSectionTypeELFSymbolTable: 
		return 'ELFSymbolTable'
	elif secType == lldb.eSectionTypeELFDynamicSymbols: 
		return 'ELFDynamicSymbols'
	elif secType == lldb.eSectionTypeELFRelocationEntries: 
		return 'ELFRelocationEntries'
	elif secType == lldb.eSectionTypeELFDynamicLinkInfo: 
		return 'ELFDynamicLinkInfo'
	elif secType == lldb.eSectionTypeEHFrame: 
		return 'EHFrame'
	elif secType == lldb.eSectionTypeARMexidx: 
		return 'ARMexidx'
	elif secType == lldb.eSectionTypeARMextab: 
		return 'ARMextab'
	elif secType == lldb.eSectionTypeCompactUnwind: 
		return 'CompactUnwind'
	elif secType == lldb.eSectionTypeGoSymtab: 
		return 'GoSymtab'
	elif secType == lldb.eSectionTypeAbsoluteAddress: 
		return 'AbsoluteAddress'
	elif secType == lldb.eSectionTypeDWARFGNUDebugAltLink: 
		return 'DWARFGNUDebugAltLink'
	elif secType == lldb.eSectionTypeDWARFDebugTypes: 
		return 'DWARFDebugTypes'
	elif secType == lldb.eSectionTypeDWARFDebugNames: 
		return 'DWARFDebugNames'
	elif secType == lldb.eSectionTypeOther: 
		return 'Other'
	elif secType == lldb.eSectionTypeDWARFDebugLineStr: 
		return 'DWARFDebugLineStr'
	elif secType == lldb.eSectionTypeDWARFDebugRngLists: 
		return 'DWARFDebugRngLists'
	elif secType == lldb.eSectionTypeDWARFDebugLocLists: 
		return 'DWARFDebugLocLists'
	elif secType == lldb.eSectionTypeDWARFDebugAbbrevDwo: 
		return 'DWARFDebugAbbrevDwo'
	elif secType == lldb.eSectionTypeDWARFDebugInfoDwo: 
		return 'DWARFDebugInfoDwo'
	elif secType == lldb.eSectionTypeDWARFDebugStrDwo: 
		return 'DWARFDebugStrDwo'
	elif secType == lldb.eSectionTypeDWARFDebugStrOffsetsDwo: 
		return 'DWARFDebugStrOffsetsDwo'
	elif secType == lldb.eSectionTypeDWARFDebugTypesDwo: 
		return 'DWARFDebugTypesDwo'
	elif secType == lldb.eSectionTypeDWARFDebugRngListsDwo: 
		return 'DWARFDebugRngListsDwo'
	elif secType == lldb.eSectionTypeDWARFDebugLocDwo: 
		return 'DWARFDebugLocDwo'
	elif secType == lldb.eSectionTypeDWARFDebugLocListsDwo: 
		return 'DWARFDebugLocListsDwo'
	elif secType == lldb.eSectionTypeDWARFDebugTuIndex: 
		return 'DWARFDebugTuIndex'
	elif secType == lldb.eSectionTypeCTF: 
		return 'CTF'	
	elif secType == lldb.eSectionTypeSwiftModules: 
		return 'SwiftModules'
	else:
		return "Other"

def SymbolTypeString(symType):
	if symType == lldb.eSymbolTypeAny:
		return "Any"	
	elif symType == lldb.eSymbolTypeInvalid:
		return "Invalid"
	elif symType == lldb.eSymbolTypeAbsolute:
		return "Absolute"
	elif symType == lldb.eSymbolTypeCode:
		return "Code"
	elif symType == lldb.eSymbolTypeResolver:
		return "Resolver"
	elif symType == lldb.eSymbolTypeData:
		return "Data"
	elif symType == lldb.eSymbolTypeTrampoline:
		return "Trampoline"
	elif symType == lldb.eSymbolTypeRuntime:
		return "Runtime"
	elif symType == lldb.eSymbolTypeException:
		return "Exception"
	elif symType == lldb.eSymbolTypeSourceFile:
		return "Source File"
	elif symType == lldb.eSymbolTypeHeaderFile:
		return "Header File"
	elif symType == lldb.eSymbolTypeObjectFile:
		return "Object File"
	elif symType == lldb.eSymbolTypeCommonBlock:
		return "Common Block"
	elif symType == lldb.eSymbolTypeBlock:
		return "Block"
	elif symType == lldb.eSymbolTypeLocal:
		return "Local"
	elif symType == lldb.eSymbolTypeParam:
		return "Param"
	elif symType == lldb.eSymbolTypeVariable:
		return "Variable"
	elif symType == lldb.eSymbolTypeVariableType:
		return "Variable Type"
	elif symType == lldb.eSymbolTypeLineEntry:
		return "Line Entry"
	elif symType == lldb.eSymbolTypeLineHeader:
		return "Line Header"
	elif symType == lldb.eSymbolTypeScopeBegin:
		return "Scope Begin"
	elif symType == lldb.eSymbolTypeScopeEnd:
		return "Scope End"
	elif symType == lldb.eSymbolTypeAdditional:
		return "Additional"
	elif symType == lldb.eSymbolTypeCompiler:
		return "Compiler"
	elif symType == lldb.eSymbolTypeInstrumentation:
		return "Instrumentation"
	elif symType == lldb.eSymbolTypeUndefined:
		return "Undefined"
	elif symType == lldb.eSymbolTypeObjCClass:
		return "ObjCClass"
	elif symType == lldb.eSymbolTypeObjCMetaClass:
		return "ObjCMetaClass"
	elif symType == lldb.eSymbolTypeObjCIVar:
		return "ObjCIVar"
	elif symType == lldb.eSymbolTypeReExported:
		return "ReExported"
	else:
		return "Unknown"
	
def BroadcastBitString(broadcastClass, broadcastBit):
	if broadcastClass == lldb.SBTarget or broadcastClass == "lldb.target":
		return TargetBroadcastBitString(broadcastBit)
	elif broadcastClass == lldb.SBProcess or broadcastClass == "lldb.process":
		return ProcessBroadcastBitString(broadcastBit)
	elif broadcastClass == lldb.SBCommandInterpreter or broadcastClass == "lldb.commandinterpreter":
		return CommandInterpreterBroadcastBitString(broadcastBit)
	elif broadcastClass == lldb.SBThread or broadcastClass == "lldb.thread":
		return ThreadBroadcastBitString(broadcastBit)
	elif broadcastClass == "lldb.anonymous":
		return "Anonymous"
	else:
		return "Unknown"
	
def CommandInterpreterBroadcastBitString(broadcastBit):
	if broadcastBit == lldb.SBCommandInterpreter.eBroadcastBitThreadShouldExit:
		return "eBroadcastBitThreadShouldExit"
	elif broadcastBit == lldb.SBCommandInterpreter.eBroadcastBitResetPrompt:
		return "eBroadcastBitResetPrompt"
	elif broadcastBit == lldb.SBCommandInterpreter.eBroadcastBitQuitCommandReceived:
		return "eBroadcastBitQuitCommandReceived"
	elif broadcastBit == lldb.SBCommandInterpreter.eBroadcastBitAsynchronousOutputData:
		return "eBroadcastBitAsynchronousOutputData"
	elif broadcastBit == lldb.SBCommandInterpreter.eBroadcastBitAsynchronousErrorData:
		return "eBroadcastBitAsynchronousErrorData"
	else:
		return "Unknown"
	
	
def TargetBroadcastBitString(broadcastBit):
	if broadcastBit == lldb.SBTarget.eBroadcastBitBreakpointChanged:
		return "eBroadcastBitBreakpointChanged"
	elif broadcastBit == lldb.SBTarget.eBroadcastBitModulesLoaded:
		return "eBroadcastBitModulesLoaded"
	elif broadcastBit == lldb.SBTarget.eBroadcastBitModulesUnloaded:
		return "eBroadcastBitModulesUnloaded"
	elif broadcastBit == lldb.SBTarget.eBroadcastBitWatchpointChanged:
		return "eBroadcastBitWatchpointChanged"
	elif broadcastBit == lldb.SBTarget.eBroadcastBitSymbolsLoaded:
		return "eBroadcastBitSymbolsLoaded"
	else:
		return "Unknown"
	
def ProcessBroadcastBitString(broadcastBit):
	if broadcastBit == lldb.SBProcess.eBroadcastBitStateChanged:
		return "eBroadcastBitStateChanged"
	elif broadcastBit == lldb.SBProcess.eBroadcastBitInterrupt:
		return "eBroadcastBitInterrupt"
	elif broadcastBit == lldb.SBProcess.eBroadcastBitSTDOUT:
		return "eBroadcastBitSTDOUT"
	elif broadcastBit == lldb.SBProcess.eBroadcastBitSTDERR:
		return "eBroadcastBitSTDERR"
	elif broadcastBit == lldb.SBProcess.eBroadcastBitProfileData:
		return "eBroadcastBitProfileData"
	elif broadcastBit == lldb.SBProcess.eBroadcastBitStructuredData:
		return "eBroadcastBitStructuredData"
	else:
		return "Unknown"
	
def ThreadBroadcastBitString(broadcastBit):
	if broadcastBit == lldb.SBThread.eBroadcastBitStackChanged:
		return "eBroadcastBitStackChanged"
	elif broadcastBit == lldb.SBThread.eBroadcastBitThreadSuspended:
		return "eBroadcastBitThreadSuspended"
	elif broadcastBit == lldb.SBThread.eBroadcastBitThreadResumed:
		return "eBroadcastBitThreadResumed"
	elif broadcastBit == lldb.SBThread.eBroadcastBitSelectedFrameChanged:
		return "eBroadcastBitSelectedFrameChanged"
	elif broadcastBit == lldb.SBThread.eBroadcastBitThreadSelected:
		return "eBroadcastBitThreadSelected"
	else:
		return "Unknown"
	
def BreakpointEventTypeString(breakpointEventType):
	if breakpointEventType == lldb.eBreakpointEventTypeInvalidType:
		return "eBreakpointEventTypeInvalidType"
	elif breakpointEventType == lldb.eBreakpointEventTypeAdded:
		return "eBreakpointEventTypeAdded"
	elif breakpointEventType == lldb.eBreakpointEventTypeRemoved:
		return "eBreakpointEventTypeRemoved"
	elif breakpointEventType == lldb.eBreakpointEventTypeLocationsAdded:
		return "eBreakpointEventTypeLocationsAdded"
	elif breakpointEventType == lldb.eBreakpointEventTypeLocationsRemoved:
		return "eBreakpointEventTypeLocationsRemoved"
	elif breakpointEventType == lldb.eBreakpointEventTypeLocationsResolved:
		return "eBreakpointEventTypeLocationsResolved"
	elif breakpointEventType == lldb.eBreakpointEventTypeEnabled:
		return "eBreakpointEventTypeEnabled"
	elif breakpointEventType == lldb.eBreakpointEventTypeDisabled:
		return "eBreakpointEventTypeDisabled"
	elif breakpointEventType == lldb.eBreakpointEventTypeCommandChanged:
		return "eBreakpointEventTypeCommandChanged"
	elif breakpointEventType == lldb.eBreakpointEventTypeConditionChanged:
		return "eBreakpointEventTypeConditionChanged"
	elif breakpointEventType == lldb.eBreakpointEventTypeIgnoreChanged:
		return "eBreakpointEventTypeIgnoreChanged"
	elif breakpointEventType == lldb.eBreakpointEventTypeThreadChanged:
		return "eBreakpointEventTypeThreadChanged"
	elif breakpointEventType == lldb.eBreakpointEventTypeAutoContinueChanged:
		return "eBreakpointEventTypeAutoContinueChanged"
	else:
		return "Unknown"
	
def WatchpointValueKindString(watchpointValueKind):
	if watchpointValueKind == lldb.eWatchPointValueKindVariable:
		return "Variable"
	elif watchpointValueKind == lldb.eWatchPointValueKindExpression:
		return "Expression"
	elif watchpointValueKind == lldb.eWatchPointValueKindInvalid:
		return "Invalid"
	else:
		return "Unknown"

#GetWatchValueKind(SBWatchpoint self) → lldb::WatchpointValueKind
#Returns the kind of value that was watched when the watchpoint was created. Returns one of the following eWatchPointValueKindVariable, eWatchPointValueKindExpression, eWatchPointValueKindInvalid.
#
##eBroadcastBitStackChanged = (1 << 0),
##eBroadcastBitThreadSuspended = (1 << 1),
##eBroadcastBitThreadResumed = (1 << 2),
##eBroadcastBitSelectedFrameChanged = (1 << 3),
##eBroadcastBitThreadSelected = (1 << 4)
	
def convert_address(address):
	# Convert the address to hex
	converted_address = int(address, 16)
	
	# Print the converted address
	return hex(converted_address)

# ==============================================================
# Get the description of an lldb object or None if not available
# ==============================================================
def get_description(obj, option=None): # self, 
	"""Calls lldb_obj.GetDescription() and returns a string, or None.

	For SBTarget and SBBreakpointLocation lldb objects, an extra option can be
	passed in to describe the detailed level of description desired:
		o lldb.eDescriptionLevelBrief
		o lldb.eDescriptionLevelFull
		o lldb.eDescriptionLevelVerbose
	"""
	method = getattr(obj, 'GetDescription')
	if not method:
		return None
	if isinstance(obj, lldb.SBTarget) or isinstance(obj, lldb.SBBreakpointLocation):
		if option is None:
			option = lldb.eDescriptionLevelBrief
			
	stream = lldb.SBStream()
	if option is None:
		success = method(stream)
	else:
		success = method(stream, option)
	if not success:
		return None
	return stream.GetData()

class FileInfos():
	
	targetBasename = "<not set>"
	
	def loadFileInfo(self, target, table):
		exe = target.GetExecutable().GetDirectory() + "/" + target.GetExecutable().GetFilename()
		self.targetBasename = os.path.basename(exe)
		
		mach_header = GetFileHeader(exe)
		
		table.addRow("Magic", MachoMagic.to_str(MachoMagic.create_magic_value(mach_header.magic)), hex(mach_header.magic))
		table.addRow("CPU Type", MachoCPUType.to_str(MachoCPUType.create_cputype_value(mach_header.cputype)), hex(mach_header.cputype))
		table.addRow("CPU SubType", str(mach_header.cpusubtype), hex(mach_header.cpusubtype))
		table.addRow("File Type", MachoFileType.to_str(MachoFileType.create_filetype_value(mach_header.filetype)), hex(mach_header.filetype))
		table.addRow("Num CMDs", str(mach_header.ncmds), hex(mach_header.ncmds))
		table.addRow("Size CMDs", str(mach_header.sizeofcmds), hex(mach_header.sizeofcmds))
		table.addRow("Flags", MachoFlag.to_str(MachoFlag.create_flag_value(mach_header.flags)), hex(mach_header.flags))
		
		table.addRow("----", str("-----"), '-----')
		table.addRow("Triple", str(target.GetTriple()), '-')
		
		