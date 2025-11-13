from PyQt6.QtCore import QObject, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QToolBar, QMenu

from config import *
from helper.debugHelper import *
from helper.recentFilesManager import RecentFilesManagerNG

TOOLBAR_NAME = 'Main ToolBar'


class MenuToolbarManager(QObject):
	mainWindow = None
	toolbar = None
	menubar = None

	view_menu = None
	showSymbolsPanel_action = None
	openRecentFileCallback = None

	nav_menu = None

	def __init__(self, mainWindow):
		super().__init__()

		self.recentFilesMgr = RecentFilesManagerNG()

		self.mainWindow = mainWindow

		self.initToolbar()
		self.initMenubar()
		self.setupToolAndMenuBar()

	def initToolbar(self):
		self.toolbar = QToolBar(TOOLBAR_NAME)
		self.toolbar.setObjectName(TOOLBAR_NAME)
		# self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
		self.mainWindow.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)
		self.toolbar.setIconSize(QSize(ConfigClass.toolbarIconSize, ConfigClass.toolbarIconSize))
		self.toolbar.setContentsMargins(0, 0, 0, 0)

	def initMenubar(self):
		self.menubar = self.mainWindow.menuBar()
		self.menubar.setNativeMenuBar(False)

	def setupToolAndMenuBar(self):
		self.main_menu = self.menubar.addMenu("File")
		self.load_action = self.addActionToToolbarAndMenu(ConfigClass.iconBug, '&Load Target', 'Load Target', 'Ctrl+L',
														  self.load_clicked, self.main_menu)
		self.load_recent_action = self.addActionToToolbarAndMenu(ConfigClass.iconBug, 'Load R&ecent', 'Load Recent',
																 'Ctrl+E', self.load_clicked, self.main_menu)
		self.attached_action = self.addActionToToolbarAndMenu(ConfigClass.iconGears, '&Attach to Target',
															  'Attach to Target', 'Ctrl+A',
															  self.load_clicked, self.main_menu)
		self.toolbar.addSeparator()
		self.resume_action = self.addActionToToolbarAndMenu(ConfigClass.iconResume, 'Resume process',
															'Resume process', 'Ctrl+R')
		self.step_over_action = self.addActionToToolbarAndMenu(ConfigClass.iconStepOver, 'Step-Over',
															   'Step-Over', 'Ctrl+O')
		self.step_into_action = self.addActionToToolbarAndMenu(ConfigClass.iconStepInto, 'Step-Into',
															   'Step-Into', 'Ctrl+I')
		self.step_out_action = self.addActionToToolbarAndMenu(ConfigClass.iconStepOut, 'Step-Out',
															  'Step-Out', 'Ctrl+U')
		self.toolbar.addSeparator()

		self.settings_action = self.addActionToToolbarAndMenu(ConfigClass.iconSettings, 'LLDBPyGUI settings',
															  'LLDBPyGUI settings', 'Ctrl+P')

		self.exit_action = self.addActionToToolbarAndMenu(ConfigClass.iconClear, 'E&xit LLDBPyGUI',
														  'Exit LLDBPYGUI', 'Ctrl+X')  # ,
		# self.exit_clicked, self.main_menu)

		self.main_menu.addAction(self.load_action)
		self.load_recent_menu = QMenu("Load recent")
		# self.load_recent_menu.addAction(self.load_recent_action)

		self.recentFilesMgr.parentMenu = self.load_recent_menu
		self.recentFilesMgr.populate_recent_files_menu(self.load_recent_menu, self.add_recent_file)
		# self.add_recent_file("test.c")
		# self.add_recent_file("kim123.txt")

		self.open_app_action = QAction("Open App", self.main_menu)
		self.main_menu.addAction(self.open_app_action)
		self.main_menu.addMenu(self.load_recent_menu)
		self.main_menu.addAction(self.attached_action)
		self.main_menu.addSeparator()
		self.save_action = self.createAction("Save project", self.main_menu)
		self.main_menu.addAction(self.save_action)
		self.save_as_action = self.createAction("Save project As ..", self.main_menu)
		self.main_menu.addAction(self.save_as_action)
		self.main_menu.addSeparator()
		self.main_menu.addAction(self.settings_action)
		self.main_menu.addSeparator()
		self.main_menu.addAction(self.exit_action)

		self.view_menu = self.menubar.addMenu("View")

		secDockPanels = self.view_menu.addSection("Dock-Panels")
		# secDockPanels.a
		self.showSymbolsPanel_action = self.createAction("Show Symbols", self.view_menu, "Show symbols panel")
		self.showSymbolsPanel_action.setCheckable(True)

		self.view_menu.addAction(self.showSymbolsPanel_action)

		self.nav_menu = self.menubar.addMenu("Navigation")
		self.goBack_action = self.addActionToToolbarAndMenu(ConfigClass.iconLeft, 'Go Back', 'Go Back', 'Ctrl+B')
		self.goForward_action = self.addActionToToolbarAndMenu(ConfigClass.iconRight, 'Go Forward', 'Go Forward',
															   'Ctrl+F')

		self.gotoOEP_action = self.addActionToToolbarAndMenu(ConfigClass.iconBug, '&Goto OEP', 'Goto OEP', 'Ctrl+G',
															 self.gotoOEP_clicked, self.nav_menu)
		self.gotoPC_action = self.addActionToToolbarAndMenu(ConfigClass.iconBug, 'Goto &PC', 'Goto PC', 'Ctrl+P')

		self.gotoAddr_action = self.addActionToToolbarAndMenu(ConfigClass.iconBug, 'Goto Address', 'Goto Address',
															  'Ctrl+A')

		self.toolbar.addSeparator()

		self.test_action = QAction(ConfigClass.iconTest, '&Test', self)
		self.test_action.setStatusTip('Test')
		self.test_action.setShortcut('Ctrl+1')
		# self.test_action.triggered.connect(self.test_clicked)
		self.toolbar.addAction(self.test_action)

		self.test_action2 = QAction(ConfigClass.iconTest, 'Test 2', self)
		self.test_action2.setStatusTip('Test 2')
		self.test_action2.setShortcut('Ctrl+2')
		# self.test_action.triggered.connect(self.test_clicked)
		self.toolbar.addAction(self.test_action2)

		self.nav_menu.addAction(self.goBack_action)
		self.nav_menu.addAction(self.goForward_action)
		self.nav_menu.addSeparator()
		self.nav_menu.addAction(self.gotoOEP_action)
		self.nav_menu.addAction(self.gotoPC_action)
		self.nav_menu.addAction(self.gotoAddr_action)

		self.dbg_menu = self.menubar.addMenu("Debug")
		# self.resume_action = self.addActionToToolbarAndMenu(ConfigClass.iconResume, 'Resume process',
		#                                                   'Resume process', 'Ctrl+R')
		# self.step_over_action = self.addActionToToolbarAndMenu(ConfigClass.iconStepOver, 'Step-Over',
		#                                                        'Step-Over', 'Ctrl+O')
		# self.step_into_action = self.addActionToToolbarAndMenu(ConfigClass.iconStepInto, 'Step-Into',
		#                                                        'Step-Into', 'Ctrl+I')
		# self.step_out_action = self.addActionToToolbarAndMenu(ConfigClass.iconStepOut, 'Step-Out',
		#                                                        'Step-Out', 'Ctrl+U')

		self.dbg_menu.addAction(self.resume_action)
		self.dbg_menu.addSeparator()
		self.dbg_menu.addAction(self.step_over_action)
		self.dbg_menu.addAction(self.step_into_action)
		self.dbg_menu.addAction(self.step_out_action)

		self.help_menu = self.menubar.addMenu("Help")
		self.about_action = self.addActionToToolbarAndMenu(ConfigClass.iconBug, 'About LLDBPyGUI', 'About LLDBPyGUI',
														   'Ctrl+A')
		self.help_menu.addAction(self.about_action)
		self.help_menu.addSeparator()
		self.show_tipsandtricks_action = QAction("Show tips and tricks", self.help_menu)
		self.help_menu.addAction(self.show_tipsandtricks_action)

	def add_recent_file(self, file_path):
		# Load the file here
		print(f"Opening: {file_path}")
		self.recentFilesMgr.save_recent_file(file_path)
		self.recentFilesMgr.populate_recent_files_menu(self.load_recent_menu, self.openRecentFileCallback)

	def createAction(self, actTxt, parent, statusTip="", shortcut=""):
		action = QAction(actTxt, parent)

		if statusTip != "":
			action.setStatusTip(statusTip)

		if shortcut != "":
			action.setShortcut(shortcut)

		return action

	def addActionToToolbarAndMenu(self, icon, actTxt, statusTip, shortcut, action_handler=None, parent=None):

		if parent is None:
			parent = self

		action = QAction(icon, actTxt, parent)
		action.setStatusTip(statusTip)
		action.setShortcut(shortcut)
		if action_handler is not None:
			action.triggered.connect(action_handler)
		self.toolbar.addAction(action)
		return action

	def createAction2(self, actTxt, icon=None, parent=None):
		if icon is not None and parent is not None:
			action = QAction(icon, actTxt, parent)
		else:
			action = QAction(actTxt)
		return action

	def load_clicked(self):
		logDbgC(f"load_clicked() ...")

	# def exit_clicked(self):
	#     logDbgC(f"exit_clicked() ...")

	def gotoOEP_clicked(self):
		logDbgC(f"gotoOEP_clicked() ...")
