#!/usr/bin/env python3

import lldb
from lldb import *
import sys
from threading import Thread
import io
import contextlib
try:
	import queue
except ImportError:
	import Queue as queue
	
import datetime
import sys
import os
import subprocess
from sys import stdin, stdout
import threading

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6 import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from lib.settings import *

from dbg.fileInfos import *
#from LLDBPyGUIWindow import SBStreamForwarder
from worker.debugWorker import StepKind
from ui.helper.listenerHelper import *
from config import *
	
class SBStreamForwarder(io.StringIO):
	def __init__(self):
		super().__init__()
		self.sb_stream = None
		
	def write(self, data):
		super().write(data)
		if self.sb_stream is None:
			self.sb_stream = lldb.SBStream()
			self.sb_stream.write(self.getvalue())
#			self.truncate(0)  # Clear the buffer for subsequent writes
			
class ListenerLogTreeWidget(QTreeWidget):
#	self.lblModule.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
#		
#	self.lblModule.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
	def getTimestamp(self):
		now = datetime.datetime.now()
		# self.setHelper.getValue(SettingsValues.EventListenerTimestampFormat)
		return now.strftime(self.setHelper.getValue(SettingsValues.EventListenerTimestampFormat)) #"%H:%M:%S") # "%Y-%m-%d %H:%M:%S"
	
#		print(formatted_date)
	
	def __init__(self, driver):
		super().__init__()
		self.driver = driver
		
		self.setHelper = SettingsHelper()
		
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
		
	def readSTDOUT(self):
		stdout = self.driver.getTarget().GetProcess().GetSTDOUT(1024)
		if stdout is not None and len(stdout) > 0:
			
			print(stdout)
			message = {"status":"event", "type":"stdout", "output": "".join(["%02x" % ord(i) for i in stdout])}
			print(message)
			byte_values = bytes.fromhex("".join(["%02x" % ord(i) for i in stdout]))
			result_string = byte_values.decode('utf-8')
			print(result_string)
		else:
			print(f"stdout IS NONE or LEN == 0")
			
	def addNewEvent(self, event, extObj):
		sectionNode = QTreeWidgetItem(self, [BroadcastBitString(str(event.GetBroadcasterClass()), event.GetType()), self.getTimestamp()])
		
		subSectionNode = QTreeWidgetItem(sectionNode, ["Type: ", BroadcastBitString(str(event.GetBroadcasterClass()), event.GetType()) + " (" + str(event.GetType()) + ")"])
		subSectionNode = QTreeWidgetItem(sectionNode, ["BroadcasterClass: ", str(event.GetBroadcasterClass())])
		subSectionNode = QTreeWidgetItem(sectionNode, ["DataFlavor: ", str(event.GetDataFlavor())])
#		subSectionNode = QTreeWidgetItem(sectionNode, ["CStringFromEvent: ", str(event.GetCStringFromEvent(event))])
		subSectionNode = QTreeWidgetItem(sectionNode, ["Description: ", str(get_description(event))])
		column_index = 1  # Assuming you want to resize the first column
#		
#		# Loop through all items in the column
##		for i in range(self.topLevelItemCount()):
##			item = self.topLevelItem(i)
#		item = subSectionNode
#		item.setSizeHint(column_index, QSize(2000, 20))
#		size = item.setSizeHint(column_index)
#		print(f"==============>>>>>>>>>>>>>>> SIZE: {size}")
#		# Set the column width to the maximum of current width and size hint
#		self.setColumnWidth(column_index, max(self.columnWidth(column_index), size.width()))
#		self.header().resizeSection(column_index, max(self.columnWidth(column_index), size.width()))
		
		sectionNode.setIcon(0, ConfigClass.iconProcess)
		bp_id = -1
		if str(event.GetBroadcasterClass()) == "lldb.anonymous" and str(event.GetDataFlavor()) == "ProgressEventData":
			sectionNode.setIcon(0, ConfigClass.iconAnon)
			return
		elif SBWatchpoint.EventIsWatchpointEvent(event):
			self.window().tabWatchpoints.reloadWatchpoints(False)
			addEventToListenerTreeItem(sectionNode, event)
#			sectionNode.setIcon(0, ConfigClass.iconGlasses)
##			self.window().tabWatchpoints.tblWatchpoints.resetContent()
#			self.window().tabWatchpoints.reloadWatchpoints(False)
#			wp = SBWatchpoint.GetWatchpointFromEvent(event)
#			subSectionNode = QTreeWidgetItem(sectionNode, ["Watchpoint ID: ", str(wp.GetID())])
#			subSectionNode = QTreeWidgetItem(sectionNode, ["Address: ", hex(wp.GetWatchAddress())])
#			subSectionNode = QTreeWidgetItem(sectionNode, ["Size: ", hex(wp.GetWatchSize())])
#			subSectionNode = QTreeWidgetItem(sectionNode, ["Condition: ", wp.GetCondition()])
#			subSectionNode = QTreeWidgetItem(sectionNode, ["Hit count: ", str(wp.GetHitCount())])
#			subSectionNode = QTreeWidgetItem(sectionNode, ["Ignore count: ", str(wp.GetIgnoreCount())])
			
#			GetWatchAddress
#			GetCondition(SBWatchpoint self) -> char const *
			
		elif SBTarget.EventIsTargetEvent(event):
			print(f"EventIsTargetEvent")
		elif SBProcess.EventIsProcessEvent(event):
			print(f"EventIsProcessEvent => Type: {event.GetType()}")
			if event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
				sectionNode.setIcon(0, ConfigClass.iconTerminal)
#				QCoreApplication.processEvents()
#				QApplication.processEvents()
				print(f"GOT STDOUT EVENT!!!")
				print(">>>>> WE GOT STDOUT")
#				print(sys.stdout)
				# Example usage:
#				with contextlib.redirect_stdout(SBStreamForwarder()):
#					print("This output will be redirected to an SBStream!")
#					
#				# Now you can access the captured output using the SBStream object
#				output_stream = SBStreamForwarder().sb_stream
#				if output_stream != None:
#					for line in output_stream:
#						print("Captured line:", line)
				tmrAppStarted = QtCore.QTimer()
				tmrAppStarted.singleShot(1000, self.readSTDOUT)
#				QCoreApplication.processEvents()
#				QApplication.processEvents()
				
				
		elif SBBreakpoint.EventIsBreakpointEvent(event):
			sectionNode.setIcon(0, ConfigClass.iconBPEnabled)
			eventType = SBBreakpoint.GetBreakpointEventTypeFromEvent(event)
			print(eventType)
			subSectionNode = QTreeWidgetItem(sectionNode, ["EventType: ", BreakpointEventTypeString(eventType) + " (" + str(eventType) + ")"])
			bp = SBBreakpoint.GetBreakpointFromEvent(event)
			print(f"EventIsBreakpointEvent => {bp}")
			bp_id = bp.GetID()
#			if isinstance(extObj, lldb.SBTarget):
#				thread = extObj.GetProcess().selected_thread
#			else:
#				thread = extObj.selected_thread
			thread = self.driver.getTarget().GetProcess().GetThreadAtIndex(0)
			print(thread)
			frame = thread.GetFrameAtIndex(0)
			print(frame)
#			self.window().handle_debugStepCompleted(StepKind.Continue, True, frame.register["rip"].value, frame)
			return
		else:
			print(f"EventIsOTHEREvent")
			
			
		if isinstance(extObj, lldb.SBProcess) or isinstance(extObj, lldb.SBTarget):
			if isinstance(extObj, lldb.SBTarget):
				thread = extObj.GetProcess().selected_thread
			else:
				thread = extObj.selected_thread
			reason = thread.GetStopReason()
			if reason == lldb.eStopReasonWatchpoint:
				print(f"WATCHPOINT HIT!!!")
				sectionNode.setIcon(0, ConfigClass.iconGlasses)
				
				wp = SBWatchpoint.GetWatchpointFromEvent(event)
				subSectionNode = QTreeWidgetItem(sectionNode, ["ID: ", str(wp.GetID())])
				
#				GetWatchpointEventTypeFromEvent(*args)
#				GetWatchpointEventTypeFromEvent(SBEvent event) -> lldb::WatchpointEventType	source code
#				
#				GetWatchpointFromEvent(*args)
#				GetWatchpointFromEvent(SBEvent event) -> SBWatchpoint
				
				
#				self.driver.debugger.SetAsync(False)
#				self.driver.getTarget().GetProcess().Stop() #GetThreadAtIndex(0).Suspend()
			elif reason == lldb.eStopReasonBreakpoint:# or reason == lldb.eBroadcastBitBreakpointChanged:
#				self.window().handle_processEvent(event, extObj)
				#assert(thread.GetStopReasonDataCount() == 2)
				if bp_id == -1:
					bp_id = thread.GetStopReasonDataAtIndex(0)
				print('bp_id:%s', bp_id)
				if isinstance(extObj, lldb.SBTarget):
					breakpoint = extObj.FindBreakpointByID(int(bp_id))
				else:
					breakpoint = extObj.GetTarget().FindBreakpointByID(int(bp_id))
				if breakpoint.GetNumLocations() == 1:
					bp_loc = breakpoint.GetLocationAtIndex(0)
				else:
					bp_loc_id = thread.GetStopReasonDataAtIndex(1)
					bp_loc = breakpoint.FindLocationByID(bp_loc_id)
				line_entry = bp_loc.GetAddress().GetLineEntry()
				file_spec = line_entry.GetFileSpec()
				filename = file_spec.fullpath
				line_no = line_entry.GetLine()
				print('stopped for BP %d: %s:%d', bp_id, filename, line_no)
				subSectionNode = QTreeWidgetItem(sectionNode, ["Breakpoint ID: ", str(bp_id)])
				subSectionNode = QTreeWidgetItem(sectionNode, ["Filename: ", str(filename)])
				subSectionNode = QTreeWidgetItem(sectionNode, ["Line no.: ", str(line_no)])
#				lldb.anonymous
#				self.window().handle_processEvent(event, extObj)
#				QCoreApplication.processEvents()
	#				if filename is not None:
	#					self.focus_signal.emit(filename, int(line_no))
	#				else:
	#					self.focus_signal.emit('', -1)
			elif reason == lldb.eStopReasonWatchpoint or \
				reason == lldb.eStopReasonPlanComplete:
				frame = thread.GetFrameAtIndex(0)
				line_entry = frame.GetLineEntry()
				file_spec = line_entry.GetFileSpec()
				filename = file_spec.fullpath
				line_no = line_entry.GetLine()
				print('stopped @ %s:%d', filename, line_no)
	#				if filename is not None:
	#					self.focus_signal.emit(filename, int(line_no))
#				break
			elif reason == lldb.eStopReasonThreadExiting:
				print('thread exit')
			elif reason == lldb.eStopReasonSignal or \
				reason == lldb.eStopReasonException:
				print('signal/exception %x', thread.GetStopReasonDataAtIndex(0))
		
			elif reason == lldb.eStopReasonExec:
				print('re-run')
				
#		subSectionNode = QTreeWidgetItem(sectionNode, ["Type: " + str(event.GetType()), ''])
#		subSectionNode = QTreeWidgetItem(sectionNode, ["BroadcasterClass: " + str(event.GetBroadcasterClass()), ''])
#		subSectionNode = QTreeWidgetItem(sectionNode, ["DataFlavor: " + str(event.GetDataFlavor()), ''])
#		subSectionNode = QTreeWidgetItem(sectionNode, ["CStringFromEvent: " + str(event.GetCStringFromEvent(event)), ''])
#		subSectionNode = QTreeWidgetItem(sectionNode, ["Description: " + str(self.get_description(event)), ''])
#		
#		if isinstance(extObj, lldb.SBProcess):
#			thread = extObj.selected_thread
#			reason = thread.GetStopReason()
#			if reason == lldb.eStopReasonBreakpoint:
#				#assert(thread.GetStopReasonDataCount() == 2)
#				bp_id = thread.GetStopReasonDataAtIndex(0)
#				print('bp_id:%s', bp_id)
#				breakpoint = extObj.GetTarget().FindBreakpointByID(int(bp_id))
#				if breakpoint.GetNumLocations() == 1:
#					bp_loc = breakpoint.GetLocationAtIndex(0)
#				else:
#					bp_loc_id = thread.GetStopReasonDataAtIndex(1)
#					bp_loc = breakpoint.FindLocationByID(bp_loc_id)
#				line_entry = bp_loc.GetAddress().GetLineEntry()
#				file_spec = line_entry.GetFileSpec()
#				filename = file_spec.fullpath
#				line_no = line_entry.GetLine()
#				print('stopped for BP %d: %s:%d', bp_id, filename, line_no)
#				subSectionNode = QTreeWidgetItem(sectionNode, ["Breakpoint ID: " + str(bp_id), ''])
#				subSectionNode = QTreeWidgetItem(sectionNode, ["Filename: " + str(filename), ''])
#				subSectionNode = QTreeWidgetItem(sectionNode, ["Line no.: " + str(line_no), ''])
#	#				if filename is not None:
#	#					self.focus_signal.emit(filename, int(line_no))
#	#				else:
#	#					self.focus_signal.emit('', -1)
#			elif reason == lldb.eStopReasonWatchpoint or \
#				reason == lldb.eStopReasonPlanComplete:
#				frame = thread.GetFrameAtIndex(0)
#				line_entry = frame.GetLineEntry()
#				file_spec = line_entry.GetFileSpec()
#				filename = file_spec.fullpath
#				line_no = line_entry.GetLine()
#				print('stopped @ %s:%d', filename, line_no)
#	#				if filename is not None:
#	#					self.focus_signal.emit(filename, int(line_no))
##				break
#			elif reason == lldb.eStopReasonThreadExiting:
#				print('thread exit')
#			elif reason == lldb.eStopReasonSignal or \
#				reason == lldb.eStopReasonException:
#				print('signal/exception %x', thread.GetStopReasonDataAtIndex(0))
#			
#			elif reason == lldb.eStopReasonExec:
#				print('re-run')
				
#		sectionNode.setExpanded(True)
		
		
			
		QCoreApplication.processEvents()
		currTabIdx = self.window().tabWidgetDbg.currentIndex()
		self.window().tabWidgetDbg.setCurrentWidget(self.window().treListener)
		self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
#		self.txtSource.horizontalScrollBar().setValue(horizontal_value)
#		if not autoScroll:
#			self.txtSource.verticalScrollBar().setValue(vertical_value)
#		else:
			
#				QApplication.processEvents()
#				currTabIdx = self.tabWidgetDbg.currentIndex()
#				self.tabWidgetDbg.setCurrentIndex(3)
#			line_text = "=>"
#			self.txtSource.scroll_to_line(line_text)
		self.window().tabWidgetDbg.setCurrentIndex(currTabIdx)
		
		QCoreApplication.processEvents()
		pass
		
	def contextMenuEvent(self, event):
		# Show the context menu
		self.context_menu.exec(event.globalPos())
		
class ListenerTreeWidget(QTreeWidget):
	
#	actionShowMemory = None
	
	def __init__(self, driver):
		super().__init__()
		self.driver = driver
#       self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
		self.context_menu = QMenu(self)
		actionShowInfos = self.context_menu.addAction("Show infos")
		
		self.actionShowMemoryFrom = self.context_menu.addAction("Show memory")
		self.actionShowMemoryTo = self.context_menu.addAction("Show memory after End")
		
		self.setFont(ConfigClass.font)
		self.setHeaderLabels(['Type / Listener'])
		self.header().resizeSection(0, 370)
#		self.header().resizeSection(1, 256)
#		self.header().resizeSection(2, 128)
#		self.header().resizeSection(3, 128)
#		self.header().resizeSection(4, 256)
		self.itemChanged.connect(self.handle_itemChanged)
		
	ommitChange = False
	def handle_itemChanged(self, item, column):
		print(f"Item changed: {item} => col: {column}")
		if not self.ommitChange:
			self.ommitChange = True
			if item.childCount() > 0:
				for i in range(item.childCount()):
					item.child(i).setCheckState(0, item.checkState(0))
					pass
			else:
				parentItem = item.parent()
				if parentItem != None:
					allSame = True
					allState = False
					for i in range(parentItem.childCount()):
	#					if parentItem.child(i).checkState(0) == Qt.CheckState.Checked:
		#					if allState == True
						itemData = parentItem.child(i).data(0, Qt.ItemDataRole.UserRole)
						print(itemData)
						if itemData != None:
							if itemData[0] == lldb.SBTarget:
								if parentItem.child(i).checkState(0) == Qt.CheckState.Checked:
									print(f"ADD LISTENER")
									self.driver.addListener(itemData[0], itemData[1])
								else:
									print(f"REMOVE LISTENER")
									self.driver.removeListener(itemData[0], itemData[1])
								
						if i == 0:
							allState = (parentItem.child(i).checkState(0) == Qt.CheckState.Checked)
						else:
							if allState != (parentItem.child(i).checkState(0) == Qt.CheckState.Checked):
								allSame = False
								break
						break
		#				item.child(i).setCheckState(0, item.checkState(0))
						pass
					if not allSame:
						parentItem.setCheckState(0, Qt.CheckState.PartiallyChecked)
					else:
						parentItem.setCheckState(0, Qt.CheckState.Checked if allState else Qt.CheckState.Unchecked)
						
			self.ommitChange = False
		pass
		
	def contextMenuEvent(self, event):
		# Show the context menu
		self.context_menu.exec(event.globalPos())
		
		
class ListenerWidget(QWidget):
	
	def handle_gotNewEvent(self, event, extObj=None):
		print(f"Got new event: {event} => {get_description(event)}")
		if extObj == None:
			extObj = self.driver.getTarget().GetProcess()
#		print(dir(event))
#		self.txtEventLog.append(f"Got new event: {event} => {self.get_description(event)}")
#		self.txtEventLog.append(f"{self.get_description(event)}")
		self.treEventLog.addNewEvent(event, extObj)
		pass
		
#	def worker(self):
#		while True:
##			global event_queue
##			global event_queue
##			item = event_queue.get()
#			print(f"INSIDE WORKER => {self.driver.event_queue}")
#			event = self.driver.event_queue.get()
#			print(f'Working on {event}')
#			#		print(f'Finished {item}')
#			self.handle_gotNewEvent(event, self.driver.getTarget().GetProcess())
#			self.driver.event_queue.task_done()
			
#			self.treEventLog.addNewEvent(event, extObj)
			
			# Turn-on the worker thread.
	
	def __init__(self, driver):
		super().__init__()
		self.driver = driver
#		self.wdtFile = QWidget()
#		self.layFile = QHBoxLayout()
#		self.wdtFile.setLayout(self.layFile)
		self.splitter = QSplitter()
		self.splitter.setContentsMargins(0, 0, 0, 0)
		self.splitter.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
		self.splitter.setOrientation(Qt.Orientation.Horizontal)
		
		self.grpSelection = QGroupBox("Listener Selection:")
		self.grpSelection.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
		self.treListener = ListenerTreeWidget(self.driver)
		self.treListener.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
		self.grpSelection.setLayout(QVBoxLayout())
		self.grpSelection.layout().addWidget(self.treListener)
		self.splitter.addWidget(self.grpSelection)
#		self.treFile.actionShowMemoryFrom.triggered.connect(self.handle_showMemoryFileStructureFrom)
#		self.lblModule.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
#		self.cmbModules.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		self.setLayout(QHBoxLayout())
		self.txtEventLog = QTextEdit()
		self.treEventLog = ListenerLogTreeWidget(self.driver)
		self.treEventLog.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
		self.grpLog = QGroupBox("Event Log:")
		self.grpLog.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
		self.grpLog.setLayout(QVBoxLayout())
		self.grpLog.layout().addWidget(self.treEventLog)
		self.splitter.addWidget(self.grpLog)
		self.layout().addWidget(self.splitter)
		self.splitter.setStretchFactor(0, 35)
		self.splitter.setStretchFactor(1, 65)
		self.loadListener()
		
	
	def addBroadcastBitItem(self, parent, type, bit, checked=True):
		subSectionNode = QTreeWidgetItem(parent, [BroadcastBitString(type, bit)])
		subSectionNode.setData(0, Qt.ItemDataRole.UserRole, [type, bit])
		subSectionNode.setCheckState(0, Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
		return subSectionNode
		pass
		
	def loadListener(self):
		
		self.treListener.ommitChange = True
		
		
		sectionNode = QTreeWidgetItem(self.treListener, ["Target"])
#		sectionNode.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled| Qt.ItemFlag.ItemIsUserCheckable)  # Set flags for editing
		sectionNode.setCheckState(0, Qt.CheckState.Checked)
		
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBTarget, lldb.SBTarget.eBroadcastBitBreakpointChanged, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBTarget, lldb.SBTarget.eBroadcastBitModulesLoaded, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBTarget, lldb.SBTarget.eBroadcastBitModulesUnloaded, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBTarget, lldb.SBTarget.eBroadcastBitWatchpointChanged, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBTarget, lldb.SBTarget.eBroadcastBitSymbolsLoaded, True)

		sectionNode.setExpanded(True)
		
		
		sectionNode = QTreeWidgetItem(self.treListener, ["Process"])
		sectionNode.setCheckState(0, Qt.CheckState.Checked)
		
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBProcess, lldb.SBProcess.eBroadcastBitStateChanged, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBProcess, lldb.SBProcess.eBroadcastBitInterrupt, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBProcess, lldb.SBProcess.eBroadcastBitSTDOUT, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBProcess, lldb.SBProcess.eBroadcastBitSTDERR, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBProcess, lldb.SBProcess.eBroadcastBitProfileData, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBProcess, lldb.SBProcess.eBroadcastBitStructuredData, True)

		sectionNode.setExpanded(True)
		
		sectionNode = QTreeWidgetItem(self.treListener, ["Thread"])
		sectionNode.setCheckState(0, Qt.CheckState.Checked)
		
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBThread, lldb.SBThread.eBroadcastBitStackChanged, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBThread, lldb.SBThread.eBroadcastBitThreadSuspended, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBThread, lldb.SBThread.eBroadcastBitThreadResumed, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBThread, lldb.SBThread.eBroadcastBitSelectedFrameChanged, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBThread, lldb.SBThread.eBroadcastBitThreadSelected, True)

		sectionNode.setExpanded(True)
		
		sectionNode = QTreeWidgetItem(self.treListener, ["CommandInterpreter"])
		sectionNode.setCheckState(0, Qt.CheckState.Checked)
		
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBCommandInterpreter, lldb.SBCommandInterpreter.eBroadcastBitThreadShouldExit, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBCommandInterpreter, lldb.SBCommandInterpreter.eBroadcastBitResetPrompt, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBCommandInterpreter, lldb.SBCommandInterpreter.eBroadcastBitQuitCommandReceived, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBCommandInterpreter, lldb.SBCommandInterpreter.eBroadcastBitAsynchronousOutputData, True)
		subSectionNode = self.addBroadcastBitItem(sectionNode, lldb.SBCommandInterpreter, lldb.SBCommandInterpreter.eBroadcastBitAsynchronousErrorData, True)
		
		sectionNode.setExpanded(True)
		
		self.treListener.ommitChange = False