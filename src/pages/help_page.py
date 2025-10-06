from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class HelpPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title_lbl = QLabel("<h2>Help</h2>")
        layout.addWidget(title_lbl)
        layout.addWidget(QLabel("User guide and troubleshooting info."))
        layout.addStretch(1)
