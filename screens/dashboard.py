from datetime import date

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Label, Static

import db


class DashboardPane(Vertical):
    DEFAULT_CSS = """
    DashboardPane {
        padding: 1 2;
    }
    #balance {
        text-style: bold;
        height: 3;
        content-align: left middle;
        padding: 0 1;
        border: round $primary;
        margin-bottom: 1;
    }
    #warnings {
        height: auto;
        padding: 0 1;
        border: round $warning;
        margin-bottom: 1;
    }
    #warnings-title {
        text-style: bold;
        margin-bottom: 0;
    }
    #recent-title {
        text-style: bold;
        margin-bottom: 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("", id="balance")
        yield Label("Budget Warnings", id="warnings-title")
        yield Static("", id="warnings")
        yield Label("Recent Transactions (this month)", id="recent-title")
        yield DataTable(id="recent-table", cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one("#recent-table", DataTable)
        table.add_columns("Date", "Description", "Category", "Amount")
        self.refresh_data()

    def refresh_data(self) -> None:
        today = date.today()
        year, month = today.year, today.month

        # Balance
        balance = db.get_monthly_balance(year, month)
        color = "green" if balance >= 0 else "red"
        self.query_one("#balance", Static).update(
            Text(f"  This month's balance: ${balance:,.2f}", style=f"bold {color}")
        )

        # Budget warnings
        warnings = db.get_budget_warnings(year, month)
        if warnings:
            lines = []
            for w in warnings:
                lines.append(
                    f"  ⚠  {w['category']}: spent ${w['spent']:.2f} "
                    f"(limit ${w['limit']:.2f}, over by ${w['over_by']:.2f})"
                )
            self.query_one("#warnings", Static).update(
                Text("\n".join(lines), style="bold red")
            )
        else:
            self.query_one("#warnings", Static).update(
                Text("  All budgets on track ✓", style="green")
            )

        # Recent transactions
        table = self.query_one("#recent-table", DataTable)
        table.clear()
        for tx in db.get_transactions(year, month)[:10]:
            amt = tx["amount"]
            amt_text = Text(f"${amt:,.2f}", style="green" if amt > 0 else "red")
            table.add_row(tx["date"], tx["description"], tx["category"], amt_text)
