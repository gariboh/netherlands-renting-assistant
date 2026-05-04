import os
import sys

PASS = "PASS"
FAIL = "FAIL"


def test_sheets():
    print("\n--- Test 1: Google Sheets connection ---", flush=True)
    try:
        from sheets_db import load_seen_ids
        ids = load_seen_ids()
        print(f"  Loaded {len(ids)} seen IDs from sheet", flush=True)
        print(f"  {PASS}: Google Sheets connection works", flush=True)
        return True
    except Exception as e:
        print(f"  {FAIL}: {e}", flush=True)
        return False


def test_email():
    print("\n--- Test 2: Email (Gmail SMTP) ---", flush=True)
    try:
        import smtplib, ssl
        sender = os.environ["EMAIL_SENDER"]
        password = os.environ["EMAIL_PASSWORD"]
        recipient = os.environ["EMAIL_RECIPIENT"]
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(sender, password)
            from email.mime.text import MIMEText
            msg = MIMEText("NL Rental Bot test email - SMTP connection OK.")
            msg["Subject"] = "[NL Rental Bot] Test email"
            msg["From"] = sender
            msg["To"] = recipient
            smtp.sendmail(sender, recipient, msg.as_string())
        print(f"  Test email sent to {recipient}", flush=True)
        print(f"  {PASS}: Gmail SMTP works", flush=True)
        return True
    except Exception as e:
        print(f"  {FAIL}: {e}", flush=True)
        return False


def test_pararius():
    print("\n--- Test 3: Pararius (Amsterdam) ---", flush=True)
    try:
        from parariusScraper import Pararius
        scraper = Pararius("amsterdam", [500, 9000])
        houses = scraper.Run()
        print(f"  Found {len(houses)} listings", flush=True)
        if houses:
            h = houses[0]
            print(f"  First listing: id={h.id} price={h.price}", flush=True)
        if len(houses) > 0:
            print(f"  {PASS}: Pararius returns listings", flush=True)
        else:
            print(f"  {FAIL}: Pararius returned 0 listings (check HTML parsing)", flush=True)
        return len(houses) > 0
    except Exception as e:
        print(f"  {FAIL}: {e}", flush=True)
        return False


def test_funda():
    print("\n--- Test 4: Funda (Amsterdam, Playwright) ---", flush=True)
    try:
        from funda import Funda
        scraper = Funda("amsterdam", [500, 9000])
        houses = scraper.Run()
        print(f"  Found {len(houses)} listings", flush=True)
        if houses:
            h = houses[0]
            print(f"  First listing: id={h.id} price={h.price}", flush=True)
        if len(houses) > 0:
            print(f"  {PASS}: Funda returns listings", flush=True)
        else:
            print(f"  {FAIL}: Funda returned 0 listings (check page title printed above)", flush=True)
        return len(houses) > 0
    except Exception as e:
        print(f"  {FAIL}: {e}", flush=True)
        return False


if __name__ == "__main__":
    results = {
        "Google Sheets": test_sheets(),
        "Gmail SMTP": test_email(),
        "Pararius": test_pararius(),
        "Funda": test_funda(),
    }

    print("\n========== SUMMARY ==========", flush=True)
    all_pass = True
    for name, ok in results.items():
        status = PASS if ok else FAIL
        print(f"  {status}  {name}", flush=True)
        if not ok:
            all_pass = False

    sys.exit(0 if all_pass else 1)