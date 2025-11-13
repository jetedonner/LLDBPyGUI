import copy

import lldb
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QPen, QPainterPath, QPolygonF
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import (
	QHBoxLayout,
	QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsPathItem, QMenu,
	QGraphicsPolygonItem
)

from config import *
# from dbg.breakpointHelper import arrRememberedLocs
from helper.debugHelper import *
from lib.utils import *
from ui.customQt.QClickLabel import QClickLabel

controlFlowWidth = 110

from PyQt6.QtWidgets import QVBoxLayout, QWidget
from PyQt6.QtCore import QThread, pyqtSignal, QTimer


# Worker thread that emits a signal every 0.5 seconds
class IntervalWorker(QThread):
	tick = pyqtSignal()

	def run(self):
		self.timer = QTimer()
		self.timer.setInterval(150)  # 0.5 seconds
		self.timer.timeout.connect(self.tick.emit)
		self.timer.start()
		self.exec()  # Start event loop for the timer


class ControlFlowConnection():
	parentControlFlow = None
	asmTable = None
	oringPos = QPointF(0, 0)
	origRow = 0
	origAddr = 0x0
	destPos = QPointF(0, 0)
	destRow = 0
	destAddr = 0x0
	deltaAddr = 0x0
	jumpDist = 0x0
	mnemonic = ""
	color = random_qcolor()  # QColor("red")
	lineWidth = ConfigClass.controlFlowLineWidth
	switched = False
	radius = 0x0

	startArrow = None
	endArrow = None

	mainLine = None
	topArc = None
	bottomArc = None

	def __init__(self, startRow=0, endRow=0, origAddr=0x0, destAddr=0x0, table=None):
		super().__init__()
		self.origRow = startRow
		self.destRow = endRow
		self.asmTable = table
		self.origAddr = origAddr
		self.destAddr = destAddr
		self.jumpDist = self.destAddr - self.origAddr
		self.jumpDistInRows = self.destRow - self.origRow

	def setToolTip(self, tooltip):
		self.mainLine.setToolTip(tooltip)
		# self.mainLine.
		self.topArc.setToolTip(tooltip)
		self.bottomArc.setToolTip(tooltip)

	def setPen(self, pen=None):
		if pen is not None:
			newPen = pen
		else:
			# newPen = QPen(self.pen().color(), 1)
			newPen = QPen(QColor("red"), 1)
		self.mainLine.setPen(newPen)
		self.topArc.setPen(newPen)
		self.bottomArc.setPen(newPen)

	def setVisible(self, visible):
		self.mainLine.setVisible(visible)
		self.startArrow.setVisible(visible)
		self.endArrow.setVisible(visible)
		self.bottomArc.setVisible(visible)
		self.topArc.setVisible(visible)


class NoScrollGraphicsView(QGraphicsView):
	disableScroll = False
	scrolling = False
	wdtDis = None

	def __init__(self, scene, wdtDis=None):
		super().__init__(scene)

		self.wdtDis = wdtDis

		self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.setStyleSheet("background-color: #393939; border: 1px solid darkgray;")
		self.setContentsMargins(0, 0, 0, 0)
		self.setRenderHint(QPainter.RenderHint.Antialiasing)
		# self.view.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
		self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
		self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
		self.verticalScrollBar().valueChanged.connect(self.on_scroll)
		self.disableScroll = False
		self.scrolling = False

	# def wheelEvent(self, event: QWheelEvent):
	#     pass  # Ignore mouse wheel

	def keyPressEvent(self, event: QKeyEvent):
		super().keyPressEvent(event)  # Optional: allow other keys

	def on_scroll(self, value):
		if not self.disableScroll:
			if self.scrolling:
				return
			else:
				self.scrolling = True
				self.wdtDis.tblDisassembly.verticalScrollBar().setValue(value)
				if self.wdtDis.wdtControlFlow is not None:
					self.wdtDis.wdtControlFlow.checkHideOverflowConnections()
				self.scrolling = False


class ArrowHelperClass:

	def resizeArrow(self, parentControlFlow, arrow, size, addOffset=False):
		if arrow is not None:
			parentControlFlow.scene.removeItem(arrow)

		if not addOffset:
			pFrom = arrow.fromPos
			pTo = arrow.toPos
		else:
			if (size != 8):
				pFrom = arrow.fromPos + QPointF(-10, 0)
				pTo = arrow.toPos + QPointF(-10, 0)
			else:
				pFrom = arrow.fromPos + QPointF(10, 0)
				pTo = arrow.toPos + QPointF(10, 0)

		arrow = parentControlFlow.draw_arrow(pFrom, pTo, size, arrow.connection, arrow.startArrow)
		return arrow


class HoverLineItem(QGraphicsLineItem, ArrowHelperClass):
	connection = None

	def __init__(self, x1, y1, x2, y2, connection, parent=None):
		super().__init__(x1, y1, x2, y2, parent)
		self.connection = connection
		self.connection.mainLine = self
		self.setAcceptHoverEvents(True)
		# self.setContentsMargins(0, 0, 0, 0)
		self.context_menu = QMenu()
		self.actionGotoOrigin = self.context_menu.addAction("Goto Origin")
		self.actionGotoOrigin.triggered.connect(self.handle_gotoOrigin)
		self.actionGotoDestination = self.context_menu.addAction("Goto Destination")
		self.actionGotoDestination.triggered.connect(self.handle_gotoDestination)

	def hoverEnterEvent(self, event):
		self.connection.setPen(QPen(self.pen().color(), 3))
		self.connection.startArrow = self.resizeArrow(self.connection.parentControlFlow, self.connection.startArrow, 16)
		self.connection.endArrow = self.resizeArrow(self.connection.parentControlFlow, self.connection.endArrow, 16,
													True)

	def hoverLeaveEvent(self, event):
		self.connection.setPen(QPen(self.pen().color(), ConfigClass.controlFlowLineWidth))
		self.connection.startArrow = self.resizeArrow(self.connection.parentControlFlow, self.connection.startArrow, 8)
		self.connection.endArrow = self.resizeArrow(self.connection.parentControlFlow, self.connection.endArrow, 8,
													True)

	def mouseDoubleClickEvent(self, event, graphicsceneevent=None):
		if event.button() == Qt.MouseButton.LeftButton:
			self.context_menu.exec(event.screenPos())

	def contextMenuEvent(self, event):
		self.context_menu.exec(event.screenPos())

	def handle_gotoOrigin(self):
		# logDbg(f"handle_gotoOrigin...")
		self.connection.asmTable.setFocus(Qt.FocusReason.NoFocusReason)
		self.connection.asmTable.selectRow(self.connection.origRow)
		self.connection.asmTable.scrollToRow(self.connection.origRow)
		pass

	def handle_gotoDestination(self):
		# logDbg(f"handle_gotoDestination....")
		self.connection.asmTable.setFocus(Qt.FocusReason.NoFocusReason)
		self.connection.asmTable.selectRow(self.connection.destRow)
		self.connection.asmTable.scrollToRow(self.connection.destRow)
		pass


class HoverPolygonItem(QGraphicsPolygonItem):
	connection = None
	startArrow = True

	def __init__(self, polygon, connection, startArrow=True):
		super().__init__(polygon, None)
		self.connection = connection
		self.startArrow = startArrow
		pass

	def mouseDoubleClickEvent(self, event, graphicsceneevent=None):
		if event.button() == Qt.MouseButton.LeftButton:
			# logDbgC(f"Arrow => mouseDoubleClickEvent()")
			if self.startArrow:
				self.handle_gotoOrigin()
			else:
				self.handle_gotoDestination()

	def handle_gotoOrigin(self):
		# logDbg(f"handle_gotoOrigin...")
		self.connection.asmTable.setFocus(Qt.FocusReason.NoFocusReason)
		self.connection.asmTable.selectRow(self.connection.origRow)
		self.connection.asmTable.scrollToRow(self.connection.origRow)
		pass

	def handle_gotoDestination(self):
		# logDbg(f"handle_gotoDestination....")
		self.connection.asmTable.setFocus(Qt.FocusReason.NoFocusReason)
		self.connection.asmTable.selectRow(self.connection.destRow)
		self.connection.asmTable.scrollToRow(self.connection.destRow)
		pass


class HoverPathItem(QGraphicsPathItem, ArrowHelperClass):
	connection = None
	startArc = True

	def __init__(self, path, connection):
		super().__init__(path)
		self.connection = connection
		self.setAcceptHoverEvents(True)
		self.context_menu = QMenu()
		self.actionGotoOrigin = self.context_menu.addAction("Goto Origin")
		self.actionGotoOrigin.triggered.connect(self.handle_gotoOrigin)  # # Create a curved path
		self.actionGotoDestination = self.context_menu.addAction("Goto Destination")  # path = QPainterPath()
		self.actionGotoDestination.triggered.connect(self.handle_gotoDestination)  # path.moveTo(50, 50)

	def hoverEnterEvent(self, event):
		self.connection.setPen(QPen(self.pen().color(), ConfigClass.controlFlowLineWidthHover))
		self.connection.startArrow = self.resizeArrow(self.connection.parentControlFlow, self.connection.startArrow, 16)
		self.connection.endArrow = self.resizeArrow(self.connection.parentControlFlow, self.connection.endArrow, 16,
													True)

	def hoverLeaveEvent(self, event):
		self.connection.setPen(QPen(self.pen().color(), ConfigClass.controlFlowLineWidth))
		self.connection.startArrow = self.resizeArrow(self.connection.parentControlFlow, self.connection.startArrow, 8)
		self.connection.endArrow = self.resizeArrow(self.connection.parentControlFlow, self.connection.endArrow, 8,
													True)

	def mouseDoubleClickEvent(self, event, graphicsceneevent=None):
		if event.button() == Qt.MouseButton.LeftButton:
			if self.startArc:
				self.handle_gotoOrigin()
			else:
				self.handle_gotoDestination()

	def contextMenuEvent(self, event):
		self.context_menu.exec(event.screenPos())

	def handle_gotoOrigin(self):
		# logDbg(f"handle_gotoOrigin...")
		self.connection.asmTable.setFocus(Qt.FocusReason.NoFocusReason)
		self.connection.asmTable.selectRow(self.connection.origRow)
		self.connection.asmTable.scrollToRow(self.connection.origRow)
		pass

	def handle_gotoDestination(self):
		# logDbg(f"handle_gotoDestination....")
		self.connection.asmTable.setFocus(Qt.FocusReason.NoFocusReason)
		self.connection.asmTable.selectRow(self.connection.destRow)
		self.connection.asmTable.scrollToRow(self.connection.destRow)
		pass


class QControlFlowWidget(QWidget):
	connections = []
	# connectionsNG = []

	currStep = 0
	worker = None
	testTimerRunning = False
	startPos = QPointF(0, 0)
	testTimerAborting = False

	yPosStart = None
	yPosEnd = None

	def __init__(self, tableView, driver):
		super().__init__()

		self.setHelper = SettingsHelper()
		self.currStep = 0
		self.startAddr = 0x0
		self.endAddr = 0x0

		self.layDisassemblyCtrl = QHBoxLayout(self)
		self.wdtDisassemblyCtrl = QWidget()
		self.wdtDisassemblyCtrl.setLayout(self.layDisassemblyCtrl)
		self.wdtDisassemblyCtrl.setFixedHeight(21)
		self.image_modules_label = QClickLabel(self)
		self.image_modules_label.setContentsMargins(0, 0, 0, 0)
		self.image_modules_label.setToolTip(f"Collapse 'Select Module' combobox")
		self.image_modules_label.setStatusTip(f"Collapse 'Select Module' combobox")
		self.image_modules_label.setPixmap(
			ConfigClass.pixSystemInt.scaled(QSize(18, 18), Qt.AspectRatioMode.KeepAspectRatio,
											Qt.TransformationMode.SmoothTransformation))
		self.image_modules_label.setFixedHeight(18)

		self.layDisassemblyCtrl.addWidget(self.image_modules_label)

		self.tblDisassembly = tableView.tblDisassembly

		# Main layout
		self.thread = None
		self.tableView = tableView
		self.driver = driver
		self.layout = QVBoxLayout(self)

		# Graphics view and scene
		self.scene = QGraphicsScene()  # 0, 0, 50, 1260

		self.setContentsMargins(0, 0, 0, 0)
		self.layout.addWidget(self.wdtDisassemblyCtrl)
		self.wdtDisassemblyCtrl.setFixedHeight(18)
		self.wdtDisassemblyCtrl.setContentsMargins(0, 0, 0, 0)
		self.layDisassemblyCtrl.setContentsMargins(0, 0, 0, 0)
		# self.wdtDisassemblyCtrl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
		self.view = NoScrollGraphicsView(self.scene, self.tableView)
		# self.view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.layout.addWidget(self.view, stretch=1)
		self.layout.setContentsMargins(0, 0, 0, 0)

	def addConnection(self, conn):
		self.connections.append(conn)

	def checkHideOverflowConnections(self):
		nVisibleCon = 0
		# print(f"def checkHideOverflowConnections(self): ...")
		for con in self.connections:
			if con.mainLine is None or con.startArrow is None or con.endArrow is None:
				# if con.mainLine is None or sip.isdeleted(con.mainLine) or con.startArrow is None or sip.isdeleted(
				#         con.startArrow) or con.endArrow is None or sip.isdeleted(con.endArrow):
				continue

			# if con.mainLine is not None and not sip.isdeleted(con.mainLine):
			if con.mainLine is not None:
				rect = con.mainLine.boundingRect()

			view_rect = self.view.mapToScene(
				self.view.viewport().rect()).boundingRect()
			line_rect = con.mainLine.mapToScene(
				con.mainLine.boundingRect()).boundingRect()
			startarrow_rect = con.startArrow.mapToScene(
				con.startArrow.boundingRect()).boundingRect()
			endarrow_rect = con.endArrow.mapToScene(
				con.endArrow.boundingRect()).boundingRect()

			# print(f"nVisibleCon: {nVisibleCon} (Before) ...")
			if view_rect.intersects(line_rect):
				if nVisibleCon >= int(self.setHelper.getValue(SettingsValues.ASMMaxLines)) and not view_rect.intersects(
						startarrow_rect) and not view_rect.intersects(endarrow_rect):
					con.setVisible(False)
					continue
			else:
				con.setVisible(False)
				continue
			nVisibleCon += 1
			con.setVisible(True)
			# print(f"nVisibleCon: {nVisibleCon} (After) ...")

	def isInsideTextSectionGetRangeVarsReady(self):
		target = self.driver.getTarget()
		process = target.GetProcess()
		self.thread = process.GetThreadAtIndex(0)
		module = self.thread.GetFrameAtIndex(0).GetModule()
		for sec in module.section_iter():
			for idx3 in range(sec.GetNumSubSections()):
				subSec = sec.GetSubSectionAtIndex(idx3)
				if subSec.GetName() == "__text":
					self.startAddr = subSec.GetFileAddress()
					self.endAddr = subSec.GetFileAddress() + subSec.GetByteSize()
				elif subSec.GetName() == "__stubs":
					# self.startAddr = subSec.GetFileAddress()
					self.endAddr = subSec.GetFileAddress() + subSec.GetByteSize()

	def isInsideTextSection(self, addr):
		try:
			return self.endAddr > int(addr, 16) >= self.startAddr
		except Exception as e:
			logDbgC(f"Exception: {e}")
			return False

	def loadConnectionsThreadingStart(self):
		# self.scrollOrig = self.tblDisassembly.verticalScrollBar().value()
		# self.tblDisassembly.verticalScrollBar().value()
		self.tblDisassembly.verticalScrollBar().setValue(0)

	# workerConnections = None
	def loadConnectionsFromWorker(self, workerConnections):
		# self.workerConnections = workerConnections
		self.draw_invisibleHeight()
		tblDisassembly = self.window().wdtDisassembly.tblDisassembly

		self.scene.setSceneRect(35, 0, 80, tblDisassembly.get_total_table_height() - 2)
		# rect = self.scene.sceneRect()
		tblDisassembly.verticalScrollBar().setValue(0)
		idx = 1
		radius = 15
		# Make copy
		self.connections = copy.deepcopy(workerConnections)
		for con in self.connections:

			# addr = section.GetStartAddress()
			# load_addr = addr.GetLoadAddress(target)
			# file_addr = addr.GetFileAddress()
			#
			# print(f"Load Address: {hex(load_addr)}")
			# print(f"File Address: {hex(file_addr)}")
			# print(f"Delta (slide): {hex(load_addr - file_addr)}")

			con.origRow, niceOrigRow = tblDisassembly.getRowForAddress(
				hex(con.origAddr))  # int(tblDisassembly.getRowForAddress(hex(con.origAddr)))
			con.destRow, niceDestRow = tblDisassembly.getRowForAddress(hex(con.destAddr + (
				con.delta_addr if con.destAddr < int("0x100000000",
													 16) else 0)))  # ∑  + int("0x100018000", 16) # int(tblDisassembly.getRowForAddress(hex(con.destAddr))) #
			# print(f"self.window().driver.target: {self.window().driver.target} ...")
			# if idx >= 4:
			#     break
			con.parentControlFlow = self
			con.asmTable = tblDisassembly
			if abs(con.jumpDist / 2) <= (radius / 2):
				con.radius = abs(con.jumpDist / 2)
				radius = con.radius

			y_position = tblDisassembly.rowViewportPosition(con.origRow)
			y_position2 = tblDisassembly.rowViewportPosition(con.destRow)
			if (con.origRow > con.destRow):
				y_position = tblDisassembly.rowViewportPosition(con.destRow)
				y_position2 = tblDisassembly.rowViewportPosition(con.origRow)
				con.switched = True
			else:
				con.switched = False

			# # Map a point with the target y-coordinate to the view's coordinate system
			# qPos = QPointF(0, y_position)
			# pos = QPoint(0, y_position)
			# view_point = self.scene.views()[0].mapFromParent(pos)# QPointF(0, y_position) # self.scene.views()[0].mapFromScene(QPointF(0, y_position))
			# view_point2 = QPoint(view_point.x(), view_point.y())
			# # Get the height of the visible area
			# view_height = self.scene.views()[0].viewport().height()
			#
			# # QRect
			# # viewport_rect(0, 0, view->viewport()->width(), view->viewport()->height());
			# # QRectF
			# # visible_scene_rect = view->mapToScene(viewport_rect).boundingRect();
			# viewport_rect = QRect(self.scene.views()[0].viewport().x(), self.scene.views()[0].viewport().y(), self.scene.views()[0].viewport().width(), self.scene.views()[0].viewport().height())
			# visible_scene_rect = self.scene.views()[0].mapToScene(viewport_rect).boundingRect()
			#
			# print(f"visible_scene_rect: {visible_scene_rect} / viewport_rect: {viewport_rect} ...")
			# # if self.scene.views()[0].fitInView(pos, Qt.AspectRatioMode.IgnoreAspectRatio):
			# #     pas
			# show = False
			# if 0 <= view_point.y() <= view_height:
			#     print(f"Visible: {view_height} / { {pos}} / {view_point2} ...")
			#     show = True
			# elif view_point.y() < 0:
			#     print(f"Scroll Up: {view_height} / { {pos}} / {view_point2} ...")
			# else:
			#     print(f"Scroll Down: {view_height} / { {pos}} / {view_point2} ...")
			#
			# if not show:
			#     continue
			# logDbgC(f"Connection ({idx}) => fromY: {y_position} / toY: {y_position2} / con.origRow: {con.origRow} / con.destRow: {con.destRow} ---->>>> CON-SWITCHED: {con.switched}")
			# logDbgC(f"- Addr from: {hex(con.origAddr)} to: {hex(con.destAddr)}")
			nRowHeight = 21
			nOffsetAdd = 23
			xOffset = (controlFlowWidth / 2) + (((controlFlowWidth - radius) / 2))  # + (radius / 2)

			self.yPosStart = y_position + (nRowHeight / 2) + (radius / 2)
			self.yPosEnd = y_position2 + (nRowHeight / 2) - (radius / 2)
			line = HoverLineItem(xOffset, self.yPosStart, xOffset,
								 self.yPosEnd, con)  # 1260)
			line.setPen(QPen(con.color, con.lineWidth))
			self.scene.addItem(line)
			con.mainLine = line

			ellipse_rect = QRectF(xOffset, y_position + (nRowHeight / 2), radius, radius)

			# Create a painter path and draw a 90° arc
			path = QPainterPath()
			path.arcMoveTo(ellipse_rect, 90)  # Start at 0 degrees
			path.arcTo(ellipse_rect, 90, 90)  # Draw 90-degree arc clockwise

			# Add the path to the scene
			arc_item = HoverPathItem(path, con)
			arc_item.startArc = con.switched
			arc_item.setPen(QPen(con.color, con.lineWidth))
			self.scene.addItem(arc_item)
			con.topArc = arc_item

			ellipse_rect2 = QRectF(xOffset, y_position2 + (nRowHeight / 2) - (radius), radius,
								   radius)
			# Create a painter path and draw a 90° arc
			path2 = QPainterPath()
			path2.arcMoveTo(ellipse_rect2, 180)  # Start at 0 degrees
			path2.arcTo(ellipse_rect2, 180, 90)  # Draw 90-degree arc clockwise

			# Add the path to the scene
			arc_item2 = HoverPathItem(path2, con)
			arc_item2.startArc = not con.switched
			arc_item2.setPen(QPen(con.color, con.lineWidth))
			self.scene.addItem(arc_item2)
			con.bottomArc = arc_item2
			if con.switched:
				arrowStart = QPointF(xOffset + (radius / 2) - 6 + 2, y_position + (
						nRowHeight / 2))
				arrowEnd = QPointF(xOffset + (radius / 2) + 6, y_position + (nRowHeight / 2))
				con.startArrow = self.draw_arrow(arrowStart, arrowEnd, 8, con, True)
			else:
				arrowEnd = QPointF(xOffset + (radius / 2) - 6 + 2, y_position + (
						nRowHeight / 2))
				arrowStart = QPointF(xOffset + (radius / 2) + 6,
									 y_position + (nRowHeight / 2))
				con.endArrow = self.draw_arrow(arrowStart, arrowEnd, 8, con, False)

			if con.switched:
				arrowEnd = QPointF(xOffset + (radius / 2) - 6 + 2, y_position2 + (
						nRowHeight / 2))
				arrowStart = QPointF(xOffset + (radius / 2) + 6,
									 y_position2 + (nRowHeight / 2))
				con.endArrow = self.draw_arrow(arrowStart, arrowEnd, 8, con, False)
			else:
				arrowStart = QPointF(xOffset + (radius / 2) - 6 + 2, y_position2 + (
						nRowHeight / 2))
				arrowEnd = QPointF(xOffset + (radius / 2) + 6,
								   y_position2 + (nRowHeight / 2))
				con.startArrow = self.draw_arrow(arrowStart, arrowEnd, 8, con, True)

			con.setToolTip(
				f"Branch ({con.mnemonic.upper()})\n- from: {hex(con.origAddr)}\n- to: {hex(con.destAddr)}\n- distance: {hex(con.jumpDist)}\n- row from: {niceOrigRow} to: {niceDestRow}")
			if radius <= 120:
				radius += 12
			idx += 1
			# logDbgC(
			#     f"Control Flow loadConnections() => scrollBar.value(): {tblDisassembly.verticalScrollBar().value()} / {y_position} / {y_position2} ... ",
			#     DebugLevel.Verbose)

	@staticmethod
	def draw_flowConnection(startRow, endRow, startAddr, endAddr, table, color=None, radius=50, lineWidth=1,
							switched=False):
		newCon = ControlFlowConnection(startRow, endRow, startAddr, endAddr, table)
		newCon.switched = switched
		newCon.color = color or random_qcolor()
		newCon.origRow = startRow
		newCon.origAddr = startAddr
		newCon.destRow = endRow
		newCon.destAddr = endAddr
		newCon.radius = radius
		return newCon

	# THIS FUNCTION ENSURES THAT THE CANVAS HAS FULL SIZE - DO NOT DELETE!!!
	def draw_invisibleHeight(self):
		start = QPointF(15, 0)
		end = QPointF(15, 0)
		line1 = QGraphicsLineItem(start.x() + 20, 0, end.x() + 20,
								  self.tableView.tblDisassembly.viewport().height() - 5 + 250)
		line1.setPen(QPen(QColor("transparent"), 0))
		self.scene.addItem(line1)

	def draw_arrow(self, fromPos, toPos, arrow_size=8, connection=None, startArrow=True):
		direction = (toPos - fromPos)
		direction /= (direction.manhattanLength() or 1)
		perp = QPointF(-direction.y(), direction.x())
		p1 = toPos - direction * arrow_size + perp * arrow_size / 2
		p2 = toPos - direction * arrow_size - perp * arrow_size / 2

		points = [toPos, p1, p2]
		polygon = QPolygonF(points)

		arrow_head = HoverPolygonItem(polygon, connection, startArrow)
		arrow_head.setPen(QPen(connection.color))
		arrow_head.setBrush(QBrush(QColor("transparent")) if arrow_size == 8 else QBrush(connection.color))
		arrow_head.fromPos = fromPos
		arrow_head.toPos = toPos
		arrow_head.arrow_size = arrow_size

		self.scene.addItem(arrow_head)

		return arrow_head

	def resetContent(self, resetCon=False):
		if resetCon:
			self.connections.clear()
		self.scene.clear()
