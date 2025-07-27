import argparse
import time
import random
import requests
import pandas as pd
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import common functions from utils
from utils.common_functions import load_rebrickable_environment

# Argument parser for command-line options
parser = argparse.ArgumentParser(
    description="Fetch parts via Rebrickable API for all user sets "
                "or a subset passed on the command line."
)
parser.add_argument(
    "sets", metavar="SET", nargs="*",
    help="optional list of set numbers to fetch (e.g. 21324-1 40498-1)"
)
ARGS = parser.parse_args()
CLI_SETS = set(ARGS.sets)           # empty set ⇒ fetch everything

# Load Rebrickable credentials
api_key, rebrickable_user_token, username, password = load_rebrickable_environment()

# Output CSV file
OUTPUT_CSV = Path(__file__).resolve().parents[2] / "data" / "rebrickable_user_parts_inventory.csv"

# API endpoint templates
USER_SETS_URL = "https://rebrickable.com/api/v3/users/{user_token}/sets/"
SET_PARTS_URL = "https://rebrickable.com/api/v3/lego/sets/{set_num}/parts/"

# Rate limit: adjust as needed to respect API limits
DELAY_BETWEEN_REQUESTS = 0.4  # seconds

# Function to handle GET requests with retry logic
def safe_get(url, headers, params=None, max_retries=10):
    """GET with back-off for 429 and 5xx errors."""
    attempt = 0
    while True:
        attempt += 1
        r = requests.get(url, headers=headers, params=params, timeout=60)
        if r.status_code == 200:
            return r
        if r.status_code in {429, 500, 502, 503, 504} and attempt <= max_retries:
            # Exponential back-off with jitter
            wait = min(60, (2 ** attempt) + random.uniform(0, 1))
            print(f"⏳  {r.status_code} on {url} (attempt {attempt}); waiting {wait:.1f}s")
            time.sleep(wait)
            continue
        r.raise_for_status()   # re-raise if exceeded retries or non-transient

# Fetch user sets from Rebrickable API
def fetch_user_sets():
    """
    Fetch all sets from the user's collection via Rebrickable API.
    Returns a list of dictionaries with 'set_num' and 'quantity'.
    """
    headers = {"Authorization": f"key {api_key}"}
    url = USER_SETS_URL.format(user_token=rebrickable_user_token)
    params = {"page_size": 1000}
    user_sets = []

    while url:
        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        for item in data["results"]:

            # 'set' is a nested object; pull the set_num out of it
            set_details = item.get("set", {})
            set_num = set_details.get("set_num")

            # Skip if the response is malformed
            if not set_num:
                print(f"Warning: missing set_num in item: {item}")
                continue

            user_sets.append({
            "set_num": set_num,
            "quantity": item.get("quantity", 1)
            })

        url = data.get("next")
        params = {}
        time.sleep(DELAY_BETWEEN_REQUESTS)

    return user_sets

# Fetch parts for a specific set from Rebrickable API
def fetch_set_parts(set_num):
    """
    Fetch all parts for a specific set.
    Returns a list of part-detail dictionaries.
    """
    headers = {"Authorization": f"key {api_key}"}
    url = SET_PARTS_URL.format(set_num=set_num)
    params = {
        "page_size": 500,
        "inc_part_details": 1,
        "inc_color_details": 1
    }
    parts = []

    while url:
        resp = safe_get(url, headers=headers, params=params)
        data = resp.json()

        for item in data["results"]:
            part = item["part"]
            color = item["color"]
            parts.append({
                "part_num": part["part_num"],
                "part_name": part["name"],
                "color_id": color["id"],
                "color_name": color["name"],
                "quantity": item["quantity"],
                "element_id": item.get("element_id"),
                "is_spare": item["is_spare"]
            })

        url = data.get("next")
        params = {}
        time.sleep(DELAY_BETWEEN_REQUESTS)

    return parts

# Build the inventory DataFrame from user sets and their parts
def build_inventory_from_api():
    """
    Fetch user sets, then fetch parts for each set, and return a DataFrame.
    """
    user_sets = fetch_user_sets()
    if CLI_SETS:
        user_sets = [s for s in user_sets if s["set_num"] in CLI_SETS]
    
    all_parts = []
    for set_record in user_sets:
        set_num = set_record["set_num"]
        owned_qty = set_record.get("quantity", 1)
        print(f"Fetching parts for set {set_num} (owned {owned_qty}) …")
        try:
            parts = fetch_set_parts(set_num)
            for part in parts:
                part["set_num"] = set_num
                part["quantity_owned"] = part["quantity"] * owned_qty
            all_parts.extend(parts)
        except Exception as exc:
            print(f"Failed to fetch parts for {set_num}: {exc}")

    return pd.DataFrame(all_parts)

# Export the inventory DataFrame to a CSV file
def export_inventory():
    """
    Generate the inventory DataFrame and write it to CSV.
    """
    df = build_inventory_from_api()
    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    write_header = not OUTPUT_CSV.exists()
    df.to_csv(OUTPUT_CSV, mode="a", header=write_header, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_CSV}")

# Main entry point
if __name__ == "__main__":
    export_inventory()