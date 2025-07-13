# from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
# from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty, QTimer
# from PyQt6.QtGui import QPixmap, QPainter, QTransform

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

class SpinnerOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setGeometry(parent.geometry())

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.spinner = QLabel(self)
        self.spinner.setPixmap(QPixmap("spinner.png"))  # Use your spinner image
        layout.addWidget(self.spinner)

        self._angle = 0
        self.animation = QPropertyAnimation(self, b"angle")
        self.animation.setStartValue(0)
        self.animation.setEndValue(360)
        self.animation.setDuration(1000)
        self.animation.setLoopCount(-1)
        self.animation.start()

    @pyqtProperty(int)
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self.spinner)
        transform = QTransform().rotate(self._angle)
        rotated = self.spinner.pixmap().transformed(transform)
        painter.drawPixmap(0, 0, rotated)
