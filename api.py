from simon import render_raw, to_img
from VideoWriter import VideoFileWriter
from numpy.typing import NDArray
from typing import Any, Type
import multiprocessing
from time import time
import math
import numpy as np
import os
import matplotlib.pyplot as plt



class Performance_Renderer:
    """This is an api wrapper class for rendering simon attractors"""
    def __init__(self, a: int | NDArray, b: int | NDArray, frames: int, fps: int = 30, n: int | list[int] = 1_000_000, resolution: int | list[int] = 1000, percentile: float | NDArray = 99, frame_buffer = 40) -> None:
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

    def get_unique_fname(self, fname: str) -> str:
        base_path = os.path.dirname(fname)
        full_name = os.path.basename(fname)
        name_only, ext = os.path.splitext(full_name)

        new_name = fname
        i_ = 0
        while os.path.exists(new_name):
            i_ += 1
            name_comp = f"{name_only}({i_}){ext}"
            new_name = os.path.join(base_path, name_comp)
        return new_name

    def start_render_process(self, fname: str, verbose_image = False, threads: int | None = 4):
        if self.color is None:
            raise SyntaxError("first call: 'add_colormap'")

        res: list[int] = self.get_iter_value("resolution")
        a: list[int] = self.get_iter_value("a")
        b: list[int] = self.get_iter_value("b")
        n: list[int] = self.get_iter_value("n")
        percentile: list[int] = self.get_iter_value("percentile")
        col = [self.color] * len(a)

        args = list(zip(res, a, b, n, percentile, col))
        assert all(len(lst) == len(res) for lst in [a, b, n, percentile, col]), "Mismatched lengths in input lists"

        self.writer = VideoFileWriter(
            filename=self.get_unique_fname(fname),
            fps=self.fps
        )

        print("Render process started!")
        tstart = time()
        with multiprocessing.Pool(threads) as pool:
            for i, img in enumerate(pool.imap(render_wrapper, args, chunksize=8)):
                # img = to_img(h_norm, self.color)
                if verbose_image:
                    self.writer.add_frame(img, a=a[i], b=b[i])
                else:
                    self.writer.add_frame(img)
                print(f"Rendered frame {i + 1}/{self.frames}")
        total = time() - tstart
        min_ = int(total // 60)
        sec_ = int(total % 60)
        print(f"Finished render process in {min_:02d}:{sec_:02d}")
        print(f"Averaged {self.frames / total:.2f} fps")
        self.writer.save()

def render_wrapper(args):
    h, _ = render_raw(*args[:-1])
    img = to_img(h, args[-1])
    return img

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


def sinspace(lower, upper, n, p=1):
    """
    Generate `n` values between `lower` and `upper` in a sinusoidal pattern
    over `p` periods.

    Parameters:
    - lower (float): The minimum value.
    - upper (float): The maximum value.
    - n (int): Number of points in the output array.
    - p (float): Number of sine periods to span across the interval.

    Returns:
    - np.ndarray: An array of values shaped by a sine wave between lower and upper.
    """
    phase = np.linspace(0, 2 * np.pi * p, n)
    sin_wave = (np.sin(phase) + 1) / 2
    return lower + (upper - lower) * sin_wave


def map_area(a: NDArray, b: NDArray, fname: str, colormap: ColorMap):
    assert len(a) == len(b), "a & b dont match in length"
    A, B = np.meshgrid(a, b)
    A = A.ravel()
    B = B.ravel()
    process = Performance_Renderer(
        a=a,
        b=b,
        frames=len(a),
        fps=10,
        percentile=99,
        n=6000000
    )
    process.add_colormap(colormap)
    process.start_render_process(fname, verbose_image=True)


def main():
    t = 10
    fps = 100
    frames = t * fps
    # frames = 300
    print(f"{frames=} {fps=} {t=}")
    accept = input("Enter y or yes to Continue:")
    if accept not in ["y", "Y", "yes", "Yes", "YES"]:
        return

    a = sinspace(0.34, 0.355, frames, p=1)
    b = np.linspace(1.5, 1.5, frames)
    # percentile = np.linspace(95, 99.9, frames)
    process = Performance_Renderer(
        a=a,
        b=b,
        frames=frames,
        fps=fps,
        percentile=98,
        n=3000000,
        frame_buffer=60
    )
    process.set_static("percentile", True)
    cmap = ColorMap("viridis")
    cmap.set_inverted(True)

    process.add_colormap(cmap)
    process.start_render_process("./render/sin.mp4", verbose_image=True)

if __name__ == "__main__":
    main()
