from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

import db

PESO = "₱"


class DailyBudgetModal(ModalScreen[bool]):
    DEFAULT_CSS = """
    DailyBudgetModal {
        align: center middle;
    }
    #dialog {
        width: 52;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: thick $primary;
    }
    #dialog-title {
        text-style: bold;
        margin-bottom: 1;
        color: $accent;
    }
    .field-label {
        margin-top: 1;
        color: $text-muted;
    }
    #buttons {
        margin-top: 2;
        height: auto;
        align: right middle;
    }
    #buttons Button {
        margin-left: 1;
    }
    """

    BINDINGS = [Binding("escape", "cancel", show=False, priority=True)]

    def __init__(self):
        super().__init__()
        self._current = db.get_daily_budget()

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Set Daily Budget", id="dialog-title")
            yield Label(f"Daily spending limit ({PESO}):", classes="field-label")
            yield Input(
                value=str(self._current) if self._current else "",
                id="inp-limit",
                placeholder="e.g. 500",
            )
            with Horizontal(id="buttons"):
                yield Button("Cancel", variant="default", id="btn-cancel")
                yield Button("Save", variant="primary", id="btn-save")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(False)
            return

        limit_str = self.query_one("#inp-limit", Input).value.strip()
        if not limit_str:
            self.app.notify("Enter a daily limit.", severity="error")
            return
        try:
            limit = float(limit_str)
            if limit <= 0:
                raise ValueError
        except ValueError:
            self.app.notify("Must be a positive number.", severity="error")
            return

        db.set_daily_budget(limit)
        self.app.notify(f"Daily budget set to {PESO}{limit:,.2f}")
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)
