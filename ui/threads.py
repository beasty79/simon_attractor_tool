from PyQt6.QtCore import QThread, pyqtSignal
from script.api import Performance_Renderer, ColorMap
from time import time

class RenderWorker(QThread):
    finished = pyqtSignal(float, int)
    progress = pyqtSignal(int)

    def __init__(self, values_a, values_b, fname, fps, colormap_name, res, n, percentile, invert: bool = False, verbose = False):
        super().__init__()
        self.values_a = values_a
        self.values_b = values_b
        self.fname = fname
        self.verbose = verbose

        # init Multiproccessing Renderer
        self.renderer = Performance_Renderer(
            a=values_a,
            b=values_b,
            colormap=ColorMap(colormap_name, invert),
            frames=len(values_a),
            fps=fps,
            n=n,
            resolution=res,
            percentile=percentile
        )
        # a, b are numpy arrays so they are given as dynamic args
        self.renderer.set_static("a", False)
        self.renderer.set_static("b", False)

        # feedback instead of terminal progress
        self.renderer.addHook(self.progress)

    def run(self):
        t1 = time()
        self.renderer.start_render_process(self.fname, verbose_image=self.verbose, threads=8, chunksize=8, skip_empty_frames=False, bypass_confirm=True)
        elapsed = time() - t1
        self.finished.emit(elapsed, len(self.values_a))