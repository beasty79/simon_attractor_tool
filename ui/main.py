from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QKeyEvent

from script.simon import render_raw, to_img
from ui.Canvas import MainCanvas, MultipleDisplays
from ui.ToolBar import Toolbar

from numpy.typing import NDArray
from os import path
import sys


mini_cmaps = [
    "viridis",
    "cividis",
    "twilight",
    "gnuplot",
]

mini_cmaps_2 = [
    "Spectral",
    "Pastel1",
    "cubehelix",
    "ocean",
]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.toolbar.update_()
        instance = QApplication.instance()
        if instance is not None:
            instance.installEventFilter(self)

        self.minicanvas_colors_1: list[list] = []
        self.minicanvas_colors_2: list[list] = []
        self.showMaximized()

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

        self.minicanvas_ = MultipleDisplays(self, 4, mini_cmaps)
        self.minicanvas_.canvasSelected.connect(lambda col: self.toolbar.cmap_box.setCurrentText(col))
        main_layout.addWidget(self.minicanvas_)

        self.minicanvas = MultipleDisplays(self, 4, mini_cmaps_2)
        self.minicanvas.canvasSelected.connect(lambda col: self.toolbar.cmap_box.setCurrentText(col))
        main_layout.addWidget(self.minicanvas)


        central_widget.setStyleSheet("background-color: rgb(200, 200, 200)")
        central_widget.updateGeometry()

    def invert_minidiplays(self, boolean: bool):
        self.minicanvas.invert(boolean)
        self.minicanvas_.invert(boolean)

    def new_render(self, res: int, a: float, b: float, n: int, percentile: float, colors: NDArray):
        """Renders a single frame and displys it in the UI"""
        h_normalized, _ = render_raw(res, a, b, n, percentile, 0)
        im = to_img(h_normalized, colors)
        self.canvas.display_image(im)

        for i in range(self.minicanvas_.displays):
            self.minicanvas_.display_raw_image(h_normalized, i, self.toolbar.invert)

        for i in range(self.minicanvas.displays):
            self.minicanvas.display_raw_image(h_normalized, i, self.toolbar.invert)

        if self.toolbar.rendering:
            self.toolbar.writer.add_frame(im)
        self.toolbar.update_display(self.toolbar.frame_index, a, b)
        return h_normalized

    def generate_infodump(self, fpath: str, a0, a1, b0, b1, n, cmap_name):
        base_name = path.basename(fpath)
        if "." in base_name:
            base_name = base_name.split(".")[-2]
        base_name += ".txt"

        file_content: str = ""
        file_content += f"a0: {a0}\n"
        file_content += f"a1: {a1}\n"
        file_content += f"b0: {b0}\n"
        file_content += f"b1: {b1}\n"
        file_content += f"iterations: {n}\n"
        file_content += f"colormap: {cmap_name}\n"

        fpath = path.dirname(__file__)
        path_to_log = path.join(fpath, "log", base_name)
        with open(path_to_log, "w") as f:
            f.write(file_content)

    def eventFilter(self, a0, a1):
        if a1 is None:
            return False
        if a1.type() == QEvent.Type.KeyPress:
            if isinstance(a1, QKeyEvent):
                key = a1.key()
                if key == Qt.Key.Key_I:
                    self.toolbar.invert_checkbox.setChecked(not self.toolbar.invert_checkbox.isChecked())
                    self.toolbar.cmap_change()
                    return True
        return False

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
