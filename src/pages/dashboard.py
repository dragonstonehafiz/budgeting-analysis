from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
    QComboBox,
    QScrollArea,
    QLayout,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import Qt, QEvent
import pandas as pd
from utils.data_loader import load_df
from utils.plots import monthly_trend_figure


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

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer_layout.addWidget(scroll, 1)

        # content widget inside the scroll area
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        yearly_layout = QVBoxLayout(content_widget)
        # anchor sections to the top so extra vertical space is not distributed between them
        try:
            yearly_layout.setAlignment(Qt.AlignTop)
            yearly_layout.setSizeConstraint(QLayout.SetMinimumSize)
            yearly_layout.setSpacing(12)
        except Exception:
            pass
        try:
            content_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        except Exception:
            pass

        # initialize sections (each will attach itself to yearly_layout)
        # Year selector (kept here so it's visually above the stats panel)
        controls_row = QHBoxLayout()
        controls_row.addWidget(QLabel("Select year:"))
        self.year_combo = QComboBox()
        self.year_combo.addItem("All")
        controls_row.addWidget(self.year_combo)
        controls_row.addStretch(1)
        yearly_layout.addLayout(controls_row)

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
            try:
                card.setMinimumHeight(50)  # Increased from 44 to 80 for proper text display
            except Exception:
                pass
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
        try:
            # remove the fixed-size constraint so the layout can expand
            stats_layout.setSizeConstraint(QLayout.SetMinimumSize)
        except Exception:
            pass

        stats_header = QLabel("<b>Statistics</b>")
        stats_header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        stats_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        try:
            stats_header.setFixedHeight(28)
        except Exception:
            pass
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
        try:
            parent_layout.addStretch(1)
        except Exception:
            pass

    def _init_overall_data_section(self, parent_layout: QVBoxLayout):
        # overall data section contains the monthly trend chart plus two tables
        self.overall_data_section = self._make_section('Overall data')
        parent_layout.addWidget(self.overall_data_section)
        self._monthly_view = None

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
        try:
            header = self._top5_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)  # Item
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Category
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Cost
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Date
            header.setSectionResizeMode(4, QHeaderView.Stretch)  # Notes
        except Exception:
            pass
        left_layout.addWidget(self._top5_table)

        # right: top 10 least expensive items
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.addWidget(QLabel('<b>Top 10 least expensive</b>'))
        self._bottom5_table = QTableWidget()
        self._bottom5_table.setColumnCount(5)
        self._bottom5_table.setHorizontalHeaderLabels(['Item', 'Category', 'Cost', 'Date', 'Notes'])
        try:
            header = self._bottom5_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.Stretch)
        except Exception:
            pass
        right_layout.addWidget(self._bottom5_table)

        overall_h.addWidget(left_frame, 1)
        overall_h.addWidget(right_frame, 1)

        # attach the overall_h below the content area; the chart will be inserted at index 0
        self.overall_data_section.content.layout().addLayout(overall_h)

    def _init_monthly_details_section(self, parent_layout: QVBoxLayout):
        self.monthly_details_section = self._make_section('Monthly details')
        parent_layout.addWidget(self.monthly_details_section)
        self.monthly_details_section.setVisible(False)

        # left: monthly totals, right: items list for selected month
        self._monthly_table = QTableWidget()
        self._monthly_table.setColumnCount(2)
        self._monthly_table.setHorizontalHeaderLabels(["Month", "Total spent"])
        self._monthly_table.horizontalHeader().setStretchLastSection(True)
        self._monthly_table.setAlternatingRowColors(True)

        details_h = QHBoxLayout()

        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        try:
            left_frame.setMaximumWidth(240)
            left_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        except Exception:
            pass
        left_layout.addWidget(self._monthly_table)

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
        try:
            header = self._items_table.horizontalHeader()
            try:
                header.setMinimumSectionSize(40)
            except Exception:
                pass
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.Stretch)
        except Exception:
            pass
        self._items_table.setAlternatingRowColors(True)
        right_layout.addWidget(self._items_table)
        right_layout.addStretch(1)

        details_h.addWidget(left_frame, 1)
        details_h.addWidget(right_frame, 2)

        self._monthly_right_layout = right_layout
        self.monthly_details_section.content.layout().addLayout(details_h)

    def _init_category_section(self, parent_layout: QVBoxLayout):
        self.category_section = self._make_section('Spending by category')
        parent_layout.addWidget(self.category_section)

    def set_data(self, df=None):
        """Public method to update the dashboard from a DataFrame.

        If `df` is None the loader `load_df()` will be used.
        """
        if df is None:
            df = load_df()

        # store raw data and populate year selector, then compute for current selection
        self._data_raw = df.copy()

        # populate years using the Year column when available, otherwise fall back to Date
        try:
            if 'Year' in self._data_raw.columns:
                yrs = self._data_raw['Year'].dropna().astype(str).unique().tolist()
                try:
                    years = sorted(yrs, key=lambda x: int(x))
                except Exception:
                    years = sorted(yrs)
            else:
                years = sorted({str(int(d.year)) for d in self._data_raw['Date'].dropna()})
        except Exception:
            years = []

        self.year_combo.blockSignals(True)
        self.year_combo.clear()
        self.year_combo.addItem("All")
        for y in years:
            self.year_combo.addItem(y)
        self.year_combo.setCurrentIndex(0)
        self.year_combo.blockSignals(False)

        # connect handler (safe to reconnect)
        try:
            self.year_combo.currentTextChanged.disconnect()
        except Exception:
            pass
        self.year_combo.currentTextChanged.connect(self._on_year_changed)

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
                lbl.setText(v)
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

        # if 'All' show full data
        if not selection_text or selection_text == 'All':
            df_sel = self._data_raw
        else:
            # try parse year
            try:
                y = int(selection_text)
                df_sel = self._data_raw[self._data_raw['Date'].dt.year == y]
            except Exception:
                df_sel = self._data_raw

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
            if selection_text and selection_text != 'All':
                # pass year as int if possible
                try:
                    year_int = int(selection_text)
                except Exception:
                    year_int = None
                self._render_monthly_details(df_sel, year=year_int)
            else:
                # hide details for All
                try:
                    self.monthly_details_section.setVisible(False)
                except Exception:
                    pass
        except Exception:
            pass

    def eventFilter(self, watched, event):
        # respond to resize events on the items table viewport to recompute column widths
        try:
            if watched is not None and event.type() == QEvent.Resize:
                if hasattr(self, '_items_table') and self._items_table is not None:
                    # recalc ratios when the viewport resizes
                    try:
                        self._apply_items_column_ratios()
                    except Exception:
                        pass
        except Exception:
            pass
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

    def _render_monthly_overview(self, df_sel: pd.DataFrame):
        """Render the monthly overview using matplotlib canvas and populate overall tables."""
        try:
            new_canvas = monthly_trend_figure(df_sel, title="Monthly Spending Trend")

            # Remove old canvas if it exists
            if self._monthly_view is not None:
                try:
                    self.overall_data_section.content.layout().removeWidget(self._monthly_view)
                    self._monthly_view.deleteLater()
                except Exception:
                    pass

            # Add new canvas
            self._monthly_view = new_canvas
            self._monthly_view.setMinimumHeight(300)
            # Insert before any existing widgets (index 0)
            try:
                self.overall_data_section.content.layout().insertWidget(0, self._monthly_view)
            except Exception:
                pass

            # populate top5 / bottom5 tables using full df_sel
            try:
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
                    date_str = ''
                    try:
                        date_str = pd.to_datetime(row.get('Date')).strftime('%Y-%m-%d')
                    except Exception:
                        date_str = str(row.get('Date', ''))
                    self._top5_table.setItem(r, 0, QTableWidgetItem(str(item)))
                    self._top5_table.setItem(r, 1, QTableWidgetItem(str(cat)))
                    self._top5_table.setItem(r, 2, QTableWidgetItem(f"${float(cost):,.2f}"))
                    self._top5_table.setItem(r, 3, QTableWidgetItem(date_str))
                    self._top5_table.setItem(r, 4, QTableWidgetItem(str(notes)))

                # top 10 least expensive (exclude zero-cost rows if you prefer)
                bottom5 = df.sort_values('Cost', ascending=True).head(10)
                self._bottom5_table.setRowCount(len(bottom5))
                for r, (_, row) in enumerate(bottom5.iterrows()):
                    item = row.get('Item', '')
                    cat = row.get('Category', '')
                    cost = row.get('Cost', 0.0)
                    notes = row.get('Notes', '')
                    date_str = ''
                    try:
                        date_str = pd.to_datetime(row.get('Date')).strftime('%Y-%m-%d')
                    except Exception:
                        date_str = str(row.get('Date', ''))
                    self._bottom5_table.setItem(r, 0, QTableWidgetItem(str(item)))
                    self._bottom5_table.setItem(r, 1, QTableWidgetItem(str(cat)))
                    self._bottom5_table.setItem(r, 2, QTableWidgetItem(f"${float(cost):,.2f}"))
                    self._bottom5_table.setItem(r, 3, QTableWidgetItem(date_str))
                    self._bottom5_table.setItem(r, 4, QTableWidgetItem(str(notes)))
            except Exception:
                # ignore table population errors but keep the chart
                pass

        except Exception as e:
            # Show error message if canvas creation failed
            if self._monthly_view is None:
                error_label = QLabel(f"Chart rendering failed: {e}")
                error_label.setWordWrap(True)
                error_label.setStyleSheet("color: red;")
                self._monthly_view = error_label
                try:
                    self.overall_data_section.content.layout().insertWidget(0, self._monthly_view)
                except Exception:
                    pass

    def _render_monthly_details(self, df_sel: pd.DataFrame, year: int | None = None):
        """Populate the monthly details table for a specific year.

        Shows each month (Jan..Dec) and total spent for that month. If `year` is
        provided, the table will show all 12 months of that year (missing months
        shown as $0.00). If the selection has no data the details section will
        be hidden.
        """
        try:
            df = df_sel.copy()
            if 'Date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['Date']):
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

            # ensure numeric costs
            df['Cost'] = pd.to_numeric(df.get('Cost', pd.Series([])), errors='coerce').fillna(0.0)

            # if year provided, focus on that year
            if year is not None:
                # create full list of first-of-month timestamps for that year
                try:
                    months = pd.date_range(start=f"{int(year)}-01-01", periods=12, freq='MS')
                except Exception:
                    months = None
                df = df[df['Date'].dt.year == int(year)]

            # resample monthly
            if not df.empty:
                monthly = df.set_index('Date')['Cost'].resample('MS').sum()
            else:
                monthly = pd.Series(dtype=float)

            # if year provided, reindex to all months to ensure 12 rows
            if year is not None and months is not None:
                monthly = monthly.reindex(months, fill_value=0.0)

            if monthly.empty:
                # nothing to show
                try:
                    self.monthly_details_section.setVisible(False)
                except Exception:
                    pass
                return

            # populate table rows
            rows = [(dt.strftime('%b %Y'), f"${val:,.2f}") for dt, val in monthly.items()]

            self._monthly_table.setRowCount(len(rows))
            for i, (month_label, total_label) in enumerate(rows):
                self._monthly_table.setItem(i, 0, QTableWidgetItem(month_label))
                self._monthly_table.setItem(i, 1, QTableWidgetItem(total_label))

            self._monthly_table.resizeColumnsToContents()
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
                            # nothing selected -> clear table
                            try:
                                self._items_table.setRowCount(0)
                            except Exception:
                                pass
                            return

                        dt = pd.to_datetime(month_label, format='%b %Y', errors='coerce')
                        if pd.isna(dt):
                            # invalid label -> clear table
                            try:
                                self._items_table.setRowCount(0)
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

                            self._items_table.setItem(r, 0, QTableWidgetItem(str(item_val)))
                            self._items_table.setItem(r, 1, QTableWidgetItem(str(cat)))
                            self._items_table.setItem(r, 2, QTableWidgetItem(f"${float(cost):,.2f}"))
                            self._items_table.setItem(r, 3, QTableWidgetItem(date_str))
                            self._items_table.setItem(r, 4, QTableWidgetItem(str(notes)))
                    except Exception:
                        # clear table on error
                        try:
                            self._items_table.setRowCount(0)
                        except Exception:
                            pass

                # connect handler
                try:
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
                if not text or text == 'All':
                    self.monthly_details_section.setVisible(False)
                else:
                    self.monthly_details_section.setVisible(True)
        except Exception:
            pass

