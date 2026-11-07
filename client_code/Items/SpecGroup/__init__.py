from anvil import *

from ._anvil_designer import SpecGroupTemplate
from ... import state


class SpecGroup(SpecGroupTemplate):
    """A group of the spec sheet on #car (Performance, Size & space ...). item = {group, rows}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        state.heading(self.title, 2)
        self.rows_panel.items = self.item["rows"]
