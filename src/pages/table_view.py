from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableView,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QLineEdit,
    QToolButton,
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, QSize
from PySide6.QtGui import QBrush, QFontMetrics

from utils.data_loader import load_df


class DataFrameModel(QAbstractTableModel):
    """A simple Qt model to display a pandas DataFrame."""

    def __init__(self, df=None, parent=None):
        super().__init__(parent)
        self._df = df if df is not None else None

    def setDataFrame(self, df):
        self.beginResetModel()
        self._df = df
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if self._df is None else len(self._df)

    def columnCount(self, parent=QModelIndex()):
        return 0 if self._df is None else len(self._df.columns)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if self._df is None:
            return None
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            try:
                return str(self._df.columns[section])
            except Exception:
                return None
        else:
            return str(self._df.index[section])

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or self._df is None:
            return None
        value = self._df.iat[index.row(), index.column()]
        if role == Qt.DisplayRole:
            # Format datetimes nicely
            if hasattr(value, 'strftime'):
                try:
                    return value.strftime('%Y-%m-%d')
                except Exception:
                    return str(value)
            return str(value)
        if role == Qt.TextAlignmentRole:
            # right align numbers
            if isinstance(value, (int, float)):
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter
        if role == Qt.BackgroundRole:
            # subtle stripe for NaNs
            import pandas as pd

            if pd.isna(value):
                return QBrush(Qt.yellow).color().lighter(170)
        return None

    def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder) -> None:
        """Sort the underlying DataFrame by the given column index.

        Uses pandas sorting so numeric and datetime columns sort correctly.
        """
        if self._df is None:
            return
        try:
            colname = self._df.columns[column]
        except Exception:
            return

        ascending = order == Qt.AscendingOrder

        # Perform sort using pandas. Use stable sort to keep row order predictable.
        try:
            # Use beginResetModel/endResetModel to notify views
            self.beginResetModel()
            # If column contains NaT or NaN, pandas will place them at the end by default
            self._df = self._df.sort_values(by=colname, ascending=ascending, kind='mergesort').reset_index(drop=True)
            self.endResetModel()
        except Exception:
            # Fallback: do nothing on error
            try:
                self.endResetModel()
            except Exception:
                pass


class DataFrameFilterProxy(QSortFilterProxyModel):
    """Proxy model that filters rows by a substring only on Item and Notes columns."""

    def __init__(self, parent=None, item_col_name='Item', notes_col_name='Notes'):
        super().__init__(parent)
        self._filter_string = ''
        self.item_col_name = item_col_name
        self.notes_col_name = notes_col_name

    def setFilterString(self, s: str):
        self._filter_string = (s or '').strip()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent) -> bool:
        if not self._filter_string:
            return True
        src = self.sourceModel()
        if src is None:
            return True
        # Try to access underlying DataFrame if available for faster checks
        df = getattr(src, '_df', None)
        if df is not None:
            # ensure row is within bounds
            try:
                if source_row < 0 or source_row >= len(df):
                    return False
                row = df.iloc[source_row]
                for col in (self.item_col_name, self.notes_col_name):
                    if col in row.index:
                        val = str(row[col])
                        if self._filter_string.lower() in val.lower():
                            return True
            except Exception:
                pass

        # Fallback to querying the source model's data method
        try:
            # Try Item column
            model = src
            for col_idx in range(model.columnCount()):
                header = model.headerData(col_idx, Qt.Horizontal, Qt.DisplayRole)
                if header in (self.item_col_name, self.notes_col_name):
                    idx = model.index(source_row, col_idx)
                    data = model.data(idx, Qt.DisplayRole)
                    if data and self._filter_string.lower() in str(data).lower():
                        return True
        except Exception:
            pass

        return False

    def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder) -> None:
        """Map proxy column to source DataFrame column and sort the source model.

        This ensures numeric/date columns are sorted using pandas rather than
        lexicographic string sorting.
        """
        src = self.sourceModel()
        if src is None:
            return
        # Determine header name at proxy column
        header = self.headerData(column, Qt.Horizontal, Qt.DisplayRole)
        try:
            df = getattr(src, '_df', None)
            if df is not None:
                # find source column index by name
                cols = list(df.columns)
                try:
                    src_col = cols.index(header)
                except ValueError:
                    # fallback to 0
                    src_col = column
            else:
                # fallback: try to match header via source model
                src_col = None
                for i in range(src.columnCount()):
                    if src.headerData(i, Qt.Horizontal, Qt.DisplayRole) == header:
                        src_col = i
                        break
                if src_col is None:
                    src_col = column

            # Call source model's sort
            if hasattr(src, 'sort'):
                src.sort(src_col, order)
                # ensure view updates
                self.invalidate()
        except Exception:
            # ignore failures to keep UI responsive
            pass


class TableViewPage(QWidget):
    def __init__(self, default_path: str = "data/purchases.xlsx"):
        super().__init__()
        self._default_path = default_path
        self._df = None

        layout = QVBoxLayout(self)
        title_lbl = QLabel("<h2>Table View</h2>")
        layout.addWidget(title_lbl)

        # Top control row with reload button
        ctl_row = QHBoxLayout()
        reload_btn = QPushButton("Reload")
        reload_btn.clicked.connect(self.reload)
        ctl_row.addWidget(reload_btn)
        ctl_row.addStretch(1)
        layout.addLayout(ctl_row)

        # Search row (below reload) — search only Item and Notes
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        # no placeholder text by user request; start empty
        self.search_input.setPlaceholderText("")
        self.search_input.setToolTip("Type to filter rows where Item or Notes contain the given text (case-insensitive).")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        search_row.addWidget(self.search_input)

        # help tool button with tooltip (small '?')
        help_btn = QToolButton()
        help_btn.setText("?")
        help_btn.setAutoRaise(True)
        help_btn.setToolTip("Searches only the Item and Notes columns (case-insensitive substring).")
        help_btn.setFixedSize(QSize(20, 20))
        search_row.addWidget(help_btn)
        search_row.addStretch(1)
        layout.addLayout(search_row)

        # Table view
        self.table = QTableView()
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table, 1)

        # Model and proxy
        self.model = DataFrameModel()
        self.proxy_model = DataFrameFilterProxy(self, item_col_name='Item', notes_col_name='Notes')
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.table.setModel(self.proxy_model)

        # attempt to load default data (no crash on failure)
        try:
            self.load_data(self._default_path)
        except Exception as e:
            # show small warning but keep UI usable
            QMessageBox.warning(self, "Load data", f"Could not load data: {e}")

    def load_data(self, filepath: str | None = None):
        path = filepath or self._default_path
        df = load_df(path)
        self._df = df
        # reset model
        self.model.setDataFrame(df.reset_index(drop=True))
        # adjust column widths to user-specified heuristics
        self.adjust_column_widths(df)

    def reload(self):
        try:
            self.load_data(self._default_path)
            QMessageBox.information(self, "Reload", "Data reloaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Reload error", str(e))

    def on_search_text_changed(self, text: str):
        # Forward the literal substring to the custom proxy (filters Item and Notes)
        if hasattr(self.proxy_model, 'setFilterString'):
            self.proxy_model.setFilterString(text)
        else:
            self.proxy_model.setFilterFixedString(text)

    def adjust_column_widths(self, df):
        """Adjust column widths based on heuristics and actual content.

        Uses font metrics to convert character width to pixels and applies a
        small padding ('sum leeway').
        """
        fm = QFontMetrics(self.table.font())

        # mapping of column name -> representative example string
        patterns = {
            'Cost': '0000.00',
            'Date': '9999-99-99',
            'Month': 'November',
            'MonthNum': '99',
            'Year': '9999',
        }

        # general padding to allow for cell margins, sort indicators, and small sums
        padding_pixels = 12

        # iterate through columns in displayed order
        for col_idx, col_name in enumerate(df.columns):
            header = str(col_name)

            # Determine the sample string to measure.
            # Avoid using the absolute longest cell (can be an outlier). Instead use the 90th-percentile length.
            sample = header
            try:
                col_series = df[col_name].astype(str)
                lengths = col_series.str.len()
                if len(lengths) > 0:
                    qlen = int(lengths.quantile(0.90))
                    # find a value at or above the 90th percentile length
                    candidates = col_series[lengths >= qlen]
                    if len(candidates) > 0:
                        sample = str(candidates.iloc[0])
                    else:
                        sample = str(col_series.iloc[0])
            except Exception:
                sample = header

            # Column-specific truncation to avoid huge widths from long notes/items
            if col_name in ('Notes', 'Item'):
                max_chars = 40
                if len(sample) > max_chars:
                    sample = sample[: max_chars - 1] + '…'

            # Use pattern examples for certain columns as well
            candidates = [header, sample]
            if col_name in patterns:
                candidates.append(patterns[col_name])

            # pick the longest candidate for sizing
            chosen = max(candidates, key=len)

            # measure in pixels and set width
            width = fm.horizontalAdvance(chosen) + padding_pixels
            # add a little more for numeric columns to allow for alignment
            if col_name == 'Cost':
                width += 24

            # Apply minimum and maximum safeguards
            min_w, max_w = 64, 900
            width = max(min_w, min(max_w, int(width)))

            self.table.setColumnWidth(col_idx, width)
