from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import LandingTemplate
from ... import catalog, state


class Landing(LandingTemplate):
    """#landing, the front page (Persuade): the promise, the live example (Components/HeroDemo), how it works,
    features, where the data comes from, FAQ. Static copy lives in the template. After it shows, the catalogue is
    fetched quietly so Explore opens at once, and the real model count replaces the placeholder."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        if state.me():
            state.set_attr(self.signup_link, "href", "#picks")
            anvil.js.get_dom_node(self.signup_link).textContent = "Your five"
        self._warm = anvil.js.report_exceptions(self._prefetch)

    @handle("", "show")
    def form_show(self, **event_args):
        window.setTimeout(self._warm, 600)

    def _prefetch(self):
        catalog.prefetch()
        n = catalog.count()
        if n:
            self.count_label.text = "%d models in the table" % n
