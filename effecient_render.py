from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication
from VideoWriter import VideoFileWriter
from simon import render_raw, to_img
from numpy.typing import NDArray
import multiprocessing
from time import time
import math

class Worker(QThread):
    progress = pyqtSignal(str)

    def run(self):
        ...

class Renderer:
    def __init__(self, a: NDArray, b: NDArray, filename: str, fps: int, colors, resolution: int, iters: int, percentile: float, buffer_size: int = 30) -> None:
        self.a = a
        self.b = b
        self.iterations: int = iters
        self.fname: str = filename
        self.file_writer = VideoFileWriter(filename, fps)
        self.colors: NDArray = colors
        self.resolution: int = resolution
        self.percentile: float = percentile
        self.buffer_size = buffer_size

    def render_all_frames(self):
            batches = math.ceil(len(self.a) / self.buffer_size)
            current_max = 0
            for i in range(0, len(self.a), self.buffer_size):
                t1 = time()
                QApplication.processEvents()
                a_batch = self.a[i:i+self.buffer_size]
                b_batch = self.b[i:i+self.buffer_size]

                params = [
                    (self.resolution, a, b, self.iterations, self.percentile, current_max) for a, b in zip(a_batch, b_batch)
                ]

                with multiprocessing.Pool() as pool:
                    results = pool.map(render_wrapper, params)

                for im, max in results:
                    if max > current_max:
                        current_max = max
                    img = to_img(im, self.colors)
                    self.file_writer.add_frame(img)

                t_needed = time() - t1
                t_per_frame = t_needed / self.buffer_size
                print(f"Finished batch: ({i//self.buffer_size}/{batches}) per frame: {t_per_frame:.2f}s")
            self.file_writer.save()

def render_wrapper(args):
    return render_raw(*args)