import os
import json
import glob
from datetime import datetime
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
def split_long_text(text: str, max_chars: int = 500, overlap: int = 50) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    pieces = []
    start = 0
    while start < len(text):
        end = start + max_chars
        pieces.append(text[start:end])
        start = end - overlap
    return pieces

def chunk_nyt():
    chunks = []
    for path in glob.glob(os.path.join(RAW_DIR, "nyt_*.json")):
        with open(path, encoding="utf-8") as f:
            articles = json.load(f)
        for a in articles:
            if not a.get("date"):
                continue
            text = f"News headline: {a['headline']}. {a.get('abstract', '')}".strip()
            for piece in split_long_text(text):
                chunks.append({"text": piece, "date": a["date"], "source": "nyt"})
    return chunks


def _parse_wiki_date(date_raw, year, month):
    if not date_raw:
        return None
    for fmt in ("%d %B %Y", "%B %d, %Y", "%B %d %Y"):
        try:
            return datetime.strptime(date_raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return f"{year}-{month:02d}-01"


def chunk_wikipedia():
    chunks = []
    for path in glob.glob(os.path.join(RAW_DIR, "wiki_*.json")):
        with open(path, encoding="utf-8") as f:
            entries = json.load(f)
        for e in entries:
            date = _parse_wiki_date(e.get("date_raw"), e["year"], e["month"])
            if not date or not e.get("events"):
                continue
            text = "World events: " + " | ".join(e["events"])
            for piece in split_long_text(text):
                chunks.append({"text": piece, "date": date, "source": "wikipedia_current_events"})
    return chunks


def chunk_billboard(top_n=10):
    csv_path = os.path.join(RAW_DIR, "billboard.csv")
    if not os.path.exists(csv_path):
        return []

    df = pd.read_csv(csv_path)
    cols = {c.lower(): c for c in df.columns}
    date_col = cols.get("chart_week") or cols.get("date")
    rank_col = cols.get("current_week") or cols.get("rank")
    song_col = cols.get("title") or cols.get("song")
    artist_col = cols.get("performer") or cols.get("artist")

    df = df[df[rank_col] <= top_n]
    chunks = []
    for date, group in df.groupby(date_col):
        songs = ", ".join(
            f"#{int(r[rank_col])} {r[song_col]} by {r[artist_col]}"
            for _, r in group.sort_values(rank_col).iterrows()
        )
        text = f"Billboard Hot 100 top {top_n} this week: {songs}"
        chunks.append({"text": text, "date": str(date)[:10], "source": "billboard"})
    return chunks


def main():
    all_chunks = chunk_nyt() + chunk_wikipedia() + chunk_billboard()
    for i, c in enumerate(all_chunks):
        c["id"] = f"chunk_{i:06d}"

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    out_path = os.path.join(PROCESSED_DIR, "chunks.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    print(f"Built {len(all_chunks)} chunks -> {out_path}")


if __name__ == "__main__":
    main()
