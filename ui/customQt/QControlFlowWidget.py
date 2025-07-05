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
from ui.helper.dbgOutputHelper import *

controlFlowWidth = 80

class ControlFlowConnection():

    asmTable = None
    originRow = 0
    destRow = 0

    mainLine = None
    topArc = None
    bottomArc = None
    
    def __init__(self):
        super().__init__()

    def setToolTip(self, tooltip):
        self.mainLine.setToolTip(tooltip)
        self.topArc.setToolTip(tooltip)
        self.bottomArc.setToolTip(tooltip)
        pass

class FixedScrollBar(QScrollBar):
    
    def __init__(self):
        super().__init__()
        self.rangeChanged.connect(self.on_range_changed)

    def on_range_changed(self, min_val, max_val):
        print("Intercepted range change:", min_val, max_val)
        # Optionally override behavior here
        self.setRange(min_val, max_val)
        
    def setRange(self, min_val, max_val):
        fixed_max = 1102  # or whatever you want
        # logDbg(f"setRange({min(fixed_max, max_val)}) / {max_val}")
        super().setRange(min_val, min(fixed_max, max_val))


class NoScrollGraphicsView(QGraphicsView):

    def __init__(self, scene):
        super().__init__(scene)

        # self.setSceneRect(scene.itemsBoundingRect())  # Lock scene bounds
        # self.setDragMode(QGraphicsView.DragMode.NoDrag)
        # self.view.verticalScrollBar().valueChanged.connect(self.on_scroll)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("background-color: #393939; border: 1px solid darkgray;")
        # self.view.setStyleSheet("background-color: transparent; border: none;")
        self.setContentsMargins(0, 0, 0, 0)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        # self.view.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.verticalScrollBar().valueChanged.connect(self.on_scroll)

        # scene.setSceneRect(0, 0, 50, 1260)  # Or whatever size you need


    def wheelEvent(self, event: QWheelEvent):
        pass  # Ignore mouse wheel

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)  # Optional: allow other keys

    disableScroll = False
    def on_scroll(self, value):
        if not self.disableScroll:
            # print(f"Scrolled to position: {value}")
            # logDbg(f"scroll: {value + 150}")
            self.window().txtMultiline.table.verticalScrollBar().setValue(value)
        # self.window().wdtControlFlow.view.centerOn(0, value + 150) # / 0.8231292517)
        # self.scroll()
        # self.view.verticalScrollBar().scroll(0, 0.783171521)

class HoverLineItem(QGraphicsLineItem):
    # def __init__(self, line: QLineF):
    connection = None
    
    def __init__(self, x1, y1, x2, y2, connection, parent = None):
        super().__init__(x1, y1, x2, y2, parent)
        self.connection = connection
        self.connection.mainLine = self
        self.setAcceptHoverEvents(True)
        self.context_menu = QMenu()
        self.actionGotoOrigin = self.context_menu.addAction("Goto Origin")
        self.actionGotoOrigin.triggered.connect(self.handle_gotoOrigin)
        self.actionGotoDestination = self.context_menu.addAction("Goto Destination")
        self.actionGotoDestination.triggered.connect(self.handle_gotoDestination)
        # self.setToolTip(f"HELLLO TOOLTIP!!!")

    def hoverEnterEvent(self, event):
        logDbg("Hover entered line")
        newPen = QPen(self.pen().color(), 3)
        self.setPen(newPen)
        self.connection.topArc.setPen(newPen)
        self.connection.bottomArc.setPen(newPen)
        # self.setPen(QPen(QColor("red"), 3))  # Highlight on hover

    def hoverLeaveEvent(self, event):
        logDbg("Hover left line")
        newPen = QPen(self.pen().color(), 1)
        self.setPen(newPen)
        self.connection.topArc.setPen(newPen)
        self.connection.bottomArc.setPen(newPen)
        # self.setPen(QPen(QColor("black"), 3))  # Reset color

    def contextMenuEvent(self, event):
        self.context_menu.exec(event.screenPos())

    def handle_gotoOrigin(self):
        logDbg(f"handle_gotoOrigin...")
        self.connection.asmTable.scrollToRow(self.connection.originRow)
        pass

    def handle_gotoDestination(self):
        logDbg(f"handle_gotoDestination....")
        self.connection.asmTable.scrollToRow(self.connection.destRow)
        pass

class HoverPathItem(QGraphicsPathItem):

    connection = None

    def __init__(self, path, connection):
        super().__init__(path)
        self.connection = connection
        # Enable hover events
        self.setAcceptHoverEvents(True)

        self.context_menu = QMenu()
        self.actionGotoOrigin = self.context_menu.addAction("Goto Origin")
        self.actionGotoOrigin.triggered.connect(self.handle_gotoOrigin)# # Create a curved path
        self.actionGotoDestination = self.context_menu.addAction("Goto Destination")# path = QPainterPath()
        self.actionGotoDestination.triggered.connect(self.handle_gotoDestination)# path.moveTo(50, 50)

    def hoverEnterEvent(self, event):
        logDbg("Hover entered path")
        newPen = QPen(self.pen().color(), 3)
        self.setPen(newPen)
        self.connection.mainLine.setPen(newPen)
        if self == self.connection.bottomArc:
            self.connection.topArc.setPen(newPen)
        else:
            self.connection.bottomArc.setPen(newPen)

    def hoverLeaveEvent(self, event):
        logDbg("Hover left path")
        newPen = QPen(self.pen().color(), 1)
        self.setPen(newPen)
        self.connection.mainLine.setPen(newPen)
        if self == self.connection.bottomArc:
            self.connection.topArc.setPen(newPen)
        else:
            self.connection.bottomArc.setPen(newPen)

    def contextMenuEvent(self, event):
        self.context_menu.exec(event.screenPos())

    def handle_gotoOrigin(self):
        logDbg(f"handle_gotoOrigin...")
        self.connection.asmTable.scrollToRow(self.connection.originRow)
        pass
    
    def handle_gotoDestination(self):
        logDbg(f"handle_gotoDestination....")
        self.connection.asmTable.scrollToRow(self.connection.destRow)
        pass

class QControlFlowWidget(QWidget):

    connections = []

    def __init__(self, tableView, driver):
        super().__init__()

        # Main layout
        self.thread = None
        self.tableView = tableView
        self.driver = driver
        self.layout = QVBoxLayout(self)

        # Graphics view and scene
        self.scene = QGraphicsScene() # 0, 0, 50, 1260
        self.scene.setSceneRect(0, 0, 80, 1260)
        self.setContentsMargins(0, 0, 0, 0)
        self.view = NoScrollGraphicsView(self.scene)
        # self.view.pos().setY(20)
        self.layout.addWidget(self.view)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.draw_instructions()

    # def loadTextSection(self):
    def isInsideTextSection(self, addr):
        target = self.driver.getTarget()
        process = target.GetProcess()
        self.thread = process.GetThreadAtIndex(0)
        module = self.thread.GetFrameAtIndex(0).GetModule()
        for sec in module.section_iter():
            for idx3 in range(sec.GetNumSubSections()):
                subSec = sec.GetSubSectionAtIndex(idx3)
                if subSec.GetName() == "__text":
                    # sEndAddr = str(hex(subSec.GetFileAddress() + subSec.GetByteSize()))
                    startAddr = subSec.GetFileAddress()
                    endAddr = subSec.GetFileAddress() + subSec.GetByteSize()
                    return endAddr > int(addr, 16) >= startAddr
                # for sym in module.symbol_in_section_iter(subSec):
                #     pass
        pass

    def loadInstructions(self):
        radius = 50
        self.window().txtMultiline.table.verticalScrollBar().setValue(0)
        for row in range(self.window().txtMultiline.table.rowCount()):
            # self.window().txtMultiline.table.rowAt(row).
            if self.window().txtMultiline.table.item(row, 3) is not None and self.window().txtMultiline.table.item(row, 3).text().startswith(("call", "jmp", "jne", "jz", "jnz")):
                if self.isInsideTextSection(self.window().txtMultiline.table.item(row, 4).text()):
                    # logDbg(f"IS INSIDE!!!")
                    logDbg(f"Found instruction with jump @: {self.window().txtMultiline.table.item(row, 2).text()} / isInside: {self.window().txtMultiline.table.item(row, 4).text()}!")
                    rowStart = int(self.window().txtMultiline.table.getRowForAddress(self.window().txtMultiline.table.item(row, 2).text()))
                    rowEnd = int(self.window().txtMultiline.table.getRowForAddress(self.window().txtMultiline.table.item(row, 4).text()))
                    if (rowStart < rowEnd):
                        self.draw_flowConnection(rowStart, rowEnd, QColor("lightblue"), radius)
                    else:
                        self.draw_flowConnection(rowEnd, rowStart, QColor("lightgreen"), radius)
                    radius -= 15
                # else:
                #     # logDbg(f"IS NOOOOOOT INSIDE!!!")
                #     pass

    def draw_flowConnection(self, startRow, endRow, color = QColor("lightblue"), radius = 50, lineWidth = 1, yOffset = 0):
        newConnection = ControlFlowConnection()
        newConnection.originRow = startRow
        newConnection.destRow = endRow
        newConnection.asmTable = self.window().txtMultiline.table
        nSectionsStart = 0
        nSectionsEnd = 0
        for idx in range(self.window().txtMultiline.table.rowCount()):
            height = self.window().txtMultiline.table.verticalHeader().sectionSize(idx)
            print(f"Row height: {height}")
            if height == 30:
                if idx <= startRow:
                    nSectionsStart += 1
                elif idx <= endRow:
                    nSectionsEnd += 1

        # logDbg(f"{newConnection.asmTable.rowAt(startRow)} / {dir(newConnection.asmTable.rowAt(startRow))}")
        # logDbg(f"{newConnection.asmTable.rowAt(endRow)} / {dir(newConnection.asmTable.rowAt(endRow))}")
        y_position = self.window().txtMultiline.table.rowViewportPosition(startRow)
        logDbg(f"y_position Start: {y_position}")

        y_position2 = self.window().txtMultiline.table.rowViewportPosition(endRow)
        logDbg(f"y_position End: {y_position2}")

        nRowHeight = 21
        nOffsetAdd = 23
        # xOffset = 65 + radius + xOffset
        xOffset = controlFlowWidth - (radius / 2)
        # 45
        # line = HoverLineItem(xOffset, 37 + (radius / 2) + ((startRow - 1) * nRowHeight), xOffset, ((endRow + 0) * nRowHeight) + nOffsetAdd + 7 - (nRowHeight / 2) + (yOffset / 2), newConnection)  # 1260)
        line = HoverLineItem(xOffset, y_position + (nRowHeight / 2) + (radius / 2), xOffset, y_position2 + (nRowHeight / 2) - (radius / 2), newConnection)  # 1260)
        line.setPen(QPen(color, lineWidth))
        self.scene.addItem(line)
        # Define the ellipse geometry (x, y, width, height)q
        # ellipse_rect = QRectF(xOffset, 45 + ((startRow + 0) * nRowHeight) + 6 - (nRowHeight / 2), radius, radius)
        ellipse_rect = QRectF(xOffset, y_position + (nRowHeight / 2), radius, radius)

        # Create a painter path and draw a 90° arc
        path = QPainterPath()
        path.arcMoveTo(ellipse_rect, 90)  # Start at 0 degrees
        path.arcTo(ellipse_rect, 90, 90)  # Draw 90-degree arc clockwise

        # Add the path to the scene
        arc_item = HoverPathItem(path, newConnection)
        arc_item.setPen(QPen(color, lineWidth))
        self.scene.addItem(arc_item)
        newConnection.topArc = arc_item

        # ellipse_rect2 = QRectF(xOffset, ((endRow + 0) * nRowHeight) + 6 - (nRowHeight / 2) + (yOffset), radius, radius)
        ellipse_rect2 = QRectF(xOffset, y_position2 + (nRowHeight / 2) - (radius), radius, radius) # y_position2 - (nRowHeight * (nSectionsStart)) - ((nSectionsEnd) * 2.5), radius, radius)
        # Create a painter path and draw a 90° arc
        path2 = QPainterPath()
        path2.arcMoveTo(ellipse_rect2, 180)  # Start at 0 degrees
        path2.arcTo(ellipse_rect2, 180, 90)  # Draw 90-degree arc clockwise

        # Add the path to the scene
        arc_item2 = HoverPathItem(path2, newConnection)
        arc_item2.setPen(QPen(color, lineWidth))
        # arc_item2.hoverMoveEvent().connect(self.handle_hoverMoveEvent)
        self.scene.addItem(arc_item2)
        newConnection.bottomArc = arc_item2

        arrowEnd = ellipse_rect.topLeft() #+ QPointF(radius / 2, -(radius + 6))
        arrowStart = ellipse_rect.topRight()
        # self.draw_arrowNG(ellipse_rect.bottomLeft(), ellipse_rect2.topLeft())
        self.draw_arrowNG(arrowStart, arrowEnd)

        self.connections.append(newConnection)
        # self.draw_arrow(QPointF(ellipse_rect.topLeft(), ellipse_rect.bottomLeft()), QPointF(ellipse_rect.topLeft(), ellipse_rect.bottomLeft()))
        return newConnection

    # def handle_hoverMoveEvent(self, event):
    #     print(f"Mouse HOVER line!!!")
    #     pass
    # def draw_instructions(self, instructions):
    def draw_instructions(self):
        start = QPointF(75, 0)
        end = QPointF(75, 0)

        # line = QGraphicsLineItem(start.x() + 20, start.y(), end.x() + 20, end.y())
        # line.setPen(QPen(QColor("red"), 2))
        # self.scene.addItem(line)

        line1 = QGraphicsLineItem(start.x() + 20, 0, end.x() + 20, 1260)
        line1.setPen(QPen(QColor("transparent"), 0))
        self.scene.addItem(line1)
    
    def draw_arrowNG(self, fromPos, toPos):
        # # Add arrowhead
        arrow_size = 12
        direction = (toPos - fromPos)
        direction /= (direction.manhattanLength() or 1)
        perp = QPointF(-direction.y(), direction.x())
        p1 = toPos - direction * arrow_size + perp * arrow_size / 2
        p2 = toPos - direction * arrow_size - perp * arrow_size / 2
        
        # # Your list of points
        points = [toPos, p1, p2]
        # # Convert to QPolygonF
        polygon = QPolygonF(points)

        arrow_head = self.scene.addPolygon(
            # [end, p1, p2],
            polygon,
            QPen(QColor("red")),
            QBrush(QColor("transparent"))
        )
