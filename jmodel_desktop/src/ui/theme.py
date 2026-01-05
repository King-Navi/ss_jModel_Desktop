from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor, QPalette


def _palette_dark():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#0f172a"))
    palette.setColor(QPalette.WindowText, QColor("#e5e7eb"))
    palette.setColor(QPalette.Base, QColor("#0b1220"))
    palette.setColor(QPalette.AlternateBase, QColor("#111c33"))
    palette.setColor(QPalette.Text, QColor("#e5e7eb"))
    palette.setColor(QPalette.Button, QColor("#111c33"))
    palette.setColor(QPalette.ButtonText, QColor("#e5e7eb"))
    palette.setColor(QPalette.Highlight, QColor("#3b82f6"))
    palette.setColor(QPalette.HighlightedText, QColor("#0b1220"))
    palette.setColor(QPalette.ToolTipBase, QColor("#0b1220"))
    palette.setColor(QPalette.ToolTipText, QColor("#e5e7eb"))
    return palette


def _palette_light():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#f8fafc"))
    palette.setColor(QPalette.WindowText, QColor("#0f172a"))
    palette.setColor(QPalette.Base, QColor("#ffffff"))
    palette.setColor(QPalette.AlternateBase, QColor("#f1f5f9"))
    palette.setColor(QPalette.Text, QColor("#0f172a"))
    palette.setColor(QPalette.Button, QColor("#e2e8f0"))
    palette.setColor(QPalette.ButtonText, QColor("#0f172a"))
    palette.setColor(QPalette.Highlight, QColor("#2563eb"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    return palette


def apply_theme(app, theme_name):
    if app is None:
        raise RuntimeError("QApplication instance is None. Create QApplication before applying theme.")
    
    if theme_name == "dark":
        app.setPalette(_palette_dark())
        app.setStyleSheet(_qss_dark())
    else:
        app.setPalette(_palette_light())
        app.setStyleSheet(_qss_light())


def load_theme_name():
    settings = QSettings()
    return settings.value("theme", "dark")


def save_theme_name(theme_name):
    settings = QSettings()
    settings.setValue("theme", theme_name)


def _qss_dark():
    return """
    QMainWindow { background: #0f172a; }
    QWidget { font-size: 13px; }
    QLabel#TitleLabel { font-size: 18px; font-weight: 700; }
    QFrame#Sidebar { background: #0b1220; border-right: 1px solid #1f2a44; }
    QListWidget { background: transparent; border: none; padding: 8px; }
    QListWidget::item { padding: 10px 12px; border-radius: 10px; color: #e5e7eb; }
    QListWidget::item:selected { background: #111c33; }
    QLineEdit, QTextEdit {
        background: #0b1220; border: 1px solid #1f2a44; border-radius: 10px; padding: 8px;
        color: #e5e7eb;
    }
    QPushButton {
        background: #111c33; border: 1px solid #1f2a44; border-radius: 12px; padding: 10px 12px;
        color: #e5e7eb;
    }
    QPushButton:hover { border-color: #3b82f6; }
    QToolBar { background: #0f172a; border: none; }
    QStatusBar { background: #0f172a; color: #9ca3af; }
    """


def _qss_light():
    return """
    QMainWindow { background: #f8fafc; }
    QWidget { font-size: 13px; }
    QLabel#TitleLabel { font-size: 18px; font-weight: 700; }
    QFrame#Sidebar { background: #ffffff; border-right: 1px solid #e2e8f0; }
    QListWidget { background: transparent; border: none; padding: 8px; }
    QListWidget::item { padding: 10px 12px; border-radius: 10px; color: #0f172a; }
    QListWidget::item:selected { background: #f1f5f9; }
    QLineEdit, QTextEdit {
        background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px;
        color: #0f172a;
    }
    QPushButton {
        background: #e2e8f0; border: 1px solid #cbd5e1; border-radius: 12px; padding: 10px 12px;
        color: #0f172a;
    }
    QPushButton:hover { border-color: #2563eb; }
    QToolBar { background: #f8fafc; border: none; }
    QStatusBar { background: #f8fafc; color: #475569; }
    """
