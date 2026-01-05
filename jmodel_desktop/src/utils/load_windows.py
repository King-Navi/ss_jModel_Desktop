from PySide6.QtCore import QFile, QIODevice
from PySide6.QtUiTools import QUiLoader

from ..resources import views_rc

def load_ui(ui_ref: str, parent=None):
    ui_file = QFile(ui_ref)
    if not ui_file.open(QIODevice.ReadOnly):
        raise RuntimeError(f"Could not open UI: {ui_ref} ({ui_file.errorString()})")

    loader = QUiLoader()
    widget = loader.load(ui_file, parent)
    ui_file.close()

    if widget is None:
        raise RuntimeError(f"Failed to load UI: {ui_ref}")

    return widget