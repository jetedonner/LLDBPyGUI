from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QListView, QApplication


class BaseListView(QListView):

	def __init__(self):
		super().__init__()

	def mousePressEvent(self, event: QMouseEvent):
		index = self.indexAt(event.pos())
		modifiers = event.modifiers()
		if index.isValid() and modifiers & Qt.KeyboardModifier.ShiftModifier:
			# if index.isValid() and event.modifiers():
			item_text = self.model().data(index, Qt.ItemDataRole.DisplayRole)
			print(f"Clicked item text: {item_text}")
			QApplication.clipboard().setText(item_text)
			self.window().updateStatusBar(f"Copied '{item_text}' to clipboard ...")
		super().mousePressEvent(event)
