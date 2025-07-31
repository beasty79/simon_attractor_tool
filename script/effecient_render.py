from script.VideoWriter import VideoFileWriter
from script.simon import render_raw, to_img
from numpy.typing import NDArray
import multiprocessing
from time import time
from datetime import timedelta

class Renderer:
    def __init__(self, a: NDArray, b: NDArray, filename: str, fps: int, colors, resolution: int, iters: int, percentile: float) -> None:
        self.a = a
        self.b = b
        self.iterations: int = iters
        self.fname: str = filename
        self.file_writer = VideoFileWriter(filename, fps)
        self.colors: NDArray = colors
        self.resolution: int = resolution
        self.percentile: float = percentile

    def render_all_frames(self):
        params = [
            (self.resolution, a, b, self.iterations, self.percentile, 0) for a, b in zip(self.a, self.b)
        ]
        t_total = time()
        with multiprocessing.Pool() as pool:
            i = 0
            t = time()
            for result in pool.imap(render_wrapper, params):
                i += 1
                im, max = result
                img = to_img(im, self.colors)
                self.file_writer.add_frame(img)
                t_new = time()
                print(f"frame: ({i}/{len(self.a)}),\t took {t_new - t:.2f}s")
                t = t_new
        self.file_writer.save()
        formatted = str(timedelta(seconds=t_total))
        print(f"Render took {formatted}.")

def render_wrapper(args):
    return render_raw(*args)