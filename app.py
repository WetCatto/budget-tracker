from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Static, TabbedContent, TabPane

import db
from screens.add_edit import AddEditModal
from screens.budgets import BudgetsPane
from screens.charts import ChartsPane
from screens.dashboard import DashboardPane
from screens.summary import SummaryPane
from screens.transactions import TransactionsPane


class BudgetApp(App):
    TITLE = "Budget Tracker"
    SUB_TITLE = "Local & Offline"

    BINDINGS = [
        Binding("1", "switch_tab('dashboard')", "Dashboard", show=True),
        Binding("2", "switch_tab('transactions')", "Transactions", show=True),
        Binding("3", "switch_tab('summary')", "Summary", show=True),
        Binding("4", "switch_tab('charts')", "Charts", show=True),
        Binding("5", "switch_tab('budgets')", "Budgets", show=True),
        Binding("a", "add_transaction", "Add Transaction", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    DEFAULT_CSS = """
    TabbedContent {
        height: 1fr;
    }
    TabPane {
        padding: 0;
    }
    #footer-bar {
        height: 1;
        background: $primary;
        color: $text;
        content-align: left middle;
        padding: 0 1;
    }
    """

    def on_mount(self) -> None:
        db.init_db()

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="dashboard"):
            with TabPane("1 Dashboard", id="dashboard"):
                yield DashboardPane()
            with TabPane("2 Transactions", id="transactions"):
                yield TransactionsPane()
            with TabPane("3 Summary", id="summary"):
                yield SummaryPane()
            with TabPane("4 Charts", id="charts"):
                yield ChartsPane()
            with TabPane("5 Budgets", id="budgets"):
                yield BudgetsPane()
        yield Static(
            " [1-5] Tab  [a] Add  [e] Edit  [d] Delete  [[] /] Month  [n] Budget Limit  [q] Quit",
            id="footer-bar",
        )

    def action_switch_tab(self, tab_id: str) -> None:
        tabs = self.query_one(TabbedContent)
        tabs.active = tab_id

    def action_add_transaction(self) -> None:
        def on_dismiss(saved: bool) -> None:
            if saved:
                self._refresh_all()

        self.push_screen(AddEditModal(), on_dismiss)

    def _refresh_all(self) -> None:
        for cls in (DashboardPane, TransactionsPane, SummaryPane, ChartsPane):
            try:
                self.query_one(cls).refresh_data()
            except Exception:
                pass
