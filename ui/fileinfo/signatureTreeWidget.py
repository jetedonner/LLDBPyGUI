#!/usr/bin/env python3
import lldb

from config import *
from helper.debugHelper import logDbgC
from lib.thirdParty import machofile
from ui.base.baseTreeWidget import *


class SignatureTreeWidget(BaseTreeWidget):

	def __init__(self, driver):
		super().__init__(driver)

		# self.context_menu = QMenu(self)

		self.setHeaderLabels(['Key', 'Value', 'Type'])
		self.setFont(ConfigClass.font)
		self.header().resizeSection(0, 396)
		self.header().resizeSection(1, 512)
		self.header().resizeSection(2, 96)

	# def contextMenuEvent(self, event):
	# 	self.context_menu.exec(event.globalPos())

	def loadSignatureInfo(self):
		macho = machofile.UniversalMachO(
			file_path=ConfigClass.testTarget)  # '/Volumes/Data/dev/python/LLDBGUI/_testtarget/cocoa_windowed_objc2')
		macho.parse()

		code_signature_info = macho.get_code_signature_info()
		logDbgC(code_signature_info)
		print(f"BEFORE code_signature_info: {code_signature_info} ...")

		self.child_item_cs = QTreeWidgetItem(self, ["Code Signature", '', ''])
		self.child_item_cs.setExpanded(True)
		self.populate_tree(code_signature_info, self.child_item_cs)

		self.child_item_lct = QTreeWidgetItem(self, ["Load Command Table", '', ''])

		load_commands = macho.get_load_commands()
		# print(f"load_commands: {load_commands}")

		all_load_commands = macho.get_load_commands(None, True)  # .parse_all_load_commands()
		# print(f"all_load_commands: {all_load_commands}")

		self.child_item_lcs = QTreeWidgetItem(self, ["Load Command (Set)", '', ''])

		formatted_load_commands_set = macho.get_load_commands_set(None, True)
		# print(f"formatted_load_commands_set: {formatted_load_commands_set} ...")
		self.child_item_lcs.setExpanded(True)
		self.populate_tree(formatted_load_commands_set, self.child_item_lcs, True)

		is_fat_binary = macho._is_fat_binary()
		# print(f"is_fat_binary: {is_fat_binary} ...")

		self.child_item_lct.setExpanded(True)
		self.populate_tree(all_load_commands, self.child_item_lct)

	# def loadSignatureInfo(self):
	# 	# macho = machofile.UniversalMachO(file_path=ConfigClass.testTarget) # '/Volumes/Data/dev/python/LLDBGUI/_testtarget/cocoa_windowed_objc2')
	# 	macho = machofile.MachO(file_path=ConfigClass.testTarget)
	# 	macho.parse()
	# 	# macho.code_signature_info()
	# 	code_signature_info = macho.code_signature_info # macho.get_code_signature_info()
	# 	logDbgC(code_signature_info)
	# 	print(f"BEFORE code_signature_info: {code_signature_info} ...")
	#
	# 	self.child_item_cs = QTreeWidgetItem(self, ["Code Signature", '', ''])
	# 	self.child_item_cs.setExpanded(True)
	# 	self.populate_tree(code_signature_info, self.child_item_cs)
	#
	# 	self.child_item_lct = QTreeWidgetItem(self, ["Load Command Table", '', ''])
	#
	# 	load_commands = macho.load_commands #.get_load_commands()
	# 	# print(f"load_commands: {load_commands}")
	#
	# 	all_load_commands = macho.load_commands #get_load_commands(None, True) #.parse_all_load_commands()
	# 	# print(f"all_load_commands: {all_load_commands}")
	#
	# 	self.child_item_lcs = QTreeWidgetItem(self, ["Load Command (Set)", '', ''])
	#
	# 	formatted_load_commands_set = macho.load_commands_set #.get_load_commands_set(None, True)
	# 	# print(f"formatted_load_commands_set: {formatted_load_commands_set} ...")
	# 	self.child_item_lcs.setExpanded(True)
	# 	self.populate_tree(formatted_load_commands_set, self.child_item_lcs, True)
	#
	# 	# is_fat_binary = macho._is_fat_binary()
	# 	# # print(f"is_fat_binary: {is_fat_binary} ...")
	#
	# 	self.child_item_lct.setExpanded(True)
	# 	self.populate_tree(all_load_commands, self.child_item_lct)

	def populate_tree(self, d, parent=None, addIdxNode=True):
		if isinstance(d, dict):
			for key, value in d.items():
				if isinstance(value, (bool, int, float, str)):
					if isinstance(value, int):
						sVal = f"{hex(value)} ({str(value)})"
					else:
						sVal = f"{str(value)}"
					QTreeWidgetItem(parent, [str(key), sVal, ''])
				# 	if addIdxNode:
				# 		QTreeWidgetItem(parent, ['', str(d), ''])
				# else:
				# 	QTreeWidgetItem(parent, [str(d), '', ''])
				elif isinstance(value, dict):
					child_item = QTreeWidgetItem(parent, [str(key), '', ''])
					child_item.setExpanded(True)
					self.populate_tree(value, child_item)
				elif isinstance(value, list):
					child_item = QTreeWidgetItem(parent, [str(key), '', ''])
					child_item.setExpanded(True)
					for i, elem in enumerate(value):
						# if addIdxNode:
						sub_item = QTreeWidgetItem(child_item, [f"[{i}]", '', ''])
						self.populate_tree(elem, sub_item)
		# 				else:
		# 					self.populate_tree(elem, parent)
		elif isinstance(d, (bool, int, float, str)):
			QTreeWidgetItem(parent, ['', str(d), ''])
		# if addIdxNode:
		# 	QTreeWidgetItem(parent, ['', str(d), ''])
		# else:
		# 	QTreeWidgetItem(parent, [str(d), '', ''])

		elif isinstance(d, list):
			for i, elem in enumerate(d):
				# if addIdxNode:
				# 	sub_item = QTreeWidgetItem(parent, [f"[{i}]", '', ''])
				# 	sub_item.setExpanded(True)
				# 	self.populate_tree(elem, sub_item)
				# else:
				# 	self.populate_tree(elem, parent, addIdxNode)
				if isinstance(elem, (bool, int, float, str)):
					# QTreeWidgetItem(parent, ['', str(d), ''])
					sub_item = QTreeWidgetItem(parent, [f"[{i}]", str(elem), ''])
				else:
					sub_item = QTreeWidgetItem(parent, [f"[{i}]", '', ''])
					sub_item.setExpanded(True)
					self.populate_tree(elem, sub_item)
