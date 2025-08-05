from PyQt6.QtWidgets import QFileDialog


def get_save_filename(cls):
    file_path, _ = QFileDialog.getSaveFileName(
        parent=cls,
        caption="Save Video File",
        filter="MP4 files (*.mp4);;All Files (*)",
        directory="render.mp4"
    )
    return file_path
