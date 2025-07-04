from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsLineItem, QGraphicsEllipseItem, QTableWidget, QTableWidgetItem, QSizePolicy, QGraphicsPathItem
)
from PyQt6.QtGui import QBrush, QPen, QColor, QTransform, QPainterPath
from PyQt6.QtCore import Qt, QPointF

from PyQt6.QtGui import QPainter
from PyQt6.QtCore import QPointF, QRectF

class QControlFlowWidget(QWidget):
    def __init__(self, tableView):
        super().__init__()
        # self.setWindowTitle("Control Flow Visualizer")

        # Main layout
        # central_widget = QWidget()
        self.tableView = tableView
        self.layout = QVBoxLayout(self)
        # self.setCentralWidget(central_widget)

        # # Table for disassembled code
        # self.table = QTableWidget(3, 2)
        # self.table.setHorizontalHeaderLabels(["Address", "Instruction"])
        # self.table.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        # self.table.setColumnWidth(0, 80)
        # self.table.setColumnWidth(1, 200)
        #
        # instructions = [
        #     ("0x1000", "MOV AX, BX"),
        #     ("0x1002", "CALL 0x2000"),
        #     ("0x1005", "JMP 0x1000"),
        #     ("0x4000", "RET"),
        # ]
        # for row, (addr, instr) in enumerate(instructions):
        #     self.table.setItem(row, 0, QTableWidgetItem(addr))
        #     self.table.setItem(row, 1, QTableWidgetItem(instr))

        # Graphics view and scene
        self.scene = QGraphicsScene()
        self.setContentsMargins(0, 0, 0, 0)
        self.view = QGraphicsView(self.scene)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setStyleSheet("background-color: #393939; border: 1px solid darkgray;")
        # self.view.setStyleSheet("background-color: transparent; border: none;")
        self.view.setContentsMargins(0, 0, 0, 0)
        # self.view.setRenderHint(self.view.RenderHint.Antialiasing)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        # self.view.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        # self.layout.addWidget(self.table)
        self.layout.addWidget(self.view)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # self.draw_instructions(instructions)
        self.draw_instructions()

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

        self.nodes = {}
        y = 0

        for idx in range(self.tableView.table.rowCount()):
            rect = QGraphicsRectItem(20, y, 150, 40)
            # rect.setBrush(QBrush(QColor("#c5e1a5")))
            # self.scene.addItem(rect)
            #
            # label = QGraphicsTextItem(f"{addr}\n{text}")
            # label.setDefaultTextColor(QColor("red"))
            # label.setPos(5, y + 5)
            # self.scene.addItem(label)

            self.nodes[idx] = rect
            y += 80

        # # Draw arrows
        # self.draw_arrow("0x1002", "0x4000")  # Will be skipped if target not found
        # self.draw_arrow("0x1005", "0x1000")

        # # Create the ellipse item
        # ellipse_rect = QRectF(115, 50, 50, 50)
        # ellipse_item = QGraphicsEllipseItem(ellipse_rect)
        #
        # # Customize appearance
        # # ellipse_item.setBrush(QBrush(QColor("skyblue")))  # Fill color
        # ellipse_item.setPen(QPen(QColor("red"), 3))  # Border color and thickness
        # ellipse_item.setSpanAngle(1440)
        # ellipse_item.setStartAngle(1440)
        # # Add the ellipse to the scene
        # self.scene.addItem(ellipse_item)

        # Define the ellipse geometry (x, y, width, height)
        ellipse_rect = QRectF(115, 45, 50, 50)
        # Create a painter path and draw a 90° arc
        path = QPainterPath()
        path.arcMoveTo(ellipse_rect, 90)  # Start at 0 degrees
        path.arcTo(ellipse_rect, 90, 90)  # Draw 90-degree arc clockwise

        # Add the path to the scene
        arc_item = QGraphicsPathItem(path)
        arc_item.setPen(QPen(QColor("red"), 2))
        self.scene.addItem(arc_item)

        ellipse_rect2 = QRectF(115, 250, 50, 50)
        # Create a painter path and draw a 90° arc
        path2 = QPainterPath()
        path2.arcMoveTo(ellipse_rect2, 180)  # Start at 0 degrees
        path2.arcTo(ellipse_rect2, 180, 90)  # Draw 90-degree arc clockwise

        # Add the path to the scene
        arc_item2 = QGraphicsPathItem(path2)
        arc_item2.setPen(QPen(QColor("red"), 2))
        self.scene.addItem(arc_item2)

    def draw_arrow(self, from_addr, to_addr):
        # if from_addr not in self.nodes or to_addr not in self.nodes:
        #     return

        start = self.nodes[from_addr].sceneBoundingRect().bottomLeft() + QPointF(75, 0)
        end = self.nodes[to_addr].sceneBoundingRect().topLeft() + QPointF(75, 0)

        # line = QGraphicsLineItem(start.x() + 20, start.y(), end.x() + 20, end.y())
        # line.setPen(QPen(QColor("red"), 2))
        # self.scene.addItem(line)

        line1 = QGraphicsLineItem(start.x() + 20, 0, end.x() + 20, 1260)
        line1.setPen(QPen(QColor("transparent"), 0))
        self.scene.addItem(line1)

        line2 = QGraphicsLineItem(start.x() + 20, 70, end.x() + 20, 275) # 1260)
        line2.setPen(QPen(QColor("red"), 2))
        self.scene.addItem(line2)

        # # Add arrowhead
        # arrow_size = 6
        # direction = (end - start)
        # direction /= (direction.manhattanLength() or 1)
        # perp = QPointF(-direction.y(), direction.x())
        # p1 = end - direction * arrow_size + perp * arrow_size / 2
        # p2 = end - direction * arrow_size - perp * arrow_size / 2
        #
        # # from PyQt6.QtGui import QPolygonF
        # # from PyQt6.QtCore import QPointF
        # #
        # # # Your list of points
        # points = [end, p1, p2]
        # #
        # # # Convert to QPolygonF
        # polygon = QPolygonF(points)
        #
        # # Now add it to the scene
        # # scene.addPolygon(polygon, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.red))
        #
        #
        # arrow_head = self.scene.addPolygon(
        #     # [end, p1, p2],
        #     polygon,
        #     QPen(QColor("red")),
        #     QBrush(QColor("red"))
        # )

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = ControlFlowVisualizer()
#     window.resize(600, 400)
#     window.show()
#     sys.exit(app.exec())

