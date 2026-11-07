import anvil.server
from anvil import *

from ._anvil_designer import PicksTemplate
from ... import fmt, picks, prefs, queries, router, state

CURRENCIES = ["USD", "CAD", "EUR", "GBP", "AUD"]


class Picks(PicksTemplate):
    """#picks: the member's five as ranked cards (notes, saved listings and the best price so far), with their search
    preferences on top. Cards raise x-find / x-add / x-move / x-remove."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        state.heading(self.title, 1)
        state.heading(self.prefs_title, 2)
        for ev, fn in (("x-find", self._find), ("x-add", self._add), ("x-move", self._move), ("x-remove", self._remove)):
            self.cards_panel.add_event_handler(ev, fn)
        self.currency_dd.items = CURRENCIES
        self.region_dd.items = queries.REGIONS
        state.set_control_attr(self.currency_dd, "aria-label", "Currency")
        state.set_control_attr(self.region_dd, "aria-label", "Region")
        for box in (self.budget_box, self.km_box, self.year_box):
            state.set_control_attr(box, "inputmode", "numeric")
        self._miles = fmt.units() == "imperial"
        self.dom_nodes["km_cap"].textContent = "Max miles" if self._miles else "Max km"
        prefs.forget()
        self._load()

    def _load(self, r=None):
        r = r or anvil.server.call("get_picks")
        picks.set_from(r)
        cars = r["picks"]
        total = len(cars)
        items = [dict(c, total=total) for c in cars] + [{"empty": True, "rank": i + 1} for i in range(total, r["max"])]
        self.cards_panel.items = items
        self.sub.text = ("%d of %d picked. Rank them, take notes, then go find them for sale." % (total, r["max"])) if total else \
            "Nothing picked yet. Star up to five cars on Explore and they land here."
        self.compare_button.enabled = total >= 2
        p = r.get("prefs") or {}
        self.p = p
        self.budget_box.text = str(p.get("budget") or "")
        self.year_box.text = str(p.get("year_from") or "")
        self.place_box.text = p.get("place") or ""
        km = p.get("max_km")
        self.km_box.text = (str(int(round(km * 0.621371))) if self._miles else str(km)) if km else ""
        self.currency_dd.selected_value = p.get("currency") or "USD"
        self.region_dd.selected_value = queries.default_region(p)

    @handle("prefs_button", "click")
    def prefs_button_click(self, **event_args):
        p = dict(self.p)
        for key, box in (("budget", self.budget_box), ("max_km", self.km_box), ("year_from", self.year_box)):
            v = prefs.number(box.text)
            if v is False:
                state.toast("%s needs to be a number." % key.replace("_", " ").capitalize(), "error")
                return
            if key == "max_km" and v and self._miles:
                v = int(round(v / 0.621371))
            p[key] = v
        p.update(place=(self.place_box.text or "").strip(), currency=self.currency_dd.selected_value,
                 region=self.region_dd.selected_value)
        if prefs.save(p):
            self.p = prefs.get()
            state.toast("Saved. Your searches use them now.", "ok")

    @handle("compare_button", "click")
    def compare_button_click(self, **event_args):
        router.go("compare")

    def _find(self, item, **event_args):
        from ...Dialogs.FindListings import FindListings
        if alert(FindListings(car=item), buttons=[], role="app-dialog", large=True) == "add":
            self._add(item)

    def _add(self, item, **event_args):
        from ...Dialogs.AddListing import AddListing
        if alert(AddListing(car_id=item["id"], currency=self.p.get("currency")), buttons=[], role="app-dialog", large=True):
            state.toast("Listing saved.", "ok")
            self._load()

    def _move(self, car_id, delta, key=None, **event_args):
        r = state.call("pick_move", car_id, delta)
        if r is not None:
            self._load(r)
            state.refocus(self.cards_panel, key)

    def _remove(self, item, **event_args):
        if confirm("Its note goes too. Saved listings stay on the Listings page.", title="Take the %s out?" % item["name"],
                   buttons=[("Cancel", False), ("Take it out", True)], role="app-dialog"):
            r = state.call("pick_remove", item["id"])
            if r is not None:
                self._load(r)
