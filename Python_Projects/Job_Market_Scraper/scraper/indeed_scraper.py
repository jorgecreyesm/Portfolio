import json
import re
from urllib.parse import urlencode, urljoin
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

BASE_URL = "https://www.indeed.com"
SEARCH_URL = f"{BASE_URL}/jobs"


class IndeedScraper(BaseScraper):

    def search(self, query: str, location: str = "", pages: int = 3) -> list[dict]:
        results = []
        for page in range(pages):
            params = {"q": query, "l": location, "sort": "date", "start": page * 15}
            print(f"  Fetching page {page + 1}/{pages}: {query!r}")
            resp = self.get(SEARCH_URL, params=params)
            if resp is None:
                continue
            soup = BeautifulSoup(resp.text, "lxml")
            cards = self._parse_cards(soup)
            print(f"    Found {len(cards)} listings")
            results.extend(cards)
        return results

    # ------------------------------------------------------------------
    # Card parsing (search results page)
    # ------------------------------------------------------------------

    def _parse_cards(self, soup: BeautifulSoup) -> list[dict]:
        cards = []

        # Indeed embeds job data as JSON inside a <script> tag
        json_data = self._extract_json_jobs(soup)
        if json_data:
            return json_data

        # Fallback: parse HTML card elements directly
        for card in soup.select("div.job_seen_beacon, div[data-jk]"):
            job = self._parse_card_html(card)
            if job:
                cards.append(job)
        return cards

    def _extract_json_jobs(self, soup: BeautifulSoup) -> list[dict]:
        """Pull jobs from the embedded JSON blob Indeed injects into the page."""
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, list):
                    parsed = [self._parse_json_entry(e) for e in data if e.get("@type") == "JobPosting"]
                    if parsed:
                        return [p for p in parsed if p]
                elif data.get("@type") == "JobPosting":
                    p = self._parse_json_entry(data)
                    return [p] if p else []
            except (json.JSONDecodeError, AttributeError):
                continue
        return []

    def _parse_json_entry(self, entry: dict) -> dict | None:
        try:
            salary_min, salary_max, salary_type = self._parse_salary_json(
                entry.get("baseSalary", {})
            )
            location_obj = entry.get("jobLocation", {})
            address = location_obj.get("address", {}) if isinstance(location_obj, dict) else {}
            location = ", ".join(filter(None, [
                address.get("addressLocality"),
                address.get("addressRegion"),
            ]))
            return {
                "job_title":    entry.get("title", "").strip(),
                "company_name": entry.get("hiringOrganization", {}).get("name", "").strip(),
                "location":     location,
                "is_remote":    "remote" in entry.get("jobLocationType", "").lower()
                                or "remote" in location.lower(),
                "salary_min":   salary_min,
                "salary_max":   salary_max,
                "salary_type":  salary_type,
                "raw_description": BeautifulSoup(
                    entry.get("description", ""), "lxml"
                ).get_text(" ", strip=True),
                "source_url":   entry.get("url", ""),
                "source":       "indeed",
                "date_posted":  entry.get("datePosted"),
            }
        except Exception:
            return None

    def _parse_card_html(self, card) -> dict | None:
        try:
            title_el = (
                card.select_one("h2.jobTitle a span")
                or card.select_one("h2.jobTitle span[title]")
                or card.select_one("h2 a[data-jk]")
            )
            company_el = (
                card.select_one("[data-testid='company-name']")
                or card.select_one("span.companyName")
            )
            location_el = (
                card.select_one("[data-testid='text-location']")
                or card.select_one("div.companyLocation")
            )
            salary_el = (
                card.select_one(".salary-snippet-container")
                or card.select_one(".metadata.salary-snippet")
            )
            url_el = card.select_one("h2.jobTitle a") or card.select_one("a[data-jk]")

            title    = title_el.get_text(strip=True)    if title_el    else ""
            company  = company_el.get_text(strip=True)  if company_el  else ""
            location = location_el.get_text(strip=True) if location_el else ""
            salary_raw = salary_el.get_text(strip=True) if salary_el   else ""
            href = url_el.get("href", "")               if url_el      else ""
            url  = urljoin(BASE_URL, href) if href else ""

            salary_min, salary_max, salary_type = self._parse_salary_text(salary_raw)

            if not title:
                return None

            return {
                "job_title":         title,
                "company_name":      company,
                "location":          location,
                "is_remote":         "remote" in location.lower(),
                "salary_min":        salary_min,
                "salary_max":        salary_max,
                "salary_type":       salary_type,
                "raw_description":   "",   # description fetched from job page if needed
                "source_url":        url,
                "source":            "indeed",
                "date_posted":       None,
            }
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Salary helpers
    # ------------------------------------------------------------------

    def _parse_salary_text(self, text: str) -> tuple:
        if not text:
            return None, None, None
        text = text.lower().replace(",", "")
        salary_type = "hourly" if "hour" in text else "annual" if "year" in text or "annually" in text else None
        nums = re.findall(r"\$?([\d]+(?:\.\d+)?)", text)
        nums = [float(n) for n in nums]
        if len(nums) == 0:
            return None, None, salary_type
        if len(nums) == 1:
            return nums[0], nums[0], salary_type
        return min(nums), max(nums), salary_type

    def _parse_salary_json(self, salary_obj: dict) -> tuple:
        if not salary_obj:
            return None, None, None
        unit = salary_obj.get("unitText", "").lower()
        salary_type = "hourly" if "hour" in unit else "annual" if "year" in unit else None
        value = salary_obj.get("value", {})
        if isinstance(value, dict):
            lo = value.get("minValue")
            hi = value.get("maxValue")
            return lo, hi, salary_type
        if isinstance(value, (int, float)):
            return float(value), float(value), salary_type
        return None, None, salary_type
