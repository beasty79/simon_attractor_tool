from script.api import (
    sinspace, cosspace, bpmspace, map_area,
    Performance_Renderer, ColorMap
)
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
    # a = np.linspace(-0.084, -0.1, 30)
    # b = np.linspace(1.85, 1.875, 30)
    # map_area(a, b, "map_small_area", ColorMap("viridis"), n=1_000_000, skip_empty=False)

    fps = 10
    t = 30
    frames = fps * t

    # a = sinspace(-0.067, -0.099, frames, p=4)
    a = bpmspace(-0.0759, -0.076, frames, 120, fps)
    # b = bpmspace(1.866, 1.867, frames, 150, fps)
    b = sinspace(1.854, 1.873, frames)

    cmap = ColorMap("viridis", True)
    process = Performance_Renderer(
        a=a,
        b=b,
        colormap=cmap,
        frames=frames,
        fps=fps,
        percentile=99.6,
        n=7_000_000,
        resolution=1000
    )
    process.set_static("a", False)
    process.set_static("b", False)
    process.start_render_process("render.mp4", verbose_image=True, threads=12)

if __name__ == "__main__":
    main()
