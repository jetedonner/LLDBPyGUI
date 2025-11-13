#!/usr/bin/env python3
import lldb
from PyQt6.QtGui import *

from config import *
from helper.debugHelper import logDbgC
from helper.memoryHelper import getMemoryValueAtAddress
from helper.variableHelper import is_int, is_hex_with_prefix, is_float
from ui.base.baseTableWidget import *
from ui.dialogs.dialogHelper import EnterHexAddressDialog


class RedTextDelegate(QStyledItemDelegate):
	def paint(self, painter, option, index):
		# Save painter state
		painter.save()

		# Fill background if selected
		# if option.state & Qt.ItemFlag..ItemIsSelected:
		# painter.fillRect(option.rect, option.palette.highlight())

		# Set text color to red
		painter.setPen(QColor("red"))

		# Draw the text manually
		text = index.data(Qt.ItemDataRole.DisplayRole)
		# Define padding (in pixels)
		padding_left = 10
		padding_top = 0
		padding_right = 0  # negative to shrink from the right
		padding_bottom = 0

		# Adjust the rectangle to add padding
		padded_rect = option.rect.adjusted(padding_left, padding_top, padding_right, padding_bottom)

		# Qt.AlignmentFlag.AlignLeft |
		# option.rect
		painter.drawText(padded_rect, Qt.AlignmentFlag.AlignVCenter, str(text))

		# Restore painter state
		painter.restore()


class RegisterTableWidget(BaseTableWidget):
	redDelegate = RedTextDelegate()
	type = None
	suspendChangeHandler = False

	def __init__(self, driver, type):
		super().__init__()
		self.type = type
		self.driver = driver
		self.context_menu = QMenu(self)
		self.actionChangeValue = self.context_menu.addAction("Change Value")
		self.actionChangeValue.triggered.connect(self.handle_changeValue)
		#		actionDisableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
		#		actionDisableBP.triggered.connect(self.handle_disableBP)
		#
		#		self.context_menu.addSeparator()

		self.setColumnCount(3)
		self.setColumnWidth(0, 128)
		self.setColumnWidth(1, 196)
		self.setColumnWidth(2, 768)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.horizontalHeader().setHighlightSections(False)
		self.setHorizontalHeaderLabels(['Register', 'Value', 'Memory'])
		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		# self.setItemDelegate(RedTextDelegate())
		self.setFont(ConfigClass.font)

		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
		self.setMouseTracking(True)
		self.cellDoubleClicked.connect(self.on_double_click)
		self.itemEntered.connect(self.handle_itemEntered)
		self.itemChanged.connect(self.handle_itemChanged)
		self.setContentsMargins(0, 0, 0, 0)

	def handle_itemEntered(self, item):
		if item.column() == 1:
			# tbl = item.tableWidget()
			sTtValue = self.item(item.row(), 1).text()
			sTtValueType = "Int"
			if is_hex_with_prefix(sTtValue):
				sTtValue = str(int(sTtValue, 16))
			elif is_float(sTtValue):
				sTtValueType = "Float"
				sTtValue = str(float(sTtValue))
			elif is_int(sTtValue):
				sTtValue = str(int(sTtValue))

			item.setToolTip(f"Register: {self.item(item.row(), 0).text()}\nValue: {sTtValue} ({sTtValueType})")

	def handle_itemChanged(self, item):
		if not self.suspendChangeHandler:
			if item.column() == 2:
				hex_string = item.text()
				# logDbgC(f"hex_string: {hex_string} ...")
				# byte_array = bytes.fromhex(hex_string)
				# logDbgC(f"byte_array: {byte_array} ...")
				# # print(byte_array)

				# hex_string = currItm.text()
				logDbgC(f"==========>>>>>>>>>>>>>>> hex_string: {hex_string} ...")
				byte_array = bytes.fromhex(hex_string)
				logDbgC(f"==========>>>>>>>>>>>>>>> byte_array: {byte_array} ...")
				if byte_array is not None and len(byte_array) > 0:
					# new_value = str(byte_array).replace("b'", "").replace("'", "")
					addr = int(self.item(item.row(), 1).text(), 16)
					error = lldb.SBError()
					if addr > 0 and addr < 0xFFFFFFFFFFFFFFFF and byte_array is not None:
						logDbgC(f"==========>>>>>>>>>>>>>>> Writing memory at address 0x{addr:x}: {byte_array}")
						result = self.driver.worker.process.WriteMemory(addr, byte_array, error)
						if not error.Success() or result != len(byte_array):
							logDbgC('==========>>>>>>>>>>>>>>> SBProcess.WriteMemory() failed!')

	# def event(self, event):
	# 	if isinstance(event, QKeyEvent):
	# 		if event.key() == Qt.Key.Key_Return:
	# 			currItm = self.currentItem()
	# 			if currItm.column() == 2:
	# 				if self.isPersistentEditorOpen(currItm):
	# 					self.closePersistentEditor(currItm)
	# 					return True
	# # 					hex_string = currItm.text()
	# # 					logDbgC(f"==========>>>>>>>>>>>>>>> hex_string: {hex_string} ...")
	# # 					byte_array = bytes.fromhex(hex_string)
	# # 					logDbgC(f"==========>>>>>>>>>>>>>>> byte_array: {byte_array} ...")
	# # 					if byte_array is not None and len(byte_array) > 0:
	# # 						# new_value = str(byte_array).replace("b'", "").replace("'", "")
	# # 						addr = int(self.item(currItm.row(), 1).text(), 16)
	# # 						error = lldb.SBError()
	# # 						if addr > 0 and addr < 0xFFFFFFFFFFFFFFFF and byte_array is not None:
	# # 							print(f"==========>>>>>>>>>>>>>>> Writing memory at address 0x{addr:x}: {byte_array}")
	# # 							result = self.driver.worker.process.WriteMemory(addr, byte_array, error)
	# # 							if not error.Success() or result != len(byte_array):
	# # 								print('==========>>>>>>>>>>>>>>> SBProcess.WriteMemory() failed!')
	# # 				else:
	# # 					# self.openPersistentEditor(currItm)
	# # 					self.editItem(currItm)
	#
	# 	return super().event(event)

	# def keyPressEvent(self, event):
	# 	if event.key() == Qt.Key.Key_Return:
	# 		if self.currentItem().column() == 2:
	# 			if self.isPersistentEditorOpen(self.currentItem()):
	# 				hex_string = self.currentItem().text()
	# 				logDbgC(f"==========>>>>>>>>>>>>>>> hex_string: {hex_string} ...")
	# 				byte_array = bytes.fromhex(hex_string)
	# 				logDbgC(f"==========>>>>>>>>>>>>>>> byte_array: {byte_array} ...")
	# 				if byte_array is not None and len(byte_array) > 0:
	# 					# new_value = str(byte_array).replace("b'", "").replace("'", "")
	# 					addr = int(self.item(self.currentItem().row(), 1).text(), 16)
	# 					error = lldb.SBError()
	# 					if addr > 0 and addr < 0xFFFFFFFFFFFFFFFF and byte_array is not None:
	# 						logDbgC(f"==========>>>>>>>>>>>>>>> Writing memory at address 0x{addr:x}: {byte_array}")
	# 						result = self.driver.worker.process.WriteMemory(addr, byte_array, error)
	# 						if not error.Success() or result != len(byte_array):
	# 							logDbgC(f'==========>>>>>>>>>>>>>>> SBProcess.WriteMemory() failed!')
	# 				return
	# 			else:
	# 				self.editItem(self.currentItem())
	# 				return
	# 	super().keyPressEvent(event)

	def on_double_click(self, row, col):
		#		if col in range(3):
		#			self.toggleBPOn(row)
		##			self.sigBPOn.emit(self.item(self.selectedItems()[0].row(), 3).text(), self.item(self.selectedItems()[0].row(), 1).isBPOn)
		if col == 1:
			print(f'Memory for Register: {self.item(row, 0).text()} => {self.item(row, col).text()}')
			# self.window().doReadMemory(int(self.item(row, col).text(), 16))
			bRet = self.window().handle_showMemory(self.item(row, col).text())
		elif col == 2:
			currItm = self.currentItem()
			if currItm.text() != "":
				# self.openPersistentEditor(currItm)
				self.editItem(currItm)
			else:
				self.closePersistentEditor(currItm)
		pass

	def contextMenuEvent(self, event):
		#		for i in dir(event):
		#			print(i)
		#		print(event.pos())
		#		print(self.itemAt(event.pos().x(), event.pos().y()))
		#		print(self.selectedItems())
		# self.currentItem().text() self.itemAt(event.pos().x(), event.pos().y())
		self.context_menu.exec(event.globalPos())
		pass

	def resetContent(self):
		self.suspendChangeHandler = True
		self.setRowCount(0)
		self.suspendChangeHandler = False

	def clearRedDelegate(self):
		for i in range(self.rowCount()):
			self.setItemDelegateForRow(i, None)

	def setRedDelegate(self, idx):
		self.setItemDelegateForRow(idx, self.redDelegate)

	def addRow(self, register, value, memory):
		self.suspendChangeHandler = True
		currRowCount = self.rowCount()
		self.setRowCount(currRowCount + 1)
		self.addItem(currRowCount, 0, str(register))
		self.addItem(currRowCount, 1, str(value))
		self.addItem(currRowCount, 2, str(memory))
		self.setRowHeight(currRowCount, 18)
		self.suspendChangeHandler = False
	# self.setItemDelegateForColumn(1, RedTextDelegate())
	# self.setItemDelegateForRow(currRowCount, self.redDelegate)

	# from PyQt6.QtWidgets import QTableWidgetItem
	# from PyQt6.QtGui import QBrush, QColor
	# from PyQt6.QtCore import Qt

	def addItem(self, row, col, txt):
		item = QTableWidgetItem(txt)
		if not col == 2:
			item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

		item.setForeground(QBrush(QColor("red")))  # 🔴 Set text color to red
		self.setItem(row, col, item)

	def handle_changeValue(self):
		dlg = EnterHexAddressDialog()
		dlg.txtInput.setText(self.item(self.currentRow(), 1).text())
		if dlg.exec():
			self.updateRegisterValue(dlg.txtInput.text())

	def updateRegisterValue(self, newVal="0x12345678"):
		self.suspendChangeHandler = True
		print(f"self.driver.thread: {self.driver.thread} ... ")

		# frame = self.driver.thread.GetFrameAtIndex(0)
		frame = self.driver.regSubWkr.thread.GetFrameAtIndex(
			0)  # [getSubWorker(SubWorkerType.LOAD_REGISTER_SUBWORKER).runSubWorker(self, initTabs=True)

		# Step 1: Access the register set (usually index 0 is GPRs)
		# gpr_set = frame.GetRegisters()[0]  # SBValueList → SBValue (GPRs)

		regName = self.item(self.currentRow(), 0).text()

		idx = 0
		for areg_set in frame.GetRegisters():
			# if areg_set
			print(areg_set)
			if areg_set.GetName() == self.type:
				for aregs in areg_set:
					if aregs.GetName() == regName:
						# # Step 2: Get the specific register (e.g., x1)
						# regName = self.item(self.currentRow(), 0).text()
						print(f"regName: {regName} ...")
						reg = areg_set.GetChildMemberWithName(regName)  # "x1")

						# handle_updateRegisterValue
						# getMemoryValueAtAddress(self.target, self.process,
						#                         child.GetValue()))

						# Step 3: Set new value
						error = lldb.SBError()
						success = reg.SetValueFromCString(newVal, error)
						#
						if success:
							logDbgC(f"Register {regName} updated successfully.")
						else:
							logDbgC(f"Failed to update register {regName}: {error.GetCString()}")

						if self.item(self.currentRow(), 1).text() != reg.GetValue():
							logDbgC(f"reg.GetValueAsAddress(): {reg.GetValueAsAddress()} ...")
							self.item(self.currentRow(), 1).setText(reg.GetValue())
							self.item(self.currentRow(), 2).setText(
								getMemoryValueAtAddress(self.driver.target, None, reg.GetValue()))
							self.setRedDelegate(self.currentRow())
						break
				break
			idx += 1
		self.suspendChangeHandler = False
		return
