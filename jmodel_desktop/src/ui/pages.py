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


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Home")
        title.setObjectName("TitleLabel")

        subtitle = QLabel("A clean, portable Qt app template (Poetry + PySide6).")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #9ca3af;")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch(1)


class ToolsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Tools")
        title.setObjectName("TitleLabel")

        row = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Type something...")
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self._run)

        row.addWidget(self.input_edit, 1)
        row.addWidget(self.run_button)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Logs...")

        layout.addWidget(title)
        layout.addLayout(row)
        layout.addWidget(self.output, 1)

    def _run(self):
        text = self.input_edit.text().strip()
        if not text:
            self.output.append("[warn] Empty input")
            return
        self.output.append(f"[ok] You typed: {text}")
        self.input_edit.clear()


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Settings")
        title.setObjectName("TitleLabel")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)

        self.mode = QComboBox()
        self.mode.addItems(["Local (127.0.0.1)", "External"])
        self.host = QLineEdit()
        self.host.setPlaceholderText("e.g. 192.168.0.10")
        self.port = QLineEdit()
        self.port.setPlaceholderText("e.g. 8000 (optional)")

        form.addRow("Mode", self.mode)
        form.addRow("Host", self.host)
        form.addRow("Port", self.port)

        hint = QLabel("Tip: persist these later using QSettings (same idea as theme).")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #9ca3af;")

        layout.addWidget(title)
        layout.addLayout(form)
        layout.addWidget(hint)
        layout.addStretch(1)
