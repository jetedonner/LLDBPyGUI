import lldb

debugger = lldb.SBDebugger.Create()
debugger.SetAsync(False)

binary_path = "/path/to/hardened.app/Contents/MacOS/executable"
target = debugger.CreateTargetWithFileAndArch(binary_path, "arm64")

if not target.IsValid():
	print("Failed to create target.")

funcs = target.FindFunctions("main")
if funcs.GetSize() > 0:
	symbol = funcs.GetContextAtIndex(0).GetSymbol()
	insts = target.ReadInstructions(symbol.GetStartAddress(), symbol.GetEndAddress())
	for inst in insts:
		print(inst)
