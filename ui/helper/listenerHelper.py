#!/usr/bin/env python3
import lldb
from lldb import *

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6 import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from config import *

def addEventToListenerTreeItem(sectionNode, event):
	if SBWatchpoint.EventIsWatchpointEvent(event):
		sectionNode.setIcon(0, ConfigClass.iconGlasses)
#			self.window().tabWatchpoints.tblWatchpoints.resetContent()
#		self.window().tabWatchpoints.reloadWatchpoints(False)
		wp = SBWatchpoint.GetWatchpointFromEvent(event)
		subSectionNode = QTreeWidgetItem(sectionNode, ["Watchpoint ID: ", str(wp.GetID())])
		subSectionNode = QTreeWidgetItem(sectionNode, ["Enabled: ", str(wp.IsEnabled())])
		subSectionNode = QTreeWidgetItem(sectionNode, ["Address: ", hex(wp.GetWatchAddress())])
		subSectionNode = QTreeWidgetItem(sectionNode, ["Size: ", hex(wp.GetWatchSize())])
		subSectionNode = QTreeWidgetItem(sectionNode, ["Condition: ", wp.GetCondition()])
		subSectionNode = QTreeWidgetItem(sectionNode, ["Hit count: ", str(wp.GetHitCount())])
		subSectionNode = QTreeWidgetItem(sectionNode, ["Ignore count: ", str(wp.GetIgnoreCount())])