from datetime import date

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Label, Static

import db

PESO = "₱"


class DashboardPane(Vertical):
    DEFAULT_CSS = """
    DashboardPane {
        padding: 1 2;
    }
    #header-row {
        height: 3;
        padding: 0 1;
        border: round $primary;
        margin-bottom: 1;
    }
    #balance {
        text-style: bold;
        width: 1fr;
        content-align: left middle;
    }
    #today {
        width: auto;
        content-align: right middle;
        color: $text-muted;
    }
    #daily-bar {
        height: 3;
        padding: 0 1;
        border: round $accent;
        margin-bottom: 1;
        content-align: left middle;
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
        with Horizontal(id="header-row"):
            yield Static("", id="balance")
            yield Static("", id="today")
        yield Static("", id="daily-bar")
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

        # Monthly balance
        balance = db.get_monthly_balance(year, month)
        color = "green" if balance >= 0 else "red"
        self.query_one("#balance", Static).update(
            Text(f"  This month's balance: {PESO}{balance:,.2f}", style=f"bold {color}")
        )

        # Today's date
        self.query_one("#today", Static).update(
            Text(f"{today.strftime('%A, %B %d %Y')}  ")
        )

        # Daily budget bar
        daily_budget = db.get_daily_budget()
        today_spending = db.get_today_spending()
        daily_widget = self.query_one("#daily-bar", Static)
        if daily_budget:
            remaining = daily_budget - today_spending
            color = "green" if remaining >= 0 else "bold red"
            t = Text()
            t.append(f"  Today: spent {PESO}{today_spending:,.2f}", style="")
            t.append(f"  /  daily budget {PESO}{daily_budget:,.2f}", style="")
            t.append(f"  →  {PESO}{remaining:,.2f} remaining", style=color)
            daily_widget.update(t)
        else:
            daily_widget.update(
                Text(f"  Today: spent {PESO}{today_spending:,.2f}  (no daily budget set — press [s] in Budgets tab)")
            )

        # Budget warnings
        warnings = db.get_budget_warnings(year, month)
        if warnings:
            lines = [
                f"  ⚠  {w['category']}: spent {PESO}{w['spent']:,.2f} "
                f"(limit {PESO}{w['limit']:,.2f}, over by {PESO}{w['over_by']:,.2f})"
                for w in warnings
            ]
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
            amt_text = Text(f"{PESO}{amt:,.2f}", style="green" if amt > 0 else "red")
            table.add_row(tx["date"], tx["description"], tx["category"], amt_text)
