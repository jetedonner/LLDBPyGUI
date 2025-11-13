from PyQt6.QtCore import QObject


class StylesheetHelper(QObject):
	mainWindow = None

	def __init__(self, mainWindow):
		super().__init__()
		self.mainWindow = mainWindow

		qss = self.load_stylesheet("resources/styles/mainstyle.qss")
		self.mainWindow.setStyleSheet(qss)

	def load_stylesheet(self, path):
		try:
			with open(path, "r") as f:
				return f.read()
		except Exception as e:
			print(f"❌ Failed to load stylesheet: {e}")
			return ""
