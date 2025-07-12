#!/usr/bin/env python3

import lldb

def launchtest(debugger, command, result, internal_dict):
	# debugger = lldb.SBDebugger.Create()
	print(f"HELLO FROM SCRIPT!!!!")
	debugger.SetAsync(False)

	target = debugger.CreateTarget("./testtarget/amicable_numbers")
	launch_info = lldb.SBLaunchInfo([])
	launch_info.SetStopAtEntry(True)

	process = target.Launch(launch_info, error=lldb.SBError())
