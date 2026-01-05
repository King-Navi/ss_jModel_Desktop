from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QStackedWidget,
    QLabel,
    QToolBar,
    QMessageBox,
    QPushButton,
)

from .pages import HomePage, ToolsPage, SettingsPage
from .video.camara_page import CameraPage
from .video.run_model_page import RunModelPage
from .theme import apply_theme, load_theme_name, save_theme_name


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nice Qt App")
        self.setMinimumSize(980, 600)

        self._theme_name = load_theme_name()  # solo guardamos el estado
        # NO aplicar tema aquí; ya lo aplicas en main.py

        self._build_ui()
        self.statusBar().showMessage("Ready")
    def app(self):
        return self.window().windowHandle().screen().virtualSiblings()[0].context().application() if False else None
        # Fallback: QApplication.instance() avoids tricky references
        # but importing QApplication here is optional.
        # We'll call it via a safe import.
        # (Yes, this looks odd—it's intentional to keep this module lightweight.)

    def _qapp(self):
        from PySide6.QtWidgets import QApplication
        return QApplication.instance()

    def _build_ui(self):
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(10)

        brand = QLabel("NiceQt")
        brand.setStyleSheet("font-size: 16px; font-weight: 800;")
        subtitle = QLabel("Portable template")
        subtitle.setStyleSheet("color: #9ca3af;")

        self.nav = QListWidget()
        self.nav.addItem("Home")
        self.nav.addItem("Tools")
        self.nav.addItem("Camera")
        self.nav.addItem("Run Model")
        self.nav.addItem("Settings")
        self.nav.setCurrentRow(0)
        self.nav.currentRowChanged.connect(self._on_nav_changed)

        sidebar_layout.addWidget(brand)
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addWidget(self.nav, 1)

        self.stack = QStackedWidget()
        self.stack.addWidget(HomePage())
        self.stack.addWidget(ToolsPage())
        self.stack.addWidget(CameraPage())
        self.stack.addWidget(RunModelPage(parent_main_window=self))
        self.stack.addWidget(SettingsPage())

        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.stack, 1)

        self.setCentralWidget(root)
        self._build_toolbar()

    def _build_toolbar(self):
        tb = QToolBar("Main")
        tb.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, tb)

        theme_button = QPushButton("Toggle theme")
        theme_button.clicked.connect(self._toggle_theme)
        tb.addWidget(theme_button)

        about_button = QPushButton("About")
        about_button.clicked.connect(self._about)
        tb.addWidget(about_button)

    def _on_nav_changed(self, index):
        self.stack.setCurrentIndex(index)

    def _toggle_theme(self):
        self._theme_name = "light" if self._theme_name == "dark" else "dark"
        apply_theme(QApplication.instance(), self._theme_name)
        save_theme_name(self._theme_name)
        self.statusBar().showMessage(f"Theme: {self._theme_name}")
        
    def _about(self):
        QMessageBox.information(
            self,
            "About",
            "Nice Qt App\n\nPySide6 + Poetry template.\nClean UI, theme toggle, and portable structure.",
        )
    def closeEvent(self, event):
        try:
            if hasattr(self, "run_model_page"):
                self.run_model_page.stop_and_wait()
        finally:
            super().closeEvent(event)
