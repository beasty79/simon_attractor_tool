from simon import render_raw, to_img
from VideoWriter import VideoFileWriter_Stream
from counter import TerminalCounter
from numpy.typing import NDArray
import matplotlib.pyplot as plt
from typing import Any
import multiprocessing
from time import time
import numpy as np
import os


class Performance_Renderer:
    """This is an api wrapper class for rendering simon attractors"""
    def __init__(self, a: int | NDArray, b: int | NDArray, frames: int, fps: int = 30, n: int | list[int] = 1_000_000, resolution: int | list[int] = 1000, percentile: float | NDArray = 99) -> None:
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
        self.fps = fps
        self.writer = None
        self.color = None
        self.counter: TerminalCounter | None = None

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

    def start_render_process(self, fname: str, verbose_image = False, threads: int | None = 4, chunksize = 4, skip_empty_frames = True):
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

        self.writer = VideoFileWriter_Stream(
            filename=self.get_unique_fname(fname),
            fps=self.fps
        )

        tstart = time()
        self.counter = TerminalCounter(self.frames)
        with multiprocessing.Pool(threads) as pool:
            for i, (img, collapsed) in enumerate(pool.imap(render_wrapper, args, chunksize=chunksize)):
                self.counter.count_up()
                if collapsed and skip_empty_frames:
                    continue
                if verbose_image:
                    self.writer.add_frame(img, a=a[i], b=b[i])
                else:
                    self.writer.add_frame(img)
        total = time() - tstart
        min_ = int(total // 60)
        sec_ = int(total % 60)
        print(f"Finished render process in {min_:02d}:{sec_:02d}")
        print(f"Averaged {self.frames / total:.2f} fps")
        self.writer.save()

def render_wrapper(args):
    h, _ = render_raw(*args[:-1])
    img = to_img(h, args[-1])

    # Filter frames
    non_zero = np.count_nonzero(h)
    pixel: int = args[0]
    thresh = pixel ** 2 * 0.05
    return img, non_zero < thresh

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


def sinspace(lower, upper, n, p=1.0):
    """
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

def cosspace(lower, upper, n, p=1.0):
    """
    Parameters:
    - lower (float): The minimum value.
    - upper (float): The maximum value.
    - n (int): Number of points in the output array.
    - p (float): Number of sine periods to span across the interval.

    Returns:
    - np.ndarray: An array of values shaped by a cos wave between lower and upper.
    """
    phase = np.linspace(0, 2 * np.pi * p, n)
    cos_wave = (np.cos(phase) + 1) / 2
    return lower + (upper - lower) * cos_wave


def map_area(a: NDArray, b: NDArray, fname: str, colormap: ColorMap):
    assert len(a) == len(b), "a & b dont match in length"
    A, B = np.meshgrid(a, b)
    A = A.ravel()
    B = B.ravel()
    fps = 15
    promt(len(A), fps, len(A) / fps)
    process = Performance_Renderer(
        a=A,
        b=B,
        frames=len(A),
        fps=fps,
        percentile=99,
        n=1_000_000
    )
    process.add_colormap(colormap)
    process.start_render_process(fname, verbose_image=True, threads=4, chunksize=8)


def promt(frames, fps, t):
    print(f"{frames=} {fps=} {t=:.0f}")
    accept = input("Enter y or yes to Continue: ")
    if accept not in ["y", "Y", "yes", "Yes", "YES"]:
        exit(0)

def main_():
    t = 1 * 60
    fps = 60
    frames = t * fps
    # frames = 300
    print(f"{frames=} {fps=} {t=}")
    accept = input("Enter y or yes to Continue: ")
    if accept not in ["y", "Y", "yes", "Yes", "YES"]:
        return

    a = sinspace(0.333, 0.35, frames, p=2)
    b = cosspace(1.45, 1.55, frames, p=2)
    # b = np.linspace(1.5, 1.5, frames)
    bpm = 145
    minutes = t / 60
    periods = minutes * bpm

    percentile = sinspace(98.25, 98.75, frames, p=periods)
    process = Performance_Renderer(
        a=a,
        b=b,
        frames=frames,
        fps=fps,
        percentile=percentile,
        n=5_000_000,
        resolution=1200
    )
    process.set_static("a", False)
    process.set_static("b", False)
    process.set_static("percentile", False)

    cmap = ColorMap("cubehelix")
    cmap.set_inverted(True)
    # (resolution=1k) per frame 2.8Mb

    process.add_colormap(cmap)
    process.start_render_process("./render/osc.mp4", verbose_image=True, threads=8, chunksize=4)  # max memory usage is threads * chunksize * 2.8Mb

def project():
    t = 1 * 120
    fps = 100
    frames = t * fps
    # frames = 300
    print(f"{frames=} {fps=} {t=}")
    accept = input("Enter y or yes to Continue: ")
    if accept not in ["y", "Y", "yes", "Yes", "YES"]:
        return

    a = sinspace(0.33, 0.36, frames, p=4)
    b = cosspace(1.45, 1.55, frames, p=2)

    bpm = 155
    minutes = t / 60
    periods = minutes * bpm

    percentile = sinspace(98.75, 99.35, frames, p=periods)
    process = Performance_Renderer(
        a=a,
        b=b,
        frames=frames,
        fps=fps,
        percentile=percentile,
        n=10_000_000,
        resolution=1500
    )
    process.set_static("percentile", False)
    cmap = ColorMap("twilight")
    cmap.set_inverted(True)

    process.add_colormap(cmap)
    process.start_render_process("./render/osc.mp4", verbose_image=False, threads=10, chunksize=4)


def main():
    # project()

    a = np.linspace(-0.067, -0.099, 1500)
    b = np.linspace(1.854, 1.873, 1500)

    # map_area(a, b, "./render/map_full_10k.mp4", ColorMap("viridis"))
    process = Performance_Renderer(
        a=a,
        b=b,
        frames=len(a),
        fps=60,
        percentile=99,
        n=5_000_000,
        resolution=1000
    )
    cmap = ColorMap("viridis")
    cmap.set_inverted(True)
    process.add_colormap(cmap)
    process.start_render_process("./render/render.mp4", verbose_image=False, threads=8)

if __name__ == "__main__":
    main()
