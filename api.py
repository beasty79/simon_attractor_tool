from simon import render_raw, to_img
from VideoWriter import VideoFileWriter
from numpy.typing import NDArray
from typing import Any, Type
import multiprocessing
from time import time
import math
import numpy as np
import matplotlib.pyplot as plt



class Performance_Renderer:
    """This is an api wrapper class for rendering simon attractors"""
    def __init__(self, a: int | NDArray, b: int | NDArray, frames: int, fps: int = 30, n: int | list[int] = 1_000_000, resolution: int | list[int] = 1000, percentile: float | list[float] = 99, frame_buffer = 40) -> None:
        self.a = a
        self.b = b
        self.n = n
        self.resolution = resolution
        self.percentile = percentile
        self.frames = frames
        self.value = {
            'a': a,
            'b': b,
            'n': n,
            'resolution': resolution,
            'percentile': percentile
        }
        self.static = {
            'a': False,
            'b': False,
            'n': True,
            'resolution': True,
            'percentile': True
        }
        self.frame_buffer = frame_buffer
        self.fps = fps
        self.writer = None
        self.color = None

    def add_colormap(self, color_map: "ColorMap"):
        self.color = color_map.get()

    def set_static(self, argument: Any, is_static: bool):
        """
        argument: {'a', 'b', 'n', 'resolution'}
        """
        if argument not in self.static:
            raise ValueError(f"arg: {argument} is invalid, should be: ['a', 'b', 'n', 'resolution', 'percentile']")
        self.static[argument] = is_static

    def get_iter_value(self, arg: str) -> list[Any]:
        if arg not in self.static:
            raise ValueError("arg not in static")
        is_static: bool = self.static[arg]

        if is_static:
            return [self.value[arg]] * self.frames
        else:
            return self.value[arg]

    def start_render_process(self, fname: str):
        if self.color is None:
            raise SyntaxError("first call: 'add_colormap'")

        res: list[int] = self.get_iter_value("resolution")
        a: list[int] = self.get_iter_value("a")
        b: list[int] = self.get_iter_value("b")
        n: list[int] = self.get_iter_value("n")
        percentile: list[int] = self.get_iter_value("percentile")

        args = list(zip(res, a, b, n, percentile))
        assert all(len(lst) == len(res) for lst in [a, b, n, percentile]), "Mismatched lengths in input lists"
        self.writer = VideoFileWriter(fname, self.fps)

        print("Render Process started!")
        tstart = time()
        with multiprocessing.Pool() as pool:
            for i in range(0, len(args), self.frame_buffer):
                batch = args[i:i + self.frame_buffer]
                results = pool.starmap(render_raw, batch)
                for h_norm, _ in results:
                    img = to_img(h_norm, self.color)
                    self.writer.add_frame(img)

        total = time() - tstart
        min_ = round(total // 60)
        sec_ = round(total - min_ * 60)
        print(f"Finished Render Process in {min_:02d}:{sec_:02d}")
        self.writer.save()

class ColorMap:
    def __init__(self, name: str) -> None:
        self.color = self.get_colors_array(name)
        self.inverted = False

    def set_inverted(self, state: bool):
        self.inverted = state

    def get_colors_array(self, cmap: str) -> NDArray:
        color_map = plt.get_cmap(cmap)
        linear = np.linspace(0, 1, 256)
        return color_map(linear)

    def get(self) -> NDArray:
        return self.color[::-1] if self.inverted else self.color

def main():
    a = np.linspace(.35, .45, 100)
    b = np.linspace(1.5, 1.5, 100)

    process = Performance_Renderer(
        a=a,
        b=b,
        frames=100,
        fps=60
    )
    process.add_colormap(ColorMap("viridis"))
    process.start_render_process("./render/api.mp4")

if __name__ == "__main__":
    main()
