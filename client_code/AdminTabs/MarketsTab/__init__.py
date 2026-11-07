from anvil import *

from ._anvil_designer import MarketsTabTemplate
from ... import state


class MarketsTab(MarketsTabTemplate):
    """Admin -> Marketplaces: add, edit, hide or delete the places people are sent to."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.markets_panel.add_event_handler("x-edit", self._edit)
        self.markets_panel.add_event_handler("x-deleted", self._load)
        self._load()

    def _load(self, **event_args):
        self.d = state.call("admin_markets")
        self.markets_panel.items = self.d["markets"]

    def _open(self, market):
        from ...Dialogs.EditMarket import EditMarket
        if alert(EditMarket(market=market, regions=self.d["regions"], kinds=self.d["kinds"]), buttons=[], role="app-dialog", large=True):
            state.toast("Saved.", "ok")
            self._load()

    def _edit(self, item, **event_args):
        self._open(item)

    @handle("add_button", "click")
    def add_button_click(self, **event_args):
        self._open(None)
