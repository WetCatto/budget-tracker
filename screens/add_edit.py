from datetime import date

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

import db

PESO = "₱"


class AddEditModal(ModalScreen[bool]):
    DEFAULT_CSS = """
    AddEditModal {
        align: center middle;
    }
    #dialog {
        width: 66;
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
    #hint {
        color: $text-muted;
        margin-top: 1;
    }
    #nav-hint {
        color: $text-muted;
        margin-top: 1;
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

    _FIELD_ORDER = ["inp-date", "inp-desc", "inp-amount", "inp-cat"]

    def __init__(self, transaction=None):
        super().__init__()
        self.transaction = transaction
        self._categories: list[str] = []
        self._descriptions: list[str] = []
        self._cat_idx = -1
        self._desc_idx = -1

    def compose(self) -> ComposeResult:
        t = self.transaction
        today = date.today().isoformat()

        with Vertical(id="dialog"):
            yield Label(
                "Edit Transaction" if t else "Add Transaction",
                id="dialog-title",
            )
            yield Label("Date (YYYY-MM-DD):", classes="field-label")
            yield Input(value=t["date"] if t else today, id="inp-date")

            yield Label("Description:", classes="field-label")
            yield Input(
                value=t["description"] if t else "",
                id="inp-desc",
                placeholder="e.g. Coffee, Salary  — ↑↓ cycle history",
            )

            yield Label(f"Amount (negative = expense, positive = income):", classes="field-label")
            yield Input(
                value=str(t["amount"]) if t else "",
                id="inp-amount",
                placeholder=f"e.g. -150 or +45000",
            )

            yield Label("Category:", classes="field-label")
            yield Input(
                value=t["category"] if t else "",
                id="inp-cat",
                placeholder="e.g. Food, Rent, Income  — ↑↓ cycle existing",
            )

            yield Static("", id="hint")
            yield Static("Enter / Tab → next field   ↑↓ in Category & Description → cycle values", id="nav-hint")

            with Horizontal(id="buttons"):
                yield Button("Cancel", variant="default", id="btn-cancel")
                yield Button("Save", variant="primary", id="btn-save")

    def on_mount(self) -> None:
        self._categories = db.get_categories()
        self._descriptions = db.get_recent_descriptions()
        self._update_hint()

    def _update_hint(self) -> None:
        cats = ", ".join(self._categories) if self._categories else "none yet"
        self.query_one("#hint", Static).update(
            f"Categories: {cats}"
        )

    # ── Enter advances to next field ──────────────────────────────────────────

    def on_input_submitted(self, event: Input.Submitted) -> None:
        try:
            idx = self._FIELD_ORDER.index(event.input.id)
        except ValueError:
            return
        if idx < len(self._FIELD_ORDER) - 1:
            self.query_one(f"#{self._FIELD_ORDER[idx + 1]}", Input).focus()
        else:
            self._save()

    # ── ↑↓ cycles autocomplete in Category and Description ───────────────────

    def on_key(self, event) -> None:
        focused = self.focused
        if not isinstance(focused, Input):
            return
        if event.key not in ("up", "down"):
            return

        fid = focused.id
        if fid == "inp-cat":
            items = self._categories
            idx_attr = "_cat_idx"
        elif fid == "inp-desc":
            items = self._descriptions
            idx_attr = "_desc_idx"
        else:
            return

        if not items:
            return

        event.prevent_default()
        event.stop()

        idx = getattr(self, idx_attr)
        idx = (idx + 1) % len(items) if event.key == "down" else (idx - 1) % len(items)
        setattr(self, idx_attr, idx)
        focused.value = items[idx]
        focused.cursor_position = len(items[idx])

    # ── Buttons ───────────────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(False)
        elif event.button.id == "btn-save":
            self._save()

    def action_cancel(self) -> None:
        self.dismiss(False)

    def _save(self) -> None:
        date_val   = self.query_one("#inp-date",   Input).value.strip()
        desc_val   = self.query_one("#inp-desc",   Input).value.strip()
        amount_str = self.query_one("#inp-amount", Input).value.strip()
        cat_val    = self.query_one("#inp-cat",    Input).value.strip()

        if not all([date_val, desc_val, amount_str, cat_val]):
            self.app.notify("All fields are required.", severity="error")
            return
        try:
            amount = float(amount_str)
        except ValueError:
            self.app.notify("Amount must be a number (e.g. -150).", severity="error")
            return
        try:
            date.fromisoformat(date_val)
        except ValueError:
            self.app.notify("Date must be YYYY-MM-DD.", severity="error")
            return

        if self.transaction:
            db.update_transaction(self.transaction["id"], date_val, desc_val, amount, cat_val)
            self.app.notify(f"Updated: {desc_val}")
        else:
            db.add_transaction(date_val, desc_val, amount, cat_val)
            self.app.notify(f"Added: {desc_val}")

        self.dismiss(True)
