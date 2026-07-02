import os
import sys
import json
import time
import requests
from bs4 import BeautifulSoup

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
HEADERS = {"User-Agent": "TimeCapsuleRAG/1.0 (student project)"}
MONTH_NAMES = ["", "January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]


def fetch_month(year: int, month: int) -> list[dict]:
    month_name = MONTH_NAMES[month]
    url = f"https://en.wikipedia.org/wiki/Portal:Current_events/{month_name}_{year}"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    entries = []
    for day_block in soup.find_all("div", class_="vevent"):
        date_tag = day_block.find(class_="summary")
        date_text = date_tag.get_text(strip=True) if date_tag else None
        bullets = [li.get_text(" ", strip=True) for li in day_block.find_all("li")]
        if bullets:
            entries.append({"date_raw": date_text, "year": year, "month": month,
                             "events": bullets, "source": "wikipedia_current_events"})
    return entries


def main():
    year, month = int(sys.argv[1]), int(sys.argv[2])
    print(f"Fetching Wikipedia events for {MONTH_NAMES[month]} {year} ...")
    entries = fetch_month(year, month)
    print(f"Got {len(entries)} day-entries.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"wiki_{year}_{month:02d}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"Saved to {out_path}")
    time.sleep(1)


if __name__ == "__main__":
    main()
