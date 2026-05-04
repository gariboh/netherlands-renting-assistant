import re
import requests
from bs4 import BeautifulSoup
from model import House
from interface import RentProviderInterface

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

class Funda(RentProviderInterface):
    BASE = "https://www.funda.nl"

    def __init__(self, city='amsterdam', price=[0, 9000], header={}):
        super().__init__(city, price)
        self._session = requests.Session()
        self._session.headers.update({**HEADERS, **header})

    def _warm_session(self):
        """Visit homepage first to get session cookies."""
        try:
            self._session.get(self.BASE + "/", timeout=15)
        except Exception:
            pass

    def Run(self):
        city_slug = self._city.lower().replace(" ", "-")
        self._warm_session()
        results = []
        seen = set()

        for page in range(1, 4):
            url = f"{self.BASE}/huur/{city_slug}/" if page == 1 else f"{self.BASE}/huur/{city_slug}/p{page}/"
            try:
                resp = self._session.get(url, timeout=15)
                print(f"  [Funda] HTTP {resp.status_code} {url}", flush=True)
                if resp.status_code != 200:
                    print(f"  [Funda] Response snippet: {resp.text[:300]}", flush=True)
                    break
                soup = BeautifulSoup(resp.text, "lxml")

                title = soup.title.string if soup.title else "none"
                print(f"  [Funda] Page title: {title}", flush=True)

                anchors = soup.find_all("a", attrs={"data-object-url-tracking": "resultlist"})
                if not anchors:
                    anchors = [
                        a for a in soup.find_all("a", href=True)
                        if re.match(r'^/huur/[^/]+/(appartement|huis|studio|kamer)-\d+', a.get("href", ""))
                    ]
                print(f"  [Funda] Found {len(anchors)} listing links on page {page}", flush=True)
                if not anchors:
                    break

                hrefs = list({a["href"] for a in anchors if a.get("href")})
                for href in hrefs:
                    if href in seen:
                        continue
                    seen.add(href)
                    try:
                        full_url = self.BASE + href
                        r2 = self._session.get(full_url, timeout=15)
                        soup2 = BeautifulSoup(r2.text, "lxml")
                        price_match = re.search(r'€\s*([\d.,]+)\s*(?:/mnd|per maand)', soup2.get_text())
                        if not price_match:
                            continue
                        rent = int(price_match.group(1).replace(".", "").replace(",", ""))
                        if not self._isPriceMatched(rent):
                            continue
                        addr_el = soup2.find("h1") or soup2.find("title")
                        address = addr_el.get_text(strip=True).split("|")[0].strip() if addr_el else href
                        area_match = re.search(r'(\d+)\s*m²', soup2.get_text())
                        area = f"{area_match.group(1)} m²" if area_match else ""
                        listing_id = re.search(r'-(\d{8,})-', href)
                        listing_id = listing_id.group(1) if listing_id else href
                        results.append(House(listing_id, full_url, address, rent, area))
                    except Exception as e:
                        print(f"  [Funda] Listing error {href}: {e}", flush=True)
                        continue

            except Exception as e:
                print(f"  [Funda] Page error p{page}: {e}", flush=True)
                break

        return results
