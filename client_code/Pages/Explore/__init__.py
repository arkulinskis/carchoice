import json

import anvil.server
from anvil import *
from anvil.js import window

from ._anvil_designer import ExploreTemplate
from ... import catalog, fmt, picks, prefs, queries, router, state


class Explore(ExploreTemplate):
    """#explore[/<filters>]: the whole catalogue in one full-width filter table (Components/Explorer, a JS engine),
    a side panel that turns the current filters into marketplace searches, and the tray of the person's five.
    The address keeps the filters (shareable); Save search stores them on the account."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        state.heading(self.title, 1)
        state.heading(self.q_title, 2)
        state.heading(self.pop_title, 2)
        state.heading(self.tray_title, 2)
        self.summary = {}
        self.cars_by_id = {}
        raw = window.CC.decodeState(args[0]) if args else None
        start = json.loads(window.JSON.stringify(raw)) if raw else None  # a real dict, not a JS object
        self.p = prefs.get()
        self.markets = anvil.server.call("list_marketplaces")["markets"]
        self.region_dd.items = queries.REGIONS
        self.region_dd.selected_value = queries.default_region(self.p)
        state.set_control_attr(self.region_dd, "aria-label", "Where to look")
        self.budget_box.text = str(self.p.get("budget") or "")
        self.year_box.text = str(self.p.get("year_from") or "")
        self.place_box.text = self.p.get("place") or ""
        self._miles = fmt.units() == "imperial"
        km = self.p.get("max_km")
        self.km_box.text = (str(int(round(km * 0.621371))) if self._miles else str(km)) if km else ""
        for box in (self.budget_box, self.km_box, self.year_box):
            state.set_control_attr(box, "inputmode", "numeric")
        self.explorer.add_event_handler("x_change", self._changed)
        self.explorer.add_event_handler("x_pick", self._pick)
        self.explorer.add_event_handler("x_open", self._open)
        self.tray_panel.add_event_handler("x-unpick", self._unpick)
        self.explorer.start(catalog.text(), start, picks.ids())
        self._draw_tray()
        pop = anvil.server.call_s("popular_picks", 8)
        self.popular_panel.items = pop
        self.pop_empty.visible = not pop
        self._draw_prefs()

    # ---- the engine's events
    def _changed(self, summary, **event_args):
        if not str(window.location.hash or "#explore").startswith("#explore"):
            return  # a late report after the person already left the page: don't pull the address back
        self.summary = summary
        enc = summary.get("encoded") or ""
        if summary.get("active"):
            router.replace("explore", enc)
        else:
            router.replace("explore")
        self._draw_query()

    def _pick(self, car_id, **event_args):
        picks.toggle(car_id)
        ids = picks.ids()
        self.explorer.set_picked(ids)
        self._draw_tray()

    def _unpick(self, car_id, **event_args):
        key = state.focus_key()
        picks.toggle(car_id)
        self.explorer.set_picked(picks.ids())
        self._draw_tray()
        state.refocus(self.tray_panel, key, self.five_button)

    def _open(self, car_id, **event_args):
        router.go("car", car_id)

    # ---- the tray of five
    def _draw_tray(self):
        cars = picks.load()
        ids = [c["id"] for c in cars]
        slots = [{"i": i, "id": c["id"], "name": c["name"]} for i, c in enumerate(cars)]
        slots += [{"i": i, "empty": True} for i in range(len(slots), picks.MAX)]
        self.tray_panel.items = slots
        self.tray_count.text = "%d of %d picked" % (len(ids), picks.MAX) if ids else "Star cars in the table to keep them here."
        self.compare_button.enabled = len(ids) >= 2
        self.compare_button.tooltip = "" if len(ids) >= 2 else "Pick at least two cars to compare"
        self.five_button.text = "Open your five" if state.me() else "Save your five"

    @handle("compare_button", "click")
    def compare_button_click(self, **event_args):
        router.go("compare")

    @handle("five_button", "click")
    def five_button_click(self, **event_args):
        if state.me():
            router.go("picks")
        else:
            router.remember_after("#picks")
            state.toast("Create a free account to keep your five, your searches and the listings you find.")
            router.go("auth", "signup")

    # ---- searches for the marketplaces
    def _draw_query(self):
        words, simple, explain = queries.explore_words(self.summary)
        self._simple = simple
        self.q_box.text = words
        self.q_explain.text = explain
        self._draw_links()

    def _draw_links(self):
        words = (self.q_box.text or "").strip()
        region = self.region_dd.selected_value
        self.links_panel.items = queries.links(words, self.markets, region, getattr(self, "_simple", "") or words)
        g = queries.guides(self.markets, region)
        self.guides.text = ("Check prices with: " + ", ".join(m["name"] for m in g)) if g else ""
        extra = queries.prefs_line(self.p)
        self.google_link.url = "https://www.google.com/search?q=" + window.encodeURIComponent(
            (words + " for sale " + (("near " + self.p["place"]) if self.p.get("place") else "")).strip()) if words else ""
        self.google_link.visible = bool(words)
        state.set_attr(self.google_link, "rel", "noopener")
        self.prefs_line.text = ("Then set on each site: " + extra) if extra else "Add a budget and mileage to remember them for every search."

    def _draw_prefs(self):
        self.dom_nodes["km_cap"].textContent = "Max miles" if self._miles else "Max km"
        self._draw_links()

    @handle("q_box", "pressed_enter")
    def q_box_pressed_enter(self, **event_args):
        self._draw_links()

    @handle("q_box", "lost_focus")
    def q_box_lost_focus(self, **event_args):
        self._draw_links()

    @handle("copy_q_button", "click")
    def copy_q_button_click(self, **event_args):
        self._copy(self.q_box.text or "", "Search words copied.")

    @handle("region_dd", "change")
    def region_dd_change(self, **event_args):
        self._save_prefs()

    def _read_prefs(self):
        p = dict(self.p)
        for key, box in (("budget", self.budget_box), ("max_km", self.km_box), ("year_from", self.year_box)):
            v = prefs.number(box.text)
            if v is False:
                state.toast("%s needs to be a number." % key.replace("_", " ").capitalize(), "error")
                return None
            if key == "max_km" and v and self._miles:
                v = int(round(v / 0.621371))
            p[key] = v
        p["place"] = (self.place_box.text or "").strip()
        p["region"] = self.region_dd.selected_value
        return p

    def _save_prefs(self, **event_args):
        p = self._read_prefs()
        if p is None:
            return
        if p != self.p and prefs.save(p):
            self.p = prefs.get()
        self._draw_links()

    @handle("budget_box", "lost_focus")
    def budget_box_lost_focus(self, **event_args):
        self._save_prefs()

    @handle("km_box", "lost_focus")
    def km_box_lost_focus(self, **event_args):
        self._save_prefs()

    @handle("year_box", "lost_focus")
    def year_box_lost_focus(self, **event_args):
        self._save_prefs()

    @handle("place_box", "lost_focus")
    def place_box_lost_focus(self, **event_args):
        self._save_prefs()

    # ---- save / share
    def _copy(self, text, done):
        try:
            window.navigator.clipboard.writeText(text)
            state.toast(done, "ok")
        except Exception:
            alert(text, title="Copy this")

    @handle("share_button", "click")
    def share_button_click(self, **event_args):
        self._copy(str(window.location.href), "Link copied: it opens these exact filters.")

    @handle("save_button", "click")
    def save_button_click(self, **event_args):
        if not state.me():
            router.remember_after(window.location.hash)
            state.toast("Create a free account to save searches.")
            router.go("auth", "signup")
            return
        from ...Dialogs.SaveSearch import SaveSearch
        s = self.summary or {}
        chips = s.get("chips") or []
        summary = "; ".join(chips) if chips else "All models"
        st = dict(s.get("state") or self.explorer.state())
        r = alert(SaveSearch(filters=st, summary=summary, count=s.get("count"), suggestion=(chips[0] if chips else "My search")[:60]),
                  buttons=[], role="app-dialog")
        if r:
            state.toast("Saved. Find it under Searches.", "ok")
