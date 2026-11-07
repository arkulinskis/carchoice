"""Turn a set of filters (or one car) into searches people can run themselves on marketplaces.

    explore_words(summary)       search words for what Explore shows ("Toyota RAV4" OR ... / "hybrid AWD SUV")
    car_words(name)              one model's search words
    prefs_line(prefs)            "up to $30,000 · up to 80,000 km · 2019 or newer · near Montreal"
    links(words, markets, region, simple)
                                 [{name, kind, notes, url, open_url, how}] for the region's marketplaces: their own
                                 search page when its address is known ({q}), otherwise a Google site: search
"""
from anvil.js import window

from . import fmt

REGIONS = ["US", "Canada", "UK", "Europe", "Baltics", "Australia"]
FUEL_WORD = {"Hybrid": "hybrid", "Plug-in hybrid": "plug-in hybrid", "Electric": "electric", "Diesel": "diesel",
             "Petrol": ""}
BODY_WORD = {"SUV": "SUV", "Sedan": "sedan", "Hatchback": "hatchback", "Wagon": "wagon", "Pickup": "pickup truck",
             "Minivan": "minivan", "Coupe": "coupe", "Convertible": "convertible", "Van": "van"}


def _enc(s):
    return window.encodeURIComponent(s)


def _host(url):
    u = (url or "").split("//")[-1].split("/")[0]
    return u[4:] if u.startswith("www.") else u


def _chosen(summary, key):
    """Values someone filtered on (state.f[key]) if any."""
    f = (summary.get("state") or {}).get("f") or {}
    v = f.get(key)
    return v if isinstance(v, list) else []


def explore_words(summary):
    """-> (words for a Google-style search, simpler words for sites that take plain words, a one-line explanation)"""
    n = summary.get("count") or 0
    names = summary.get("names") or []
    if not n:
        return "", "", "Nothing matches yet: loosen a filter."
    if n <= 6:
        return (" OR ".join('"%s"' % x for x in names[:6]), names[0],
                "Your %d matching models, ready to paste into a search box." % n)
    words = []
    fuels = [FUEL_WORD.get(x, "") for x in _chosen(summary, "fuel")]
    if len(fuels) == 1 and fuels[0]:
        words.append(fuels[0])
    drives = _chosen(summary, "drive")
    if drives and all(d in ("AWD", "4WD") for d in drives):
        words.append("AWD" if "AWD" in drives else "4WD")
    bodies = [BODY_WORD.get(x, x) for x in _chosen(summary, "body")]
    makes = _chosen(summary, "make")
    if len(makes) in (1, 2):
        words = [" or ".join(makes)] + words
    if len(bodies) == 1:
        words.append(bodies[0])
    if not words:
        # no simple words: name the first few models in the current order
        top = names[:4]
        return (" OR ".join('"%s"' % x for x in top), top[0] if top else "",
                "%d models match: these are the first %d in your current order. Narrow further for a sharper search." % (n, len(top)))
    w = " ".join(words)
    return w, w, "%d models match. These words describe them; narrow to six or fewer to search by name." % n


def car_words(name):
    return '"%s"' % name


def prefs_line(prefs):
    parts = []
    cur = prefs.get("currency") or "USD"
    if prefs.get("budget"):
        parts.append("up to " + fmt.money(prefs["budget"], cur))
    if prefs.get("max_km"):
        parts.append("up to " + fmt.km(prefs["max_km"]))
    if prefs.get("year_from"):
        parts.append("%s or newer" % int(prefs["year_from"]))
    if prefs.get("place"):
        parts.append("near " + prefs["place"])
    return " · ".join(parts)


def default_region(prefs):
    if prefs.get("region") in REGIONS:
        return prefs["region"]
    lang = str(window.navigator.language or "")
    zone = ""
    try:
        zone = str(window.Intl.DateTimeFormat().resolvedOptions().timeZone or "")
    except Exception:
        pass
    if lang.endswith("-CA") or zone in ("America/Toronto", "America/Montreal", "America/Vancouver", "America/Edmonton",
                                        "America/Winnipeg", "America/Halifax", "America/Regina"):
        return "Canada"
    if lang.endswith("-GB") or zone == "Europe/London":
        return "UK"
    if zone in ("Europe/Riga", "Europe/Tallinn", "Europe/Vilnius"):
        return "Baltics"
    if zone.startswith("Australia/"):
        return "Australia"
    if zone.startswith("Europe/"):
        return "Europe"
    return "US"


def links(words, markets, region, simple=None):
    out = []
    if not words:
        return out
    for m in markets:
        if m.get("region") != region or m.get("kind") == "Price guide":
            continue
        if m.get("search_url"):
            q = simple or words
            url = m["search_url"].replace("{q}", _enc(q.replace('"', "")))
            how = "Opens its own search"
        else:
            url = "https://www.google.com/search?q=" + _enc("%s site:%s" % (words, _host(m.get("url"))))
            how = "Google search of the site"
        out.append({"name": m["name"], "kind": m.get("kind") or "", "notes": m.get("notes") or "", "url": m.get("url") or "",
                    "open_url": url, "how": how})
    return out


def guides(markets, region):
    return [m for m in markets if m.get("region") == region and m.get("kind") == "Price guide"]
