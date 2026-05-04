import re
import requests
from bs4 import BeautifulSoup
from model import House
from interface import RentProviderInterface

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

class Pararius(RentProviderInterface):
    BASE = "https://www.pararius.com/apartments"

    def __init__(self, city='amsterdam', price=[0, 9000], header={}):
        super().__init__(city, price)
        self._min_price = price[0]
        self._max_price = price[1]
        self._header = {"User-Agent": UA, **header}

    def Run(self):
        base_url = f"{self.BASE}/{self._city}/{self._min_price}-{self._max_price}"
        results = []
        page = 1

        while True:
            url = base_url if page == 1 else f"{base_url}/page-{page}"
            try:
                resp = requests.get(url, headers=self._header, timeout=15)
                if resp.status_code != 200:
                    break
                soup = BeautifulSoup(resp.text, "lxml")

                listings = soup.find_all("li", class_="search-list__item search-list__item--listing")
                if not listings:
                    break

                for item in listings:
                    try:
                        link = "https://www.pararius.com" + item.section.h2.a["href"]
                        name = item.section.h2.a.get_text(strip=True)
                        price_text = item.section.find("div", class_="listing-search-item__price").get_text(strip=True)
                        rent = int(price_text.split("per")[0].split("€")[1].strip().replace(",", ""))
                        features = item.section.find("div", class_="listing-search-item__features")
                        area = features.ul.find_all("li")[0].get_text(strip=True) if features else ""
                        listing_id = re.search(r'[a-f0-9-]{20,}', link)
                        listing_id = listing_id.group() if listing_id else link
                        results.append(House(listing_id, link, name, rent, area))
                    except Exception:
                        continue

                pagination = soup.find("ul", class_="pagination__list")
                if not pagination:
                    break
                if not pagination.find("li", class_="pagination__item--next"):
                    break
                page += 1

            except Exception as e:
                print(f"Pararius error p{page}: {e}")
                break

        return results
