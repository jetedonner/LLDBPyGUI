from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsLineItem, QGraphicsEllipseItem, QTableWidget, QTableWidgetItem, QSizePolicy, QGraphicsPathItem, QMenu
)
from PyQt6.QtGui import QBrush, QPen, QColor, QTransform, QPainterPath, QPolygonF
from PyQt6.QtCore import Qt, QPointF, QLineF

from PyQt6.QtGui import QPainter
from PyQt6.QtCore import QPointF, QRectF

# import sys
# from PyQt6.QtWidgets import (
#     QApplication, QGraphicsScene, QGraphicsView, QGraphicsPathItem
# )
# from PyQt6.QtGui import QPainterPath, QPen, QColor
# from PyQt6.QtCore import Qt, QRectF

# from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtGui import QWheelEvent, QKeyEvent
from ui.helper.dbgOutputHelper import *

class ControlFlowConnection():

    asmTable = None
    originRow = 0
    destRow = 0
    
    mainLine = None
    topArc = None
    bottomArc = None
    
    def __init__(self):
        super().__init__()

from PyQt6.QtWidgets import QScrollBar

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

        self.setSceneRect(scene.itemsBoundingRect())  # Lock scene bounds
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        # self.view.verticalScrollBar().valueChanged.connect(self.on_scroll)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("background-color: #393939; border: 1px solid darkgray;")
        # self.view.setStyleSheet("background-color: transparent; border: none;")
        self.setContentsMargins(0, 0, 0, 0)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        # self.view.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        # self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        # scene.setSceneRect(0, 0, 50, 1260)  # Or whatever size you need


    def wheelEvent(self, event: QWheelEvent):
        pass  # Ignore mouse wheel

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)  # Optional: allow other keys

    # def resizeEvent(self, event):
    #     # Skip any scaling logic
    #     super().resizeEvent(event)
    #     # Optionally keep the center fixed
    #     # self.centerOn(self.scene().itemsBoundingRect().center())
    #     # self.resetTransform()
    #     # self.repaint()

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
        # path.cubicTo(150, 0, 250, 100, 350, 50)
        # self.setPath(path)
        #
        # # Default appearance
        # self.setPen(QPen(QColor("black"), 4))

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

    def __init__(self, tableView):
        super().__init__()

        # Main layout
        self.tableView = tableView
        self.layout = QVBoxLayout(self)

        # Graphics view and scene
        self.scene = QGraphicsScene() # 0, 0, 50, 1260
        self.setContentsMargins(0, 0, 0, 0)
        self.view = NoScrollGraphicsView(self.scene)
        # self.view.pos().setY(20)
        self.layout.addWidget(self.view)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.draw_instructions()

    # def on_scroll(self, value):
    #     print(f"Flow Control Scrolled to position: {value}")
    #     # self.window().txtMultiline.disableScroll = True
    #     # self.window().txtMultiline.scroll(0, value + 150)
    #     # self.window().txtMultiline.disableScroll = False

    def draw_flowConnection(self, startRow, endRow, color = QColor("lightblue"), xOffset = 0, radius = 50, lineWidth = 1, yOffset = 0):
        newConnection = ControlFlowConnection()
        newConnection.originRow = startRow
        newConnection.destRow = endRow
        newConnection.asmTable = self.window().txtMultiline.table
        
        nRowHeight = 21
        nOffsetAdd = 23
        xOffset = 65 + radius + xOffset
        # 45
        line = HoverLineItem(xOffset, 45 + ((startRow + 0) * nRowHeight) + 6 + nOffsetAdd - (nRowHeight / 2) - (yOffset / 2), xOffset, ((endRow + 0) * nRowHeight) + nOffsetAdd + 7 - (nRowHeight / 2) + (yOffset / 2), newConnection)  # 1260)
        line.setPen(QPen(color, lineWidth))
        self.scene.addItem(line)

        # Define the ellipse geometry (x, y, width, height)q
        ellipse_rect = QRectF(xOffset, 45 + ((startRow + 0) * nRowHeight) + 6 - (nRowHeight / 2), radius, radius)
        # Create a painter path and draw a 90° arc
        path = QPainterPath()
        path.arcMoveTo(ellipse_rect, 90)  # Start at 0 degrees
        path.arcTo(ellipse_rect, 90, 90)  # Draw 90-degree arc clockwise

        # Add the path to the scene
        arc_item = HoverPathItem(path, newConnection)
        arc_item.setPen(QPen(color, lineWidth))
        self.scene.addItem(arc_item)
        newConnection.topArc = arc_item

        ellipse_rect2 = QRectF(xOffset, ((endRow + 0) * nRowHeight) + 6 - (nRowHeight / 2) + (yOffset), radius, radius)
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

        arrowEnd = ellipse_rect.bottomLeft() + QPointF(radius / 2, -(radius + 6))
        arrowStart = ellipse_rect.bottomLeft()
        # self.draw_arrowNG(ellipse_rect.bottomLeft(), ellipse_rect2.topLeft())
        self.draw_arrowNG(arrowStart, arrowEnd)

        self.connections.append(newConnection)
        # self.draw_arrow(QPointF(ellipse_rect.topLeft(), ellipse_rect.bottomLeft()), QPointF(ellipse_rect.topLeft(), ellipse_rect.bottomLeft()))
        pass

    def handle_hoverMoveEvent(self, event):
        print(f"Mouse HOVER line!!!")
        pass
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

        # line2 = QGraphicsLineItem(115, 45 + 23, 115, 250 + 23)  # 1260)
        # line2.setPen(QPen(QColor("red"), 2))
        # self.scene.addItem(line2)
        #
        # self.nodes = {}
        # y = 0
        #
        # for idx in range(self.tableView.table.rowCount()):
        #     rect = QGraphicsRectItem(20, y, 150, 40)
        #     # rect.setBrush(QBrush(QColor("#c5e1a5")))
        #     # self.scene.addItem(rect)
        #     #
        #     # label = QGraphicsTextItem(f"{addr}\n{text}")
        #     # label.setDefaultTextColor(QColor("red"))
        #     # label.setPos(5, y + 5)
        #     # self.scene.addItem(label)
        #
        #     self.nodes[idx] = rect
        #     y += 80
        #
        # # # Draw arrows
        # # self.draw_arrow("0x1002", "0x4000")  # Will be skipped if target not found
        # # self.draw_arrow("0x1005", "0x1000")
        #
        # # # Create the ellipse item
        # # ellipse_rect = QRectF(115, 50, 50, 50)
        # # ellipse_item = QGraphicsEllipseItem(ellipse_rect)
        # #
        # # # Customize appearance
        # # # ellipse_item.setBrush(QBrush(QColor("skyblue")))  # Fill color
        # # ellipse_item.setPen(QPen(QColor("red"), 3))  # Border color and thickness
        # # ellipse_item.setSpanAngle(1440)
        # # ellipse_item.setStartAngle(1440)
        # # # Add the ellipse to the scene
        # # self.scene.addItem(ellipse_item)
        #
        # # Define the ellipse geometry (x, y, width, height)
        # ellipse_rect = QRectF(115, 45, 50, 50)
        # # Create a painter path and draw a 90° arc
        # path = QPainterPath()
        # path.arcMoveTo(ellipse_rect, 90)  # Start at 0 degrees
        # path.arcTo(ellipse_rect, 90, 90)  # Draw 90-degree arc clockwise
        #
        # # Add the path to the scene
        # arc_item = QGraphicsPathItem(path)
        # arc_item.setPen(QPen(QColor("red"), 2))
        # self.scene.addItem(arc_item)
        #
        # ellipse_rect2 = QRectF(115, 250, 50, 50)
        # # Create a painter path and draw a 90° arc
        # path2 = QPainterPath()
        # path2.arcMoveTo(ellipse_rect2, 180)  # Start at 0 degrees
        # path2.arcTo(ellipse_rect2, 180, 90)  # Draw 90-degree arc clockwise
        #
        # # Add the path to the scene
        # arc_item2 = QGraphicsPathItem(path2)
        # arc_item2.setPen(QPen(QColor("red"), 2))
        # self.scene.addItem(arc_item2)

    # def draw_arrow(self, fromPos, toPos):
    # # def draw_arrow(self, from_addr, to_addr):
    # #     # if from_addr not in self.nodes or to_addr not in self.nodes:
    # #     #     return
    # #
    # #     start = self.nodes[from_addr].sceneBoundingRect().bottomLeft() + QPointF(75, 0)
    # #     end = self.nodes[to_addr].sceneBoundingRect().topLeft() + QPointF(75, 0)
    #
    #     # line = QGraphicsLineItem(start.x() + 20, start.y(), end.x() + 20, end.y())
    #     # line.setPen(QPen(QColor("red"), 2))
    #     # self.scene.addItem(line)
    #
    #     # line1 = QGraphicsLineItem(fromPos + 20, 0, toPos + 20, 1260)
    #     # line1.setPen(QPen(QColor("transparent"), 0))
    #     # self.scene.addItem(line1)
    #     #
    #     # line2 = QGraphicsLineItem(fromPos + 20, 70, toPos + 20, 275) # 1260)
    #     # line2.setPen(QPen(QColor("red"), 2))
    #     # self.scene.addItem(line2)
    #
    #     # # Add arrowhead
    #     arrow_size = 6
    #     direction = (toPos - fromPos)
    #     direction /= (direction.manhattanLength() or 1)
    #     perp = QPointF(-direction.y(), direction.x())
    #     p1 = toPos - direction * arrow_size + perp * arrow_size / 2
    #     p2 = toPos - direction * arrow_size - perp * arrow_size / 2
    #
    #     # from PyQt6.QtGui import QPolygonF
    #     # from PyQt6.QtCore import QPointF
    #     #
    #     # # Your list of points
    #     points = [toPos, p1, p2]
    #     #
    #     # # Convert to QPolygonF
    #     polygon = QPolygonF(points)
    #
    #     # Now add it to the scene
    #     # scene.addPolygon(polygon, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.red))
    #
    #
    #     arrow_head = self.scene.addPolygon(
    #         # [end, p1, p2],
    #         polygon,
    #         QPen(QColor("red")),
    #         QBrush(QColor("red"))
    #     )

    
    def draw_arrowNG(self, fromPos, toPos):
        # def draw_arrow(self, from_addr, to_addr):
        #     # if from_addr not in self.nodes or to_addr not in self.nodes:
        #     #     return
        #
        #     start = self.nodes[from_addr].sceneBoundingRect().bottomLeft() + QPointF(75, 0)
        #     end = self.nodes[to_addr].sceneBoundingRect().topLeft() + QPointF(75, 0)

        # # Add arrowhead
        arrow_size = 12
        direction = (toPos - fromPos)
        direction /= (direction.manhattanLength() or 1)
        perp = QPointF(-direction.y(), direction.x())
        p1 = toPos - direction * arrow_size + perp * arrow_size / 2
        p2 = toPos - direction * arrow_size - perp * arrow_size / 2

        # from PyQt6.QtGui import QPolygonF
        # from PyQt6.QtCore import QPointF
        #
        # # Your list of points
        points = [toPos, p1, p2]
        #
        # # Convert to QPolygonF
        polygon = QPolygonF(points)

        # Now add it to the scene
        # scene.addPolygon(polygon, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.red))


        arrow_head = self.scene.addPolygon(
            # [end, p1, p2],
            polygon,
            QPen(QColor("red")),
            QBrush(QColor("red"))
        )
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = ControlFlowVisualizer()
#     window.resize(600, 400)
#     window.show()
#     sys.exit(app.exec())

