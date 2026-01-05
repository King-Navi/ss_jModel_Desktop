import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from .ui.theme import apply_theme, load_theme_name

from PySide6.QtWidgets import QApplication
from .resources import views_rc
from .utils.load_windows import load_ui

from .controllers.run_model_controller import RunModelController 


def main():
    app = QApplication(sys.argv)

    window = load_ui(":/views/../views/run_model_window.ui")

    _controller = RunModelController(window)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()