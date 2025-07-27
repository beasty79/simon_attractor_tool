from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
import numpy as np
import cv2


class VideoFileWriter:
    def __init__(self, filename: str, fps: int = 30):
        self.filename = filename
        self.fps = fps
        self.frames = []
        self.frame_size: tuple[int, int] | None = None
        self.is_color = None

    def change_cursor(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

    def add_frame(self, frame: np.ndarray, a: float | None = None, b: float | None = None):
        if self.frame_size is None:
            self.frame_size = (frame.shape[1], frame.shape[0])
            self.is_color = len(frame.shape) == 3

        if (frame.shape[1], frame.shape[0]) != self.frame_size:
            return

        # Convert 4-channel RGBA to BGR
        if len(frame.shape) == 3 and frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)

        # Convert grayscale to BGR
        if not self.is_color and len(frame.shape) == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        # 🆕 Overlay a, b values if provided
        if a is not None and b is not None:
            text = f"a = {a:.4f}, b = {b:.4f}"
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (255, 255, 255), 2, cv2.LINE_AA)
        self.frames.append(frame)

    def save(self, no_cursor_override = False):
        if not self.frames:
            raise ValueError("No frames to write")

        fourcc = cv2.VideoWriter.fourcc(*'mp4v')

        if self.frame_size is None:
            return

        out = cv2.VideoWriter(self.filename, fourcc, self.fps, self.frame_size, isColor=True)

        for frame in self.frames:
            out.write(frame)
        out.release()
        print(f"Video saved to -> '{self.filename}'")
        if not no_cursor_override:
            QApplication.restoreOverrideCursor()
