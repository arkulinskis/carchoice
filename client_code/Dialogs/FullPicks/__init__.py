from anvil import *

from ._anvil_designer import FullPicksTemplate
from ... import state


class FullPicks(FullPicksTemplate):
    """Five cars are already picked: which one makes room? cars = the current five (summaries).
    Closes with the id to swap out, or None."""

    def __init__(self, cars=(), **properties):
        super().__init__(**properties)
        state.heading(self.heading, 2)
        self.cars_panel.items = list(cars)
        self.cars_panel.add_event_handler("x-swap", self._swap)

    def _swap(self, car_id, **event_args):
        self.raise_event("x-close-alert", value=car_id)

    @handle("cancel_button", "click")
    def cancel_button_click(self, **event_args):
        self.raise_event("x-close-alert", value=None)
