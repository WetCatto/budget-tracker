import calendar
from datetime import date

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Label, Static

import db


class SummaryPane(Vertical):
    BINDINGS = [
        Binding("[", "prev_month", "◀ Month", show=True),
        Binding("]", "next_month", "Month ▶", show=True),
    ]

    DEFAULT_CSS = """
    SummaryPane {
        padding: 1 2;
    }
    #month-label {
        text-style: bold;
        margin-bottom: 1;
    }
    #totals {
        height: 5;
        padding: 0 1;
        border: round $primary;
        margin-bottom: 1;
    }
    """

    def __init__(self):
        super().__init__()
        today = date.today()
        self._year = today.year
        self._month = today.month

    def compose(self) -> ComposeResult:
        yield Static("", id="month-label")
        yield Static("", id="totals")
        yield DataTable(id="summary-table", cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one("#summary-table", DataTable)
        table.add_columns("Category", "Income", "Spent", "Budget Limit", "Remaining")
        self.refresh_data()

    def refresh_data(self) -> None:
        month_name = calendar.month_name[self._month]
        self.query_one("#month-label", Static).update(
            Text(f"  Monthly Summary — {month_name} {self._year}  [[] Prev  ] Next", style="bold")
        )

        rows = db.get_monthly_summary(self._year, self._month)

        total_income = sum(r["income"] for r in rows)
        total_spent = sum(r["spent"] for r in rows)
        net = total_income - total_spent
        net_color = "green" if net >= 0 else "red"

        totals_text = Text()
        totals_text.append(f"  Total Income:   ${total_income:>10,.2f}\n", style="green")
        totals_text.append(f"  Total Expenses: ${total_spent:>10,.2f}\n", style="red")
        totals_text.append(f"  Net:            ${net:>10,.2f}", style=f"bold {net_color}")
        self.query_one("#totals", Static).update(totals_text)

        table = self.query_one("#summary-table", DataTable)
        table.clear()
        for r in rows:
            limit = r["monthly_limit"]
            spent = r["spent"]
            income = r["income"]

            if limit:
                remaining = limit - spent
                remaining_text = Text(
                    f"${remaining:,.2f}",
                    style="green" if remaining >= 0 else "bold red",
                )
                limit_text = Text(f"${limit:,.2f}")
            else:
                remaining_text = Text("—", style="$text-muted")
                limit_text = Text("—")

            spent_text = Text(f"${spent:,.2f}", style="red" if spent > 0 else "")
            income_text = Text(f"${income:,.2f}", style="green" if income > 0 else "")

            table.add_row(
                r["category"],
                income_text,
                spent_text,
                limit_text,
                remaining_text,
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
