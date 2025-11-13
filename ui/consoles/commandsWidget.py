#!/usr/bin/env python3
from itertools import islice

import lldb

from config import *
from helper.debugHelper import logDbgC
from lib.settings import *
from ui.customQt.QConsoleTextEdit import *
from ui.customQt.QHistoryLineEdit import *
from ui.customQt.QSwitch import *
from worker.execCommandWorker import ExecCommandWorker


class CommandsWidget(QWidget):
    driver = None

    def __init__(self, driver):
        super().__init__()

        self.driver = driver

        self.setHelper = SettingsHelper()

        self.wdgCmd = QWidget()
        self.wdgCmd.setContentsMargins(0, 0, 0, 0)
        #		self.wdgCommands = QWidget()
        self.layCmdParent = QVBoxLayout()
        self.layCmdParent.setContentsMargins(0, 0, 0, 0)
        self.layCmd = QHBoxLayout()
        self.layCmd.setContentsMargins(0, 0, 0, 0)
        self.wdgCmd.setLayout(self.layCmd)
        self.setLayout(self.layCmdParent)

        self.txtCmd = QHistoryLineEdit(self.setHelper.getValue(SettingsValues.CmdHistory),
                                       self.setHelper.getValue(SettingsValues.PersistentCommandHistory),
                                       ConfigClass.lldbConsoleCmdHistory)
                                       # "./resources/histories/lldb_console_history.json")
        self.txtCmd.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.txtCmd.setPlaceholderText("Enter LLDB command here ...")
        self.txtCmd.returnPressed.connect(self.execCommand_clicked)
        self.txtCmd.availCompletitions.connect(self.handle_availCompletitions)
        self.txtCmd.setFocus(Qt.FocusReason.NoFocusReason)
        self.txtCmd.setContentsMargins(0, 0, 0, 0)

        self.swtAutoscroll = QSwitch("Autoscroll", SwitchSize.ExtraSmall)
        self.swtAutoscroll.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.swtAutoscroll.setChecked(True)

        self.cmdExecuteCmd = QPushButton("Execute")
        self.cmdExecuteCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.cmdExecuteCmd.clicked.connect(self.execCommand_clicked)

        self.cmdClear = QPushButton()
        self.cmdClear.setIcon(ConfigClass.iconTrash)
        self.cmdClear.setToolTip("Clear the Commands log")
        self.cmdClear.setIconSize(QSize(16, 16))
        self.cmdClear.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.cmdClear.clicked.connect(self.clear_clicked)

        self.layCmd.addWidget(self.txtCmd)
        self.layCmd.addWidget(self.cmdExecuteCmd)
        self.layCmd.addWidget(self.swtAutoscroll)
        self.layCmd.addWidget(self.cmdClear)
        self.layCmd.setContentsMargins(0, 0, 0, 0)
        self.wdgCmd.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.wdgCmd.setContentsMargins(0, 0, 0, 0)

        self.txtCommands = QConsoleTextEdit()
        self.txtCommands.setReadOnly(True)
        self.txtCommands.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.txtCommands.setFont(ConfigClass.font)
        self.txtCommands.setText("Here you can run LLDB commands. Type 'help' for a list of available commands.\n")

        self.txtCommands.setContentsMargins(0, 0, 0, 0)
        self.layCmdParent.addWidget(self.txtCommands)
        self.layCmdParent.addWidget(self.wdgCmd)
        self.layCmdParent.setContentsMargins(0, 0, 0, 0)

    def focusTxtCmd(self):
        self.txtCmd.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    def handle_availCompletitions(self, compl):
        self.txtCommands.append("Available Completions:")
        for m in islice(compl, 1, None):
            self.txtCommands.append(m)
        pass

    def clear_clicked(self):
        self.txtCommands.setText("")

    def execCommand_clicked(self):
        logDbgC(f"execCommand_clicked() in commandsWidget ...")
        newCommand = ""
        if self.setHelper.getValue(SettingsValues.CmdHistory):
            newCommand = self.txtCmd.addCommandToHistory()
            self.txtCmd.setText("")

        self.txtCommands.append(f"({PROMPT_TEXT}) {newCommand.strip()}")
        if newCommand.strip().lower() in ["clear", "clr"]:
            self.clear_clicked()
        else:
            self.start_execCommandWorker(newCommand, self.handle_commandFinished)

    def start_execCommandWorker(self, command, handle_commandFinished):
        self.workerExecCommand = ExecCommandWorker(self.driver, command)
        self.workerExecCommand.signals.commandCompleted.connect(handle_commandFinished)
        QThreadPool.globalInstance().start(self.workerExecCommand)

    def handle_commandFinished(self, res):
        sOutput = ""
        if res.Succeeded():
            sOutput = res.GetOutput()
            self.txtCommands.appendEscapedText(sOutput)
        # self.center_last_arrow_line()
        # # Find the line with "->"
        # lines = sOutput.splitlines()
        # for i, line in enumerate(lines):
        # 	if "->" in line:
        # 		cursor = self.txtCommands.textCursor()
        # 		# Move to start
        # 		cursor.movePosition(QTextCursor.MoveOperation.Start)
        # 		# Move to the line
        # 		for _ in range(i):
        # 			cursor.movePosition(QTextCursor.MoveOperation.Down)
        # 		cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        # 		self.txtCommands.setTextCursor(cursor)
        # 		self.txtCommands.centerCursor()
        # 		break
        # # if sOutput.contains("->"):
        # 	# self.txtCommands
        else:
            self.txtCommands.appendEscapedText(f"{res.GetError()}")

        if not res.Succeeded() or (res.Succeeded() and (sOutput.find("->") == -1 or not self.center_last_arrow_line())):
            if self.swtAutoscroll.isChecked():
                self.sb = self.txtCommands.verticalScrollBar()
                self.sb.setValue(self.sb.maximum())

    def center_last_arrow_line(self):
        bRet = False

        lines = self.txtCommands.toPlainText().splitlines()
        for i in reversed(range(len(lines))):
            if lines[i].startswith("->"):
                target_line_index = i
                bRet = True
                break
        else:
            return bRet  # No matching line found

        cursor = self.txtCommands.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        for _ in range(target_line_index):
            cursor.movePosition(QTextCursor.MoveOperation.Down)

        self.txtCommands.setTextCursor(cursor)
        return bRet

    def resetContent(self, resetCommandHistory=False, resetConsole=False):
        self.txtCmd.clearCommandText(resetCommandHistory)
        if resetConsole:
            self.txtCommands.setText("")
