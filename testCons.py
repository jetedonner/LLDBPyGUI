from PyQt6 import QtCore, QtWidgets
import sys

# On Windows it looks like cp850 is used for my console. We need it to decode the QByteArray correctly.
# Based on https://forum.qt.io/topic/85064/qbytearray-to-string/2
import ctypes
# CP_console = f"cp{ctypes.cdll.kernel32.GetConsoleOutputCP()}"


class gui(QtWidgets.QMainWindow):
    def __init__(self):
        super(gui, self).__init__()
        self.initUI()

    def dataReady(self):
        cursor = self.output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)

        # Here we have to decode the QByteArray
        cursor.insertText(f"GOT DATA: {self.process.readAll()}")
            # str(self.process.readAll().data().decode(CP_console)))
        self.output.ensureCursorVisible()

    def callProgram(self):
        # run the process
        # `start` takes the exec and a list of arguments
        # self.process.start('ping', ['127.0.0.1'])
        self.process.start('ls', ['-al'])

    def initUI(self):
        # Layout are better for placing widgets
        layout = QtWidgets.QVBoxLayout()
        self.runButton = QtWidgets.QPushButton('Run')
        self.runButton.clicked.connect(self.callProgram)

        self.output = QtWidgets.QTextEdit()

        layout.addWidget(self.output)
        layout.addWidget(self.runButton)

        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        # QProcess object for external app
        self.process = QtCore.QProcess(self)
        # QProcess emits `readyRead` when there is data to be read
        self.process.readyRead.connect(self.dataReady)

        # Just to prevent accidentally running multiple times
        # Disable the button when process starts, and enable it when it finishes
        self.process.started.connect(lambda: self.runButton.setEnabled(False))
        self.process.finished.connect(lambda: self.runButton.setEnabled(True))

# Function Main Start


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = gui()
    ui.show()
    sys.exit(app.exec())
# Function Main END


if __name__ == '__main__':
    main()