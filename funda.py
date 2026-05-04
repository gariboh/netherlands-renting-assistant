import re
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from playwright_stealth import Stealth
from bs4 import BeautifulSoup
from model import House
from interface import RentProviderInterface


class Funda(RentProviderInterface):
    BASE = "https://www.funda.nl"

    def __init__(self, city='amsterdam', price=[0, 9000], header={}):
        super().__init__(city, price)

    def Run(self):
        city_slug = self._city.lower().replace(" ", "-")
        results = []
        seen = set()

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

            for page_num in range(1, 4):
                url = (
                    f"{self.BASE}/huur/{city_slug}/"
                    if page_num == 1
                    else f"{self.BASE}/huur/{city_slug}/p{page_num}/"
                )
                print(f"  [Funda] Fetching {url}", flush=True)
                try:
                    pw_page.goto(url, wait_until="load", timeout=45000)
                    if "bijna" in (pw_page.title() or "").lower():
                        print("  [Funda] Challenge page, waiting for resolve...", flush=True)
                        pw_page.wait_for_timeout(8000)
                except PWTimeout:
                    print(f"  [Funda] Timeout on page {page_num}", flush=True)

                html = pw_page.content()
                soup = BeautifulSoup(html, "lxml")
                title = soup.title.string if soup.title else "none"
                print(f"  [Funda] Page title: {title}", flush=True)

                anchors = [
                    a for a in soup.find_all("a", href=True)
                    if re.match(
                        r'/huur/[^/]+/(appartement|huis|studio|kamer|woning)-\d+',
                        a.get("href", "")
                    )
                ]
                print(f"  [Funda] Found {len(anchors)} listing links on page {page_num}", flush=True)

                if not anchors:
                    break

                for a_tag in anchors:
                    href = a_tag.get("href", "")
                    if not href or href in seen:
                        continue
                    seen.add(href)
                    try:
                        full_url = self.BASE + href
                        listing_id_match = re.search(r'-(\d{8,})-', href)
                        listing_id = listing_id_match.group(1) if listing_id_match else href

                        container = a_tag
                        price_match = None
                        for _ in range(7):
                            container = container.parent
                            if container is None:
                                break
                            text = container.get_text(" ", strip=True)
                            price_match = re.search(
                                r'€\s*([\d.]+)\s*/mnd', text, re.IGNORECASE
                            )
                            if price_match:
                                break

                        if not price_match:
                            continue
                        rent = int(price_match.group(1).replace(".", "").replace(",", ""))
                        if not self._isPriceMatched(rent):
                            continue

                        parts = [p for p in href.split("/") if p]
                        addr_text = parts[-1] if parts else href
                        container_text = container.get_text(" ") if container else ""
                        area_match = re.search(r'(\d+)\s*m2', container_text)
                        area = f"{area_match.group(1)} m2" if area_match else ""

                        results.append(House(listing_id, full_url, addr_text, rent, area))
                    except Exception as e:
                        print(f"  [Funda] Error parsing {href}: {e}", flush=True)

            browser.close()

        return results
