from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from ui.fileinfo.fileInfoTableWidget import FileInfosTableWidget
from ui.fileinfo.fileStructureTreeView import FileStructureWidget
from ui.fileinfo.signatureTreeWidget import SignatureTreeWidget
from ui.fileinfo.statisticsTreeWidget import StatisticsTreeWidget


class FileInfosTabWidget(QWidget):
	driver = None

	def __init__(self, driver):
		super().__init__()
		self.driver = driver

		self.initTabWidget()

	def initTabWidget(self):
		self.tblFileInfos = FileInfosTableWidget()
		self.setLayout(QVBoxLayout())

		self.tabWidgetFileInfo = QTabWidget()

		self.tabWidgetFileInfo.addTab(self.tblFileInfos, "Header")
		self.layout().addWidget(self.tabWidgetFileInfo)

		self.tabWidgetStruct = FileStructureWidget(self.driver)
		self.tabWidgetStruct.setContentsMargins(0, 0, 0, 0)
		self.tabWidgetFileInfo.addTab(self.tabWidgetStruct, "Structure")

		self.treSignature = SignatureTreeWidget(self.driver)
		self.tabWidgetFileInfo.addTab(self.treSignature, "Signature / Load Commands")

		# self.layout().addWidget(self.tabWidgetFileInfo)

		self.treStats = StatisticsTreeWidget(self.driver)
		self.tabWidgetFileInfo.addTab(self.treStats, "Statistics")

	def resetContent(self):
		self.tblFileInfos.resetContent()
		self.tabWidgetStruct.resetContent()
		self.treStats.clear()
		self.treSignature.clear()
