from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ImportExportSettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title_lbl = QLabel("<h2>Import / Export / Settings</h2>")
        layout.addWidget(title_lbl)
        layout.addWidget(QLabel("Import CSV/XLSX, configure data path, and backups."))
        layout.addStretch(1)
