#!/usr/bin/env python3
import lldb
import sys
import os

def main():
    exe_path = "./hello_library_exec"  # Replace with your binary
    if not os.path.exists(exe_path):
        print(f"❌ Executable not found: {exe_path}")
        return

    # Create debugger instance
    debugger = lldb.SBDebugger.Create()
    debugger.SetAsync(False)

    # Create target
    target = debugger.CreateTarget(exe_path)
    if not target.IsValid():
        print("❌ Failed to create target.")
        return

    # Launch process and stop at entry
    launch_info = lldb.SBLaunchInfo(None)
    launch_info.SetExecutableFile(lldb.SBFileSpec(exe_path), True)
    launch_info.SetLaunchFlags(lldb.eLaunchFlagStopAtEntry)

    error = lldb.SBError()
    process = target.Launch(launch_info, error)
    if not process.IsValid():
        print(f"❌ Launch failed: {error.GetCString()}")
        return

    # Get current thread and frame
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()

    # Disassemble current function
    function = frame.GetFunction()
    if not function.IsValid():
        print("⚠️ No valid function at current frame.")
        return

    instructions = function.GetInstructions(target)
    for inst in instructions:
        addr = inst.GetAddress().GetLoadAddress(target)
        mnemonic = inst.GetMnemonic(target)
        operands = inst.GetOperands(target)
        comment = inst.GetComment(target)
        print(f"0x{addr:x}: {mnemonic} {operands} ; {comment}")

    # Cleanup
    lldb.SBDebugger.Destroy(debugger)

if __name__ == "__main__":
    main()
