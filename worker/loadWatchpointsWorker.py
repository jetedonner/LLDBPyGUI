#!/usr/bin/env python3
import lldb

from worker.baseWorker import *

#class LoadWatchpointsWorkerReceiver(BaseWorkerReceiver):
#	interruptWorker = pyqtSignal()
	
class LoadWatchpointsWorkerSignals(BaseWorkerSignals):
#	loadWatchpoints = pyqtSignal(str)
#	loadWatchpointsValue = pyqtSignal(object, bool)
#	updateBreakpointsValue = pyqtSignal(object)
	loadWatchpointsValue = pyqtSignal(object)
	updateWatchpointsValue = pyqtSignal(object)

class LoadWatchpointsWorker(BaseWorker):
	
	initTable = True
		
	def __init__(self, driver, initTable = True):
		super(LoadWatchpointsWorker, self).__init__(driver)
		self.initTable = initTable
		self.signals = LoadWatchpointsWorkerSignals()
		
	def workerFunc(self):
		super(LoadWatchpointsWorker, self).workerFunc()
		
		self.sendStatusBarUpdate("Reloading watchpoints ...")
		target = self.driver.getTarget()
		idx = 0
#		for i in range(target.GetNumBreakpoints()):
#			idx += 1
#			bp_cur = target.GetBreakpointAtIndex(i)
#			# Make sure the name list has the remaining name:
#			name_list = lldb.SBStringList()
#			bp_cur.GetNames(name_list)
#			num_names = name_list.GetSize()
#			name = name_list.GetStringAtIndex(0)
#
#			if self.initTable:
#				self.signals.LoadWatchpointsValue.emit(bp_cur, self.initTable)
#			else:
#				self.signals.updateBreakpointsValue.emit(bp_cur)
		
		for wp_loc in target.watchpoint_iter():
			if self.initTable:
				self.signals.loadWatchpointsValue.emit(wp_loc) #, self.initTable)
			else:
				self.signals.updateWatchpointsValue.emit(wp_loc)
#		pass
		

		