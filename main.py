import os
import sys
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
    print("=== NL Rental Check starting ===", flush=True)

    print("Loading seen IDs from Google Sheets...", flush=True)
    seen_ids = load_seen_ids()
    print(f"Loaded {len(seen_ids)} seen IDs", flush=True)

    for city in CITIES:
        for SvcClass in [Funda, Pararius]:
            city_key = city["funda"] if SvcClass is Funda else city["pararius"]
            print(f"Scraping {SvcClass.__name__} / {city['display']} ({city_key})...", flush=True)
            try:
                scraper = SvcClass(city_key, PRICE, header=HEADERS)
                houses = scraper.Run()
                print(f"  -> {len(houses)} listings found", flush=True)
            except Exception as e:
                print(f"  ERROR: {SvcClass.__name__} {city['display']}: {e}", flush=True)
                import traceback; traceback.print_exc()
                continue

            new_count = 0
            for house in houses:
                if str(house.id) in seen_ids:
                    continue
                house.city = city["display"]
                try:
                    send_email(house)
                    save_listing(house)
                    seen_ids.add(str(house.id))
                    new_count += 1
                    print(f"  Notified: {house.address} €{house.price}", flush=True)
                except Exception as e:
                    print(f"  Notify error {house.id}: {e}", flush=True)
            print(f"  -> {new_count} new listings notified", flush=True)

    print("=== Done ===", flush=True)
