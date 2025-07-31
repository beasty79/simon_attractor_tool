from script.api import sinspace, cosspace, bpmspace, Performance_Renderer
from script.utils import ColorMap
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
    process.start_render_process("osc.mp4", verbose_image=False, threads=10, chunksize=4)


def main():
    # map_area(a, b, "./render/map_full_10k.mp4", ColorMap("viridis"))

    a = sinspace(-0.067, -0.099, 1500, p=4)
    b = sinspace(1.854, 1.873, 1500)

    cmap = ColorMap("viridis", True)
    process = Performance_Renderer(
        a=a,
        b=b,
        colormap=cmap,
        frames=len(a),
        fps=60,
        percentile=99,
        n=5_000_000,
        resolution=1000
    )
    process.start_render_process("render.mp4", verbose_image=False, threads=8)

if __name__ == "__main__":
    main()
