from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QSizePolicy
from matplotlib.figure import Figure
from numpy.typing import NDArray

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
        # self.widget.setStyleSheet("border: 1px solid red;")
        self.widget.setFixedWidth(100)
        layout.addWidget(self.widget)


    def display_image(self, img: NDArray):
        self.mainCanvas.display_image(img)

    def resizeEvent(self, a0):
        size = min(self.width(), self.height())
        self.resize(size, size)
        super().resizeEvent(a0)