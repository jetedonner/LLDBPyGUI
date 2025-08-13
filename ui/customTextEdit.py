import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QTextEdit, QLabel, QVBoxLayout)
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QGraphicsOpacityEffect

from config import ConfigClass


class CustomTextEdit(QTextEdit):
    """
    A QTextEdit widget with a custom hoverable, clickable image in the corner.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Type your text here...")

        # Create the QLabel for the image
        self.image_label = QLabel(self)

        # Load the image (use a real image path or create one)
        # pixmap = QPixmap(64, 64)
        # pixmap.fill(Qt.GlobalColor.green)  # Using a green square for demonstration
        # self.image_label.setPixmap(pixmap.scaled(QSize(24, 24), Qt.AspectRatioMode.KeepAspectRatio,
        #                                          Qt.TransformationMode.SmoothTransformation))

        pixmap = ConfigClass.pixSearch
        # pixmap.fill(Qt.GlobalColor.green)  # Using a green square for demonstration
        self.image_label.setPixmap(pixmap.scaled(QSize(24, 24), Qt.AspectRatioMode.KeepAspectRatio,
                                                 Qt.TransformationMode.SmoothTransformation))

        self.image_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Set the initial opacity
        self.opacity_effect = QGraphicsOpacityEffect(self.image_label)
        self.opacity_effect.setOpacity(0.75)
        self.image_label.setGraphicsEffect(self.opacity_effect)

        # Connect mouse events
        self.image_label.mousePressEvent = self.on_image_clicked
        self.image_label.enterEvent = self.on_image_hover_enter
        self.image_label.leaveEvent = self.on_image_hover_leave

        # Initially position the label
        self.update_image_position()

    def resizeEvent(self, event):
        """
        Overrides resizeEvent to reposition the image when the widget resizes.
        """
        super().resizeEvent(event)
        self.update_image_position()

    def update_image_position(self):
        """
        Positions the image_label in the top-right corner of the QTextEdit.
        """
        label_size = self.image_label.size()
        text_edit_width = self.width()
        padding = 5  # Adjust padding as needed

        # Calculate new position
        x = text_edit_width - label_size.width() - padding
        y = padding

        self.image_label.move(x, y)

    def on_image_clicked(self, event):
        """
        This method is called when the user clicks the image.
        """
        print("Image clicked! Executing an action...")
        # Add your custom action here, e.g., show a dialog, trigger a function, etc.
        # Example: show a simple message box
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Image Clicked", "You clicked the image!")

    def on_image_hover_enter(self, event):
        """
        This method is called when the mouse enters the image area.
        """
        self.opacity_effect.setOpacity(1.0)

    def on_image_hover_leave(self, event):
        """
        This method is called when the mouse leaves the image area.
        """
        self.opacity_effect.setOpacity(0.75)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = QWidget()
#     layout = QVBoxLayout(window)
#
#     text_edit = CustomTextEdit()
#
#     layout.addWidget(text_edit)
#     window.setWindowTitle("Custom QTextEdit with Image")
#     window.show()
#     sys.exit(app.exec())