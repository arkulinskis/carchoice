import anvil.server
from anvil import *

from ._anvil_designer import EditMarketTemplate
from ... import state


class EditMarket(EditMarketTemplate):
    """Add or edit a marketplace (admins). market = the row dict or None. Closes with the saved one, or None."""

    def __init__(self, market=None, regions=(), kinds=(), **properties):
        super().__init__(**properties)
        m = market or {}
        self.market = m
        self.heading.text = "Edit %s" % m["name"] if m.get("id") else "Add a marketplace"
        state.heading(self.heading, 2)
        self.region_dd.items, self.kind_dd.items = list(regions), list(kinds)
        self.name_box.text, self.url_box.text = m.get("name", ""), m.get("url", "")
        self.search_box.text, self.notes_box.text = m.get("search_url", ""), m.get("notes", "")
        self.region_dd.selected_value = m.get("region") or (list(regions) or ["US"])[0]
        self.kind_dd.selected_value = m.get("kind") or (list(kinds) or ["Marketplace"])[0]
        self.active_box.checked = m.get("active", True)

    @handle("cancel_button", "click")
    def cancel_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)

    @handle("save_button", "click")
    def save_button_click(self, **event_args):
        data = {"id": self.market.get("id"), "name": self.name_box.text, "url": (self.url_box.text or "").strip(),
                "search_url": (self.search_box.text or "").strip(), "notes": self.notes_box.text,
                "region": self.region_dd.selected_value, "kind": self.kind_dd.selected_value, "active": self.active_box.checked}
        r = anvil.server.call("save_market", data)
        if not r.get("ok"):
            self.message.text, self.message.visible = r.get("error"), True
            return
        self.raise_event("x-close-alert", value=r["market"])
