import matplotlib.pyplot as plt
import numpy as np
from PyQt6.QtWidgets import QFileDialog


def promt(frames, fps):
    t = round(frames / fps, 1)
    print(f"{frames=} {fps=} {t=:.0f}s")
    accept = input("Enter y or yes to Continue: ")
    if accept not in ["y", "Y", "yes", "Yes", "YES"]:
        exit(0)


def make_filename(a_1, a_2, b_1, b_2, extension="mp4"):
    parts = []
    if a_1 != a_2:
        parts.append(f"a_{a_1}-{a_2}")
    if b_1 != b_2:
        parts.append(f"b_{b_1}-{b_2}")

    fname = "_".join(parts) + f".{extension}"
    return fname


def get_save_filename(cls):
    file_path, _ = QFileDialog.getSaveFileName(
        parent=cls,
        caption="Save Video File",
        filter="MP4 files (*.mp4);;All Files (*)",
        directory="render.mp4"
    )
    return file_path