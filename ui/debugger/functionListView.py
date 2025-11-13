from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QSize, QRect, QModelIndex
from PyQt6.QtGui import (
	QStandardItemModel, QStandardItem, QPixmap, QPainter, QMouseEvent, QFontMetrics
)
from PyQt6.QtWidgets import (
	QListView, QWidget, QVBoxLayout, QSizePolicy, QAbstractItemView, QToolBox, QFrame, QMenu
)
from PyQt6.QtWidgets import QStyledItemDelegate

from config import ConfigClass
from helper.debugHelper import logDbgC
from ui.base.baseListView import BaseListView


class FunctionsListViewWidget(QWidget):
	driver = None

	def __init__(self, driver):
		super().__init__()

		self.driver = driver

		self.setContentsMargins(0, 0, 0, 0)
		# self.lblTitle = QLabel("Symbols:")
		# self.lblTitle.setContentsMargins(0, 0, 0, 0)
		self.setLayout(QVBoxLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)
		# self.layout().addWidget(self.lblTitle)
		# self.splitterFuncMain = QSplitter(Qt.Orientation.Vertical)
		# self.splitterFuncMain.setContentsMargins(0, 0, 0, 0)
		self.tbMain = QToolBox()
		self.tbMain.setContentsMargins(0, 0, 0, 0)
		self.lstFunctions = FunctionsListView(self.driver)
		self.setMaximumWidth(320)
		self.lstFunctions.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
		self.lstFunctions.setContentsMargins(0, 0, 0, 0)
		# self.splitterFuncMain.addWidget(self.lstFunctions)
		self.tbMain.addItem(self.lstFunctions, "Symbols")
		self.lstFunctions.setFont(ConfigClass.font)

		self.lstStrings = FunctionsListView(self.driver)
		# self.setMaximumWidth(320)
		self.lstStrings.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		# self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
		self.lstStrings.setContentsMargins(0, 0, 0, 0)
		# self.splitterFuncMain.addWidget(self.lstActions)
		self.tbMain.addItem(self.lstStrings, "Strings")
		# self.layout().addWidget(self.tbMain)
		self.lstStrings.setFont(ConfigClass.font)

		self.lstActions = FunctionsListView(self.driver)
		# self.setMaximumWidth(320)
		self.lstActions.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		# self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
		self.lstActions.setContentsMargins(0, 0, 0, 0)
		# self.splitterFuncMain.addWidget(self.lstActions)
		self.tbMain.addItem(self.lstActions, "Actions")
		self.layout().addWidget(self.tbMain)
		self.lstActions.setFont(ConfigClass.font)

	def addSymbol(self, symbolName, row):
		self.lstFunctions.add_item(symbolName, row, ConfigClass.pixFunction)

	def addAction(self, actionName, row):
		self.lstActions.add_item(actionName, row)

	def addString(self, string, row):
		self.lstStrings.add_item(string, row, ConfigClass.pixString)

	def resetContent(self):
		self.lstFunctions.resetContent()
		self.lstActions.resetContent()
		# self.lstStrings.resetContent()
		logDbgC(f"self.lstStrings.resetContent() ...")


class RightAlignedDelegate(QStyledItemDelegate):

	# def sizeHint(self, option, index):
	#     return QSize(320, 20)  # Width, Height

	# def __init__(self, parent, QObject=None, *args, **kwargs): # real signature unknown; NOTE: unreliably restored from __doc__
	#     super(QStyledItemDelegate, self).__init__(parent, None, *args, **kwargs)
	#     pass

	def initStyleOption(self, option, index):
		super(RightAlignedDelegate, self).initStyleOption(option, index)

		# option.backgroundBrush = QBrush(QColor(SettingsHelper().getValue(SettingsValues.SelectedRowColor)))

	# class WidthBasedDelegate(QStyledItemDelegate):
	def sizeHint(self, option, index):
		text = index.data()
		font_metrics = QFontMetrics(ConfigClass.font12)  # option.font)
		width = font_metrics.horizontalAdvance(text)
		height = 20  # font_metrics.height()
		return QSize(width, height)

	def paint(self, painter: QPainter, option, index: QModelIndex):
		painter.save()

		painter.setFont(ConfigClass.font12)
		# Get data
		icon = index.data(Qt.ItemDataRole.DecorationRole)
		text = index.data(Qt.ItemDataRole.DisplayRole)
		row = int(index.data(Qt.ItemDataRole.UserRole))

		# Icon
		icon_size = QSize(18, 18)
		icon_rect = QRect(option.rect.left() + 5, option.rect.top() + 2, icon_size.width(), icon_size.height())

		option.rect.setHeight(icon_size.height() + 4)

		if option.state & QtWidgets.QStyle.StateFlag.State_Selected:
			# QColor(SettingsHelper().getValue(SettingsValues.SelectedRowColor))
			painter.fillRect(option.rect,
							 ConfigClass.colorSelected)  # QColor(SettingsHelper().getValue(SettingsValues.SelectedRowColor))) # ConfigClass.colorSelected) # QColor("#9b000c")) #144aff"))

		if isinstance(icon, QPixmap):
			# scaled_icon = icon.scaled(icon_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
			painter.drawPixmap(icon_rect, icon)

		text_rect = icon_rect
		text_rect.setLeft(icon_rect.right() + 5)
		text_rect.setWidth(option.rect.width() - icon_size.width() - 10)
		# # text_rect = QRect(
		# #     icon_rect.right() + 5,
		# #     option.rect.top(),
		# #     option.rect.width() - icon_size.width() - 10,
		# #     icon_size.height() + 10
		# # )
		#
		# print(f"text_rect: {text_rect} / text: {text} / row: {row}...")
		#
		# # painter.setFont(ConfigClass.font12)
		painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, text)

		painter.restore()


# from PyQt6.QtWidgets import QStyledItemDelegate
# from PyQt6.QtCore import QSize
#
# class MyDelegate(QStyledItemDelegate):
#     def sizeHint(self, option, index):
#         return QSize(320, 20)  # Width, Height


class QHLine(QFrame):
	def __init__(self):
		super(QHLine, self).__init__()
		self.setFrameShape(QFrame.Shape.HLine)
		self.setFrameShadow(QFrame.Shadow.Sunken)


class FunctionsListView(BaseListView):
	driver = None

	def __init__(self, driver):
		super().__init__()

		self.driver = driver

		self.setItemDelegate(RightAlignedDelegate())
		self.stdModel = QStandardItemModel()
		self.setModel(self.stdModel)
		# self.setUniformItemSizes(True)
		self.setMaximumWidth(320)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
		self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
		self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
		# self.setResizeMode(QListView.ResizeMode.Fixed)
		self.setResizeMode(QListView.ResizeMode.Adjust)
		self.setUniformItemSizes(False)
		self.setWrapping(False)
		self.setFlow(QListView.Flow.TopToBottom)
		self.setFont(ConfigClass.font12)

		# list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

		# list_view.setFlow(QListView.TopToBottom)
		# self.setLa

		self.context_menu = QMenu(self)
		self.actionAddBP = self.context_menu.addAction("Add Breakpoint")
		self.actionAddBP.triggered.connect(self.handle_addBP)

	def contextMenuEvent(self, event):
		#		for i in dir(event):
		#			print(i)
		#		print(event.pos())
		#		print(self.itemAt(event.pos().x(), event.pos().y()))
		#		print(self.selectedItems())
		self.context_menu.exec(event.globalPos())
		pass

	def mouseDoubleClickEvent(self, event: QMouseEvent):
		index = self.indexAt(event.position().toPoint())

		if index.isValid():
			# self.itemDoubleClicked.emit(index)
			# print(f"self.model().data(index, Qt.ItemDataRole.UserRole): {self.model().data(index, Qt.ItemDataRole.UserRole)} ...")
			self.window().wdtDisassembly.tblDisassembly.viewAddress(
				hex(self.model().data(index, Qt.ItemDataRole.UserRole)))
		super().mouseDoubleClickEvent(event)

	def handle_addBP(self):
		logDbgC(f"handle_addBP ...")
		selected_indexes = self.selectedIndexes()
		if selected_indexes:
			selected_index = selected_indexes[0]
			selected_item = self.model().data(selected_index, Qt.ItemDataRole.UserRole)
			logDbgC(f"Selected item: {selected_item} ...")
			# self.driver.debugger.HandleCommand(f"br set -a {hex(selected_item)}")
			self.driver.bpMgr.addBPByAddr(selected_item)
			# self.window().driver.debugger.HandleCommand(f"br set -a {hex(selected_item)} -s {modName}")
			# self.driver.bpMgr.enableBPByID(selected_item, True)
			# self.driver.bpMgr.enableBPByID(daItem.text(0), not daItem.isBPEnabled)

	def add_item(self, text, row, ico=ConfigClass.pixFunction):
		item = QStandardItem(text)
		item.setToolTip(f"{text} (@ {hex(row)})")
		item.setFont(ConfigClass.font12)
		item.setEditable(False)
		item.setData(ico, Qt.ItemDataRole.DecorationRole)
		item.setData(row, Qt.ItemDataRole.UserRole)
		self.model().appendRow(item)

		# sepItm = QListWidgetItem()
		# QListViewItem
		#
		# sepItm.setSizeHint(QSize(200, 5))
		# sepItm.setFlags(Qt.ItemFlag.NoItemFlags)
		#
		# self.model().appendRow(sepItm)
		# sepFrm = QFrame()
		# sepFrm.setFrameShape(QFrame.Shape.HLine)
		# sepFrm.setFrameShadow(QFrame.Shadow.Sunken)
		# sepItm.listWidget().setItemWidget(sepItm, sepFrm)
		#
		# # self.model().
		# # self.model().appendRow(QHLine())

	def resetContent(self):
		self.stdModel.clear()
