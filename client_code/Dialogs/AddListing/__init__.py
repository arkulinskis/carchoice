import anvil.server
from anvil import *

from ._anvil_designer import AddListingTemplate
from ... import fmt, state

STATUSES = ["Watching", "Contacted", "Seen it", "Not for me", "Bought"]
CURRENCIES = ["USD", "CAD", "EUR", "GBP", "AUD"]


class AddListing(AddListingTemplate):
    """Save (or edit: listing=) a listing someone found. car_id preselects the car. Closes with the saved listing,
    or None. Mileage is typed in the unit the person uses (km or miles, from the Explore units choice)."""

    def __init__(self, listing=None, car_id=None, currency=None, **properties):
        super().__init__(**properties)
        self.listing = listing or {}
        self.miles = fmt.units() == "imperial"
        if self.miles:
            self.km_box.placeholder = "28000"
        state.set_control_attr(self.km_box, "aria-label", "Mileage in miles" if self.miles else "Mileage in kilometres")
        choices = anvil.server.call("pick_choices")
        items = [("Not linked to a car", "")]
        items += [("★ " + name, cid) for name, cid in choices["mine"]]
        items += [(name, cid) for name, cid in choices["all"]]
        self.car_dd.items = items
        self.currency_dd.items = CURRENCIES
        self.status_dd.items = STATUSES
        li = self.listing
        self.car_dd.selected_value = li.get("car_id") or car_id or ""
        self.currency_dd.selected_value = li.get("currency") or currency or "USD"
        self.status_dd.selected_value = li.get("status") or "Watching"
        self.url_box.text = li.get("url") or ""
        title = str(li.get("title") or "")
        self.title_box.text = title if title != li.get("host") else ""
        self.price_box.text = str(li["price"]) if li.get("price") is not None else ""
        self.year_box.text = str(li["year"]) if li.get("year") else ""
        if li.get("km") is not None:
            self.km_box.text = str(int(round(li["km"] * 0.621371))) if self.miles else str(li["km"])
        self.location_box.text = li.get("location") or ""
        self.seller_box.text = li.get("seller") or ""
        self.notes_box.text = li.get("notes") or ""
        if li.get("id"):
            self.heading.text = "Edit the listing"
        state.heading(self.heading, 2)
        state.set_control_attr(self.url_box, "type", "url")
        state.set_control_attr(self.url_box, "inputmode", "url")
        for box in (self.price_box, self.year_box, self.km_box):
            state.set_control_attr(box, "inputmode", "numeric")
        if self.miles:
            self.dom_nodes["km_cap"].textContent = "Mileage (mi)"

    @handle("", "show")
    def form_show(self, **event_args):
        if not self.url_box.text:
            self.url_box.focus()

    @handle("cancel_button", "click")
    def cancel_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)

    def _say(self, text):
        self.message.text, self.message.visible = text, True

    @handle("save_button", "click")
    def save_button_click(self, **event_args):
        url = (self.url_box.text or "").strip()
        if not url.lower().startswith(("http://", "https://")):
            self._say("Paste the full link to the listing (it starts with https://).")
            state.focus(self.url_box)
            return
        km = (self.km_box.text or "").replace(",", "").replace(" ", "")
        if km and self.miles:
            try:
                km = str(int(round(float(km) / 0.621371)))
            except ValueError:
                self._say("Mileage needs to be a number.")
                return
        data = {"id": self.listing.get("id"), "url": url, "title": self.title_box.text, "car_id": self.car_dd.selected_value,
                "price": (self.price_box.text or "").replace("$", "").replace("€", "").replace("£", ""), "currency": self.currency_dd.selected_value,
                "year": self.year_box.text, "km": km, "location": self.location_box.text, "seller": self.seller_box.text,
                "status": self.status_dd.selected_value, "notes": self.notes_box.text}
        self.save_button.enabled = False
        try:
            r = anvil.server.call("save_listing", data)
        finally:
            self.save_button.enabled = True
        if not r.get("ok"):
            self._say(r.get("error") or "That didn't work.")
            return
        self.raise_event("x-close-alert", value=r["listing"])
