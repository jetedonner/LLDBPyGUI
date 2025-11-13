COMMENT_CHAR = "#"
COMMENT_CHARS = ("#")

JMP_MNEMONICS = ("call", "callq", "jmp", "jne", "jz", "je", "jnz", "jle", "jl", "jge", "jg", "b", "bl", "bg", "be",
				 "ble", "blz", "bz", "bne", "bnz", "cbnz", "cbz", "adrp")
JMP_MNEMONICS_EXCLUDE = ("jmpq")
JMP_MNEMONICS_ADDRISSECONDARG = ("cbnz", "cbz", "adrp")
#
# User configurable options
#
CONFIG_ENABLE_COLOR = 1
# light or dark mode
CONFIG_APPEARANCE = "light"
# display the instruction bytes in disassembler output
CONFIG_DISPLAY_DISASSEMBLY_BYTES = 1
# the maximum number of lines to display in disassembler output
CONFIG_DISASSEMBLY_LINE_COUNT = 8
# x/i and disas output customization - doesn't affect context disassembler output
CONFIG_USE_CUSTOM_DISASSEMBLY_FORMAT = 1
# enable all the registers command shortcuts
CONFIG_ENABLE_REGISTER_SHORTCUTS = 1
# display stack contents on context stop
CONFIG_DISPLAY_STACK_WINDOW = 0
CONFIG_DISPLAY_FLOW_WINDOW = 0
# display data contents on context stop - an address for the data must be set with "datawin" command
CONFIG_DISPLAY_DATA_WINDOW = 0
# disassembly flavor 'intel' or 'att' - default is Intel unless AT&T syntax is your cup of tea
CONFIG_FLAVOR = "intel"

# setup the logging level, which is a bitmask of any of the following possible values (don't use spaces, doesn't seem to work)
#
# LOG_VERBOSE LOG_PROCESS LOG_THREAD LOG_EXCEPTIONS LOG_SHLIB LOG_MEMORY LOG_MEMORY_DATA_SHORT LOG_MEMORY_DATA_LONG LOG_MEMORY_PROTECTIONS LOG_BREAKPOINTS LOG_EVENTS LOG_WATCHPOINTS
# LOG_STEP LOG_TASK LOG_ALL LOG_DEFAULT LOG_NONE LOG_RNB_MINIMAL LOG_RNB_MEDIUM LOG_RNB_MAX LOG_RNB_COMM  LOG_RNB_REMOTE LOG_RNB_EVENTS LOG_RNB_PROC LOG_RNB_PACKETS LOG_RNB_ALL LOG_RNB_DEFAULT
# LOG_DARWIN_LOG LOG_RNB_NONE
#
# to see log (at least in macOS)
# $ log stream --process debugserver --style compact
# (or whatever style you like)
CONFIG_LOG_LEVEL = "LOG_NONE"

# removes the offsets and modifies the module name position
# reference: https://lldb.llvm.org/formats.html
CUSTOM_DISASSEMBLY_FORMAT = "\"{${function.initial-function}{${function.name-without-args}} @ {${module.file.basename}}:\n}{${function.changed}\n{${function.name-without-args}} @ {${module.file.basename}}:\n}{${current-pc-arrow} }${addr-file-or-load}: \""

# the colors definitions - don't mess with this
if CONFIG_ENABLE_COLOR:
	RESET = "\033[0m"
	BOLD = "\033[1m"
	UNDERLINE = "\033[4m"
	BLINK = "\033[5m"
	REVERSE = "\033[7m"
	NORMAL = "\033[22m"
	BLACK = "\033[30m"
	RED = "\033[31m"
	GREEN = "\033[32m"
	YELLOW = "\033[33m"
	BLUE = "\033[34m"
	MAGENTA = "\033[35m"
	CYAN = "\033[36m"
	WHITE = "\033[37m"
else:
	RESET = ""
	BOLD = ""
	UNDERLINE = ""
	REVERSE = ""
	BLACK = ""
	RED = ""
	GREEN = ""
	YELLOW = ""
	BLUE = ""
	MAGENTA = ""
	CYAN = ""
	WHITE = ""

# default colors - modify as you wish
# since these are just strings modes can be combined
if CONFIG_APPEARANCE == "light":
	COLOR_REGVAL = BLACK
	COLOR_REGNAME = GREEN
	COLOR_CPUFLAGS = BOLD + UNDERLINE + MAGENTA
	COLOR_SEPARATOR = BOLD + BLUE
	COLOR_HIGHLIGHT_LINE = RED
	COLOR_REGVAL_MODIFIED = RED
	COLOR_SYMBOL_NAME = BLUE
	COLOR_CURRENT_PC = RED
	COLOR_CONDITIONAL_YES = REVERSE + GREEN
	COLOR_CONDITIONAL_NO = REVERSE + RED
	COLOR_HEXDUMP_HEADER = BLUE
	COLOR_HEXDUMP_ADDR = BLACK
	COLOR_HEXDUMP_DATA = BLACK
	COLOR_HEXDUMP_ASCII = BLACK
	COLOR_COMMENT = GREEN
elif CONFIG_APPEARANCE == "dark":
	COLOR_REGVAL = WHITE
	COLOR_REGNAME = GREEN
	COLOR_CPUFLAGS = BOLD + UNDERLINE + MAGENTA
	COLOR_SEPARATOR = CYAN
	COLOR_HIGHLIGHT_LINE = RED
	COLOR_REGVAL_MODIFIED = RED
	COLOR_SYMBOL_NAME = BLUE
	COLOR_CURRENT_PC = RED
	COLOR_CONDITIONAL_YES = REVERSE + GREEN
	COLOR_CONDITIONAL_NO = REVERSE + RED
	COLOR_HEXDUMP_HEADER = BLUE
	COLOR_HEXDUMP_ADDR = WHITE
	COLOR_HEXDUMP_DATA = WHITE
	COLOR_HEXDUMP_ASCII = WHITE
	COLOR_COMMENT = GREEN  # XXX: test and change
else:
	print("[-] Invalid CONFIG_APPEARANCE value.")
