from anvil import *

from ._anvil_designer import SwapRowTemplate
from ... import fmt, state


class SwapRow(SwapRowTemplate):
    """A car in the "Your five is full" dialog. Swap out raises x-swap on the panel."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.facts.text = fmt.facts(self.item)
        state.set_control_attr(self.swap_button, "aria-label", "Swap out the %s" % self.item["name"])

    @handle("swap_button", "click")
    def swap_button_click(self, **event_args):
        self.parent.raise_event("x-swap", car_id=self.item["id"])
