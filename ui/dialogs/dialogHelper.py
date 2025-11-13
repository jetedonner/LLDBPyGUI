#!/usr/bin/env python3

from PyQt6.QtCore import *
from PyQt6.QtGui import QShortcut
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton

from config import *
from helper.debugHelper import logDbgC


class WebDialog(QDialog):

	def __init__(self, url):
		super().__init__()
		self.setWindowTitle("Website Viewer")
		self.setModal(True)
		self.resize(800, 600)

		layout = QVBoxLayout(self)

		# Web view
		self.web_view = QWebEngineView()
		self.web_view.load(QUrl(url))

		self.web_view.installEventFilter(self)

		layout.addWidget(self.web_view)

		# QShortcut(QKeySequence("Esc"), self, activated=self.reject)
		esc_shortcut = QShortcut(self)
		esc_shortcut.setKey(Qt.Key.Key_Escape)
		esc_shortcut.activated.connect(self.closeThisModal)

	def closeThisModal(self):
		logDbgC(f"dialogHelper.keyPressEvent() => closeThisModal() ...")
		self.reject()
		pass

	# def eventFilter(self, obj, event):
	#     logDbgC(f"WebDialog.eventFilter({obj}, {event}) ...")
	#     if obj == self.web_view and event.type() == QEvent.Type.KeyPress:
	#         if event.key() == Qt.Key.Key_Escape:
	#             self.accept()
	#             self.close()
	#             return True
	#     return super().eventFilter(obj, event)

	# def keyPressEvent(self, event):
	#     logDbgC(f"WebDialog.keyPressEvent({event}) ...")
	#     if event.key() == Qt.Key.Key_Escape:
	#         self.reject()  # or self.close()
	#     else:
	#         super().keyPressEvent(event)


class ARMDocDialog(WebDialog):
	def __init__(self, url):
		super().__init__()
		self.setWindowTitle("Website Viewer")
		self.setModal(True)
		self.resize(800, 600)


class ConfirmDialog(QDialog):
	button_clicked = QDialogButtonBox.StandardButton.Abort

	def __init__(self, title, question, abortBtn=None):
		super().__init__()
		self.setWindowTitle(title)

		self.buttonBox = QDialogButtonBox()

		# Create buttons and add them to the button box with explicit roles.
		# Create the Abort button and make it the default.
		# self.btnAbort = QPushButton("Detach")
		if abortBtn is not None:
			self.btnAbort = self.buttonBox.addButton(
				QDialogButtonBox.StandardButton.Abort)  # (self.btnAbort, QDialogButtonBox.ButtonRole.DestructiveRole)
			self.btnAbort.setText(abortBtn)
			self.btnAbort.setDefault(True)
			self.btnAbort.setAutoDefault(True)
			self.btnAbort.clicked.connect(self.handle_detached)

		# Create Ok and Cancel buttons and add them.
		# The Ok button's role is now `AcceptRole`, but since another button is
		# explicitly set as default, it won't be made default.
		self.btnOk = QPushButton("OK")
		self.buttonBox.addButton(self.btnOk, QDialogButtonBox.ButtonRole.AcceptRole)
		self.btnOk.clicked.connect(self.accept)

		self.btnCancel = QPushButton("Cancel")
		self.buttonBox.addButton(self.btnCancel, QDialogButtonBox.ButtonRole.RejectRole)
		self.btnCancel.clicked.connect(self.close)

		# self.buttonBox.accepted.connect(self.accept)
		# self.buttonBox.rejected.connect(self.reject)
		#
		# self.buttonBox.destroyed.connect(self.destroy)

		# Layout setup remains the same
		self.layout = QVBoxLayout()
		message = QLabel(question)
		self.icon = ConfigClass.iconBugGreen
		pixmap = self.icon.pixmap(64, 64)
		icon_label = QLabel()
		icon_label.setPixmap(pixmap)

		self.layoutIco = QHBoxLayout()
		self.layoutIco.addWidget(icon_label)
		self.layoutIco.addWidget(message)

		self.layout.addLayout(self.layoutIco)
		self.layout.addWidget(self.buttonBox)
		self.setLayout(self.layout)

	def handle_detached(self):
		print("Abort button clicked!")
		self.button_clicked = QDialogButtonBox.StandardButton.Abort
		self.destroy()

	def accept(self):
		print("OK button clicked!")
		self.button_clicked = QDialogButtonBox.StandardButton.Ok
		super().accept()

	def reject(self):
		print("Cancel button clicked!")
		self.button_clicked = QDialogButtonBox.StandardButton.Cancel
		super().reject()

	def destroy(self):
		print("Destroy button clicked!")
		self.button_clicked = QDialogButtonBox.StandardButton.Abort
		super().destroy()


class InputDialog(QDialog):

	button_clicked = QDialogButtonBox.StandardButton.Abort

	def __init__(self, title="", prompt="", preset="", placeholder=""):
		super().__init__()

		self.setWindowTitle(title)

		QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

		self.buttonBox = QDialogButtonBox(QBtn)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)

		self.layout = QVBoxLayout()
		self.layout.setContentsMargins(15, 15, 15, 15)
		self.message = QLabel(prompt)
		self.txtInput = QLineEdit()
		if preset != "":
			self.txtInput.setText(preset)

		if placeholder != "":
			self.txtInput.setPlaceholderText(placeholder)

		self.layout.addWidget(self.message)
		self.layout.addWidget(self.txtInput)
		self.layout.addWidget(self.buttonBox)
		self.setLayout(self.layout)
		self.txtInput.setFocus()

	def accept(self):
		print("OK button clicked!")
		self.button_clicked = QDialogButtonBox.StandardButton.Ok
		super().accept()

	def reject(self):
		print("Cancel button clicked!")
		self.button_clicked = QDialogButtonBox.StandardButton.Cancel
		super().reject()

	# def destroy(self):
	# 	print("Destroy button clicked!")
	# 	self.button_clicked = QDialogButtonBox.StandardButton.Abort
	# 	super().destroy()


class BPNameDialog(InputDialog):
	def __init__(self, presetAddress="0x"):
		super().__init__("Address to goto", "Enter an address to goto:", presetAddress)


class GotoAddressDialog(InputDialog):
	def __init__(self, presetAddress="0x"):
		super().__init__("Address to goto", "Enter an address to goto:", presetAddress)


class EnterHexAddressDialog(InputDialog):
	def __init__(self, presetAddress="0x"):
		super().__init__("Modify hex value", "Enter new hex value:", presetAddress)


def showSaveFileDialog(app=None, nameFilter="JSON (*.json)", dontUseNativeDialog=False):
	dialog = QFileDialog(None, "Select file to save", "", nameFilter)
	if dontUseNativeDialog:
		dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
	dialog.setFileMode(QFileDialog.FileMode.AnyFile)
	dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
	dialog.setNameFilter(nameFilter)
	if not dontUseNativeDialog:
		dialog.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
	# if app != None:
	#     app.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, True)

	if dialog.exec():
		filename = dialog.selectedFiles()[0]
		#		while os.path.exists(filename):
		#			if dialog.exec():
		#				filename = dialog.selectedFiles()[0]
		#		print(filename)
		return filename
	#			self.start_workerLoadTarget(filename)
	else:
		return None


def showOpenFileDialog(path="./"):
	dialog = QFileDialog(None, "Select executable or library", path, "All Files (*.*)")  # "./_testtarget"

	dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
	# dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
	# dialog.setNameFilter("All Files (*)")

	dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
	dialog.setNameFilter("Executables (*.exe *.com *.bat *);;Libraries (*.dll *.so *.dylib)")

	if dialog.exec():
		filename = dialog.selectedFiles()[0]
		return filename
	else:
		return None
