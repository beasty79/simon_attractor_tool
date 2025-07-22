from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QSizePolicy
from matplotlib.figure import Figure
from PyQt6.QtGui import QKeyEvent
from numpy.typing import NDArray
from PyQt6.QtCore import Qt
from ToolBar import Toolbar
from simon import render
import sys


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure()
        self.ax = self.fig.add_axes((0, 0, 1, 1))
        super().__init__(self.fig)
        self.setParent(parent)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.updateGeometry()
        self.ax.axis('off')

    def display_image(self, img):
        self.ax.clear()
        self.ax.set_aspect('auto')
        self.ax.set_axis_off()
        self.ax.set_aspect('equal')  # Maintains square pixels
        self.ax.imshow(img, interpolation='bilinear')
        self.draw_idle()


class MultipleDisplays(QWidget):
    def __init__(self, parent: QWidget | None, displays: int = 4) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.displays = displays
        self.setStyleSheet("background-color: rgb(100, 100, 100);")

        self.canvase: list[MplCanvas] = []
        for _ in range(self.displays):
            canvas = MplCanvas(self)
            self.canvase.append(canvas)
            layout.addWidget(canvas)

    def display(self, index: int, img: NDArray):
        self.canvase[index].display_image(img)

    def mirror(self, img: NDArray):
        for i in range(self.displays):
            self.canvase[i].display_image(img)

class MainCanvas(QWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.mainCanvas = MplCanvas(self)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.mainCanvas)
        self.setLayout(layout)

        self.setStyleSheet("background-color: rgb(100, 100, 100);")
        self.widget = QWidget(self)
        self.widget.setStyleSheet("border: 1px solid red;")
        self.widget.setFixedWidth(100)
        layout.addWidget(self.widget)

    def display_image(self, img: NDArray):
        self.mainCanvas.display_image(img)

    def resizeEvent(self, a0):
        size = min(self.width(), self.height())
        self.resize(size, size)
        super().resizeEvent(a0)

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

        self.canvas = MainCanvas(self)
        main_layout.addWidget(self.canvas, stretch=1)
        # self.minicanvas = MultipleDisplays(self, 4)
        # main_layout.addWidget(self.minicanvas)

        central_widget.setStyleSheet("background-color: rgb(200, 200, 200)")
        central_widget.updateGeometry()


    def new_render(self, res: int, a: float, b: float, n: int, percentile: float, colors: NDArray):
        """Renders a single frame and displys it in the UI"""
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
