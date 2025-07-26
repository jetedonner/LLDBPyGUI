#!/usr/bin/env python3
import lldb
from itertools import islice

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from ui.customQt.QSwitch import *
from ui.customQt.QHistoryLineEdit import *
from ui.customQt.QConsoleTextEdit import *

from lib.settings import *
from config import *

import sys
import code
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QTextEdit, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt, QObject, pyqtSignal

from ui.helper.dbgOutputHelper import logDbgC


# 1. Custom Stream for Redirecting Output
# This class acts as a file-like object that redirects write calls to a PyQt signal.
class ConsoleStream(QObject):
    """
    A custom stream class that emits a signal when text is written to it.
    Used to redirect stdout and stderr to a QTextEdit widget.
    """
    new_text = pyqtSignal(str)

    def write(self, text):
        """
        Writes the given text to the stream and emits the new_text signal.
        """
        self.new_text.emit(text)
        # Optional: Keep the original stdout/stderr for debugging the console itself
        sys.__stdout__.write(text)  # Uncomment for console debugging

    def flush(self):
        """
        No-op for this stream, but required for file-like object compatibility.
        """
        sys.__stdout__.flush()
        pass


# 2. Custom Interactive Console for PyQt
# This class integrates Python's InteractiveConsole with our custom stream.
class PyQtInteractiveConsole(code.InteractiveConsole):
    """
    A custom InteractiveConsole that directs its output to a QTextEdit via ConsoleStream.
    It takes an initial namespace (globals/locals) to operate within.
    """

    def __init__(self, output_stream, locals=None):
        """
        Initializes the interactive console.
        :param output_stream: An instance of ConsoleStream for output redirection.
        :param locals: The dictionary representing the namespace for the interpreter.
                       If None, a new empty namespace is used.
        """
        super().__init__(locals=locals)
        self.output_stream = output_stream
        self.history = []
        self.history_index = -1

    def write(self, data):
        """
        Overrides the default write method to send data to our output_stream.
        """
        self.output_stream.write(data)

    def flush(self):
        """
        Overrides the default write method to send data to our output_stream.
        """
        self.output_stream.flush()

    def run_command(self, command):
        """
        Executes a single Python command.
        :param command: The Python command string to execute.
        """
        if command.strip():
            self.history.append(command)
            self.history_index = len(self.history)

        # Temporarily redirect stdout and stderr to our custom stream
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = self.output_stream
        sys.stderr = self.output_stream
        print(f"ConsoleWidget => CHANGING STDOUT!!!!")
        try:
            # Use 'push' for multi-line input handling, though for single-line
            # QLineEdit, it behaves like 'runsource'.
            self.output_stream.write(f">>> {command}\n")  # Echo command
            self.push(command)
        except Exception as e:
            # Catch any unexpected errors from the interpreter itself
            sys.stderr.write(f"Internal interpreter error: {e}\n")
        finally:
            # Restore original stdout and stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def get_history_command(self, direction):
        """
        Retrieves commands from history for arrow key navigation.
        :param direction: 'up' for previous, 'down' for next.
        """
        if not self.history:
            return ""

        if direction == 'up':
            self.history_index = max(0, self.history_index - 1)
        elif direction == 'down':
            self.history_index = min(len(self.history), self.history_index + 1)

        if self.history_index < len(self.history):
            return self.history[self.history_index]
        else:
            return ""  # Return empty for "past" last command


# 3. The PyQt Widget for the Console
class PyQtConsoleWidget(QWidget):
    """
    A PyQt widget that provides an interactive Python console interface.
    It consists of an output QTextEdit and an input QLineEdit.
    """

    def __init__(self, locals_dict=None, parent=None):
        """
        Initializes the console widget.
        :param locals_dict: The dictionary of local variables/objects
                            to expose to the interpreter.
        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.locals_dict = locals_dict if locals_dict is not None else {}
        self._setup_ui()
        self._setup_interpreter()

    def _setup_ui(self):
        """
        Sets up the graphical user interface for the console.
        """
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # main_layout.setSpacing(5)

        # Output TextEdit
        self.output_text_edit = QTextEdit()
        self.output_text_edit.setReadOnly(True)
        self.output_text_edit.setFontPointSize(12)
        self.output_text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.output_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #282c34; /* Dark background */
                color: #abb2bf; /* Light grey text */
                border: 1px solid #3e4452;
                border-radius: 5px;
                padding: 5px;
                font: 12px 'Courier New';
            }
        """)
        main_layout.addWidget(self.output_text_edit)

        # Input LineEdit
        self.input_line_edit = QLineEdit()
        # self.input_line_edit.setFontPointSize(12)
        self.input_line_edit.setPlaceholderText("Enter Python command here...")
        self.input_line_edit.returnPressed.connect(self._execute_command)  # Connect Enter key
        self.input_line_edit.setStyleSheet("""
            QLineEdit {
                background-color: #3e4452; /* Slightly lighter dark */
                color: #abb2bf;
                border: 1px solid #5c6370;
                border-radius: 5px;
                padding: 5px;
                font: 12px 'Courier New';
            }
            QLineEdit:focus {
                border: 1px solid #61afef; /* Highlight on focus */
            }
        """)

        # Add history navigation using up/down arrow keys
        self.input_line_edit.keyPressEvent = self._custom_key_press_event

        main_layout.addWidget(self.input_line_edit)

    def _custom_key_press_event(self, event):
        """
        Custom key press event handler for the input line to manage history.
        """
        if event.key() == Qt.Key.Key_Up:
            self.input_line_edit.setText(self.console.get_history_command('up'))
        elif event.key() == Qt.Key.Key_Down:
            self.input_line_edit.setText(self.console.get_history_command('down'))
        else:
            # Let the default QLineEdit key press event handle other keys
            QLineEdit.keyPressEvent(self.input_line_edit, event)

    def _setup_interpreter(self):
        """
        Sets up the Python interactive console and connects its output to the GUI.
        """
        # Create our custom stream and connect its signal to the text edit
        self.console_stream = ConsoleStream()
        self.console_stream.new_text.connect(self.output_text_edit.append)

        # Create the interactive console, passing the desired namespace
        self.console = PyQtInteractiveConsole(
            output_stream=self.console_stream,
            locals=self.locals_dict
        )

        # Display a welcome message
        # (Type 'exit()' to close this window)
        self.output_text_edit.append("Python Interactive Console")
        self.output_text_edit.append("Access app variables using 'app_object.<variable_name>' if exposed.")
        self.output_text_edit.append("------------------------------------------------------------------\n")

    def _execute_command(self):
        """
        Retrieves the command from the input line, executes it, and clears the input.
        """
        command = self.input_line_edit.text()
        self.input_line_edit.clear()

        # if command.strip().lower() == 'exit()':
        #     # Handle exit command to close the console window or hide it
        #     self.parentWidget().close() # Assuming parent is a window
        #     return

        # Execute the command using the interactive console
        self.console.run_command(command)


class ConsoleWidget(QWidget):
    #	actionShowMemory = None
    workerManager = None

    def __init__(self, workerManager):
        super().__init__()

        self.workerManager = workerManager

        self.setHelper = SettingsHelper()

        self.wdgCmd = QWidget()
        #		self.wdgCommands = QWidget()
        self.layCmdParent = QVBoxLayout()
        self.layCmd = QHBoxLayout()
        self.wdgCmd.setLayout(self.layCmd)
        self.setLayout(self.layCmdParent)

        # self.lblCmd = QLabel("Command: ")
        # self.lblCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        #
        # self.txtCmd = QHistoryLineEdit(self.setHelper.getValue(SettingsValues.CmdHistory))
        # self.txtCmd.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        # self.txtCmd.setText(ConfigClass.initialCommand)
        # self.txtCmd.returnPressed.connect(self.execCommand_clicked)
        # self.txtCmd.availCompletitions.connect(self.handle_availCompletitions)
        # self.txtCmd.setFocus(Qt.FocusReason.NoFocusReason)
        #
        # self.swtAutoscroll = QSwitch("Autoscroll")
        # self.swtAutoscroll.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        # self.swtAutoscroll.setChecked(True)
        #
        # self.cmdExecuteCmd = QPushButton("Execute")
        # self.cmdExecuteCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        # self.cmdExecuteCmd.clicked.connect(self.execCommand_clicked)
        #
        # self.cmdClear = QPushButton()
        # self.cmdClear.setIcon(ConfigClass.iconTrash)
        # self.cmdClear.setToolTip("Clear the Commands log")
        # self.cmdClear.setIconSize(QSize(16, 16))
        # self.cmdClear.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        # self.cmdClear.clicked.connect(self.clear_clicked)
        #
        # self.layCmd.addWidget(self.lblCmd)
        # self.layCmd.addWidget(self.txtCmd)
        # self.layCmd.addWidget(self.cmdExecuteCmd)
        # self.layCmd.addWidget(self.swtAutoscroll)
        # self.layCmd.addWidget(self.cmdClear)
        # self.wdgCmd.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

        self.txtConsole = QConsoleTextEdit()
        # self.txtConsole.setReadOnly(True)
        self.txtConsole.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.txtConsole.setFont(ConfigClass.font)
        # self.txtConsole.setText("Here you can run LLDB commands. Type 'help' for a list of available commands.\n")
        self.txtConsole.setText("dave@Mia testtarget %")
        self.layCmdParent.addWidget(self.txtConsole)

    # self.layCmdParent.addWidget(self.wdgCmd)

    def handle_availCompletitions(self, compl):

        self.txtCommands.append("Available Completions:")
        #		self.win.scroll(1)
        for m in islice(compl, 1, None):
            self.txtCommands.append(m)
        pass

    def clear_clicked(self):
        self.txtCommands.setText("")

    #		command_interpreter = self.debugger.GetCommandInterpreter()

    #		self.data = self.txtCmd.text()
    #		matches = lldb.SBStringList()
    #		commandinterpreter = self.workerManager.driver.debugger.GetCommandInterpreter()
    #		commandinterpreter.HandleCompletion(
    #			self.data, len(self.data), 0, -1, matches)
    #		if len(matches) > 0:
    #			self.txtCmd.insert(matches.GetStringAtIndex(0))
    #		for match in matches:
    #			print(match)

    def execCommand_clicked(self):
        logDbgC(f"execCommand_clicked() in consoleWidget ...")
        if self.setHelper.getValue(SettingsValues.CmdHistory):
            self.txtCmd.addCommandToHistory()

        self.txtCommands.append(f"({PROMPT_TEXT}) {self.txtCmd.text().strip()}")
        if self.txtCmd.text().strip().lower() in ["clear", "clr"]:
            self.clear_clicked()
        else:
            self.workerManager.start_execCommandWorker(self.txtCmd.text(), self.handle_commandFinished)

    def handle_commandFinished(self, res):
        if res.Succeeded():
            self.txtCommands.appendEscapedText(res.GetOutput())
        else:
            self.txtCommands.appendEscapedText(f"{res.GetError()}")

        if self.swtAutoscroll.isChecked():
            self.sb = self.txtCommands.verticalScrollBar()
            self.sb.setValue(self.sb.maximum())
