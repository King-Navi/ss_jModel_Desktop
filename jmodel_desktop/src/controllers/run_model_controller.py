from PySide6.QtCore import QObject
from PySide6.QtWidgets import QComboBox, QPushButton, QRadioButton, QTextEdit

from ..service.models import listar_modelos_desde_env
from ..service.devices import list_v4l2_devices_linux

class RunModelController(QObject):
    def __init__(self, window):
        super().__init__()
        self.window = window

        self._resolve_widgets()
        self._wire_signals()
        self._init_ui_state()

    # ---------- Widget lookup ----------
    def _require(self, widget_type, object_name: str):
        widget = self.window.findChild(widget_type, object_name)
        if widget is None:
            raise RuntimeError(f"Widget not found: {object_name} ({widget_type.__name__})")
        return widget

    def _resolve_widgets(self):
        # Buttons
        self.btn_ultralytics = self._require(QPushButton, "pushButton_utralytics")  # UI name as-is
        self.btn_gstream = self._require(QPushButton, "pushButton_gstream")
        self.btn_opencv = self._require(QPushButton, "pushButton_opencv")

        # Radios
        self.radio_local = self._require(QRadioButton, "radioButton_local")
        self.radio_remote = self._require(QRadioButton, "radioButton_remote")

        # Combos
        self.combo_model = self._require(QComboBox, "comboBox_select_model")
        self.combo_device = self._require(QComboBox, "comboBox_2")

        # Optional: URL text edit
        self.text_url = self._require(QTextEdit, "textEdit_url")

    # ---------- Signal wiring ----------
    def _wire_signals(self):
        button_handlers = {
            self.btn_ultralytics: self.on_ultralytics_clicked,
            self.btn_gstream: self.on_gstream_clicked,
            self.btn_opencv: self.on_opencv_clicked,
        }
        for button, handler in button_handlers.items():
            button.clicked.connect(handler)

        self.radio_local.toggled.connect(self._on_local_toggled)
        self.radio_remote.toggled.connect(self._on_remote_toggled)

        self.combo_model.currentTextChanged.connect(self.on_model_changed)
        self.combo_device.currentTextChanged.connect(self.on_device_changed)

    # ---------- Initial UI state ----------
    def _init_ui_state(self):
        # Defaults
        self.radio_local.setChecked(True)
        self.text_url.setEnabled(False)

        # Fill combos
        self._fill_model_combo_from_env()
        self._fill_device_combo_from_v4l2()

    # ---- Fill combos ----
    def _fill_model_combo_from_env(self):
        models = listar_modelos_desde_env()

        self.combo_model.blockSignals(True)
        try:
            self.combo_model.clear()

            if not models:
                self.combo_model.addItem("No models found", None)
                self.combo_model.setEnabled(False)
                return

            self.combo_model.setEnabled(True)

            for filename in sorted(models.keys()):
                self.combo_model.addItem(filename, models[filename])

            self.combo_model.setCurrentIndex(0)
        finally:
            self.combo_model.blockSignals(False)

    def _fill_device_combo_from_v4l2(self):
        devices = list_v4l2_devices_linux()  # [(path, label), ...]

        self.combo_device.blockSignals(True)
        try:
            self.combo_device.clear()

            if not devices:
                self.combo_device.addItem("No devices found", None)
                self.combo_device.setEnabled(False)
                return

            self.combo_device.setEnabled(True)

            # show label, store path
            for device_path, label in devices:
                display = f"{label} ({device_path})"
                self.combo_device.addItem(display, device_path)

            self.combo_device.setCurrentIndex(0)
        finally:
            self.combo_device.blockSignals(False)

    # ---------- Helpers ----------
    def _mode(self) -> str:
        return "local" if self.radio_local.isChecked() else "remote"

    def selected_device_path(self):
        """
        returns something like "/dev/video0" or None
        
        :param self:
        """
        return self.combo_device.currentData()
    # ---------- Slots / handlers ----------
    def on_ultralytics_clicked(self):
        selected_model_path = self.combo_model.currentData()
        print("Model path:", selected_model_path)
        selected_device_value = self.combo_device.currentData()
        print("Device path:", selected_device_value)
        print(f"Ultralytics clicked | mode={self._mode()} | model={self.combo_model.currentText()} | device={self.combo_device.currentText()}")

    def on_gstream_clicked(self):
        print(f"GStream clicked | mode={self._mode()} | model={self.combo_model.currentText()} | device={self.combo_device.currentText()}")

    def on_opencv_clicked(self):
        print(f"OpenCV clicked | mode={self._mode()} | model={self.combo_model.currentText()} | device={self.combo_device.currentText()}")

    def _on_local_toggled(self, checked: bool):
        if not checked:
            return
        self.text_url.setEnabled(False)
        print("Mode set to: Local")

    def _on_remote_toggled(self, checked: bool):
        if not checked:
            return
        self.text_url.setEnabled(True)
        print("Mode set to: Remote")

    def on_model_changed(self, text: str):
        print("Model selected:", text)

    def on_device_changed(self, text: str):
        print("Device selected:", text)
