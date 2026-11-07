"""The five cars someone is deciding between. Members: stored on the server (Shortlist.py). Visitors: kept in this
browser (localStorage "cc.picks") and moved into their account when they sign up (merge_guest).

    picks.ids()            car ids in order
    picks.toggle(car_id)   add or take out; when five are already picked, asks which one to swap. Returns True if added.
    picks.load()           fresh list of summaries (members: from the server; visitors: cars_summary)
"""
import json

import anvil.server
from anvil import alert
from anvil.js import window

from . import state

MAX = 5
KEY = "cc.picks"
_p: dict = {"ids": None}


def _guest_ids():
    try:
        v = json.loads(window.localStorage.getItem(KEY) or "[]")
        return [str(x) for x in v][:MAX] if isinstance(v, list) else []
    except Exception:
        return []


def _save_guest(ids):
    try:
        window.localStorage.setItem(KEY, json.dumps(ids[:MAX]))
    except Exception:
        pass


def ids():
    if not state.me():
        return _guest_ids()
    if _p["ids"] is None:
        r = anvil.server.call("get_picks")
        _p["ids"] = [p["id"] for p in r["picks"]]
    return list(_p["ids"])


def set_from(r):
    """Remember the list a server call just returned ({"picks": [...]})."""
    if r and r.get("picks") is not None:
        _p["ids"] = [p["id"] for p in r["picks"]]


def forget():
    _p["ids"] = None


def load():
    """[{id, name, make, model, price, ...}] in order."""
    if state.me():
        r = anvil.server.call("get_picks")
        set_from(r)
        return r["picks"]
    return anvil.server.call("cars_summary", _guest_ids())


def _ask_swap(car_id):
    """Five already picked: which one goes? Returns the id to replace, or None."""
    from .Dialogs.FullPicks import FullPicks
    return alert(FullPicks(cars=load()), buttons=[], role="app-dialog")


def toggle(car_id):
    current = ids()
    if car_id in current:
        if state.me():
            set_from(state.call("pick_remove", car_id))
        else:
            _save_guest([i for i in current if i != car_id])
        state.toast("Taken out of your five.")
        return False
    if len(current) >= MAX:
        old = _ask_swap(car_id)
        if not old:
            return False
        if state.me():
            set_from(state.call("pick_replace", old, car_id))
        else:
            _save_guest([car_id if i == old else i for i in current])
        state.toast("Swapped into your five.", "ok")
        return True
    if state.me():
        r = state.call("pick_add", car_id)
        if r is None:
            return False
        set_from(r)
    else:
        _save_guest(current + [car_id])
    n = len(ids())
    state.toast("Added to your five (%d of %d)." % (n, MAX), "ok")
    return True


def merge_guest():
    """After signing in or up: the browser's picks join the account (up to five), then the browser list is cleared."""
    g = _guest_ids()
    _p["ids"] = None
    if not g or not state.me():
        return
    r = anvil.server.call("picks_merge", g)
    if r and r.get("ok"):
        set_from(r)
        _save_guest([])
