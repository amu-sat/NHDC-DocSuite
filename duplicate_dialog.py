from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
    QHeaderView,
)

from PySide6.QtCore import Qt


class DuplicateDialog(QDialog):

    KEEP_ORIGINAL = 0
    KEEP_DUPLICATE = 1
    KEEP_BOTH = 2

    def __init__(self, duplicates, parent=None):

        super().__init__(parent)

        self.choice = self.KEEP_BOTH

        self.setWindowTitle("Duplicate PDFs Found")

        self.resize(900, 500)

        layout = QVBoxLayout(self)

        lbl = QLabel(
            "Duplicate PDF files were detected.\n"
            "Choose how you want to proceed."
        )

        lbl.setAlignment(Qt.AlignCenter)

        layout.addWidget(lbl)

        self.table = QTableWidget()

        self.table.setColumnCount(2)

        self.table.setHorizontalHeaderLabels(
            [
                "Original PDF",
                "Duplicate PDF",
            ]
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.setRowCount(len(duplicates))

        for row, (original, duplicate) in enumerate(duplicates):

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(str(original))
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(str(duplicate))
            )

        layout.addWidget(self.table)

        buttons = QHBoxLayout()

        btn_original = QPushButton("Keep Original")

        btn_duplicate = QPushButton("Keep Duplicate")

        btn_both = QPushButton("Keep Both")

        btn_cancel = QPushButton("Cancel")

        btn_original.clicked.connect(
            self.keep_original
        )

        btn_duplicate.clicked.connect(
            self.keep_duplicate
        )

        btn_both.clicked.connect(
            self.keep_both
        )

        btn_cancel.clicked.connect(
            self.reject
        )

        buttons.addStretch()

        buttons.addWidget(btn_original)

        buttons.addWidget(btn_duplicate)

        buttons.addWidget(btn_both)

        buttons.addWidget(btn_cancel)

        layout.addLayout(buttons)

    # ------------------------------------------

    def keep_original(self):

        self.choice = self.KEEP_ORIGINAL

        self.accept()

    # ------------------------------------------

    def keep_duplicate(self):

        self.choice = self.KEEP_DUPLICATE

        self.accept()

    # ------------------------------------------

    def keep_both(self):

        self.choice = self.KEEP_BOTH

        self.accept()