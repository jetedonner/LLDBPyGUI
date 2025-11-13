from PyQt6.QtWidgets import QWizard, QCheckBox, QHBoxLayout, QWidget, QGroupBox, \
	QComboBox

from config import ConfigClass
from ui.dialogs.dialogHelper import showOpenFileDialog


class DecompileExecWizard(QWizard):

	def __init__(self):
		super().__init__()

		# self.addPage(self.createIntroPage())
		# self.addPage(FileSelectPage())

		self.setMinimumSize(800, 640)
		self.setWindowTitle("Decompile-Wizard")
		self.setWizardStyle(QWizard.WizardStyle.MacStyle)

		pixmap = ConfigClass.pixYingYang
		# Set as watermark (bottom-left corner in MacStyle)
		self.setPixmap(QWizard.WizardPixmap.WatermarkPixmap, pixmap)

		# Optionally set a logo (top-left corner)
		self.setPixmap(QWizard.WizardPixmap.LogoPixmap, pixmap)

		# Or set a header image (top banner)
		self.setPixmap(QWizard.WizardPixmap.BannerPixmap, pixmap)

		self.setPixmap(QWizard.WizardPixmap.BackgroundPixmap, pixmap)

		self.addPage(self.createIntroPage())
		self.addPage(FileSelectPage())

		# wdt = QWidget()
		# wdt.setLayout(QVBoxLayout())
		# wdt.layout().addWidget(QPushButton("HElLO !!!"))
		# self.setSideWidget(wdt)
		# self.show()

	def createIntroPage(self):
		introPage = QWizardPage()
		introPage.setTitle("Introduction")

		lblIntro = QLabel("This wizard will help you to load an executable or library and decompile it.")
		lblIntro.setWordWrap(True)

		layMain = QVBoxLayout(introPage)
		layMain.addWidget(lblIntro)
		introPage.setLayout(layMain)

		introPage.setStyleSheet("""
            QWizardPage {
                background-image: url(../../../resources/img/YinYang_RedBlack_Roses.png);
                background-repeat: no-repeat;
                background-position: center;
            }
        """)

		return introPage

	def showWizard(self):
		self.setCurrentId(0)
		self.exec()


from PyQt6.QtWidgets import (
	QWizardPage, QLabel, QVBoxLayout, QPushButton, QLineEdit
)


class FileSelectPage(QWizardPage):
	def __init__(self):
		super().__init__()
		self.setTitle("Select File")

		layout = QVBoxLayout(self)

		self.grpTarget = QGroupBox("Target")
		# self.grpDebugger.setCheckable(True)
		# self.grpDebugger.setChecked(True)
		self.layTarget = QVBoxLayout()
		self.grpTarget.setLayout(self.layTarget)

		self.label = QLabel("Choose a file to decompile:")
		self.label.setWordWrap(True)

		self.layBrowse = QHBoxLayout()
		self.wdtBrowse = QWidget()
		self.wdtBrowse.setLayout(self.layBrowse)

		self.filePathEdit = QLineEdit()
		# self.filePathEdit.setReadOnly(True)
		self.layBrowse.addWidget(self.filePathEdit)

		self.selectButton = QPushButton("...")
		self.selectButton.clicked.connect(self.openFileDialog)
		self.layBrowse.addWidget(self.selectButton)

		self.chkLoadSrc = QCheckBox("Load source code")

		self.grpDebugger = QGroupBox("Debugger")
		# self.grpDebugger.setCheckable(True)
		# self.grpDebugger.setChecked(True)
		self.layDebugger = QVBoxLayout()
		self.grpDebugger.setLayout(self.layDebugger)
		self.chkBreakAtMain = QCheckBox("Break at main function")
		self.chkBreakAtScanf = QCheckBox("Break at scanf etc.")

		self.layTarget.addWidget(self.label)
		self.layTarget.addWidget(self.wdtBrowse)

		self.cmbArch = QComboBox()
		self.cmbArch.currentIndexChanged.connect(self.cmbArch_changed)
		self.cmbArch.addItem("arm64")
		self.cmbArch.addItem("x86_64")

		self.layTarget.addWidget(self.cmbArch)

		self.layTarget.addWidget(self.chkLoadSrc)
		layout.addWidget(self.grpTarget)

		self.layDebugger.addWidget(self.chkBreakAtMain)
		self.layDebugger.addWidget(self.chkBreakAtScanf)
		# self.grpDebugger.setFlat(True)
		layout.addWidget(self.grpDebugger)
		self.setLayout(layout)

	def cmbArch_changed(self, index):
		pass

	def openFileDialog(self):
		file_path = showOpenFileDialog()
		# if filename and filename != "":
		#     file_path, _ = QFileDialog.getOpenFileName(
		#         self,
		#         "Select File",
		#         "",
		#         "Executable Files (*.dylib *.bin *.exe);;All Files (*)"
		#     )
		if file_path:
			self.filePathEdit.setText(file_path)
