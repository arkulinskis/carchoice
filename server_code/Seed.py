"""Reference data CarChoice starts with: the field list (every column/filter), brands, marketplaces, the data-source
wishlist, and the starter car set (SeedCars.CSV, loaded through Importer like any admin upload).

ensure_seeded() runs once (app setting "seeded"); each part only fills an EMPTY table, so admin edits are never
overwritten. The starter car set is an ordinary import: Admin -> Car data can remove it ("Undo") like any other.
"""
from anvil.tables import app_tables

from . import common as C

# key, label, group, kind, unit, decimals, filter, show (default column), help, better (high/low/"")
FIELDS = [
    ("make", "Make", "Basics", "choice", "", 0, True, True, "", ""),
    ("model", "Model", "Basics", "text", "", 0, False, True, "", ""),
    ("body", "Body", "Basics", "choice", "", 0, True, True, "", ""),
    ("size", "Size class", "Basics", "choice", "", 0, True, False, "", ""),
    ("tier", "Market tier", "Basics", "choice", "", 0, True, False, "Budget, Mainstream, Premium, Luxury or Exotic.", ""),
    ("origin", "Brand country", "Basics", "choice", "", 0, True, False, "Where the brand comes from (not where the car is built).", ""),
    ("year_from", "Generation since", "Basics", "number", "", 0, True, False, "The year the current generation came out.", "high"),
    ("price", "Base price", "Price & ownership", "number", "USD", 0, True, True,
     "Approximate starting price new, in US dollars. Europe-only models are converted from euros.", "low"),
    ("warranty", "Warranty", "Price & ownership", "number", "yrs", 0, True, False, "Basic new-car warranty in the US.", "high"),
    ("pt_warranty", "Powertrain warranty", "Price & ownership", "number", "yrs", 0, True, False, "Engine and gearbox warranty in the US.", "high"),
    ("hp", "Power", "Performance", "number", "hp", 0, True, True, "", "high"),
    ("torque", "Torque", "Performance", "number", "Nm", 0, True, False, "", "high"),
    ("zero100", "0-100 km/h", "Performance", "number", "s", 1, True, False, "", "low"),
    ("top_speed", "Top speed", "Performance", "number", "km/h", 0, True, False, "", "high"),
    ("engine_l", "Engine size", "Performance", "number", "L", 1, True, False, "0 means fully electric.", ""),
    ("cyl", "Cylinders", "Performance", "number", "", 0, True, False, "0 means fully electric.", ""),
    ("trans", "Gearbox", "Performance", "multi", "", 0, True, False, "", ""),
    ("drive", "Drive", "Performance", "multi", "", 0, True, True, "", ""),
    ("fuel", "Fuel", "Efficiency & EV", "multi", "", 0, True, True, "", ""),
    ("l100", "Fuel use", "Efficiency & EV", "number", "L/100km", 1, True, True,
     "Combined rating of the base petrol, diesel or hybrid version.", "low"),
    ("ev_range", "Electric range", "Efficiency & EV", "number", "km", 0, True, True,
     "EPA for North American models, WLTP for Europe-only ones. Plug-in hybrids: the electric-only range.", "high"),
    ("battery", "Battery", "Efficiency & EV", "number", "kWh", 1, True, False, "Usable capacity where published.", "high"),
    ("dc_kw", "Fast charging", "Efficiency & EV", "number", "kW", 0, True, False, "Peak DC charging power.", "high"),
    ("length", "Length", "Size & space", "number", "mm", 0, True, False, "", ""),
    ("width", "Width", "Size & space", "number", "mm", 0, True, False, "Without mirrors.", ""),
    ("height", "Height", "Size & space", "number", "mm", 0, True, False, "", ""),
    ("wheelbase", "Wheelbase", "Size & space", "number", "mm", 0, True, False, "", "high"),
    ("weight", "Weight", "Size & space", "number", "kg", 0, True, False, "Approximate curb weight.", "low"),
    ("cargo", "Cargo space", "Size & space", "number", "litres", 0, True, True,
     "Behind the second row. North American figures (SAE) run larger than European ones (VDA).", "high"),
    ("seats", "Seats", "Size & space", "number", "", 0, True, True, "Most seats offered.", "high"),
    ("ground", "Ground clearance", "Size & space", "number", "mm", 0, True, False, "", "high"),
    ("towing", "Towing", "Capability", "number", "kg", 0, True, False, "Most braked towing offered; 0 means not rated.", "high"),
    ("carplay", "CarPlay / Android Auto", "Features", "bool", "", 0, True, False, "Available on at least one trim.", ""),
    ("acc", "Adaptive cruise", "Features", "bool", "", 0, True, False, "Available on at least one trim.", ""),
    ("aeb", "Automatic emergency braking", "Features", "bool", "", 0, True, False, "Available on at least one trim.", ""),
    ("row3", "Third row", "Features", "bool", "", 0, True, False, "Seven or more seats available.", ""),
    ("heatpump", "Heat pump", "Features", "bool", "", 0, True, False, "Keeps electric range up in the cold.", ""),
    ("hud", "Head-up display", "Features", "bool", "", 0, True, False, "Available on at least one trim.", ""),
    ("cam360", "360° camera", "Features", "bool", "", 0, True, False, "Available on at least one trim.", ""),
    ("roof", "Sunroof or open top", "Features", "bool", "", 0, True, False, "Available on at least one trim.", ""),
    ("manual", "Manual gearbox", "Features", "bool", "", 0, True, False, "A manual is offered.", ""),
    ("regions", "Sold in", "Market", "multi", "", 0, True, False, "", ""),
    ("status", "Status", "Market", "choice", "", 0, True, False, "Discontinued models can still be bought used.", ""),
    ("ncap", "Euro NCAP stars", "Safety", "number", "", 0, True, False, "No ratings in the starter data yet: an admin can upload them.", "high"),
    ("iihs", "IIHS award", "Safety", "choice", "", 0, True, False, "No ratings in the starter data yet: an admin can upload them.", ""),
]

# name, country, group, founded, website, US warranty years (basic, powertrain)
BRANDS = [
    ("Toyota", "Japan", "Toyota Motor", 1937, "https://www.toyota.com", 3, 5),
    ("Lexus", "Japan", "Toyota Motor", 1989, "https://www.lexus.com", 4, 6),
    ("Honda", "Japan", "Honda", 1948, "https://automobiles.honda.com", 3, 5),
    ("Acura", "Japan", "Honda", 1986, "https://www.acura.com", 4, 6),
    ("Nissan", "Japan", "Nissan", 1933, "https://www.nissan-global.com", 3, 5),
    ("Infiniti", "Japan", "Nissan", 1989, "https://www.infinitiusa.com", 4, 6),
    ("Mazda", "Japan", "Mazda", 1920, "https://www.mazda.com", 3, 5),
    ("Subaru", "Japan", "Subaru Corporation", 1953, "https://www.subaru.com", 3, 5),
    ("Mitsubishi", "Japan", "Mitsubishi Motors", 1970, "https://www.mitsubishicars.com", 5, 10),
    ("Suzuki", "Japan", "Suzuki", 1909, "https://www.globalsuzuki.com", None, None),
    ("Hyundai", "South Korea", "Hyundai Motor Group", 1967, "https://www.hyundai.com", 5, 10),
    ("Kia", "South Korea", "Hyundai Motor Group", 1944, "https://www.kia.com", 5, 10),
    ("Genesis", "South Korea", "Hyundai Motor Group", 2015, "https://www.genesis.com", 5, 10),
    ("Ford", "United States", "Ford Motor Company", 1903, "https://www.ford.com", 3, 5),
    ("Lincoln", "United States", "Ford Motor Company", 1917, "https://www.lincoln.com", 4, 6),
    ("Chevrolet", "United States", "General Motors", 1911, "https://www.chevrolet.com", 3, 5),
    ("GMC", "United States", "General Motors", 1911, "https://www.gmc.com", 3, 5),
    ("Cadillac", "United States", "General Motors", 1902, "https://www.cadillac.com", 4, 6),
    ("Buick", "United States", "General Motors", 1903, "https://www.buick.com", 4, 6),
    ("Jeep", "United States", "Stellantis", 1941, "https://www.jeep.com", 3, 5),
    ("Ram", "United States", "Stellantis", 2010, "https://www.ramtrucks.com", 3, 5),
    ("Dodge", "United States", "Stellantis", 1914, "https://www.dodge.com", 3, 5),
    ("Chrysler", "United States", "Stellantis", 1925, "https://www.chrysler.com", 3, 5),
    ("Tesla", "United States", "Tesla", 2003, "https://www.tesla.com", 4, 8),
    ("Rivian", "United States", "Rivian", 2009, "https://rivian.com", 5, 8),
    ("Lucid", "United States", "Lucid Group", 2007, "https://lucidmotors.com", 4, 8),
    ("Volkswagen", "Germany", "Volkswagen Group", 1937, "https://www.volkswagen.com", 4, 4),
    ("Audi", "Germany", "Volkswagen Group", 1909, "https://www.audi.com", 4, 4),
    ("Porsche", "Germany", "Volkswagen Group", 1931, "https://www.porsche.com", 4, 4),
    ("BMW", "Germany", "BMW Group", 1916, "https://www.bmw.com", 4, 4),
    ("Mini", "United Kingdom", "BMW Group", 1959, "https://www.mini.com", 4, 4),
    ("Mercedes-Benz", "Germany", "Mercedes-Benz Group", 1926, "https://www.mercedes-benz.com", 4, 4),
    ("Smart", "China", "Mercedes-Benz and Geely", 1994, "https://www.smart.com", None, None),
    ("Volvo", "Sweden", "Geely", 1927, "https://www.volvocars.com", 4, 4),
    ("Polestar", "Sweden", "Geely", 2017, "https://www.polestar.com", 4, 8),
    ("Land Rover", "United Kingdom", "JLR (Tata Motors)", 1948, "https://www.landrover.com", 4, 4),
    ("Jaguar", "United Kingdom", "JLR (Tata Motors)", 1935, "https://www.jaguar.com", 5, 5),
    ("Alfa Romeo", "Italy", "Stellantis", 1910, "https://www.alfaromeo.com", 4, 4),
    ("Fiat", "Italy", "Stellantis", 1899, "https://www.fiat.com", 4, 4),
    ("Maserati", "Italy", "Stellantis", 1914, "https://www.maserati.com", 4, 4),
    ("Ferrari", "Italy", "Ferrari", 1939, "https://www.ferrari.com", 3, 3),
    ("Lamborghini", "Italy", "Volkswagen Group", 1963, "https://www.lamborghini.com", 3, 3),
    ("Peugeot", "France", "Stellantis", 1810, "https://www.peugeot.com", None, None),
    ("Renault", "France", "Renault Group", 1899, "https://www.renault.com", None, None),
    ("Dacia", "Romania", "Renault Group", 1966, "https://www.dacia.com", None, None),
    ("Citroën", "France", "Stellantis", 1919, "https://www.citroen.com", None, None),
    ("Opel", "Germany", "Stellantis", 1862, "https://www.opel.com", None, None),
    ("Skoda", "Czech Republic", "Volkswagen Group", 1895, "https://www.skoda-auto.com", None, None),
    ("Seat", "Spain", "Volkswagen Group", 1950, "https://www.seat.com", None, None),
    ("Cupra", "Spain", "Volkswagen Group", 2018, "https://www.cupraofficial.com", None, None),
    ("BYD", "China", "BYD", 2003, "https://www.byd.com", None, None),
    ("MG", "China", "SAIC Motor", 1924, "https://www.mgmotor.eu", None, None),
    # Brands with no models in the starter data yet (the directory is wider than the table)
    ("Aston Martin", "United Kingdom", "Aston Martin Lagonda", 1913, "https://www.astonmartin.com", None, None),
    ("Bentley", "United Kingdom", "Volkswagen Group", 1919, "https://www.bentleymotors.com", None, None),
    ("Rolls-Royce", "United Kingdom", "BMW Group", 1906, "https://www.rolls-roycemotorcars.com", None, None),
    ("McLaren", "United Kingdom", "McLaren Group", 1985, "https://cars.mclaren.com", None, None),
    ("Lotus", "United Kingdom", "Geely", 1948, "https://www.lotuscars.com", None, None),
    ("Bugatti", "France", "Bugatti Rimac", 1909, "https://www.bugatti.com", None, None),
    ("Alpine", "France", "Renault Group", 1955, "https://www.alpinecars.com", None, None),
    ("DS Automobiles", "France", "Stellantis", 2014, "https://www.dsautomobiles.com", None, None),
    ("Lancia", "Italy", "Stellantis", 1906, "https://www.lancia.com", None, None),
    ("Abarth", "Italy", "Stellantis", 1949, "https://www.abarth.com", None, None),
    ("Zeekr", "China", "Geely", 2021, "https://www.zeekr.eu", None, None),
    ("NIO", "China", "NIO", 2014, "https://www.nio.com", None, None),
    ("XPeng", "China", "XPeng", 2014, "https://www.xpeng.com", None, None),
    ("Li Auto", "China", "Li Auto", 2015, "https://www.lixiang.com", None, None),
    ("Geely", "China", "Geely", 1986, "https://global.geely.com", None, None),
    ("Chery", "China", "Chery", 1997, "https://www.cheryinternational.com", None, None),
    ("GWM", "China", "Great Wall Motor", 1984, "https://www.gwm-global.com", None, None),
    ("Leapmotor", "China", "Leapmotor (Stellantis partner)", 2015, "https://www.leapmotor.com", None, None),
    ("VinFast", "Vietnam", "Vingroup", 2017, "https://vinfastauto.com", None, None),
    ("Tata", "India", "Tata Motors", 1945, "https://cars.tatamotors.com", None, None),
    ("Mahindra", "India", "Mahindra Group", 1945, "https://auto.mahindra.com", None, None),
    ("Maruti Suzuki", "India", "Suzuki", 1981, "https://www.marutisuzuki.com", None, None),
    ("Proton", "Malaysia", "DRB-HICOM and Geely", 1983, "https://www.proton.com", None, None),
    ("Scout Motors", "United States", "Volkswagen Group", 2022, "https://www.scoutmotors.com", None, None),
]

# name, region, kind, url, search_url ({q} = the search words; blank = a Google site: search), notes
MARKETPLACES = [
    ("Autotrader", "US", "Marketplace", "https://www.autotrader.com", "", "Dealer and private listings with filters for price, mileage and distance."),
    ("Cars.com", "US", "Marketplace", "https://www.cars.com", "", "Dealer listings with dealer reviews and price badges."),
    ("CarGurus", "US", "Marketplace", "https://www.cargurus.com", "", "Rates each listing against its own price estimate, from great deal to overpriced."),
    ("CarMax", "US", "Dealer", "https://www.carmax.com", "", "Used-car superstores with fixed prices; read the return policy."),
    ("Carvana", "US", "Online dealer", "https://www.carvana.com", "", "Buy online with home delivery and a return window; read the terms."),
    ("TrueCar", "US", "Marketplace", "https://www.truecar.com", "", "New and used listings with price ranges from recent sales."),
    ("Facebook Marketplace", "US", "Classifieds", "https://www.facebook.com/marketplace", "https://www.facebook.com/marketplace/search/?query={q}", "Many private sellers. See the car before paying anything."),
    ("Craigslist", "US", "Classifieds", "https://www.craigslist.org", "", "Pick your city first. Private sellers; meet somewhere public."),
    ("eBay Motors", "US", "Auction", "https://www.ebay.com/motors", "https://www.ebay.com/sch/i.html?_nkw={q}&_sacat=6001", "Auctions and buy-it-now listings across the country."),
    ("Cars & Bids", "US", "Auction", "https://carsandbids.com", "", "Online auctions for enthusiast cars from the 1980s on."),
    ("Bring a Trailer", "US", "Auction", "https://bringatrailer.com", "", "Online auctions for classic and enthusiast cars."),
    ("Edmunds", "US", "Price guide", "https://www.edmunds.com", "", "Reviews, listings and its own market-value prices."),
    ("Kelley Blue Book", "US", "Price guide", "https://www.kbb.com", "", "Fair purchase prices and trade-in values by trim and mileage."),
    ("AutoTrader.ca", "Canada", "Marketplace", "https://www.autotrader.ca", "", "A large Canadian marketplace for dealer and private listings."),
    ("Kijiji Autos", "Canada", "Classifieds", "https://www.kijijiautos.ca", "", "Dealer and private listings across Canada."),
    ("CarGurus Canada", "Canada", "Marketplace", "https://www.cargurus.ca", "", "Deal ratings on Canadian listings."),
    ("Clutch", "Canada", "Online dealer", "https://www.clutch.ca", "", "Buy online with delivery; read the return terms."),
    ("Canada Drives", "Canada", "Online dealer", "https://www.canadadrives.ca", "", "Buy online with delivery in several provinces."),
    ("Canadian Black Book", "Canada", "Price guide", "https://www.canadianblackbook.com", "", "Used-car values for the Canadian market."),
    ("Auto Trader UK", "UK", "Marketplace", "https://www.autotrader.co.uk", "", "The big UK marketplace, with a price indicator on each listing."),
    ("Motors.co.uk", "UK", "Marketplace", "https://www.motors.co.uk", "", "Dealer listings from across the UK."),
    ("Gumtree", "UK", "Classifieds", "https://www.gumtree.com", "", "Private and trade sellers."),
    ("eBay UK", "UK", "Auction", "https://www.ebay.co.uk", "https://www.ebay.co.uk/sch/i.html?_nkw={q}&_sacat=9801", "Auctions and buy-it-now cars."),
    ("CarGurus UK", "UK", "Marketplace", "https://www.cargurus.co.uk", "", "Deal ratings on UK listings."),
    ("Cinch", "UK", "Online dealer", "https://www.cinch.co.uk", "", "Buy online with delivery."),
    ("Carwow", "UK", "Marketplace", "https://www.carwow.co.uk", "", "Dealers compete with offers on new and used cars."),
    ("Parkers", "UK", "Price guide", "https://www.parkers.co.uk", "", "UK used-car valuations and reviews."),
    ("mobile.de", "Europe", "Marketplace", "https://www.mobile.de", "", "Germany's big car marketplace; buyers come from all over Europe."),
    ("AutoScout24", "Europe", "Marketplace", "https://www.autoscout24.com", "", "Listings across many European countries."),
    ("Kleinanzeigen", "Europe", "Classifieds", "https://www.kleinanzeigen.de", "", "German classifieds with many private sellers."),
    ("Leboncoin", "Europe", "Classifieds", "https://www.leboncoin.fr", "", "France's big classifieds site."),
    ("La Centrale", "Europe", "Marketplace", "https://www.lacentrale.fr", "", "French car listings with a price rating."),
    ("Subito", "Europe", "Classifieds", "https://www.subito.it", "", "Italian classifieds."),
    ("Coches.net", "Europe", "Marketplace", "https://www.coches.net", "", "Spanish car listings."),
    ("Marktplaats", "Europe", "Classifieds", "https://www.marktplaats.nl", "", "Dutch classifieds."),
    ("Blocket", "Europe", "Classifieds", "https://www.blocket.se", "", "Swedish classifieds."),
    ("Finn.no", "Europe", "Classifieds", "https://www.finn.no", "", "Norwegian classifieds; many used electric cars."),
    ("OLX Poland", "Europe", "Classifieds", "https://www.olx.pl", "", "Polish classifieds (OLX also runs sites in other countries)."),
    ("SS.com", "Baltics", "Classifieds", "https://www.ss.com", "", "Latvia's big classifieds site."),
    ("auto24", "Baltics", "Marketplace", "https://www.auto24.ee", "", "Estonian car listings (also auto24.lv)."),
    ("Autoplius", "Baltics", "Marketplace", "https://autoplius.lt", "", "Lithuanian car listings."),
    ("carsales", "Australia", "Marketplace", "https://www.carsales.com.au", "", "Australia's big car marketplace."),
    ("Drive", "Australia", "Marketplace", "https://www.drive.com.au", "", "Reviews and car listings."),
    ("Gumtree Australia", "Australia", "Classifieds", "https://www.gumtree.com.au", "", "Private and trade sellers."),
]

# title, kind, publisher, year, url, status, notes
SOURCES = [
    ("Fuel economy data for every US model since 1984", "Dataset", "US EPA / Department of Energy", None,
     "https://www.fueleconomy.gov/feg/download.shtml", "Wishlist",
     "Free download (vehicles.csv, public domain). Fuel use, engine, drive, class and EV range for every US model year. Needs a column map to import."),
    ("Fuel consumption ratings (Canada)", "Dataset", "Natural Resources Canada", None,
     "https://open.canada.ca", "Wishlist", "Open Government Licence - Canada. Search the portal for \"Fuel consumption ratings\"."),
    ("Vehicle Product Information Catalog (vPIC)", "Dataset", "NHTSA", None, "https://vpic.nhtsa.dot.gov/api/", "Wishlist",
     "Free API: every make and model sold in the US, VIN decoding."),
    ("5-Star Safety Ratings", "Dataset", "NHTSA", None, "https://www.nhtsa.gov/nhtsa-datasets-and-apis", "Wishlist",
     "Free US crash-test ratings by model year."),
    ("CO2 emissions from new passenger cars (EU)", "Dataset", "European Environment Agency", None,
     "https://www.eea.europa.eu", "Wishlist", "Every car registered in the EU: mass, engine size, power, CO2, fuel."),
    ("Car fuel and CO2 data (UK)", "Dataset", "Vehicle Certification Agency", None,
     "https://carfueldata.vehicle-certification-agency.gov.uk", "Wishlist", "Official UK fuel and CO2 figures."),
    ("Euro NCAP results", "Website", "Euro NCAP", None, "https://www.euroncap.com", "Wishlist",
     "Star ratings for the Euro NCAP field. Check the terms before copying in bulk."),
    ("IIHS ratings", "Website", "Insurance Institute for Highway Safety", None, "https://www.iihs.org/ratings", "Wishlist",
     "Top Safety Pick awards for the IIHS field."),
    ("Manufacturer spec sheets and press kits", "Brochure", "Each manufacturer", None, "", "Wishlist",
     "Media sites publish trim-level specs and prices: the best source for every number in the table."),
    ("Automobil Revue catalogue (annual)", "Book", "Automobil Revue", None, "", "Wishlist",
     "Yearly catalogue of cars on sale worldwide with full specifications."),
    ("Auto Katalog (annual)", "Book", "auto motor und sport", None, "", "Wishlist",
     "Yearly German catalogue of every model on sale in Europe with prices and specs."),
    ("Annual Auto Issue", "Magazine", "Consumer Reports", None, "https://www.consumerreports.org", "Wishlist",
     "Reliability and owner satisfaction by model (subscription; reuse needs permission)."),
    ("Owner's manuals", "Manual", "Each manufacturer", None, "", "Wishlist",
     "Towing limits, capacities, tyre sizes, maintenance schedules."),
]


def ensure_seeded():
    """Fill the reference tables the first time the app runs (only empty tables are filled)."""
    if C.get_setting("seeded"):
        return
    fill_fields()
    if not len(app_tables.brands.search()):
        for name, country, group, founded, web, w, pw in BRANDS:
            app_tables.brands.add_row(name=name, country=country, group_name=group, founded=founded, website=web,
                                      warranty=w, pt_warranty=pw, notes="")
    if not len(app_tables.marketplaces.search()):
        for i, (name, region, kind, url, s_url, notes) in enumerate(MARKETPLACES):
            app_tables.marketplaces.add_row(name=name, region=region, kind=kind, url=url, search_url=s_url,
                                            notes=notes, sort=i, active=True)
    if not len(app_tables.sources.search()):
        for title, kind, pub, year, url, status, notes in SOURCES:
            app_tables.sources.add_row(title=title, kind=kind, publisher=pub, year=year, url=url, status=status,
                                       notes=notes, created=C.now())
    if not len(app_tables.cars.search()):
        from . import Importer, SeedCars
        Importer.run(SeedCars.CSV, filename="CarChoice starter set", source="CarChoice starter set (approximate)",
                     kind="seed", who=None, mode="merge")
    C.set_setting("seeded", True)


def fill_fields():
    have = {r["key"] for r in app_tables.car_fields.search()}
    for i, (key, label, grp, kind, unit, dec, filt, show, help_, better) in enumerate(FIELDS):
        if key not in have:
            app_tables.car_fields.add_row(key=key, label=label, grp=grp, kind=kind, unit=unit, decimals=dec,
                                          filter=filt, show=show, sort=i * 10, help=help_, better=better)
