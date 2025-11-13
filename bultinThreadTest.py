import sys
import threading
import queue
import time

import lldb
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import QTimer

# Create LLDB debugger and listener
debugger = lldb.SBDebugger.Create()
debugger.SetAsync(True)
target = debugger.CreateTarget("_testtarget/hello_library_exec2")  # Replace with your binary path
listener = debugger.GetListener()

# Launch process with listener
error = lldb.SBError()
li = lldb.SBLaunchInfo(None)
li.SetLaunchFlags(lldb.eLaunchFlagStopAtEntry)
# li.SetListener(listener)
process = target.Launch(li, error) # listener, [], [], sys.stdin, sys.stdout, sys.stderr, "", 0, True, error)
print(f"Process launched: {process} => error: {error}")

# Event queue for cross-thread communication
event_queue = queue.Queue()

# Background thread to listen for LLDB events
def lldb_event_thread(listener, event_queue):
    while True:
        event = lldb.SBEvent()
        if listener.WaitForEvent(1, event):
            event_queue.put(event)

threading.Thread(target=lldb_event_thread, args=(listener, event_queue), daemon=True).start()

# PyQt6 GUI
class LLDBEventViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel("Waiting for LLDB events...")
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.btn = QPushButton("Send event")
        self.btn.clicked.connect(self.handle_btn_clicked)
        layout.addWidget(self.btn)
        self.setLayout(layout)

        # Timer to poll event queue
        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_events)
        self.timer.start(100)

    bStop = False
    def handle_btn_clicked(self):
        if not self.bStop:
            target.GetProcess().Continue()
        else:
            target.GetProcess().Stop()
        self.bStop = not self.bStop

        pass

    def poll_events(self):
        while not event_queue.empty():
            event = event_queue.get()
            self.handle_event(event)

    def handle_event(self, event):
        if lldb.SBProcess.EventIsProcessEvent(event):
            state = lldb.SBProcess.GetStateFromEvent(event)
            # state_str = lldb.SBDebugger.StateAsCString(state)
            # self.label.setText(f"Process state changed: {state_str}")
            if event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
                process = lldb.SBProcess.GetProcessFromEvent(event)
                thread = process.GetSelectedThread()
                frame = thread.GetSelectedFrame()
                pc_address = frame.GetPC()  # This returns the program counter as an integer

                mystr = self.readSTDOUT(process)
                self.label.setText(f"Process output: {mystr}")
                print(f"mystr: {mystr} ...")
                # time.sleep(3)
            else:
                state_str = lldb.SBDebugger.StateAsCString(state)
                self.label.setText(f"Process state changed: {state_str}")

    def readSTDOUT(self, proc):
        # QApplication.processEvents()
        # proc.GetTarget().debugger.SetAsync(False)
        # QApplication.processEvents()
        stdout = proc.GetSTDOUT(1024)
        # print(f"proc.GetSTDOUT(1024): {stdout}")
        result_string = ""
        if stdout is not None and len(stdout) > 0:
            # print(stdout)
            message = {"status": "event", "type": "stdout", "output": "".join(["%02x" % ord(i) for i in stdout])}
            print(message)
            print(f"message: {message}")
            byte_values = bytes.fromhex("".join(["%02x" % ord(i) for i in stdout]))
            print(f"byte_values: {byte_values}")
            result_string = byte_values.decode('utf-8')
            print(f"result_string: {result_string}")
            # logDbg(f"Reading STDOUT after Event: {result_string}")
        # proc.GetTarget().debugger.SetAsync(True)
        # QApplication.processEvents()
        return result_string

def startTest():
    app = QApplication(sys.argv)
    viewer = LLDBEventViewer()
    viewer.setWindowTitle("LLDB Event Viewer")
    viewer.resize(400, 100)
    viewer.show()
    sys.exit(app.exec())