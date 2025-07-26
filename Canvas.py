from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QSizePolicy
from matplotlib.figure import Figure
from numpy.typing import NDArray
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QResizeEvent
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from simon import to_img


def get_colors(cmap: str) -> NDArray:
    color_map = plt.get_cmap(cmap)
    linear = np.linspace(0, 1, 256)
    return color_map(linear)


class MplCanvas(FigureCanvas):
    clicked = pyqtSignal(bool)

    def __init__(self, parent=None):
        self.fig = Figure()
        self.ax = self.fig.add_axes((0, 0, 1, 1))
        # self.ax = self.fig.add_subplot(111)
        # self.ax.set_position((0, 0, 1, 1))  # left, bottom, width, height (0 to 1)
        super().__init__(self.fig)

        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.updateGeometry()
        self.ax.axis('off')
        self.fig.set_facecolor((0.5, 0.5, 0.5))

    def display_image(self, img):
        self.ax.clear()
        self.ax.set_aspect('auto')
        self.ax.set_axis_off()
        self.ax.set_aspect('equal')  # Maintains square pixels
        self.ax.imshow(img, interpolation='bilinear')
        self.draw_idle()

    def mousePressEvent(self, event):
        self.clicked.emit(True)
        return super().mousePressEvent(event)


class MultipleDisplays(QWidget):
    canvasSelected = pyqtSignal(str)
    def __init__(self, parent: QWidget | None, displays: int = 4, colormap_names: list[str] = 4 * ["cividis"]) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.displays = displays
        self.colormaps_name = colormap_names
        self.colormaps = [get_colors(cmap) for cmap in self.colormaps_name]
        self.setStyleSheet("background-color: rgb(100, 100, 100);")

        self.canvase: list[MplCanvas] = []
        for i in range(self.displays):
            canvas = MplCanvas(self)
            canvas.clicked.connect(lambda _, i=i: self.canvasSelected.emit(self.colormaps_name[i]))
            self.canvase.append(canvas)
            layout.addWidget(canvas)
        self.setFixedWidth(250)
        self.h_normalized: None | np.typing.NDArray = None

    def display_raw_image(self, raw: np.typing.NDArray, display_index: int, inverted: bool):
        cmap = self.colormaps[display_index]
        if inverted:
            cmap = cmap[::-1]
        img = to_img(raw, cmap)
        self.display(index=display_index, img=img)
        self.h_normalized = raw

    def invert(self, inverted: bool):
        if self.h_normalized is None:
            return

        for i in range(self.displays):
            self.display_raw_image(self.h_normalized, i, inverted=inverted)

    def display(self, index: int, img: NDArray):
        self.canvase[index].display_image(img)

    def mirror(self, img: NDArray):
        for i in range(self.displays):
            self.canvase[i].display_image(img)

    def resizeEvent(self, a0) -> None:
        h = self.height()
        new_w = round(h / 4)
        self.resize(new_w, h)

class MainCanvas(QWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.mainCanvas = MplCanvas(self)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.mainCanvas)
        self.setLayout(layout)

        self.setStyleSheet("background-color: rgb(100, 100, 100);")
        self.widget = QWidget(self)
        # self.widget.setStyleSheet("border: 1px solid red;")
        layout.addWidget(self.widget)
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

    def display_image(self, img: NDArray):
        self.mainCanvas.display_image(img)

    # def resizeEvent(self, a0: QResizeEvent | None):
    #     size = min(self.width(), self.height())
    #     self.resize(size, size)
    #     if a0 is None:
    #         return
    #     print(f"resize {a0.size()} {self.width()} {self.height()}")