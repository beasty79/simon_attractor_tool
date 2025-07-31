import sys

class TerminalCounter:
    def __init__(self, max_i):
        self.max_i = max_i
        self.i = 0
        self._update_terminal()

    def count_up(self):
        if self.i < self.max_i:
            self.i += 1
            self._update_terminal()

    def _update_terminal(self):
        sys.stdout.write(f"\rframe ({self.i}/{self.max_i})")
        sys.stdout.flush()
