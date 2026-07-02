import sys
import os
import time
import subprocess

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
WAIT_SECONDS = 15  # pause between requests so we don't get rate-limited


def already_fetched(year, month, prefix):
    path = os.path.join(RAW_DIR, f"{prefix}_{year}_{month:02d}.json")
    return os.path.exists(path)


def run_script(script_name, year, month):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    result = subprocess.run(
        [sys.executable, script_path, str(year), str(month)],
        capture_output=True, text=True
    )
    return result.returncode == 0, result.stdout, result.stderr


def main():
    if len(sys.argv) != 5:
        print("Usage: python fetch_many_months.py <start_year> <start_month> <end_year> <end_month>")
        print("Example: python fetch_many_months.py 2015 1 2026 6")
        sys.exit(1)

    start_year, start_month, end_year, end_month = map(int, sys.argv[1:])

    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        print(f"\n=== {year}-{month:02d} ===")

        # NYT
        if already_fetched(year, month, "nyt"):
            print("  NYT: already have it, skipping")
        else:
            ok, out, err = run_script("fetch_nyt_news.py", year, month)
            print(f"  NYT: {'OK' if ok else 'FAILED'}")
            if not ok:
                print(f"    error: {err.strip()[-300:]}")
            time.sleep(WAIT_SECONDS)

        # Wikipedia
        if already_fetched(year, month, "wiki"):
            print("  Wikipedia: already have it, skipping")
        else:
            ok, out, err = run_script("fetch_wikipedia_events.py", year, month)
            print(f"  Wikipedia: {'OK' if ok else 'FAILED'}")
            if not ok:
                print(f"    error: {err.strip()[-300:]}")
            time.sleep(3)  # Wikipedia is more lenient, shorter wait is fine

        # move to next month
        month += 1
        if month > 12:
            month = 1
            year += 1

    print("\nDone! Run chunk_and_tag.py and build_vector_db.py next.")


if __name__ == "__main__":
    main()
