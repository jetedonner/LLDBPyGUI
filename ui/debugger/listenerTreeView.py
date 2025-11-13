from datetime import datetime

import lldb
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMenu, QTreeWidgetItem, QLabel, QVBoxLayout, QWidget, QSizePolicy, QGroupBox, QHBoxLayout, \
	QSplitter, QApplication
from lldb import *

from config import ConfigClass
from lib.fileInfos import BroadcastBitString, get_description, BreakpointEventTypeString
from lib.settings import SettingsValues
from ui.base.baseTreeWidget import BaseTreeWidget


class ListenerLogTreeWidget(BaseTreeWidget):
	#	self.lblModule.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
	#
	#	self.lblModule.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
	# sigSTDOUT = pyqtSignal(str)
	bp_loc = 0

	def getTimestamp(self):
		now = datetime.now()
		# self.setHelper.getValue(SettingsValues.EventListenerTimestampFormat)
		return now.strftime(
			self.setHelper.getValue(SettingsValues.EventListenerTimestampFormat))  # "%H:%M:%S") # "%Y-%m-%d %H:%M:%S"

	#		print(formatted_date)

	def __init__(self, driver, setHelper):
		super().__init__(driver)
		# self.driver = driver
		self.bp_loc = 0
		self.setHelper = setHelper

		self.setContentsMargins(0, 0, 0, 0)

		#       self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
		self.context_menu = QMenu(self)
		actionShowInfos = self.context_menu.addAction("Show infos")

		self.actionExpandAll = self.context_menu.addAction("Expand All")
		self.actionExpandAll.triggered.connect(self.expandAll_clicked)
		self.actionCollapseAll = self.context_menu.addAction("Collapse All")
		self.actionCollapseAll.triggered.connect(self.collapseAll_clicked)

		self.context_menu.addSeparator()

		self.actionClear = self.context_menu.addAction("Clear events")
		self.actionClear.triggered.connect(self.clear_clicked)

		self.setFont(ConfigClass.font)
		self.setHeaderLabels(['Event-Type', 'Timestamp / Values'])
		self.header().resizeSection(0, 312)
		self.header().resizeSection(1, 1200)

	#		self.verticalScrollBar().setPolicy(QScrollBar.Policy.ScrollBarAsNeeded)
	#		self.horizontalScrollBar().setPolicy(QScrollBar.Policy.ScrollBarAsNeeded)

	def clear_clicked(self):
		self.clear()

	def expandAll_clicked(self):
		self.expandAll()

	def collapseAll_clicked(self):
		self.collapseAll()

	def addNewEvent(self, event, extObj):
		# logDbgC(f"listenerTreeView.addNewEvent(...) ...")
		sectionNode = QTreeWidgetItem(self, [BroadcastBitString(str(event.GetBroadcasterClass()), event.GetType()),
											 self.getTimestamp()])

		subSectionNode = QTreeWidgetItem(sectionNode, ["Type: ",
													   BroadcastBitString(str(event.GetBroadcasterClass()),
																		  event.GetType()) + " (" + str(
														   event.GetType()) + ")"])
		subSectionNode = QTreeWidgetItem(sectionNode, ["BroadcasterClass: ", str(event.GetBroadcasterClass())])
		subSectionNode = QTreeWidgetItem(sectionNode, ["DataFlavor: ", str(event.GetDataFlavor())])
		#		subSectionNode = QTreeWidgetItem(sectionNode, ["CStringFromEvent: ", str(event.GetCStringFromEvent(event))])
		subSectionNode = QTreeWidgetItem(sectionNode, ["Description: ", str(get_description(event))])
		column_index = 1  # Assuming you want to resize the first column

		sectionNode.setIcon(0, ConfigClass.iconProcess)
		bp_id = -1
		if str(event.GetBroadcasterClass()) == "lldb.anonymous" and str(
				event.GetDataFlavor()) == "ProgressEventData":
			sectionNode.setIcon(0, ConfigClass.iconAnon)
			return
		# elif SBWatchpoint.EventIsWatchpointEvent(event):
		#     print(f"SBWatchpoint.EventIsWatchpointEvent(event) ....")
		#     self.window().tabWatchpoints.reloadWatchpoints(False)
		#     self.addEventToListenerTreeItem(sectionNode, event)
		#
		# elif SBTarget.EventIsTargetEvent(event):
		#     print(f"EventIsTargetEvent")
		elif SBProcess.EventIsProcessEvent(event):
			# print(f"EventIsProcessEvent => Type: {event.GetType()}")
			if event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
				sectionNode.setIcon(0, ConfigClass.iconTerminal)

				# QApplication.processEvents()
				QApplication.processEvents()

				# tmrAppStarted = QtCore.QTimer()
				# tmrAppStarted.singleShot(1000, self.readSTDOUT)
				# return
				process = self.driver.target.GetProcess()
				# if process.GetState() == lldb.eStateStopped:
				#     self.readSTDOUT(process)
				# else:
				#     print(f"APP NOT STOOOOOOOOOOOOOOOPPPPPPPPPPPEEEEEEEEEEDDDDDDDDDD!!!!!!!!")
				#     self.readSTDOUT(process)
			# elif event.GetType() == lldb.SBProcess.eBroadcastBitStateChanged:
			#     process = self.driver.getTarget().GetProcess()
			#     if process.GetState() == lldb.eStateRunning:  # or process.GetState() == lldb.eStateStepping:
			#         self.window().setWinTitleWithState("Running")
			#         # logDbgC(f"event  .....")
			#         self.window().wdtDisassembly.clearPC()
			#         self.window().setResumeActionIcon(False)
			#         pass
			#     elif process.GetState() == lldb.eStateStopped:
			#         self.window().setWinTitleWithState(f"Interrupted")
			#         self.window().setResumeActionIcon(True)
			#         thread = self.driver.getTarget().GetProcess().GetThreadAtIndex(0)
			#         reason = thread.GetStopReason()
			#         # if reason == lldb.eStopReasonWatchpoint:
			#         # 	print(f"WATCHPOINT HIT!!!")
			#         # 	sectionNode.setIcon(0, ConfigClass.iconGlasses)
			#         #
			#         # 	wp = SBWatchpoint.GetWatchpointFromEvent(event)
			#         # 	subSectionNode = QTreeWidgetItem(sectionNode, ["Watchpoint ID: ", str(wp.GetID())])
			#         #
			#         # 	self.window().txtMultiline.setPC(self.driver.getPC(), True)
			#         # 	self.window().updateStatusBar("Watchpoint hit ...", True, 3000)
			#         # 	self.window().setResumeActionIcon()
			#
			#         if reason == lldb.eStopReasonBreakpoint:
			#             print(f"===========>>>>>>>>>>>>>> BREAKPOINT HIT!!!!!!")
			#             if bp_id == -1:
			#                 bp_id = thread.GetStopReasonDataAtIndex(0)
			#             # for idx in range(thread.GetStopReasonDataCount()):
			#             # 	if idx == 0:
			#             # 		bp_id = thread.GetStopReasonDataAtIndex(idx)
			#             # 	logDbg(f"StopReasonData({idx}): {thread.GetStopReasonDataAtIndex(idx)}")
			#
			#             if isinstance(extObj, lldb.SBTarget):
			#                 breakpoint = extObj.FindBreakpointByID(int(bp_id))
			#             else:
			#                 breakpoint = extObj.GetTarget().FindBreakpointByID(int(bp_id))
			#
			#             if breakpoint is not None:  # and breakpoint.GetID() == self.driver.mainID:
			#                 addr = breakpoint.location[0].GetLoadAddress()
			#                 self.window().txtMultiline.setPC(addr)
			#
			#                 self.bp_loc = 0
			#                 if breakpoint.GetNumLocations() == 1:
			#                     self.bp_loc = breakpoint.GetLocationAtIndex(0)
			#                 else:
			#                     bp_loc_id = thread.GetStopReasonDataAtIndex(1)
			#                     self.bp_loc = breakpoint.FindLocationByID(bp_loc_id)
			#
			#                 setBPPC = True
			#                 bpCond = arrBPConditions.get(str(breakpoint.GetID()) + "." + str(self.bp_loc.GetID()))
			#                 if bpCond is not None and bpCond != "":
			#                     # if (dbg.breakpointHelper.arrBPConditions[str(breakpoint.GetID())] != None and dbg.breakpointHelper.arrBPConditions[str(breakpoint.GetID())] != ""):
			#                     frame = thread.GetFrameAtIndex(0)
			#                     # Evaluate the condition
			#                     value = frame.EvaluateExpression(bpCond)
			#                     if value.GetError().Success():
			#                         result = value.GetValueAsUnsigned()
			#                         setBPPC = result
			#                     # if result:
			#
			#                 self.window().wdtBPsWPs.treBPs.setPC(hex(addr), setBPPC)
			#                 pass
			#     pass


		elif SBBreakpoint.EventIsBreakpointEvent(event):
			sectionNode.setIcon(0, ConfigClass.iconBPEnabled)
			eventType = SBBreakpoint.GetBreakpointEventTypeFromEvent(event)

			subSectionNode = QTreeWidgetItem(sectionNode, ["EventType: ",
														   BreakpointEventTypeString(eventType) + " (" + str(
															   eventType) + ")"])
			bp = SBBreakpoint.GetBreakpointFromEvent(event)
			bp_id = bp.GetID()

			thread = self.driver.target.GetProcess().GetThreadAtIndex(0)
			print(thread)
			frame = thread.GetFrameAtIndex(0)
			print(frame)

			# if eventType == lldb.eBreakpointEventTypeAdded:
			#     self.bpHelper = BreakpointHelperNG(self.driver)
			#     self.bpHelper.setCtrls(self.window().txtMultiline, self.window().wdtBPsWPs.treBPs)
			#     print("=============>>>>>>>>>>>>> BP ADDED!!!!!")
			#     arrBPConditions[str(bp.GetID())] = bp.GetCondition()
			#     arrBPHits[str(bp.GetID())] = 0
			#     for bl in bp:
			#         arrBPConditions[str(bp.GetID()) + "." + str(bl.GetID())] = bl.GetCondition()
			#         arrBPHits[str(bp.GetID()) + "." + str(bl.GetID())] = 0
			#         # logDbgC(f"addNewEvent...")
			#         self.bpHelper.enableBP(hex(bl.GetAddress().GetLoadAddress(self.driver.getTarget())), True)
			#         self.window().wdtBPsWPs.treBPs.addBP(bp)
			#     pass
			# elif eventType == lldb.eBreakpointEventTypeEnabled or eventType == lldb.eBreakpointEventTypeDisabled:
			#     if eventType == lldb.eBreakpointEventTypeEnabled:
			#         pass
			#     else:
			#         pass
			#     pass
			# # elif eventType == lldb.eBreakpointEventType
			# # for module in self.target.module_iter():
			# # 	for section in module.section_iter():
			# # 		if hasattr(section, 'symbol_in_section_iter'):
			# # 			for symbol in module.symbol_in_section_iter(section):
			# # 				if symbol.IsValid():
			# # 					name = symbol.GetName()
			# # 					start_addr = symbol.GetStartAddress().GetLoadAddress(self.target)
			# # 					self.logDbgC.emit(
			# # 						f"------------------>>>>>>>>>>>>>Symbol: {name}, Address: {hex(start_addr)}",
			# # 						DebugLevel.Verbose)
			return
		else:
			# print(f"EventIsOTHEREvent")
			pass

		if isinstance(extObj, lldb.SBProcess) or isinstance(extObj, lldb.SBTarget):
			if isinstance(extObj, lldb.SBTarget):
				thread = extObj.GetProcess().selected_thread
			else:
				thread = extObj.selected_thread
			reason = thread.GetStopReason()
			# if reason == lldb.eStopReasonWatchpoint:
			#     print(f"WATCHPOINT HIT!!!")
			#     sectionNode.setIcon(0, ConfigClass.iconGlasses)
			#
			#     wp = SBWatchpoint.GetWatchpointFromEvent(event)
			#     subSectionNode = QTreeWidgetItem(sectionNode, ["Watchpoint ID: ", str(wp.GetID())])
			#
			#     self.window().txtMultiline.setPC(self.driver.getPC(), True)
			#     self.window().updateStatusBar("Watchpoint hit ...", True, 3000)
			#     self.window().setResumeActionIcon()
			#
			# elif reason == lldb.eStopReasonBreakpoint:
			if reason == lldb.eStopReasonBreakpoint:

				if isinstance(extObj, lldb.SBTarget):
					thread = extObj.GetProcess().selected_thread
				else:
					thread = extObj.selected_thread

				# breakpoint = SBBreakpoint.GetBreakpointFromEvent(event)
				# logDbgC(f"breakpoint HIT: {breakpoint}")
				if bp_id == -1:
					bp_id = thread.GetStopReasonDataAtIndex(0)
				# for idx in range(thread.GetStopReasonDataCount()):
				# 	if idx == 0:
				# 		bp_id = thread.GetStopReasonDataAtIndex(idx)
				# 	logDbg(f"StopReasonData({idx}): {thread.GetStopReasonDataAtIndex(idx)}")

				if isinstance(extObj, lldb.SBTarget):
					breakpoint = extObj.FindBreakpointByID(int(bp_id))
				else:
					breakpoint = extObj.GetTarget().FindBreakpointByID(int(bp_id))

				# if breakpoint is not None and breakpoint.GetID() == self.driver.mainID:
				#     if breakpoint.MatchesName("main"):
				#         # self.logDbgC.emit(f"if breakpoint.MatchesName('main')", DebugLevel.Verbose)
				#         for module in self.driver.getTarget().module_iter():
				#             for section in module.section_iter():
				#                 if hasattr(section, 'symbol_in_section_iter'):
				#                     for symbol in module.symbol_in_section_iter(section):
				#                         if symbol.IsValid():
				#                             name = symbol.GetName()
				#                             start_addr = symbol.GetStartAddress().GetLoadAddress(self.target)
				#                         # self.logDbgC.emit(f"------------------>>>>>>>>>>>>>Symbol: {name}, Address: {hex(start_addr)}", DebugLevel.Verbose)
				#     pass
				# elif breakpoint is not None and breakpoint.GetID() == self.driver.scanfID:
				#
				#     if breakpoint.MatchesName("scanf"):
				#         # logDbgC(f"if breakpoint.MatchesName('scanf')")
				#         self.window().txtMultiline.table.handle_gotoAddr()
				#     # logDbgC(f"breakpoint.GetTarget(): {breakpoint.GetTarget()}")
				#     slNames = lldb.SBStringList()
				#     breakpoint.GetNames(slNames)
				#
				#     # logDbgC(f"FOUND BREAKPOINT-NAMES: {len(slNames)}")
				#
				#     for name in slNames:
				#         # logDbgC(f"Name for breakpoint (ID: {breakpoint.GetID()}) found: {name}")
				#         if name == "scanf":
				#             # logDbgC(f"SCANF FOUND !!!!")
				#             print(f"SCANF FOUND !!!!")
				#         # self.window().txtMultiline.table.handle_gotoAddr()
				#
				self.bp_loc = 0
				if breakpoint.GetNumLocations() == 1:
					self.bp_loc = breakpoint.GetLocationAtIndex(0)
				else:
					bp_loc_id = thread.GetStopReasonDataAtIndex(1)
					self.bp_loc = breakpoint.FindLocationByID(bp_loc_id)
				#
				# # print(f"bp_id: {bp_id} / bp_loc.GetID() => {self.bp_loc.GetID()}")
				# # if(breakpoint.GetCondition() != ""):
				# # print(arrBPConditions)
				# # print(arrBPHits)
				# bpCond = arrBPConditions.get(str(breakpoint.GetID()) + "." + str(self.bp_loc.GetID()))
				# if bpCond is not None and bpCond != "":
				#     # if (dbg.breakpointHelper.arrBPConditions[str(breakpoint.GetID())] != None and dbg.breakpointHelper.arrBPConditions[str(breakpoint.GetID())] != ""):
				#     frame = thread.GetFrameAtIndex(0)
				#     # Evaluate the condition
				#     value = frame.EvaluateExpression(bpCond)
				#
				#     if value.GetError().Success():
				#         result = value.GetValueAsUnsigned()
				#         if result:
				#             print(f"✅ Condition is True: {bpCond}")
				#
				#             # blHit = arrBPHits.get(str(breakpoint.GetID()) + "." + str(self.bp_loc.GetID()))
				#             curHits = 0
				#             if arrBPHits.get(str(breakpoint.GetID()) + "." + str(
				#                     self.bp_loc.GetID())) is not None and arrBPHits.get(
				#                     str(breakpoint.GetID()) + "." + str(self.bp_loc.GetID())) != "":
				#                 curHits = int(
				#                     arrBPHits.get(str(breakpoint.GetID()) + "." + str(self.bp_loc.GetID())))
				#                 curHits += 1
				#                 arrBPHits[str(breakpoint.GetID()) + "." + str(self.bp_loc.GetID())] = curHits
				#             else:
				#                 curHits += 1
				#                 arrBPHits[str(breakpoint.GetID()) + "." + str(self.bp_loc.GetID())] = curHits
				#         # passa
				#         else:
				#             print(f"❌ Condition is False: {bpCond}")
				#             extObj.Continue()
				#             return
				#     else:
				#         print("⚠️ Evaluation error:", value.GetError().GetCString())

				line_entry = self.bp_loc.GetAddress().GetLineEntry()
				file_spec = line_entry.GetFileSpec()
				filename = file_spec.fullpath
				line_no = line_entry.GetLine()
				# print(f'stopped for BP {bp_id}: {filename}:{line_no}')
				subSectionNode = QTreeWidgetItem(sectionNode, ["Breakpoint ID: ", str(bp_id)])
				subSectionNode = QTreeWidgetItem(sectionNode, ["Filename: ", str(filename)])
				subSectionNode = QTreeWidgetItem(sectionNode, ["Line no.: ", str(line_no)])

			# elif reason == lldb.eStopReasonWatchpoint or \
			#         reason == lldb.eStopReasonPlanComplete:
			#     frame = thread.GetFrameAtIndex(0)
			#     line_entry = frame.GetLineEntry()
			#     file_spec = line_entry.GetFileSpec()
			#     filename = file_spec.fullpath
			#     line_no = line_entry.GetLine()
			#     print('stopped @ %s:%d', filename, line_no)
			elif reason == lldb.eStopReasonThreadExiting:
				print('thread exit')
			elif reason == lldb.eStopReasonSignal or \
					reason == lldb.eStopReasonException:
				print('signal/exception %x', thread.GetStopReasonDataAtIndex(0))

			elif reason == lldb.eStopReasonExec:
				print('re-run')

		# DIRTY HACK BECAUSE OF MY INPATIENCE => REMOVEE !!!!
		# QApplication.processEvents()
		# currTabIdx = self.window().tabWidgetDbg.currentIndex()
		# self.window().tabWidgetDbg.setCurrentWidget(self.window().treListener)
		# self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
		# self.window().tabWidgetDbg.setCurrentIndex(currTabIdx)

		QApplication.processEvents()

	# def addEventToListenerTreeItem(sectionNode, event):
	#     if SBWatchpoint.EventIsWatchpointEvent(event):
	#         sectionNode.setIcon(0, ConfigClass.iconGlasses)
	#         #			self.window().tabWatchpoints.tblWatchpoints.resetContent()
	#         #		self.window().tabWatchpoints.reloadWatchpoints(False)
	#         wp = SBWatchpoint.GetWatchpointFromEvent(event)
	#         subSectionNode = QTreeWidgetItem(sectionNode, ["Watchpoint ID: ", str(wp.GetID())])
	#         subSectionNode = QTreeWidgetItem(sectionNode, ["Enabled: ", str(wp.IsEnabled())])
	#         subSectionNode = QTreeWidgetItem(sectionNode, ["Address: ", hex(wp.GetWatchAddress())])
	#         subSectionNode = QTreeWidgetItem(sectionNode, ["Size: ", hex(wp.GetWatchSize())])
	#         subSectionNode = QTreeWidgetItem(sectionNode, ["Condition: ", wp.GetCondition()])
	#         subSectionNode = QTreeWidgetItem(sectionNode, ["Hit count: ", str(wp.GetHitCount())])
	#         subSectionNode = QTreeWidgetItem(sectionNode, ["Ignore count: ", str(wp.GetIgnoreCount())])

	def contextMenuEvent(self, event):
		# Show the context menu
		self.context_menu.exec(event.globalPos())


class ListenerTreeWidget(BaseTreeWidget):
	setHelper = None
	ommitChange = False

	def __init__(self, driver, setHelper):
		super().__init__(driver)
		self.setHelper = setHelper

		self.setContentsMargins(0, 0, 0, 0)

		self.context_menu = QMenu(self)
		actionShowInfos = self.context_menu.addAction("Show infos")

		self.actionShowMemoryFrom = self.context_menu.addAction("Show memory")
		self.actionShowMemoryTo = self.context_menu.addAction("Show memory after End")

		self.setFont(ConfigClass.font)
		self.setHeaderLabels(['Type / Listener'])
		self.header().resizeSection(0, 370)
		self.setMouseTracking(True)
		self.itemChanged.connect(self.handle_itemChanged)

	#     self.itemEntered.connect(self.handle_itemEntered)
	#
	# def handle_itemEntered(self, item, col):
	#     if item.childCount() == 0 and col == 0:
	#         if item.checkState(col) == Qt.CheckState.Checked:
	#             # self.statusBarManager.setStatusMsg(
	#             #     f"Successfully loaded target: {self.driver.worker.getTargetFilename()}", 3500)
	#             self.window().statusBarManager.setStatusMsg(f"Disable '{item.text(0)}' listener ...")
	#         else:
	#             self.window().statusBarManager.setStatusMsg(f"Enable '{item.text(0)}' listener ...")
	#     else:
	#         if item.checkState(col) == Qt.CheckState.Checked:
	#             self.window().statusBarManager.setStatusMsg(f"Disable All '{item.text(0)}' listeners ...")
	#         elif item.checkState(col) == Qt.CheckState.Unchecked:
	#             self.window().statusBarManager.setStatusMsg(f"Enable All '{item.text(0)}' listeners ...")
	#         else:
	#             self.window().statusBarManager.setStatusMsg(f"Enable All '{item.text(0)}' listeners ...")
	#     pass

	def getKeyForBroadcastBitData(self, daData):
		setKey = ""
		if daData != None:
			if isinstance(daData[0], str):
				setKey = str(daData[0]) + "_" + str(BroadcastBitString(daData[0], daData[1]))
			elif daData[0] == lldb.SBCommandInterpreter:
				setKey = str("lldb.commandinterpreter") + "_" + str(BroadcastBitString(daData[0], daData[1]))
			else:
				setKey = str(daData[0].GetBroadcasterClassName()) + "_" + str(BroadcastBitString(daData[0], daData[1]))
		return setKey

	def handle_itemChanged(self, item, column):
		if not self.ommitChange:
			self.ommitChange = True
			if item.childCount() > 0:
				self.setHelper.beginWriteArray("listener_" + item.text(0))
				for i in range(item.childCount()):
					item.child(i).setCheckState(0, item.checkState(0))
					daData = item.child(i).data(0, Qt.ItemDataRole.UserRole)
					if daData != None:
						setKey = self.getKeyForBroadcastBitData(daData)
						self.setHelper.setArrayValue(setKey,
													 (True if item.checkState(0) == Qt.CheckState.Checked else False))
				self.setHelper.endArray()
			else:
				parentItem = item.parent()
				if parentItem is not None:
					allSame = True
					allState = False
					for i in range(parentItem.childCount()):
						itemData = parentItem.child(i).data(0, Qt.ItemDataRole.UserRole)
						print(itemData)
						if itemData != None:
							self.setHelper.beginWriteArray("listener_" + parentItem.text(0))
							setKey = self.getKeyForBroadcastBitData(itemData)
							self.setHelper.setArrayValue(setKey, (
								True if parentItem.child(i).checkState(0) == Qt.CheckState.Checked else False))
							self.setHelper.endArray()

							if itemData[0] == lldb.SBTarget or itemData[0] == lldb.SBProcess:
								if itemData[1] == item.data(0, Qt.ItemDataRole.UserRole)[1]:
									# if item.checkState(
									#         0) == Qt.CheckState.Checked:  # parentItem.child(i).checkState(0) == Qt.CheckState.Checked:
									#     print(f"ADD LISTENER")
									#     self.driver.addListener(itemData[0], itemData[1])
									#     print(f"ADD LISTENER ===>>> LISTENER")
									#     self.window().listener._add_listener(itemData[0], itemData[1])
									# else:
									#     print(f"REMOVE LISTENER")
									#     self.driver.removeListener(itemData[0], itemData[1])
									#     print(f"REMOVE LISTENER ===>>> LISTENER")
									#     self.window().listener._remove_listener(itemData[0], itemData[1])
									pass

						if i == 0:
							allState = (parentItem.child(i).checkState(0) == Qt.CheckState.Checked)
						else:
							if allSame and allState != (parentItem.child(i).checkState(0) == Qt.CheckState.Checked):
								allSame = False
						pass
					if not allSame:
						parentItem.setCheckState(0, Qt.CheckState.PartiallyChecked)
					else:
						parentItem.setCheckState(0, Qt.CheckState.Checked if allState else Qt.CheckState.Unchecked)

			self.ommitChange = False
		pass

	def contextMenuEvent(self, event):
		self.context_menu.exec(event.globalPos())


class ListenerWidget(QWidget):
	setHelper = None

	def __init__(self, driver, setHelper):
		super().__init__()
		self.driver = driver
		self.setHelper = setHelper

		self.splitter = QSplitter()
		self.setContentsMargins(0, 0, 0, 0)
		self.splitter.setContentsMargins(0, 0, 0, 0)
		self.splitter.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
		self.splitter.setOrientation(Qt.Orientation.Horizontal)

		self.grpSelection = QGroupBox("Listener Selection:")
		self.grpSelection.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
		self.treListener = ListenerTreeWidget(self.driver, self.setHelper)
		self.treListener.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
		self.grpSelection.setLayout(QVBoxLayout())
		self.grpSelection.layout().addWidget(self.treListener)
		self.splitter.addWidget(self.treListener)

		self.setLayout(QHBoxLayout())

		self.treEventLog = ListenerLogTreeWidget(self.driver, self.setHelper)
		self.treEventLog.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
		self.treEventLog.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

		self.grpLog = QGroupBox("Event Log:")
		self.grpLog.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
		self.grpLog.setLayout(QVBoxLayout())

		self.wdtLog = QWidget()
		self.wdtLog.setLayout(QVBoxLayout())
		self.wdtLog.layout().addWidget(self.treEventLog)
		self.wdtLog.layout().addWidget(QLabel("HELLO"))
		self.grpLog.layout().addWidget(self.wdtLog)

		self.splitter.addWidget(self.treEventLog)
		self.layout().addWidget(self.splitter)
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.setContentsMargins(0, 0, 0, 0)
		self.splitter.setStretchFactor(0, 35)
		self.splitter.setStretchFactor(1, 65)
		self.splitter.setContentsMargins(0, 0, 0, 0)
		self.loadListener()

	def handle_gotNewEvent(self, event, extObj=None):
		# print(f"Got new event: {event} => {get_description(event)}")
		if extObj == None:
			extObj = self.driver.target.GetProcess()
		self.treEventLog.addNewEvent(event, extObj)

	def addBroadcastBitItem(self, parent, type, bit, checked=True):
		subSectionNode = QTreeWidgetItem(parent, [BroadcastBitString(type, bit)])
		subSectionNode.setData(0, Qt.ItemDataRole.UserRole, [type, bit])

		self.setHelper.beginReadArray("listener_" + parent.text(0))
		setKey = self.treListener.getKeyForBroadcastBitData([type, bit])

		subSectionNode.setCheckState(0, Qt.CheckState.Checked if self.setHelper.getArrayValue(
			setKey) == "true" else Qt.CheckState.Unchecked)
		self.setHelper.endArray()

		return subSectionNode

	def addBroadcastBitGroup(self, groupName, broadcastClass, bits):

		sectionNode = QTreeWidgetItem(self.treListener, [groupName])
		allSame = True
		allCheckState = Qt.CheckState.Unchecked
		i = 0
		for bit in bits:
			subSectionNode = self.addBroadcastBitItem(sectionNode, broadcastClass, bit, True)
			if i == 0:
				allCheckState = subSectionNode.checkState(0)
			else:
				if allSame and allCheckState != subSectionNode.checkState(0):
					allSame = False
			i += 1

		if not allSame:
			sectionNode.setCheckState(0, Qt.CheckState.PartiallyChecked)
		else:
			sectionNode.setCheckState(0, allCheckState)
		sectionNode.setExpanded(True)

		return sectionNode

	def loadListener(self):

		self.treListener.ommitChange = True

		self.addBroadcastBitGroup("Misc", "lldb.anonymous", [0])

		self.addBroadcastBitGroup("Target", lldb.SBTarget, [lldb.SBTarget.eBroadcastBitBreakpointChanged,
															lldb.SBTarget.eBroadcastBitModulesLoaded,
															lldb.SBTarget.eBroadcastBitModulesUnloaded,
															lldb.SBTarget.eBroadcastBitWatchpointChanged,
															lldb.SBTarget.eBroadcastBitSymbolsLoaded])

		self.addBroadcastBitGroup("Process", lldb.SBProcess,
								  [lldb.SBProcess.eBroadcastBitStateChanged, lldb.SBProcess.eBroadcastBitInterrupt,
								   lldb.SBProcess.eBroadcastBitSTDOUT, lldb.SBProcess.eBroadcastBitSTDERR,
								   lldb.SBProcess.eBroadcastBitProfileData, lldb.SBProcess.eBroadcastBitStructuredData])

		self.addBroadcastBitGroup("Thread", lldb.SBThread,
								  [lldb.SBThread.eBroadcastBitStackChanged, lldb.SBThread.eBroadcastBitThreadSuspended,
								   lldb.SBThread.eBroadcastBitThreadResumed,
								   lldb.SBThread.eBroadcastBitSelectedFrameChanged,
								   lldb.SBThread.eBroadcastBitThreadSelected])

		self.addBroadcastBitGroup("CommandInterpreter", lldb.SBCommandInterpreter,
								  [lldb.SBCommandInterpreter.eBroadcastBitThreadShouldExit,
								   lldb.SBCommandInterpreter.eBroadcastBitResetPrompt,
								   lldb.SBCommandInterpreter.eBroadcastBitQuitCommandReceived,
								   lldb.SBCommandInterpreter.eBroadcastBitAsynchronousOutputData,
								   lldb.SBCommandInterpreter.eBroadcastBitAsynchronousErrorData])

		self.treListener.ommitChange = False
