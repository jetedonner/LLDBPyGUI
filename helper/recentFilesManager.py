import os

from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QAction, QCursor
from PyQt6.QtWidgets import QToolTip


# from PyQt6.QtCore import QSettings
class RecentFilesManagerNG:
	settings = QSettings("./recent_files.ini", QSettings.Format.IniFormat)
	parentMenu = None

	def checkRemovePath(self, file_path):
		if "/" in file_path:
			filename = file_path.rsplit("/", 1)[-1]
		else:
			filename = file_path
		return filename

	def save_recent_file(self, file_path):
		recent_files = self.settings.value("recentFiles", [])
		filename_only = file_path  # self.checkRemovePath(file_path)
		if filename_only in recent_files:
			recent_files.remove(filename_only)
		recent_files.insert(0, filename_only)
		recent_files = recent_files[:5]  # Limit to 5 entries
		self.settings.setValue("recentFiles", recent_files)

	# from PyQt6.QtWidgets import QMenu, QAction

	def populate_recent_files_menu(self, menu, open_callback):
		menu.clear()
		recent_files = self.settings.value("recentFiles", [])
		# return recent_files
		print(f"recent_files: {recent_files} ...")
		if recent_files:
			for file_path in recent_files:
				file_name = os.path.basename(file_path)
				action = QAction(file_name, menu)
				action.triggered.connect(lambda checked, path=file_path: open_callback(path))
				action.setToolTip(file_path)
				# Connect hovered signal to show tooltip manually
				# for action in [action1, action2]:
				action.hovered.connect(lambda a=action: QToolTip.showText(QCursor.pos(), a.toolTip()))
				action.setStatusTip(f"Load {file_path} ...")
				menu.addAction(action)
			menu.addSeparator()
			clear_recent_action = QAction("Clear recent list", menu)
			clear_recent_action.triggered.connect(self.handle_clear_recent)
			menu.addAction(clear_recent_action)
		else:
			menu.addAction(QAction("No recent files", menu)).setEnabled(False)

	def handle_clear_recent(self):
		self.parentMenu.clear()
		self.parentMenu.addSeparator()
		clear_recent_action = QAction("Clear recent list", self.parentMenu)
		clear_recent_action.triggered.connect(self.handle_clear_recent)
		self.parentMenu.addAction(clear_recent_action)

# class RecentFilesManager:
#
#     # setHelper = None
#     recentFilesSettingsFile = QSettings(ConfigClass.recentFilesFilename, QSettings.Format.IniFormat)
#
#     def __init__(self):
#         super().__init__()
#         # self.setHelper = SettingsHelper()
#         # settings = QSettings(ConfigClass.recentFilesFilename, QSettings.Format.IniFormat)
#
#     def getAllRecentFiles(self):
#         arrRecentFiles = []
#         nCntRecentFiles = self.beginReadArray("recentFiles")
#         for i in range(nCntRecentFiles):
#             arrRecentFiles.append(self.getArrayValue(f"recentFile_{i}"))
#         self.endArray()
#         return arrRecentFiles
#
#     def beginWriteArray(self, prefix):
#         self.recentFilesSettingsFile.beginWriteArray(prefix)
#
#     def beginReadArray(self, prefix):
#         return self.recentFilesSettingsFile.beginReadArray(prefix)
#
#     def setArrayValue(self, setting, value):
#         self.recentFilesSettingsFile.setValue(setting, value)
#
#     def getArrayValue(self, setting):
#         return self.recentFilesSettingsFile.value(setting)
#
#     # def getArrayChecked(self, setting):
#     #     return Qt.CheckState.Checked if self.settings.value(setting) == "true" else Qt.CheckState.Unchecked
#
#     def endArray(self):
#         self.recentFilesSettingsFile.endArray()
