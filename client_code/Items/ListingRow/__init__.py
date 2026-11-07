from anvil import *

from ._anvil_designer import ListingRowTemplate
from ... import fmt, state

VERDICT_ROLE = {"Good price": "badge-good", "Fair price": "badge-brand", "Pricey": "badge-warn"}


class ListingRow(ListingRowTemplate):
    """One saved listing on #listings. item = a listing from list_listings (+ "statuses"). Edit / Delete raise
    x-edit / x-deleted on the panel; the status saves itself."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        state.set_attr(self.title_link, "rel", "noopener")
        meta = [it["host"]] + [x for x in (it.get("car_name"), it.get("location"), it.get("seller")) if x]
        self.meta.text = " · ".join(meta)
        self.price.text = fmt.money(it["price"], it["currency"]) if it.get("price") else "No price"
        self.price.role = ["ls-amount"] if it.get("price") else ["ls-amount", "faint"]
        yk = [str(it["year"])] if it.get("year") else []
        if it.get("km") is not None:
            yk.append(fmt.km(it["km"]))
        self.yk.text = " · ".join(yk)
        sc = it.get("score")
        if sc:
            self.verdict.text = sc["verdict"]
            self.verdict.role = ["badge", VERDICT_ROLE.get(sc["verdict"], "badge-brand")]
            self.score_note.text = "%d of %d for this model · fair ≈ %s" % (sc["rank"], sc["of"], fmt.money(sc["fair"], it["currency"]))
        else:
            self.verdict.visible = False
            self.score_note.text = ("Add a price and year to compare" if not (it.get("price") and it.get("year"))
                                    else ("Pick the car to compare" if not it.get("car_id") else "Save another listing of this model to compare"))
        self.row.classes["is-out"] = it["status"] in ("Not for me",)
        self.row.classes["is-bought"] = it["status"] == "Bought"
        self.status_dd.items = it.get("statuses") or [it["status"]]
        self.status_dd.selected_value = it["status"]
        state.set_control_attr(self.status_dd, "aria-label", "Status of %s" % it["title"])
        state.set_control_attr(self.edit_button, "aria-label", "Edit %s" % it["title"])
        state.set_control_attr(self.delete_button, "aria-label", "Delete %s" % it["title"])

    @handle("status_dd", "change")
    def status_dd_change(self, **event_args):
        if state.call("set_listing_status", self.item["id"], self.status_dd.selected_value) is not None:
            self.item["status"] = self.status_dd.selected_value
            self.row.classes["is-out"] = self.item["status"] == "Not for me"
            self.row.classes["is-bought"] = self.item["status"] == "Bought"
            state.toast("Marked: %s" % self.item["status"], "ok")
            self.parent.raise_event("x-status")

    @handle("edit_button", "click")
    def edit_button_click(self, **event_args):
        self.parent.raise_event("x-edit", item=self.item)

    @handle("delete_button", "click")
    def delete_button_click(self, **event_args):
        if confirm("The link and your notes on it are deleted.", title="Delete this listing?",
                   buttons=[("Cancel", False), ("Delete", True)], role="app-dialog"):
            if state.call("delete_listing", self.item["id"]) is not None:
                self.parent.raise_event("x-deleted")
