import sys

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QFileDialog, QLineEdit
from PySide6.QtCore import Qt, QObject, QThread, Signal, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox

from ...service.devices import list_v4l2_devices_linux


class VideoWorker(QObject):
    frame_ready = Signal(QImage)
    error = Signal(str)
    finished = Signal()

    def __init__(self, device_path):
        super().__init__()
        self.device_path = device_path
        self._running = False

    @Slot()
    def run(self):
        try:
            import cv2
        except Exception as e:
            self.error.emit(f"OpenCV (cv2) not available: {e}")
            self.finished.emit()
            return

        self._running = True

        # Simple pipeline (you can replace with your Jetson-friendly pipeline later)
        # If you already have a known-good gst pipeline string, use that instead.
        cap = cv2.VideoCapture(self.device_path)
        if not cap.isOpened():
            self.error.emit(f"Could not open camera: {self.device_path}")
            self.finished.emit()
            return

        while self._running:
            ok, frame = cap.read()
            if not ok:
                self.error.emit("Failed to read frame")
                break

            # TODO: Run Ultralytics here (later)
            # Example placeholder: keep raw frame

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
            self.frame_ready.emit(img)

        cap.release()
        self.finished.emit()

    def stop(self):
        self._running = False


class VideoPreviewWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Model Output")
        self.setMinimumSize(900, 600)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        layout = QVBoxLayout(self)
        self.video_label = QLabel("Waiting for video...")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setScaledContents(True)

        layout.addWidget(self.video_label, 1)

    @Slot(QImage)
    def on_frame(self, image):
        self.video_label.setPixmap(QPixmap.fromImage(image))


class RunModelPage(QWidget):
    def __init__(self, parent_main_window=None):
        super().__init__(parent_main_window)
        self._parent_main_window = parent_main_window

        self._thread = None
        self._worker = None
        self._preview = None

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Run Model")
        title.setObjectName("TitleLabel")

        row = QHBoxLayout()

        self.camera_combo = QComboBox()
        self.camera_combo.setMinimumWidth(420)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self._start)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._stop)

        row.addWidget(QLabel("Camera:"))
        row.addWidget(self.camera_combo, 1)
        row.addWidget(self.start_button)
        row.addWidget(self.stop_button)

        self.status = QLabel("Select a camera and press Start.")
        self.status.setStyleSheet("color: #9ca3af;")

        layout.addWidget(title)
        layout.addLayout(row)
        layout.addWidget(self.status)
        layout.addStretch(1)

        self._load_cameras()
        model_row = QHBoxLayout()

        self.model_path_edit = QLineEdit()
        self.model_path_edit.setReadOnly(True)
        self.model_path_edit.setPlaceholderText("Select a model file (.engine / .pt / .pth / .onnx)...")

        self.browse_model_button = QPushButton("Browse model")
        self.browse_model_button.clicked.connect(self._browse_model)

        self.clear_model_button = QPushButton("Clear")
        self.clear_model_button.clicked.connect(self._clear_model)

        model_row.addWidget(QLabel("Model:"))
        model_row.addWidget(self.model_path_edit, 1)
        model_row.addWidget(self.browse_model_button)
        model_row.addWidget(self.clear_model_button)

        layout.addLayout(row)        # camera row
        layout.addLayout(model_row)  # model row
        self._load_saved_model()

    def _load_cameras(self):
        self.camera_combo.clear()

        if sys.platform.startswith("linux"):
            devices = list_v4l2_devices_linux()  # [("/dev/video0", "Name"), ...]
            if not devices:
                self.camera_combo.addItem("No cameras found", None)
                return

            for path, label in devices:
                self.camera_combo.addItem(f"{label} ({path})", path)
        else:
            self.camera_combo.addItem("Camera listing not implemented for this OS yet", None)

    def _ensure_preview_window(self):
        if self._preview is not None:
            return

        # Make it a child of the main window so it closes when main closes
        self._preview = VideoPreviewWindow(parent=self._parent_main_window)
        self._preview.setWindowFlag(Qt.Window, True)
        self._preview.show()

    def _start(self):
        device_path = self.camera_combo.currentData()
        model_path = self.model_path_edit.text().strip()

        if not device_path:
            self.status.setText("No camera selected.")
            return

        if not model_path:
            self.status.setText("No model selected.")
            return

        # TODO: use model_path later when you load Ultralytics / TensorRT
    

        self._ensure_preview_window()

        self._thread = QThread()
        self._worker = VideoWorker(device_path)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        
        self._worker.frame_ready.connect(self._preview.on_frame)
        self._worker.error.connect(self._on_error)
        
        self._worker.finished.connect(self._on_finished)
        self._worker.finished.connect(self._thread.quit)
        
        self._thread.finished.connect(self._on_thread_finished)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status.setText(f"Running on {device_path} ...")

    def _stop(self):
        if self._worker is not None:
            self._worker.stop()
        self.status.setText("Stopping...")

    def _on_error(self, message):
        self.status.setText(f"Error: {message}")

    def _on_finished(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status.setText("Stopped.")
        # Leave preview window open; closing main will close it anyway.
    def _on_thread_finished(self):
        self._thread = None
        self._worker = None
    def stop_and_wait(self):
        if self._worker:
            self._worker.stop()
        if self._thread:
            self._thread.quit()
            self._thread.wait(2000)

    def _settings(self):
        return QSettings()

    def _load_saved_model(self):
        saved = self._settings().value("model_path", "", str)
        if saved:
            self.model_path_edit.setText(saved)

    def _save_model_path(self, path):
        self._settings().setValue("model_path", path)

    def _browse_model(self):
        file_filter = "Model files (*.engine *.pt *.pth *.onnx);;All files (*)"
        path, _ = QFileDialog.getOpenFileName(self, "Select model file", "", file_filter)
        if not path:
            return
        self.model_path_edit.setText(path)
        self._save_model_path(path)

    def _clear_model(self):
        self.model_path_edit.clear()
        self._save_model_path("")
