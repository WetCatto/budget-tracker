from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import DataTable, Label, Static

import db
from screens.budget_modal import BudgetModal
from screens.confirm import ConfirmModal
from screens.daily_budget_modal import DailyBudgetModal

PESO = "₱"


class BudgetsPane(Vertical):
    BINDINGS = [
        Binding("n", "add_budget",      "Add Budget Limit",   show=True),
        Binding("e", "edit_selected",   "Edit Budget Limit",  show=True),
        Binding("d", "delete_selected", "Delete Budget Limit", show=True),
        Binding("s", "set_daily",       "Set Daily Budget",   show=True),
    ]

    DEFAULT_CSS = """
    BudgetsPane { padding: 1 2; }
    #daily-info {
        height: 3;
        padding: 0 1;
        border: round $accent;
        margin-bottom: 1;
        content-align: left middle;
    }
    #hint { color: $text-muted; margin-bottom: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Static("", id="daily-info")
        yield Static("[n] Add limit  [e] Edit limit  [d] Delete limit  [s] Set daily budget", id="hint")
        yield DataTable(id="budget-table", cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one("#budget-table", DataTable)
        table.add_columns("Category", "Monthly Limit")
        self.refresh_data()

    def refresh_data(self) -> None:
        # Daily budget line
        daily = db.get_daily_budget()
        daily_widget = self.query_one("#daily-info", Static)
        if daily:
            daily_widget.update(
                Text(f"  Daily Budget: {PESO}{daily:,.2f} / day   [s] to change", style="bold")
            )
        else:
            daily_widget.update(
                Text(f"  No daily budget set.  Press [s] to set one.", style="bold $text-muted")
            )

        # Monthly limits table
        table = self.query_one("#budget-table", DataTable)
        table.clear()
        for b in db.get_budgets():
            table.add_row(
                b["category"],
                Text(f"{PESO}{b['monthly_limit']:,.2f}", style="yellow"),
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

    def _on_saved(self, saved: bool) -> None:
        if saved:
            self.refresh_data()
            self.app.query_one("DashboardPane").refresh_data()
            self.app.query_one("SummaryPane").refresh_data()

    def action_add_budget(self) -> None:
        self.app.push_screen(BudgetModal(), self._on_saved)

    def action_edit_selected(self) -> None:
        category = self._get_selected_category()
        if category is None:
            self.app.notify("Select a budget limit first.", severity="warning")
            return
        budgets = {b["category"]: b["monthly_limit"] for b in db.get_budgets()}
        self.app.push_screen(
            BudgetModal(category=category, current_limit=budgets.get(category)),
            self._on_saved,
        )

    def action_delete_selected(self) -> None:
        category = self._get_selected_category()
        if category is None:
            self.app.notify("Select a budget limit first.", severity="warning")
            return

        def on_confirm(confirmed: bool) -> None:
            if confirmed:
                db.delete_budget(category)
                self.app.notify(f"Removed budget limit for: {category}")
                self._on_saved(True)

        self.app.push_screen(
            ConfirmModal(
                "Delete Budget Limit",
                f"Remove the monthly limit for \"{category}\"?",
            ),
            on_confirm,
        )

    def action_set_daily(self) -> None:
        self.app.push_screen(DailyBudgetModal(), self._on_saved)
