AGENCY_KEYWORDS = [
    # Generic descriptors
    "staffing", "recruiting", "recruitment", "talent solutions",
    "talent acquisition", "consulting", "consultants", "placement",
    "contract staffing", "temp agency", "workforce solutions",
    # Known national agencies
    "robert half", "randstad", "insight global", "teksystems",
    "kforce", "apex group", "addison group", "experis", "manpower",
    "adecco", "spherion", "kelly services", "aerotek", "cintas",
    # Offshore/outsourcing firms that staff analysts
    "infosys", "cognizant", "wipro", "tata consultancy", "tcs",
    "hcl technologies", "capgemini", "accenture federal",
]


def detect_agency(company_name: str, description: str = "") -> tuple[bool, str | None]:
    """Return (is_agency, reason) based on company name and description."""
    text = f"{company_name} {description}".lower()
    for kw in AGENCY_KEYWORDS:
        if kw in text:
            return True, kw
    return False, None
