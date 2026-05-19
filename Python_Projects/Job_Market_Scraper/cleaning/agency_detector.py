AGENCY_KEYWORDS = [
    # Generic descriptors
    "staffing", "recruiting", "recruitment", "talent solutions",
    "talent acquisition", "placement",
    "contract staffing", "temp agency", "workforce solutions",
    # Known national agencies
    "robert half", "randstad", "insight global", "teksystems",
    "kforce", "apex group", "addison group", "experis", "manpower",
    "adecco", "spherion", "kelly services", "aerotek", "cintas",
    # Known scam/fake company names from live data
    "capitalplanholdings", "globalsoft", "data cloud merge",
    "asset capital market", "crossing hurdles", "vinsys",
    "prism data consulting",
]

BODY_SHOP_PHRASES = [
    "we are not the eor",
    "we do not hire for these roles",
    "connecting candidates with employers",
    "pathway program",
    "back to work program",
]


def detect_agency(company_name: str, description: str = "") -> tuple[bool, str | None]:
    """Return (is_agency, reason) based on company name and description."""
    company_lower = company_name.lower()
    desc_lower    = description.lower()

    for kw in AGENCY_KEYWORDS:
        if kw in company_lower:
            return True, kw

    for phrase in BODY_SHOP_PHRASES:
        if phrase in desc_lower:
            return True, phrase

    return False, None
