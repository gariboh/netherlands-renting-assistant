import os
from funda import Funda
from parariusScraper import Pararius
from notifier import send_email
from sheets_db import load_seen_ids, save_listing

PRICE = [1100, 1400]
HEADERS = {}

CITIES = [
    {"funda": "amsterdam",  "pararius": "amsterdam",  "display": "Amsterdam"},
    {"funda": "den-haag",   "pararius": "den-haag",   "display": "Den Haag"},
    {"funda": "rotterdam",  "pararius": "rotterdam",  "display": "Rotterdam"},
]

if __name__ == '__main__':
    seen_ids = load_seen_ids()

    for city in CITIES:
        for SvcClass in [Funda, Pararius]:
            try:
                scraper = SvcClass(city["funda"] if SvcClass is Funda else city["pararius"], PRICE, header=HEADERS)
                houses = scraper.Run()
            except Exception as e:
                print(f"Scraper error ({SvcClass.__name__}, {city['display']}): {e}")
                continue

            for house in houses:
                if str(house.id) in seen_ids:
                    continue
                house.city = city["display"]
                try:
                    send_email(house)
                    save_listing(house)
                    seen_ids.add(str(house.id))
                    print(f"Notified: {house.address} in {house.city} €{house.price}")
                except Exception as e:
                    print(f"Error processing {house.id}: {e}")
