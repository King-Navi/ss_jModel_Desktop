import sys
import time

from PySide6.QtCore import Qt, Signal, QObject, QThread
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow

from ultralytics import YOLO


# ===== Constantes (antes las importabas de constant) =====
OUR_MODEL_ENGINE = "path/a/tu_modelo.engine"   # <-- cambia esto
CONF = 0.25
IMGSZ = 640
SOURCE = 0  # webcam: 0, 1, 2...


def bgr_to_qpixmap(frame_bgr):
    # Ultralytics/plot devuelve BGR (tipo OpenCV)
    # Qt necesita RGB
    import cv2  # import local para que este archivo funcione aunque no uses cv2 directo arriba

    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    h, w, ch = frame_rgb.shape
    bytes_per_line = ch * w
    qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(qimg.copy())  # copy() para evitar referencias a memoria temporal


class PredictWorker(QObject):
    frame_ready = Signal(QPixmap, float)  # pixmap, fps
    error = Signal(str)
    finished = Signal()

    def __init__(self, engine_path: str, source: int, imgsz: int, conf: float):
        super().__init__()
        self.engine_path = engine_path
        self.source = source
        self.imgsz = imgsz
        self.conf = conf
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        try:
            model = YOLO(self.engine_path)

            # stream=True => iterador que va entregando Results
            stream = model.predict(
                source=self.source,
                stream=True,
                imgsz=self.imgsz,
                conf=self.conf,
                verbose=False,
            )

            prev_time = 0.0

            for results in stream:
                if not self._running:
                    break

                # results es un objeto Results (para 1 frame)
                annotated = results.plot()  # numpy BGR

                now = time.time()
                fps = 1.0 / (now - prev_time) if prev_time else 0.0
                prev_time = now

                pixmap = bgr_to_qpixmap(annotated)
                self.frame_ready.emit(pixmap, fps)

        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLO - PySide6 (Ultralytics predict source=0)")

        self.label = QLabel("Iniciando...")
        self.label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.label)

        self._last_pixmap = None

        self.thread = QThread(self)
        self.worker = PredictWorker(
            engine_path=OUR_MODEL_ENGINE,
            source=SOURCE,
            imgsz=IMGSZ,
            conf=CONF,
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

        # título con FPS
        self.setWindowTitle(f"YOLO - PySide6 (predict) | FPS: {fps:.1f}")

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
