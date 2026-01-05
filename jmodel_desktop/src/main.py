import sys
from PySide6.QtWidgets import QApplication
from jmodel_desktop.src.ui.theme import apply_theme, load_theme_name
from jmodel_desktop.src.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("jmodel_desktop")
    app.setOrganizationName("King-Navi")
    app.setStyle("Fusion")

    apply_theme(app, load_theme_name())

    window = MainWindow()
    window.show()

    raise SystemExit(app.exec())
