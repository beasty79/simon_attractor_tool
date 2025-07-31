from numpy.typing import NDArray
import matplotlib.pyplot as plt
import numpy as np


def promt(frames, fps):
    t = round(frames / fps, 1)
    print(f"{frames=} {fps=} {t=:.0f}s")
    accept = input("Enter y or yes to Continue: ")
    if accept not in ["y", "Y", "yes", "Yes", "YES"]:
        exit(0)

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
