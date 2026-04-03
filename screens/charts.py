import calendar
from datetime import date

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Static
from textual.scroll_view import ScrollView

import db

PESO = "₱"


def _build_chart(title: str, labels: list, values: list, width: int = 68, height: int = 12) -> Text:
    """Render a horizontal bar chart using plotext, fallback to ASCII if unavailable."""
    try:
        import plotext as plt

        plt.clf()
        plt.theme("dark")
        plt.title(title)
        plt.bar(labels, values, orientation="h")
        plt.plotsize(width, height)
        return Text.from_ansi(plt.build())
    except Exception:
        lines = [f"  {title}", ""]
        if not values:
            lines.append("  (no data)")
            return Text("\n".join(lines))
        max_val = max(values) if values else 1
        bar_width = 30
        for label, val in zip(labels, values):
            filled = int((val / max_val) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            lines.append(f"  {label:15s} {bar} {PESO}{val:,.2f}")
        return Text("\n".join(lines))


class ChartsPane(Vertical):
    BINDINGS = [
        Binding("[", "prev_month", "◀ Month", show=True, priority=True),
        Binding("]", "next_month", "Month ▶", show=True, priority=True),
    ]

    DEFAULT_CSS = """
    ChartsPane {
        padding: 1 2;
        overflow-y: auto;
    }
    #month-label {
        text-style: bold;
        margin-bottom: 1;
    }
    #chart-category {
        height: 14;
        margin-bottom: 1;
        border: round $primary;
        padding: 0 1;
    }
    #chart-monthly {
        height: 14;
        border: round $accent;
        padding: 0 1;
    }
    """

    def __init__(self):
        super().__init__()
        today = date.today()
        self._year = today.year
        self._month = today.month

    def compose(self) -> ComposeResult:
        yield Static("", id="month-label")
        yield Static("", id="chart-category")
        yield Static("", id="chart-monthly")

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        month_name = calendar.month_name[self._month]
        # Use Text() so [ and ] are literal, not Rich markup
        self.query_one("#month-label", Static).update(
            Text(f"  Charts — {month_name} {self._year}   [ Prev month   ] Next month", style="bold")
        )

        rows = db.get_spending_by_category(self._year, self._month)
        labels = [r["category"] for r in rows] if rows else []
        values = [r["total"] for r in rows] if rows else []

        self.query_one("#chart-category", Static).update(
            _build_chart(f"Spending by Category — {month_name} {self._year}", labels, values)
        )

        monthly = db.get_monthly_totals(6)
        m_labels = [r["month"] for r in monthly] if monthly else []
        m_expenses = [r["expenses"] for r in monthly] if monthly else []

        self.query_one("#chart-monthly", Static).update(
            _build_chart("Monthly Expenses (last 6 months)", m_labels, m_expenses)
        )

    def action_prev_month(self) -> None:
        if self._month == 1:
            self._month = 12
            self._year -= 1
        else:
            self._month -= 1
        self.refresh_data()

    def action_next_month(self) -> None:
        if self._month == 12:
            self._month = 1
            self._year += 1
        else:
            self._month += 1
        self.refresh_data()
