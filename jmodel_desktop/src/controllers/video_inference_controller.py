from PySide6.QtCore import QObject, Signal, Slot, QThread, Qt, QEvent
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel

import threading
import time
import numpy as np
import cv2
from ultralytics import YOLO

class SharedFrame:
    def __init__(self):
        self._lock = threading.Lock()
        self._frame = None

    def set(self, frame):
        with self._lock:
            self._frame = frame

    def get_copy(self):
        with self._lock:
            if self._frame is None:
                return None
            return self._frame.copy()

class CaptureWorker(QObject):
    video_qimage = Signal(object)  # QImage
    error = Signal(str)
    finished = Signal()

    def __init__(self, capture_source, shared: SharedFrame, use_gstreamer=True, ui_fps=15, parent=None):
        super().__init__(parent)
        self.capture_source = capture_source
        self.shared = shared
        self.use_gstreamer = use_gstreamer
        self.ui_period = 1.0 / float(ui_fps)
        self._running = False

    @Slot()
    def run(self):

        cap = cv2.VideoCapture(self.capture_source, cv2.CAP_GSTREAMER if self.use_gstreamer else 0)
        if not cap.isOpened():
            self.error.emit("Could not open video capture source.")
            self.finished.emit()
            return

        self._running = True
        last_emit = 0.0
        fail_count = 0

        while self._running:
            ok, frame = cap.read()
            if not ok or frame is None:
                fail_count += 1
                time.sleep(0.01)  # evita busy loop
                if fail_count > 100:
                    self.error.emit("Capture stalled (too many read failures).")
                    break
                continue

            fail_count = 0
            self.shared.set(frame)

            now = time.monotonic()
            if (now - last_emit) >= self.ui_period:
                frame = np.ascontiguousarray(frame)
                h, w = frame.shape[:2]
                qimg = QImage(frame.data, w, h, frame.strides[0], QImage.Format_BGR888).copy()
                self.video_qimage.emit(qimg)
                last_emit = now

        cap.release()
        self.finished.emit()

    def stop(self):
        self._running = False


class InferenceWorker(QObject):
    infer_qimage = Signal(object)  # QImage
    error = Signal(str)
    finished = Signal()

    def __init__(self, model_path, shared: SharedFrame, infer_fps=6, parent=None):
        super().__init__(parent)
        self.model_path = model_path
        self.shared = shared
        self.infer_period = 1.0 / float(infer_fps)
        self._running = False

    @Slot()
    def run(self):

        model = YOLO(self.model_path, task="detect")
        try:
            dummy = np.zeros((640, 640, 3), dtype=np.uint8)
            _ = model.predict(dummy, verbose=False)
        except Exception as e:
            self.error.emit(f"Model not usable (engine/TRT mismatch): {e}")
            self.finished.emit()
            return
        self._running = True
        last_infer = 0.0

        while self._running:
            now = time.monotonic()
            if (now - last_infer) < self.infer_period:
                time.sleep(0.005)
                continue

            frame = self.shared.get_copy()
            if frame is None:
                time.sleep(0.01)
                continue

            last_infer = now

            try:
                import cv2
                small = cv2.resize(frame, (640, 640), interpolation=cv2.INTER_LINEAR)
                results = model.predict(small, verbose=False)
                
                annotated = results[0].plot()  # numpy BGR
                annotated = np.ascontiguousarray(annotated)
                h, w = annotated.shape[:2]
                qimg = QImage(annotated.data, w, h, annotated.strides[0], QImage.Format_BGR888).copy()
                self.infer_qimage.emit(qimg)
            except Exception as e:
                self.error.emit(f"Inference error: {e}")
                break

        self.finished.emit()

    def stop(self):
        self._running = False

class VideoInferenceController(QObject):
    def __init__(self, window, model_path, device_path, width=1280, height=720, fps=30, parent=None):
        super().__init__(parent)
        self.window = window
        self.model_path = model_path
        self.device_path = device_path
        self.width = width
        self.height = height
        self.fps = fps

        self._resolve_widgets()
        self.window.installEventFilter(self)

        # Reduce trabajo por frame
        self.label_video.setScaledContents(True)
        self.label_inference.setScaledContents(True)

        self._shared = SharedFrame()

        self._capture_thread = None
        self._infer_thread = None
        self._capture_worker = None
        self._infer_worker = None

        self._start()

    def _require(self, widget_type, object_name):
        w = self.window.findChild(widget_type, object_name)
        if w is None:
            raise RuntimeError(f"Widget not found: {object_name} ({widget_type.__name__})")
        return w

    def _resolve_widgets(self):
        self.label_video = self._require(QLabel, "label_video")
        self.label_inference = self._require(QLabel, "label_inference")

    def _build_gstreamer_pipeline_mjpeg(self):
        return (
            f"v4l2src device={self.device_path} io-mode=2 ! "
            f"image/jpeg,width={self.width},height={self.height},framerate={self.fps}/1 ! "
            "jpegdec ! videoconvert ! "
            "queue leaky=downstream max-size-buffers=1 ! "
            "appsink max-buffers=1 drop=true sync=false"
        )

    def _start(self):
        pipeline = self._build_gstreamer_pipeline_mjpeg()

        # Capture thread
        self._capture_thread = QThread(self.window)
        self._capture_worker = CaptureWorker(
            capture_source=pipeline,
            shared=self._shared,
            use_gstreamer=True,
            ui_fps=15,
        )
        self._capture_worker.moveToThread(self._capture_thread)
        self._capture_thread.started.connect(self._capture_worker.run)
        self._capture_worker.video_qimage.connect(self._on_video_qimage)
        self._capture_worker.error.connect(self._on_error)

        # Inference thread
        self._infer_thread = QThread(self.window)
        self._infer_worker = InferenceWorker(
            model_path=self.model_path,
            shared=self._shared,
            infer_fps=6,
        )
        self._infer_worker.moveToThread(self._infer_thread)
        self._infer_thread.started.connect(self._infer_worker.run)
        self._infer_worker.infer_qimage.connect(self._on_infer_qimage)
        self._infer_worker.error.connect(self._on_error)

        # Cleanup
        self._capture_worker.finished.connect(self._capture_thread.quit)
        self._capture_worker.finished.connect(self._capture_worker.deleteLater)
        self._capture_thread.finished.connect(self._capture_thread.deleteLater)

        self._infer_worker.finished.connect(self._infer_thread.quit)
        self._infer_worker.finished.connect(self._infer_worker.deleteLater)
        self._infer_thread.finished.connect(self._infer_thread.deleteLater)

        self._capture_thread.start()
        self._infer_thread.start()

    def stop(self):
        if self._capture_worker:
            self._capture_worker.stop()
        if self._infer_worker:
            self._infer_worker.stop()

        if self._capture_thread:
            self._capture_thread.quit()
            self._capture_thread.wait(1500)

        if self._infer_thread:
            self._infer_thread.quit()
            self._infer_thread.wait(1500)

    def eventFilter(self, watched, event):
        if watched == self.window and event.type() == QEvent.Close:
            self.stop()
        return super().eventFilter(watched, event)

    def _on_video_qimage(self, qimg):
        self.label_video.setPixmap(QPixmap.fromImage(qimg))

    def _on_infer_qimage(self, qimg):
        self.label_inference.setPixmap(QPixmap.fromImage(qimg))

    def _on_error(self, msg: str):
        print("[VideoInference] ERROR:", msg)
        self.stop()