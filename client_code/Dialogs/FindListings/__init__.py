import anvil.server
from anvil import *

from ._anvil_designer import FindListingsTemplate
from ... import prefs, queries, state


class FindListings(FindListingsTemplate):
    """Searches for one car on the marketplaces of a region. car = a car summary. Closes with "add" when the person
    wants to save a listing next, else None."""

    def __init__(self, car=None, **properties):
        super().__init__(**properties)
        self.car = car or {}
        self.heading.text = "Find the %s for sale" % self.car.get("name", "car")
        state.heading(self.heading, 2)
        self.markets = anvil.server.call("list_marketplaces")["markets"]
        self.p = prefs.get()
        self.prefs_line.text = ("Your search: " + queries.prefs_line(self.p)) if queries.prefs_line(self.p) else \
            "Tip: set your budget and mileage on Your five, and they show here."
        self.words_box.text = queries.car_words(self.car.get("name", ""))
        self.region_dd.items = queries.REGIONS
        self.region_dd.selected_value = queries.default_region(self.p)
        state.set_control_attr(self.region_dd, "aria-label", "Region")
        self._draw()

    def _draw(self):
        region = self.region_dd.selected_value
        words = (self.words_box.text or "").strip()
        self.links_panel.items = queries.links(words, self.markets, region, words.replace('"', ""))
        g = queries.guides(self.markets, region)
        self.guides.text = ("Check the price with: " + ", ".join(m["name"] for m in g)) if g else ""

    @handle("region_dd", "change")
    def region_dd_change(self, **event_args):
        self._draw()
        if state.me():
            p = dict(self.p, region=self.region_dd.selected_value)
            if prefs.save(p):
                self.p = p

    @handle("words_box", "pressed_enter")
    def words_box_pressed_enter(self, **event_args):
        self._draw()

    @handle("words_box", "lost_focus")
    def words_box_lost_focus(self, **event_args):
        self._draw()

    @handle("close_button", "click")
    def close_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)

    @handle("add_button", "click")
    def add_button_click(self, **event_args):
        self.raise_event("x-close-alert", value="add")
