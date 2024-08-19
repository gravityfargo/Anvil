from PySide6.QtCore import QObject, QRunnable, Signal

from .ansible import anvilrun


class WorkerSignals(QObject):
    finished = Signal(bool)
    message = Signal(dict)


class Worker(QRunnable):
    def __init__(self, play, progress_signal):
        super(Worker, self).__init__()
        self.play = play
        self.signals = WorkerSignals()

    def run(self):
        try:
            anvilrun(self.play, self.signals.message)
            self.signals.finished.emit(True)  # Emit finished signal with success=True
        except Exception as e:
            self.signals.finished.emit(False)  # Emit finished signal with success=False
            raise e  # Optionally re-raise the exception
