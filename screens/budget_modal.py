from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

import db

PESO = "₱"


class BudgetModal(ModalScreen[bool]):
    DEFAULT_CSS = """
    BudgetModal {
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

    BINDINGS = [
        Binding("escape", "cancel", show=False, priority=True),
    ]

    def __init__(self, category=None, current_limit=None):
        super().__init__()
        self.existing_category = category
        self.current_limit = current_limit

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(
                "Edit Budget Limit" if self.existing_category else "Add Budget Limit",
                id="dialog-title",
            )
            yield Label("Category:", classes="field-label")
            yield Input(
                value=self.existing_category or "",
                id="inp-cat",
                placeholder="e.g. Food",
                disabled=bool(self.existing_category),
            )
            yield Label(f"Monthly limit ({PESO}):", classes="field-label")
            yield Input(
                value=str(self.current_limit) if self.current_limit else "",
                id="inp-limit",
                placeholder="e.g. 5000",
            )
            with Horizontal(id="buttons"):
                yield Button("Cancel", variant="default", id="btn-cancel")
                yield Button("Save", variant="primary", id="btn-save")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "inp-cat":
            self.query_one("#inp-limit", Input).focus()
        elif event.input.id == "inp-limit":
            self._save()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(False)
        elif event.button.id == "btn-save":
            self._save()

    def action_cancel(self) -> None:
        self.dismiss(False)

    def _save(self) -> None:
        cat_val = self.query_one("#inp-cat", Input).value.strip()
        limit_str = self.query_one("#inp-limit", Input).value.strip()

        if not cat_val or not limit_str:
            self.app.notify("All fields are required.", severity="error")
            return
        try:
            limit = float(limit_str)
            if limit <= 0:
                raise ValueError
        except ValueError:
            self.app.notify("Limit must be a positive number.", severity="error")
            return

        db.set_budget(cat_val, limit)
        self.app.notify(f"Budget set: {cat_val} → {PESO}{limit:,.2f}/mo")
        self.dismiss(True)
