from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget, QComboBox, QHBoxLayout, QLabel

from config import ConfigClass
from helper.debugHelper import logDbgC
from ui.customQt.QClickLabel import QClickLabel


class WidgetModules(QWidget):
	is_second_section_hidden = False
	currentModule = ""
	action_close = None

	def __init__(self):
		super().__init__()

		self.is_second_section_hidden = False
		self.initWidgetModules()

	def initWidgetModules(self):
		self.action_close = QAction("Modules", self)
		self.action_close.setChecked(True)

		self.setContentsMargins(10, 10, 0, 0)
		self.setMaximumHeight(40)
		self.cmbFiles = QComboBox()
		self.cmbFiles.setContentsMargins(0, 0, 0, 0)
		self.cmbFiles.currentIndexChanged.connect(self.handle_module_changed)
		# act = QAction("Testetetete")
		# act.
		self.layFiles = QHBoxLayout()
		self.layFiles.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.layFiles)
		lblFiles = QLabel(f"Modules: ")
		lblFiles.setContentsMargins(0, 0, 0, 0)
		lblFiles.setMaximumWidth(65)
		self.layFiles.addWidget(lblFiles)
		self.layFiles.addWidget(self.cmbFiles)
		self.image_modules_label = QClickLabel(self)
		self.image_modules_label.setContentsMargins(0, 0, 10, 0)
		self.image_modules_label.setToolTip(f"Collapse 'Select Module' combobox")
		self.image_modules_label.setStatusTip(f"Collapse 'Select Module' combobox")
		self.image_modules_label.setPixmap(
			ConfigClass.pixClose.scaled(QSize(18, 18), Qt.AspectRatioMode.KeepAspectRatio,
										Qt.TransformationMode.SmoothTransformation))

		self.act = self.image_modules_label.clicked.connect(self.handle_hideModulesSection)
		self.image_modules_label.clicked.connect(self.action_close.trigger)  # self.handle_hideModulesSection)

		self.image_modules_label.setMaximumWidth(32)
		self.layFiles.addWidget(self.image_modules_label)

	def toggleViewAction(self):
		return self.action_close

	bDisableLoad = False

	def select_module(self, modName, setCmb=False):
		# logDbgC(f"select_module => modName: {modName} / self.currentModule: {self.currentModule} / setCmb: {setCmb} ...")
		if modName == self.currentModule:
			return False
		# else:
		#     self.currentModule = modName

		# if modName in self.window().wdtDisassembly.disassemblies:
		#     logDbgC(f"modName IS in disassemblies (0) ...")
		# else:
		#     logDbgC(f"modName NOT in disassemblies (0) ...")
		#
		# if modName in self.window().wdtDisassembly.disassemblies.keys():
		#     logDbgC(f"modName IS in disassemblies (1) ...")
		# else:
		#     logDbgC(f"modName NOT in disassemblies (1) ...")

		idx = 0
		for modNameKey in self.window().wdtDisassembly.disassemblies.keys():
			if modNameKey == modName:
				if setCmb:
					self.bDisableLoad = True

				self.cmbFiles.setCurrentIndex(idx)

				if setCmb:
					self.bDisableLoad = False
					# break
				# else:
				#     self.cmbFiles.setCurrentIndex(idx)
				#     # self.handle_module_changed(idx)
				break
			idx += 1
		self.currentModule = modName
		return True

	def handle_module_changed(self, currentIdx):
		# idx = 0
		# logDbgC(f"handle_module_changed: currentIdx: {currentIdx}, self.bDisableLoad: {self.bDisableLoad} ...")
		if self.bDisableLoad:
			return

		self.window().wdtDisassembly.wdtFunctionList.lstStrings.resetContent()
		modName = self.cmbFiles.itemText(currentIdx).split(' (')[0].strip()
		# logDbgC(f"handle_module_changed: modName: {modName} / self.currentModule: {self.currentModule} / currentIdx: {currentIdx} ...")
		# if modName == self.currentModule:
		#     return
		# else:
		#     self.currentModule = modName

		self.currentModule = modName
		disassemblies = self.window().wdtDisassembly.disassemblies
		# logDbgC(f"handle_module_changed({currentIdx}) => {modName} / disassemblies: {len(disassemblies)} ...")
		if modName in disassemblies:
			# logDbgC(disassemblies[modName])
			self.window().wdtDisassembly.resetContent()
			self.window().wdtDisassembly.lastModuleKey = modName
			print(disassemblies)
			for key, value in disassemblies[modName].items():
				if key != "connections" and key != "symbols":
					self.window().wdtDisassembly.handle_loadSymbol(key, False)
					self.window().wdtDisassembly.lastSymbolKey = key
				if key == "connections":
					# logDbgC(f"connections => value: {value} ...")
					self.window().wdtDisassembly.handle_workerFinished(value, modName, {}, self.window().driver.getPC(),
																	   False)
					continue

				if key == "symbols":
					self.window().handle_workerFinished2(None, modName, value)
					continue

				for key2, value2 in value.items():
					if key == "__cstring":
						self.window().wdtDisassembly.handle_loadString(value2[0], key2, value2[1], False)
						# pass
					else:
						self.window().wdtDisassembly.handle_loadSymbol(key2, False)
						self.window().wdtDisassembly.lastSubSymbolKey = key2
						for key3, value3 in value2.items():
							self.window().wdtDisassembly.handle_loadInstruction(value3, None, False)

			# self.window().setDbgTabLbl(f"{modName}")
			self.window().wdtDisassembly.setCurrentModule(modName)
			logDbgC(f"self.window().treBreakpoints.treBP.nextViewAddress: {self.window().treBreakpoints.treBP.nextViewAddress} ...")
			bFound = self.window().wdtDisassembly.setPC(self.window().driver.getPC(), True)
			print(self.window().driver.worker.target)
			print(self.window().driver.worker.module)
			self.window().get_breakpoints_for_module(self.window().driver.worker.target,
													 modName)  # self.window().driver.worker.module)
			# self.window().wdtDisassembly.lastSubSymbolKey = key2

	def loadModulesCallback(self, frame, modules=None):
		# logDbgC(f"Reloading modules ...")
		self.cmbFiles.clear()
		if modules is not None and len(modules) > 0:
			for i in range(len(modules)):
				self.cmbFiles.addItem(modules[i].GetFileSpec().GetFilename() + " (" + str(i) + ")")
				if i == 0:
					self.currentModule = modules[i].GetFileSpec().GetFilename()
		else:
			self.cmbFiles.addItem(
				frame.GetModule().GetFileSpec().GetFilename() + " (" + str(frame.GetFrameID()) + ")")
			self.currentModule = frame.GetModule().GetFileSpec().GetFilename()

		showModules = self.cmbFiles.count() > 0
		# logDbgC(f"showModules: {showModules}")
		self.setModuleVisible(showModules)

	def setModuleVisible(self, isVisible=True):
		if self.is_second_section_hidden == isVisible:
			# logDbgC(f"self.is_second_section_hidden: {self.is_second_section_hidden} / isVisible: {isVisible}")
			self.toggle_second_section()
			self.is_second_section_hidden = not isVisible
		else:

			sizes = self.parentWidget().sizes()
			# logDbgC(f"sizes: {sizes}")
			if sizes[0] <= 0:
				# self.original_sizes = sizes  # Store the original size to restore it later
				new_sizes = [(self.original_sizes[0] if not self.original_sizes is None and len(
					self.original_sizes) > 0 else 30), sizes[1], sizes[2]]
				# logDbgC(f"new_sizes: {new_sizes}")
				self.parentWidget().setSizes(new_sizes)
				self.is_second_section_hidden = not isVisible
			pass

	def handle_hideModulesSection(self):
		self.action_close.setChecked(not self.action_close.isChecked())
		self.toggle_second_section()
		pass

	def toggle_second_section(self):
		sizes = self.parentWidget().sizes()

		self.original_sizes = sizes
		new_sizes = [0, sizes[1]]  # , sizes[2]]
		self.parentWidget().setSizes(new_sizes)
		self.is_second_section_hidden = True

	def resetContent(self):
		self.cmbFiles.clear()
		self.currentModule = ""
