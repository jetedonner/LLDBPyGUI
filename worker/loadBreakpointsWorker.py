#!/usr/bin/env python3
import lldb

from worker.baseWorker import *

#class LoadBreakpointsWorkerReceiver(BaseWorkerReceiver):
#	interruptWorker = pyqtSignal()
	
class LoadBreakpointsWorkerSignals(BaseWorkerSignals):
	loadBreakpoints = pyqtSignal(str)
	loadBreakpointsValue = pyqtSignal(object, bool)
	updateBreakpointsValue = pyqtSignal(object)
	loadWatchpointsValue = pyqtSignal(object)
	updateWatchpointsValue = pyqtSignal(object)

class LoadBreakpointsWorker(BaseWorker):
	
	initTable = True
		
	def __init__(self, driver, initTable = True):
		super(LoadBreakpointsWorker, self).__init__(driver)
		self.initTable = initTable
		self.signals = LoadBreakpointsWorkerSignals()
		
	def workerFunc(self):
		super(LoadBreakpointsWorker, self).workerFunc()
		
		self.sendStatusBarUpdate("Reloading breakpoints ...")
		target = self.driver.getTarget()
		idx = 0
		for i in range(target.GetNumBreakpoints()):
			idx += 1
			bp_cur = target.GetBreakpointAtIndex(i)
			# Make sure the name list has the remaining name:
			name_list = lldb.SBStringList()
			bp_cur.GetNames(name_list)
			num_names = name_list.GetSize()
			name = name_list.GetStringAtIndex(0)

			if self.initTable:
				self.signals.loadBreakpointsValue.emit(bp_cur, self.initTable)
			else:
				self.signals.updateBreakpointsValue.emit(bp_cur)
		
#		for wp_loc in target.watchpoint_iter():
#			if self.initTable:
#				self.signals.loadWatchpointsValue.emit(wp_loc)
#			else:
#				self.signals.updateWatchpointsValue.emit(wp_loc)
#		pass
		

		