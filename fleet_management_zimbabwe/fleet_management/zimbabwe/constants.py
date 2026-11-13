"""Zimbabwe fleet constants. Statutory rates are configurable in ZIMRA Fleet Settings;
these are defaults only."""

DEFAULT_VAT_RATE = 15.5  # Finance Act (No. 7) 2025, effective 1 Jan 2026
LOCAL_CURRENCY = "ZWG"
FOREIGN_CURRENCY = "USD"

# Vehicle Documents Type records seeded on migrate
VEHICLE_DOCUMENT_TYPES = [
    "ZINARA Vehicle Licence",
    "VID Certificate of Fitness",
    "Operator's Licence (Road Service Permit)",
    "Third Party Insurance Certificate",
    "COMESA Yellow Card",
    "Cross-Border Road Access Fee Receipt",
    "ZIMRA Carbon Tax Certificate",
    "Vehicle Registration Book (CVR)",
    "Goods Vehicle Operator Permit (Cross-Border)",
    "Fire Extinguisher / Reflective Triangle Compliance",
]

# Trip Location records: (description, is_local_border, is_international_border)
BORDER_POSTS = [
    ("Beitbridge Border Post (ZW/ZA)", 0, 1),
    ("Chirundu Border Post (ZW/ZM)", 0, 1),
    ("Kazungula Border Post (ZW/BW/ZM)", 0, 1),
    ("Plumtree Border Post (ZW/BW)", 0, 1),
    ("Forbes Border Post (ZW/MZ)", 0, 1),
    ("Nyamapanda Border Post (ZW/MZ)", 0, 1),
    ("Victoria Falls Border Post (ZW/ZM)", 0, 1),
    ("Mount Selinda (Espungabera) Border Post (ZW/MZ)", 0, 1),
    ("Sango Border Post (ZW/MZ)", 0, 1),
    ("Kariba Border Post (ZW/ZM)", 0, 1),
]

CURRENCIES = ["ZWG", "USD"]
