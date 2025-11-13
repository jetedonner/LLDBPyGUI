import re

import lldb


class TrySwift():
	debugger = None

	def __init__(self, debugger=None):
		super().__init__()
		self.debugger = debugger

	def tryswift(self, ):
		# Create debugger instance
		# debugger = lldb.SBDebugger.Create()
		self.debugger.SetAsync(False)

		# Load your compiled .app binary (usually in Contents/MacOS)
		target = self.debugger.CreateTarget(
			"./_testtarget/LLDBGUISwiftTestApp/Build/Products/Debug/LLDBGUISwiftTestApp.app/Contents/MacOS/LLDBGUISwiftTestApp")

		main_bp = target.BreakpointCreateByName("main")
		main_bp.SetOneShot(True)
		res = lldb.SBCommandReturnObject()
		ci = self.debugger.GetCommandInterpreter()

		# settings
		# ci.HandleCommand("settings set target.x86-disassembly-flavor " + CONFIG_FLAVOR, res)
		ci.HandleCommand(f'breakpoint set -a 0x100035e9c', res)  # 0x100035f10', res)
		print(f"res: {res} ...")

		# 0x100035f10

		# bp = target.BreakpointCreateByName("applicationDidFinishLaunching:")

		process = target.LaunchSimple(None, None, "/")

		symbol = target.FindFunctions("viewDidLoad")[0].GetSymbol()
		insts = symbol.GetInstructions(target)
		for inst in insts:
			print(inst)

		# [0x5464

		symbol2 = target.FindFunctions("testButtonAction")[0].GetSymbol()
		insts2 = symbol2.GetInstructions(target)
		for inst2 in insts2:
			print(inst2)
		# bp2 = target.BreakpointCreateByName("testButtonAction:")

		bp3 = target.BreakpointCreateByAddress(int("0x0000000100035464", 16))
		# breakpoint
		# set - a
		# 0x0000000100035464

		objc_method_pattern = re.compile(r"-\[\w+\s+\w+\]")  # matches -[Class method:]
		for module in target.module_iter():
			if module.GetFileSpec().GetFilename() == "LLDBGUISwiftTestApp.debug.dylib":  # or module.GetFileSpec().GetFilename() == "LLDBGUISwiftTestApp":
				for symbol in module:
					name = symbol.GetName()
					print(f"Symbol found: {name} ...")
					if name and objc_method_pattern.match(name):
						print("Possible IBAction:", name)

		# ci.HandleCommand('po class_copyMethodList(NSClassFromString("ViewController"), nil)', res)
		# print(res.GetOutput())
