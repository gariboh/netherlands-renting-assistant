import re
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from playwright_stealth import Stealth
from bs4 import BeautifulSoup
from model import House
from interface import RentProviderInterface


class Pararius(RentProviderInterface):
    BASE = "https://www.pararius.com"

    def __init__(self, city='amsterdam', price=[0, 9000], header={}):
        super().__init__(city, price)
        self._min_price = price[0]
        self._max_price = price[1]

    def Run(self):
        base_url = f"{self.BASE}/apartments/{self._city}/{self._min_price}-{self._max_price}"
        results = []
        page_num = 1

        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            ctx = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="nl-NL",
                viewport={"width": 1280, "height": 900},
            )
            pw_page = ctx.new_page()
            Stealth().apply_stealth_sync(pw_page)

            while True:
                url = base_url if page_num == 1 else f"{base_url}/page-{page_num}"
                print(f"  [Pararius] Fetching {url}", flush=True)
                try:
                    pw_page.goto(url, wait_until="load", timeout=45000)
                    if "just a moment" in (pw_page.title() or "").lower():
                        print("  [Pararius] Challenge page, waiting...", flush=True)
                        pw_page.wait_for_timeout(6000)
                except PWTimeout:
                    print(f"  [Pararius] Timeout on page {page_num}", flush=True)
                    break

                html = pw_page.content()
                soup = BeautifulSoup(html, "lxml")
                title = soup.title.string if soup.title else "none"
                print(f"  [Pararius] Page title: {title}", flush=True)

                items = soup.find_all("li", class_=lambda c: c and "search-list__item--listing" in c)
                print(f"  [Pararius] {len(items)} listing items on page {page_num}", flush=True)
                if not items:
                    print(f"  [Pararius] Page snippet: {soup.get_text()[:300]}", flush=True)
                    break

                for item in items:
                    try:
                        link_el = (
                            item.find("a", href=re.compile(r'/(appartement|woning|kamer|studio)-te-huur/'))
                            or item.find("a", href=re.compile(r'^/[a-z]+-te-huur/'))
                            or (item.find("h2").find("a") if item.find("h2") else None)
                            or (item.find("h3").find("a") if item.find("h3") else None)
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
                        area_match = re.search(r'(\d+)\s*m2', area_text)
                        area = f"{area_match.group(1)} m2" if area_match else ""

                        listing_id = link_el["href"].rstrip("/").split("/")[-1]
                        results.append(House(listing_id, link, name, rent, area))
                    except Exception as e:
                        print(f"  [Pararius] Parse error: {e} | {item.get_text()[:80]}", flush=True)
                        continue

                pagination = soup.find("ul", class_=lambda c: c and "pagination" in c)
                if not pagination or not pagination.find("li", class_=lambda c: c and "next" in c):
                    break
                page_num += 1

            browser.close()

        return results
