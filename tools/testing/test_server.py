"""Server tests against the strict mock of Anvil (tools/testing/mock).

    python tools/testing/test_server.py          -> prints ALL OK, or the first failure

call(name, ...) runs a server function the way the browser does: by name, with require_user enforced,
and the reply must be JSON (a datetime or a row in a reply fails here, like it would break the page).
Add tests for every new server function: the happy path, bad input, and someone who isn't allowed.
"""
import datetime as dt
import importlib
import json
import os
import pathlib
import shutil
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
_tmp = pathlib.Path(tempfile.mkdtemp())
shutil.copytree(PROJECT / "server_code", _tmp / "app")
(_tmp / "app" / "__init__.py").write_text("")
os.environ["ANVIL_APP_YAML"] = str(PROJECT / "anvil.yaml")  # the mock's tables follow the app's own schema
sys.path[:0] = [str(HERE / "mock"), str(_tmp)]
import anvil.server  # noqa: E402
import anvil.users  # noqa: E402
from anvil.tables import app_tables as T  # noqa: E402

M = {p.stem: importlib.import_module("app." + p.stem) for p in sorted((PROJECT / "server_code").glob("*.py"))}
now = dt.datetime.now(dt.timezone.utc)


def call(name, *args):
    r = anvil.server.call(name, *args)
    json.dumps(r)  # strict: must be JSON-able
    return r


def as_user(row):
    anvil.users.CURRENT[0] = row
    anvil.server.session.use(row.get_id() if row is not None else None)


def denied(name, *args):
    try:
        call(name, *args)
    except anvil.server.PermissionDenied:
        return True
    return False


def ok(r, msg=""):
    assert isinstance(r, dict) and r.get("ok"), (msg, r)
    return r


def bad(r, msg=""):
    assert isinstance(r, dict) and r.get("ok") is False and r.get("error"), (msg, r)
    return r


def person(email, name=None, **kw):
    return T.users.add_row(email=email, enabled=True, signed_up=now, display_name=name, **kw)


# ---------------------------------------------------------------------------------- accounts
admin = person("arkulinskis@gmail.com", "The Admin")
ana = person("ana@example.com", "Ana")
bob = person("bob@example.com")

as_user(None)
assert call("get_me") is None
assert denied("update_profile", "X")
as_user(admin)
assert call("get_me")["is_admin"] is True, "ADMIN_EMAILS become admins on first sign-in"
as_user(ana)
me = call("get_me")
assert me["name"] == "Ana" and me["is_admin"] is False
assert ana["last_seen"] is not None
as_user(bob)
assert call("get_me")["name"] == "Bob", "a name comes from the email when none is set"
bad(call("update_profile", " x "))
assert ok(call("update_profile", "  Bob   Stone "))["me"]["name"] == "Bob Stone"

# ---------------------------------------------------------------------------------- feedback
as_user(None)
bad(call("submit_feedback", "bug", "hi"))
ok(call("submit_feedback", "bug", "The button is broken", "guest@example.com", {"page": "#home", "evil": "x" * 9999}))
fb = T.feedback.search()[0]
assert fb["name"] == "Guest" and fb["email"] == "guest@example.com" and "evil" not in fb["context"] and fb["status"] == "new"
for i in range(4):
    ok(call("submit_feedback", "idea", "Idea number %d" % i))
bad(call("submit_feedback", "idea", "One too many this hour"), "rate limit")
as_user(ana)
ok(call("submit_feedback", "nonsense-kind", "Signed-in feedback"))
assert T.feedback.get(message="Signed-in feedback")["kind"] == "other"
assert denied("list_feedback")
as_user(admin)
lst = call("list_feedback")
assert lst["counts"]["new"] == 6 and len(lst["items"]) == 6
fid = lst["items"][0]["id"]
ok(call("set_feedback_status", fid, "done", "Fixed it"))
assert call("list_feedback", "done")["items"][0]["note"] == "Fixed it"
bad(call("set_feedback_status", fid, "weird"))
bad(call("set_feedback_status", "nope", "done"))
ok(call("delete_feedback", fid))
assert len(call("list_feedback")["items"]) == 5

# ---------------------------------------------------------------------------------- admin
as_user(ana)
for fn, args in [("admin_overview", ()), ("list_users", ()), ("set_admin", (bob.get_id(), True)), ("demo_load", ()), ("demo_remove", ())]:
    assert denied(fn, *args), fn
as_user(admin)
ov = call("admin_overview")
assert ov["users"] == 3 and ov["admins"] == 1 and ov["feedback_new"] == 5
assert len(call("list_users")["users"]) == 3 and len(call("list_users", "bob")["users"]) == 1
ok(call("set_admin", bob.get_id(), True))
assert bob["is_admin"] is True
bad(call("set_admin", admin.get_id(), False), "can't remove your own admin")
ok(call("set_enabled", bob.get_id(), False))
assert bob["enabled"] is False
bad(call("set_enabled", admin.get_id(), False))
ok(call("set_enabled", bob.get_id(), True))
ok(call("set_admin", bob.get_id(), False))
assert bob["is_admin"] is False

# ---------------------------------------------------------------------------------- catalogue: seed, import, demo
as_user(None)
cat = call("get_catalog")
data = json.loads(cat["json"])
n_cars = len(data["cars"])
assert n_cars >= 250, "starter set loads on first visit (%d cars)" % n_cars
imp0 = T.imports.search()[0]
assert imp0["kind"] == "seed" and not imp0["notes"], "the starter set imports without problems: %r" % imp0["notes"]
assert call("get_catalog", cat["v"]) == {"v": cat["v"], "same": True}, "cached version answers 'same'"
keys = {f["key"] for f in data["fields"]}
assert len([f for f in data["fields"] if f["filter"]]) >= 30, "at least 30 filters"
rav4 = T.cars.get(slug="toyota-rav4")
s = rav4["specs"]
assert s["fuel"] == ["Hybrid", "Plug-in hybrid"] and s["origin"] == "Japan" and s["warranty"] == 3 and s["carplay"] is True
assert s["regions"] == ["North America", "Europe", "UK", "Australia", "Asia"] and s["status"] == "On sale"
assert T.cars.get(slug="mitsubishi-mirage")["specs"]["status"] == "Discontinued"
assert T.cars.get(slug="citroen-c3")["make"] == "Citroën", "makes match brands ignoring accents"
assert T.cars.get(slug="honda-civic")["specs"]["manual"] is True, "a manual gearbox sets the manual feature"
assert T.cars.get(slug="kia-telluride")["specs"]["row3"] is True
for c in data["cars"]:
    for k in c["s"]:
        assert k in keys, "every spec has a field: %s" % k
assert M["DemoData"].state() == "loaded" and T.picks.search(is_demo=True)
pop = call("popular_picks")
assert pop[0]["name"] == "Toyota RAV4" and pop[0]["count"] >= 4 and "email" not in json.dumps(pop)

car = call("get_car", rav4.get_id())
ok(car)
assert car["car"]["name"] == "Toyota RAV4" and car["brand"]["country"] == "Japan" and len(car["similar"]) == 6
grp = {g["group"]: g for g in car["car"]["groups"]}
price = [r for r in grp["Price & ownership"]["rows"] if r["key"] == "price"][0]
assert 0 <= price["pct"] <= 100 and car["picked"] is False
bad(call("get_car", "nope"))
cmp_ = call("compare_cars", [rav4.get_id(), T.cars.get(slug="honda-cr-v").get_id(), "junk"])
assert len(cmp_["cars"]) == 2 and any(r["key"] == "price" and r["best"] for r in cmp_["rows"])
assert len(call("cars_summary", [rav4.get_id(), "junk"])) == 1
br = call("list_brands")
assert any(b["name"] == "Toyota" and b["models"] >= 15 for b in br["brands"]) and "Japan" in br["countries"]
assert any(b["models"] == 0 for b in br["brands"]), "brands with no models yet are listed too"
mk = call("list_marketplaces")
assert len(mk["markets"]) >= 30 and "Canada" in mk["regions"]

# ---------------------------------------------------------------------------------- the five (shortlist)
assert denied("get_picks") and denied("pick_add", rav4.get_id())
as_user(ana)
assert ok(call("get_picks"))["picks"] == []
ids = [T.cars.get(slug=x).get_id() for x in ["toyota-rav4", "honda-cr-v", "mazda-cx-5", "kia-sportage", "hyundai-tucson", "subaru-forester"]]
for i in ids[:5]:
    ok(call("pick_add", i))
r = call("pick_add", ids[5])
assert r.get("full") and r["ok"] is False, "six is too many"
ok(call("pick_add", ids[0]))  # already in: fine
assert [p["rank"] for p in call("get_picks")["picks"]] == [1, 2, 3, 4, 5]
r = ok(call("pick_move", ids[2], -1))
assert r["picks"][1]["id"] == ids[2]
bad(call("pick_move", ids[5], 1))
ok(call("pick_note", ids[0], "Test drive Saturday"))
assert call("get_picks")["picks"][0]["note"] == "Test drive Saturday"
r = ok(call("pick_replace", ids[4], ids[5]))
assert ids[5] in [p["id"] for p in r["picks"]] and ids[4] not in [p["id"] for p in r["picks"]]
r = ok(call("pick_remove", ids[5]))
assert len(r["picks"]) == 4
as_user(None)
assert call("get_car", rav4.get_id())["pickers"] >= 5
as_user(bob)
r = ok(call("picks_merge", ids[:2] + ["junk"]))
assert len(r["picks"]) == 2
bad(call("save_prefs", {"budget": "lots"}))
ok(call("save_prefs", {"budget": "30000", "max_km": 80000, "place": "Montreal", "evil": "x"}))
assert call("get_picks")["prefs"] == {"budget": 30000, "max_km": 80000, "place": "Montreal"}

# ---------------------------------------------------------------------------------- saved searches
as_user(None)
assert denied("list_searches")
as_user(ana)
bad(call("save_search", "x", {}))
bad(call("save_search", "Hybrid SUVs", "not a dict"))
srch = ok(call("save_search", "Hybrid SUVs under 35k", {"f": {"body": ["SUV"], "price": [None, 35000]}}, "SUV, under $35,000", 41))["search"]
assert srch["count"] == 41
assert ok(call("rename_search", srch["id"], "Family hybrids"))["search"]["name"] == "Family hybrids"
as_user(bob)
bad(call("rename_search", srch["id"], "Mine now"))
ok(call("delete_search", srch["id"]))  # not his: quietly nothing
as_user(ana)
assert len(call("list_searches")["searches"]) == 1
ok(call("delete_search", srch["id"]))
assert call("list_searches")["searches"] == []

# ---------------------------------------------------------------------------------- saved listings + the price check
as_user(None)
assert denied("list_listings")
as_user(ana)
bad(call("save_listing", {"url": "autotrader.com/123"}), "needs a full link")
bad(call("save_listing", {"url": "https://www.autotrader.com/a", "price": "cheap"}))
bad(call("save_listing", {"url": "https://www.autotrader.com/a", "year": 1700}))
L = []
for price, year, km in [(30000, 2022, 40000), (26000, 2022, 42000), (31000, 2021, 30000), (35000, 2023, 20000)]:
    L.append(ok(call("save_listing", {"url": "https://www.autotrader.com/cars/%d" % price, "price": price, "year": year,
                                     "km": km, "currency": "USD", "car_id": rav4.get_id(), "location": "Laval"}))["listing"])
ok(call("save_listing", {"url": "https://example.com/very/long/" + "x" * 300, "title": "A" * 400}))
lst = call("list_listings")
assert lst["total"] == 5 and lst["cars"][0][1] == "Toyota RAV4"
cheap = [x for x in lst["listings"] if x["price"] == 26000][0]
assert cheap["score"]["rank"] == 1 and cheap["score"]["verdict"] == "Good price" and cheap["host"] == "autotrader.com"
assert len(call("list_listings", rav4.get_id())["listings"]) == 4
assert call("get_picks")["picks"][0]["listings"]["best"]["price"] == 26000
ok(call("set_listing_status", cheap["id"], "Contacted"))
bad(call("set_listing_status", cheap["id"], "Teleported"))
upd = ok(call("save_listing", dict(cheap, price=27000, status="Seen it")))["listing"]
assert upd["price"] == 27000 and upd["status"] == "Seen it"
as_user(bob)
bad(call("save_listing", dict(cheap, price=1)), "can't change someone else's listing")
bad(call("delete_listing", cheap["id"]))
assert call("list_listings")["total"] == 0
assert len(call("pick_choices")["mine"]) == 2
as_user(ana)
ok(call("delete_listing", cheap["id"]))
assert call("list_listings")["total"] == 4

# ---------------------------------------------------------------------------------- admin: car data
as_user(ana)
for fn, args in [("admin_import_preview", ("make,model\nA,B",)), ("admin_import", ("make,model\nA,B",)),
                 ("admin_imports", ()), ("admin_undo_import", ("x",)), ("admin_export_csv", ()), ("admin_cars", ()),
                 ("admin_car_status", ("x", "hidden")), ("admin_delete_car", ("x",)), ("admin_fields", ()),
                 ("admin_save_field", ("x", {})), ("admin_sources", ()), ("admin_save_source", ({},)),
                 ("admin_delete_source", ("x",)), ("admin_markets", ()), ("save_market", ({},)), ("delete_market", ("x",))]:
    assert denied(fn, *args), fn
as_user(admin)
CSV = ("Make;Model;Horsepower;MSRP;Fuel type;Seating;Euro NCAP;Bed length (mm);Features\n"
       "Toyota;RAV4;230;32500;H/PH;5;5;;std\n"
       "Zeta Motors;Comet One;150;19 990;Electric;4;;;360\n"
       "Zeta Motors;Comet Pickup;300;45000;E;5;4;1800;cp\n"
       "Zeta Motors;Broken;abc;1;E;5;;;\n")
pv = ok(call("admin_import_preview", CSV))["preview"]
assert pv["new"] == 3 and pv["updates"] == 1 and pv["new_makes"] == ["Zeta Motors"], pv
assert [f["key"] for f in pv["new_fields"]] == ["bed_length_mm"] and pv["new_fields"][0]["kind"] == "number", pv
assert any("hp 'abc'" in e for e in pv["errors"]), pv["errors"]
assert T.cars.get(slug="zeta-motors-comet-one") is None, "preview changes nothing"
bad(call("admin_import", "make,model\n"))
res = ok(call("admin_import", anvil.Media("text/csv", CSV.encode("utf-8"), "zeta.csv"), "", "Zeta brochure 2026"))["result"]
assert res["added"] == 3 and res["updated"] == 1
assert T.cars.get(slug="toyota-rav4")["specs"]["price"] == 32500 and T.cars.get(slug="toyota-rav4")["specs"]["ncap"] == 5
assert T.cars.get(slug="toyota-rav4")["specs"]["length"] == 4600, "empty cells don't wipe what's there"
comet = T.cars.get(slug="zeta-motors-comet-one")
assert comet["specs"]["price"] == 19990 and comet["specs"]["fuel"] == ["Electric"] and comet["specs"]["cam360"] is True
assert T.car_fields.get(key="bed_length_mm")["grp"] == "Imported" and T.brands.get(name="Zeta Motors")
assert call("get_catalog", cat["v"]).get("json"), "a new import gives a new catalogue version"
imps = ok(call("admin_imports"))["imports"]
assert imps[0]["filename"] == "zeta.csv" and imps[0]["added"] == 3 and imps[0]["who"] == "The Admin"
# a member picks an imported car, then the import is undone: the pick goes, the listing stays without a car
as_user(bob)
ok(call("pick_add", comet.get_id()))
ok(call("save_listing", {"url": "https://zeta.example/comet", "car_id": comet.get_id()}))
as_user(admin)
assert ok(call("admin_undo_import", imps[0]["id"]))["removed"] == 3
assert T.cars.get(slug="zeta-motors-comet-one") is None and T.cars.get(slug="toyota-rav4") is not None
as_user(bob)
assert len(call("get_picks")["picks"]) == 2 and call("list_listings")["listings"][0]["car_id"] is None
as_user(admin)
ex = ok(call("admin_export_csv"))
assert ex["csv"].startswith("make,model,") and "Toyota,RAV4" in ex["csv"] and ex["csv"].count("\n") >= n_cars
assert ok(call("admin_export_csv", True))["csv"].count("\n") == 1
# a round trip: the exported file imports again as pure updates
pv2 = ok(call("admin_import_preview", ex["csv"]))["preview"]
assert pv2["new"] == 0 and pv2["updates"] == n_cars and not pv2["errors"], pv2["errors"][:3]
cars_ = ok(call("admin_cars", "rav4"))["cars"]
assert cars_[0]["name"] == "Toyota RAV4"
ok(call("admin_car_status", rav4.get_id(), "hidden"))
as_user(None)
assert all(c["id"] != rav4.get_id() for c in json.loads(call("get_catalog")["json"])["cars"]), "hidden cars leave the catalogue"
bad(call("get_car", rav4.get_id()))
as_user(admin)
bad(call("admin_car_status", rav4.get_id(), "weird"))
ok(call("admin_car_status", rav4.get_id(), "published"))
fl = ok(call("admin_fields"))
assert any(f["key"] == "price" and f["cars"] >= n_cars for f in fl["fields"])
ok(call("admin_save_field", "price", {"label": "Starting price", "group": "Price & ownership", "kind": "number", "unit": "USD", "filter": True, "show": True, "better": "low"}))
assert T.car_fields.get(key="price")["label"] == "Starting price"
ok(call("admin_save_field", "Insurance group", {"label": "Insurance group", "kind": "number", "group": "Ownership"}))
assert T.car_fields.get(key="insurance_group")["kind"] == "number"
bad(call("admin_save_field", "x", {"label": ""}))
src = ok(call("admin_sources"))
assert len(src["sources"]) >= 10
s1 = ok(call("admin_save_source", {"title": "Auto Katalog 2026", "kind": "Book", "year": "2026", "status": "Requested"}))["source"]
bad(call("admin_save_source", {"title": "X", "url": "ftp://x"}))
bad(call("admin_save_source", {"title": "Year test", "year": "soon"}))
ok(call("admin_delete_source", s1["id"]))
ok(call("admin_delete_car", T.cars.get(slug="honda-cr-v").get_id()))
as_user(ana)
assert len(call("get_picks")["picks"]) == 3, "deleting a car removes it from people's five"
as_user(admin)
m = ok(call("save_market", {"name": "Test Cars", "region": "Canada", "kind": "Dealer", "url": "https://test.example", "search_url": "https://test.example/s?q={q}"}))["market"]
bad(call("save_market", {"name": "No q", "url": "https://x.example", "search_url": "https://x.example/s"}))
bad(call("save_market", {"name": "Bad", "url": "x.example"}))
assert any(x["name"] == "Test Cars" for x in call("admin_markets")["markets"])
ok(call("delete_market", m["id"]))

# ---------------------------------------------------------------------------------- admin overview + demo data
as_user(ana)
for fn, args in [("admin_overview", ()), ("list_users", ()), ("set_admin", (bob.get_id(), True)), ("demo_load", ()), ("demo_remove", ())]:
    assert denied(fn, *args), fn
as_user(admin)
ov = call("admin_overview")
assert ov["users"] == 3 and ov["admins"] == 1 and ov["cars"] >= 250 and ov["imports"] == 2
ok(call("demo_remove"))
assert M["DemoData"].state() == "removed" and not T.users.search(is_demo=True) and not T.picks.search(is_demo=True)
assert len(T.picks.search()) == 4, "removing demo data keeps real picks"
as_user(None)
call("get_catalog")
assert M["DemoData"].state() == "removed", "removed demo data doesn't come back by itself"
as_user(admin)
ok(call("demo_load"))
ok(call("demo_load"))
assert len(T.users.search(is_demo=True)) == len(M["DemoData"].DEMO_USERS), "reloading replaces the demo instead of doubling it"

# ---------------------------------------------------------------------------------- Privacy & Terms
if "legal_server" in M:
    as_user(ana)
    st = call("legal_state")
    assert st["signedIn"] and st["accepted_version"] is None
    ok(call("legal_accept", st["version"], "signup"))
    assert ana["legal_source"] == "signup" and call("legal_state")["accepted_version"] == st["version"]

# ---------------------------------------------------------------------------------- schema check (App Board): names only, never data
r = anvil.server.ENDPOINTS["/schema-check"](tables="users, cars,no_such_table")
json.dumps(r)
assert "email" in r["tables"]["users"] and "specs" in r["tables"]["cars"] and r["tables"]["no_such_table"] is None, r

# ---------------------------------------------------------------------------------- every callable is covered by a permission check
# A callable that changes data without require_user / a C.require_* check is a security hole. List the public ones here.
PUBLIC = {"get_me", "submit_feedback", "legal_state", "legal_accept", "get_catalog", "get_car", "cars_summary",
          "compare_cars", "list_brands", "popular_picks", "list_marketplaces"}
for name, (f, need) in sorted(anvil.server.CALLABLES.items()):
    if name in PUBLIC:
        continue
    assert need, "%s is callable by anyone: add require_user=True (or list it in PUBLIC in test_server.py)" % name

print("ALL OK (%d server functions)" % len(anvil.server.CALLABLES))
