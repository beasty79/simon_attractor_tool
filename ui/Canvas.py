from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QSizePolicy
from matplotlib.figure import Figure
from numpy.typing import NDArray
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QResizeEvent
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from script.simon import to_img


def get_colors(cmap: str) -> NDArray:
    color_map = plt.get_cmap(cmap)
    linear = np.linspace(0, 1, 256)
    return color_map(linear)


class MlpCanvas(FigureCanvas):
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
    def __init__(self, parent: QWidget | None, displays: int = 4, colormap_names: list[str] = 4 * ["cividis"], vertical = True) -> None:
        super().__init__(parent)
        if vertical:
            layout = QVBoxLayout(self)
            self.setFixedWidth(250)
        else:
            layout = QHBoxLayout(self)
            # self.setMinimumWidth(900)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout.setContentsMargins(0, 0, 0, 0)
        self.inverted = False
        self.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.displays = displays
        self.colormaps_name = colormap_names
        self.colormaps = [get_colors(cmap) for cmap in self.colormaps_name]
        self.setStyleSheet("background-color: rgb(100, 100, 100);")
        self.vertical = vertical

        self.canvase: list[MlpCanvas] = []
        for i in range(self.displays):
            canvas = MlpCanvas(self)
            canvas.clicked.connect(lambda _, i=i: self.canvasSelected.emit(self.colormaps_name[i]))
            self.canvase.append(canvas)
            canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            layout.addWidget(canvas, stretch=1)

        self.h_normalized: None | np.typing.NDArray = None

    def display_raw_image(self, raw: np.typing.NDArray, display_index: int, inverted: bool):
        """keeps normalized img [0-1] in memory for further changes"""
        cmap = self.colormaps[display_index]
        if inverted:
            cmap = cmap[::-1]
        img = to_img(raw, cmap)
        self.display(index=display_index, img=img)
        self.h_normalized = raw

    def invert(self, inverted: bool):
        from time import time
        t1= time()
        if self.inverted == inverted:
            return
        if self.h_normalized is None:
            return

        for i in range(self.displays):
            self.display_raw_image(self.h_normalized, i, inverted=inverted)
        self.inverted = inverted
        print(f"took {time()-t1:.2f}s for {self.displays} displays")

    def display(self, index: int, img: NDArray):
        self.canvase[index].display_image(img)

    def mirror(self, img: NDArray):
        for i in range(self.displays):
            self.canvase[i].display_image(img)

    def resizeEvent(self, a0) -> None:
        if self.vertical:
            h = self.height()
            new_w = round(h / 4)
            self.resize(new_w, h)

class DualDisplay(MultipleDisplays):
    def __init__(self, parent: QWidget | None, colormap_names: list[str]) -> None:
        super().__init__(parent, 2, colormap_names, vertical=False)


    def hideWindow(self, index: int = 1):
        if 0 <= index < len(self.canvase):
            canvas: MlpCanvas = self.canvase[index]
            canvas.hide()

            layout = self.layout()
            if layout is not None:
                layout.invalidate()

    def showWindow(self, index: int = 1):
        if index < 0 and index >= len(self.canvase):
            return

        canvas: MlpCanvas = self.canvase[index]
        canvas.show()


class MainCanvas(QWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.mainCanvas = MlpCanvas(self)
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