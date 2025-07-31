from numpy.typing import NDArray
from numba import njit, prange
from functools import wraps
# from math import sin, cos
# from math import sin, cos
import math
from numpy import ndarray
from typing import Any
import numpy as np
import timeit


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = timeit.default_timer()
        result = func(*args, **kwargs)
        end = timeit.default_timer()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@njit
def iterate(a: float, b: float, n: int) -> tuple[ndarray, ndarray]:
    x, y = a, b

    arr_x = np.zeros(shape=(n,), dtype=np.float64)
    arr_y = np.zeros(shape=(n,), dtype=np.float64)
    for i in range(n):
        x_new = math.sin(x**2 - y**2 + a)
        y_new = math.cos(2 * x * y + b)

        x, y = x_new, y_new
        arr_x[i] = x
        arr_y[i] = y

    return arr_x, arr_y


def render(colors: np.typing.NDArray[np.float32], resolution: int, a: float, b: float, n: int, percentile: float):
    """This Calcultes the image using a, b be the inital value for the iterations the Simon Attractor

    Args:
        colors (np.typing.NDArray[np.float32]): colormap_values in range [0;1]
        resolution (int): how many pixels are generated (resxres) scales O(n**2) so be carefull
        a_initial (float):
        b_initial (float):
        n (int): higher values will improve the output scales O(n)
        percentile (float): This makes sure to the colormaps range is properly utilized usually between (95-99.9)

    Returns:
        image as a numpy array in shape
    """
    x_raw, y_raw = iterate(a, b, n)
    histogramm, _, _ = np.histogram2d(x_raw, y_raw, bins=resolution)
    if percentile is None:
        percentile = 95
    clip_max = np.percentile(histogramm, percentile)
    if clip_max == 0 or np.isnan(clip_max):
        clip_max = 1
    h_normalized = histogramm / clip_max
    h_normalized = np.clip(h_normalized, 0, 1)
    values = (h_normalized * 255).astype(int)
    img = (colors[values] * 255).astype(np.uint8)
    return img


def render_raw(resolution: int, a: float, b: float, n: int, percentile: float, current_percentile_max: int = 0) -> tuple[NDArray[np.float32], Any]:
    """
    same as render but it doesnt apply the colormaps yet
    Computes a normalized 2D histogram of the Simon Attractor iterations.
    Args:
        resolution (int): The resolution of the output grid (res x res). Be cautious: runtime ~ O(n^2).
        a (float): Parameter 'a' for the Simon Attractor.
        b (float): Parameter 'b' for the Simon Attractor.
        n (int): Number of iterations. Higher values yield smoother output.
        percentile (float | None): Upper clipping percentile for normalization. Typical values: 95–99.9.

    Returns:
        NDArray[np.float32]: A normalized (0.0–1.0) 2D array representing the histogram density.
    """
    x_raw, y_raw = iterate(a, b, n)
    histogram, _, _ = np.histogram2d(x_raw, y_raw, bins=resolution)

    clip_max = np.percentile(histogram, percentile)
    clip_max = clip_max if clip_max > current_percentile_max else current_percentile_max
    if clip_max == 0 or np.isnan(clip_max):
        clip_max = 1.0
    h_normalized = histogram / clip_max
    h_normalized = np.clip(h_normalized, 0, 1)
    return h_normalized.astype(np.float32), clip_max


def to_img(h_normalized: NDArray[np.float32], colors: NDArray[np.float32]) -> NDArray[np.uint8]:
    values = (h_normalized * 255).astype(int)
    values = np.clip(values, 0, 255)
    img = (colors[values] * 255).astype(np.uint8)
    return img



@njit(parallel=True)
def parallel_iterate(a_list, b_list, n):
    num_frames = len(a_list)
    # Pre-allocate output arrays
    x_all = np.zeros((num_frames, n), dtype=np.float64)
    y_all = np.zeros((num_frames, n), dtype=np.float64)

    for i in prange(num_frames):
        x_raw, y_raw = iterate(a_list[i], b_list[i], n)
        x_all[i, :] = x_raw
        y_all[i, :] = y_raw
    return x_all, y_all


def render_parallel(colors: NDArray[np.float32], resolution: int, a_list: NDArray, b_list: NDArray, n: int, percentile: float) -> NDArray[np.uint8]:
    """
    Parallel rendering of multiple Simon Attractor frames for lists of (a, b) parameters.

    Args:
        colors (npt.NDArray[np.float32]): colormap values in range [0;1]
        resolution (int): output image resolution (res x res)
        a_list (List[float]): list of 'a' initial values
        b_list (List[float]): list of 'b' initial values
        n (int): number of iterations per frame
        percentile (float): histogram percentile for normalization

    Returns:
        npt.NDArray[np.uint8]: stacked images, shape (len(a_list), resolution, resolution, 3)
    """
    print(type(colors), resolution, a_list, n, percentile)
    # Run all iterations in parallel
    x_all, y_all = parallel_iterate(a_list, b_list, n)

    images = []
    for i in range(len(a_list)):
        img = render(
            colors=colors,
            resolution=resolution,
            a=0.0,  # dummy, won't be used since we override below
            b=0.0,
            n=n,
            percentile=percentile
        )

        # Here's a minimal inline hack for now:
        histogramm, _, _ = np.histogram2d(x_all[i], y_all[i], bins=resolution)
        clip_max = np.percentile(histogramm, percentile)
        if clip_max == 0 or np.isnan(clip_max):
            clip_max = 1
        h_normalized = histogramm / clip_max
        h_normalized = np.clip(h_normalized, 0, 1)
        values = (h_normalized * 255).astype(int)
        img = (colors[values] * 255).astype(np.uint8)
        images.append(img)
    return np.stack(images)


def test_render_parallel():
    # Create a simple colormap: 256 colors, RGB, float32 in [0,1]
    colors = np.linspace(0, 1, 256, dtype=np.float32)
    colors = np.stack([colors, colors, colors], axis=1)  # grayscale colormap shape (256,3)

    resolution = 64  # small resolution for quick test
    a_list = np.array([0.1, 0.5, 0.9], dtype=np.float64)
    b_list = np.array([0.2, 0.6, 1.0], dtype=np.float64)
    n = 1000  # iterations count
    percentile = 95.0

    # Call render_parallel
    images = render_parallel(colors, resolution, a_list, b_list, n, percentile)

    # Assertions
    assert isinstance(images, np.ndarray), "Output should be a numpy array"
    assert images.shape == (len(a_list), resolution, resolution, 3), f"Output shape mismatch: {images.shape}"
    assert images.dtype == np.uint8, "Output dtype should be uint8"
    print("render_parallel test passed.")