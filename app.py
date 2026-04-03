from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Header, Static, TabbedContent, TabPane

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

    # priority=True so all bindings fire before any focused widget (e.g. DataTable)
    BINDINGS = [
        Binding("1", "switch_tab('dashboard')",    "Dashboard",    show=True, priority=True),
        Binding("2", "switch_tab('transactions')", "Transactions", show=True, priority=True),
        Binding("3", "switch_tab('summary')",      "Summary",      show=True, priority=True),
        Binding("4", "switch_tab('charts')",       "Charts",       show=True, priority=True),
        Binding("5", "switch_tab('budgets')",      "Budgets",      show=True, priority=True),
        Binding("a", "add_transaction",            "Add",          show=True, priority=True),
        Binding("e", "edit",                       "Edit",         show=True, priority=True),
        Binding("d", "delete",                     "Delete",       show=True, priority=True),
        Binding("n", "add_limit",                  "Add Limit",    show=True, priority=True),
        Binding("s", "set_daily",                  "Daily Budget", show=True, priority=True),
        Binding("comma",      "prev_month", ", Prev Month", show=True, priority=True),
        Binding("full_stop",  "next_month", ". Next Month", show=True, priority=True),
        Binding("q", "quit",                       "Quit",         show=True, priority=True),
    ]

    # Maps tab id → pane class that has action_prev/next_month
    _MONTH_PANES = {
        "transactions": TransactionsPane,
        "summary":      SummaryPane,
        "charts":       ChartsPane,
    }

    DEFAULT_CSS = """
    TabbedContent { height: 1fr; }
    TabPane      { padding: 0;  }
    #footer-bar  {
        dock: bottom;
        height: 1;
        background: $primary-darken-2;
        color: $text;
        padding: 0 1;
    }
    """

    def on_mount(self) -> None:
        db.init_db()

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="dashboard"):
            with TabPane("1 Dashboard",    id="dashboard"):
                yield DashboardPane()
            with TabPane("2 Transactions", id="transactions"):
                yield TransactionsPane()
            with TabPane("3 Summary",      id="summary"):
                yield SummaryPane()
            with TabPane("4 Charts",       id="charts"):
                yield ChartsPane()
            with TabPane("5 Budgets",      id="budgets"):
                yield BudgetsPane()
        yield Static(
            Text(" [1-5] Switch tab  [a] Add  [e] Edit  [d] Delete"
                 "  [,] Prev month  [.] Next month  [n] Budget  [s] Daily  [q] Quit"),
            id="footer-bar",
        )

    # ── Tab switching ─────────────────────────────────────────────────────────

    def action_switch_tab(self, tab_id: str) -> None:
        self.query_one(TabbedContent).active = tab_id

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Auto-focus the DataTable inside the newly active tab."""
        self.call_after_refresh(self._focus_active_table)

    def _focus_active_table(self) -> None:
        active_id = self.query_one(TabbedContent).active
        try:
            pane = self.query_one(f"#{active_id}")
            table = next(iter(pane.query(DataTable)), None)
            if table:
                table.focus()
        except Exception:
            pass

    # ── Month navigation (routed to the active pane) ──────────────────────────

    def action_prev_month(self) -> None:
        self._route_month("action_prev_month")

    def action_next_month(self) -> None:
        self._route_month("action_next_month")

    def _route_month(self, action: str) -> None:
        active = self.query_one(TabbedContent).active
        cls = self._MONTH_PANES.get(active)
        if cls:
            try:
                getattr(self.query_one(cls), action)()
            except Exception:
                pass

    # ── Edit / Delete (routed by active tab) ─────────────────────────────────

    def action_edit(self) -> None:
        active = self.query_one(TabbedContent).active
        if active == "transactions":
            self.query_one(TransactionsPane).action_edit_selected()
        elif active == "budgets":
            self.query_one(BudgetsPane).action_edit_selected()

    def action_delete(self) -> None:
        active = self.query_one(TabbedContent).active
        if active == "transactions":
            self.query_one(TransactionsPane).action_delete_selected()
        elif active == "budgets":
            self.query_one(BudgetsPane).action_delete_selected()

    def action_add_limit(self) -> None:
        if self.query_one(TabbedContent).active == "budgets":
            self.query_one(BudgetsPane).action_add_budget()

    def action_set_daily(self) -> None:
        if self.query_one(TabbedContent).active == "budgets":
            self.query_one(BudgetsPane).action_set_daily()

    # ── Add transaction ───────────────────────────────────────────────────────

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
