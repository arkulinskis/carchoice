from anvil import *
from anvil.js import window

from ._anvil_designer import HeroDemoTemplate


class HeroDemo(HeroDemoTemplate):
    """The landing page's live example (theme/assets/cc-hero.js): filters tighten, rows fade, five cars drop into the
    tray. The template holds a still copy, so the hero reads even if the script never runs."""

    def __init__(self, **properties):
        self._api = None
        super().__init__(**properties)

    @handle("", "show")
    def form_show(self, **event_args):
        if self._api is None and window.get("CC") and window.CC.get("hero"):
            self._api = window.CC.hero(self.dom_nodes["host"])

    @handle("", "hide")
    def form_hide(self, **event_args):
        if self._api is not None:
            self._api.destroy()
            self._api = None
