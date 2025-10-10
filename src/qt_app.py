"""
Minimal PySide6 application skeleton for the budgeting dashboard.
Provides four pages:
- Dashboard
- Table View
- Import / Export / Settings
- Help

This is intentionally lightweight: pages are placeholder widgets to wire navigation.

Dependencies (install before running):
- PySide6
- pandas (for later pages)

Run: python -m src.qt_app or python src/qt_app.py
"""

from pathlib import Path
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QHBoxLayout,
    QFrame,
    QPushButton,
    QMenuBar,
    QFileDialog,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction
 
from pages.dashboard import DashboardPage
from pages.table_view import TableViewPage
from pages.import_export_settings import ImportExportSettingsPage
from pages.help_page import HelpPage


APP_NAME = "Budgeting Dashboard"


# pages are implemented in src/pages/*.py


class MainWindow(QMainWindow):
    def __init__(self, data_dir: Path | None = None):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        # default to 720p window size
        self.resize(1280, 720)
        try:
            # also set a sensible minimum size
            self.setMinimumSize(1024, 600)
        except Exception:
            pass

        self.data_dir = data_dir or (Path(__file__).parent.parent / "data")

        # Menu
        self._create_menu()

        # Main layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Sidebar (navigation)
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(220)
        self.sidebar.setSpacing(6)
        self.sidebar.setFrameShape(QFrame.NoFrame)
        for name in ["Dashboard", "Table View", "Import/Export/Settings", "Help"]:
            it = QListWidgetItem(name)
            it.setSizeHint(QSize(200, 42))
            self.sidebar.addItem(it)
        self.sidebar.currentRowChanged.connect(self.on_nav_changed)

        # Stack for pages
        self.stack = QStackedWidget()
        self._create_pages()

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack, 1)

        # select first page now that stack exists
        self.sidebar.setCurrentRow(0)

        # Status bar
        self.statusBar().showMessage(f"Data folder: {self.data_dir}")

    def _create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open Data Folder", self)
        open_action.triggered.connect(self.open_data_folder)
        file_menu.addAction(open_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _create_pages(self):
        # Dashboard page
        dash = DashboardPage()

        # Table view page
        table = TableViewPage()

        # Import/Export/Settings page
        settings = ImportExportSettingsPage()

        # Help page
        help_p = HelpPage()

        for w in (dash, table, settings, help_p):
            self.stack.addWidget(w)

    def on_nav_changed(self, index: int):
        self.stack.setCurrentIndex(index)

    def open_data_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select data folder", str(self.data_dir))
        if folder:
            self.data_dir = Path(folder)
            self.statusBar().showMessage(f"Data folder: {self.data_dir}")

    def show_about(self):
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(self, "About", f"{APP_NAME}\n\nMinimal prototype built with PySide6.")


def main(argv: list[str] | None = None):
    app = QApplication(argv or [])
    w = MainWindow()
    w.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
