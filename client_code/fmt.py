"""Numbers for people: units (metric or imperial, the same choice as on Explore), money, mileage. Mirrors CC.fmt in
cc-explore.js for the Python pages (car sheet, compare, your five, listings)."""
from anvil.js import window

IMP = {"km": ("mi", 0.621371), "mm": ("in", 0.0393701), "kg": ("lb", 2.20462), "litres": ("cu ft", 0.0353147),
       "Nm": ("lb-ft", 0.737562), "km/h": ("mph", 0.621371)}
SYMBOL = {"USD": "$", "CAD": "CA$", "EUR": "€", "GBP": "£", "AUD": "A$"}


def units():
    try:
        return "imperial" if window.localStorage.getItem("cc.units") == "imperial" else "metric"
    except Exception:
        return "metric"


def set_units(u):
    try:
        window.localStorage.setItem("cc.units", u)
    except Exception:
        pass


def _group(n, dec=0):
    """12345.6 -> '12,346' (thousands separators by hand: the browser's Python has no ',' format)."""
    neg = n < 0
    whole, _, frac = (("%." + str(dec) + "f") % abs(n)).partition(".")
    out = ""
    while len(whole) > 3:
        out = "," + whole[-3:] + out
        whole = whole[:-3]
    return ("-" if neg else "") + whole + out + ("." + frac if frac else "")


def unit_label(unit, u=None):
    u = u or units()
    if u == "imperial":
        if unit in IMP:
            return IMP[unit][0]
        if unit == "L/100km":
            return "mpg"
    if unit == "litres":
        return "L"
    return unit or ""


def value(kind, unit, dec, v, u=None):
    """One spec as text: '31,900' with its unit ('$31,900', '226 hp', '5.9 L/100km' or '40 mpg')."""
    if v is None or v == "" or v == []:
        return "–"
    if kind == "bool":
        return "Yes" if v else "No"
    if isinstance(v, list):
        return " / ".join(str(x) for x in v)
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        u = u or units()
        x, d = v, dec or 0
        if u == "imperial" and unit in IMP:
            x = v * IMP[unit][1]
            d = 1 if IMP[unit][0] == "cu ft" else 0
        elif u == "imperial" and unit == "L/100km":
            x, d = (235.215 / v if v else 0), 0
        if not unit and isinstance(x, int) and 1800 <= x <= 2200:
            return str(x)  # a year
        if unit == "USD":
            return "$" + _group(x)
        lab = unit_label(unit, u)
        return _group(x, d) + (" " + lab if lab else "")
    return str(v)


def money(v, currency="USD"):
    if v is None or v == "":
        return "–"
    return SYMBOL.get(currency or "USD", (currency or "") + " ") + _group(v)


def km(v, u=None):
    if v is None or v == "":
        return ""
    if (u or units()) == "imperial":
        return _group(v * 0.621371) + " mi"
    return _group(v) + " km"


def range_line(car):
    """'5.9 L/100km' or '512 km range' for summaries."""
    parts = []
    if car.get("l100"):
        parts.append(value("number", "L/100km", 1, car["l100"]))
    if car.get("ev_range"):
        parts.append(value("number", "km", 0, car["ev_range"]) + " electric")
    return " · ".join(parts)


def facts(car):
    """One line of key facts for cards: price · power · fuel · seats."""
    parts = []
    if car.get("price"):
        parts.append("from " + value("number", "USD", 0, car["price"]))
    if car.get("hp"):
        parts.append("%s hp" % car["hp"])
    if car.get("fuel"):
        parts.append(" / ".join(car["fuel"]))
    if car.get("seats"):
        parts.append("%s seats" % car["seats"])
    return " · ".join(parts)
