from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QSizePolicy, QHBoxLayout, QFrame, QComboBox, QApplication
)
import matplotlib.pyplot as plt
from PyQt6.QtCore import QTimer, Qt, QRegularExpression
import numpy as np
from VideoWriter import VideoFileWriter
from numpy.typing import NDArray
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator
if 0!=0: from app import MainWindow
from time import time

# cmap
top_colormaps = [
    'viridis', 'plasma','inferno','magma','cividis','turbo','coolwarm','Spectral','RdYlBu','RdYlGn','PiYG',
    'PRGn', 'BrBG', 'PuOr', 'Set1', 'Set2', 'Set3', 'Paired', 'Pastel1', 'Pastel2', 'tab10', 'tab20', 'cubehelix', 'nipy_spectral', \
    'gist_rainbow', 'gnuplot', 'twilight', 'twilight_shifted', 'terrain', 'ocean'
]


class Toolbar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_: "MainWindow" = parent

        self.setFixedWidth(250)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self.wait_timer = QTimer(self)
        self.wait_timer.setInterval(500)
        self.wait_timer.setSingleShot(True)
        self.wait_timer.timeout.connect(self.render_single_frame)

        self.rendering = False
        self.max_frames = 0

        # Animation state
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.next_frame)
        self.frame_index = 0
        self.values_a = []
        self.values_b = []
        self.animation_params = {}
        self.colors = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        float_validator = QRegularExpressionValidator(QRegularExpression(r"^[+-]?\d+\.\d+$"))
        int_validator = QIntValidator()

        # Input: a and b
        para_1 = QHBoxLayout()
        self.input_a = QLineEdit("0.53", self)
        self.input_a.setValidator(float_validator)
        para_1.addWidget(QLabel("a:"))
        para_1.addWidget(self.input_a)

        self.input_b = QLineEdit("1.23", self)
        self.input_b.setValidator(float_validator)
        para_1.addWidget(QLabel("b:"))
        para_1.addWidget(self.input_b)
        layout.addLayout(para_1)

        # Input: iterations
        para_3 = QHBoxLayout()
        self.input_n = QLineEdit("1000000", self)
        self.input_n.setValidator(int_validator)
        para_3.addWidget(QLabel("Iterations:"))
        para_3.addWidget(self.input_n)
        layout.addLayout(para_3)

        # Input: Percentile
        para_4 = QHBoxLayout()
        self.input_percentile = QLineEdit("95", self)
        self.input_percentile.setValidator(float_validator)
        para_4.addWidget(QLabel("Percentile (1-100):"))
        para_4.addWidget(self.input_percentile)
        layout.addLayout(para_4)

        # Input: resolution
        para_4 = QHBoxLayout()
        self.input_res = QLineEdit("1000", self)
        self.input_res.setValidator(int_validator)
        para_4.addWidget(QLabel("Resolution (pixel):"))
        para_4.addWidget(self.input_res)
        layout.addLayout(para_4)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setLineWidth(1)
        layout.addWidget(separator)

        # colormap
        self.cmap_box = QComboBox(self)
        self.cmap_box.addItems(top_colormaps)
        self.cmap_box.currentTextChanged.connect(lambda: self.render_single_frame())
        layout.addWidget(self.cmap_box)

        # Animation Section
        layout.addWidget(QLabel("Animate: "))

        # Animate a
        animate_layout_a = QHBoxLayout()
        self._from = QLineEdit("1", self)
        self._to = QLineEdit("2", self)
        self._from.setValidator(float_validator)
        self._to.setValidator(float_validator)
        animate_layout_a.addWidget(QLabel("(a) From:"))
        animate_layout_a.addWidget(self._from)
        animate_layout_a.addWidget(QLabel("To:"))
        animate_layout_a.addWidget(self._to)
        layout.addLayout(animate_layout_a)

        # Animate b
        animate_layout_b = QHBoxLayout()
        self._from_b = QLineEdit("1", self)
        self._to_b = QLineEdit("2", self)
        self._from_b.setValidator(float_validator)
        self._to_b.setValidator(float_validator)
        animate_layout_b.addWidget(QLabel("(b) From:"))
        animate_layout_b.addWidget(self._from_b)
        animate_layout_b.addWidget(QLabel("To:"))
        animate_layout_b.addWidget(self._to_b)
        layout.addLayout(animate_layout_b)

        self._from.setFixedWidth(50)
        self._from_b.setFixedWidth(50)
        self._to.setFixedWidth(50)
        self._to_b.setFixedWidth(50)

        # Frames
        frame_layout = QHBoxLayout()
        self.frames = QLineEdit("100", self)
        self.frames.setValidator(int_validator)
        label_frame = QLabel("Frames:")
        label_frame.setFixedWidth(150)
        frame_layout.addWidget(label_frame)
        frame_layout.addWidget(self.frames)
        layout.addLayout(frame_layout)

        # FPS input
        fps_layout = QHBoxLayout()
        self.fps_input = QLineEdit("10", self)
        self.fps_input.setValidator(int_validator)
        label_fps = QLabel("FPS:")
        label_fps.setFixedWidth(150)
        fps_layout.addWidget(label_fps)
        fps_layout.addWidget(self.fps_input)
        layout.addLayout(fps_layout)

        # video time label
        self.video_time_label = QLabel("")
        layout.addWidget(self.video_time_label)

        # Start Animation
        self.start_animation = QPushButton("Start Animation")
        self.start_animation.clicked.connect(self.animate)
        layout.addWidget(self.start_animation)

        layout.addStretch()
        self.setLayout(layout)

        # Separator 2
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setLineWidth(1)
        layout.addWidget(separator2)

        self.last_frame_sec = QLabel("Last Rendered Frame took -")
        layout.addWidget(self.last_frame_sec)

        self.label_framecount = QLabel("Frame: 0/0")
        layout.addWidget(self.label_framecount)

        self.label_ab = QLabel("a, b: (0, 0)")
        layout.addWidget(self.label_ab)

        # Input signals
        self.input_a.textChanged.connect(self.update_)
        self.input_b.textChanged.connect(self.update_)
        self.input_n.textChanged.connect(self.update_render)
        self.input_percentile.textChanged.connect(self.update_render)
        self.input_res.textChanged.connect(self.update_render)

        self.frames.textChanged.connect(lambda: self.update_time())
        self.fps_input.textChanged.connect(lambda: self.update_time())

        self.update_render()
        self.update_time()

    def update_time(self):
        try:
            fps = int(self.fps_input.text())
            frames = int(self.frames.text())
        except ValueError:
            return
        if not fps or not frames:
            return

        total = frames / fps
        self.video_time_label.setText(f"Video length: {total:.0f}s")

    def update_display(self, frame: int, a: float, b:float):
        self.label_framecount.setText(f"{frame}/{self.max_frames}")
        self.label_ab.setText(f"a, b: ({a:.3f}, {b:.3f})")

    def next_cmap(self):
        length = len(self.cmap_box)
        index = self.cmap_box.currentIndex() + 1
        self.cmap_box.setCurrentIndex(index if index < length else length - 1)

    def prev_cmap(self):
        index = self.cmap_box.currentIndex() - 1
        self.cmap_box.setCurrentIndex(index if index > 0 else 0)

    def update_(self):
        # self._from.setText(self.input_a.text())
        # self._from_b.setText(self.input_b.text())
        # self._to.setText(self.input_a.text())
        # self._to_b.setText(self.input_b.text())
        self.update_render()

    def update_render(self):
        if self.wait_timer.isActive():
            self.wait_timer.stop()
        self.wait_timer.start()

    @property
    def a(self) -> float:
        return float(self.input_a.text())

    @property
    def b(self) -> float:
        return float(self.input_b.text())

    @property
    def iterations(self) -> int:
        return int(self.input_n.text())

    @property
    def percentile(self) -> float:
        x = float(self.input_percentile.text())
        if x > 100:
            return 100
        elif x < 0:
            return 0
        return x

    @property
    def resolution(self) -> int:
        res = int(self.input_res.text())
        return res if res > 0 else 10

    def get_colors(self) -> NDArray:
        cmap = plt.get_cmap(self.cmap_box.currentText())
        linear = np.linspace(0, 1, 256)
        return cmap(linear)

    def render_single_frame(self):
        t1 = time()
        QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)
        colors = self.get_colors()
        self.parent_.new_render(self.resolution, self.a, self.b, self.iterations, colors=colors, percentile=self.percentile)
        QApplication.restoreOverrideCursor()
        time_needed = time()-t1
        self.last_frame_sec.setText(f"Last Rendered Frame took {time_needed:.2f}s")

    def animate(self):
        try:
            a_1 = float(self._from.text())
            a_2 = float(self._to.text())
            b_1 = float(self._from_b.text())
            b_2 = float(self._to_b.text())
            frames = int(self.frames.text())
            res = int(self.input_res.text())
            n = int(self.input_n.text())
            fps = int(self.fps_input.text())
        except Exception as e:
            print("Invalid input:", e)
            return

        self.rendering = True
        fname = make_filename(a_1, a_2, b_1, b_2, extension="mp4")
        self.writer = VideoFileWriter(fname, fps=fps)


        self.values_a = np.linspace(a_1, a_2, frames)
        self.values_b = np.linspace(b_1, b_2, frames)
        self.frame_index = 0
        self.animation_params = {"res": res, "n": n}

        cmap = plt.get_cmap(self.cmap_box.currentText())
        linear = np.linspace(0, 1, 256)
        self.colors = cmap(linear)


        frame_delay_ms = int(1000 / 60)
        self.animation_timer.start(frame_delay_ms)
        self.max_frames = frames

    def next_frame(self):
        if self.frame_index >= len(self.values_a):
            self.writer.save()
            self.animation_timer.stop()
            self.rendering = False
            return


        a = self.values_a[self.frame_index]
        b = self.values_b[self.frame_index]
        res = self.animation_params["res"]
        n = self.animation_params["n"]

        self.parent_.new_render(res, a, b, n, colors=self.colors)
        self.frame_index += 1

def make_filename(a_1, a_2, b_1, b_2, extension="mp4"):
    parts = []
    if a_1 != a_2:
        parts.append(f"a_{a_1}-{a_2}")
    if b_1 != b_2:
        parts.append(f"b_{b_1}-{b_2}")

    fname = "_".join(parts) + f".{extension}"
    return fname