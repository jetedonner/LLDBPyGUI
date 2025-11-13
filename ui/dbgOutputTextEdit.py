from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTextEdit

from lib.settings import *
from ui.customQt.QSwitch import QSwitch, SwitchSize


class OutputStream(QObject):
	text_written = pyqtSignal(object)
	text_flush = pyqtSignal()

	def write(self, text):
		self.text_written.emit(text)

	def flush(self):
		self.text_flush.emit()
		pass  # Required for compatibility


class DbgOutputWidget(QWidget):

	def __init__(self):
		super().__init__()

		self.layHMain = QHBoxLayout()
		self.layCtrls = QVBoxLayout()

		# self.cmdShrink = QPushButton()
		# # self.cmdShrink.setToolTip("Hide Debug Output...")
		# self.cmdShrink.setIcon(ConfigClass.iconShrink)
		# self.cmdShrink.setMaximumWidth(18)
		# self.cmdShrink.clicked.connect(self.cmdShrink_clicked)
		# self.cmdShrink.setContentsMargins(0, 0, 0, 0)
		# self.cmdShrink.setStatusTip(f"Hide debug output console...")
		self.layCtrls.setContentsMargins(10, 10, 0, 0)
		# self.layCtrls.addWidget(self.cmdShrink)

		self.cmdClear = QPushButton()
		# self.cmdClear.setToolTip("Clear Debug Output...")
		self.cmdClear.setIcon(ConfigClass.iconClear)
		self.cmdClear.setMaximumWidth(18)
		self.cmdClear.clicked.connect(self.cmdClear_clicked)
		self.cmdClear.setContentsMargins(0, 0, 0, 0)
		self.cmdClear.setStatusTip(f"Clear debug output console")
		self.layCtrls.addWidget(self.cmdClear)
		self.swtAutoscroll = QSwitch(f"", SwitchSize.ExtraSmall)
		doAutoscroll = SettingsHelper().getValue(SettingsValues.AutoScrollDbgOutput)
		self.swtAutoscroll.setChecked(doAutoscroll)
		self.swtAutoscroll.checked.connect(self.swtAutoscroll_changed)
		self.swtAutoscroll.setContentsMargins(0, 0, 0, 0)
		self.swtAutoscroll.setStatusTip(f"Autoscroll the debug output")
		self.layCtrls.addWidget(self.swtAutoscroll)

		# Add stretch to push everything above it to the top
		self.layCtrls.addStretch()
		self.wdtCtrls = QWidget()
		self.wdtCtrls.setLayout(self.layCtrls)
		self.layHMain.addWidget(self.wdtCtrls)
		self.txtDbg = DbgOutputTextEdit()
		self.txtDbg.setAutoscroll(doAutoscroll)
		self.txtDbg.setContentsMargins(0, 0, 0, 0)
		self.layHMain.addWidget(self.txtDbg)
		self.layHMain.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.layHMain)

	def logDbg(self, logMsg):
		self.txtDbg.logDbg(logMsg)

	# def cmdShrink_clicked(self):
	#     # self.window().splitterMain.
	#     sizes = self.parentWidget().sizes()
	#     logDbgC(f"sizes: {sizes}")
	#
	#     self.window().splitterMain.setSizes([sizes[0], sizes[1], 0])
	#
	#     pass

	def cmdClear_clicked(self):
		self.txtDbg.setText("")

	def swtAutoscroll_changed(self, checked):
		self.txtDbg.setAutoscroll(checked)
		SettingsHelper().setValue(SettingsValues.AutoScrollDbgOutput,
								  checked)  # Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)


class DbgOutputTextEdit(QTextEdit):
	autoscroll = True

	def __init__(self):
		super().__init__()

		self.autoscroll = True
		self.setReadOnly(True)
		self.setUndoRedoEnabled(False)
		self.setTabChangesFocus(True)

		# self.setStyleSheet("""
		#     QTextEdit {
		#         background-color: #282c34; /* Dark background */
		#         color: #abb2bf; /* Light grey text */
		#         border: 1px solid #3e4452;
		#         border-radius: 5px;
		#         padding: 5px;
		#         font: 12px 'Courier New';
		#     }
		# """)

	def setAutoscroll(self, doAutoscroll=True):
		self.autoscroll = doAutoscroll
		if self.autoscroll:
			self.scrollToEnd()

	def logDbg(self, logMsg):

		if self.autoscroll:
			self.append(logMsg)
			self.scrollToEnd()
			# cursor = self.textCursor()
			# cursor.movePosition(QTextCursor.MoveOperation.End)
			# self.setTextCursor(cursor)
			# self.ensureCursorVisible()
		else:
			oldScrollPos = self.verticalScrollBar().value()
			self.append(logMsg)
			self.verticalScrollBar().setValue(oldScrollPos)

	def scrollToEnd(self):
		cursor = self.textCursor()
		# , QTextCursor.MoveMode.MoveAnchor
		cursor.movePosition(QTextCursor.MoveOperation.End)
		self.setTextCursor(cursor)
		self.ensureCursorVisible()
