from PyQt6.QtCore import QObject, QSize, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QToolBar

from _ng.config import *
from _ng.helper.debugHelper import *

class MenuToolbarManager(QObject):

    mainWindow = None
    toolbar = None
    menubar = None

    def __init__(self, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow

        self.initToolbar()
        self.initMenubar()
        self.setupToolAndMenuBar()

    def initToolbar(self):
        self.toolbar = QToolBar('Main ToolBar')
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        # self.mainWindow.toolbar = self.toolbar
        self.mainWindow.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)
        self.toolbar.setIconSize(QSize(ConfigClass.toolbarIconSize, ConfigClass.toolbarIconSize))
        self.toolbar.setContentsMargins(0, 0, 0, 0)


    def initMenubar(self):
        self.menubar = self.mainWindow.menuBar()
        self.menubar.setNativeMenuBar(False)

    def setupToolAndMenuBar(self):
        self.main_menu = self.menubar.addMenu("File")
        self.load_action = self.addActionToToolbarAndMenu(ConfigClass.iconBug, '&Load Target', 'Load Target', 'Ctrl+L', self.load_clicked, self.main_menu)
        self.attached_action = self.addActionToToolbarAndMenu(ConfigClass.iconGears, '&Attach to Target', 'Attach to Target', 'Ctrl+A',
                                                          self.load_clicked, self.main_menu)
        self.exit_action = self.addActionToToolbarAndMenu(ConfigClass.iconClear, 'E&xit LLDBPyGUI',
                                                              'Exit LLDBPYGUI', 'Ctrl+X',
                                                              self.exit_clicked, self.main_menu)

        self.main_menu.addAction(self.load_action)
        self.main_menu.addAction(self.attached_action)
        self.main_menu.addSeparator()
        self.main_menu.addAction(self.exit_action)

        self.nav_menu = self.menubar.addMenu("Navigation")
        self.gotoOEP_action = self.addActionToToolbarAndMenu(ConfigClass.iconBug, '&Goto OEP', 'Goto OEP', 'Ctrl+G',
                                                          self.gotoOEP_clicked, self.nav_menu)
        self.nav_menu.addAction(self.gotoOEP_action)

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

    def load_clicked(self):
        logDbgC(f"load_clicked() ...")

    def exit_clicked(self):
        logDbgC(f"exit_clicked() ...")

    def gotoOEP_clicked(self):
        logDbgC(f"gotoOEP_clicked() ...")