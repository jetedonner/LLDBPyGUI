from PyQt6.QtCore import QMimeData
from PyQt6.QtWidgets import QTextEdit


class CleanPasteTextEdit(QTextEdit):
	def insertFromMimeData(self, source: QMimeData):
		if source.hasText():
			# Insert plain text only, stripping rich formatting
			self.insertPlainText(source.text())
		else:
			# Fallback to default behavior
			super().insertFromMimeData(source)
