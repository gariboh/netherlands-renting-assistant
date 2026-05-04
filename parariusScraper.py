import re
import cloudscraper
from bs4 import BeautifulSoup
from model import House
from interface import RentProviderInterface

# Shared scraper so all city requests reuse the same session/cookies
_scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
)

class Pararius(RentProviderInterface):
    BASE = "https://www.pararius.com"

    def __init__(self, city='amsterdam', price=[0, 9000], header={}):
        super().__init__(city, price)
        self._min_price = price[0]
        self._max_price = price[1]

    def Run(self):
        base_url = f"{self.BASE}/apartments/{self._city}/{self._min_price}-{self._max_price}"
        results = []
        page = 1

        while True:
            url = base_url if page == 1 else f"{base_url}/page-{page}"
            try:
                resp = _scraper.get(url, timeout=30)
                print(f"  [Pararius] HTTP {resp.status_code} {url}", flush=True)
                if resp.status_code != 200:
                    print(f"  [Pararius] Blocked: {resp.text[:200]}", flush=True)
                    break
                soup = BeautifulSoup(resp.text, "lxml")

                items = soup.find_all("li", class_=lambda c: c and "search-list__item--listing" in c)
                print(f"  [Pararius] {len(items)} listing elements on page {page}", flush=True)
                if not items:
                    print(f"  [Pararius] Page snippet: {resp.text[300:700]}", flush=True)
                    break

                for item in items:
                    try:
                        # Flexible link finding — handles changed HTML structure
                        link_el = (
                            item.find("a", href=re.compile(r'/(appartement|woning|kamer|studio)-te-huur/'))
                            or item.find("a", href=re.compile(r'^/[a-z]+-te-huur/'))
                            or item.find("h2").find("a") if item.find("h2") else None
                            or item.find("h3").find("a") if item.find("h3") else None
                        )
                        if not link_el:
                            continue
                        link = self.BASE + link_el["href"]
                        name = link_el.get_text(strip=True) or link

                        price_el = item.find(class_=re.compile(r'price'))
                        price_text = price_el.get_text(strip=True) if price_el else ""
                        price_match = re.search(r'[\d.,]{3,}', price_text.replace(".", "").replace(",", ""))
                        if not price_match:
                            m = re.search(r'€\s*([\d.]+)', price_text)
                            if not m:
                                continue
                            rent = int(m.group(1).replace(".", ""))
                        else:
                            rent = int(price_match.group().replace(".", "").replace(",", ""))

                        area_text = item.get_text()
                        area_match = re.search(r'(\d+)\s*m²', area_text)
                        area = f"{area_match.group(1)} m²" if area_match else ""

                        listing_id = link_el["href"].rstrip("/").split("/")[-1]
                        results.append(House(listing_id, link, name, rent, area))
                    except Exception as e:
                        print(f"  [Pararius] Parse error: {e} | {item.get_text()[:80]}", flush=True)
                        continue

                pagination = soup.find("ul", class_=lambda c: c and "pagination" in c)
                if not pagination or not pagination.find("li", class_=lambda c: c and "next" in c):
                    break
                page += 1

            except Exception as e:
                print(f"  [Pararius] Request error p{page}: {e}", flush=True)
                break

        return results
