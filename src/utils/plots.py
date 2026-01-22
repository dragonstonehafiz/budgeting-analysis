"""Matplotlib plotting utilities for the budgeting dashboard.

Provides functions to create interactive matplotlib charts with Qt integration.
These are intended to be embedded directly as Qt widgets.
"""
from __future__ import annotations

from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from utils.category_colors import get_category_color

__all__ = ["monthly_trend_figure", "InteractiveCanvas", "category_pie_chart", "amount_distribution_pie", "monthly_bar_chart", "top_items_bar_chart", "rolling_average_figure", "cumulative_spending_figure"]


class InteractiveCanvas(FigureCanvas):
    """
    General-purpose matplotlib canvas with hover tooltips for various chart types.
    
    Supports: line charts, scatter plots, bar charts, pie charts
    Auto-detects chart type and applies appropriate hover behavior.
    """
    
    def __init__(self, figure):
        super().__init__(figure)
        self.figure = figure
        self.ax = None
        self.chart_type = None
        self.chart_data = {}
        self.annotation = None
        
        # Connect mouse motion event
        self.mpl_connect('motion_notify_event', self.on_hover)
    
    def set_line_data(self, x_data, y_data, ax, line, x_formatter=None):
        """Configure for line/scatter charts"""
        self.chart_type = 'line'
        self.ax = ax
        self.chart_data = {
            'x_data': x_data,
            'y_data': y_data,
            'line': line,
            'x_formatter': x_formatter or (lambda x: str(x))
        }
        self._create_annotation()
    
    def set_bar_data(self, categories, values, ax, bars, value_formatter=None):
        """Configure for bar charts"""
        self.chart_type = 'bar'
        self.ax = ax
        self.chart_data = {
            'categories': categories,
            'values': values,
            'bars': bars,
            'value_formatter': value_formatter or (lambda x: f"${x:,.2f}")
        }
        self._create_annotation()
    
    def set_pie_data(self, labels, values, ax, wedges, value_formatter=None):
        """Configure for pie charts"""
        self.chart_type = 'pie'
        self.ax = ax
        total = sum(values)
        self.chart_data = {
            'labels': labels,
            'values': values,
            'wedges': wedges,
            'total': total,
            'value_formatter': value_formatter or (lambda x: f"${x:,.2f}"),
            # optional counts per wedge (list) to include in hover text
            'counts': None,
        }
        self._create_annotation()
    
    def _create_annotation(self):
        """Create or recreate the hover annotation"""
        if self.annotation:
            self.annotation.remove()
        
        if self.ax:
            # Anchor the tooltip relative to the axes (axes fraction coords).
            # We'll position it at y=0 (x-axis) and adjust the text offset so
            # the tooltip appears just above the axis and stays on-screen.
            # No arrow: keep a clean label rendered at the x-axis center
            self.annotation = self.ax.annotate(
                '',
                xy=(0.5, 0),
                xycoords='axes fraction',
                xytext=(0, 10),
                textcoords='offset points',
                bbox=dict(boxstyle='round', fc='w', alpha=0.95, edgecolor='gray'),
                visible=False,
                fontsize=10,
                zorder=1000,
                ha='center',
            )
    
    def on_hover(self, event):
        """Show tooltip based on chart type"""
        if event.inaxes != self.ax or not self.chart_data:
            self._hide_annotation()
            return
        
        if self.chart_type == 'line':
            self._handle_line_hover(event)
        elif self.chart_type == 'bar':
            self._handle_bar_hover(event)
        elif self.chart_type == 'pie':
            self._handle_pie_hover(event)
    
    def _handle_line_hover(self, event):
        """Handle hover for line/scatter charts"""
        if not hasattr(event, 'xdata') or event.xdata is None:
            self._hide_annotation()
            return
        
        x_data = self.chart_data['x_data']
        y_data = self.chart_data['y_data']
        x_formatter = self.chart_data['x_formatter']
        
        if len(x_data) == 0:
            self._hide_annotation()
            return
        
        # Handle datetime x-axis
        if hasattr(x_data[0], 'strftime'):  # datetime objects
            mouse_date = mdates.num2date(event.xdata)
            date_diffs = [abs((d - mouse_date.replace(tzinfo=None)).total_seconds()) for d in x_data]
            closest_idx = date_diffs.index(min(date_diffs))

            # Within 30 days threshold for datetime
            if min(date_diffs) < 30 * 24 * 3600:
                x_str = x_data[closest_idx].strftime('%b %Y')
                y_str = f"${y_data[closest_idx]:,.2f}"

                # compute x as fraction of axes so tooltip stays anchored to x-axis
                try:
                    x_val = mdates.date2num(x_data[closest_idx])
                    xmin, xmax = self.ax.get_xlim()
                    denom = xmax - xmin if xmax != xmin else 1
                    x_frac = (x_val - xmin) / denom
                    x_frac = max(0.0, min(1.0, x_frac))
                except Exception:
                    x_frac = 0.5

                self.annotation.xy = (x_frac, 0)
                # show month label and formatted amount at center for readability
                self.annotation.set_text(f"{x_str}: {y_str}")
                self.annotation.set_visible(True)
                self.draw_idle()
            else:
                self._hide_annotation()
        else:  # numeric x-axis
            # Find closest point by x-distance
            x_diffs = [abs(x - event.xdata) for x in x_data]
            closest_idx = x_diffs.index(min(x_diffs))
            
            # Show if reasonably close (within 5% of x-range)
            x_range = max(x_data) - min(x_data) if len(x_data) > 1 else 1
            threshold = x_range * 0.05
            
            if min(x_diffs) <= threshold:
                x_str = x_formatter(x_data[closest_idx])
                y_str = f"${y_data[closest_idx]:,.2f}"

                try:
                    xmin, xmax = min(x_data), max(x_data)
                    denom = xmax - xmin if xmax != xmin else 1
                    x_frac = (x_data[closest_idx] - xmin) / denom
                    x_frac = max(0.0, min(1.0, x_frac))
                except Exception:
                    x_frac = 0.5

                self.annotation.xy = (x_frac, 0)
                # show x label and formatted amount at center for readability
                self.annotation.set_text(f"{x_str}: {y_str}")
                self.annotation.set_visible(True)
                self.draw_idle()
            else:
                self._hide_annotation()
    
    def _handle_bar_hover(self, event):
        """Handle hover for bar charts"""
        bars = self.chart_data['bars']
        categories = self.chart_data['categories']
        values = self.chart_data['values']
        value_formatter = self.chart_data['value_formatter']
        
        for i, bar in enumerate(bars):
            if bar.contains(event)[0]:  # Mouse is over this bar
                category = categories[i]
                value = values[i]
                # anchor at the x-axis (axes fraction y=0)
                self.annotation.xy = (0.5, -0.2)
                # show label and amount at center for readability
                try:
                    amt_text = value_formatter(value)
                except Exception:
                    amt_text = str(value)
                self.annotation.set_text(f"{category}: {amt_text}")
                self.annotation.set_visible(True)
                self.draw_idle()
                return
        
        self._hide_annotation()
    
    def _handle_pie_hover(self, event):
        """Handle hover for pie charts"""
        wedges = self.chart_data['wedges']
        labels = self.chart_data['labels']
        values = self.chart_data['values']
        total = self.chart_data['total']
        value_formatter = self.chart_data['value_formatter']
        counts = self.chart_data.get('counts')
        
        for i, wedge in enumerate(wedges):
            if wedge.contains(event)[0]:  # Mouse is over this wedge
                label = labels[i]
                value = values[i]
                percentage = (value / total) * 100 if total > 0 else 0

                # keep tooltip at center x-axis and show label, amount, and percent
                self.annotation.xy = (0.5, 0)
                try:
                    amt_text = value_formatter(value)
                except Exception:
                    amt_text = str(value)
                self.annotation.set_text(f"{label}: {amt_text} ({percentage:.1f}%)")
                self.annotation.set_visible(True)
                self.draw_idle()
                return
        
        self._hide_annotation()
    
    def _hide_annotation(self):
        """Hide the hover annotation"""
        if self.annotation:
            self.annotation.set_visible(False)
            self.draw_idle()


def monthly_trend_figure(
    df: pd.DataFrame,
    date_col: str = "Date",
    cost_col: str = "Cost",
    title: Optional[str] = None,
    hide_values: bool = False,
):
    """Create a matplotlib figure showing monthly spending trends with Qt integration.
    
    Args:
        df: DataFrame containing at least `date_col` and `cost_col`.
        date_col: column name for dates (will be coerced to datetime).
        cost_col: column name for numeric cost values.
        title: optional title for the chart.
    
    Returns:
        InteractiveCanvas widget ready for Qt layout
    """
    
    # Create figure with tight layout
    fig = Figure(figsize=(10, 4), dpi=100)
    fig.patch.set_facecolor('white')
    
    canvas = InteractiveCanvas(fig)
    ax = fig.add_subplot(111)
    
    if df.empty:
        ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes, 
                ha='center', va='center', fontsize=12, color='gray')
        ax.set_title(title or "Monthly Spending Trend")
        fig.tight_layout()
        return canvas
    
    # Prepare data
    df = df.copy()
    if date_col not in df.columns or cost_col not in df.columns:
        ax.text(0.5, 0.5, f'Missing {date_col} or {cost_col} columns', transform=ax.transAxes, 
                ha='center', va='center', fontsize=12, color='red')
        ax.set_title(title or "Monthly Spending Trend")
        fig.tight_layout()
        return canvas
    
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    
    if df.empty:
        ax.text(0.5, 0.5, 'No valid dates found', transform=ax.transAxes, 
                ha='center', va='center', fontsize=12, color='gray')
        ax.set_title(title or "Monthly Spending Trend")
        fig.tight_layout()
        return canvas
    
    df[cost_col] = pd.to_numeric(df[cost_col], errors='coerce').fillna(0.0)
    
    # Resample by month
    monthly_totals = df.set_index(date_col)[cost_col].resample('MS').sum()
    
    if monthly_totals.empty:
        ax.text(0.5, 0.5, 'No data to plot', transform=ax.transAxes, 
                ha='center', va='center', fontsize=12, color='gray')
        ax.set_title(title or "Monthly Spending Trend")
        fig.tight_layout()
        return canvas
    
    # Plot the data
    dates = monthly_totals.index.to_pydatetime()
    values = monthly_totals.values

    line = ax.plot(dates, values, 'o-', linewidth=2, markersize=4,
                   color='#1976D2', markerfacecolor='white', markeredgecolor='#1976D2')[0]

    # Draw the average line across the plotted points
    try:
        avg = float(np.nanmean(values))
        avg_color = '#d32f2f'  # a distinct red for the average line
        ax.axhline(avg, color=avg_color, linestyle='--', linewidth=1.5, zorder=1)

        # place a small label for the average in the same area as y-axis text/ticks
        if not hide_values:
            try:
                ax_text = f"Avg: ${avg:,.2f}"
                ymin, ymax = ax.get_ylim()
                if ymax - ymin == 0:
                    y_frac = 0.5
                else:
                    y_frac = (avg - ymin) / (ymax - ymin)

                # place at the left edge of axes area (x=0 in axes fraction coords)
                # right-align so it sits next to the y-axis tick labels
                ax.text(0.0, y_frac, ax_text, transform=ax.transAxes,
                        color=avg_color, fontsize=9, va='center', ha='right',
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.9), clip_on=False)
            except Exception:
                # ignore annotation placement errors
                pass
    except Exception:
        # non-fatal: if mean calculation fails, continue without average
        avg = None

    # Annotate each data point with its amount (small, above the marker)
    if not hide_values:
        for x, y in zip(dates, values):
            try:
                # format cents for small values, round for large values
                if abs(y) >= 100:
                    lbl = f"${y:,.0f}"
                else:
                    lbl = f"${y:,.2f}"
                ax.annotate(lbl, xy=(x, y), xytext=(0, 6), textcoords='offset points',
                            ha='center', fontsize=8, color='#111', zorder=5)
            except Exception:
                continue

    # Set up the canvas with hover data for line chart
    canvas.set_line_data(dates, values, ax, line, x_formatter=lambda d: d.strftime('%b %Y'))
    
    # Format the plot
    ax.set_title(title or "Monthly Spending Trend", fontsize=14, pad=15)
    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Amount ($)", fontsize=11)
    
    # Format x-axis based on data range
    try:
        min_date = dates[0]
        max_date = dates[-1]
        date_range_days = (max_date - min_date).days
        
        if date_range_days >= 1095:
            # For 3+ years, show year starts
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        elif date_range_days >= 365:
            # For 1-3 years, show every 6 months
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        else:
            # For less than 1 year, show months
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    except Exception:
        # Fallback formatting
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, len(dates)//8)))
    
    # Format y-axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Style
    ax.grid(True, alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Hide y-axis values in privacy mode (after formatter)
    if hide_values:
        ax.set_yticklabels([])
    
    # Rotate x-axis labels if needed
    if len(dates) > 6:
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    fig.tight_layout()
    return canvas


def rolling_average_figure(
    df: pd.DataFrame,
    date_col: str = "Date",
    cost_col: str = "Cost",
    window: int = 3,
    title: Optional[str] = None,
    hide_values: bool = False,
):
    """Create a monthly series with a rolling average and volatility band.

    Args:
        df: DataFrame with date and cost columns.
        date_col: column name for dates.
        cost_col: column name for numeric costs.
        window: rolling window in months (integer).
        title: optional chart title.

    Returns:
        InteractiveCanvas widget with the plot.
    """

    fig = Figure(figsize=(10, 4), dpi=100)
    fig.patch.set_facecolor('white')
    canvas = InteractiveCanvas(fig)
    ax = fig.add_subplot(111)

    if df is None or df.empty:
        ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='gray')
        ax.set_title(title or f'Rolling {window}-month average')
        fig.tight_layout()
        return canvas

    df = df.copy()
    if date_col not in df.columns or cost_col not in df.columns:
        ax.text(0.5, 0.5, f'Missing {date_col} or {cost_col}', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='red')
        fig.tight_layout()
        return canvas

    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    if df.empty:
        ax.text(0.5, 0.5, 'No valid dates', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='gray')
        fig.tight_layout()
        return canvas

    df[cost_col] = pd.to_numeric(df[cost_col], errors='coerce').fillna(0.0)

    monthly = df.set_index(date_col)[cost_col].resample('MS').sum()
    if monthly.empty:
        ax.text(0.5, 0.5, 'No data to plot', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='gray')
        fig.tight_layout()
        return canvas

    # compute rolling mean and std (centered=False to be causal)
    roll_mean = monthly.rolling(window=window, min_periods=1).mean()
    roll_std = monthly.rolling(window=window, min_periods=1).std().fillna(0.0)

    dates = monthly.index.to_pydatetime()
    values = monthly.values

    # plot raw monthly points (light) and rolling mean
    ax.plot(dates, values, 'o', color='#9E9E9E', markersize=4, alpha=0.7)
    mean_line, = ax.plot(dates, roll_mean.values, '-', color='#1976D2', linewidth=2)

    # volatility band
    try:
        upper = roll_mean + roll_std
        lower = roll_mean - roll_std
        ax.fill_between(dates, lower.values, upper.values, color='#1976D2', alpha=0.12)
    except Exception:
        pass

    ax.set_title(title or f'{window}-month rolling average', fontsize=14, pad=12)
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount ($)')
    ax.grid(True, alpha=0.3)

    # Hide y-axis values in privacy mode
    if hide_values:
        ax.set_yticklabels([])

    # Format x-axis based on data range
    try:
        min_date = dates[0]
        max_date = dates[-1]
        date_range_days = (max_date - min_date).days
        
        if date_range_days >= 1095:
            # For 3+ years, show year starts
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            label_rotation = 0
        elif date_range_days >= 365:
            # For 1-3 years, show every 6 months
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            label_rotation = 0
        else:
            # For less than 1 year, show months
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            label_rotation = 0
        
        # Apply rotation
        tick_count = len(dates)
        label_fontsize = 9 if tick_count <= 12 else 8
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=label_rotation, fontsize=label_fontsize)
    except Exception:
        # Fallback: use horizontal, smaller labels for readability
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, len(dates)//8)))
        try:
            tick_count = len(dates)
            label_fontsize = 9 if tick_count <= 12 else 8
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, fontsize=label_fontsize)
        except Exception:
            pass

    # hover uses the rolling mean values as the primary label
    try:
        canvas.set_line_data(dates, roll_mean.values.tolist(), ax, mean_line, x_formatter=lambda d: d.strftime('%b %Y'))
    except Exception:
        try:
            canvas.set_line_data(dates, roll_mean.values.tolist(), ax, mean_line)
        except Exception:
            pass

    # Add an explanatory caption at the bottom-center describing the rolling window
    try:
        caption = f"Blue line = {window}-month rolling average (smoothed monthly spend). Shaded band = typical month-to-month variability around the average."
        # place just below the x-axis inside the figure using axes-fraction coords
        ax.text(0.5, -0.12, caption, transform=ax.transAxes, ha='center', va='top', fontsize=9, color='gray')
    except Exception:
        # non-fatal: if caption placement fails, continue without it
        pass

    fig.tight_layout()
    return canvas


def cumulative_spending_figure(
    df: pd.DataFrame,
    date_col: str = "Date",
    cost_col: str = "Cost",
    title: Optional[str] = None,
    hide_values: bool = False,
):
    """Create a line chart showing cumulative spending over time (day by day).
    
    Shows running total that increases each day purchases are made, and stays
    flat on days with no spending. Includes all days in the date range.
    
    Args:
        df: DataFrame with date and cost columns.
        date_col: column name for dates.
        cost_col: column name for numeric costs.
        title: optional chart title.
    
    Returns:
        InteractiveCanvas widget with the cumulative spending plot.
    """
    fig = Figure(figsize=(10, 4), dpi=100)
    fig.patch.set_facecolor('white')
    canvas = InteractiveCanvas(fig)
    ax = fig.add_subplot(111)
    
    if df is None or df.empty:
        ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='gray')
        ax.set_title(title or 'Cumulative Spending')
        fig.tight_layout()
        return canvas
    
    df = df.copy()
    if date_col not in df.columns or cost_col not in df.columns:
        ax.text(0.5, 0.5, f'Missing {date_col} or {cost_col}', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='red')
        fig.tight_layout()
        return canvas
    
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    if df.empty:
        ax.text(0.5, 0.5, 'No valid dates', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='gray')
        fig.tight_layout()
        return canvas
    
    df[cost_col] = pd.to_numeric(df[cost_col], errors='coerce').fillna(0.0)
    
    # Get date range and create daily index
    min_date = df[date_col].min()
    max_date = df[date_col].max()
    
    # Create complete daily date range
    daily_index = pd.date_range(start=min_date, end=max_date, freq='D')
    
    # Resample to daily totals (sum spending per day)
    daily_totals = df.set_index(date_col)[cost_col].resample('D').sum()
    
    # Reindex to include all days (fills missing days with 0)
    daily_totals = daily_totals.reindex(daily_index, fill_value=0.0)
    
    # Calculate cumulative sum
    cumulative = daily_totals.cumsum()
    
    if cumulative.empty:
        ax.text(0.5, 0.5, 'No data to plot', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='gray')
        fig.tight_layout()
        return canvas
    
    # Plot cumulative spending
    dates = cumulative.index.to_pydatetime()
    values = cumulative.values
    
    line = ax.plot(dates, values, '-', linewidth=2, color='#1976D2')[0]
    
    # Set up hover data
    canvas.set_line_data(dates, values, ax, line, x_formatter=lambda d: d.strftime('%b %d, %Y'))
    
    # Format the plot
    ax.set_title(title or 'Cumulative Spending', fontsize=14, pad=15)
    ax.set_xlabel('Date', fontsize=11)
    ax.set_ylabel('Cumulative Total ($)', fontsize=11)
    
    # Format x-axis based on data range
    date_range_days = (max_date - min_date).days
    if date_range_days >= 1095:
        # For 3+ years, show year starts
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    elif date_range_days >= 365:
        # For 1-3 years, show every 6 months
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    else:
        # For less than 1 year, show months
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    
    # Format y-axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Style
    ax.grid(True, alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Hide y-axis values in privacy mode
    if hide_values:
        ax.set_yticklabels([])
    
    # Rotate x-axis labels for readability
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Add annotation showing final total
    if not hide_values:
        try:
            final_total = float(values[-1])
            ax.text(0.98, 0.98, f'Total: ${final_total:,.2f}',
                    transform=ax.transAxes, ha='right', va='top',
                    bbox=dict(boxstyle='round', fc='white', alpha=0.8, edgecolor='gray'),
                    fontsize=10, weight='bold')
        except Exception:
            pass
    
    fig.tight_layout()
    return canvas


def amount_distribution_pie(
    df: pd.DataFrame,
    cost_col: str = "Cost",
    title: Optional[str] = None,
    hide_values: bool = False,
):
    """Create a donut chart showing distribution of spend by transaction-size quartiles.

    - Uses quartiles (0-25%, 25-50%, 50-75%, 75-100%) based on transaction amounts.
    - Slice sizes represent total spend contributed by transactions in that quartile.
    - Hover shows: quartile label, total spend, and number of transactions.
    """
    fig = Figure(figsize=(6, 6), dpi=100)
    fig.patch.set_facecolor('white')
    canvas = InteractiveCanvas(fig)
    ax = fig.add_subplot(111)

    if df is None or df.empty:
        ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='gray')
        ax.set_title(title or 'Spend by transaction quartile')
        fig.tight_layout()
        return canvas

    df = df.copy()
    if cost_col not in df.columns:
        ax.text(0.5, 0.5, f'Missing {cost_col}', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='red')
        fig.tight_layout()
        return canvas

    # prepare amounts, exclude NaNs
    df[cost_col] = pd.to_numeric(df[cost_col], errors='coerce')
    df = df.dropna(subset=[cost_col])
    if df.empty:
        ax.text(0.5, 0.5, 'No valid amounts', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='gray')
        fig.tight_layout()
        return canvas

    # define quartile bins using qcut; duplicates='drop' handles flat distributions
    try:
        df['quartile'] = pd.qcut(df[cost_col], q=4, labels=['Q1 (0-25%)', 'Q2 (25-50%)', 'Q3 (50-75%)', 'Q4 (75-100%)'], duplicates='drop')
    except Exception:
        # fallback: if qcut fails (e.g., not enough unique values), use rank-based bins
        df['quartile'] = pd.cut(df[cost_col].rank(method='first'), bins=4, labels=['Q1 (0-25%)', 'Q2 (25-50%)', 'Q3 (50-75%)', 'Q4 (75-100%)'])

    # Explicitly pass observed=False to retain current behavior and avoid a FutureWarning
    grouped = df.groupby('quartile', observed=False)[cost_col].agg(total_spend='sum', tx_count='count')
    # ensure quartile order
    ordered_labels = ['Q1 (0-25%)', 'Q2 (25-50%)', 'Q3 (50-75%)', 'Q4 (75-100%)']
    grouped = grouped.reindex(ordered_labels).fillna(0.0)

    labels = []
    values = []
    counts = []
    for lbl in ordered_labels:
        labels.append(lbl)
        values.append(float(grouped.loc[lbl, 'total_spend']))
        counts.append(int(grouped.loc[lbl, 'tx_count']))

    # colors: reuse category color map cyclically for visibility
    cmap = plt.get_cmap('tab20')
    colors = [cmap(i) for i in range(len(labels))]

    wedgeprops = dict(width=0.38, edgecolor='white')
    pie_result = ax.pie(values, labels=None, colors=colors, autopct=None, startangle=90, wedgeprops=wedgeprops)
    if isinstance(pie_result, (list, tuple)) and len(pie_result) >= 2:
        wedges = pie_result[0]
    else:
        wedges = pie_result

    ax.set_title(title or 'Spend by transaction quartile', fontsize=13, pad=12)

    # center total
    if not hide_values:
        try:
            total_amount = float(sum(values))
            ax.text(0, 0, f"Total\n${total_amount:,.2f}", ha='center', va='center', fontsize=11, weight='bold')
        except Exception:
            pass

    # Hook up hover data including counts
    try:
        canvas.set_pie_data(labels, values, ax, wedges, value_formatter=lambda x: f"${x:,.2f}")
        # attach counts into chart_data for richer tooltip
        canvas.chart_data['counts'] = counts
    except Exception:
        pass

    fig.tight_layout()
    return canvas


def top_items_bar_chart(
    df: pd.DataFrame,
    item_col: str = "Item",
    cost_col: str = "Cost",
    top_n: int = 10,
    title: Optional[str] = None,
    hide_values: bool = False,
):
    """Create a horizontal bar chart showing top items by total spend.

    Groups rows by `item_col`, sums `cost_col`, sorts descending and plots the
    top_n items. Each bar is annotated at the end with the formatted total amount.

    Returns an InteractiveCanvas ready to add to Qt layouts.
    """
    fig = Figure(figsize=(10, 4), dpi=100)
    fig.patch.set_facecolor('white')
    canvas = InteractiveCanvas(fig)
    ax = fig.add_subplot(111)

    if df is None or df.empty:
        ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='gray')
        ax.set_title(title or 'Top items')
        fig.tight_layout()
        return canvas

    # Prepare data and validate
    df = df.copy()
    if item_col not in df.columns or cost_col not in df.columns:
        ax.text(0.5, 0.5, f'Missing {item_col} or {cost_col}', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='red')
        fig.tight_layout()
        return canvas

    df[cost_col] = pd.to_numeric(df[cost_col], errors='coerce').fillna(0.0)

    # compute totals and pick top items by total spend
    totals = df.groupby(item_col, dropna=False)[cost_col].sum().sort_values(ascending=False)
    if totals.empty:
        ax.text(0.5, 0.5, 'No spend found', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='gray')
        fig.tight_layout()
        return canvas

    top_items = totals.head(top_n).index.astype(str).tolist()

    # For each top item, get the individual transaction amounts (preserve original order)
    segments_per_item = []
    for it in top_items:
        sub = df[df[item_col].astype(str) == str(it)]
        # use the raw numeric costs as segments
        segs = sub[cost_col].tolist()
        # if no segments (shouldn't happen), add a zero placeholder
        if len(segs) == 0:
            segs = [0.0]
        segments_per_item.append(segs)

    # plotting: stacked horizontal bars. Largest item at top to match expected visual
    items = top_items
    n = len(items)
    y_pos = np.arange(n)

    # single color for all segments; draw white edges to visually separate segments
    bars_flat = []
    values_flat = []
    categories_flat = []
    items_flat = []  # keep item name per segment for hover
    notes_flat = []  # keep Notes per segment for hover

    for idx, segs in enumerate(segments_per_item):
        y = y_pos[idx]
        left = 0.0
        # iterate segments and plot each as a stacked piece
        for s_i, seg_val in enumerate(segs):
            try:
                # determine category for this transaction row (use df rows ordering)
                # attempt to find the original row corresponding to this segment
                # Note: segments were extracted from sub = df[df[item_col].astype(str) == str(it)] in order
                # so we can index into that sub DataFrame to get the category
                sub = df[df[item_col].astype(str) == str(items[idx])]
                try:
                    cat_val = sub.iloc[s_i].get('Category', 'Miscellaneous')
                except Exception:
                    cat_val = sub['Category'].iloc[0] if len(sub) > 0 and 'Category' in sub.columns else 'Miscellaneous'

                seg_color = get_category_color(cat_val)

                rect = ax.barh(y, seg_val, left=left, height=0.6,
                               color=seg_color, edgecolor='white', linewidth=0.8)
                # rect is a BarContainer; get the rectangle patch
                patch = rect[0] if len(rect) > 0 else None
                if patch is not None:
                    bars_flat.append(patch)
                    values_flat.append(float(seg_val))
                    categories_flat.append(str(cat_val))
                    items_flat.append(items[idx])
                    # attempt to extract Notes for this transaction row
                    try:
                        note_val = sub.iloc[s_i].get('Notes', '')
                    except Exception:
                        note_val = sub['Notes'].iloc[s_i] if ('Notes' in sub.columns and len(sub) > s_i) else ''
                    notes_flat.append('' if note_val is None else str(note_val))
                left += float(seg_val)
            except Exception:
                left += 0.0

        # annotate total at the right end of the stacked bar
        if not hide_values:
            try:
                total_val = float(sum(segs))
                ax.annotate(f"${total_val:,.2f}", xy=(left, y), xytext=(4, 0),
                            textcoords='offset points', ha='left', va='center', fontsize=9)
            except Exception:
                pass

    ax.set_yticks(y_pos)
    ax.set_yticklabels(items, fontsize=10)
    # invert y-axis so the first (largest) item appears at the top
    try:
        ax.invert_yaxis()
    except Exception:
        pass
    ax.set_xlabel('Cost ($)')

    # styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='x', alpha=0.25)
    ax.set_title(title or f"Top {len(items)} items by spend", fontsize=13, pad=12)

    # Hide x-axis values in privacy mode (horizontal bars show amounts on x-axis)
    if hide_values:
        ax.set_xticklabels([])

    # Provide hover data: combine item and category for clarity
    try:
        # Build hover labels including Notes when available
        hover_labels = []
        for it, cat, note in zip(items_flat, categories_flat, notes_flat):
            base = f"{it} — {cat}"
            if note and str(note).strip():
                # include notes separated by an em-dash for readability
                base = f"{base} — {note}"
            hover_labels.append(base)
        canvas.set_bar_data(hover_labels, values_flat, ax, bars_flat, value_formatter=lambda x: f"${x:,.2f}")
    except Exception:
        # fallback: provide totals per item so hover still shows useful info
        try:
            canvas.set_bar_data(items[::-1], [totals[it] for it in items[::-1]], ax, [], value_formatter=lambda x: f"${x:,.2f}")
        except Exception:
            pass

    fig.tight_layout()
    return canvas


def category_pie_chart(
    df: pd.DataFrame,
    category_col: str = "Category",
    cost_col: str = "Cost",
    title: Optional[str] = None,
    top_n: Optional[int] = 10,
    hide_values: bool = False,
):
    """Create a pie chart showing percent of expenditure by category.

    Args:
        df: DataFrame containing at least `category_col` and `cost_col`.
        category_col: name of the category column.
        cost_col: name of the numeric cost column.
        title: optional chart title.
        top_n: if provided, show only the top_n categories and aggregate the rest into 'Other'.

    Returns:
        InteractiveCanvas widget ready for Qt layout.
    """
    fig = Figure(figsize=(6, 6), dpi=100)
    fig.patch.set_facecolor('white')
    canvas = InteractiveCanvas(fig)
    ax = fig.add_subplot(111)

    if df is None or df.empty:
        ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='gray')
        ax.set_title(title or 'Spending by category')
        fig.tight_layout()
        return canvas

    df = df.copy()
    if category_col not in df.columns or cost_col not in df.columns:
        ax.text(0.5, 0.5, f'Missing {category_col} or {cost_col}', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='red')
        fig.tight_layout()
        return canvas

    df[cost_col] = pd.to_numeric(df[cost_col], errors='coerce').fillna(0.0)

    totals = df.groupby(category_col)[cost_col].sum().sort_values(ascending=False)
    if totals.empty or totals.sum() == 0:
        ax.text(0.5, 0.5, 'No spend found', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='gray')
        fig.tight_layout()
        return canvas

    # Optionally aggregate small categories into 'Other'
    if top_n is not None and top_n > 0 and len(totals) > top_n:
        top = totals.head(top_n)
        other_sum = totals.iloc[top_n:].sum()
        labels = list(top.index.astype(str)) + ['Other']
        values = list(top.values) + [float(other_sum)]
    else:
        labels = list(totals.index.astype(str))
        values = list(totals.values)

    # Colors for each label using the category color map; 'Other' uses Miscellaneous
    colors = [get_category_color(lbl) if lbl != 'Other' else get_category_color('Miscellaneous') for lbl in labels]

    # Draw a donut by setting a wedge width (supported in modern matplotlib)
    wedgeprops = dict(width=0.38, edgecolor='white')
    pie_result = ax.pie(values, labels=None, colors=colors, autopct=None, startangle=90, wedgeprops=wedgeprops)
    # pie_result may be (wedges, texts) or (wedges, texts, autotexts)
    if isinstance(pie_result, (list, tuple)) and len(pie_result) >= 2:
        wedges = pie_result[0]
        texts = pie_result[1]
        autotexts = pie_result[2] if len(pie_result) > 2 else []
    else:
        wedges = pie_result
        texts = []
        autotexts = []

    ax.set_title(title or 'Spending by category', fontsize=13, pad=12)

    # Center total amount text
    if not hide_values:
        try:
            total_amount = float(sum(values))
            ax.text(0, 0, f"Total\n${total_amount:,.2f}", ha='center', va='center', fontsize=11, weight='bold')
        except Exception:
            pass

    # Hook up hover data
    try:
        canvas.set_pie_data(labels, values, ax, wedges, value_formatter=lambda x: f"${x:,.2f}")
    except Exception:
        pass

    fig.tight_layout()
    return canvas


def monthly_pie_chart(
    monthly_series: pd.Series,
    title: Optional[str] = None,
    hide_values: bool = False,
):
    """Create a donut pie chart showing spend by month.

    Accepts a pandas Series whose index are datetimes (first-of-month) and
    values are numeric totals for that month.
    """
    fig = Figure(figsize=(5, 5), dpi=100)
    fig.patch.set_facecolor('white')
    canvas = InteractiveCanvas(fig)
    ax = fig.add_subplot(111)

    if monthly_series is None or len(monthly_series) == 0:
        ax.text(0.5, 0.5, 'No data available', transform=ax.transAxes,
                ha='center', va='center', fontsize=12, color='gray')
        ax.set_title(title or 'Spending by month')
        fig.tight_layout()
        return canvas

    # Ensure index are datetimes and sort
    try:
        idx = pd.DatetimeIndex(monthly_series.index)
    except Exception:
        idx = pd.to_datetime(monthly_series.index, errors='coerce')

    labels = [d.strftime('%b %Y') for d in idx]
    values = [float(v) for v in monthly_series.values]

    # Build visual labels that include month and formatted amount (keeps hover labels
    # separate so the interactive tooltip shows the same month text without duplication)
    def _fmt_amt(x):
        try:
            return f"${x:,.2f}"
        except Exception:
            return str(x)

    # Only show amounts on labels if privacy mode is off
    if hide_values:
        visual_labels = [f"{m}" for m in labels]
    else:
        visual_labels = [f"{m}\n{_fmt_amt(v)}" for m, v in zip(labels, values)]

    cmap = plt.get_cmap('tab20')
    colors = [cmap(i) for i in range(len(labels))]

    wedgeprops = dict(width=0.38, edgecolor='white')
    # Pass visual_labels to show month + amount on the chart. For many slices this
    # can become crowded; acceptable fallback is the hover tooltip handled by
    # InteractiveCanvas.
    pie_result = ax.pie(values, labels=visual_labels, colors=colors, autopct=None, startangle=90, wedgeprops=wedgeprops)
    if isinstance(pie_result, (list, tuple)) and len(pie_result) >= 2:
        wedges = pie_result[0]
    else:
        wedges = pie_result

    ax.set_title(title or 'Spending by month', fontsize=13, pad=12)

    if not hide_values:
        try:
            total_amount = float(sum(values))
            ax.text(0, 0, f"Total\n${total_amount:,.2f}", ha='center', va='center', fontsize=11, weight='bold')
        except Exception:
            pass

    try:
        canvas.set_pie_data(labels, values, ax, wedges, value_formatter=lambda x: f"${x:,.2f}")
    except Exception:
        pass

    fig.tight_layout()
    return canvas
