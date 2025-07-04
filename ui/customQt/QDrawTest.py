import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsLineItem, QTableWidget, QTableWidgetItem, QSizePolicy
)
from PyQt6.QtGui import QBrush, QPen, QColor, QTransform
from PyQt6.QtCore import Qt, QPointF

from PyQt6.QtGui import QPainter

from PyQt6.QtGui import QPolygonF
from PyQt6.QtCore import QPointF


class ControlFlowVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Flow Visualizer")

        # Main layout
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Table for disassembled code
        self.table = QTableWidget(3, 2)
        self.table.setHorizontalHeaderLabels(["Address", "Instruction"])
        self.table.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(1, 200)

        instructions = [
            ("0x1000", "MOV AX, BX"),
            ("0x1002", "CALL 0x2000"),
            ("0x1005", "JMP 0x1000"),
        ]
        for row, (addr, instr) in enumerate(instructions):
            self.table.setItem(row, 0, QTableWidgetItem(addr))
            self.table.setItem(row, 1, QTableWidgetItem(instr))

        # Graphics view and scene
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        # self.view.setRenderHint(self.view.RenderHint.Antialiasing)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        # self.view.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        layout.addWidget(self.table)
        layout.addWidget(self.view)

        self.draw_instructions(instructions)

    def draw_instructions(self, instructions):
        self.nodes = {}
        y = 0

        for addr, text in instructions:
            rect = QGraphicsRectItem(0, y, 150, 40)
            rect.setBrush(QBrush(QColor("#c5e1a5")))
            self.scene.addItem(rect)

            label = QGraphicsTextItem(f"{addr}\n{text}")
            label.setPos(5, y + 5)
            self.scene.addItem(label)

            self.nodes[addr] = rect
            y += 80

        # Draw arrows
        self.draw_arrow("0x1002", "0x2000")  # Will be skipped if target not found
        self.draw_arrow("0x1005", "0x1000")

    def draw_arrow(self, from_addr, to_addr):
        if from_addr not in self.nodes or to_addr not in self.nodes:
            return

        start = self.nodes[from_addr].sceneBoundingRect().bottomLeft() + QPointF(75, 0)
        end = self.nodes[to_addr].sceneBoundingRect().topLeft() + QPointF(75, 0)

        line = QGraphicsLineItem(start.x(), start.y(), end.x(), end.y())
        line.setPen(QPen(QColor("black"), 2))
        self.scene.addItem(line)

        # Add arrowhead
        arrow_size = 6
        direction = (end - start)
        direction /= (direction.manhattanLength() or 1)
        perp = QPointF(-direction.y(), direction.x())
        p1 = end - direction * arrow_size + perp * arrow_size / 2
        p2 = end - direction * arrow_size - perp * arrow_size / 2

        # from PyQt6.QtGui import QPolygonF
        # from PyQt6.QtCore import QPointF
        #
        # # Your list of points
        points = [end, p1, p2]
        #
        # # Convert to QPolygonF
        polygon = QPolygonF(points)

        # Now add it to the scene
        # scene.addPolygon(polygon, QPen(Qt.GlobalColor.black), QBrush(Qt.GlobalColor.red))


        arrow_head = self.scene.addPolygon(
            # [end, p1, p2],
            polygon,
            QPen(QColor("black")),
            QBrush(QColor("black"))
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ControlFlowVisualizer()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())
