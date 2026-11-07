"""Search preferences (budget, mileage, year, place, region): what goes into the marketplace searches.
Members keep them on their account (users.prefs); visitors in this browser."""
import json

import anvil.server
from anvil.js import window

from . import picks, state

KEY = "cc.prefs"
_c: dict = {"prefs": None}


def get():
    if _c["prefs"] is not None:
        return dict(_c["prefs"])
    p: dict = {}
    if state.me():
        r = anvil.server.call("get_picks")
        picks.set_from(r)
        p = r.get("prefs") or {}
    else:
        try:
            v = json.loads(window.localStorage.getItem(KEY) or "{}")
            p = v if isinstance(v, dict) else {}
        except Exception:
            p = {}
    _c["prefs"] = p
    return dict(p)


def save(p):
    """Returns True when saved (a toast says what was wrong otherwise)."""
    clean = {k: v for k, v in p.items() if v not in (None, "")}
    if state.me():
        r = state.call("save_prefs", clean)
        if r is None:
            return False
        clean = r["prefs"]
    else:
        try:
            window.localStorage.setItem(KEY, json.dumps(clean))
        except Exception:
            pass
    _c["prefs"] = clean
    return True


def forget():
    _c["prefs"] = None


def number(text):
    """'30 000' / '$30,000' -> 30000; '' -> None; junk -> False."""
    s = "".join(ch for ch in str(text or "") if ch.isdigit() or ch == ".")
    if not str(text or "").strip():
        return None
    try:
        v = float(s)
    except ValueError:
        return False
    return int(v) if v == int(v) else v
