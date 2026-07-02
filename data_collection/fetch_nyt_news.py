import os
import sys
import json
import time
import requests
NYT_API_KEY = os.environ.get("NYT_API_KEY", "")
BASE_URL = "https://api.nytimes.com/svc/archive/v1/{year}/{month}.json"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def fetch_month(year: int, month: int) -> list[dict]:
    if NYT_API_KEY == "PASTE_YOUR_KEY_HERE":
        raise ValueError("Get a free key at https://developer.nytimes.com/ and set NYT_API_KEY.")

    url = BASE_URL.format(year=year, month=month)
    resp = requests.get(url, params={"api-key": NYT_API_KEY}, timeout=30)
    resp.raise_for_status()
    docs = resp.json().get("response", {}).get("docs", [])

    cleaned = []
    for d in docs:
        cleaned.append({
            "date": d.get("pub_date", "")[:10],
            "headline": d.get("headline", {}).get("main", ""),
            "abstract": d.get("abstract", ""),
            "section": d.get("section_name", ""),
            "source": "nyt",
        })
    return cleaned


def main():
    year, month = int(sys.argv[1]), int(sys.argv[2])
    print(f"Fetching NYT articles for {year}-{month:02d} ...")
    articles = fetch_month(year, month)
    print(f"Got {len(articles)} articles.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"nyt_{year}_{month:02d}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"Saved to {out_path}")
    time.sleep(1)


if __name__ == "__main__":
    main()
