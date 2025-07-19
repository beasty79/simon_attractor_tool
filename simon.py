import matplotlib.pyplot as plt
from scipy.ndimage import zoom
from functools import wraps
from math import sin, cos
from numpy import ndarray
from numba import njit
import numpy as np
import timeit
import sys


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = timeit.default_timer()
        result = func(*args, **kwargs)
        end = timeit.default_timer()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

# @timer
@njit
def iterate(a: float, b: float, n: int) -> tuple[ndarray, ndarray]:
    x, y = a, b

    arr_x = np.zeros(shape=(n,), dtype=np.float64)
    arr_y = np.zeros(shape=(n,), dtype=np.float64)
    for i in range(n):
        x_new = sin(x**2 - y**2 + a)
        y_new = cos(2 * x * y + b)

        x, y = x_new, y_new
        arr_x[i] = x
        arr_y[i] = y

    return arr_x, arr_y


def render(colors, resolution: int = 1000, a: float = 0.54, b: float = 1.23, n: int=100_000_000, output_resolution=None, percentile=None):
    x_raw, y_raw = iterate(a, b, n)
    h, _, _ = np.histogram2d(x_raw, y_raw, bins=resolution)

    if percentile is None:
        percentile = 95
    clip_max = np.percentile(h, percentile)
    if clip_max == 0 or np.isnan(clip_max):
        clip_max = 1

    h_normalized = h / clip_max
    h_normalized = np.clip(h_normalized, 0, 1)

    # cmap = plt.get_cmap('viridis')
    # linear = np.linspace(0, 1, 256)
    # colors = cmap(linear)

    values = (h_normalized * 255).astype(int)
    img = (colors[values] * 255).astype(np.uint8)

    if output_resolution is None or output_resolution == resolution:
        return img
    else:
        # Compute zoom factors for height, width, channels (channels = 1, so no zoom on that axis)
        zoom_factors = (
            output_resolution / resolution,
            output_resolution / resolution,
            1
        )
        # Use scipy.ndimage.zoom with order=1 for bilinear interpolation
        img_resized = zoom(img, zoom_factors, order=1)
        return img_resized.astype(np.uint8)