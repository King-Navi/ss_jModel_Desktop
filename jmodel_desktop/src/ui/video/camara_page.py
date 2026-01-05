import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QFormLayout,
    QComboBox,
)
from .devices import list_v4l2_devices_linux
from PySide6.QtMultimedia import QMediaDevices

class CameraPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Camera")
        title.setObjectName("TitleLabel")

        row = QHBoxLayout()
        self.camera_combo = QComboBox()
        self.camera_combo.setPlaceholderText("Select a camera...")
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._refresh_devices)

        row.addWidget(self.camera_combo, 1)
        row.addWidget(self.refresh_button)

        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlaceholderText("Camera info will appear here...")

        self.camera_combo.currentIndexChanged.connect(self._on_camera_selected)

        layout.addWidget(title)
        layout.addLayout(row)
        layout.addWidget(self.details, 1)

        self._refresh_devices()

    def _refresh_devices(self):
        self.camera_combo.blockSignals(True)
        self.camera_combo.clear()

        qt_devices = QMediaDevices.videoInputs()
        if qt_devices:
            for dev in qt_devices:
                self.camera_combo.addItem(dev.description(), dev)
        else:
            self.camera_combo.addItem("No cameras found (Qt)", None)
            self.camera_combo.setCurrentIndex(0)

        self.camera_combo.blockSignals(False)

        self.details.clear()
        self.details.append("== Qt videoInputs() ==")
        if qt_devices:
            for i, dev in enumerate(qt_devices, start=1):
                self.details.append(f"{i}. {dev.description()}")
        else:
            self.details.append("(none)")

        self.details.append("\n== Linux /dev/video* (v4l2 sysfs) ==")
        if sys.platform.startswith("linux"):
            v4l2 = list_v4l2_devices_linux()
            if v4l2:
                for path, label in v4l2:
                    self.details.append(f"- {path}: {label}")
            else:
                self.details.append("(none found in /sys/class/video4linux)")
        else:
            self.details.append("(not linux)")

        self._on_camera_selected()

    def _on_camera_selected(self):
        dev = self.camera_combo.currentData()
        if dev is None:
            return
        self.details.append(f"\nSelected: {dev.description()}")