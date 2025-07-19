import multiprocessing
from simon import render
from queue import Queue



class Renderer:
    def __init__(self, a: list[float], b: list[float], filename: str) -> None:
        self.a = a
        self.b = b
        self.fname = filename
        self.thread_safe_queue = Queue()

    def render_all_frames(self):

        ...

def Thread(qu: Queue, *args):
    frame = render(*args)
    qu.put(frame)