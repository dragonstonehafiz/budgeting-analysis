from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
    QComboBox,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QLayout,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import Qt, QEvent
import pandas as pd
from utils.data_loader import load_df
from utils.plots import monthly_trend_figure, top_items_bar_chart, category_pie_chart, amount_distribution_pie, rolling_average_figure
from utils.xlsx_handler import remake_xlsx_file
from PySide6.QtWidgets import QMessageBox
import logging
import warnings
import traceback

logger = logging.getLogger(__name__)


class DashboardPage(QWidget):
    """Dashboard page with two tabs: Total and Yearly.

    - Total: overall summary cards and a placeholder for charts
    - Yearly: selector for year and yearly breakdown area

    The page exposes a `set_data(df: pandas.DataFrame)` stub for future wiring.
    """

    def __init__(self):
        super().__init__()
        self._init_ui()

        # attempt to load default data immediately so KPIs are visible
        try:
            # call set_data which will load via load_df() and populate the year selector
            self.set_data()
        except Exception:
            # no-op; UI will show placeholders until data is provided
            pass

    def _init_ui(self):
        # Use a scroll area so the dashboard becomes scrollable when content is tall
        outer_layout = QVBoxLayout(self)

        header = QLabel("<h1>Dashboard</h1>")
        outer_layout.addWidget(header)
        # Controls row (year selector + search) placed outside the scroll area so it stays
        # visible while the rest of the dashboard content scrolls.
        controls_row = QHBoxLayout()
        controls_row.addWidget(QLabel("Select year:"))
        self.year_combo = QComboBox()
        self.year_combo.addItem("All")
        controls_row.addWidget(self.year_combo)
        # search box to filter by Item or Notes (case-insensitive substring)
        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText('Search items or notes...')
        controls_row.addWidget(self._search_box)
        # explicit Search button to trigger filtering
        self._search_button = QPushButton('Search')
        controls_row.addWidget(self._search_button)
        # Remake purchases.xlsx quick action
        self._remake_btn = QPushButton('Remake purchases.xlsx')
        self._remake_btn.setToolTip('Backup and reinitialize purchases.xlsx (sorts rows by Date)')
        self._remake_btn.clicked.connect(self._on_remake_clicked)
        controls_row.addWidget(self._remake_btn)
        # Privacy mode toggle
        from PySide6.QtWidgets import QCheckBox
        self._privacy_mode = QCheckBox('Privacy Mode')
        self._privacy_mode.setToolTip('Hide all monetary values and sensitive data')
        self._privacy_mode.stateChanged.connect(self._on_privacy_mode_changed)
        controls_row.addWidget(self._privacy_mode)
        controls_row.addStretch(1)
        outer_layout.addLayout(controls_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer_layout.addWidget(scroll, 1)

        # content widget inside the scroll area
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        yearly_layout = QVBoxLayout(content_widget)
        # anchor sections to the top so extra vertical space is not distributed between them
        yearly_layout.setAlignment(Qt.AlignTop)
        yearly_layout.setSizeConstraint(QLayout.SetMinimumSize)
        yearly_layout.setSpacing(12)
        content_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

    # initialize sections (each will attach itself to yearly_layout)

        # stats panel
        self._init_stats_section(yearly_layout)

        # monthly overview section
        self._init_overall_data_section(yearly_layout)

        # monthly details section (hidden unless a year is selected)
        self._init_monthly_details_section(yearly_layout)

        # category section
        self._init_category_section(yearly_layout)
        
    
    def _make_section(self, title: str, placeholder_text: str = "") -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QVBoxLayout(frame)
        header = QLabel(f"<b>{title}</b>")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)
        content = QFrame()
        content.setFrameShape(QFrame.NoFrame)
        content_layout = QVBoxLayout(content)
        content_layout.addWidget(QLabel(placeholder_text))
        layout.addWidget(content)
        frame.content = content
        return frame

    def _create_cards_row(self, parent_layout: QVBoxLayout, metrics: tuple[str, ...]):
        cards_row = QHBoxLayout()
        for name in metrics:
            card = QFrame()
            card.setFrameShape(QFrame.StyledPanel)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            card.setMinimumHeight(50) 
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(8, 6, 8, 6)  # Add padding inside cards
            card_layout.setSpacing(2)  # Add spacing between title and value
            title = QLabel(f"<b>{name}</b>")
            value_lbl = QLabel("—")
            value_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            card_layout.addWidget(title)
            card_layout.addWidget(value_lbl)
            cards_row.addWidget(card)
            self._cards[name] = value_lbl
            card.setToolTip("")
            value_lbl.setToolTip("")

        parent_layout.addLayout(cards_row)

    def _init_stats_section(self, parent_layout: QVBoxLayout):
        # Summary cards grouped under a 'Statistics' panel
        self._cards = {}
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.StyledPanel)
        # allow the statistics panel to expand and take available vertical space
        stats_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(12, 8, 12, 8)
        stats_layout.setSpacing(8)
        # remove the fixed-size constraint so the layout can expand
        stats_layout.setSizeConstraint(QLayout.SetMinimumSize)

        stats_header = QLabel("<b>Statistics</b>")
        stats_header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        stats_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        stats_header.setFixedHeight(28)
        stats_layout.addWidget(stats_header)

        # group the cards into the rows you requested
        row1 = ('Total spent', 'Items bought')
        row2 = ('Average spend', 'Lower 25th percentile', 'Median spend', 'Upper 25th percentile', 'Standard deviation')
        row3 = ('Average weekly spend', 'Average monthly spend', 'Average yearly spend', 'Spending volatility')

        self._create_cards_row(stats_layout, row1)
        self._create_cards_row(stats_layout, row2)
        self._create_cards_row(stats_layout, row3)

        # add the stats frame and give it stretch so it fills the column
        parent_layout.addWidget(stats_frame)
        parent_layout.addStretch(1)

    def _init_overall_data_section(self, parent_layout: QVBoxLayout):
        # overall data section contains the monthly trend chart plus two tables
        self.overall_data_section = self._make_section('Overall data')
        parent_layout.addWidget(self.overall_data_section)
        # chart selector: allow picking between Monthly trend and Rolling average
        controls_h = QHBoxLayout()
        controls_h.addWidget(QLabel('Chart:'))
        self._overview_chart_combo = QComboBox()
        self._overview_chart_combo.addItems(['Monthly spending trend', 'Rolling average', 'Cumulative spending'])
        self._overview_chart_combo.setCurrentIndex(0)
        controls_h.addWidget(self._overview_chart_combo)
        controls_h.addStretch(1)
        self._overview_chart_combo.currentTextChanged.connect(self._on_overview_chart_changed)
        self.overall_data_section.content.layout().insertLayout(0, controls_h)
        self._monthly_view = None
        # canvas for top-items bar chart
        self._top_items_view = None
        # canvas for category pie chart
        self._category_pie_view = None
        # canvas for amount distribution (quartile) pie
        self._amount_dist_view = None
        # container frame for small charts row (category + amount distribution)
        self._charts_row = None

        # create a small two-column area under the chart for top/bottom lists
        overall_h = QHBoxLayout()


        # left: top 10 most expensive items
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.addWidget(QLabel('<b>Top 10 most expensive</b>'))
        self._top5_table = QTableWidget()
        self._top5_table.setColumnCount(5)
        self._top5_table.setHorizontalHeaderLabels(['Item', 'Category', 'Cost', 'Date', 'Notes'])
        # make Item and Notes stretch to fill remaining width; others size to contents
        header = self._top5_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Item
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Cost
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Notes
        left_layout.addWidget(self._top5_table)
        try:
            self._set_table_height_for_rows(self._top5_table, rows=10)
        except Exception:
            pass

        overall_h.addWidget(left_frame, 1)

        # attach the overall_h below the content area; the chart will be inserted at index 0
        self.overall_data_section.content.layout().addLayout(overall_h)

    def _init_monthly_details_section(self, parent_layout: QVBoxLayout):
        self.monthly_details_section = self._make_section('Monthly details')
        parent_layout.addWidget(self.monthly_details_section)
        self.monthly_details_section.setVisible(False)

        # Create the table (kept for fallback) and the items area
        self._monthly_table = QTableWidget()
        self._monthly_table.setColumnCount(2)
        self._monthly_table.setHorizontalHeaderLabels(["Month", "Total spent"])
        self._monthly_table.horizontalHeader().setStretchLastSection(True)
        self._monthly_table.setAlternatingRowColors(True)

        # Vertical layout: pie on top, items below
        details_v = QVBoxLayout()

        # Top area: left_frame will hold the pie (and keep the table if needed)
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        left_layout.addWidget(self._monthly_table)
        # placeholder for monthly pie canvas
        self._monthly_pie_view = None

        # Bottom area: items list and month selector
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.addWidget(QLabel('<b>Items bought</b>'))

        right_controls = QHBoxLayout()
        self._month_combo = QComboBox()
        try:
            self._month_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        except Exception:
            pass
        right_controls.addWidget(self._month_combo)
        right_layout.addLayout(right_controls)

        self._items_table = QTableWidget()
        self._items_table.setColumnCount(5)
        self._items_table.setHorizontalHeaderLabels(['Item', 'Category', 'Cost', 'Date', 'Notes'])
        header = self._items_table.horizontalHeader()
        header.setMinimumSectionSize(40)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        self._items_table.setAlternatingRowColors(True)
        # make the items table expand vertically to fill available space
        self._items_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # set minimum height to ensure table takes up significant vertical space
        self._items_table.setMinimumHeight(400)
        right_layout.addWidget(self._items_table)

        # Add placeholders for month-specific charts below the items table
        # Category pie chart for selected month
        self._month_category_pie_view = None
        # Top items chart for selected month
        self._month_top_items_view = None

        details_v.addWidget(left_frame)
        details_v.addWidget(right_frame)

        self._monthly_right_layout = right_layout
        self.monthly_details_section.content.layout().addLayout(details_v)

    def _init_category_section(self, parent_layout: QVBoxLayout):
        self.category_section = self._make_section('Spending by category')
        parent_layout.addWidget(self.category_section)
        # Add controls and placeholders for category-specific views.
        # Place the selector as the first row of the section content.
        content_layout = self.category_section.content.layout()
        controls = QHBoxLayout()
        controls.addWidget(QLabel('Category:'))
        self._category_combo = QComboBox()
        controls.addWidget(self._category_combo)
        controls.addStretch(1)
        # insert controls at top (index 0) so selector remains first row
        try:
            content_layout.insertLayout(0, controls)
        except Exception:
            content_layout.addLayout(controls)

        # placeholder for category-specific top-items chart
        self._category_top_items_view = None
        # table for top 10 most expensive items within the selected category
        self._category_top_table = QTableWidget()
        self._category_top_table.setColumnCount(5)
        self._category_top_table.setHorizontalHeaderLabels(['Item', 'Category', 'Cost', 'Date', 'Notes'])
        hdr = self._category_top_table.horizontalHeader()
        try:
            hdr.setSectionResizeMode(0, QHeaderView.Stretch)
            hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            hdr.setSectionResizeMode(4, QHeaderView.Stretch)
        except Exception:
            pass
        # make table reasonably sized
        try:
            self._set_table_height_for_rows(self._category_top_table, rows=10)
        except Exception:
            pass
        content_layout.addWidget(self._category_top_table)

        # connect handler for category combo changes
        try:
            # disconnect may emit a RuntimeWarning in some PySide6 versions if there was
            # no prior connection; suppress such warnings while attempting to disconnect.
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                self._category_combo.currentTextChanged.disconnect()
        except Exception:
            pass
        self._category_combo.currentTextChanged.connect(lambda txt: self._render_category_details(getattr(self, '_data', getattr(self, '_data_raw', None))))

    def set_data(self, df=None):
        """Public method to update the dashboard from a DataFrame.

        If `df` is None the loader `load_df()` will be used.
        """
        if df is None:
            df = load_df()

        # store raw data and populate year selector, then compute for current selection
        self._data_raw = df.copy()

        # populate years using the Year column when available, otherwise fall back to Date
        if 'Year' in self._data_raw.columns:
            yrs = self._data_raw['Year'].dropna().astype(str).unique().tolist()
            try:
                years = sorted(yrs, key=lambda x: int(x), reverse=True)
            except Exception:
                years = sorted(yrs, reverse=True)
        else:
            years = sorted({str(int(d.year)) for d in self._data_raw['Date'].dropna()}, reverse=True)

        self.year_combo.blockSignals(True)
        self.year_combo.clear()
        self.year_combo.addItem("Last 12 months")
        self.year_combo.addItem("All")
        for y in years:
            self.year_combo.addItem(y)
        self.year_combo.setCurrentIndex(0)
        self.year_combo.blockSignals(False)

        # connect handler (safe to reconnect)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                self.year_combo.currentTextChanged.disconnect()
        except Exception:
            # ignore if not previously connected
            pass
        self.year_combo.currentTextChanged.connect(self._on_year_changed)

        # wire explicit Search button to trigger recompute (user presses when ready)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                self._search_button.clicked.disconnect()
        except Exception:
            pass
        self._search_button.clicked.connect(lambda: self._compute_and_update(self.year_combo.currentText()))

        # compute metrics for the default/current selection
        self._compute_and_update(self.year_combo.currentText())

    def _update_metrics(self, df):
        """Internal: compute metrics from the provided DataFrame and update UI widgets."""
        self._data = df

        # ensure DataFrame has Date parsed
        try:
            df = df.copy()
            if 'Date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['Date']):
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        except Exception:
            df = df

        # base numeric series
        costs = pd.to_numeric(df['Cost'], errors='coerce').fillna(0.0)

        items_bought = int(len(df))
        total_spent = float(costs.sum())

        # monthly totals (period index)
        monthly = df.set_index('Date')['Cost'].resample('MS').sum()
        # active months = months with any spend
        active_months = int((monthly != 0).sum())
        avg_monthly = float(monthly[monthly != 0].mean()) if active_months > 0 else 0.0

        # weekly
        weekly = df.set_index('Date')['Cost'].resample('W').sum()
        avg_weekly = float(weekly[weekly != 0].mean()) if len(weekly) > 0 else 0.0

        median_spend = float(costs.median()) if items_bought > 0 else 0.0
        lower_25 = float(costs.quantile(0.25)) if items_bought > 0 else 0.0
        upper_25 = float(costs.quantile(0.75)) if items_bought > 0 else 0.0
        avg_spend_per_item = float(total_spent / items_bought) if items_bought > 0 else 0.0
        spending_volatility = float(monthly.std()) if len(monthly) > 0 else 0.0

        # additional summary metrics
        avg_spend = float(costs.mean()) if items_bought > 0 else 0.0
        std_tx = float(costs.std()) if items_bought > 0 else 0.0
        yearly = df.set_index('Date')['Cost'].resample('YS').sum()
        active_years = int((yearly != 0).sum())
        avg_yearly = float(yearly[yearly != 0].mean()) if active_years > 0 else 0.0

        # helper formatting
        def _fmt_money(x):
            try:
                return f"${x:,.2f}"
            except Exception:
                return str(x)

        def _fmt_num(x):
            try:
                if isinstance(x, float) and x.is_integer():
                    return str(int(x))
                return f"{x:,}"
            except Exception:
                return str(x)

        # mapping of display name -> formatted value
        mapping = {
            'Total spent': _fmt_money(total_spent),
            'Items bought': _fmt_num(items_bought),
            'Average spend': _fmt_money(avg_spend),
            'Lower 25th percentile': _fmt_money(lower_25),
            'Median spend': _fmt_money(median_spend),
            'Upper 25th percentile': _fmt_money(upper_25),
            'Standard deviation': _fmt_money(std_tx),
            'Avg spend per item': _fmt_money(avg_spend_per_item),
            'Active months': _fmt_num(active_months),
            'Average weekly spend': _fmt_money(avg_weekly),
            'Average monthly spend': _fmt_money(avg_monthly),
            'Average yearly spend': _fmt_money(avg_yearly),
            'Spending volatility': _fmt_money(spending_volatility),
        }

        # tooltips for each metric (plain-language, non-stat wording)
        tooltips = {
            'Total spent': 'Total money spent in the selected data.',
            'Items bought': 'How many purchases or transactions are recorded.',
            'Average spend': 'Typical amount spent for a single purchase: add all purchases and divide by the number of purchases.',
            'Lower 25th percentile': 'A value near the lower end of your purchases — about 25% of purchases are this amount or less (shows cheaper purchases).',
            'Median spend': 'The middle purchase amount — half of your purchases are smaller and half are larger. This avoids being skewed by very large purchases.',
            'Upper 25th percentile': 'A value near the higher end — about 25% of purchases are this amount or more (shows higher-cost purchases).',
            'Standard deviation': 'A simple measure of how different your purchase amounts are. Small = purchases are similar sizes; large = they vary a lot.',
            'Avg spend per item': 'Total spent divided by number of purchases — another way to see typical spend per purchase.',
            'Active months': 'How many months had at least one purchase (used as the basis for monthly averages).',
            'Average weekly spend': 'Typical money spent per week, averaged across weeks with activity.',
            'Average monthly spend': 'Typical money spent per month, averaged across months with activity.',
            'Average yearly spend': 'Typical money spent per year, averaged across years with activity.',
            'Spending volatility': 'How much your monthly spending goes up and down. Higher means spending swings more from month to month.',
        }

        for k, v in mapping.items():
            lbl = self._cards.get(k)
            if lbl is not None:
                # Apply privacy masking
                display_val = self._mask_value(v)
                lbl.setText(display_val)
                tip = tooltips.get(k, '')
                try:
                    lbl.setToolTip(tip)
                    parent = lbl.parent()
                    if hasattr(parent, 'setToolTip'):
                        parent.setToolTip(tip)
                except Exception:
                    pass

    def _compute_and_update(self, selection_text: str):
        """Filter the raw data by year selection and update metrics."""
        if not hasattr(self, '_data_raw') or self._data_raw is None:
            return

        # if 'Last 12 months' show data from the last 12 complete calendar months
        if selection_text == 'Last 12 months':
            try:
                # get the most recent date in the data
                max_date = pd.to_datetime(self._data_raw['Date']).max()
                # get the first day of that month
                month_start = max_date.replace(day=1)
                # go back 11 months (to include the current month = 12 total complete months)
                twelve_months_ago = month_start - pd.DateOffset(months=11)
                df_sel = self._data_raw[pd.to_datetime(self._data_raw['Date']) >= twelve_months_ago]
            except Exception:
                df_sel = self._data_raw
        # if 'All' show full data
        elif not selection_text or selection_text == 'All':
            df_sel = self._data_raw
        else:
            # try parse year
            try:
                y = int(selection_text)
                df_sel = self._data_raw[self._data_raw['Date'].dt.year == y]
            except Exception:
                df_sel = self._data_raw

        # apply search box filter if present (filter Item or Notes columns)
        try:
            search_term = ''
            try:
                search_term = self._search_box.text().strip()
            except Exception:
                search_term = ''

            if search_term:
                # defensive: ensure columns exist and cast to str for matching
                try:
                    mask_item = df_sel['Item'].astype(str).str.contains(search_term, case=False, na=False) if 'Item' in df_sel.columns else pd.Series(False, index=df_sel.index)
                except Exception:
                    mask_item = pd.Series(False, index=df_sel.index)
                try:
                    mask_notes = df_sel['Notes'].astype(str).str.contains(search_term, case=False, na=False) if 'Notes' in df_sel.columns else pd.Series(False, index=df_sel.index)
                except Exception:
                    mask_notes = pd.Series(False, index=df_sel.index)

                try:
                    df_sel = df_sel[mask_item | mask_notes]
                except Exception:
                    # if indexing fails, leave df_sel unchanged
                    pass
        except Exception:
            # non-fatal: if search filtering fails, ignore and continue
            pass

        # hand off to update function
        self._update_metrics(df_sel)
        # render the monthly overview chart for this selection
        try:
            self._render_monthly_overview(df_sel)
        except Exception:
            # keep UI stable if plotting fails
            pass

        # render monthly details table when a specific year is selected
        try:
            if selection_text and selection_text not in ('All', 'Last 12 months'):
                # df_sel is already filtered to the chosen year in _compute_and_update
                self._render_monthly_details(df_sel)
            else:
                # hide details for All and Last 12 months
                try:
                    self.monthly_details_section.setVisible(False)
                except Exception:
                    pass
        except Exception:
            pass

        # update category section (top items + table) with current filtered data
        try:
            self._render_category_details(df_sel)
        except Exception:
            pass

    def eventFilter(self, watched, event):
        # respond to resize events on the items table viewport to recompute column widths
        if watched is not None and event.type() == QEvent.Resize:
            if hasattr(self, '_items_table') and self._items_table is not None:
                # recalc ratios when the viewport resizes
                self._apply_items_column_ratios()
        return super().eventFilter(watched, event)

    def _apply_items_column_ratios(self):
        """Apply proportional column widths so the items table fills its area.

        Ratios: Item=0.55, Category=0.15, Cost=0.10, Date=0.10, Notes=0.10
        """
        try:
            table = self._items_table
            header = table.horizontalHeader()
            try:
                header.setSectionResizeMode(QHeaderView.Fixed)
            except Exception:
                pass

            # Fixed widths (pixels) — pick values that look good for most data
            fixed_widths = {
                0: 480,  # Item
                1: 220,  # Category
                2: 100,  # Cost
                3: 110,  # Date
                4: 240,  # Notes
            }

            for col, w in fixed_widths.items():
                try:
                    table.setColumnWidth(col, w)
                except Exception:
                    pass
        except Exception:
            pass

    def _set_table_height_for_rows(self, table: QTableWidget, rows: int = 10, row_height: int | None = None):
        """Set fixed height for `table` so it displays `rows` rows without vertical scroll."""
        try:
            if row_height is None:
                row_height = table.verticalHeader().defaultSectionSize() or 20
            header_h = table.horizontalHeader().height() or 24
            frame_margin = 8
            total_h = header_h + (row_height * rows) + frame_margin
            table.setMinimumHeight(total_h)
            table.setMaximumHeight(total_h)
            try:
                table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            except Exception:
                pass
        except Exception:
            pass

    def _clear_overall_canvases(self):
        """Remove and delete any existing canvases in the overall data section.

        This keeps the layout from accumulating duplicate widgets and ensures
        figures are released. It's safe to call even if canvases are None.
        """
        try:
            layout = self.overall_data_section.content.layout()

            # Remove monthly canvas if present
            mv = getattr(self, '_monthly_view', None)
            if mv is not None:
                layout.removeWidget(mv)
                mv.deleteLater()
                self._monthly_view = None

            # Remove top-items canvas if present
            tv = getattr(self, '_top_items_view', None)
            if tv is not None:
                layout.removeWidget(tv)
                tv.deleteLater()
                self._top_items_view = None

            # Remove category pie canvas if present
            cp = getattr(self, '_category_pie_view', None)
            if cp is not None:
                layout.removeWidget(cp)
                cp.deleteLater()
                self._category_pie_view = None
            # Remove amount distribution canvas if present
            ad = getattr(self, '_amount_dist_view', None)
            if ad is not None:
                layout.removeWidget(ad)
                ad.deleteLater()
                self._amount_dist_view = None
            # Remove charts row container if present
            cr = getattr(self, '_charts_row', None)
            if cr is not None:
                try:
                    layout.removeWidget(cr)
                except Exception:
                    pass
                cr.deleteLater()
                self._charts_row = None
        except Exception:
            logger.exception("Failed to clear existing overall canvases")

    def _render_monthly_overview(self, df_sel: pd.DataFrame):
        """Render the monthly overview using matplotlib canvas and populate overall tables."""
        try:
            # Clear any previous canvases and create new ones
            self._clear_overall_canvases()

            # choose which chart to show based on selector
            sel = self._overview_chart_combo.currentText()

            # Check privacy mode
            privacy_mode = self._privacy_mode.isChecked() if hasattr(self, '_privacy_mode') else False

            if sel == 'Rolling average':
                self._monthly_view = rolling_average_figure(df_sel, title=f"{3}-month rolling average", hide_values=privacy_mode)
            elif sel == 'Cumulative spending':
                from utils.plots import cumulative_spending_figure
                self._monthly_view = cumulative_spending_figure(df_sel, title="Cumulative Spending", hide_values=privacy_mode)
            else:
                self._monthly_view = monthly_trend_figure(df_sel, title="Monthly Spending Trend", hide_values=privacy_mode)

            self._monthly_view.setMinimumHeight(300)
            # insert after the controls layout so the chart selector remains the first row
            self.overall_data_section.content.layout().insertWidget(1, self._monthly_view)

            # create a horizontal container to hold the two donut charts side-by-side
            charts_frame = QFrame()
            charts_layout = QHBoxLayout(charts_frame)
            charts_layout.setContentsMargins(0, 0, 0, 0)

            # category pie canvas
            self._category_pie_view = category_pie_chart(df_sel, title="Spending by category", hide_values=privacy_mode)
            self._category_pie_view.setMinimumHeight(260)
            charts_layout.addWidget(self._category_pie_view, 1)

            # amount distribution canvas (quartile)
            self._amount_dist_view = amount_distribution_pie(df_sel, title="Spend by transaction quartile", hide_values=privacy_mode)
            self._amount_dist_view.setMinimumHeight(260)
            charts_layout.addWidget(self._amount_dist_view, 1)

            # store the container so we can remove it cleanly later
            self._charts_row = charts_frame
            # charts row goes after the main chart
            self.overall_data_section.content.layout().insertWidget(2, self._charts_row)

            # top-items canvas
            self._top_items_view = top_items_bar_chart(df_sel, top_n=10, title="Top items by spend", hide_values=privacy_mode)
            # top items come after the charts row
            self.overall_data_section.content.layout().insertWidget(3, self._top_items_view)

            # populate top5 / bottom5 tables using full df_sel
            df = df_sel.copy()
            if 'Date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['Date']):
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df['Cost'] = pd.to_numeric(df.get('Cost', pd.Series([])), errors='coerce').fillna(0.0)

            # top 10 most expensive
            top5 = df.sort_values('Cost', ascending=False).head(10)
            self._top5_table.setRowCount(len(top5))
            for r, (_, row) in enumerate(top5.iterrows()):
                item = row.get('Item', '')
                cat = row.get('Category', '')
                cost = row.get('Cost', 0.0)
                notes = row.get('Notes', '')
                date_val = row.get('Date')
                date_str = pd.to_datetime(date_val).strftime('%Y-%m-%d') if pd.notna(date_val) else str(date_val)
                
                # Apply privacy masking to cost only
                cost_display = self._mask_money(float(cost))
                
                self._top5_table.setItem(r, 0, QTableWidgetItem(str(item)))
                self._top5_table.setItem(r, 1, QTableWidgetItem(str(cat)))
                self._top5_table.setItem(r, 2, QTableWidgetItem(cost_display))
                self._top5_table.setItem(r, 3, QTableWidgetItem(date_str))
                self._top5_table.setItem(r, 4, QTableWidgetItem(str(notes)))

            # right-side least-expensive table removed per user request
        except Exception as e:
            logger.exception("Failed rendering monthly overview")
            # Show error message if canvas creation failed
            error_label = QLabel(f"Chart rendering failed: {e}")
            error_label.setWordWrap(True)
            error_label.setStyleSheet("color: red;")
            self._monthly_view = error_label
            # keep selector as first row; insert error message after it
            self.overall_data_section.content.layout().insertWidget(1, self._monthly_view)

    def _on_overview_chart_changed(self):
        """Handle chart selector changes by re-rendering the monthly overview.

        Uses the current filtered data (self._data) when available, otherwise
        falls back to the raw data loaded into the dashboard.
        """
        try:
            df_sel = getattr(self, '_data', None)
            if df_sel is None:
                df_sel = getattr(self, '_data_raw', None)
            if df_sel is None:
                return
            self._render_monthly_overview(df_sel)
        except Exception:
            pass

    def _on_remake_clicked(self):
        # Confirmation dialog before running the potentially-destructive action
        try:
            resp = QMessageBox.question(self, "Remake purchases.xlsx",
                                        "This will create a backup and overwrite 'data/purchases.xlsx'. Continue?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if resp != QMessageBox.Yes:
                return

            # Get the app's data directory from the main window
            try:
                main_window = self.window()
                if hasattr(main_window, 'data_dir'):
                    purchases_path = str(main_window.data_dir / "purchases.xlsx")
                else:
                    # fallback to relative path
                    purchases_path = "data/purchases.xlsx"
            except Exception:
                purchases_path = "data/purchases.xlsx"
            remake_xlsx_file(purchases_path)
            QMessageBox.information(self, "Remake complete", "purchases.xlsx has been backed up and remade successfully.")
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            full_traceback = traceback.format_exc()
            
            detailed_error = f"Error Type: {error_type}\n\nError Message:\n{error_msg}\n\nFull Traceback:\n{full_traceback}"
            
            try:
                QMessageBox.critical(self, "Remake failed", f"Remaking purchases.xlsx failed:\n\n{detailed_error}")
            except Exception:
                pass
            logger.exception('Remake failed')


    def _render_category_details(self, df_sel: pd.DataFrame):
        """Render the category selector, top-items chart for the selected category, and the top-10 table."""
        try:
            if df_sel is None:
                return

            df = df_sel.copy()
            if 'Category' not in df.columns or 'Cost' not in df.columns:
                return

            # populate category combo with available categories (preserve 'All')
            # Populate combo only if choices changed; preserve current selection.
            try:
                existing = [self._category_combo.itemText(i) for i in range(self._category_combo.count())]
            except Exception:
                existing = []

            try:
                cats = sorted([str(c) for c in df['Category'].dropna().unique()])
            except Exception:
                cats = []

            new_items = cats
            try:
                if existing != new_items:
                    # preserve previous selection if still present
                    prev = None
                    try:
                        prev = self._category_combo.currentText()
                    except Exception:
                        prev = None

                    self._category_combo.blockSignals(True)
                    self._category_combo.clear()
                    for it in new_items:
                        self._category_combo.addItem(it)
                    # restore previous selection if possible, otherwise default to highest-spend category
                    if prev and prev in new_items:
                        idx = new_items.index(prev)
                        try:
                            self._category_combo.setCurrentIndex(idx)
                        except Exception:
                            pass
                    else:
                        try:
                            if len(new_items) > 0:
                                # find category with highest spend
                                category_totals = df.groupby('Category')['Cost'].sum().sort_values(ascending=False)
                                if not category_totals.empty:
                                    top_category = str(category_totals.index[0])
                                    if top_category in new_items:
                                        idx = new_items.index(top_category)
                                        self._category_combo.setCurrentIndex(idx)
                                    else:
                                        self._category_combo.setCurrentIndex(0)
                                else:
                                    self._category_combo.setCurrentIndex(0)
                        except Exception:
                            pass
                    self._category_combo.blockSignals(False)
            except Exception:
                pass

            # determine selected category (user selection should be preserved)
            try:
                sel = self._category_combo.currentText()
            except Exception:
                sel = 'All'

            # filter df to selected category if not 'All'
            if sel and sel != 'All':
                try:
                    df_cat = df[df['Category'].astype(str) == str(sel)].copy()
                except Exception:
                    df_cat = df.copy()
            else:
                df_cat = df.copy()

            # remove any existing category chart canvas
            try:
                if getattr(self, '_category_top_items_view', None) is not None:
                    try:
                        # the chart was added to the content layout; remove it safely
                        parent = self._category_top_items_view.parent()
                        if parent is not None and hasattr(parent, 'layout'):
                            try:
                                parent.layout().removeWidget(self._category_top_items_view)
                            except Exception:
                                pass
                        self._category_top_items_view.deleteLater()
                    except Exception:
                        pass
                    self._category_top_items_view = None
            except Exception:
                pass

            # create top-items bar chart for this category
            try:
                from utils.plots import top_items_bar_chart
                privacy_mode = self._privacy_mode.isChecked() if hasattr(self, '_privacy_mode') else False
                chart = top_items_bar_chart(df_cat, top_n=10, title=f"Top items — {sel if sel else 'All'}", hide_values=privacy_mode)
                chart.setMinimumHeight(240)
                # insert chart above the top table in the category content area
                try:
                    self.category_section.content.layout().insertWidget(1, chart)
                except Exception:
                    try:
                        self.category_section.content.layout().addWidget(chart)
                    except Exception:
                        pass
                self._category_top_items_view = chart
            except Exception:
                pass

            # populate top-10 table using df_cat
            try:
                df_cat = df_cat.copy()
                if 'Date' in df_cat.columns and not pd.api.types.is_datetime64_any_dtype(df_cat['Date']):
                    df_cat['Date'] = pd.to_datetime(df_cat['Date'], errors='coerce')
                df_cat['Cost'] = pd.to_numeric(df_cat.get('Cost', pd.Series([])), errors='coerce').fillna(0.0)

                top10 = df_cat.sort_values('Cost', ascending=False).head(10)
                self._category_top_table.setRowCount(len(top10))
                for r, (_, row) in enumerate(top10.iterrows()):
                    item = row.get('Item', '')
                    cat = row.get('Category', '')
                    cost = row.get('Cost', 0.0)
                    notes = row.get('Notes', '')
                    date_val = row.get('Date')
                    date_str = pd.to_datetime(date_val).strftime('%Y-%m-%d') if pd.notna(date_val) else str(date_val)
                    
                    # Apply privacy masking to cost only
                    cost_display = self._mask_money(float(cost))
                    
                    self._category_top_table.setItem(r, 0, QTableWidgetItem(str(item)))
                    self._category_top_table.setItem(r, 1, QTableWidgetItem(str(cat)))
                    self._category_top_table.setItem(r, 2, QTableWidgetItem(cost_display))
                    self._category_top_table.setItem(r, 3, QTableWidgetItem(date_str))
                    self._category_top_table.setItem(r, 4, QTableWidgetItem(str(notes)))
            except Exception:
                try:
                    self._category_top_table.setRowCount(0)
                except Exception:
                    pass
        except Exception:
            # do not crash the dashboard; log and continue
            try:
                logger.exception('Failed rendering category details')
            except Exception:
                pass

    def _render_monthly_details(self, df_sel: pd.DataFrame):
        """Populate the monthly details table for the provided (already-filtered) DataFrame.

        If `df_sel` corresponds to a single year (all Date values share the same
        year) this function will display all 12 months for that year (zero-filled
        months shown as $0.00). Otherwise it shows months present in `df_sel`.
        If the selection has no data the details section will be hidden.
        """
        try:
            df = df_sel.copy()
            if 'Date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['Date']):
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

            # ensure numeric costs
            df['Cost'] = pd.to_numeric(df.get('Cost', pd.Series([])), errors='coerce').fillna(0.0)

            # infer year from df_sel: if all dates share a single year, show full 12 months
            months = None
            inferred_year = None
            try:
                years_in_data = pd.DatetimeIndex(df['Date'].dropna()).year.unique()
                if len(years_in_data) == 1:
                    inferred_year = int(years_in_data[0])
                    try:
                        months = pd.date_range(start=f"{inferred_year}-01-01", periods=12, freq='MS')
                    except Exception:
                        months = None
            except Exception:
                inferred_year = None

            # resample monthly
            if not df.empty:
                monthly = df.set_index('Date')['Cost'].resample('MS').sum()
            else:
                monthly = pd.Series(dtype=float)

            # if we inferred a single year, reindex to ensure all 12 months are present
            if inferred_year is not None and months is not None:
                monthly = monthly.reindex(months, fill_value=0.0)

            # If there's no data, hide the details section
            if monthly.empty:
                try:
                    self.monthly_details_section.setVisible(False)
                except Exception:
                    pass
                return

            # populate table rows. If we inferred a single year, iterate the 12-month list
            if inferred_year is not None and months is not None:
                rows = []
                for dt in months:
                    try:
                        val = float(monthly.loc[dt]) if dt in monthly.index else float(0.0)
                    except Exception:
                        try:
                            val = float(monthly.get(dt, 0.0))
                        except Exception:
                            val = 0.0
                    rows.append((dt.strftime('%b %Y'), f"${val:,.2f}"))
            else:
                rows = [(dt.strftime('%b %Y'), f"${val:,.2f}") for dt, val in monthly.items()]

            # Instead of populating the left table, create a month-share pie chart
            try:
                # clean up existing pie if present
                if getattr(self, '_monthly_pie_view', None) is not None:
                    try:
                        self._monthly_pie_view.setParent(None)
                        self._monthly_pie_view.deleteLater()
                    except Exception:
                        pass
                    self._monthly_pie_view = None

                # build a pandas Series of monthly totals for the pie
                monthly_series = monthly.copy()
                # create pie canvas using helper in utils.plots
                try:
                    from utils.plots import monthly_pie_chart
                    privacy_mode = self._privacy_mode.isChecked() if hasattr(self, '_privacy_mode') else False
                    pie = monthly_pie_chart(monthly_series, title='Month share', hide_values=privacy_mode)
                    pie.setMinimumHeight(260)
                    # hide the textual table and insert pie into the left layout
                    try:
                        self._monthly_table.setVisible(False)
                    except Exception:
                        pass
                    # place pie in the same parent layout as the table
                    parent = self._monthly_table.parent()
                    if parent is not None and hasattr(parent, 'layout'):
                        try:
                            parent.layout().addWidget(pie)
                            self._monthly_pie_view = pie
                        except Exception:
                            # fallback: attach to overall right layout if insertion fails
                            try:
                                self._monthly_right_layout.addWidget(pie)
                                self._monthly_pie_view = pie
                            except Exception:
                                pass
                except Exception:
                    # if pie creation fails, fall back to table rendering below
                    pass
            except Exception:
                pass

            # ensure columns/widgets are sized
            try:
                self._monthly_table.resizeColumnsToContents()
            except Exception:
                pass
            try:
                # ensure it displays all 12 months without scrolling when a year is selected
                self._set_table_height_for_rows(self._monthly_table, rows=12)
            except Exception:
                pass
            try:
                self.monthly_details_section.setVisible(True)
            except Exception:
                pass
            # populate right-side charts: monthly bar + category pie
            # populate month selector and items table on the right
            try:
                # prepare monthly index labels
                months = [dt.strftime('%b %Y') for dt in monthly.index]

                # populate month combo
                try:
                    self._month_combo.blockSignals(True)
                    self._month_combo.clear()
                    for m in months:
                        self._month_combo.addItem(m)
                    # default to the first month if available
                    if months:
                        self._month_combo.setCurrentIndex(0)
                    else:
                        # no months available
                        try:
                            self._month_combo.setCurrentIndex(-1)
                        except Exception:
                            pass
                finally:
                    try:
                        self._month_combo.blockSignals(False)
                    except Exception:
                        pass

                # helper to populate items for a given month label
                def _populate_items_for(month_label: str):
                    try:
                        items_df = df_sel.copy()
                        if 'Date' in items_df.columns and not pd.api.types.is_datetime64_any_dtype(items_df['Date']):
                            items_df['Date'] = pd.to_datetime(items_df['Date'], errors='coerce')

                        # require a valid month label (no 'All' option anymore)
                        if not month_label:
                            # nothing selected -> clear table and charts
                            try:
                                self._items_table.setRowCount(0)
                            except Exception:
                                pass
                            # clear month-specific charts
                            try:
                                if self._month_category_pie_view is not None:
                                    self._monthly_right_layout.removeWidget(self._month_category_pie_view)
                                    self._month_category_pie_view.deleteLater()
                                    self._month_category_pie_view = None
                                if self._month_top_items_view is not None:
                                    self._monthly_right_layout.removeWidget(self._month_top_items_view)
                                    self._month_top_items_view.deleteLater()
                                    self._month_top_items_view = None
                            except Exception:
                                pass
                            return

                        dt = pd.to_datetime(month_label, format='%b %Y', errors='coerce')
                        if pd.isna(dt):
                            # invalid label -> clear table and charts
                            try:
                                self._items_table.setRowCount(0)
                            except Exception:
                                pass
                            try:
                                if self._month_category_pie_view is not None:
                                    self._monthly_right_layout.removeWidget(self._month_category_pie_view)
                                    self._month_category_pie_view.deleteLater()
                                    self._month_category_pie_view = None
                                if self._month_top_items_view is not None:
                                    self._monthly_right_layout.removeWidget(self._month_top_items_view)
                                    self._month_top_items_view.deleteLater()
                                    self._month_top_items_view = None
                            except Exception:
                                pass
                            return

                        # filter to the chosen month
                        items_df = items_df[(items_df['Date'].dt.year == dt.year) & (items_df['Date'].dt.month == dt.month)]
                        item_col = 'Item' if 'Item' in items_df.columns else None

                        # ensure expected columns exist
                        if 'Category' not in items_df.columns:
                            items_df['Category'] = ''
                        if 'Cost' not in items_df.columns:
                            items_df['Cost'] = 0.0
                        if 'Notes' not in items_df.columns:
                            items_df['Notes'] = ''

                        # populate table: Item, Category, Cost, Date, Notes
                        items = items_df.sort_values('Date')
                        self._items_table.setRowCount(len(items))
                        for r, (_, row) in enumerate(items.iterrows()):
                            # Item/description
                            item_val = row.get(item_col, '') if item_col else ''
                            cat = row.get('Category', '')
                            cost = row.get('Cost', 0.0)
                            notes = row.get('Notes', '')
                            # date display
                            date_str = ''
                            try:
                                date_str = pd.to_datetime(row.get('Date')).strftime('%Y-%m-%d')
                            except Exception:
                                date_str = str(row.get('Date', ''))

                            # Apply privacy masking to cost only
                            cost_display = self._mask_money(float(cost))

                            self._items_table.setItem(r, 0, QTableWidgetItem(str(item_val)))
                            self._items_table.setItem(r, 1, QTableWidgetItem(str(cat)))
                            self._items_table.setItem(r, 2, QTableWidgetItem(cost_display))
                            self._items_table.setItem(r, 3, QTableWidgetItem(date_str))
                            self._items_table.setItem(r, 4, QTableWidgetItem(str(notes)))

                        # Create/update month-specific charts below the table
                        # Remove old charts first
                        try:
                            if self._month_category_pie_view is not None:
                                self._monthly_right_layout.removeWidget(self._month_category_pie_view)
                                self._month_category_pie_view.deleteLater()
                                self._month_category_pie_view = None
                            if self._month_top_items_view is not None:
                                self._monthly_right_layout.removeWidget(self._month_top_items_view)
                                self._month_top_items_view.deleteLater()
                                self._month_top_items_view = None
                        except Exception:
                            pass

                        # Create new charts for this month's data
                        try:
                            from utils.plots import category_pie_chart, top_items_bar_chart
                            
                            privacy_mode = self._privacy_mode.isChecked() if hasattr(self, '_privacy_mode') else False
                            
                            # Category pie for selected month
                            if not items_df.empty:
                                self._month_category_pie_view = category_pie_chart(
                                    items_df, 
                                    title=f"Spending by category — {month_label}",
                                    hide_values=privacy_mode
                                )
                                self._month_category_pie_view.setMinimumHeight(260)
                                self._monthly_right_layout.addWidget(self._month_category_pie_view)

                                # Top items for selected month
                                self._month_top_items_view = top_items_bar_chart(
                                    items_df, 
                                    top_n=10, 
                                    title=f"Top items — {month_label}",
                                    hide_values=privacy_mode
                                )
                                self._month_top_items_view.setMinimumHeight(240)
                                self._monthly_right_layout.addWidget(self._month_top_items_view)
                        except Exception:
                            pass

                    except Exception:
                        # clear table on error
                        try:
                            self._items_table.setRowCount(0)
                        except Exception:
                            pass

                # connect handler
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore')
                        self._month_combo.currentTextChanged.disconnect()
                except Exception:
                    pass
                self._month_combo.currentTextChanged.connect(_populate_items_for)

                # populate initially with the first month (no 'All' option)
                if months:
                    _populate_items_for(months[0])
                else:
                    _populate_items_for('')
            except Exception:
                # if something goes wrong, hide details as fallback
                try:
                    self.monthly_details_section.setVisible(False)
                except Exception:
                    pass
        except Exception:
            # keep UI stable on errors
            try:
                self.monthly_details_section.setVisible(False)
            except Exception:
                pass

    def _on_year_changed(self, text: str):
        # recompute metrics for selected year
        self._compute_and_update(text)
        # Show or hide the per-year monthly breakdown section depending on selection
        try:
            if hasattr(self, 'monthly_details_section'):
                if not text or text in ('All', 'Last 12 months'):
                    self.monthly_details_section.setVisible(False)
                else:
                    self.monthly_details_section.setVisible(True)
        except Exception:
            pass

    def _on_privacy_mode_changed(self):
        """Handle privacy mode toggle - refresh all views with masked/unmasked data."""
        try:
            # Re-render everything with current selection
            year_text = self.year_combo.currentText() if hasattr(self, 'year_combo') else 'All'
            self._compute_and_update(year_text)
        except Exception:
            pass

    def _mask_value(self, value: str) -> str:
        """Return masked version of value if privacy mode is enabled."""
        if hasattr(self, '_privacy_mode') and self._privacy_mode.isChecked():
            return '***'
        return value

    def _mask_money(self, amount: float) -> str:
        """Return masked money value if privacy mode enabled, otherwise formatted."""
        if hasattr(self, '_privacy_mode') and self._privacy_mode.isChecked():
            return '$***'
        try:
            return f"${amount:,.2f}"
        except Exception:
            return str(amount)

