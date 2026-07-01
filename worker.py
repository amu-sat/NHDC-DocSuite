from pathlib import Path

from PySide6.QtCore import (
    QThread,
    Signal,
)

from pdf_tools import (
    process_pdfs,
)


class Worker(QThread):

    progress = Signal(int)
    status = Signal(str)
    log = Signal(str)

    finished = Signal()

    def __init__(
        self,
        output_folder,
        compress=True,
        split=True,
    ):

        super().__init__()

        self.output_folder = output_folder

        self.compress = compress
        self.split = split

    # -------------------------------------------------

    def run(self):

        try:

            self.status.emit(
                "Processing PDFs..."
            )

            self.progress.emit(35)

            process_pdfs(
                root_folder=self.output_folder,
                compress=self.compress,
                split=self.split,
                logger=self.log.emit,
                progress=self.progress.emit,
                status=self.status.emit,
            )

            self.progress.emit(100)

            self.status.emit(
                "Completed"
            )

        except Exception as e:

            self.log.emit("")

            self.log.emit("=" * 60)

            self.log.emit("ERROR")

            self.log.emit("=" * 60)

            self.log.emit(str(e))

        self.finished.emit()