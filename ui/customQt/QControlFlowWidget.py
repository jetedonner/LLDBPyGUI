import lldb
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsLineItem, QGraphicsEllipseItem, QTableWidget, QTableWidgetItem, QSizePolicy, QGraphicsPathItem, QMenu
)
from PyQt6.QtGui import QBrush, QPen, QColor, QTransform, QPainterPath, QPolygonF
from PyQt6.QtCore import Qt, QPointF, QLineF
from PyQt6.QtWidgets import QScrollBar

from PyQt6.QtGui import QPainter
from PyQt6.QtCore import QPointF, QRectF

from PyQt6.QtGui import QWheelEvent, QKeyEvent

from dbg.breakpointHelper import arrRememberedLocs
from ui.helper.dbgOutputHelper import *
from lib.utils import *
from config import *

controlFlowWidth = 110

# import threading
# import time
#
# class Repeater(threading.Thread):
#     def __init__(self, interval, function):
#         super().__init__()
#         self.interval = interval
#         self.function = function
#         self.stop_event = threading.Event()
#
#     def run(self):
#         while not self.stop_event.wait(self.interval):
#             self.function()
#
#     def stop(self):
#         self.stop_event.set()

from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
import sys

# Worker thread that emits a signal every 0.5 seconds
class IntervalWorker(QThread):
    tick = pyqtSignal()

    def run(self):
        self.timer = QTimer()
        self.timer.setInterval(150)  # 0.5 seconds
        self.timer.timeout.connect(self.tick.emit)
        self.timer.start()
        self.exec()  # Start event loop for the timer

class ControlFlowConnectionNG():

    parentControlFlow = None
    asmTable = None
    oringPos = QPointF(0, 0)
    origRow = 0
    origAddr = 0x0
    destPos = QPointF(0, 0)
    destRow = 0
    destAddr = 0x0
    jumpDist = 0x0
    mnemonic = ""
    color = random_qcolor() # QColor("red")
    lineWidth = 1
    switched = False
    radius = 0x0

    startArrow = None
    endArrow = None

    mainLine = None
    topArc = None
    bottomArc = None

    def __init__(self, startRow = 0, endRow = 0, origAddr = 0x0, destAddr = 0x0, table = None):
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

    def setPen(self, pen = None):
        if pen is not None:
            newPen = pen
        else:
            # newPen = QPen(self.pen().color(), 1)
            newPen = QPen(QColor("red"), 1)
        self.mainLine.setPen(newPen)
        self.topArc.setPen(newPen)
        self.bottomArc.setPen(newPen)

class NoScrollGraphicsView(QGraphicsView):

    disableScroll = False
    scrolling = False

    def __init__(self, scene):
        super().__init__(scene)

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
            if  self.scrolling:
                return
            else:
                self.scrolling = True
                # logDbgC(f"on_scroll({value}")
                self.window().txtMultiline.table.verticalScrollBar().setValue(value)
                if self.window().wdtControlFlow is not None:
                    self.window().wdtControlFlow.checkHideOverflowConnections()
                self.scrolling = False

class ArrowHelperClass:

    def resizeArrow(self, parentControlFlow, arrow, size, addOffset = False):
        if arrow is not None:
            parentControlFlow.scene.removeItem(arrow)

        if not addOffset:
            pFrom = arrow.fromPos
            pTo = arrow.toPos
        else:
            if(size != 8):
                pFrom = arrow.fromPos + QPointF(-10, 0)
                pTo = arrow.toPos + QPointF(-10, 0)
            else:
                pFrom = arrow.fromPos + QPointF(10, 0)
                pTo = arrow.toPos + QPointF(10, 0)

        arrow = parentControlFlow.draw_arrowNG(pFrom, pTo, size, arrow.connection, arrow.startArrow)
        return arrow

class HoverLineItem(QGraphicsLineItem, ArrowHelperClass):
    # def __init__(self, line: QLineF):
    connection = None
    
    def __init__(self, x1, y1, x2, y2, connection, parent = None):
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
        # self.setToolTip(f"HELLLO TOOLTIP!!!")

    def hoverEnterEvent(self, event):
        self.connection.setPen(QPen(self.pen().color(), 3))
        self.connection.startArrow = self.resizeArrow(self.connection.parentControlFlow, self.connection.startArrow, 16)
        self.connection.endArrow = self.resizeArrow(self.connection.parentControlFlow, self.connection.endArrow, 16, True)

    def hoverLeaveEvent(self, event):
        self.connection.setPen(QPen(self.pen().color(), 1))
        self.connection.startArrow = self.resizeArrow(self.connection.parentControlFlow, self.connection.startArrow, 8)
        self.connection.endArrow = self.resizeArrow(self.connection.parentControlFlow, self.connection.endArrow, 8, True)

    def mouseDoubleClickEvent(self, event, graphicsceneevent = None):
        if event.button() == Qt.MouseButton.LeftButton:
            self.context_menu.exec(event.screenPos())

            # Show the menu at the cursor position
            # menu.exec(event.globalPosition().toPoint())

    def contextMenuEvent(self, event):
        self.context_menu.exec(event.screenPos())

    def handle_gotoOrigin(self):
        logDbg(f"handle_gotoOrigin...")
        # self.connection.asmTable.scrollToRow(self.connection.origRow)
        self.connection.asmTable.setFocus(Qt.FocusReason.NoFocusReason)
        self.connection.asmTable.selectRow(self.connection.origRow)
        self.connection.asmTable.scrollToRow(self.connection.origRow)
        pass

    def handle_gotoDestination(self):
        logDbg(f"handle_gotoDestination....")
        # self.connection.asmTable.scrollToRow(self.connection.destRow)
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
            logDbgC(f"Arrow => mouseDoubleClickEvent()")
            # pass
            # self.context_menu.exec(event.screenPos())
            if self.startArrow:
                self.handle_gotoOrigin()
            else:
                self.handle_gotoDestination()

    def handle_gotoOrigin(self):
        logDbg(f"handle_gotoOrigin...")
        self.connection.asmTable.setFocus(Qt.FocusReason.NoFocusReason)
        self.connection.asmTable.selectRow(self.connection.origRow)
        self.connection.asmTable.scrollToRow(self.connection.origRow)
        pass

    def handle_gotoDestination(self):
        logDbg(f"handle_gotoDestination....")
        # self.connection.asmTable.scrollToRow(self.connection.destRow)
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
        self.actionGotoOrigin.triggered.connect(self.handle_gotoOrigin)# # Create a curved path
        self.actionGotoDestination = self.context_menu.addAction("Goto Destination")# path = QPainterPath()
        self.actionGotoDestination.triggered.connect(self.handle_gotoDestination)# path.moveTo(50, 50)

    def hoverEnterEvent(self, event):
        self.connection.setPen(QPen(self.pen().color(), 3))
        self.connection.startArrow = self.resizeArrow(self.connection.parentControlFlow, self.connection.startArrow, 16)
        self.connection.endArrow = self.resizeArrow(self.connection.parentControlFlow, self.connection.endArrow, 16, True)

    def hoverLeaveEvent(self, event):
        self.connection.setPen(QPen(self.pen().color(), 1))
        self.connection.startArrow = self.resizeArrow(self.connection.parentControlFlow, self.connection.startArrow, 8)
        self.connection.endArrow = self.resizeArrow(self.connection.parentControlFlow, self.connection.endArrow, 8, True)

    def mouseDoubleClickEvent(self, event, graphicsceneevent=None):
        if event.button() == Qt.MouseButton.LeftButton:
            # self.context_menu.exec(event.screenPos())
            if self.startArc:
                self.handle_gotoOrigin()
            else:
                self.handle_gotoDestination()
            # Show the menu at the cursor position
            # menu.exec(event.globalPosition().toPoint())

    def contextMenuEvent(self, event):
        self.context_menu.exec(event.screenPos())

    def handle_gotoOrigin(self):
        logDbg(f"handle_gotoOrigin...")
        self.connection.asmTable.setFocus(Qt.FocusReason.NoFocusReason)
        self.connection.asmTable.selectRow(self.connection.origRow)
        self.connection.asmTable.scrollToRow(self.connection.origRow)
        pass
    
    def handle_gotoDestination(self):
        logDbg(f"handle_gotoDestination....")
        # self.connection.asmTable.scrollToRow(self.connection.destRow)
        self.connection.asmTable.setFocus(Qt.FocusReason.NoFocusReason)
        self.connection.asmTable.selectRow(self.connection.destRow)
        self.connection.asmTable.scrollToRow(self.connection.destRow)
        pass

class QControlFlowWidget(QWidget):

    connections = []
    connectionsNG = []

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

        # Main layout
        self.thread = None
        self.tableView = tableView
        self.driver = driver
        self.layout = QVBoxLayout(self)

        # Graphics view and scene
        self.scene = QGraphicsScene() # 0, 0, 50, 1260

        self.setContentsMargins(0, 0, 0, 0)
        self.view = NoScrollGraphicsView(self.scene)
        self.layout.addWidget(self.view)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # self.draw_instructions()

    def addConnection(self, conn):
        self.connections.append(conn)

    def checkHideOverflowConnections(self):
        nVisibleCon = 0
        for con in self.connections:
            # print(f"con: {con}, con.mainLine: {con.mainLine}")
            # con.origRow
            if con.mainLine is None or con.startArrow is None or con.endArrow is None:
                continue

            view_rect = self.view.mapToScene(
                self.view.viewport().rect()).boundingRect()
            line_rect = con.mainLine.mapToScene(
                con.mainLine.boundingRect()).boundingRect()
            startarrow_rect = con.startArrow.mapToScene(
                con.startArrow.boundingRect()).boundingRect()
            endarrow_rect = con.startArrow.mapToScene(
                con.endArrow.boundingRect()).boundingRect()

            if view_rect.intersects(line_rect):
                nVisibleCon += 1
                if nVisibleCon >= int(self.setHelper.getValue(SettingsValues.ASMMaxLines)) and not view_rect.intersects(startarrow_rect) and not view_rect.intersects(endarrow_rect):
                    con.mainLine.setVisible(False)
                    con.startArrow.setVisible(False)
                    con.endArrow.setVisible(False)
                    con.bottomArc.setVisible(False)
                    con.topArc.setVisible(False)
                    continue
            else:
                # logDbg(f"Line item IS NOOOOOTTTTT VISIBLE in the view!!!!")
                # self.connectionsNG[5].mainLine.setVisible(False)
                pass
            con.mainLine.setVisible(True)
            con.startArrow.setVisible(True)
            con.endArrow.setVisible(True)
            con.bottomArc.setVisible(True)
            con.topArc.setVisible(True)
            pass
        pass

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
        # except (ValueError, TypeError) as e:
        #     print(f"Caught a value or type error: {e}")
        except Exception as e:
            logDbgC(f"Exception: {e}")
            return False

    def loadConnectionsThreadingStart(self):
        tblDisassembly = self.window().txtMultiline.table
        scrollOrig = tblDisassembly.verticalScrollBar().value()
        tblDisassembly.verticalScrollBar().setValue(0)

    def loadConnections(self):
        # logDbgC(f"Control Flow loadConnections() ... (from inside func) ...")
        # radius = 140
        return
        radius = 10

        tblDisassembly = self.window().txtMultiline.table
        scrollOrig = tblDisassembly.verticalScrollBar().value()
        scrollOrig2 = self.view.verticalScrollBar().value()
        logDbgC(f"Control Flow loadConnections() => scrollOrig: {scrollOrig} / {scrollOrig2}", DebugLevel.Verbose)
        tblDisassembly.verticalScrollBar().setValue(0)
        self.isInsideTextSectionGetRangeVarsReady()
        for row in range(tblDisassembly.rowCount()):
            if tblDisassembly.item(row, 3) is None:
                continue

            # doDisassemble FlowControl
            sMnemonic = tblDisassembly.item(row, 3).text()
            if sMnemonic is not None and sMnemonic.startswith(JMP_MNEMONICS) and not sMnemonic.startswith(JMP_MNEMONICS_EXCLUDE):
                sAddrJumpTo = tblDisassembly.item(row, 4).text()
                if self.isInsideTextSection(sAddrJumpTo):
                    sAddrJumpFrom = tblDisassembly.item(row, 2).text()
                    # logDbg(f"Found instruction with jump @: {sAddrJumpFrom} / isInside: {sAddrJumpTo}!")
                    rowStart = int(tblDisassembly.getRowForAddress(sAddrJumpFrom))
                    rowEnd = int(tblDisassembly.getRowForAddress(sAddrJumpTo))

                    if (rowStart < rowEnd):
                        # QColor("lightblue")
                        newConObj = QControlFlowWidget.draw_flowConnectionNG(rowStart, rowEnd, int(sAddrJumpFrom, 16), int(sAddrJumpTo, 16), self.window().txtMultiline.table, random_qcolor(), radius)
                    else:
                        # QColor("lightgreen")
                        newConObj = QControlFlowWidget.draw_flowConnectionNG(rowEnd, rowStart, int(sAddrJumpFrom, 16), int(sAddrJumpTo, 16), self.window().txtMultiline.table, random_qcolor(), radius, 1, True)
                    newConObj.parentControlFlow = self
                    self.addConnection(newConObj)
                    # if radius >= 10:
                    #     radius -= 10
                    if radius <= 130:
                        radius += 15
        self.connections.sort(key=lambda x: abs(x.jumpDist), reverse=True)

        idx = 1
        radius = 10
        for con in self.connections:
            y_position = tblDisassembly.rowViewportPosition(con.origRow)
            y_position2 = tblDisassembly.rowViewportPosition(con.destRow)

            nRowHeight = 21
            nOffsetAdd = 23
            xOffset = (controlFlowWidth / 2) + (((controlFlowWidth - radius) / 2)) # + (radius / 2)

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
            arc_item2.setPen(QPen(con.color, con.lineWidth))
            self.scene.addItem(arc_item2)
            con.bottomArc = arc_item2

            if con.switched:
                arrowStart = QPointF(xOffset + (radius / 2) - 6 + 2, y_position + (
                        nRowHeight / 2))
                arrowEnd = QPointF(xOffset + (radius / 2) + 2, y_position + (nRowHeight / 2))
                con.startArrow = self.draw_arrowNG(arrowStart, arrowEnd, 8, con, True)
            else:
                arrowEnd = QPointF(xOffset + (radius / 2) - 6 + 2, y_position + (
                        nRowHeight / 2))
                arrowStart = QPointF(xOffset + (radius / 2) + 2,
                                     y_position + (nRowHeight / 2))
                con.endArrow = self.draw_arrowNG(arrowStart, arrowEnd, 8, con, False)

            if con.switched:
                arrowEnd = QPointF(xOffset + (radius / 2) - 6 + 2, y_position2 + (
                        nRowHeight / 2))
                arrowStart = QPointF(xOffset + (radius / 2) + 2,
                                     y_position2 + (nRowHeight / 2))
                con.endArrow = self.draw_arrowNG(arrowStart, arrowEnd, 8, con, False)
            else:
                arrowStart = QPointF(xOffset + (radius / 2) - 6 + 2, y_position2 + (
                        nRowHeight / 2))
                arrowEnd = QPointF(xOffset + (radius / 2) + 2,
                                   y_position2 + (nRowHeight / 2))
                con.startArrow = self.draw_arrowNG(arrowStart, arrowEnd, 8, con, True)

            con.setToolTip(f"Branch ({con.mnemonic.upper()})\n-from: {hex(con.origAddr)}\n-to: {hex(con.destAddr)}\n-distance: {hex(con.jumpDist)}")
            if radius <= 130:
                radius += 15
            idx += 1

        logDbgC(f"Control Flow loadConnections() => scrollOrig: {scrollOrig}", DebugLevel.Verbose)
        tblDisassembly.verticalScrollBar().setValue(scrollOrig)
        self.view.verticalScrollBar().setValue(scrollOrig)
        # pass

    def loadConnectionsFromWorker(self, workerConnections):
        tblDisassembly = self.window().txtMultiline.table

        self.scene.setSceneRect(35, 0, 79.5, tblDisassembly.get_total_table_height() - 2)
        rect = self.scene.sceneRect()
        logDbgC(f"rect: {rect}, tblDisassembly.get_total_table_height(): {tblDisassembly.get_total_table_height()}")
        # rect.setHeight(tblDisassembly.get_total_table_height() - 2 + 250)
        # # self.scene.setSceneRect(rect)
        # self.scene.setMinimumRenderSize(QSize(75, tblDisassembly.get_total_table_height() - 2 + 250))
        #
        # # self.scene.sceneRect().setHeight(tblDisassembly.get_total_table_height() - 2 + 250)
        tblDisassembly.verticalScrollBar().setValue(0)
        idx = 1
        radius = 15
        self.connections = workerConnections
        for con in self.connections:
            con.parentControlFlow = self
            con.asmTable = tblDisassembly
            if abs(con.jumpDist / 2) <= (radius / 2):
                con.radius = abs(con.jumpDist / 2)
                radius = con.radius
            # if con. is None:
            #     continue

            # addr = self.driver.getTarget().ResolveLoadAddress(con.destAddr)
            # function = addr.GetFunction()
            # if function.IsValid():
            #     logDbgC(f"Function name: {function.GetName()}")
            # else:
            #     logDbgC(f"No function found at this address.")
            #
            # context = self.driver.getTarget().ResolveSymbolContextForAddress(addr, lldb.eSymbolContextEverything)
            # func = context.GetFunction()
            # print(context)
            # print(dir(context))
            # if func.IsValid():
            #     print("Function name:", func.GetName())
            # else:
            #     print("Function not found via symbol context.")
            #
            # symbols = []
            # for module in self.driver.getTarget().module_iter():
            #     for symbol in module:
            #         if symbol.IsValid():
            #             symbols.append(symbol)
            #
            # symbols.sort(key=lambda s: s.GetStartAddress().GetLoadAddress(self.driver.getTarget()))
            #
            # # current_addr = self.driver.getTarget().ResolveLoadAddress(con.destAddr)
            #
            # idxNGDef = 1
            # for idxNG, symbol in enumerate(symbols):
            #     start = symbol.GetStartAddress().GetLoadAddress(self.driver.getTarget())
            #     end = symbol.GetEndAddress().GetLoadAddress(self.driver.getTarget())
            #
            #     if start <= con.destAddr < end:
            #         logDbgC(f"Current symbol '{symbol.GetName()}' is number {idxNG} in the disassembly order.")
            #         # idxNGDef = idxNG - 1
            #         break
            #     idxNGDef += 1

            con.origRow = int(tblDisassembly.getRowForAddress(hex(con.origAddr)))
            con.destRow = int(tblDisassembly.getRowForAddress(hex(con.destAddr)))

            # for idx, symbol in enumerate(symbols):
            #     if symbol.ContainsAddress(addr):
            #         logDbgC(f"Current symbol '{symbol.GetName()}' is number {idx + 1} in the disassembly order.")
            #         break

            y_position = tblDisassembly.rowViewportPosition(con.origRow)# + idxNGDef)#(1 if con.origRow == 0 else 0))
            y_position2 = tblDisassembly.rowViewportPosition(con.destRow)# - idxNGDef)#(1 if con.destRow == 0 else 0) + 0)
            if(con.origRow > con.destRow):
                y_position = tblDisassembly.rowViewportPosition(con.destRow)# + idxNGDef)#(1 if con.origRow == 0 else 0))
                y_position2 = tblDisassembly.rowViewportPosition(con.origRow)# + idxNGDef)#(1 if con.destRow == 0 else 0) + 0)
                con.switched = True
            else:
                con.switched = False

            logDbgC(f"Connection ({idx}) => fromY: {y_position} / toY: {y_position2} / con.origRow: {con.origRow} / con.destRow: {con.destRow} ---->>>> CON-SWITCHED: {con.switched}")
            logDbgC(f"- Addr from: {hex(con.origAddr)} to: {hex(con.destAddr)}")
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
            # logDbgC(f"---->>>> CON-SWITCHED: {con.switched}")
            if con.switched:
                arrowStart = QPointF(xOffset + (radius / 2) - 6 + 2, y_position + (
                        nRowHeight / 2))
                arrowEnd = QPointF(xOffset + (radius / 2) + 2, y_position + (nRowHeight / 2))
                con.startArrow = self.draw_arrowNG(arrowStart, arrowEnd, 8, con, True)
            else:
                arrowEnd = QPointF(xOffset + (radius / 2) - 6 + 2, y_position + (
                        nRowHeight / 2))
                arrowStart = QPointF(xOffset + (radius / 2) + 2,
                                     y_position + (nRowHeight / 2))
                con.endArrow = self.draw_arrowNG(arrowStart, arrowEnd, 8, con, False)
                # arrowStart = QPointF(xOffset + (radius / 2) - 6 + 2, y_position2 + (
                #         nRowHeight / 2))
                # arrowEnd = QPointF(xOffset + (radius / 2) + 2,
                #                    y_position2 + (nRowHeight / 2))
                # con.startArrow = self.draw_arrowNG(arrowStart, arrowEnd)

            if con.switched:
                arrowEnd = QPointF(xOffset + (radius / 2) - 6 + 2, y_position2 + (
                        nRowHeight / 2))
                arrowStart = QPointF(xOffset + (radius / 2) + 2,
                                     y_position2 + (nRowHeight / 2))
                con.endArrow = self.draw_arrowNG(arrowStart, arrowEnd, 8, con, False)
            else:
                arrowStart = QPointF(xOffset + (radius / 2) - 6 + 2, y_position2 + (
                        nRowHeight / 2))
                arrowEnd = QPointF(xOffset + (radius / 2) + 2,
                                   y_position2 + (nRowHeight / 2))
                con.startArrow = self.draw_arrowNG(arrowStart, arrowEnd, 8, con, True)
                # arrowEnd = QPointF(xOffset + (radius / 2) - 6 + 2, y_position + (
                #         nRowHeight / 2))
                # arrowStart = QPointF(xOffset + (radius / 2) + 2,
                #                      y_position + (nRowHeight / 2))
                # con.endArrow = self.draw_arrowNG(arrowStart, arrowEnd)

            con.setToolTip(
                f"Branch ({con.mnemonic.upper()})\n- from: {hex(con.origAddr)}\n- to: {hex(con.destAddr)}\n- distance: {hex(con.jumpDist)}\n- row from: {con.origRow} to: {con.destRow}")
            if radius <= 130:
                radius += 15
            idx += 1

    def loadInstructions(self):
        radius = 75
        self.scene.setSceneRect(0, 0, 75, self.tableView.table.get_total_table_height() - 2)
        scrollOrig = self.window().txtMultiline.table.verticalScrollBar().value()
        self.window().txtMultiline.table.verticalScrollBar().setValue(0)
        for row in range(self.window().txtMultiline.table.rowCount()):
            if self.window().txtMultiline.table.item(row, 3) is not None and self.window().txtMultiline.table.item(row, 3).text().startswith(JMP_MNEMONICS): #("call", "jmp", "jne", "jz", "je", "jnz", "jle", "jl", "jge", "jg")):
                sAddrJumpTo = self.window().txtMultiline.table.item(row, 4).text()
                if self.isInsideTextSection(sAddrJumpTo):
                    sAddrJumpFrom = self.window().txtMultiline.table.item(row, 2).text()
                    # logDbg(f"Found instruction with jump @: {sAddrJumpFrom} / isInside: {sAddrJumpTo}!")
                    rowStart = int(self.window().txtMultiline.table.getRowForAddress(sAddrJumpFrom))
                    rowEnd = int(self.window().txtMultiline.table.getRowForAddress(sAddrJumpTo))
                    if (rowStart < rowEnd):
                        # QColor("lightblue")
                        newConObj = self.draw_flowConnection(rowStart, rowEnd, random_qcolor(), radius)
                    else:
                        # QColor("lightgreen")
                        newConObj = self.draw_flowConnection(rowEnd, rowStart, random_qcolor(), radius, 1, True)

                    newConObj.parentControlFlow = self
                    newConObj.setToolTip(f"Branch from {sAddrJumpFrom} to {sAddrJumpTo}")
                    if radius >= 20:
                        radius -= 10

        self.window().txtMultiline.table.verticalScrollBar().setValue(scrollOrig)

    def toggleTestTimer(self):
        if self.testTimerAborting:
            return

        self.testTimerRunning = not self.testTimerRunning
        if self.testTimerRunning:
            self.startPos = self.connections[0].startArrow.pos()
            self.connections[0].startArrow.setPos(self.startPos + QPointF(-8, 0))
            self.worker = IntervalWorker()
            self.worker.tick.connect(self.on_tick)
            self.worker.start()
        else:
            self.testTimerAborting = True
            self.worker.quit()
            self.worker.wait()
            self.currStep = 0
            self.connections[0].startArrow.setPos(self.startPos)
            self.testTimerAborting = False

    def on_tick(self):
        self.currStep += 1
        logDbg(f"Tick at 0.5s interval! Step: {self.currStep}")
        if self.currStep % 5 == 0:
            self.connections[0].startArrow.setPos(self.startPos + QPointF(-8, 0))
            self.connections[0].endArrow.moveBy(8, 0)
            self.currStep = 0
        else:
            self.connections[0].startArrow.setPos(self.startPos + QPointF(-8 + (2 * self.currStep), 0))
            self.connections[0].endArrow.moveBy(-2, 0)

    @staticmethod
    def draw_flowConnectionNG(startRow, endRow, startAddr, endAddr, table, color=None, radius=50, lineWidth=1, switched=False):
        newConnectionNG = ControlFlowConnectionNG(startRow, endRow, startAddr, endAddr, table)
        newConnectionNG.switched = switched
        newConnectionNG.color = color or random_qcolor()
        newConnectionNG.origRow = startRow
        newConnectionNG.origAddr = startAddr
        newConnectionNG.destRow = endRow
        newConnectionNG.destAddr = endAddr
        newConnectionNG.radius = radius

        return newConnectionNG

    def logViewportHeight(self):
        logDbgC(f"self.tableView.table.viewport().height(): {self.tableView.table.viewport().height()}")

    # THIS FUNCTION ENSURES THAT THE CANVAS HAS FULL SIZE - DO NOT DELETE!!!
    def draw_instructions(self):
        start = QPointF(15, 0)
        end = QPointF(15, 0)
        # print(f"self.tableView.viewport().height() => {self.tableView.table.viewport().height()}")
        line1 = QGraphicsLineItem(start.x() + 20, 0, end.x() + 20, self.tableView.table.viewport().height() - 5 + 250)
        # self.logViewportHeight()
        line1.setPen(QPen(QColor("transparent"), 0))
        self.scene.addItem(line1)
    
    def draw_arrowNG(self, fromPos, toPos, arrow_size = 8, connection=None, startArrow=True):
        direction = (toPos - fromPos)
        direction /= (direction.manhattanLength() or 1)
        perp = QPointF(-direction.y(), direction.x())
        p1 = toPos - direction * arrow_size + perp * arrow_size / 2
        p2 = toPos - direction * arrow_size - perp * arrow_size / 2

        points = [toPos, p1, p2]
        # # Convert to QPolygonF
        polygon = QPolygonF(points)

        # arrow_head = self.scene.addPolygon(
        #     # [end, p1, p2],
        #     polygon,
        #     QPen(QColor("lightgreen")),
        #     QBrush(QColor("transparent")) if arrow_size == 8 else QBrush(QColor("lightgreen")) # lightgreen")) #
        # )

        # arrow_head.fromPos = fromPos
        # arrow_head.toPos = toPos
        # arrow_head.arrow_size = arrow_size

        arrow_headNG = HoverPolygonItem(polygon, connection, startArrow)
        # QColor("lightgreen")
        arrow_headNG.setPen(QPen(connection.color))
        # QColor("lightgreen")
        arrow_headNG.setBrush(QBrush(QColor("transparent")) if arrow_size == 8 else QBrush(connection.color))
        arrow_headNG.fromPos = fromPos
        arrow_headNG.toPos = toPos
        arrow_headNG.arrow_size = arrow_size

        self.scene.addItem(arrow_headNG)

        return arrow_headNG
        # return arrow_head

    def resetContent(self):
        self.connections.clear()
        self.scene.clear()
        pass