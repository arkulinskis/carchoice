from anvil import *

from ._anvil_designer import SourcesTabTemplate
from ... import state


class SourcesTab(SourcesTabTemplate):
    """Admin -> Data sources: the wishlist of published material (books, manuals, datasets) and its status."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.sources_panel.add_event_handler("x-edit", self._edit)
        self.sources_panel.add_event_handler("x-deleted", self._load)
        self._load()

    def _load(self, **event_args):
        self.d = state.call("admin_sources")
        self.sources_panel.items = self.d["sources"]

    def _open(self, source):
        from ...Dialogs.EditSource import EditSource
        if alert(EditSource(source=source, kinds=self.d["kinds"], statuses=self.d["statuses"]), buttons=[], role="app-dialog", large=True):
            state.toast("Saved.", "ok")
            self._load()

    def _edit(self, item, **event_args):
        self._open(item)

    @handle("add_button", "click")
    def add_button_click(self, **event_args):
        self._open(None)
