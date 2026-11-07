"""The car catalogue in the browser: one JSON string, cached in localStorage by version, handed straight to the
JavaScript engine (cc-explore.js). The browser's Python never unpacks it (that would be slow).

    catalog.text()      the JSON text (one server call; it answers "same" when the cached copy is current)
    catalog.prefetch()  warm the cache quietly (the landing page does this, so Explore opens at once)
"""
import anvil.server
from anvil.js import window

_c = {"v": None, "json": None}
KEY_V, KEY_J = "cc.catalog.v", "cc.catalog.json"


def _get(key):
    try:
        return window.localStorage.getItem(key)
    except Exception:
        return None


def _put(v, text):
    try:
        window.localStorage.setItem(KEY_J, text)
        window.localStorage.setItem(KEY_V, v)
    except Exception:
        pass  # private window or full storage: the in-memory copy still works


def _apply(r):
    if r.get("same"):
        _c["v"], _c["json"] = r["v"], _get(KEY_J)
    else:
        _c["v"], _c["json"] = r["v"], r["json"]
        _put(r["v"], r["json"])


def text():
    if _c["json"]:
        return _c["json"]
    have = _get(KEY_V) if _get(KEY_J) else None
    _apply(anvil.server.call("get_catalog", have))
    if not _c["json"]:  # the cache vanished between the two reads
        _apply(anvil.server.call("get_catalog", None))
    return _c["json"]


def prefetch():
    if _c["json"]:
        return
    have = _get(KEY_V) if _get(KEY_J) else None
    try:
        r = anvil.server.call_s("get_catalog", have)
    except Exception:
        return
    _apply(r)


def forget():
    """After an admin changed the data: fetch it again next time."""
    _c["v"], _c["json"] = None, None
    try:
        window.localStorage.removeItem(KEY_V)
    except Exception:
        pass


def count():
    """How many models the cached catalogue holds (counted in JavaScript, which reads the JSON quickly)."""
    if not _c["json"]:
        return 0
    try:
        return int(window.JSON.parse(_c["json"]).cars.length)
    except Exception:
        return 0
