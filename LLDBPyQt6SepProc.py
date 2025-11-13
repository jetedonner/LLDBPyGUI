import os
import subprocess
import time

import lldb

from gui_launcher import MyGUI

APP_NAME = "LLDBPyQt6SepProc"
PROMPT_TEXT = "LLDBPyQt6SepProc"

import multiprocessing

multiprocessing.set_start_method("spawn", force=True)
bIsActive = False

def __lldb_init_module(debugger, internal_dict):
    # don't load if we are in Xcode since it is not compatible and will block Xcode
    if os.getenv('PATH').startswith('/Applications/Xcode'):
        return

    res = lldb.SBCommandReturnObject()
    ci = debugger.GetCommandInterpreter()

    ci.HandleCommand(f'settings set prompt \"({PROMPT_TEXT}) \"', res)
    ci.HandleCommand(
        f"command script add -h '({PROMPT_TEXT}) Start the {APP_NAME}.' -f LLDBPyQt6SepProc.startLLDBPyQtTest pqt",
        res)


# def gui_process(queue):
#     from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
#     import sys
#
#     app = QApplication(sys.argv)
#     window = QMainWindow()
#     label = QLabel("Waiting for data...", window)
#     window.setCentralWidget(label)
#     window.show()
#
#     def check_queue():
#         if not queue.empty():
#             msg = queue.get()
#             label.setText(f"Received: {msg}")
#         QTimer.singleShot(100, check_queue)
#
#     from PyQt6.QtCore import QTimer
#     QTimer.singleShot(100, check_queue)
#     app.exec()

import socket


def wait_for_ack(s):
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.bind(("localhost", 6000))
    s.listen()
    conn, _ = s.accept()
    print(f"IN ACK => conn: {conn} ...")
    with conn:
        msg = conn.recv(1024)
        return msg.decode() == "ACK"

def wait_for_ready():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 6000))
        s.listen()
        conn, _ = s.accept()
        with conn:
            msg = conn.recv(1024)
            return msg.decode() == "READY"

def wait_for_quit():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 6000))
        s.listen()
        conn, _ = s.accept()
        with conn:
            msg = conn.recv(1024)
            return msg.decode() == "QUIT"


def send_to_gui(msg):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 5689))
        s.sendall(msg.encode())


def startLLDBPyQtTest(debugger, command, result, dict):
    from datetime import datetime
    global bIsActive
    # print(f"before gui start ...")
    # MyGUI().start_gui()
    # print(f"after gui start ...")
    # time.sleep(5)
    # now = datetime.now()
    # swiss_dt = now.strftime("%A, %d. %B %Y, %H:%M:%S Uhr")
    #
    # send_to_gui(f"Es ist:\n{swiss_dt} ...")



    # # gui_script_path = "/Volumes/Data/dev/python/LLDBGUI/gui_launcher.py"
    # # subprocess.Popen([sys.executable, gui_script_path])
    # # subprocess.Popen(["python3", "/Volumes/Data/dev/python/LLDBGUI/gui_launcher.py"])
    proc = subprocess.Popen(
        ["python3", "/Volumes/Data/dev/python/LLDBGUI/gui_launcher.py"]) #,
        # stdin=subprocess.PIPE,
        # text=True
    # )
    if wait_for_ready():
        time.sleep(0.5)
        startSocketServer()
    #     bIsActive = True
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #         s.connect(("localhost", 5689))  # GUI listener
    #         while bIsActive:
    #             now = datetime.now()
    #             swiss_dt = now.strftime("%A, %d. %B %Y, %H:%M:%S Uhr")
    #             byte_data = swiss_dt.encode('utf-8')
    #             try:
    #                 s.sendall(byte_data) # b"Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! ....")
    #                 time.sleep(1)
    #             except Exception as e:
    #                 bIsActive = False
    #                 s.shutdown(socket.SHUT_RDWR)
    #                 s.close()
    #                 break
    #                 # print(f"ERROR: {e} ...")
    #             # wait_for_quit()
    # # # send_to_gui("HELLO FROM LLDBGUI")
    # # # proc.stdin.write("Hello from LLDB\n")
    # # # proc.stdin.flush()

def startSocketServer():
    from datetime import datetime
    global bIsActive
    bIsActive = True
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 5689))  # GUI listener
        while bIsActive:
            now = datetime.now()
            swiss_dt = now.strftime("%A, %d. %B %Y, %H:%M:%S Uhr")
            byte_data = swiss_dt.encode('utf-8')
            try:
                s.sendall(
                    byte_data)  # b"Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! Hello from LLDB WITH SUBPROC! ....")
                wait_for_ack(s)
                time.sleep(1)
            except Exception as e:
                bIsActive = False
                # s.shutdown(socket.SHUT_RDWR)
                # s.close()
                return
        s.shutdown(socket.SHUT_RDWR)
        s.close()