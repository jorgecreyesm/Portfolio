import time
import random
import requests
from fake_useragent import UserAgent

_ua = UserAgent()

HEADERS_BASE = {
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection":      "keep-alive",
    "DNT":             "1",
}


class BaseScraper:
    def __init__(self, delay_range=(2.5, 5.0)):
        self.delay_range = delay_range
        self.session = requests.Session()
        self._rotate_agent()

    def _rotate_agent(self):
        self.session.headers.update({**HEADERS_BASE, "User-Agent": _ua.random})

    def _sleep(self):
        time.sleep(random.uniform(*self.delay_range))

    def get(self, url, params=None, retries=3):
        for attempt in range(retries):
            try:
                self._rotate_agent()
                response = self.session.get(url, params=params, timeout=15)
                response.raise_for_status()
                self._sleep()
                return response
            except requests.RequestException as e:
                wait = 2 ** attempt * random.uniform(1, 2)
                print(f"  [retry {attempt + 1}/{retries}] {e} — waiting {wait:.1f}s")
                time.sleep(wait)
        print(f"  [failed] could not fetch {url}")
        return None
