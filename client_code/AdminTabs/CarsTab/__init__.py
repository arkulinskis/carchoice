from anvil import *

from ._anvil_designer import CarsTabTemplate
from ... import catalog, state


class CarsTab(CarsTabTemplate):
    """Admin -> Cars: find a car, hide/show it on Explore, or delete it."""

    def __init__(self, **properties):
        super().__init__(**properties)
        state.set_control_attr(self.search_box, "aria-label", "Search cars")
        self.cars_panel.add_event_handler("x-deleted", self._deleted)
        self.cars_panel.add_event_handler("x-changed", self._changed)
        self._load()

    def _load(self, **event_args):
        d = state.call("admin_cars", self.search_box.text or "")
        self.cars_panel.items = d["cars"]
        shown = len(d["cars"])
        self.count.text = state.plural(d["total"], "car") + ((" (first %d shown)" % shown) if shown < d["total"] else "")

    def _deleted(self, **event_args):
        catalog.forget()
        state.toast("Deleted.", "ok")
        self._load()

    def _changed(self, **event_args):
        catalog.forget()

    @handle("search_box", "pressed_enter")
    def search_box_pressed_enter(self, **event_args):
        self._load()

    @handle("search_button", "click")
    def search_button_click(self, **event_args):
        self._load()
