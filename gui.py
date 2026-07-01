from pathlib import Path

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QProgressBar,
    QMessageBox,
    QCheckBox,
)

from worker import Worker
from zip_tools import extract_all_zips
from duplicate import (
    scan_duplicates,
    apply_choice,
)
from duplicate_dialog import DuplicateDialog


class MainWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.worker = None

        self.setWindowTitle(
            "NHDC Document Suite"
        )

        self.resize(850, 650)

        self.build_ui()

    # ----------------------------------------------------

    def build_ui(self):

        layout = QVBoxLayout(self)

        title = QLabel(
            "NHDC Document Suite"
        )

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            QLabel{
                font-size:22px;
                font-weight:bold;
            }
        """)

        layout.addWidget(title)

        # ----------------------------------------------

        grp = QGroupBox("Main Folder")

        h = QHBoxLayout()

        self.txt_input = QLineEdit()

        btn = QPushButton("Browse")

        btn.clicked.connect(
            self.select_input
        )

        h.addWidget(self.txt_input)

        h.addWidget(btn)

        grp.setLayout(h)

        layout.addWidget(grp)

        # ----------------------------------------------

        grp = QGroupBox("Output Folder")

        h = QHBoxLayout()

        self.txt_output = QLineEdit()

        btn = QPushButton("Browse")

        btn.clicked.connect(
            self.select_output
        )

        h.addWidget(self.txt_output)

        h.addWidget(btn)

        grp.setLayout(h)

        layout.addWidget(grp)

        # ----------------------------------------------

        grp = QGroupBox("Options")

        v = QVBoxLayout()

        self.chk_duplicates = QCheckBox(
            "Detect duplicate PDFs"
        )

        self.chk_duplicates.setChecked(True)

        self.chk_compress = QCheckBox(
            "Compress PDF if >20 MB"
        )

        self.chk_compress.setChecked(True)

        self.chk_split = QCheckBox(
            "Split if still >20 MB"
        )

        self.chk_split.setChecked(True)

        v.addWidget(
            self.chk_duplicates
        )

        v.addWidget(
            self.chk_compress
        )

        v.addWidget(
            self.chk_split
        )

        grp.setLayout(v)

        layout.addWidget(grp)

        # ----------------------------------------------

        self.lbl_status = QLabel("Ready")

        layout.addWidget(
            self.lbl_status
        )

        self.progress = QProgressBar()

        self.progress.setValue(0)

        layout.addWidget(
            self.progress
        )

        self.log = QTextEdit()

        self.log.setReadOnly(True)

        layout.addWidget(
            self.log
        )

        # ----------------------------------------------

        h = QHBoxLayout()

        self.btn_start = QPushButton(
            "Start"
        )

        self.btn_exit = QPushButton(
            "Exit"
        )

        self.btn_start.clicked.connect(
            self.start_processing
        )

        self.btn_exit.clicked.connect(
            self.close
        )

        h.addStretch()

        h.addWidget(
            self.btn_start
        )

        h.addWidget(
            self.btn_exit
        )

        layout.addLayout(h)

    # ----------------------------------------------------

    def add_log(self, text):

        self.log.append(text)

    # ----------------------------------------------------

    def select_input(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Main Folder"
        )

        if folder:

            self.txt_input.setText(folder)

    # ----------------------------------------------------

    def select_output(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder"
        )

        if folder:

            self.txt_output.setText(folder)

    # ----------------------------------------------------

    def start_processing(self):

        input_folder = self.txt_input.text().strip()

        output_folder = self.txt_output.text().strip()

        if not input_folder:

            QMessageBox.warning(
                self,
                "Input Folder",
                "Please select Main Folder."
            )

            return

        if not output_folder:

            QMessageBox.warning(
                self,
                "Output Folder",
                "Please select Output Folder."
            )

            return

        self.log.clear()

        self.progress.setValue(0)

        self.btn_start.setEnabled(False)

        self.lbl_status.setText(
            "Extracting ZIP files..."
        )

        try:

            extract_all_zips(
                input_folder,
                output_folder,
                self.add_log,
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "ZIP Extraction",
                str(e)
            )

            self.btn_start.setEnabled(True)

            return

        self.progress.setValue(20)

        if self.chk_duplicates.isChecked():

            self.lbl_status.setText(
                "Scanning duplicates..."
            )

            duplicates = scan_duplicates(
                output_folder
            )
                    # ----------------------------------------------
        # Duplicate Handling
        # ----------------------------------------------

            if duplicates:

                self.add_log("")
                self.add_log(
                    f"{len(duplicates)} duplicate(s) found."
                )

                dialog = DuplicateDialog(
                    duplicates,
                    self
                )

                if dialog.exec():

                    apply_choice(
                        duplicates,
                        dialog.choice
                    )

                    self.add_log(
                        "Duplicate action applied."
                    )

                else:

                    self.btn_start.setEnabled(True)

                    self.lbl_status.setText(
                        "Cancelled"
                    )

                    return

            else:

                self.add_log(
                    "No duplicate PDFs found."
                )

        self.lbl_status.setText(
            "Processing PDFs..."
        )

        # ----------------------------------------------
        # Start Worker
        # ----------------------------------------------

        self.worker = Worker(
            output_folder=output_folder,
            compress=self.chk_compress.isChecked(),
            split=self.chk_split.isChecked(),
        )

        self.worker.progress.connect(
            self.progress.setValue
        )

        self.worker.status.connect(
            self.lbl_status.setText
        )

        self.worker.log.connect(
            self.add_log
        )

        self.worker.finished.connect(
            self.processing_finished
        )

        self.worker.start()

    # ----------------------------------------------------

    def processing_finished(self):

        self.progress.setValue(100)

        self.lbl_status.setText(
            "Completed"
        )

        self.btn_start.setEnabled(True)

        self.add_log("")
        self.add_log("=" * 60)
        self.add_log("Processing Completed")
        self.add_log("=" * 60)

        QMessageBox.information(
            self,
            "NHDC Document Suite",
            "Processing completed successfully."
        )

    # ----------------------------------------------------

    def closeEvent(self, event):

        if (
            self.worker is not None
            and self.worker.isRunning()
        ):

            reply = QMessageBox.question(
                self,
                "Exit",
                "Processing is still running.\n\nExit anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.No:

                event.ignore()

                return

            self.worker.terminate()

            self.worker.wait()

        event.accept()