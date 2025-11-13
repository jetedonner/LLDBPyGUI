from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QLineEdit


class QHexLineEdit(QLineEdit):

	def __init__(self, parent=None):
		super().__init__(parent)

		self.hex_validator = QRegularExpressionValidator(QRegularExpression("^0x[0-9a-fA-F]*$"))  # QRegularExpression("^[0-9a-fA-F]*$"))
		self.setValidator(self.hex_validator)