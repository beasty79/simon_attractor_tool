from api import sinspace, cosspace, bpmspace, Performance_Renderer
from utils import ColorMap
import numpy as np


def example():
    # constants
    t = 1 * 60
    fps = 100
    bpm = 155

    # creating input args for every frame
    frames = t * fps
    a = sinspace(0.33, 0.36, frames, p=4)
    b = cosspace(1.45, 1.55, frames, p=2)
    p = bpmspace(98.75, 99.35, frames, bpm, fps)

    process = Performance_Renderer(
        a=a,
        b=b,
        colormap=ColorMap("twilight", True),
        frames=frames,
        fps=fps,
        percentile=p,
        n=10_000_000,
        resolution=1500
    )

    # set to static so it accepts the array as input arg
    process.set_static("a", False)
    process.set_static("b", False)
    process.set_static("percentile", False)

    # (resolution=1k) per frame 2.8Mb
    # max memory usage is threads * chunksize * 2.8Mb
    process.start_render_process("./render/osc.mp4", verbose_image=False, threads=10, chunksize=4)


if __name__ == "__main__":
    example()
