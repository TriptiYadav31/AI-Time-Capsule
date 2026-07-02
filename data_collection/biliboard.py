import os
import requests

# Ensure the output directory exists
os.makedirs("data/raw", exist_ok=True)

url = "https://raw.githubusercontent.com/utdata/rwd-billboard-data/main/data-out/hot-100-current.csv"
save_path = "data/raw/billboard.csv"

print("Downloading Billboard data...")
response = requests.get(url)
response.raise_for_status()

with open(save_path, "wb") as f:
    f.write(response.content)

print(f"Saved to {os.path.abspath(save_path)}")
