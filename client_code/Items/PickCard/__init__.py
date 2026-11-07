from anvil import *

from ._anvil_designer import PickCardTemplate
from ... import fmt, router, state

VERDICT_ROLE = {"Good price": "badge-good", "Fair price": "badge-brand", "Pricey": "badge-warn"}


class PickCard(PickCardTemplate):
    """One of the member's five on #picks. item = a pick from get_picks (rank, name, note, listings: {count, best})
    or {empty: True, rank}. Buttons raise x-find / x-add / x-move / x-remove on the panel; the note saves itself."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        empty = bool(it.get("empty"))
        self.rank.text = str(it["rank"])
        self.card.classes["is-empty"] = empty
        self.full.visible = not empty
        self.empty.visible = empty
        if empty:
            return
        self.make.text, self.model.text = it["make"], it["model"]
        state.set_attr(self.name_link, "href", router.href("car", it["id"]))
        self.facts.text = fmt.facts(it)
        self.eff.text = fmt.range_line(it)
        self.eff.visible = bool(self.eff.text)
        self.note_box.text = it.get("note") or ""
        state.set_control_attr(self.note_box, "aria-label", "Your notes on the %s" % it["name"])
        lst = it.get("listings") or {}
        n = lst.get("count") or 0
        best = lst.get("best")
        self.listings_text.text = state.plural(n, "saved listing") if n else "No listings saved yet"
        state.set_attr(self.listings_link, "href", router.href("listings", it["id"]))
        if best:
            self.best_badge.text = "Best: %s, %s" % (fmt.money(best["price"], best["currency"]), best["verdict"].lower())
            self.best_badge.role = ["badge", VERDICT_ROLE.get(best["verdict"], "badge-brand")]
        self.best_badge.visible = bool(best)
        self.up_button.enabled = it["rank"] > 1
        self.down_button.enabled = it["rank"] < it.get("total", 5)
        for b, verb in ((self.up_button, "Move up"), (self.down_button, "Move down"), (self.remove_button, "Remove")):
            state.set_control_attr(b, "aria-label", "%s: %s" % (verb, it["name"]))
            state.set_control_attr(b, "data-key", "%s-%s" % (verb, it["id"]))
        self._note = self.note_box.text

    @handle("note_box", "lost_focus")
    def note_box_lost_focus(self, **event_args):
        text = self.note_box.text or ""
        if text != self._note and state.call("pick_note", self.item["id"], text) is not None:
            self._note = text
            state.toast("Note saved.", "ok")

    @handle("find_button", "click")
    def find_button_click(self, **event_args):
        self.parent.raise_event("x-find", item=self.item)

    @handle("add_button", "click")
    def add_button_click(self, **event_args):
        self.parent.raise_event("x-add", item=self.item)

    @handle("up_button", "click")
    def up_button_click(self, **event_args):
        self.parent.raise_event("x-move", car_id=self.item["id"], delta=-1, key="Move up-" + self.item["id"])

    @handle("down_button", "click")
    def down_button_click(self, **event_args):
        self.parent.raise_event("x-move", car_id=self.item["id"], delta=1, key="Move down-" + self.item["id"])

    @handle("remove_button", "click")
    def remove_button_click(self, **event_args):
        self.parent.raise_event("x-remove", item=self.item)
