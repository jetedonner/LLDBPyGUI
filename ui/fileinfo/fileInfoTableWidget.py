#!/usr/bin/env python3
import lldb

from config import *
from helper.debugHelper import logDbgC
from helper.memoryHelper import *
from lib.fileInfos import MachoMagic, MachoCPUType, MachoFileType, MachoFlag, FileInfos
from lib.thirdParty import machofile
from ui.base.baseTableWidget import *


class FileInfosTableWidget(BaseTableWidget):

	def __init__(self):
		super().__init__()
		self.context_menu = QMenu(self)

		self.setColumnCount(3)
		self.setColumnWidth(0, 198)
		self.setColumnWidth(1, 512)
		self.setColumnWidth(2, 128)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.horizontalHeader().setHighlightSections(False)
		self.setHorizontalHeaderLabels(['Key', 'Value', 'Raw'])
		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.setFont(ConfigClass.font)

		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
		self.cellDoubleClicked.connect(self.on_double_click)

	# self.testMachofile()

	def loadFileInfos(self, mach_header, targetRet):
		self.resetContent()
		size_info = FileInfos.get_target_filesize(targetRet)

		# targetRet.process.SaveCore(f"/Users/dave/Desktop/testCoreFile.txt")
		self.addRow("Process-ID", f"{str(targetRet.process.GetProcessID())}", f"{hex(targetRet.process.GetProcessID())}")
		self.addRow("--- HEADER ---", str("-----"), '-----', True)
		self.addRow("Filename", str(FileInfos.getTargetFilename(targetRet)), "")
		# {size_info['kilobytes']} KB = >
		self.addRow("Size", f"{format_file_size(size_info['bytes'])}", f"({size_info['bytes']} bytes)")
		self.addRow("--- EXECUTABLE ---", str("-----"), '-----', True)
		self.addRow("Magic", MachoMagic.to_str(MachoMagic.create_magic_value(mach_header.magic)),
					hex(mach_header.magic))
		self.addRow("CPU Type", MachoCPUType.to_str(MachoCPUType.create_cputype_value(mach_header.cputype)),
					hex(mach_header.cputype))
		self.addRow("CPU SubType", str(mach_header.cpusubtype), hex(mach_header.cpusubtype))
		self.addRow("File Type", MachoFileType.to_str(MachoFileType.create_filetype_value(mach_header.filetype)),
					hex(mach_header.filetype))
		self.addRow("Num CMDs", str(mach_header.ncmds), hex(mach_header.ncmds))
		self.addRow("Size CMDs", str(mach_header.sizeofcmds), hex(mach_header.sizeofcmds))
		self.addRow("Flags", MachoFlag.to_str(MachoFlag.create_flag_value(mach_header.flags)), hex(mach_header.flags))

		# self.addRow("----", str("-----"), '-----')
		self.addRow("Triple", str(self.get_os_from_target(targetRet)), '')  # GetTriple()
		self.testMachofile()
		QApplication.processEvents()

	def get_os_from_target(self, target):
		if not target.IsValid():
			return "Invalid target"

		module = target.GetModuleAtIndex(0)
		if not module.IsValid():
			return "Invalid module"

		triple = module.GetTriple()
		return triple  # This often includes the correct OS

	def on_double_click(self, row, col):
		#		if col in range(3):
		#			self.toggleBPOn(row)
		##			self.sigBPOn.emit(self.item(self.selectedItems()[0].row(), 3).text(), self.item(self.selectedItems()[0].row(), 1).isBPOn)
		pass

	def contextMenuEvent(self, event):
		#		for i in dir(event):
		#			print(i)
		#		print(event.pos())
		#		print(self.itemAt(event.pos().x(), event.pos().y()))
		#		print(self.selectedItems())
		#		self.context_menu.exec(event.globalPos())
		pass

	def resetContent(self):
		self.setRowCount(0)

	def addRow(self, key, value, raw, bold=False):
		currRowCount = self.rowCount()
		self.setRowCount(currRowCount + 1)
		self.addItem(currRowCount, 0, str(key), bold)
		self.addItem(currRowCount, 1, str(value), bold)
		self.addItem(currRowCount, 2, str(raw), bold)
		self.setRowHeight(currRowCount, 18)

	def addItem(self, row, col, txt, bold=False):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Qt.ItemFlag.ItemIsSelectable)
		if bold:
			item.setFont(ConfigClass.fontBold)
		self.setItem(row, col, item)

	def testMachofile(self):
		self.addRow("--- FILE INTEGRITY ---", str("-----"), '-----', True)
		macho = machofile.UniversalMachO(file_path='/Volumes/Data/dev/python/LLDBGUI/_testtarget/cocoa_windowed_objc2')
		macho.parse()

		# Raw data (default)
		general_info = macho.get_general_info()
		# Returns: {'Filename': str, 'Filesize': int, 'MD5': str, 'SHA1': str, 'SHA256': str}
		logDbgC(f"general_info: {general_info}")
		# for key, value in general_info.items()[2:]:
		for key, value in list(general_info.items())[2:]:
			print(f"{key}: {value}")
			self.addRow(str(key), str(value), "")

		uuid = macho.get_uuid()
		self.addRow("UUID", str(uuid), "")
		self.addRow("--- HASHES ---", str("-----"), '-----', True)

		similarity_hashes = macho.get_similarity_hashes()
		for key, value in similarity_hashes.items():
			self.addRow(str(key), str(value), "")
		# logDbgC(similarity_hashes)

		entry_point = macho.get_entry_point()
		logDbgC(entry_point)

		version_info = macho.get_version_info(formatted=True)
		logDbgC(version_info)

		code_signature_info = macho.get_code_signature_info()
		logDbgC(code_signature_info)
		self.pretty(code_signature_info)

	def pretty(self, d, indent=0):
		for key, value in d.items():
			print('\t' * indent + str(key))
			if isinstance(value, dict):
				self.pretty(value, indent + 1)
			else:
				print('\t' * (indent + 1) + str(value))
