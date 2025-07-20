import lldb
import shlex

FLAGS = [
	['CF', 'Carry Flag'],
	[None, 'Reserved'],
	['PF', 'Parity Flag'],
	[None, 'Reserved'],
	['AF', 'Adjust Flag'],
	[None, 'Reserved'],
	['ZF', 'Zero Flag'],
	['SF', 'Sign Flag'],
	['TF', 'Trap Flag'],
	['IF', 'Interrupt Enable Flag'],
	['DF', 'Direction Flag'],
	['OF', 'Overflow Flag'],
	['IOPL_H', 'I/O privilege level High bit'],
	['IOPL_L', 'I/O privilege level Low bit'],
	['NT', 'Nested Task Flag'],
	[None, 'Reserved'],

	# eflags
	['RF', 'Resume Flag'],
	['VM', 'Virtual 8086 mode flag'],
	['AC', 'Alignment check'],
	['VIF', 'Virtual interrupt flag'],
	['VIP', 'Virtual interrupt pending'],
	['ID', 'Able to use CPUID instruction'],
	# 22-31 reserved

	# rflags 32-63 reserved
]

def parse_flags(val):
	""" Returns list of set flags """
	set_flags = list()

	for bit, desc in enumerate(FLAGS):
		if val & (1 << bit) and desc[0] is not None:
			set_flags.append(desc)

	return set_flags

def flag_list_to_str(l):
	return ' '.join((desc[0] for desc in l))

def get_flags_reg(frame):
	grs = list()
	
	for rs in frame.GetRegisters():
		if rs.GetName().lower() == 'general purpose registers':
			grs = rs
			break

	for reg in grs:
		if 'flags' in reg.GetName():
			return reg

	return None

def fmt_lst(fl_reg, lst):
	val = fl_reg.GetValueAsUnsigned()
	lst = [x.upper() for x in lst]
	found = list()

	for bit, desc in enumerate(FLAGS):
		if desc[0] is not None and desc[0] in lst:
			lst.remove(desc[0])
			found.append([desc[0], bool(val & (1 << bit))])

	ret = list()
	# lst must be empty at this point
	# anything left wasn't found
	if lst:
		ret.append('ERROR: Unknown flags: [%s]' % ' '.join(lst))

	for x in found:
		ret.append('%s: %d'%(x[0], int(x[1])))

	return '\n'.join(ret)

def fmt_shortNG(fl_reg):
	val = fl_reg.GetValueAsUnsigned()
	reg_print_width = fl_reg.GetByteSize() * 2
	descs = parse_flags(val)

	# print(f"============>>>>>>>>>>>>>> flag_list_to_str(descs): {flag_list_to_str(descs)}")
	# return ('%s: 0x%.*x [%s]' % (
	# 	fl_reg.GetName(), 		# register name
	# 	reg_print_width, 		# how many hex digits to print
	# 	val, 					# value
	# 	flag_list_to_str(descs) # parsed value (list of set flags)
	# ))
	return flag_list_to_str(descs)


def fmt_short(fl_reg):
	val = fl_reg.GetValueAsUnsigned()
	reg_print_width = fl_reg.GetByteSize() * 2
	descs = parse_flags(val)

	print(f"============>>>>>>>>>>>>>> flag_list_to_str(descs): {flag_list_to_str(descs)}")
	return ('%s: 0x%.*x [%s]' % (
		fl_reg.GetName(), 		# register name
		reg_print_width, 		# how many hex digits to print
		val, 					# value
		flag_list_to_str(descs) # parsed value (list of set flags)
	))

# def decode_rflags_command(debugger, command, result, dict):

def pfl_cmd(debugger, command, result, internal_dict):
	# print(f"Hello PFL Command!")
	target = debugger.GetSelectedTarget()
	process = target.GetProcess()
	thread = process.GetSelectedThread()
	frame = thread.GetSelectedFrame()

	fl_reg = get_flags_reg(frame)
	if fl_reg is None:
		print("ERROR: Cant find flags register!")
		return

	# lst = shlex.split(command)

	# # ret = ''
	#
	# if lst:
	# 	# dirty argparse hack
	# 	# XXX handle flags and eflags diff for fun? :)
	# 	if '-l' in lst:
	# 		lst = [desc[0] for desc in FLAGS if desc[0] is not None]
	#
	# 	ret = fmt_lst(fl_reg, lst)
	# else:
	# 	ret = fmt_short(fl_reg)
	#
	# print(ret)

	ret = fmt_shortNG(fl_reg)
	return ret

def __lldb_init_module(debugger, dict):
	# debugger.HandleCommand('command script add -f decode_rflags.decode_rflags_command drf')
	debugger.HandleCommand('command script add -f prettyflags.pfl_cmd pfl')
	print('The "pfl_cmd" command has been loaded.')