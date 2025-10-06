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

__all__ = ["monthly_trend_figure", "InteractiveCanvas", "category_pie_chart", "monthly_bar_chart"]


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
            'value_formatter': value_formatter or (lambda x: f"${x:,.2f}")
        }
        self._create_annotation()
    
    def _create_annotation(self):
        """Create or recreate the hover annotation"""
        if self.annotation:
            self.annotation.remove()
        
        if self.ax:
            self.annotation = self.ax.annotate('', xy=(0,0), xytext=(20,20), 
                                        textcoords="offset points",
                                        bbox=dict(boxstyle="round", fc="w", alpha=0.9, edgecolor='gray'),
                                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
                                        visible=False, fontsize=10, zorder=1000)
    
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
                
                self.annotation.xy = (mdates.date2num(x_data[closest_idx]), y_data[closest_idx])
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
                
                self.annotation.xy = (x_data[closest_idx], y_data[closest_idx])
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
                
                # Position tooltip at top of bar
                x = bar.get_x() + bar.get_width() / 2
                y = bar.get_height()
                
                self.annotation.xy = (x, y)
                self.annotation.set_text(f"{category}: {value_formatter(value)}")
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
        
        for i, wedge in enumerate(wedges):
            if wedge.contains(event)[0]:  # Mouse is over this wedge
                label = labels[i]
                value = values[i]
                percentage = (value / total) * 100 if total > 0 else 0
                
                # Position tooltip at wedge center
                theta = (wedge.theta1 + wedge.theta2) / 2
                r = wedge.r * 0.7  # Position at 70% of radius
                x = r * np.cos(np.radians(theta))
                y = r * np.sin(np.radians(theta))
                
                self.annotation.xy = (x, y)
                self.annotation.set_text(f"{label}: {value_formatter(value)} ({percentage:.1f}%)")
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
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, len(dates)//8)))
    
    # Format y-axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Style
    ax.grid(True, alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Rotate x-axis labels if needed
    if len(dates) > 6:
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    fig.tight_layout()
    return canvas
