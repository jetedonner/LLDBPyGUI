from PyQt6.QtWidgets import (
	QWidget, QLabel, QHBoxLayout
)

from config import ConfigClass
from ui.customQt.QClickLabel import QClickLabel


class CustomDockViewTitleBar(QWidget):

	# def __init__(self, title):
	#     super().__init__()
	#     layout = QHBoxLayout()
	#     layout.setContentsMargins(5, 5, 5, 5)  # Optional: tweak spacing
	#     label = QLabel(title)
	#     label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
	#     layout.addWidget(label)
	#     layout.addStretch()  # Pushes label to the left
	#     self.setLayout(layout)

	def __init__(self, dock_widget, title):
		super().__init__()
		self.dock = dock_widget
		layout = QHBoxLayout()
		layout.setContentsMargins(5, 0, 0, 0)

		label = QLabel(title)
		# toggle_btn = QPushButton("X")  # or "+" when collapsed
		# toggle_btn.setFont(ConfigClass.font12)

		self.toggle_btn = QClickLabel(self)
		self.toggle_btn.setContentsMargins(0, 0, 5, 0)
		self.toggle_btn.setToolTip(f"Close '{title}' panel ...")
		self.toggle_btn.setStatusTip(f"Close '{title}' panel ...")
		self.toggle_btn.setPixmap(
			ConfigClass.pixClose)  # .scaled(QSize(18, 18), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

		# self.image_modules_label.clicked.connect(toggle)

		def toggle():
			self.dock.setVisible(not self.dock.isVisible())
			# is_visible = self.dock.widget().isVisible()
			# self.dock.widget().setVisible(not is_visible)
			# toggle_btn.setText("+" if not is_visible else "−")

		self.toggle_btn.clicked.connect(toggle)

		layout.addWidget(label)
		layout.addStretch()
		layout.addWidget(self.toggle_btn)
		self.setLayout(layout)

# class CollapsibleTitleBar(QWidget):
#     def __init__(self, dock_widget, title):
#         super().__init__()
#         self.dock = dock_widget
#         layout = QHBoxLayout()
#         layout.setContentsMargins(5, 0, 0, 0)
#
#         label = QLabel(title)
#         toggle_btn = QPushButton("−")  # or "+" when collapsed
#
#         def toggle():
#             is_visible = self.dock.widget().isVisible()
#             self.dock.widget().setVisible(not is_visible)
#             toggle_btn.setText("+" if not is_visible else "−")
#
#         toggle_btn.clicked.connect(toggle)
#
#         layout.addWidget(label)
#         layout.addStretch()
#         layout.addWidget(toggle_btn)
#         self.setLayout(layout)
