# gui_launcher.py
import socket
import sys
import time

from PyQt6.QtCore import QThread, QObject
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow


class MySocketListener(QObject):
	labelTarget = None
	abort = False

	def __init__(self, labelTarget):
		super().__init__()

		self.labelTarget = labelTarget
		self.abort = False
	# def start_socket_listener(self):
	# 	def listen():
	# 		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	# 			s.bind(("localhost", 5689))
	# 			s.listen()
	# 			conn, _ = s.accept()
	# 			with conn:
	# 				data = conn.recv(1024)
	# 				if data:
	# 					self.labelTarget.setText(data.decode())
	# 					print(f"Received: {data.decode()} ...")
	# 					QTimer.singleShot(100, listen)
	#
	# 	QTimer.singleShot(100, listen)

	def start_socket_listener(self):
		self.abort = False

		def listen():
			if self.abort:
				print("Socket listener aborted.")
				return

			try:
				with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
					s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
					s.bind(("localhost", 5689))
					s.listen()
					while not self.abort:
						try:
							conn, _ = s.accept()
							with conn:
								while not self.abort:
									data = conn.recv(1024)
									if not data:
										break
									self.labelTarget.setText(data.decode())
									print(f"Received: {data.decode()} ...")
									conn.sendall(b"ACK")  # Optional response
						except socket.timeout:
							continue
			except Exception as e:
				print(f"Socket error: {e}")

			QTimer.singleShot(100, listen)

		QTimer.singleShot(100, listen)

	# def start_socket_listener(self):
	# 	self.abort = False  # Add this as an instance variable
	# 	def listen():
	# 		if self.abort:
	# 			print("Socket listener aborted.")
	# 			return
	#
	# 		try:
	# 			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	# 				s.settimeout(1.0)  # Avoid blocking forever
	# 				s.bind(("localhost", 5689))
	# 				s.listen()
	# 				conn, _ = s.accept()
	# 				with conn:
	# 					while not self.abort:
	# 						try:
	# 							data = conn.recv(1024)
	# 							if data:
	# 								self.labelTarget.setText(data.decode())
	# 								print(f"Received: {data.decode()} ...")
	# 								time.sleep(0.5)
	# 								conn.sendall(b"ACK")
	# 						except socket.timeout:
	# 							pass  # No data yet, continue loop
	# 		except Exception as e:
	# 			print(f"Socket error: {e}")
	# 		# Schedule next check
	# 		QTimer.singleShot(100, listen)
	# 	QTimer.singleShot(100, listen)


class MyWin(QMainWindow):
	thread = None

	def __init__(self, thread):
		super().__init__()

		self.thread = thread

	def notify_quit(self):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect(("localhost", 6000))  # LLDB listener
			s.sendall(b"QUIT")

	def closeEvent(self, event):
		# self.notify_quit()
		global bIsActive
		bIsActive = False
		if self.thread.isRunning():
			self.thread.terminate()
		# time.sleep(1)
		# self.thread.wait()


class MyGUI:
	app = None
	window = None
	label = None

	listener = None
	thread = None

	def notify_ready(self):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect(("localhost", 6000))  # LLDB listener
			s.sendall(b"READY")

	def start_gui(self):
		self.thread = QThread()

		self.app = QApplication(sys.argv)
		self.window = MyWin(self.thread)
		self.label = QLabel("Waiting for data...", self.window)
		self.window.setCentralWidget(self.label)

		self.listener = MySocketListener(self.label)
		self.listener.moveToThread(self.thread)
		self.thread.started.connect(self.listener.start_socket_listener)

		self.window.show()
		self.thread.start()
		self.notify_ready()
		self.app.exec()


if __name__ == "__main__":
	MyGUI().start_gui()

# app = QApplication(sys.argv)
# window = QMainWindow()
# label = QLabel("Hello from LLDB!", window)
# window.setCentralWidget(label)
# start_socket_listener(label)
# window.show()
# app.exec()
#
# # import sys
#
# for line in sys.stdin:
#     print(f"Received: {line.strip()}")
#     # You can trigger GUI updates here
