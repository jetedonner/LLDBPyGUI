import lldb
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from lib.settings import SettingsHelper, SettingsValues


class Arm64InstructionReferenceWidget(QWidget):

	def __init__(self):
		super().__init__()

		# self.driver = driver
		self.setContentsMargins(0, 0, 0, 0)
		self.setLayout(QVBoxLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)

		self.web_view = QWebEngineView()
		self.web_view.load(QUrl(SettingsHelper().getValue(SettingsValues.URLARM64InstRef)))

		self.layout().addWidget(self.web_view)
