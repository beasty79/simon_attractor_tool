from script.simon import render_raw, to_img
from script.VideoWriter import VideoFileWriter_Stream
from script.counter import TerminalCounter
from numpy.typing import NDArray
from typing import Any
import multiprocessing
from time import time
from PyQt6.QtCore import pyqtBoundSignal
import numpy as np
import os
from script.utils import promt
import matplotlib.pyplot as plt


class ColorMap:
    def __init__(self, name: str, inverted: bool = False) -> None:
        self.color = self.get_colors_array(name)
        self.inverted = inverted

    def set_inverted(self, state: bool):
        self.inverted = state

    def get_colors_array(self, cmap: str) -> NDArray:
        color_map = plt.get_cmap(cmap)
        linear = np.linspace(0, 1, 256)
        return color_map(linear)

    def get(self) -> NDArray:
        return self.color[::-1] if self.inverted else self.color


def _render_wrapper(args):
    h, _ = render_raw(*args[:-1])
    img = to_img(h, args[-1])

    # Filter frames
    non_zero = np.count_nonzero(h)
    pixel: int = args[0]
    thresh = pixel ** 2 * 0.05
    return img, non_zero < thresh

class Performance_Renderer:
    """This is an api wrapper class for rendering simon attractors"""
    def __init__(self, a: int | NDArray, b: int | NDArray, colormap: "ColorMap", frames: int, fps: int = 30, n: int | list[int] = 1_000_000, resolution: int | list[int] = 1000, percentile: float | NDArray = 99) -> None:
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
            'a': True,
            'b': True,
            'n': True,
            'resolution': True,
            'percentile': True
        }
        self.fps = fps
        self.writer = None
        self.color = None
        self.counter: TerminalCounter | None = None
        self.colormap: ColorMap = colormap
        self.hook: pyqtBoundSignal | None = None

    def set_static(self, argument: Any, is_static: bool):
        """
        argument: {'a', 'b', 'n', 'resolution', 'percentile'}
        """
        if argument not in self.static:
            raise ValueError(f"arg: {argument} is invalid, should be: ['a', 'b', 'n', 'resolution', 'percentile']")
        self.static[argument] = is_static

    def addHook(self, signal: pyqtBoundSignal):
        self.hook = signal

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

    def start_render_process(self, fname: str, verbose_image = False, threads: int | None = 4, chunksize = 4, skip_empty_frames = True, bypass_confirm = False):
        res: list[int] = self.get_iter_value("resolution")
        a: list[int] = self.get_iter_value("a")
        b: list[int] = self.get_iter_value("b")
        n: list[int] = self.get_iter_value("n")
        percentile: list[int] = self.get_iter_value("percentile")
        self.color = self.colormap.get()
        col = [self.color] * len(a)

        # checks and promting
        args = list(zip(res, a, b, n, percentile, col))
        assert all(len(lst) == len(res) for lst in [a, b, n, percentile, col]), "Mismatched lengths in input lists"
        if not bypass_confirm:
            promt(self.frames, self.fps)

        # prepare path
        if "/" not in fname and "\\" not in fname:
            fname = f"./render/{fname}"

        if ".mp4" not in fname:
            fname = f"{fname}.mp4"
        print(fname)

        # File Writer
        self.writer = VideoFileWriter_Stream(
            filename=self.get_unique_fname(fname),
            fps=self.fps
        )

        # Terminal Feedback
        tstart = time()
        self.counter = TerminalCounter(self.frames)
        if self.hook is None:
            self.counter.start()

        # Multiproccessing
        try:
            with multiprocessing.Pool(threads) as pool:
                for i, (img, collapsed) in enumerate(pool.imap(_render_wrapper, args, chunksize=chunksize)):

                    # Either Signal or Terminal
                    if self.hook is not None:
                        self.hook.emit(i)
                    else:
                        self.counter.count_up()

                    # filter
                    if collapsed and skip_empty_frames:
                        continue

                    # write a, b
                    if verbose_image:
                        self.writer.add_frame(img, a=a[i], b=b[i])
                    else:
                        self.writer.add_frame(img)
        except Exception:
            raise ValueError("use set_static('a', False) for every attribute you give as an array")

        # Process Finished
        total = time() - tstart
        min_ = int(total // 60)
        sec_ = int(total % 60)
        print(f"Finished render process in {min_:02d}:{sec_:02d}")
        print(f"Average: {self.frames / total:.2f} fps")
        self.writer.save()

def bpmspace(lower: float, upper: float, n: int, bpm: int, fps: int):
    """
    Parameters:
    - lower (float): The minimum value.
    - upper (float): The maximum value.
    - n (int): Number of points in the output array.
    - p (float): Number of sine periods to span across the interval.

    Returns:
    - np.ndarray: An array of values shaped by a sine wave between lower and upper.
    """
    total_time = n / fps
    minutes = total_time / 60
    periods_needed = minutes * bpm
    return sinspace(lower, upper, n, p=periods_needed)


def sinspace(lower: float, upper: float, n: int, p: float = 1.0):
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


def cosspace(lower: float, upper: float, n: int, p: float = 1.0):
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


def map_area(a: NDArray, b: NDArray, fname: str, colormap: ColorMap, skip_empty: bool = True, fps = 15, n=1_000_000, percentile=99, resolution=1000):
    """Generates a animation over a whole area. a, b are the axis (uses np.meshgrid)"""
    assert len(a) == len(b), "a & b dont match in length"
    A, B = np.meshgrid(a, b)

    for i in range(A.shape[0]):
        if i % 2 == 1:
            A[i] = A[i][::-1]
    A = A.flatten()

    # A = A.ravel()
    B = B.ravel()
    process = Performance_Renderer(
        a=A,
        b=B,
        colormap=colormap,
        frames=len(A),
        fps=fps,
        percentile=percentile,
        n=n,
        resolution=resolution
    )
    process.set_static("a", False)
    process.set_static("b", False)
    process.start_render_process(fname, verbose_image=True, threads=4, chunksize=8, skip_empty_frames=skip_empty)