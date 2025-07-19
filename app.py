import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QSizePolicy
import matplotlib.pyplot as plt
from ToolBar import Toolbar
from PyQt6.QtCore import Qt
import numpy as np
from simon import render
from PyQt6.QtGui import QKeyEvent


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        super().__init__(self.fig)
        self.setParent(parent)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.updateGeometry()
        self.ax.axis('off')

    def display_image(self, img):
        self.ax.clear()
        self.ax.axis('off')
        self.ax.imshow(img, interpolation='bilinear')
        self.draw_idle()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.toolbar.update_()

    def init_ui(self):
        self.setWindowTitle("Render Tool")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        self.toolbar = Toolbar(self)
        self.toolbar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.toolbar, stretch=0)

        self.canvas = MplCanvas(self)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.canvas, stretch=1)

        central_widget.setStyleSheet("background-color: rgb(200, 200, 200)")
        central_widget.updateGeometry()


    def new_render(self, res: int, a: float, b: float, n: int, percentile: float, colors=None):
        img = render(colors, resolution=res, a=a, b=b, n=n, percentile=percentile)
        self.canvas.display_image(img)
        if self.toolbar.rendering:
            self.toolbar.writer.add_frame(img)
        self.toolbar.update_display(self.toolbar.frame_index, a, b)


    def keyPressEvent(self, a0: QKeyEvent | None):
        if a0 is None:
            return

        key = a0.key()
        modifiers = a0.modifiers()
        key_text = a0.text()

        if key == Qt.Key.Key_PageUp:
            self.toolbar.prev_cmap()
        elif key == Qt.Key.Key_PageDown:
            self.toolbar.next_cmap()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
