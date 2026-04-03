from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ConfirmModal(ModalScreen[bool]):
    DEFAULT_CSS = """
    ConfirmModal {
        align: center middle;
    }
    #dialog {
        width: 54;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: thick $error;
    }
    #title {
        text-style: bold;
        color: $error;
        margin-bottom: 1;
    }
    #detail {
        color: $text-muted;
        margin-bottom: 2;
    }
    #buttons {
        height: auto;
        align: right middle;
    }
    #buttons Button {
        margin-left: 1;
    }
    """

    BINDINGS = [Binding("escape", "dismiss_no", show=False, priority=True)]

    def __init__(self, title: str, detail: str = ""):
        super().__init__()
        self._title = title
        self._detail = detail

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self._title, id="title")
            if self._detail:
                yield Label(self._detail, id="detail")
            with Horizontal(id="buttons"):
                yield Button("Cancel", variant="default", id="btn-no")
                yield Button("Delete", variant="error",   id="btn-yes")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-yes")

    def action_dismiss_no(self) -> None:
        self.dismiss(False)
