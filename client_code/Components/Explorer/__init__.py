import json

from anvil import *
import anvil.js
from anvil.js import window

from ._anvil_designer import ExplorerTemplate


class Explorer(ExplorerTemplate):
    """The Explore engine (theme/assets/cc-explore.js: filter rail + data table) as a component.

    start(catalog_json, state, picked_ids) draws it; it raises x_change (summary = a dict: state, count, names,
    makes ... as the engine reports them), x_pick (car_id: the star was pressed) and x_open (car_id: a model's name).
    set_picked(ids) re-marks the stars. The engine is destroyed when the page goes away."""

    def __init__(self, **properties):
        self._api = None
        self._change = anvil.js.report_exceptions(self._on_change)
        self._pick = anvil.js.report_exceptions(self._on_pick)
        self._open = anvil.js.report_exceptions(self._on_open)
        super().__init__(**properties)

    def start(self, catalog_json, state=None, picked=()):
        self.stop()
        self._api = window.CC.mountExplorer(self.dom_nodes["host"], catalog_json, json.dumps(state or {}),
                                            json.dumps(list(picked)), self._change, self._pick, self._open)

    def stop(self):
        if self._api is not None:
            self._api.destroy()
            self._api = None

    def set_picked(self, ids):
        if self._api is not None:
            self._api.setPicked(window.JSON.parse(json.dumps(list(ids))))

    def set_state(self, state):
        if self._api is not None:
            self._api.setState(window.JSON.parse(json.dumps(state or {})))

    def state(self):
        return json.loads(self._api.getState()) if self._api is not None else {}

    def _on_change(self, payload):
        self.raise_event("x_change", summary=json.loads(payload))

    def _on_pick(self, car_id):
        self.raise_event("x_pick", car_id=str(car_id))

    def _on_open(self, car_id):
        self.raise_event("x_open", car_id=str(car_id))

    @handle("", "hide")
    def form_hide(self, **event_args):
        self.stop()
