import datetime
import subprocess
import sys
import time

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
	QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget, QLineEdit, QLabel
)

MAX_RETRIES = 5
BASE_WAIT = 30  # seconds


class InstallerWorker(QThread):
	log_signal = pyqtSignal(str)
	finished_signal = pyqtSignal(bool)

	def __init__(self, version=None):
		super().__init__()
		self.version = version
		self._stop_requested = False

	def stop(self):
		self._stop_requested = True

	def log(self, message):
		timestamp = datetime.datetime.now().strftime("%H:%M:%S")
		self.log_signal.emit(f"[{timestamp}] {message}")

	def run(self):
		for attempt in range(1, MAX_RETRIES + 1):
			if self._stop_requested:
				self.log("🛑 Download cancelled.")
				self.finished_signal.emit(False)
				return

			cmd = ["softwareupdate", "--fetch-full-installer"]
			if self.version:
				cmd += ["--full-installer-version", self.version]

			self.log(f"Running: {' '.join(cmd)} (attempt {attempt})")
			try:
				result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
				self.log(result.stdout)
				if result.returncode == 0:
					self.log("✅ Download completed successfully.")
					self.finished_signal.emit(True)
					return
				else:
					self.log(f"❌ Failed with code {result.returncode}")
					self.log(result.stderr)
			except subprocess.TimeoutExpired:
				self.log("⏱️ Download timed out.")
			except Exception as e:
				self.log(f"⚠️ Exception: {e}")

			wait_time = BASE_WAIT * attempt
			self.log(f"Retrying in {wait_time} seconds...")
			time.sleep(wait_time)

		self.log("❌ All attempts failed.")
		self.finished_signal.emit(False)


class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("macOS Installer Downloader")
		self.worker = None

		# UI Elements
		self.log_output = QTextEdit()
		self.log_output.setReadOnly(True)

		self.version_input = QLineEdit()
		self.version_input.setPlaceholderText("Optional: macOS version (e.g. 15.0)")

		self.start_button = QPushButton("Start Download")
		self.stop_button = QPushButton("Cancel")
		self.stop_button.setEnabled(False)

		layout = QVBoxLayout()
		layout.addWidget(QLabel("macOS Full Installer Downloader"))
		layout.addWidget(self.version_input)
		layout.addWidget(self.start_button)
		layout.addWidget(self.stop_button)
		layout.addWidget(self.log_output)

		container = QWidget()
		container.setLayout(layout)
		self.setCentralWidget(container)

		# Signals
		self.start_button.clicked.connect(self.start_download)
		self.stop_button.clicked.connect(self.stop_download)

	def start_download(self):
		version = self.version_input.text().strip() or None
		self.worker = InstallerWorker(version)
		self.worker.log_signal.connect(self.append_log)
		self.worker.finished_signal.connect(self.download_finished)
		self.worker.start()

		self.start_button.setEnabled(False)
		self.stop_button.setEnabled(True)
		self.append_log("🚀 Starting download...")

	def stop_download(self):
		if self.worker:
			self.worker.stop()
		self.append_log("🛑 Cancelling download...")

	def download_finished(self, success):
		self.start_button.setEnabled(True)
		self.stop_button.setEnabled(False)
		if success:
			self.append_log("🎉 Installer is ready in /Applications.")
		else:
			self.append_log("⚠️ Download did not complete.")

	def append_log(self, message):
		self.log_output.append(message)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.resize(600, 400)
	window.show()
	sys.exit(app.exec())
