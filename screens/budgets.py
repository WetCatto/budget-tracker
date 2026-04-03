from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import DataTable, Label, Static

import db
from screens.budget_modal import BudgetModal


class BudgetsPane(Vertical):
    BINDINGS = [
        Binding("n", "add_budget", "Add Budget", show=True),
        Binding("e", "edit_selected", "Edit", show=True),
        Binding("d", "delete_selected", "Delete", show=True),
    ]

    DEFAULT_CSS = """
    BudgetsPane {
        padding: 1 2;
    }
    #hint {
        color: $text-muted;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Monthly Budget Limits", id="title")
        yield Static("[n] Add  [e] Edit  [d] Delete", id="hint")
        yield DataTable(id="budget-table", cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one("#budget-table", DataTable)
        table.add_columns("Category", "Monthly Limit")
        self.refresh_data()

    def refresh_data(self) -> None:
        table = self.query_one("#budget-table", DataTable)
        table.clear()
        for b in db.get_budgets():
            table.add_row(
                b["category"],
                Text(f"${b['monthly_limit']:,.2f}", style="yellow"),
                key=b["category"],
            )

    def _get_selected_category(self) -> str | None:
        table = self.query_one("#budget-table", DataTable)
        if table.row_count == 0:
            return None
        try:
            cell_key = table.coordinate_to_cell_key(table.cursor_coordinate)
            return cell_key.row_key.value
        except Exception:
            return None

    def action_add_budget(self) -> None:
        def on_dismiss(saved: bool) -> None:
            if saved:
                self.refresh_data()
                self.app.query_one("DashboardPane").refresh_data()
                self.app.query_one("SummaryPane").refresh_data()

        self.app.push_screen(BudgetModal(), on_dismiss)

    def action_edit_selected(self) -> None:
        category = self._get_selected_category()
        if category is None:
            self.app.notify("No budget selected.", severity="warning")
            return

        budgets = {b["category"]: b["monthly_limit"] for b in db.get_budgets()}
        current_limit = budgets.get(category)

        def on_dismiss(saved: bool) -> None:
            if saved:
                self.refresh_data()
                self.app.query_one("DashboardPane").refresh_data()
                self.app.query_one("SummaryPane").refresh_data()

        self.app.push_screen(BudgetModal(category=category, current_limit=current_limit), on_dismiss)

    def action_delete_selected(self) -> None:
        category = self._get_selected_category()
        if category is None:
            self.app.notify("No budget selected.", severity="warning")
            return
        db.delete_budget(category)
        self.app.notify(f"Removed budget for: {category}")
        self.refresh_data()
        self.app.query_one("DashboardPane").refresh_data()
        self.app.query_one("SummaryPane").refresh_data()
