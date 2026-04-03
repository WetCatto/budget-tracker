import calendar
from datetime import date

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

import db

PESO = "₱"


def _build_chart(title: str, labels: list, values: list,
                 width: int = 60, height: int = 8) -> Text:
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
        max_val = max(values)
        for label, val in zip(labels, values):
            filled = int((val / max_val) * 28)
            bar = "█" * filled + "░" * (28 - filled)
            lines.append(f"  {label:14s} {bar} {PESO}{val:,.2f}")
        return Text("\n".join(lines))


class ChartsPane(Vertical):
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
        height: 11;
        border: round $primary;
        padding: 0 1;
        margin-bottom: 2;
    }
    #chart-monthly {
        height: 11;
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
        self.query_one("#month-label", Static).update(
            Text(f"  Charts — {month_name} {self._year}   < prev month   > next month", style="bold")
        )

        rows = db.get_spending_by_category(self._year, self._month)
        labels = [r["category"] for r in rows]
        values = [r["total"]    for r in rows]
        self.query_one("#chart-category", Static).update(
            _build_chart(f"Spending by Category — {month_name} {self._year}", labels, values)
        )

        monthly = db.get_monthly_totals(6)
        self.query_one("#chart-monthly", Static).update(
            _build_chart(
                "Monthly Expenses (last 6 months)",
                [r["month"]    for r in monthly],
                [r["expenses"] for r in monthly],
            )
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
