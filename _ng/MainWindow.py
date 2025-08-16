from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QLabel, QToolBar

from _ng.config import *
from _ng.helper.debugHelper import *
from _ng.ui.menuToolbarManager import MenuToolbarManager


class MainWindow(QMainWindow):

    menuToolbarManager = None

    def __init__(self, driver=None, debugger=None, loadExec2=False):
        super().__init__()

        self.lblTest = QLabel("TESET")
        self.setCentralWidget(self.lblTest)

        self.menuToolbarManager = MenuToolbarManager(self)

        # self.toolbar = QToolBar('Main ToolBar')
        # self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)
        # self.toolbar.setIconSize(QSize(ConfigClass.toolbarIconSize, ConfigClass.toolbarIconSize))
        # self.toolbar.setContentsMargins(0, 0, 0, 0)

        # # self.load_action = self.addActionToToolbarAndMenu(ConfigClass.iconBug, '&Load Target', 'Load Target', 'Ctrl+L', self.load_clicked)
        # # self.attached_action = self.addActionToToolbarAndMenu(ConfigClass.iconGears, '&Attach to Target', 'Attach to Target', 'Ctrl+A',
        # #                                                   self.load_clicked)
        # # self.exit_action = self.addActionToToolbarAndMenu(ConfigClass.iconClear, 'E&xit LLDBPyGUI',
        # #                                                       'Exit LLDBPYGUI', 'Ctrl+X',
        # #                                                       self.exit_clicked)
        #
        # self.menuBar().setNativeMenuBar(True)
        # self.menu = self.menuBar()
        #
        # self.main_menu = self.menu.addMenu("File")
        # self.menusect_loadTarget = self.main_menu.addSection("Load Targets")
        # # self.menusect_loadTarget.
        # self.main_menu.addMenu("Disassemble executable")
        # self.main_menu.addMenu("Load executable")
        # self.main_menu.addMenu("Attach to pid / process")
        # # self.exit_action = self.addActionToToolbarAndMenu(ConfigClass.iconClear, 'E&xit LLDBPyGUI',
        # #                                                   'Exit LLDBPYGUI', 'Ctrl+X',
        # #                                                   self.exit_clicked, self.main_menu)
        # # self.main_menu.addActions([self.exit_action, self.load_action, self.attached_action])
        # # self.main_menu.addAction(self.exit_action)
        # # self.main_menu.addAction(self.load_action)
        # # self.main_menu.addSeparator()
        # # self.main_menu.addAction(self.attached_action)
        # # # self.main_menu.addSeparator()
        # # # self.main_menu.addAction(self.exit_action)
        #
        # self.file_menu = self.menu.addMenu("&Load Action")
        # # self.file_menu.addAction(self.load_action)
        # self.setM


    # def addActionToToolbarAndMenu(self, icon, actTxt, statusTip, shortcut, action_handler, parent=None):
    #
    #     if parent is None:
    #         parent = self
    #
    #     action = QAction(icon, actTxt, parent)
    #     action.setStatusTip(statusTip)
    #     action.setShortcut(shortcut)
    #     action.triggered.connect(action_handler)
    #     self.toolbar.addAction(action)
    #     return action

    def load_clicked(self):
        logDbgC(f"load_clicked() ...")
        pass

    def exit_clicked(self):
        logDbgC(f"exit_clicked() ...")
        pass
