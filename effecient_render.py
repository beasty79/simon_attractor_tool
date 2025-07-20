import multiprocessing
from simon import render
from VideoWriter import VideoFileWriter
from PyQt6.QtWidgets import QApplication
from numpy.typing import NDArray
import math
from time import time

class Renderer:
    def __init__(self, a: NDArray, b: NDArray, filename: str, fps: int, colors, resolution: int, iters: int, percentile: float) -> None:
        self.a = a
        self.b = b
        self.iterations = iters
        self.fname = filename
        self.file_writer = VideoFileWriter(filename, fps)
        self.colors: NDArray = colors
        self.resolution = resolution
        self.percentile = percentile

    def render_all_frames(self):
            buffer_size = 50
            batches = math.ceil(len(self.a) / buffer_size)
            for i in range(0, len(self.a), buffer_size):
                t1 = time()
                QApplication.processEvents()
                a_batch = self.a[i:i+buffer_size]
                b_batch = self.b[i:i+buffer_size]

                params = [
                    (self.colors, self.resolution, a, b, self.iterations, self.percentile) for a, b in zip(a_batch, b_batch)
                ]

                with multiprocessing.Pool() as pool:
                    results = pool.map(render_wrapper, params)

                for im in results:
                    self.file_writer.add_frame(im)

                t_needed = time() - t1
                t_per_frame = t_needed / buffer_size
                print(f"Finished batch: ({i//buffer_size}/{batches}) per frame: {t_per_frame:.2f}s")
            self.file_writer.save()
            print(f"Saved to: {self.fname}")

def render_wrapper(args):
    return render(*args)