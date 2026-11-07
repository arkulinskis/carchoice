import anvil.server
from anvil import *
from anvil.js import window

from ._anvil_designer import CarTemplate
from ... import fmt, picks, router, state


class Car(CarTemplate):
    """#car/<id>: one model's spec sheet. Key figures, every spec grouped (with where it ranks among all models),
    the brand, similar models, and buttons to keep it in your five or find it for sale."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        self.car_id = args[0] if args else ""
        state.heading(self.sim_title, 2)
        state.heading(self.brand_title, 2)
        r = anvil.server.call("get_car", self.car_id) if self.car_id else None
        found = bool(r and r.get("ok"))
        self.missing.visible = not found
        self.sheet.visible = found
        if not r or not r.get("ok"):
            return
        self.r = r
        car = r["car"]
        self.car = car
        window.document.title = car["name"] + " · CarChoice"
        self.make.text, self.model.text = car["make"], car["model"]
        state.heading(self.model, 1)
        state.set_attr(self.model, "aria-label", car["name"])
        s = car["specs"]
        tags = [s.get("body"), s.get("size"), " / ".join(s.get("fuel") or []), " / ".join(s.get("drive") or [])]
        if s.get("status") == "Discontinued":
            tags.append("discontinued: buy used")
        self.tags.text = " · ".join(t for t in tags if t)
        self.price.text = fmt.value("number", "USD", 0, s.get("price")) if s.get("price") else "Price not listed"
        self.price_note.visible = bool(s.get("price"))
        n = r.get("pickers") or 0
        self.pickers.text = ("In %s." % state.plural(n, "person's five", "people's fives")) if n else ""
        self.similar_panel.items = r["similar"]
        self.source.text = "Source: %s%s. Figures are for a typical trim and approximate: check the maker's spec sheet before buying." % (
            car["source"] or "CarChoice", (" · " + car["notes"]) if car.get("notes") else "")
        b = r.get("brand")
        self.brand_box.visible = bool(b)
        if b:
            self.brand_title.text = "About %s" % b["name"]
            self.brand_line.text = " · ".join(str(x) for x in [b["country"], b["group"], ("founded %s" % b["founded"]) if b["founded"] else ""] if x)
            self.warranty.text = ("US warranty: %s years basic, %s years powertrain." % (b["warranty"], b["pt_warranty"])) if b.get("warranty") else ""
            self.warranty.visible = bool(b.get("warranty"))
            self.brand_site.url = b["website"]
            self.brand_site.visible = bool(b["website"])
            state.set_attr(self.brand_site, "rel", "noopener")
        self._draw()
        self._draw_pick()

    def _draw(self):
        s = self.car["specs"]
        u = fmt.units()
        keys = [("hp", "Power", "number", "hp", 0), ("zero100", "0-100 km/h", "number", "s", 1)]
        if s.get("ev_range") and "Electric" in (s.get("fuel") or []):
            keys.append(("ev_range", "Electric range", "number", "km", 0))
        else:
            keys.append(("l100", "Fuel use", "number", "L/100km", 1))
        keys += [("seats", "Seats", "number", "", 0), ("cargo", "Cargo space", "number", "litres", 0)]
        boxes = [(self.k1, self.k1_v, self.k1_l), (self.k2, self.k2_v, self.k2_l), (self.k3, self.k3_v, self.k3_l),
                 (self.k4, self.k4_v, self.k4_l), (self.k5, self.k5_v, self.k5_l)]
        for (box, v, lab), (k, label, kind, unit, dec) in zip(boxes, keys):
            v.text = fmt.value(kind, unit, dec, s.get(k), u)
            lab.text = label
        self.groups_panel.items = self.r["car"]["groups"]
        self.u_metric.classes["on"] = u == "metric"
        self.u_imperial.classes["on"] = u == "imperial"

    def units_click(self, event):
        fmt.set_units(str(event.currentTarget.getAttribute("data-u")))
        self._draw()

    def _draw_pick(self):
        on = self.car_id in picks.ids()
        self.pick_button.text = "In your five" if on else "Add to your five"
        self.pick_button.role = ["btn", "ic-check"] if on else ["btn", "btn-primary", "ic-star"]
        state.set_control_attr(self.pick_button, "aria-pressed", "true" if on else "false")

    @handle("pick_button", "click")
    def pick_button_click(self, **event_args):
        picks.toggle(self.car_id)
        self._draw_pick()

    @handle("find_button", "click")
    def find_button_click(self, **event_args):
        from ...Dialogs.FindListings import FindListings
        if alert(FindListings(car=self.car), buttons=[], role="app-dialog", large=True) == "add":
            if not state.me():
                router.remember_after(window.location.hash)
                state.toast("Create a free account to save the listings you find.")
                router.go("auth", "signup")
                return
            from ...Dialogs.AddListing import AddListing
            if alert(AddListing(car_id=self.car_id), buttons=[], role="app-dialog", large=True):
                state.toast("Listing saved.", "ok")
