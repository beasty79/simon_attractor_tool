from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QWidget, QSpacerItem
from PyQt6.QtCore import Qt
from ui.point import Libary, Animation
from PyQt6.QtGui import QPixmap

class InfoPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout_ = QVBoxLayout()
        self.setLayout(self.layout_)
        # self.setFixedWidth(400)
        self.setStyleSheet("background-color: 1px solid red;")
        self.init_ui()


    @property
    def origin(self) -> str:
        return self._origin.text()

    @origin.setter
    def origin(self, text: str) -> None:
        self._origin.setText(text)

    @property
    def destination(self) -> str:
        return self._destination.text()

    @destination.setter
    def destination(self, text: str) -> None:
        self._destination.setText(text)

    @property
    def colorMap(self) -> str:
        return self._colorMap.text()

    @colorMap.setter
    def colorMap(self, text: str) -> None:
        self._colorMap.setText(text)


    def init_ui(self):
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignTop)
        image_layout = QHBoxLayout()

        self.image = QLabel(self)
        self.image.setFixedSize(150, 150)
        self.image.setScaledContents(True)

        self.image1 = QLabel(self)
        self.image1.setFixedSize(150, 150)
        self.image1.setScaledContents(True)

        self.image2 = QLabel(self)
        self.image2.setFixedSize(150, 150)
        self.image2.setScaledContents(True)

        self.image.setStyleSheet("border: 1px solid black;")
        self.image1.setStyleSheet("border: 1px solid black;")
        self.image2.setStyleSheet("border: 1px solid black;")

        image_layout.addWidget(self.image)
        image_layout.addWidget(self.image1)
        image_layout.addWidget(self.image2)
        self.layout_.addLayout(image_layout)

        self._origin = QLabel("origin: (0, 0)")
        self.layout_.addWidget(self._origin)

        self._destination = QLabel("destination: (0, 0)")
        self.layout_.addWidget(self._destination)

        self._colorMap = QLabel("colormap: 'viridis' (inverted)")
        self.layout_.addWidget(self._colorMap)

        self._time = QLabel("time: 1:30")
        self.layout_.addWidget(self._time)

        self._iterations = QLabel("iterations: 1_000_000")
        self.layout_.addWidget(self._iterations)

        self._frames = QLabel("frames: 3000")
        self.layout_.addWidget(self._frames)


class MangerWindow(QMainWindow):
    def __init__(self, libary: Libary):
        super().__init__()
        self.lib = libary
        self.setWindowTitle("Floating Window")
        self.setGeometry(100, 100, 400, 300)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        central_widget = QWidget()
        self.layout_ = QHBoxLayout()
        self.setCentralWidget(central_widget)
        central_widget.setLayout(self.layout_)

        self.setFixedSize(1000, 560)
        self.init_ui()
        self.init_lib()

        self.table.cellClicked.connect(lambda row, _: self.selectRow(row))

    def selectRow(self, row: int):
        self.table.selectRow(row)
        print(f"display: {self.lib.animations[row]}")


    def init_ui(self):
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setFixedWidth(500)
        self.table.setHorizontalHeaderLabels(["Origin", "Destination", "Iterations", "Pixel", "Time"])
        self.layout_.addWidget(self.table)

        self.infopanel = InfoPanel(self)
        self.layout_.addWidget(self.infopanel)

    def init_lib(self):
        self.table.setRowCount(len(self.lib.animations))

        for row, ani in enumerate(self.lib.animations):
            o = ani.origin
            e = ani.end
            self.table.setItem(row, 0, QTableWidgetItem(f"({o.a:.2f}, {o.b:.2f})"))
            self.table.setItem(row, 1, QTableWidgetItem(f"({e.a:.2f}, {e.b:.2f})"))
            self.table.setItem(row, 2, QTableWidgetItem("1_000_000"))
            self.table.setItem(row, 3, QTableWidgetItem("1000"))
            self.table.setItem(row, 4, QTableWidgetItem("1:00"))

    # def select_row(self, row, cloumn):
