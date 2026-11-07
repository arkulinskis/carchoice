"""CarChoice's starter car data: one row per model (a typical trim, model years 2024-2026).

Approximate figures compiled from manufacturers' published specifications. They are a starting point for research, not
a quote: check the maker's own spec sheet before buying. Admins replace or extend this set with official data through
Admin -> Car data (the same CSV format, read by Importer.py; short codes below are expanded there).

Short codes: fuel P petrol, D diesel, H hybrid, PH plug-in hybrid, E electric; trans A automatic, M manual, CVT,
DCT dual-clutch, 1 single-speed; regions NA, EU, UK, AU, AS, ALL; status D = discontinued (blank = on sale);
features: std = CarPlay/Android Auto + adaptive cruise + emergency braking, cp, acc, aeb, row3, heatpump, hud, 360, roof, man.
Prices: approximate US starting prices in USD; Europe-only models converted from euros (noted). Ranges: EPA for North
American models, WLTP for Europe-only ones (noted). Cargo: behind the second row.
"""

CSV = """make,model,body,size,tier,fuel,drive,trans,year_from,price,hp,torque,zero100,top_speed,engine_l,cyl,l100,ev_range,battery,dc_kw,length,width,height,wheelbase,weight,cargo,seats,ground,towing,regions,status,features,notes
Toyota,Corolla,Sedan,Compact,Mainstream,P/H,FWD/AWD,CVT,2019,22800,169,205,8.6,180,2.0,4,6.7,,,,4630,1780,1435,2700,1350,371,5,135,0,ALL,,std,
Toyota,Corolla Cross,SUV,Compact,Mainstream,P/H,FWD/AWD,CVT,2022,24600,169,203,9.0,180,2.0,4,7.4,,,,4460,1825,1620,2640,1450,742,5,203,680,NA/EU/AU/AS,,std,
Toyota,Camry,Sedan,Midsize,Mainstream,H,FWD/AWD,CVT,2025,28400,225,221,7.6,180,2.5,4,4.7,,,,4920,1840,1445,2825,1610,428,5,145,454,NA/AU/AS,,std,
Toyota,Prius,Hatchback,Compact,Mainstream,H/PH,FWD/AWD,CVT,2023,28500,194,190,7.2,180,2.0,4,4.1,63,13.6,,4600,1780,1430,2750,1420,400,5,140,0,ALL,,std,
Toyota,RAV4,SUV,Compact,Mainstream,H/PH,FWD/AWD,CVT,2026,31900,226,221,7.8,180,2.5,4,5.9,80,22.7,50,4600,1855,1685,2690,1700,1050,5,200,1600,ALL,,std 360 roof hud,
Toyota,Grand Highlander,SUV,Large,Mainstream,P/H,FWD/AWD,A,2024,41500,265,420,7.8,180,2.4,4,9.8,,,,5115,1990,1780,2950,1980,1640,8,205,2268,NA,,std row3 roof hud 360,
Toyota,4Runner,SUV,Midsize,Mainstream,P/H,RWD/4WD,A,2025,41000,278,430,7.5,180,2.4,4,11.2,,,,4950,1975,1800,2850,2100,1260,7,239,2722,NA,,std row3 roof,
Toyota,Tacoma,Pickup,Midsize,Mainstream,P/H,RWD/4WD,A/M,2024,32000,228,330,8.0,170,2.4,4,10.7,,,,5410,1955,1800,3330,1950,,5,240,2950,NA,,std,
Toyota,Tundra,Pickup,Large,Mainstream,P/H,RWD/4WD,A,2022,40500,389,649,6.5,180,3.4,6,12.4,,,,5933,2037,1980,3700,2400,,5,240,5443,NA,,std roof 360 hud,
Toyota,Sienna,Minivan,Large,Mainstream,H,FWD/AWD,CVT,2021,39200,245,239,7.9,180,2.5,4,6.5,,,,5175,1995,1740,3060,2000,2130,8,150,1588,NA/AS,,std row3 roof hud 360,
Toyota,bZ,SUV,Compact,Mainstream,E,FWD/AWD,1,2023,35000,221,269,7.0,160,0,0,,504,74.7,150,4690,1860,1650,2850,1950,750,5,205,1600,ALL,,std heatpump 360 roof,Called bZ4X before 2026
Toyota,Land Cruiser,SUV,Large,Premium,H/D,4WD,A,2024,57200,326,630,7.6,170,2.4,4,10.7,,,,4920,1980,1870,2850,2400,1065,5,220,2722,ALL,,std roof 360,
Toyota,GR86,Coupe,Small,Mainstream,P,RWD,A/M,2022,30000,228,250,6.3,226,2.4,4,10.2,,,,4265,1775,1310,2575,1275,226,4,130,0,ALL,,std man,
Toyota,GR Supra,Coupe,Small,Premium,P,RWD,A/M,2020,46600,382,500,4.1,250,3.0,6,9.0,,,,4380,1855,1295,2470,1540,290,2,115,0,ALL,,std man hud,
Toyota,Yaris,Hatchback,Small,Mainstream,H,FWD,CVT,2020,25000,116,141,9.7,175,1.5,3,3.9,,,,3940,1745,1500,2560,1090,286,5,140,0,EU/UK/AU/AS,,std,EU price converted
Toyota,C-HR,SUV,Compact,Mainstream,H/PH,FWD/AWD,CVT,2024,36000,140,142,9.9,180,1.8,4,4.8,,,,4360,1830,1560,2640,1450,364,5,160,725,EU/UK/AU,,std roof,EU price converted
Lexus,ES,Sedan,Midsize,Premium,P/H,FWD/AWD,CVT,2019,43200,215,221,8.1,180,2.5,4,5.3,,,,4975,1865,1445,2870,1650,470,5,150,454,ALL,,std hud 360 roof,
Lexus,IS,Sedan,Compact,Premium,P/H,RWD/AWD,A,2014,41000,241,350,7.0,230,2.0,4,9.4,,,,4710,1840,1435,2800,1630,300,5,130,0,NA/AU/AS,,std roof,
Lexus,UX,SUV,Small,Premium,H,FWD/AWD,CVT,2019,37500,196,188,8.0,177,2.0,4,5.0,,,,4495,1840,1540,2640,1520,300,5,160,0,ALL,,std,
Lexus,NX,SUV,Compact,Premium,P/H/PH,FWD/AWD,A/CVT,2022,42000,203,250,8.6,200,2.5,4,8.7,60,18.1,,4660,1865,1660,2690,1750,640,5,205,907,ALL,,std hud 360 roof,
Lexus,RX,SUV,Midsize,Premium,P/H/PH,FWD/AWD,A/CVT,2023,50000,275,430,7.6,200,2.4,4,9.0,,,,4890,1920,1695,2850,1950,612,5,205,1588,ALL,,std hud 360 roof,
Lexus,TX,SUV,Large,Premium,P/H/PH,FWD/AWD,A,2024,55000,275,430,8.0,180,2.4,4,10.2,,,,5160,1990,1780,2950,2100,1600,7,203,2268,NA,,std row3 hud 360 roof,
Lexus,GX,SUV,Large,Luxury,P,4WD,A,2024,65000,349,650,7.0,180,3.4,6,13.8,,,,4950,1980,1920,2850,2600,1300,7,210,3629,NA/AU/AS,,std row3 hud 360 roof,
Lexus,RZ,SUV,Compact,Premium,E,FWD/AWD,1,2023,46000,221,269,7.3,160,0,0,,428,72.8,150,4805,1895,1635,2850,2000,522,5,175,0,ALL,,std heatpump hud 360 roof,
Honda,Civic,Sedan,Compact,Mainstream,P/H,FWD,CVT/M,2022,25000,150,180,8.5,200,2.0,4,6.7,,,,4675,1800,1415,2735,1310,419,5,135,0,ALL,,std man,
Honda,Civic Type R,Hatchback,Compact,Premium,P,FWD,M,2023,46000,315,420,5.4,275,2.0,4,9.8,,,,4595,1890,1405,2735,1430,410,4,125,0,ALL,,std man,
Honda,Accord,Sedan,Midsize,Mainstream,P/H,FWD,CVT,2023,28300,192,260,7.7,200,1.5,4,7.4,,,,4970,1860,1450,2830,1500,473,5,135,454,NA/AU/AS,,std hud roof,
Honda,HR-V,SUV,Small,Mainstream,P,FWD/AWD,CVT,2023,25500,158,187,9.5,180,2.0,4,8.4,,,,4565,1840,1620,2610,1430,690,5,185,0,NA/AU/AS,,std,
Honda,CR-V,SUV,Compact,Mainstream,P/H/PH,FWD/AWD,CVT,2023,30900,190,243,8.2,190,1.5,4,7.6,,,,4705,1865,1680,2700,1590,1113,5,208,680,ALL,,std roof,
Honda,Pilot,SUV,Large,Mainstream,P,FWD/AWD,A,2023,40200,285,355,7.0,180,3.5,6,11.2,,,,5085,1995,1805,2890,1950,1380,8,185,2268,NA,,std row3 roof,
Honda,Passport,SUV,Midsize,Mainstream,P,AWD,A,2026,44000,285,355,7.0,180,3.5,6,11.8,,,,4840,2000,1850,2890,2000,1240,5,211,2268,NA,,std roof,
Honda,Odyssey,Minivan,Large,Mainstream,P,FWD,A,2018,39500,280,355,7.3,180,3.5,6,10.7,,,,5220,1995,1735,3000,2000,2450,8,115,1361,NA/AS,,std row3 roof,
Honda,Ridgeline,Pickup,Midsize,Mainstream,P,AWD,A,2017,40000,280,355,7.0,180,3.5,6,11.8,,,,5420,1995,1800,3180,2000,,5,200,2268,NA,,std roof,
Honda,Prologue,SUV,Midsize,Mainstream,E,FWD/AWD,1,2024,47400,220,333,7.6,160,0,0,,476,85,150,4880,1990,1640,3095,2250,650,5,165,680,NA,,std heatpump roof 360,
Acura,Integra,Hatchback,Compact,Premium,P,FWD,CVT/M,2023,33000,200,260,7.5,210,1.5,4,7.4,,,,4720,1830,1410,2735,1395,688,5,130,0,NA,,std man hud,
Acura,TLX,Sedan,Midsize,Premium,P,FWD/AWD,A,2021,45000,272,380,6.2,210,2.0,4,9.4,,,,4945,1910,1430,2870,1650,382,5,135,0,NA,,std hud roof,
Acura,RDX,SUV,Compact,Premium,P,FWD/AWD,A,2019,44700,272,380,6.6,200,2.0,4,9.8,,,,4745,1900,1670,2750,1800,841,5,210,680,NA,,std hud roof,
Acura,MDX,SUV,Midsize,Premium,P,FWD/AWD,A,2022,51000,290,362,6.8,200,3.5,6,11.2,,,,5040,1980,1710,2890,1950,1370,7,190,2268,NA,,std row3 hud 360 roof,
Nissan,Versa,Sedan,Small,Budget,P,FWD,CVT/M,2020,18300,122,155,10.0,180,1.6,4,6.9,,,,4495,1740,1465,2620,1150,422,5,140,0,NA,,std man,
Nissan,Sentra,Sedan,Compact,Mainstream,P,FWD,CVT,2025,22000,149,198,9.0,190,2.0,4,7.1,,,,4640,1815,1450,2710,1360,405,5,140,0,NA/AS,,std,
Nissan,Altima,Sedan,Midsize,Mainstream,P,FWD/AWD,CVT,2019,27000,188,244,8.0,200,2.5,4,7.6,,,,4900,1850,1445,2825,1480,437,5,135,0,NA/AS,,std,
Nissan,Kicks,SUV,Small,Budget,P,FWD/AWD,CVT,2025,22000,141,190,9.4,180,2.0,4,7.6,,,,4365,1800,1630,2655,1390,870,5,210,0,NA/AS,,std,
Nissan,Rogue,SUV,Compact,Mainstream,P/PH,FWD/AWD,CVT,2021,29500,201,305,8.0,190,1.5,3,7.4,,,,4650,1840,1700,2705,1580,1047,5,210,680,NA/AS,,std hud 360 roof,
Nissan,Pathfinder,SUV,Large,Mainstream,P,FWD/AWD,A,2022,37500,284,351,7.0,180,3.5,6,10.7,,,,5005,1980,1800,2900,1950,1270,8,180,2722,NA/AU/AS,,std row3 360 roof hud,
Nissan,Frontier,Pickup,Midsize,Mainstream,P,RWD/4WD,A,2022,31000,310,381,6.9,180,3.8,6,12.4,,,,5265,1850,1825,3200,2000,,5,225,2948,NA,,std,
Nissan,Leaf,Hatchback,Compact,Mainstream,E,FWD,1,2026,30000,214,355,7.6,160,0,0,,488,75,150,4360,1810,1550,2690,1880,420,5,150,0,NA/EU/UK/AS,,std heatpump,Third generation; figures from launch data
Nissan,Ariya,SUV,Compact,Mainstream,E,FWD/AWD,1,2023,41000,214,300,7.5,160,0,0,,349,63,130,4595,1850,1660,2775,1950,640,5,180,680,NA/EU/UK/AS,,std heatpump hud 360 roof,
Nissan,Z,Coupe,Small,Premium,P,RWD,A/M,2023,42000,400,475,4.5,250,3.0,6,11.2,,,,4380,1845,1315,2550,1590,195,2,125,0,NA/AU/AS,,std man,
Nissan,Qashqai,SUV,Compact,Mainstream,P/H,FWD/AWD,CVT/M,2021,34000,158,260,9.2,199,1.3,4,6.4,,,,4425,1835,1625,2665,1450,504,5,175,1800,EU/UK/AU/AS,,std man 360 hud roof,EU price converted
Infiniti,QX60,SUV,Large,Premium,P,FWD/AWD,A,2022,50000,268,380,7.0,190,2.0,4,10.2,,,,5035,1980,1770,2900,2050,1180,7,180,2722,NA,,std row3 hud 360 roof,
Infiniti,QX80,SUV,Large,Luxury,P,RWD/4WD,A,2025,85000,450,700,6.0,210,3.5,6,13.8,,,,5370,2060,1945,3075,2750,1420,8,230,3855,NA/AS,,std row3 hud 360 roof,
Mazda,Mazda3,Hatchback,Compact,Mainstream,P,FWD/AWD,A/M,2019,24500,191,252,7.9,210,2.5,4,7.6,,,,4460,1795,1440,2725,1400,334,5,140,0,ALL,,std man hud 360 roof,
Mazda,CX-30,SUV,Small,Mainstream,P,FWD/AWD,A/M,2020,25000,191,252,8.4,200,2.5,4,8.1,,,,4395,1795,1540,2655,1500,572,5,175,0,ALL,,std man hud 360 roof,
Mazda,CX-5,SUV,Compact,Mainstream,P/H,AWD,A,2026,30000,187,252,8.6,200,2.5,4,8.4,,,,4690,1860,1695,2815,1700,1050,5,210,907,ALL,,std hud 360 roof,Third generation
Mazda,CX-50,SUV,Compact,Mainstream,P/H,AWD,A/CVT,2023,31000,187,252,8.5,200,2.5,4,8.7,,,,4720,1920,1625,2815,1650,891,5,220,1588,NA,,std hud 360 roof,
Mazda,CX-90,SUV,Large,Premium,P/PH,AWD,A,2024,38000,280,450,7.0,210,3.3,6,9.8,42,17.8,,5100,1995,1745,3120,2050,1135,8,190,2268,NA/AU,,std row3 hud 360 roof,
Mazda,MX-5,Convertible,Small,Mainstream,P,RWD,A/M,2016,30000,181,205,5.8,220,2.0,4,8.1,,,,3915,1735,1235,2310,1060,130,2,135,0,ALL,,cp aeb man,Sold as MX-5 Miata in North America
Mazda,CX-60,SUV,Midsize,Premium,P/D/PH,RWD/AWD,A,2022,52000,327,500,5.8,200,2.5,4,1.5,63,17.8,,4745,1890,1680,2870,2050,570,5,180,2500,EU/UK/AU/AS,,std hud 360 roof,EU price converted; WLTP figures
Subaru,Impreza,Hatchback,Compact,Mainstream,P,AWD,CVT,2024,23500,152,197,9.5,190,2.0,4,7.8,,,,4475,1780,1480,2670,1420,585,5,130,0,NA,,std,
Subaru,Crosstrek,SUV,Small,Mainstream,P/H,AWD,CVT,2024,26500,152,197,9.6,190,2.0,4,8.1,,,,4495,1800,1620,2670,1500,565,5,220,680,ALL,,std,
Subaru,Forester,SUV,Compact,Mainstream,P/H,AWD,CVT,2025,30000,180,241,9.0,190,2.5,4,8.7,,,,4655,1830,1730,2670,1600,830,5,220,680,ALL,,std roof,
Subaru,Outback,Wagon,Midsize,Mainstream,P,AWD,CVT,2026,33000,180,241,9.5,190,2.5,4,8.7,,,,4870,1880,1700,2745,1700,920,5,220,1588,NA/AU,,std hud roof,
Subaru,Ascent,SUV,Large,Mainstream,P,AWD,CVT,2019,38000,260,375,7.5,200,2.4,4,10.7,,,,5000,1930,1820,2890,2000,1345,8,220,2268,NA,,std row3 roof,
Subaru,WRX,Sedan,Compact,Mainstream,P,AWD,CVT/M,2022,33000,271,350,5.5,230,2.4,4,10.7,,,,4670,1825,1470,2675,1530,357,5,135,0,NA/AU/AS,,std man,
Subaru,BRZ,Coupe,Small,Mainstream,P,RWD,A/M,2022,31500,228,250,6.3,226,2.4,4,10.2,,,,4265,1775,1310,2575,1280,180,4,130,0,ALL,,cp aeb man,
Subaru,Solterra,SUV,Compact,Mainstream,E,AWD,1,2023,39000,338,338,5.0,160,0,0,,435,74.7,150,4690,1860,1650,2850,2050,680,5,210,680,ALL,,std heatpump roof,
Mitsubishi,Mirage,Hatchback,Mini,Budget,P,FWD,CVT,2014,17000,78,100,12.8,170,1.2,3,6.0,,,,3795,1665,1510,2450,920,487,5,160,0,NA/AS,D,cp aeb,US sales ended after the 2024 model year
Mitsubishi,Outlander,SUV,Compact,Mainstream,P/PH,FWD/AWD,CVT,2022,29500,181,245,9.0,190,2.5,4,9.0,61,22.7,50,4710,1860,1745,2705,1650,950,7,213,907,ALL,,std row3 hud 360 roof,
Mitsubishi,Eclipse Cross,SUV,Compact,Mainstream,P/PH,FWD/AWD,CVT,2018,27000,152,250,9.5,195,1.5,4,8.4,,,,4545,1805,1685,2670,1500,650,5,210,680,NA/AU/AS,,std hud 360 roof,
Suzuki,Swift,Hatchback,Small,Budget,P/H,FWD/AWD,CVT/M,2024,20000,82,112,12.5,165,1.2,3,4.4,,,,3860,1735,1495,2450,950,265,5,120,0,EU/UK/AU/AS,,std man,EU price converted
Suzuki,Jimny,SUV,Mini,Budget,P,4WD,A/M,2018,28000,102,130,11.9,145,1.5,4,7.7,,,,3645,1645,1720,2250,1100,85,4,210,1300,EU/UK/AU/AS,,cp aeb man,EU price converted
Suzuki,Vitara,SUV,Small,Mainstream,H,FWD/AWD,A/M,2015,27000,129,235,10.2,190,1.4,4,5.9,,,,4175,1775,1610,2500,1255,375,5,185,1200,EU/UK/AU/AS,,std man roof,EU price converted
Hyundai,Elantra,Sedan,Compact,Mainstream,P/H,FWD,CVT/DCT,2021,22500,147,179,9.0,195,2.0,4,6.7,,,,4710,1825,1420,2720,1290,402,5,140,0,NA/AU/AS,,std,
Hyundai,Sonata,Sedan,Midsize,Mainstream,P/H,FWD/AWD,A,2020,27500,191,247,7.9,200,2.5,4,7.6,,,,4910,1860,1445,2840,1500,453,5,135,0,NA/AS,,std hud 360 roof,
Hyundai,Venue,SUV,Small,Budget,P,FWD,CVT,2020,21000,121,151,10.5,175,1.6,4,7.4,,,,4040,1770,1590,2520,1200,530,5,170,0,NA/AU/AS,,std,
Hyundai,Kona,SUV,Small,Mainstream,P/H,FWD/AWD,A/CVT,2024,25000,147,179,9.2,185,2.0,4,7.4,,,,4350,1825,1585,2660,1350,723,5,170,680,ALL,,std hud 360 roof,
Hyundai,Kona Electric,SUV,Small,Mainstream,E,FWD,1,2024,33000,201,255,7.8,172,0,0,,420,64.8,100,4355,1825,1580,2660,1700,723,5,160,0,ALL,,std heatpump hud 360 roof,
Hyundai,Tucson,SUV,Compact,Mainstream,P/H/PH,FWD/AWD,A,2022,29000,187,241,9.4,190,2.5,4,9.0,53,13.8,,4640,1865,1665,2755,1600,1095,5,210,907,ALL,,std hud 360 roof,
Hyundai,Santa Fe,SUV,Midsize,Mainstream,P/H/PH,FWD/AWD,A,2024,34500,277,422,7.0,210,2.5,4,9.8,,,,4830,1900,1720,2815,1850,1150,7,180,2041,ALL,,std row3 hud 360 roof,
Hyundai,Palisade,SUV,Large,Mainstream,P/H,FWD/AWD,A,2026,39500,287,352,7.5,200,3.5,6,11.2,,,,5060,1980,1795,2970,2000,1270,8,200,2268,NA/AU/AS,,std row3 hud 360 roof,Second generation
Hyundai,Santa Cruz,Pickup,Compact,Mainstream,P,FWD/AWD,A,2022,29000,191,245,9.0,180,2.5,4,9.4,,,,4970,1905,1695,3005,1750,,5,220,2268,NA,,std,
Hyundai,Ioniq 5,SUV,Compact,Mainstream,E,RWD/AWD,1,2022,43000,225,350,7.3,185,0,0,,512,84,235,4655,1890,1605,3000,1950,770,5,160,1588,ALL,,std heatpump hud 360 roof,
Hyundai,Ioniq 6,Sedan,Midsize,Mainstream,E,RWD/AWD,1,2023,38600,225,350,7.4,185,0,0,,547,77.4,235,4855,1880,1495,2950,1900,401,5,125,0,ALL,,std heatpump hud 360 roof,
Hyundai,Ioniq 9,SUV,Large,Mainstream,E,RWD/AWD,1,2026,59000,215,350,8.4,190,0,0,,539,110.3,230,5060,1980,1790,3130,2600,1320,7,175,2268,ALL,,std row3 heatpump hud 360 roof,
Hyundai,i10,Hatchback,Mini,Budget,P,FWD,A/M,2020,18500,79,96,13.8,171,1.0,3,5.2,,,,3670,1680,1480,2425,960,252,5,150,0,EU/UK/AS,,std man,EU price converted
Kia,K4,Sedan,Compact,Mainstream,P,FWD,CVT/A,2025,22000,147,179,9.0,195,2.0,4,6.9,,,,4710,1850,1420,2720,1330,416,5,140,0,NA/AS,,std hud 360 roof,
Kia,K5,Sedan,Midsize,Mainstream,P,FWD/AWD,A,2021,27500,191,247,7.8,210,1.6,4,7.6,,,,4905,1860,1445,2850,1450,453,5,135,0,NA/AS,,std hud 360 roof,
Kia,Seltos,SUV,Small,Mainstream,P,FWD/AWD,CVT/A,2021,25000,147,179,9.5,185,2.0,4,7.6,,,,4385,1800,1620,2630,1400,750,5,185,680,NA/AU/AS,,std roof,
Kia,Niro,SUV,Small,Mainstream,H/PH/E,FWD,DCT/1,2023,27500,139,265,9.8,165,1.6,4,4.4,,,,4420,1825,1545,2720,1450,640,5,160,590,ALL,,std hud roof,
Kia,Sportage,SUV,Compact,Mainstream,P/H/PH,FWD/AWD,A,2023,29000,187,241,9.4,185,2.5,4,9.0,55,13.8,,4660,1865,1680,2755,1600,1110,5,210,1134,ALL,,std hud 360 roof,
Kia,Sorento,SUV,Midsize,Mainstream,P/H/PH,FWD/AWD,A/DCT,2021,32000,191,247,8.5,200,2.5,4,9.0,,,,4815,1900,1700,2815,1750,1090,7,200,1588,ALL,,std row3 hud 360 roof,
Kia,Telluride,SUV,Large,Mainstream,P,FWD/AWD,A,2020,37000,291,355,7.2,200,3.8,6,10.7,,,,5000,1990,1750,2900,1950,1300,8,210,2268,NA,,std row3 hud 360 roof,
Kia,Carnival,Minivan,Large,Mainstream,P/H,FWD,A,2022,37000,287,355,7.5,200,3.5,6,11.2,,,,5155,1995,1775,3090,2000,2460,8,170,1588,ALL,,std row3 hud 360 roof,
Kia,EV3,SUV,Small,Mainstream,E,FWD,1,2024,39000,204,283,7.5,170,0,0,,605,81.4,128,4300,1850,1560,2680,1850,460,5,170,1000,EU/UK/AU/AS,,std heatpump hud,EU price converted; WLTP range
Kia,EV6,SUV,Compact,Mainstream,E,RWD/AWD,1,2022,43000,225,350,7.2,185,0,0,,512,84,235,4695,1890,1550,2900,1950,680,5,160,1588,ALL,,std heatpump hud 360 roof,
Kia,EV9,SUV,Large,Mainstream,E,RWD/AWD,1,2024,55000,215,350,8.0,185,0,0,,488,99.8,210,5010,1980,1755,3100,2500,1230,7,175,2268,ALL,,std row3 heatpump hud 360 roof,
Genesis,G70,Sedan,Compact,Premium,P,RWD/AWD,A,2019,41500,300,422,6.0,240,2.5,4,9.8,,,,4685,1850,1400,2835,1650,297,5,130,0,NA/AU/AS,,std hud 360 roof,
Genesis,G80,Sedan,Midsize,Premium,P/E,RWD/AWD,A,2021,54000,300,422,6.0,240,2.5,4,10.2,,,,4995,1925,1465,3010,1850,424,5,135,0,ALL,,std hud 360 roof,
Genesis,GV60,SUV,Compact,Premium,E,RWD/AWD,1,2023,52000,225,350,7.5,185,0,0,,470,84,235,4515,1890,1580,2900,2000,432,5,160,0,ALL,,std heatpump hud 360 roof,
Genesis,GV70,SUV,Compact,Premium,P/E,AWD,A,2022,46000,300,422,6.0,240,2.5,4,10.2,,,,4715,1910,1630,2875,1900,813,5,180,1588,ALL,,std hud 360 roof,
Genesis,GV80,SUV,Midsize,Luxury,P,AWD,A,2021,59000,300,422,6.8,240,2.5,4,11.2,,,,4945,1975,1715,2955,2150,991,7,185,2722,ALL,,std row3 hud 360 roof,
Ford,Mustang,Coupe,Midsize,Mainstream,P,RWD,A/M,2024,32500,315,475,5.5,230,2.3,4,9.8,,,,4810,1915,1400,2720,1680,382,4,130,0,ALL,,std man,
Ford,Mustang Mach-E,SUV,Compact,Mainstream,E,RWD/AWD,1,2021,38000,260,430,6.4,180,0,0,,418,72,150,4725,1880,1620,2985,2000,820,5,145,680,ALL,,std heatpump roof,
Ford,Bronco,SUV,Midsize,Mainstream,P,4WD,A/M,2021,40000,300,441,7.0,180,2.3,4,11.8,,,,4810,1930,1850,2950,2100,1000,5,250,1588,NA,,std man roof,
Ford,Bronco Sport,SUV,Compact,Mainstream,P,AWD,A,2021,32000,180,258,9.0,180,1.5,3,9.4,,,,4385,1890,1785,2670,1600,920,5,200,998,NA,,std roof,
Ford,Escape,SUV,Compact,Mainstream,P/H,FWD/AWD,A/CVT,2020,29500,180,258,8.7,190,1.5,3,8.4,,,,4585,1880,1680,2710,1550,1060,5,190,907,NA,,std hud roof,Sold as the Kuga in Europe
Ford,Explorer,SUV,Large,Mainstream,P,RWD/AWD,A,2020,40000,300,420,6.5,200,2.3,4,9.8,,,,5050,2005,1775,3025,2000,1355,7,200,2404,NA,,std row3 hud 360 roof,
Ford,Expedition,SUV,Large,Mainstream,P,RWD/4WD,A,2025,61000,400,650,6.0,180,3.5,6,13.1,,,,5340,2030,1950,3110,2600,1800,8,210,4354,NA,,std row3 hud 360 roof,
Ford,Maverick,Pickup,Compact,Budget,H/P,FWD/AWD,CVT/A,2022,28000,191,210,7.7,180,2.5,4,5.9,,,,5070,1845,1745,3075,1630,,5,210,1814,NA,,std,
Ford,Ranger,Pickup,Midsize,Mainstream,P/D,RWD/4WD,A,2024,34000,270,420,7.0,180,2.3,4,11.2,,,,5370,1920,1880,3270,2000,,5,225,3402,ALL,,std 360,
Ford,F-150,Pickup,Large,Mainstream,P/H,RWD/4WD,A,2021,38000,325,542,6.0,180,2.7,6,11.8,,,,5890,2030,1960,3685,2050,,5,240,6350,NA,,std hud 360 roof,
Ford,F-150 Lightning,Pickup,Large,Mainstream,E,AWD,1,2022,55000,452,1050,4.5,175,0,0,,386,98,155,5915,2030,1990,3700,2950,,5,225,3500,NA,,std hud 360 roof,Ford has announced the end of production: check stock
Ford,Puma,SUV,Small,Mainstream,P/H,FWD,A/M,2020,30000,125,210,9.8,191,1.0,3,5.6,,,,4215,1805,1555,2590,1300,456,5,165,1200,EU/UK/AU,,std man hud roof,EU price converted
Chevrolet,Trax,SUV,Small,Budget,P,FWD,A,2024,21500,137,220,9.0,180,1.2,3,7.8,,,,4540,1825,1560,2700,1400,721,5,175,0,NA/AS,,std,
Chevrolet,Trailblazer,SUV,Small,Budget,P,FWD/AWD,CVT/A,2021,24000,137,220,9.5,180,1.3,3,7.6,,,,4410,1810,1650,2640,1450,728,5,175,454,NA/AS,,std roof,
Chevrolet,Equinox,SUV,Compact,Mainstream,P,FWD/AWD,A/CVT,2025,29000,175,275,8.5,190,1.5,4,8.7,,,,4655,1900,1700,2730,1600,845,5,205,680,NA/AS,,std roof,
Chevrolet,Equinox EV,SUV,Compact,Mainstream,E,FWD/AWD,1,2024,35000,213,328,7.9,160,0,0,,513,85,150,4840,1905,1640,3095,2150,742,5,180,680,NA,,std heatpump hud roof 360,
Chevrolet,Blazer EV,SUV,Midsize,Mainstream,E,FWD/RWD/AWD,1,2024,45000,288,333,6.5,180,0,0,,539,85,150,4880,1985,1650,3095,2250,725,5,185,1588,NA,,std heatpump roof hud 360,
Chevrolet,Bolt,SUV,Small,Budget,E,FWD,1,2026,29000,210,270,7.0,150,0,0,,410,65,150,4300,1770,1610,2675,1700,470,5,150,0,NA,,std heatpump,2027 model year; figures from launch announcements
Chevrolet,Traverse,SUV,Large,Mainstream,P,FWD/AWD,A,2024,40000,328,441,6.8,180,2.5,4,10.7,,,,5205,2000,1795,3070,2050,1640,8,190,2268,NA,,std row3 hud 360 roof,
Chevrolet,Tahoe,SUV,Large,Mainstream,P/D,RWD/4WD,A,2021,59000,355,519,7.0,180,5.3,8,14.7,,,,5350,2060,1925,3070,2550,2055,8,200,3765,NA/AS,,std row3 hud 360 roof,
Chevrolet,Suburban,SUV,Large,Mainstream,P/D,RWD/4WD,A,2021,62000,355,519,7.3,180,5.3,8,14.7,,,,5735,2060,1925,3405,2650,2655,8,200,3765,NA/AS,,std row3 hud 360 roof,
Chevrolet,Colorado,Pickup,Midsize,Mainstream,P,RWD/4WD,A,2023,31000,237,350,7.6,180,2.7,4,11.2,,,,5410,1905,1790,3335,1950,,5,240,3493,NA,,std 360,
Chevrolet,Silverado 1500,Pickup,Large,Mainstream,P/D,RWD/4WD,A,2019,38000,310,583,6.5,180,2.7,4,11.8,,,,5885,2063,1918,3745,2050,,6,220,6000,NA/AS,,std hud 360 roof,
Chevrolet,Corvette,Coupe,Small,Premium,P/H,RWD/AWD,DCT,2020,70000,490,637,3.3,296,6.2,8,12.4,,,,4630,1935,1235,2720,1530,357,2,95,0,ALL,,std hud 360 roof,
Chevrolet,Malibu,Sedan,Midsize,Mainstream,P,FWD,CVT,2016,26000,160,250,8.5,200,1.5,4,8.1,,,,4935,1855,1465,2830,1450,445,5,140,0,NA,D,std,Production ended in late 2024
GMC,Terrain,SUV,Compact,Mainstream,P,FWD/AWD,A,2025,33000,175,275,8.7,190,1.5,4,9.0,,,,4655,1905,1730,2730,1650,840,5,205,680,NA,,std roof,
GMC,Acadia,SUV,Large,Mainstream,P,FWD/AWD,A,2024,43000,328,441,6.8,180,2.5,4,10.7,,,,5150,2000,1810,3070,2100,1610,7,200,2268,NA,,std row3 hud 360 roof,
GMC,Yukon,SUV,Large,Premium,P/D,RWD/4WD,A,2021,62000,355,519,7.0,180,5.3,8,14.7,,,,5335,2060,1940,3070,2600,2055,8,200,3765,NA/AS,,std row3 hud 360 roof,
GMC,Sierra 1500,Pickup,Large,Mainstream,P/D,RWD/4WD,A,2019,40000,310,583,6.5,180,2.7,4,11.8,,,,5885,2063,1918,3745,2100,,6,220,6000,NA/AS,,std hud 360 roof,
GMC,Hummer EV,Pickup,Large,Luxury,E,AWD,1,2022,90000,570,,4.5,170,0,0,,504,205,350,5507,2201,2032,3445,4100,,5,290,3402,NA,,std hud 360 roof,Also sold as an SUV
Cadillac,CT5,Sedan,Midsize,Premium,P,RWD/AWD,A,2020,50000,237,350,7.0,210,2.0,4,9.4,,,,4925,1880,1450,2950,1650,337,5,130,0,NA/AS,,std hud 360 roof,
Cadillac,Optiq,SUV,Compact,Premium,E,AWD,1,2025,54000,300,480,6.0,180,0,0,,486,85,150,4820,1910,1640,2955,2350,742,5,160,680,NA/EU/AS,,std heatpump hud 360 roof,
Cadillac,Lyriq,SUV,Midsize,Premium,E,RWD/AWD,1,2023,58000,365,440,5.7,190,0,0,,526,102,190,5005,1980,1625,3095,2550,793,5,150,1588,NA/EU/AS,,std heatpump hud 360 roof,
Cadillac,Escalade,SUV,Large,Luxury,P/D,RWD/4WD,A,2021,90000,420,624,6.0,180,6.2,8,15.7,,,,5380,2060,1950,3070,2700,2055,8,205,3765,NA/AS,,std row3 hud 360 roof,
Buick,Envista,SUV,Small,Budget,P,FWD,A,2024,23500,137,220,9.2,180,1.2,3,7.8,,,,4640,1815,1560,2700,1400,580,5,165,0,NA/AS,,std roof,
Buick,Enclave,SUV,Large,Premium,P,FWD/AWD,A,2025,46000,328,441,6.8,180,2.5,4,10.7,,,,5235,2000,1800,3070,2100,1640,7,190,2268,NA,,std row3 hud 360 roof,
Jeep,Wrangler,SUV,Midsize,Mainstream,P,4WD,A/M,2018,33000,285,353,7.5,160,3.6,6,12.4,,,,4880,1895,1850,3010,2000,900,5,250,1588,ALL,,std man roof,
Jeep,Grand Cherokee,SUV,Midsize,Mainstream,P,RWD/4WD,A,2022,39000,293,353,7.5,200,3.6,6,11.8,,,,4915,1980,1795,2965,2000,1070,5,215,2812,ALL,,std hud 360 roof,
Jeep,Compass,SUV,Compact,Mainstream,P,AWD,A,2017,29000,200,300,8.5,190,2.0,4,9.4,,,,4400,1820,1640,2635,1550,770,5,210,907,NA/EU/UK/AS,,std roof,
Jeep,Gladiator,Pickup,Midsize,Mainstream,P,4WD,A/M,2020,39000,285,353,7.5,160,3.6,6,13.1,,,,5590,1895,1850,3490,2100,,5,250,3470,NA,,std man roof,
Jeep,Wagoneer S,SUV,Midsize,Premium,E,AWD,1,2025,60000,500,840,4.0,190,0,0,,491,100.5,270,4885,1950,1645,2930,2600,860,5,175,907,NA,,std heatpump hud 360 roof,
Ram,1500,Pickup,Large,Mainstream,P,RWD/4WD,A,2025,42000,420,635,6.0,180,3.0,6,12.4,,,,5920,2085,1970,3570,2400,,6,220,5070,NA,,std hud 360 roof,
Dodge,Hornet,SUV,Compact,Mainstream,P,AWD,A,2023,31000,268,400,6.5,200,2.0,4,10.2,,,,4530,1835,1620,2635,1650,770,5,150,907,NA,,std hud roof,
Dodge,Durango,SUV,Large,Mainstream,P,RWD/AWD,A,2011,41000,295,353,7.5,190,3.6,6,11.8,,,,5110,1925,1800,3040,2200,1225,7,205,2812,NA,,std row3 roof,
Dodge,Charger Daytona,Coupe,Large,Mainstream,E,AWD,1,2024,60000,496,545,4.7,220,0,0,,495,94,183,5250,2020,1490,3075,2650,1090,5,140,0,NA,,std hud roof,
Chrysler,Pacifica,Minivan,Large,Mainstream,P/PH,FWD/AWD,A,2017,42000,287,355,7.5,180,3.6,6,10.7,51,16,,5185,2020,1775,3090,2050,2480,8,130,1633,NA,,std row3 360 roof,
Tesla,Model 3,Sedan,Midsize,Premium,E,RWD/AWD,1,2024,37000,271,,6.1,201,0,0,,517,69,175,4720,1850,1440,2875,1760,594,5,138,1000,ALL,,acc aeb heatpump roof,No CarPlay; Standard trim figures
Tesla,Model Y,SUV,Midsize,Premium,E,RWD/AWD,1,2025,40000,299,,7.2,201,0,0,,517,69,175,4790,1920,1625,2890,1900,854,5,167,1588,ALL,,acc aeb heatpump roof,No CarPlay; Standard trim figures
Tesla,Model S,Sedan,Large,Luxury,E,AWD,1,2012,85000,670,,3.2,250,0,0,,660,100,250,5020,1990,1430,2960,2100,793,5,130,0,ALL,,acc aeb heatpump roof,No CarPlay
Tesla,Model X,SUV,Large,Luxury,E,AWD,1,2015,90000,670,,3.9,250,0,0,,565,100,250,5050,2000,1680,2965,2400,1000,7,160,2268,ALL,,row3 acc aeb heatpump roof,No CarPlay
Tesla,Cybertruck,Pickup,Large,Premium,E,AWD,1,2024,80000,600,,4.1,180,0,0,,523,123,325,5683,2200,1790,3660,3100,,5,315,4990,NA,,acc aeb heatpump roof,No CarPlay
Rivian,R1T,Pickup,Midsize,Premium,E,AWD,1,2022,71000,533,829,4.5,177,0,0,,434,92.5,220,5515,2015,1990,3450,3100,,5,370,4990,NA,,acc aeb heatpump 360 roof,No CarPlay
Rivian,R1S,SUV,Large,Premium,E,AWD,1,2022,77000,533,829,4.5,177,0,0,,434,92.5,220,5100,2080,1965,3075,3200,1300,7,370,3500,NA,,row3 acc aeb heatpump 360 roof,No CarPlay
Lucid,Air,Sedan,Large,Luxury,E,RWD/AWD,1,2022,70000,430,550,4.5,200,0,0,,676,84,200,4975,1940,1410,2960,2350,627,5,140,0,NA/EU/AS,,std heatpump 360 roof,
Lucid,Gravity,SUV,Large,Luxury,E,AWD,1,2025,94900,828,,3.5,250,0,0,,724,120,400,5034,1990,1655,3090,2700,1040,7,150,2722,NA,,std row3 heatpump 360 roof,Grand Touring figures
Lincoln,Corsair,SUV,Compact,Premium,P,FWD/AWD,A,2020,41000,250,373,7.8,200,2.0,4,9.8,,,,4590,1890,1630,2710,1700,790,5,185,907,NA/AS,,std hud 360 roof,
Lincoln,Nautilus,SUV,Midsize,Premium,P/H,AWD,A,2024,52000,250,373,7.5,200,2.0,4,10.2,,,,4910,1950,1735,2900,2000,1060,5,200,1588,NA/AS,,std hud 360 roof,
Lincoln,Aviator,SUV,Large,Luxury,P,RWD/AWD,A,2020,58000,400,563,6.0,210,3.0,6,11.8,,,,5065,2020,1760,3025,2200,1185,7,195,3039,NA/AS,,std row3 hud 360 roof,
Lincoln,Navigator,SUV,Large,Luxury,P,4WD,A,2025,98000,440,691,6.0,180,3.5,6,13.8,,,,5335,2030,1945,3110,2700,1900,8,210,3855,NA/AS,,std row3 hud 360 roof,
Volkswagen,Polo,Hatchback,Small,Mainstream,P,FWD,A/M,2017,23000,95,175,10.8,187,1.0,3,5.4,,,,4075,1750,1450,2550,1180,351,5,140,1100,EU/UK/AU/AS,,std man,EU price converted
Volkswagen,Golf,Hatchback,Compact,Mainstream,P/D/PH,FWD,A/M,2020,33000,116,220,9.8,202,1.5,4,5.4,,,,4280,1790,1460,2630,1300,381,5,135,1500,EU/UK/AU/AS,,std man hud roof,EU price converted
Volkswagen,Golf GTI,Hatchback,Compact,Mainstream,P,FWD,DCT,2022,33500,241,370,5.9,250,2.0,4,8.4,,,,4290,1790,1460,2630,1450,380,5,135,0,ALL,,std hud roof,
Volkswagen,Jetta,Sedan,Compact,Mainstream,P,FWD,A/M,2019,23000,158,250,8.0,205,1.5,4,6.7,,,,4700,1800,1460,2685,1350,400,5,140,0,NA,,std man roof,
Volkswagen,Taos,SUV,Small,Mainstream,P,FWD/AWD,A/DCT,2022,25000,174,250,8.3,195,1.5,4,7.6,,,,4465,1840,1630,2680,1450,790,5,175,0,NA,,std roof,
Volkswagen,Tiguan,SUV,Compact,Mainstream,P,FWD/AWD,A,2025,30500,201,280,7.8,205,2.0,4,9.0,,,,4540,1840,1660,2680,1650,1050,5,190,680,ALL,,std hud roof 360,Third generation
Volkswagen,Atlas,SUV,Large,Mainstream,P,FWD/AWD,A,2018,39000,269,370,7.6,200,2.0,4,10.2,,,,5100,1990,1780,2980,2000,1570,7,205,2268,NA,,std row3 hud 360 roof,
Volkswagen,Passat,Wagon,Midsize,Mainstream,P/D/PH,FWD/AWD,DCT,2024,45000,150,250,9.2,220,1.5,4,5.6,120,19.7,50,4920,1850,1500,2840,1550,690,5,135,2000,EU/UK/AU,,std hud roof 360,EU price converted; WLTP figures
Volkswagen,ID.3,Hatchback,Compact,Mainstream,E,RWD,1,2020,40000,204,310,7.3,160,0,0,,427,59,165,4260,1810,1560,2770,1800,385,5,140,0,EU/UK/AU/AS,,std heatpump hud roof,EU price converted; WLTP range
Volkswagen,ID.4,SUV,Compact,Mainstream,E,RWD/AWD,1,2021,40000,282,545,6.0,160,0,0,,467,77,175,4585,1850,1630,2765,2050,850,5,165,1225,ALL,,std heatpump hud roof,
Volkswagen,ID. Buzz,Minivan,Large,Premium,E,RWD/AWD,1,2025,61500,282,560,7.5,160,0,0,,377,86,200,4960,1985,1925,3240,2700,1340,7,165,1000,ALL,,std row3 heatpump hud roof 360,
Audi,A3,Sedan,Compact,Premium,P,FWD/AWD,DCT,2022,39000,201,300,6.8,210,2.0,4,8.1,,,,4495,1815,1425,2635,1450,300,5,130,0,ALL,,std hud roof,
Audi,A5,Sedan,Midsize,Premium,P,FWD/AWD,DCT,2025,47000,268,400,5.7,250,2.0,4,9.0,,,,4830,1860,1440,2900,1700,445,5,130,1600,ALL,,std hud 360 roof,Replaces the A4
Audi,A6 e-tron,Sedan,Midsize,Premium,E,RWD/AWD,1,2025,66000,375,565,5.4,210,0,0,,600,94.9,270,4930,1925,1470,2950,2200,502,5,130,1800,ALL,,std heatpump hud 360 roof,
Audi,e-tron GT,Sedan,Large,Luxury,E,AWD,1,2021,107000,670,740,3.4,245,0,0,,480,97,320,4990,1965,1395,2900,2300,405,5,120,0,ALL,,std heatpump hud 360 roof,
Audi,Q3,SUV,Compact,Premium,P,AWD,A/DCT,2019,39000,228,350,7.0,210,2.0,4,9.4,,,,4485,1855,1615,2680,1700,670,5,175,0,ALL,,std hud 360 roof,
Audi,Q4 e-tron,SUV,Compact,Premium,E,RWD/AWD,1,2022,50000,282,545,6.5,180,0,0,,463,77,175,4590,1865,1630,2765,2150,520,5,165,1200,ALL,,std heatpump hud 360 roof,
Audi,Q5,SUV,Midsize,Premium,P/PH,AWD,DCT,2025,52000,268,400,6.0,240,2.0,4,9.8,,,,4715,1900,1655,2820,1950,520,5,195,2000,ALL,,std hud 360 roof,Third generation
Audi,Q6 e-tron,SUV,Midsize,Premium,E,RWD/AWD,1,2025,64000,422,590,5.5,210,0,0,,495,94.9,270,4770,1940,1695,2900,2350,526,5,175,2400,ALL,,std heatpump hud 360 roof,
Audi,Q7,SUV,Large,Premium,P,AWD,A,2017,61000,261,370,7.0,210,2.0,4,10.7,,,,5065,1970,1740,2995,2100,865,7,205,2495,ALL,,std row3 hud 360 roof,
BMW,2 Series Gran Coupe,Sedan,Compact,Premium,P,FWD/AWD,DCT,2025,40000,241,400,6.2,250,2.0,4,8.4,,,,4545,1800,1445,2670,1500,430,5,130,0,ALL,,std hud roof,
BMW,3 Series,Sedan,Midsize,Premium,P/D/PH,RWD/AWD,A,2019,46000,255,400,5.8,250,2.0,4,8.1,,,,4710,1825,1440,2850,1600,480,5,140,1600,ALL,,std hud 360 roof,
BMW,5 Series,Sedan,Midsize,Premium,P/PH,RWD/AWD,A,2024,58000,255,400,6.2,250,2.0,4,8.7,,,,5060,1900,1515,2995,1800,520,5,135,2000,ALL,,std hud 360 roof,
BMW,i4,Sedan,Midsize,Premium,E,RWD/AWD,1,2022,57000,335,430,5.7,190,0,0,,510,81.1,205,4785,1850,1450,2855,2100,470,5,125,1600,ALL,,std heatpump hud 360 roof,
BMW,i5,Sedan,Midsize,Luxury,E,RWD/AWD,1,2024,68000,335,430,5.7,193,0,0,,475,81.2,205,5060,1900,1505,2995,2200,490,5,135,1500,ALL,,std heatpump hud 360 roof,
BMW,X1,SUV,Compact,Premium,P/D/PH/E,AWD,DCT,2023,42000,241,400,6.4,250,2.0,4,8.7,,,,4500,1845,1640,2690,1700,540,5,200,1800,ALL,,std hud 360 roof,
BMW,X3,SUV,Compact,Premium,P/D/PH,AWD,A,2025,50000,255,400,6.2,250,2.0,4,9.0,,,,4755,1920,1660,2865,1900,570,5,205,2268,ALL,,std hud 360 roof,Fourth generation
BMW,X5,SUV,Midsize,Luxury,P/D/PH,AWD,A,2019,67000,375,520,5.5,250,3.0,6,10.2,64,25.7,,4935,2005,1765,2975,2200,650,5,215,3500,ALL,,std row3 hud 360 roof,Third row optional
BMW,X7,SUV,Large,Luxury,P,AWD,A,2019,84000,375,520,5.6,250,3.0,6,11.2,,,,5180,2000,1835,3105,2450,1375,7,220,3500,ALL,,std row3 hud 360 roof,
BMW,iX,SUV,Midsize,Luxury,E,AWD,1,2022,87000,536,765,4.6,200,0,0,,547,109.1,195,4955,1965,1695,3000,2600,500,5,200,2500,ALL,,std heatpump hud 360 roof,
BMW,Z4,Convertible,Small,Premium,P,RWD,A/M,2019,54000,255,400,5.2,250,2.0,4,8.1,,,,4325,1865,1305,2470,1490,281,2,115,0,ALL,,std man hud,
Mini,Cooper,Hatchback,Small,Premium,P/E,FWD,DCT,2025,29000,161,250,7.5,225,1.5,3,6.9,,,,3875,1745,1455,2495,1250,210,4,130,0,ALL,,std hud roof,
Mini,Countryman,SUV,Compact,Premium,P/E,AWD,DCT,2025,39000,241,400,6.2,240,2.0,4,8.4,,,,4445,1845,1660,2690,1650,460,5,190,1800,ALL,,std hud roof 360,
Mercedes-Benz,CLA,Sedan,Compact,Premium,E/H,RWD/AWD,1,2025,48000,268,335,6.6,210,0,0,,600,85,320,4720,1855,1470,2790,2050,405,5,120,0,ALL,,std heatpump hud 360 roof,Electric version first; range approximate
Mercedes-Benz,C-Class,Sedan,Midsize,Premium,P/D/PH,RWD/AWD,A,2022,49000,255,400,6.0,250,2.0,4,8.4,,,,4750,1820,1440,2865,1700,455,5,125,1800,ALL,,std hud 360 roof,
Mercedes-Benz,E-Class,Sedan,Midsize,Luxury,P/D/PH,RWD/AWD,A,2024,63000,255,400,6.2,250,2.0,4,8.7,,,,4950,1880,1470,2960,1850,540,5,130,2100,ALL,,std hud 360 roof,
Mercedes-Benz,S-Class,Sedan,Large,Luxury,P/D/PH,RWD/AWD,A,2021,120000,442,560,4.9,250,3.0,6,10.2,,,,5290,1955,1505,3215,2200,550,5,130,0,ALL,,std hud 360 roof,
Mercedes-Benz,EQS,Sedan,Large,Luxury,E,RWD/AWD,1,2022,105000,355,568,6.2,210,0,0,,628,118,200,5225,1925,1515,3210,2500,610,5,125,0,ALL,,std heatpump hud 360 roof,
Mercedes-Benz,GLA,SUV,Compact,Premium,P/D,FWD/AWD,DCT,2021,44000,221,350,6.7,240,2.0,4,8.4,,,,4410,1835,1610,2730,1600,435,5,165,1800,ALL,,std hud 360 roof,
Mercedes-Benz,GLC,SUV,Midsize,Premium,P/D/PH,AWD,A,2023,50000,255,400,6.2,240,2.0,4,9.0,,,,4715,1890,1640,2890,1850,620,5,200,2268,ALL,,std hud 360 roof,
Mercedes-Benz,GLE,SUV,Midsize,Luxury,P/D/PH,AWD,A,2020,64000,255,400,7.0,210,2.0,4,10.2,,,,4925,2020,1795,2995,2150,630,7,205,3500,ALL,,std row3 hud 360 roof,
Mercedes-Benz,GLS,SUV,Large,Luxury,P/D,AWD,A,2020,90000,375,500,5.9,250,3.0,6,11.8,,,,5210,1955,1825,3135,2500,890,7,215,3500,ALL,,std row3 hud 360 roof,
Mercedes-Benz,G-Class,SUV,Midsize,Luxury,P/D/E,4WD,A,2019,148000,443,560,5.2,210,3.0,6,13.8,,,,4825,1930,1975,2890,2560,667,5,240,3500,ALL,,std hud 360 roof,
Porsche,911,Coupe,Small,Luxury,P/H,RWD/AWD,DCT/M,2019,125000,388,450,4.1,294,3.0,6,10.7,,,,4540,1850,1300,2450,1500,132,4,110,0,ALL,,std man roof,
Porsche,718 Cayman,Coupe,Small,Luxury,P,RWD,DCT/M,2016,72000,300,380,5.1,275,2.0,4,10.2,,,,4380,1800,1295,2475,1400,275,2,120,0,NA/AU/AS,,std man,EU sales ended in 2024; production ending
Porsche,Macan Electric,SUV,Compact,Luxury,E,RWD/AWD,1,2024,78000,402,563,5.7,220,0,0,,507,95,270,4785,1940,1620,2895,2300,624,5,190,2000,ALL,,std heatpump hud 360 roof,
Porsche,Cayenne,SUV,Midsize,Luxury,P/PH,AWD,A,2018,92000,348,500,5.7,248,3.0,6,11.8,,,,4930,1985,1700,2895,2100,772,5,210,3500,ALL,,std hud 360 roof,
Porsche,Taycan,Sedan,Midsize,Luxury,E,RWD/AWD,1,2020,100000,402,410,4.8,230,0,0,,470,89,320,4965,1965,1380,2900,2100,450,4,125,0,ALL,,std heatpump hud 360 roof,
Volvo,EX30,SUV,Small,Premium,E,RWD/AWD,1,2024,44900,268,343,5.1,180,0,0,,407,64,153,4235,1835,1550,2650,1850,318,5,175,1600,ALL,,std heatpump 360 roof,
Volvo,XC40,SUV,Compact,Premium,P,AWD,A,2018,42000,247,350,6.3,180,2.0,4,8.7,,,,4440,1865,1650,2700,1650,460,5,210,1600,ALL,,std 360 roof,
Volvo,XC60,SUV,Midsize,Premium,P/PH,AWD,A,2018,47000,247,360,6.6,180,2.0,4,9.0,56,18.8,,4710,1900,1660,2865,1900,483,5,215,2250,ALL,,std hud 360 roof,
Volvo,XC90,SUV,Large,Premium,P/PH,AWD,A,2015,58000,247,360,7.0,180,2.0,4,9.8,,,,4955,1960,1775,2985,2050,1000,7,235,2700,ALL,,std row3 hud 360 roof,
Volvo,EX90,SUV,Large,Luxury,E,AWD,1,2025,80000,402,770,5.7,180,0,0,,499,104,250,5040,1960,1745,2985,2800,655,7,230,2200,ALL,,std row3 heatpump hud 360 roof,
Polestar,2,Sedan,Compact,Premium,E,RWD/AWD,1,2021,50000,299,490,6.2,205,0,0,,515,79,205,4610,1860,1480,2735,2000,405,5,150,1500,ALL,,std heatpump 360 roof,
Polestar,3,SUV,Midsize,Luxury,E,RWD/AWD,1,2024,74000,489,840,4.9,210,0,0,,507,111,250,4900,1970,1615,2985,2580,484,5,210,2200,ALL,,std heatpump hud 360 roof,
Polestar,4,SUV,Midsize,Premium,E,RWD/AWD,1,2025,57000,272,343,7.1,200,0,0,,480,94,200,4840,2008,1535,2999,2230,526,5,160,2000,ALL,,std heatpump hud 360 roof,No rear window (camera mirror)
Land Rover,Defender,SUV,Midsize,Premium,P/D/PH,AWD,A,2020,62000,296,400,7.7,191,2.0,4,11.8,,,,5018,2008,1967,3022,2300,900,7,225,3500,ALL,,std row3 hud 360 roof,Defender 110 figures
Land Rover,Range Rover Evoque,SUV,Compact,Premium,P/D/PH,AWD,A,2019,51000,246,365,7.6,230,2.0,4,9.4,,,,4371,1904,1649,2681,1800,472,5,212,1800,ALL,,std hud 360 roof,
Land Rover,Range Rover Sport,SUV,Midsize,Luxury,P/D/PH,AWD,A,2023,85000,395,550,5.7,242,3.0,6,11.2,,,,4946,2047,1820,2997,2350,647,5,216,3000,ALL,,std hud 360 roof,
Land Rover,Range Rover,SUV,Large,Luxury,P/D/PH,AWD,A,2022,110000,395,550,5.8,242,3.0,6,11.8,,,,5052,2047,1870,2997,2500,818,5,219,3500,ALL,,std row3 hud 360 roof,Seven seats in the long version
Jaguar,F-Pace,SUV,Midsize,Premium,P/D/PH,AWD,A,2016,58000,247,365,6.9,217,2.0,4,9.8,,,,4747,1936,1664,2874,1850,613,5,213,2400,ALL,D,std hud 360 roof,Jaguar paused new-car sales for its electric relaunch: buy used
Jaguar,I-Pace,SUV,Midsize,Premium,E,AWD,1,2018,72000,394,696,4.8,200,0,0,,396,84.7,104,4682,2011,1565,2990,2200,656,5,174,750,ALL,D,std heatpump hud 360 roof,Production ended in 2024: buy used
Alfa Romeo,Giulia,Sedan,Midsize,Premium,P,RWD/AWD,A,2017,46000,280,400,5.7,240,2.0,4,9.4,,,,4643,1860,1436,2820,1550,480,5,135,1600,ALL,,std roof,
Alfa Romeo,Stelvio,SUV,Midsize,Premium,P/D,AWD,A,2018,49000,280,400,5.7,230,2.0,4,10.2,,,,4687,1903,1671,2818,1750,525,5,200,1600,ALL,,std roof,
Alfa Romeo,Tonale,SUV,Compact,Premium,H/PH,FWD/AWD,A,2023,45000,285,,6.0,206,1.3,4,8.1,53,15.5,,4530,1840,1600,2636,1850,385,5,170,1000,ALL,,std roof,Plug-in hybrid figures
Fiat,500e,Hatchback,Mini,Mainstream,E,FWD,1,2021,33000,117,220,9.0,150,0,0,,240,37.3,85,3630,1685,1530,2320,1350,185,4,130,0,ALL,,std heatpump roof,
Fiat,Grande Panda,Hatchback,Small,Budget,H/E,FWD,A/DCT,2025,21000,110,205,11.2,160,1.2,3,5.0,,,,3999,1760,1570,2540,1200,412,5,165,900,EU/UK,,std,EU price converted
Fiat,600,SUV,Small,Mainstream,H/E,FWD,DCT/1,2024,28000,145,230,9.0,194,1.2,3,5.0,,,,4171,1781,1523,2557,1350,385,5,180,1000,EU/UK,,std,EU price converted
Maserati,Grecale,SUV,Compact,Luxury,P/E,AWD,A,2023,70000,300,450,5.6,240,2.0,4,9.4,,,,4846,1948,1670,2901,1870,570,5,190,2000,ALL,,std hud 360 roof,
Ferrari,296 GTB,Coupe,Small,Exotic,PH,RWD,DCT,2022,320000,819,740,2.9,330,3.0,6,12.0,25,7.45,,4565,1958,1187,2600,1470,,2,100,0,ALL,,cp,
Lamborghini,Urus,SUV,Large,Exotic,PH,AWD,A,2025,260000,789,950,3.4,312,4.0,8,13.0,60,25.9,,5123,2022,1638,3003,2505,616,5,160,3500,ALL,,std hud 360 roof,Urus SE plug-in hybrid
Peugeot,208,Hatchback,Small,Mainstream,P/H/E,FWD,A/M,2019,23000,100,205,9.9,188,1.2,3,5.4,,,,4055,1745,1430,2540,1100,352,5,140,1150,EU/UK/AU/AS,,std man,EU price converted
Peugeot,2008,SUV,Small,Mainstream,P/H/E,FWD,A/M,2020,28000,130,230,9.5,200,1.2,3,5.6,,,,4300,1770,1550,2610,1250,434,5,165,1200,EU/UK/AU/AS,,std man roof,EU price converted
Peugeot,308,Hatchback,Compact,Mainstream,P/D/H/PH/E,FWD,A/M,2021,32000,130,230,9.7,210,1.2,3,5.6,,,,4367,1852,1441,2675,1300,412,5,135,1400,EU/UK/AU/AS,,std man hud roof 360,EU price converted
Peugeot,3008,SUV,Compact,Mainstream,H/PH/E,FWD/AWD,A,2024,40000,136,230,10.2,201,1.2,3,5.7,,,,4542,1895,1641,2739,1580,520,5,180,1600,EU/UK/AU/AS,,std hud 360 roof,EU price converted
Peugeot,5008,SUV,Midsize,Mainstream,H/PH/E,FWD/AWD,A,2024,45000,136,230,10.5,201,1.2,3,5.9,,,,4791,1895,1694,2900,1700,748,7,180,1600,EU/UK/AU/AS,,std row3 hud 360 roof,EU price converted
Renault,Clio,Hatchback,Small,Budget,P/H,FWD,A/M,2019,22000,90,160,12.2,180,1.0,3,5.4,,,,4050,1798,1440,2583,1100,391,5,140,1000,EU/UK/AS,,std man,EU price converted; new generation from 2026
Renault,Captur,SUV,Small,Mainstream,P/H,FWD,A/M,2020,28000,145,205,10.6,170,1.6,4,4.7,,,,4239,1797,1575,2639,1300,440,5,170,750,EU/UK/AU/AS,,std man,EU price converted
Renault,5 E-Tech,Hatchback,Small,Mainstream,E,FWD,1,2024,30000,150,245,7.9,150,0,0,,410,52,100,3920,1770,1500,2540,1450,326,5,140,0,EU/UK/AS,,std heatpump,EU price converted; WLTP range
Renault,Megane E-Tech,Hatchback,Compact,Mainstream,E,FWD,1,2022,40000,220,300,7.4,160,0,0,,450,60,130,4200,1768,1505,2685,1650,440,5,135,900,EU/UK/AU/AS,,std heatpump roof,EU price converted; WLTP range
Renault,Austral,SUV,Compact,Mainstream,H,FWD/AWD,A,2022,38000,200,410,8.4,175,1.2,3,4.6,,,,4510,1825,1645,2667,1550,555,5,200,1500,EU/UK/AS,,std hud 360 roof,EU price converted
Renault,Scenic E-Tech,SUV,Compact,Mainstream,E,FWD,1,2024,45000,220,300,7.9,170,0,0,,620,87,150,4470,1864,1571,2785,1890,545,5,160,1500,EU/UK/AS,,std heatpump hud 360 roof,EU price converted; WLTP range
Dacia,Spring,Hatchback,Mini,Budget,E,FWD,1,2024,18000,65,113,13.7,125,0,0,,225,26.8,30,3700,1583,1519,2423,980,308,4,150,0,EU/UK,,cp aeb,EU price converted; WLTP range
Dacia,Sandero,Hatchback,Small,Budget,P,FWD,A/M,2021,15000,100,170,11.6,183,1.0,3,5.3,,,,4088,1848,1499,2604,1100,410,5,133,1100,EU/UK,,cp aeb man,EU price converted
Dacia,Duster,SUV,Compact,Budget,P/H,FWD/4WD,A/M,2024,23000,130,230,10.0,180,1.2,3,5.7,,,,4343,1813,1656,2657,1300,472,5,217,1500,EU/UK/AS,,cp aeb man 360,EU price converted
Dacia,Jogger,Wagon,Compact,Budget,P/H,FWD,A/M,2022,22000,110,200,11.2,183,1.0,3,5.6,,,,4547,1784,1632,2897,1250,708,7,200,1200,EU/UK/AS,,cp aeb man row3,EU price converted
Citroen,C3,Hatchback,Small,Budget,P/H/E,FWD,A/M,2024,20000,100,205,10.6,180,1.2,3,5.6,,,,4015,1755,1577,2540,1150,310,5,163,1000,EU/UK/AS,,std man,EU price converted
Citroen,C4,Hatchback,Compact,Mainstream,P/D/H/E,FWD,A/M,2020,30000,130,230,9.4,205,1.2,3,5.8,,,,4375,1800,1525,2670,1300,380,5,156,1200,EU/UK/AS,,std man hud,EU price converted
Opel,Corsa,Hatchback,Small,Mainstream,P/H/E,FWD,A/M,2019,24000,100,205,9.9,188,1.2,3,5.4,,,,4060,1765,1435,2538,1100,309,5,140,1200,EU/UK,,std man,Sold as Vauxhall in the UK; EU price converted
Opel,Astra,Hatchback,Compact,Mainstream,P/D/PH/E,FWD,A/M,2022,31000,130,230,9.7,210,1.2,3,5.6,,,,4374,1860,1470,2675,1300,422,5,135,1400,EU/UK,,std man 360,Sold as Vauxhall in the UK; EU price converted
Opel,Mokka,SUV,Small,Mainstream,P/H/E,FWD,A/M,2021,29000,130,230,9.2,200,1.2,3,5.6,,,,4151,1791,1534,2557,1250,350,5,175,1200,EU/UK,,std man,Sold as Vauxhall in the UK; EU price converted
Skoda,Fabia,Hatchback,Small,Budget,P,FWD,A/M,2021,21000,95,175,10.7,195,1.0,3,5.3,,,,4108,1780,1459,2564,1150,380,5,140,1100,EU/UK/AS,,std man,EU price converted
Skoda,Octavia,Hatchback,Compact,Mainstream,P/D/H,FWD/AWD,A/M,2020,32000,150,250,8.5,230,1.5,4,5.5,,,,4698,1829,1470,2686,1350,600,5,135,1600,EU/UK/AU/AS,,std man hud 360 roof,EU price converted; estate version too
Skoda,Superb,Wagon,Midsize,Mainstream,P/D/PH,FWD/AWD,DCT,2024,42000,150,250,9.1,225,1.5,4,5.9,,,,4902,1849,1482,2841,1550,690,5,140,2000,EU/UK/AU/AS,,std hud 360 roof,EU price converted
Skoda,Kodiaq,SUV,Midsize,Mainstream,P/D/PH,FWD/AWD,DCT,2024,42000,150,250,9.7,206,1.5,4,6.5,,,,4758,1864,1659,2791,1650,910,7,190,2300,EU/UK/AU/AS,,std row3 hud 360 roof,EU price converted
Skoda,Elroq,SUV,Compact,Mainstream,E,RWD,1,2025,37000,204,310,8.0,160,0,0,,400,59,165,4488,1884,1625,2765,1900,470,5,180,1000,EU/UK/AS,,std heatpump hud,EU price converted; WLTP range
Skoda,Enyaq,SUV,Compact,Mainstream,E,RWD/AWD,1,2021,47000,286,545,6.7,180,0,0,,580,77,135,4658,1879,1616,2768,2100,585,5,160,1200,EU/UK/AU/AS,,std heatpump hud 360 roof,EU price converted; WLTP range
Seat,Ibiza,Hatchback,Small,Budget,P,FWD,A/M,2017,21000,95,175,10.9,186,1.0,3,5.2,,,,4059,1780,1444,2564,1150,355,5,140,1100,EU/UK/AS,,std man,EU price converted
Cupra,Formentor,SUV,Compact,Premium,P/PH,FWD/AWD,DCT,2020,40000,150,250,8.9,207,1.5,4,6.2,,,,4450,1839,1511,2680,1450,450,5,150,1600,EU/UK/AU/AS,,std 360 roof,EU price converted
Cupra,Born,Hatchback,Compact,Mainstream,E,RWD,1,2021,40000,231,310,6.6,160,0,0,,425,59,165,4322,1809,1540,2767,1800,385,5,140,0,EU/UK/AU/AS,,std heatpump roof,EU price converted; WLTP range
BYD,Dolphin,Hatchback,Compact,Mainstream,E,FWD,1,2021,33000,204,310,7.0,160,0,0,,427,60.4,88,4290,1770,1570,2700,1650,345,5,120,0,EU/UK/AU/AS,,std heatpump 360 roof,EU price converted; WLTP range
BYD,Atto 3,SUV,Compact,Mainstream,E,FWD,1,2022,38000,204,310,7.3,160,0,0,,420,60.5,88,4455,1875,1615,2720,1750,440,5,175,0,EU/UK/AU/AS,,std heatpump 360 roof,EU price converted; WLTP range
BYD,Seal,Sedan,Midsize,Mainstream,E,RWD/AWD,1,2022,45000,313,360,5.9,180,0,0,,570,82.5,150,4800,1875,1460,2920,2050,400,5,120,0,EU/UK/AU/AS,,std heatpump hud 360 roof,EU price converted; WLTP range
BYD,Seal U DM-i,SUV,Midsize,Mainstream,PH,FWD/AWD,CVT,2024,42000,218,300,8.9,170,1.5,4,5.5,80,18.3,18,4775,1890,1670,2765,1950,552,5,180,1300,EU/UK/AU/AS,,std 360 roof,EU price converted; WLTP figures
MG,MG4,Hatchback,Compact,Budget,E,RWD/AWD,1,2022,33000,170,250,7.7,160,0,0,,350,51,117,4287,1836,1504,2705,1650,363,5,140,500,EU/UK/AU/AS,,std,EU price converted; WLTP range
MG,ZS,SUV,Small,Budget,H/E,FWD,A,2024,25000,197,,8.7,170,1.5,4,5.0,,,,4430,1818,1635,2610,1450,443,5,160,500,EU/UK/AU/AS,,std 360 roof,EU price converted
MG,HS,SUV,Compact,Mainstream,P/PH,FWD,A,2024,32000,170,250,9.5,190,1.5,4,7.4,,,,4655,1890,1664,2765,1600,507,5,155,1500,EU/UK/AU/AS,,std 360 roof,EU price converted
Smart,#1,SUV,Small,Premium,E,RWD/AWD,1,2023,41000,272,343,6.7,180,0,0,,440,66,150,4270,1822,1636,2750,1800,313,5,155,1600,EU/UK/AU/AS,,std heatpump hud 360 roof,EU price converted; WLTP range
"""
