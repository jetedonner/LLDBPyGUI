import lldb

def decode_rflags_command(debugger, command, result, dict):
    target = debugger.GetSelectedTarget()
    if not target:
        result.AppendError("No target selected.")
        return

    process = target.GetProcess()
    if not process:
        result.AppendError("No process running.")
        return

    thread = process.GetSelectedThread()
    if not thread:
        result.AppendError("No thread selected.")
        return

    frame = thread.GetSelectedFrame()
    if not frame:
        result.AppendError("No frame selected.")
        return

    rflags_reg = frame.FindRegister("rflags")
    if not rflags_reg:
        result.AppendError("Could not find rflags register.")
        return

    rflags_value = rflags_reg.GetValueAsUnsigned()

    flags = []

    # Define the flags and their bit positions
    # (Bit 0 to 21 are the most common ones to check)
    if (rflags_value >> 0) & 1: flags.append("CF (Carry)")
    else: flags.append("NC (No Carry)")

    # Bit 1 is reserved and always 1
    # if (rflags_value >> 1) & 1: flags.append("1 (Reserved)")

    if (rflags_value >> 2) & 1: flags.append("PF (Parity Even)")
    else: flags.append("PO (Parity Odd)")

    # Bit 3 is reserved and always 0

    if (rflags_value >> 4) & 1: flags.append("AF/NA (Auxiliary Carry)")
    else: flags.append("NA/AF (No Auxiliary Carry)")

    # Bit 5 is reserved and always 0

    if (rflags_value >> 6) & 1: flags.append("ZF/NZ (Zero)")
    else: flags.append("NZ/ZF (Not Zero)")

    if (rflags_value >> 7) & 1: flags.append("SF/PL (Sign Negative)")
    else: flags.append("PL/FL (Sign Positive)")

    if (rflags_value >> 8) & 1: flags.append("TF/NTF (Trap/Single Step)")
    else: flags.append("NTF/TF (No Trap/Single Step)")

    if (rflags_value >> 9) & 1: flags.append("IF/ID (Interrupt Enable)")
    else: flags.append("ID/IF (Interrupt Disable)")

    if (rflags_value >> 10) & 1: flags.append("DF/DU (Direction Down)")
    else: flags.append("DU/DF (Direction Up)")

    if (rflags_value >> 11) & 1: flags.append("OF/NO (Overflow)")
    else: flags.append("NO/OF (No Overflow)")

    iopl = (rflags_value >> 12) & 0x3 # 2 bits
    flags.append(f"IOPL={iopl}")

    if (rflags_value >> 14) & 1: flags.append("NT/NNT (Nested Task)")
    else: flags.append("NNT/NT (Not Nested Task)")

    # Bit 15 is reserved and always 0

    if (rflags_value >> 16) & 1: flags.append("RF (Resume Flag)")

    if (rflags_value >> 17) & 1: flags.append("VM (Virtual-8086 Mode)")

    if (rflags_value >> 18) & 1: flags.append("AC (Alignment Check)")

    if (rflags_value >> 19) & 1: flags.append("VIF (Virtual Interrupt)")

    if (rflags_value >> 20) & 1: flags.append("VIP (Virtual Interrupt Pending)")

    if (rflags_value >> 21) & 1: flags.append("ID (ID Flag)")

    result.AppendMessage(f"RFLAGS: 0x{rflags_value:016x} [{', '.join(flags)}]")


def __lldb_init_module(debugger, dict):
    debugger.HandleCommand('command script add -f decode_rflags.decode_rflags_command decode_rflags')
    debugger.HandleCommand('command script add -f decode_rflags.decode_rflags_command drf')
    # print('The "decode_rflags" / "drf" command has been loaded...')