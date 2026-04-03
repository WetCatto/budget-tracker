from datetime import date

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Label, Static

import db
from screens.add_edit import AddEditModal


class TransactionsPane(Vertical):
    BINDINGS = [
        Binding("e", "edit_selected", "Edit", show=True),
        Binding("d", "delete_selected", "Delete", show=True),
        Binding("[", "prev_month", "◀ Month", show=True),
        Binding("]", "next_month", "Month ▶", show=True),
    ]

    DEFAULT_CSS = """
    TransactionsPane {
        padding: 1 2;
    }
    #filter-bar {
        height: 3;
        align: left middle;
        margin-bottom: 1;
    }
    #month-label {
        text-style: bold;
        width: auto;
        margin-right: 2;
        content-align: left middle;
    }
    #hint {
        color: $text-muted;
        width: auto;
        content-align: left middle;
    }
    """

    def __init__(self):
        super().__init__()
        today = date.today()
        self._year = today.year
        self._month = today.month

    def compose(self) -> ComposeResult:
        with Horizontal(id="filter-bar"):
            yield Static("", id="month-label")
            yield Static("  [e] Edit  [d] Delete  [ ] Prev  ] Next month", id="hint")
        yield DataTable(id="tx-table", cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one("#tx-table", DataTable)
        table.add_columns("Date", "Description", "Category", "Amount")
        self.refresh_data()

    def refresh_data(self) -> None:
        import calendar
        month_name = calendar.month_name[self._month]
        self.query_one("#month-label", Static).update(
            Text(f"  {month_name} {self._year}", style="bold")
        )
        table = self.query_one("#tx-table", DataTable)
        table.clear()
        for tx in db.get_transactions(self._year, self._month):
            amt = tx["amount"]
            amt_text = Text(f"${amt:,.2f}", style="green" if amt > 0 else "red")
            table.add_row(
                tx["date"], tx["description"], tx["category"], amt_text,
                key=str(tx["id"]),
            )

    def _get_selected_id(self) -> int | None:
        table = self.query_one("#tx-table", DataTable)
        if table.row_count == 0:
            return None
        try:
            cell_key = table.coordinate_to_cell_key(table.cursor_coordinate)
            return int(cell_key.row_key.value)
        except Exception:
            return None

    def action_edit_selected(self) -> None:
        tx_id = self._get_selected_id()
        if tx_id is None:
            self.app.notify("No transaction selected.", severity="warning")
            return
        tx = db.get_transaction(tx_id)
        if tx is None:
            return

        def on_dismiss(saved: bool) -> None:
            if saved:
                self.refresh_data()
                self.app.query_one("DashboardPane").refresh_data()
                self.app.query_one("SummaryPane").refresh_data()
                self.app.query_one("ChartsPane").refresh_data()

        self.app.push_screen(AddEditModal(transaction=tx), on_dismiss)

    def action_delete_selected(self) -> None:
        tx_id = self._get_selected_id()
        if tx_id is None:
            self.app.notify("No transaction selected.", severity="warning")
            return
        db.delete_transaction(tx_id)
        self.app.notify("Transaction deleted.")
        self.refresh_data()
        self.app.query_one("DashboardPane").refresh_data()
        self.app.query_one("SummaryPane").refresh_data()
        self.app.query_one("ChartsPane").refresh_data()

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
