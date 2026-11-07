import json

from anvil import *
from anvil.js import window

from ._anvil_designer import SearchRowTemplate
from ... import router, state


class SearchRow(SearchRowTemplate):
    """One saved search on #searches. item = from list_searches. Open goes to Explore with its filters; Rename /
    Delete raise x-rename / x-deleted on the panel."""

    def __init__(self, **properties):
        super().__init__(**properties)
        it = self.item
        self.summary.text = it.get("summary") or "All models (no filters)"
        bits = ["Saved " + state.short_date(it.get("created"))]
        if it.get("count") is not None:
            bits.append(state.plural(it["count"], "match", "matches") + " then")
        self.meta.text = " · ".join(bits)
        self._href = router.href("explore", window.CC.encodeState(window.JSON.parse(json.dumps(it.get("filters") or {}))))
        state.set_attr(self.name_link, "href", self._href)
        for b, verb in ((self.rename_button, "Rename"), (self.delete_button, "Delete"), (self.open_button, "Open"),
                        (self.copy_button, "Copy the link to")):
            state.set_control_attr(b, "aria-label", "%s %s" % (verb, it["name"]))

    @handle("open_button", "click")
    def open_button_click(self, **event_args):
        window.location.hash = self._href

    @handle("copy_button", "click")
    def copy_button_click(self, **event_args):
        url = str(window.location.href).split("#")[0] + self._href
        try:
            window.navigator.clipboard.writeText(url)
            state.toast("Link copied. Anyone with it sees these filters.", "ok")
        except Exception:
            alert(url, title="Copy this link")

    @handle("rename_button", "click")
    def rename_button_click(self, **event_args):
        self.parent.raise_event("x-rename", item=self.item)

    @handle("delete_button", "click")
    def delete_button_click(self, **event_args):
        if confirm("The search is deleted (the cars aren't affected).", title="Delete \"%s\"?" % self.item["name"],
                   buttons=[("Cancel", False), ("Delete", True)], role="app-dialog"):
            if state.call("delete_search", self.item["id"]) is not None:
                self.parent.raise_event("x-deleted")
