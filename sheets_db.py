import json
import os
from datetime import date
from google.oauth2.service_account import Credentials
import gspread

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def _client():
    creds_json = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS"])
    creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    return gspread.authorize(creds)

def load_seen_ids() -> set:
    gc = _client()
    ws = gc.open_by_key(os.environ["GOOGLE_SHEET_ID"]).worksheet("seen_listings")
    rows = ws.get_all_values()
    return {row[0] for row in rows[1:] if row and row[0]}

def save_listing(house):
    gc = _client()
    ws = gc.open_by_key(os.environ["GOOGLE_SHEET_ID"]).worksheet("seen_listings")
    ws.append_row([
        str(house.id),
        house.URL,
        getattr(house, "city", ""),
        str(house.price),
        str(date.today())
    ])
