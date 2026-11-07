import anvil.server
from anvil import *

from ._anvil_designer import SearchesTemplate
from ... import state


class Searches(SearchesTemplate):
    """#searches: the member's saved Explore filters. Open, copy the link, rename, delete."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        state.heading(self.title, 1)
        state.heading(self.empty_title, 2)
        self.list_panel.add_event_handler("x-deleted", self._load)
        self.list_panel.add_event_handler("x-rename", self._rename)
        self._load()

    def _load(self, **event_args):
        items = anvil.server.call("list_searches")["searches"]
        self.list_panel.items = items
        self.empty.visible = not items
        self.sub.text = state.plural(len(items), "search", "searches") if items else ""

    def _rename(self, item, **event_args):
        from ...Dialogs.SaveSearch import SaveSearch
        if alert(SaveSearch(search=item), buttons=[], role="app-dialog"):
            state.toast("Renamed.", "ok")
            self._load()
