import os
from ui.main import MainWindow
from PyQt6.QtWidgets import QApplication
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
