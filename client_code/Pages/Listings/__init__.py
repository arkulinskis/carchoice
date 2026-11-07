import anvil.server
from anvil import *

from ._anvil_designer import ListingsTemplate
from ... import router, state

SORTS = [("Best value first", "value"), ("Newest saved", "new"), ("Lowest price", "price"), ("Lowest mileage", "km")]


class Listings(ListingsTemplate):
    """#listings[/<car id>]: every listing the member saved (their links, kept here instead of in bookmarks), with the
    price check per model. Filter by car, sort, change status, edit, delete."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        state.heading(self.title, 1)
        state.heading(self.empty_title, 2)
        self.car_filter = args[0] if args else ""
        self.sort_dd.items = SORTS
        self.sort_dd.selected_value = "value"
        state.set_control_attr(self.sort_dd, "aria-label", "Sort")
        for ev, fn in (("x-edit", self._edit), ("x-deleted", self._reload), ("x-status", self._redraw)):
            self.list_panel.add_event_handler(ev, fn)
        self._reload()

    def _reload(self, **event_args):
        self.data = anvil.server.call("list_listings")
        cars = self.data["cars"]
        self.car_dd.items = [("All cars", "")] + [(name, cid) for cid, name in cars] + [("Not linked to a car", "-")]
        if self.car_filter and self.car_filter not in [c[0] for c in cars] + ["-"]:
            self.car_filter = ""
        self.car_dd.selected_value = self.car_filter
        state.set_control_attr(self.car_dd, "aria-label", "Car")
        self._redraw()

    def _redraw(self, **event_args):
        items = list(self.data["listings"])
        f = self.car_filter
        if f == "-":
            items = [i for i in items if not i["car_id"]]
        elif f:
            items = [i for i in items if i["car_id"] == f]
        if self.hide_box.checked:
            items = [i for i in items if i["status"] != "Not for me"]
        how = self.sort_dd.selected_value
        if how == "value":
            items.sort(key=lambda i: (i["car_name"] or "~", (i["score"] or {}).get("ratio", 9), -(i["price"] or 0)))
        elif how == "price":
            items.sort(key=lambda i: (i["price"] is None, i["price"] or 0))
        elif how == "km":
            items.sort(key=lambda i: (i["km"] is None, i["km"] or 0))
        statuses = self.data["statuses"]
        self.list_panel.items = [dict(i, statuses=statuses) for i in items]
        n, total = len(items), self.data["total"]
        self.empty.visible = total == 0
        self.sub.text = ("%s%s." % (state.plural(total, "listing"), (", %d shown" % n) if n != total else "")) if total else ""

    @handle("car_dd", "change")
    def car_dd_change(self, **event_args):
        self.car_filter = self.car_dd.selected_value or ""
        if self.car_filter and self.car_filter != "-":
            router.replace("listings", self.car_filter)
        else:
            router.replace("listings")
        self._redraw()

    @handle("sort_dd", "change")
    def sort_dd_change(self, **event_args):
        self._redraw()

    @handle("hide_box", "change")
    def hide_box_change(self, **event_args):
        self._redraw()

    @handle("add_button", "click")
    def add_button_click(self, **event_args):
        from ...Dialogs.AddListing import AddListing
        car = self.car_filter if self.car_filter not in ("", "-") else None
        if alert(AddListing(car_id=car), buttons=[], role="app-dialog", large=True):
            state.toast("Listing saved.", "ok")
            self._reload()

    def _edit(self, item, **event_args):
        from ...Dialogs.AddListing import AddListing
        if alert(AddListing(listing=item), buttons=[], role="app-dialog", large=True):
            state.toast("Saved.", "ok")
            self._reload()
