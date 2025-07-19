from PyQt6.QtWidgets import QWidget, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer, QRect
from PyQt6.QtGui import QPalette, QColor

from ui.helper.dbgOutputHelper import get_main_window, logDbgC


class Notification(QWidget):
    def __init__(self, parent, message, duration=3000):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedHeight(50)

        # Style and message
        self.label = QLabel(message, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("background-color: #ff6e63; color: white; padding: 10px; border-radius: 5px;")
        self.label.setGeometry(0, 0, parent.width(), 50)

        # Position off-screen initially
        self.setGeometry(0, 0, parent.width(), 50)

        # Animate drop-in
        # self.anim_in = QPropertyAnimation(self, b"geometry")
        # self.anim_in.setDuration(500)
        # self.anim_in.setStartValue(QRect(0, -50, parent.width(), 50))
        mainWin = get_main_window()
        if mainWin is not None:
            logDbgC(f"mainWin.height(): {mainWin.height()}")
            # self.anim_in.setEndValue(QRect(0, get_main_window().height() / 2, parent.width(), 50))
            self.setGeometry(QRect((get_main_window().width() / 2) - (parent.width() / 2), get_main_window().height() / 2, (get_main_window().width() / 2) + (parent.width() / 2), get_main_window().height() / 2))

        # self.setGeometry(0, -50, parent.width(), 50)
        # else:
        #     # self.anim_in.setEndValue(QRect(0, 0a, parent.width(), 50))
        #     self.setGeometry(QRect(0, (get_main_window().width() / 2) + (parent.width() / 2), parent.width(), 50))
            # self.
        # self.anim_in.start()
        # self.opacity_effect = QGraphicsOpacityEffect()
        # self.setGraphicsEffect(self.opacity_effect)
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        animation = QPropertyAnimation(self.effect, b"opacity")
        animation.setDuration(1000)  # Duration in milliseconds
        animation.setStartValue(0.0)  # Fully visible
        animation.setEndValue(1.0)  # Fully transparent
        animation.start()
        #
        # # Timer to fade out
        QTimer.singleShot(duration, self.fade_out)
        self.show()

    def fade_out(self):
        # self.anim_out = QPropertyAnimation(self, b"geometry")
        # self.anim_out.setDuration(500)
        # self.anim_out.setStartValue(QRect(0, 0, self.width(), 50))
        # self.anim_out.setEndValue(QRect(0, -50, self.width(), 50))
        # self.anim_out.finished.connect(self.close)
        # self.anim_out.start()
        animation = QPropertyAnimation(self.effect, b"opacity")
        animation.setDuration(1000)  # Duration in milliseconds
        animation.setStartValue(1.0)  # Fully visible
        animation.setEndValue(0.0)  # Fully transparent
        animation.start()

