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


    def add_frame(self, frame: np.ndarray):
        if self.frame_size is None:
            # Set frame size and color mode based on first frame
            self.frame_size = (frame.shape[1], frame.shape[0])
            self.is_color = len(frame.shape) == 3

        # Validate size consistency
        if (frame.shape[1], frame.shape[0]) != self.frame_size:
            return

            # Check for 4 channels (RGBA)
        if len(frame.shape) == 3 and frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
            # frame = frame[:, :, :3]

        # Convert grayscale to BGR if needed
        if not self.is_color and len(frame.shape) == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        self.frames.append(frame)

    def save(self):
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
        QApplication.restoreOverrideCursor()
