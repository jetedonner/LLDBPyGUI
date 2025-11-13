import os

import markdown
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QFont, QShortcut, QKeySequence
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QPushButton, QCheckBox, QSizePolicy

from helper.debugHelper import logDbgC
from lib.settings import SettingsHelper, SettingsValues


class TipsAndTricksDialog(QDialog):
	pages = ["TipsAndTricks-00-Start.md", "TipsAndTricks-01-Main-GUI-Overview.md", "TipsAndTricks-02-Shortcuts.md",
			 "TipsAndTricks-03-FileInfos.md", "TipsAndTricks-04-Disassembly.md", "TipsAndTricks-05-Registers.md",
			 "TipsAndTricks-06-Variables.md", "TipsAndTricks-07-Breakpoints.md", "TipsAndTricks-08-Sourcecode.md",
			 "TipsAndTricks-09-ThreadsFrames.md", "TipsAndTricks-10-Listeners.md", "TipsAndTricks-09-Console.md"]
	currIdx = 0

	def __init__(self, parent=None):
		super(QDialog, self).__init__(parent)
		# self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

		self.setHelper = SettingsHelper()
		# Create layout and label for the GIF
		layout = QVBoxLayout()
		self.lblTitle = QLabel("LLDBGUI - Tips and Tricks")
		self.lblTitle.setFont(QFont(f"'Courier New' 64qpx"))
		layout.addWidget(self.lblTitle)

		self.weView = QWebEngineView()
		self.base_path = os.path.abspath("resources/tipsAndTricks")
		self.base_url = QUrl.fromLocalFile(self.base_path + "/")

		self.loadPage(self.pages[self.currIdx])

		self.weView.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		layout.addWidget(self.weView)

		self.wdtCtrl = QWidget()
		self.layCtrl = QHBoxLayout()
		self.wdtCtrl.setLayout(self.layCtrl)

		self.chkShowAtStartup = QCheckBox("Show tips at startup")
		self.chkShowAtStartup.setChecked(bool(self.setHelper.getValue(SettingsValues.ShowTipsAtStartup)))
		self.chkShowAtStartup.clicked.connect(self.showAtStart_clicked)
		self.layCtrl.addWidget(self.chkShowAtStartup)

		self.cmdPrev = QPushButton(f"Previous")
		self.cmdPrev.clicked.connect(self.prev_clicked)
		self.layCtrl.addWidget(self.cmdPrev)

		self.cmdNext = QPushButton(f"Next")
		self.cmdNext.clicked.connect(self.next_clicked)
		self.layCtrl.addWidget(self.cmdNext)

		self.cmdClose = QPushButton(f"Close")
		self.cmdClose.clicked.connect(self.close_clicked)
		self.layCtrl.addWidget(self.cmdClose)

		layout.addWidget(self.wdtCtrl)

		self.setLayout(layout)

		self.setFixedSize(750, 840)
		self.setModal(True)

		# Add shortcut
		esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
		esc_shortcut.activated.connect(self.close)

	@staticmethod
	def showTipsAndTricksDialog():
		ttd = TipsAndTricksDialog()
		return ttd.exec()

	def keyPressEvent(self, event):
		logDbgC(f"keyPressEvent occurred {event.key()} ...")
		if event.key() == Qt.Key.Key_Escape:
			self.close()
		elif event.key() == Qt.Key.Key_Left:
			self.prev_clicked()
		elif event.key() == Qt.Key.Key_Right:
			self.next_clicked()
		else:
			super().keyPressEvent(event)

	def loadPage(self, page):
		# self.base_path = os.path.abspath("resources/tipsAndTricks")
		# self.base_url = QUrl.fromLocalFile(self.base_path + "/")
		html = self.loadMD(f"{self.base_path}/{page}")
		htmlFull = self.makeResponsive(html)
		# logDbgC(f"base_url: {self.base_url} (In Init) ...\r\n\r\n{html}\r\n\r\n{htmlFull}")
		self.weView.setHtml(htmlFull, self.base_url)

	def showAtStart_clicked(self):
		self.setHelper.setValue(SettingsValues.ShowTipsAtStartup, self.chkShowAtStartup.isChecked())

	def prev_clicked(self):
		# logDbgC(f"PREV clicked ...")
		if (self.currIdx - 1) >= 0:
			self.currIdx -= 1
		else:
			self.currIdx = len(self.pages) - 1
		self.loadPage(self.pages[self.currIdx])

	def next_clicked(self):
		# logDbgC(f"NEXT clicked ...")
		if (self.currIdx + 1) < len(self.pages):
			self.currIdx += 1
		else:
			self.currIdx = 0
		# logDbgC(f"NEXT clicked (after): {self.currIdx} ({self.pages[self.currIdx]}) ...")
		self.loadPage(self.pages[self.currIdx])

	def close_clicked(self):
		SettingsHelper().setValue(SettingsValues.ShowTipsAtStartup, self.chkShowAtStartup.isChecked())
		self.close()

	def loadMD(self, fileName):
		# import os
		# base_path = os.path.abspath("img/")
		# base_url = QUrl.fromLocalFile(base_path + "/")
		# logDbgC(f"base_url: {base_url} (In loadMD) ...")

		script_dir = os.path.dirname(os.path.abspath(__file__))
		md_path = os.path.join(script_dir + "/../../resources/tipsAndTricks/", fileName)

		# Read the Markdown file content
		with open(md_path, "r", encoding="utf-8") as f:
			md_text = f.read()

		return markdown.markdown(md_text, extensions=["fenced_code", "tables"])

	def makeResponsive(self, html_content):
		return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    box-sizing: border-box;
                    width: 100%;
                    max-width: 100%;
                    overflow-x: hidden;
                    font-family: sans-serif;
                }}
                img, table {{
                    max-width: 100%;
                    height: auto;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
