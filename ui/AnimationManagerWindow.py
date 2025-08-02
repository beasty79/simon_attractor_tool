from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from ui.point import Libary, Animation

class MangerWindow(QMainWindow):
    def __init__(self, libary: Libary):
        super().__init__()
        self.lib = libary
        self.setWindowTitle("Floating Window")
        self.setGeometry(100, 100, 400, 300)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        central_widget = QLabel()
        self.setCentralWidget(central_widget)
        self.layout_ = QVBoxLayout()
        central_widget.setLayout(self.layout_)
        self.setFixedSize(1000, 560)

        self.init_ui()
        self.init_lib()

        self.table.cellClicked.connect(lambda row, _: self.table.selectRow(row))

    def init_ui(self):
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Origin", "Destination", "Iterations", "Pixel", "Time", "Colormap"])
        self.layout_.addWidget(self.table)

    def init_lib(self):
        self.table.setRowCount(len(self.lib.animations))

        for row, ani in enumerate(self.lib.animations):
            o = ani.origin
            e = ani.end
            self.table.setItem(row, 0, QTableWidgetItem(f"({o.a:2f}, {o.b:.2f})"))
            self.table.setItem(row, 1, QTableWidgetItem(f"({e.a:2f}, {e.b:.2f})"))
            self.table.setItem(row, 2, QTableWidgetItem("1_000_000"))
            self.table.setItem(row, 3, QTableWidgetItem("1000"))
            self.table.setItem(row, 4, QTableWidgetItem("1:00"))
            self.table.setItem(row, 5, QTableWidgetItem("viridis"))

    # def select_row(self, row, cloumn):
