import sys
import time
import cv2

from PySide6.QtCore import Qt, Signal, QObject, QThread
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow

from ultralytics import YOLO


# ===== Constantes =====
MODEL_PATH_ENGINE = "path/a/tu_modelo.engine"  # <-- cambia esto

DEVICE = "/dev/video0"
WIDTH = 640
HEIGHT = 480
FPS_TARGET = 30


def bgr_to_qpixmap(frame_bgr):
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    h, w, ch = frame_rgb.shape
    bytes_per_line = ch * w
    qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(qimg.copy())


class CameraWorker(QObject):
    frame_ready = Signal(QPixmap, float)  # pixmap, fps
    error = Signal(str)
    finished = Signal()

    def __init__(self, engine_path: str, device: str, width: int, height: int, fps: int):
        super().__init__()
        self.engine_path = engine_path
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        # MJPEG pipeline (como tu ejemplo)
        gst_str = (
            f"v4l2src device={self.device} ! "
            f"image/jpeg, width={self.width}, height={self.height}, framerate={self.fps}/1 ! "
            "jpegdec ! "
            "videoconvert ! "
            "appsink drop=1"
        )

        cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)
        if not cap.isOpened():
            self.error.emit("Error: no se pudo abrir la camara con GStreamer (¿OpenCV con GStreamer instalado?)")
            self.finished.emit()
            return

        try:
            model = YOLO(self.engine_path)
            prev_time = 0.0

            while self._running:
                ret, frame = cap.read()
                if not ret:
                    self.error.emit("No se pudo leer frame de la camara")
                    break

                results = model(frame, verbose=False)[0]
                annotated = results.plot()

                now = time.time()
                fps_val = 1.0 / (now - prev_time) if prev_time else 0.0
                prev_time = now

                cv2.putText(
                    annotated,
                    f"FPS: {fps_val:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 255, 0),
                    2,
                )

                pixmap = bgr_to_qpixmap(annotated)
                self.frame_ready.emit(pixmap, fps_val)

        except Exception as e:
            self.error.emit(str(e))
        finally:
            cap.release()
            self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLO - PySide6 (GStreamer)")

        self.label = QLabel("Iniciando cámara...")
        self.label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.label)

        self._last_pixmap = None

        self.thread = QThread(self)
        self.worker = CameraWorker(
            engine_path=MODEL_PATH_ENGINE,
            device=DEVICE,
            width=WIDTH,
            height=HEIGHT,
            fps=FPS_TARGET,
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.frame_ready.connect(self.on_frame)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_frame(self, pixmap: QPixmap, fps: float):
        self._last_pixmap = pixmap
        self._render()
        self.setWindowTitle(f"YOLO - PySide6 (GStreamer) | FPS: {fps:.1f}")

    def _render(self):
        if not self._last_pixmap:
            return
        scaled = self._last_pixmap.scaled(
            self.label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.label.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._render()

    def on_error(self, msg: str):
        self.label.setText(f"Error:\n{msg}")

    def closeEvent(self, event):
        if hasattr(self, "worker") and self.worker:
            self.worker.stop()
        if hasattr(self, "thread") and self.thread:
            self.thread.quit()
            self.thread.wait(1500)
        event.accept()


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(960, 540)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
