from datetime import date

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

import db


class AddEditModal(ModalScreen[bool]):
    DEFAULT_CSS = """
    AddEditModal {
        align: center middle;
    }
    #dialog {
        width: 64;
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
    #hint {
        color: $text-muted;
        margin-top: 1;
    }
    """

    def __init__(self, transaction=None):
        super().__init__()
        self.transaction = transaction  # None = add mode, Row = edit mode

    def compose(self) -> ComposeResult:
        t = self.transaction
        today = date.today().isoformat()
        categories = db.get_categories()
        cat_hint = "Existing: " + ", ".join(categories) if categories else "Type any category name"

        with Vertical(id="dialog"):
            yield Label(
                "Edit Transaction" if t else "Add Transaction",
                id="dialog-title",
            )
            yield Label("Date (YYYY-MM-DD):", classes="field-label")
            yield Input(value=t["date"] if t else today, id="inp-date")
            yield Label("Description:", classes="field-label")
            yield Input(value=t["description"] if t else "", id="inp-desc", placeholder="e.g. Coffee, Salary")
            yield Label("Amount (negative = expense, positive = income):", classes="field-label")
            yield Input(value=str(t["amount"]) if t else "", id="inp-amount", placeholder="e.g. -12.50 or 2000")
            yield Label("Category:", classes="field-label")
            yield Input(value=t["category"] if t else "", id="inp-cat", placeholder="e.g. Food, Rent, Income")
            yield Static(cat_hint, id="hint")
            with Horizontal(id="buttons"):
                yield Button("Cancel", variant="default", id="btn-cancel")
                yield Button("Save", variant="primary", id="btn-save")

    _FIELD_ORDER = ["inp-date", "inp-desc", "inp-amount", "inp-cat"]

    def on_input_submitted(self, event: Input.Submitted) -> None:
        try:
            idx = self._FIELD_ORDER.index(event.input.id)
        except ValueError:
            return
        if idx < len(self._FIELD_ORDER) - 1:
            self.query_one(f"#{self._FIELD_ORDER[idx + 1]}", Input).focus()
        else:
            self._save()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(False)
        elif event.button.id == "btn-save":
            self._save()

    def _save(self) -> None:
        date_val = self.query_one("#inp-date", Input).value.strip()
        desc_val = self.query_one("#inp-desc", Input).value.strip()
        amount_str = self.query_one("#inp-amount", Input).value.strip()
        cat_val = self.query_one("#inp-cat", Input).value.strip()

        if not all([date_val, desc_val, amount_str, cat_val]):
            self.app.notify("All fields are required.", severity="error")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            self.app.notify("Amount must be a number (e.g. -12.50).", severity="error")
            return

        try:
            date.fromisoformat(date_val)
        except ValueError:
            self.app.notify("Date must be YYYY-MM-DD format.", severity="error")
            return

        if self.transaction:
            db.update_transaction(self.transaction["id"], date_val, desc_val, amount, cat_val)
            self.app.notify(f"Updated: {desc_val}")
        else:
            db.add_transaction(date_val, desc_val, amount, cat_val)
            self.app.notify(f"Added: {desc_val}")

        self.dismiss(True)
