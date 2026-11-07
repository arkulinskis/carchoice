"""Where people sell cars: marketplaces, dealers, auctions and price guides by region. Everyone can read them; admins
edit them (search_url holds {q} for the search words, or stays blank for a Google site: search)."""
import anvil.server
from anvil.tables import app_tables

from . import common as C
from . import Seed

REGIONS = ["US", "Canada", "UK", "Europe", "Baltics", "Australia"]
KINDS = ["Marketplace", "Classifieds", "Dealer", "Online dealer", "Auction", "Price guide"]


def _out(r):
    return {"id": r.get_id(), "name": r["name"], "region": r["region"] or "", "kind": r["kind"] or "",
            "url": r["url"] or "", "search_url": r["search_url"] or "", "notes": r["notes"] or "",
            "sort": r["sort"] or 0, "active": bool(r["active"])}


@anvil.server.callable
def list_marketplaces():
    Seed.ensure_seeded()
    rows = sorted((r for r in app_tables.marketplaces.search() if r["active"]), key=lambda r: (r["sort"] or 0, r["name"]))
    return {"markets": [_out(r) for r in rows], "regions": REGIONS, "kinds": KINDS}


@anvil.server.callable(require_user=True)
def admin_markets():
    C.require_admin()
    rows = sorted(app_tables.marketplaces.search(), key=lambda r: (r["sort"] or 0, r["name"]))
    return {"markets": [_out(r) for r in rows], "regions": REGIONS, "kinds": KINDS}


@anvil.server.callable(require_user=True)
def save_market(data):
    C.require_admin()
    if not isinstance(data, dict):
        return C.fail("That didn't make sense.")
    name = C.text(data.get("name"), 80)
    url = C.text(data.get("url"), 300)
    s_url = C.text(data.get("search_url"), 400)
    if len(name) < 2:
        return C.fail("Give it a name.")
    if not url.startswith(("http://", "https://")):
        return C.fail("The website needs a full address starting with https://.")
    if s_url and (not s_url.startswith(("http://", "https://")) or "{q}" not in s_url):
        return C.fail("The search address must start with https:// and contain {q} where the search words go.")
    values: dict = dict(name=name, url=url, search_url=s_url, notes=C.text(data.get("notes"), 300),
                  region=data.get("region") if data.get("region") in REGIONS else "US",
                  kind=data.get("kind") if data.get("kind") in KINDS else "Marketplace",
                  active=bool(data.get("active", True)))
    row = C.row_by_id(app_tables.marketplaces, data.get("id")) if data.get("id") else None
    if row is None:
        values["sort"] = max([r["sort"] or 0 for r in app_tables.marketplaces.search()] + [0]) + 1
        row = app_tables.marketplaces.add_row(**values)
    else:
        row.update(**values)
    return C.ok(market=_out(row))


@anvil.server.callable(require_user=True)
def delete_market(market_id):
    C.require_admin()
    row = C.row_by_id(app_tables.marketplaces, market_id)
    if row is not None:
        row.delete()
    return C.ok()
