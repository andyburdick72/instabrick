import time
import requests
import pandas as pd
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import common functions from utils
from utils.common_functions import load_rebrickable_environment

# Load Rebrickable credentials
api_key, rebrickable_user_token, username, password = load_rebrickable_environment()

# Output CSV file
OUTPUT_CSV = Path(__file__).resolve().parent.parent / "data" / "rebrickable_user_parts_inventory.csv"

# API endpoint templates
USER_SETS_URL = "https://rebrickable.com/api/v3/users/{user_token}/sets/"
SET_PARTS_URL = "https://rebrickable.com/api/v3/lego/sets/{set_num}/parts/"

# Rate limit: adjust as needed to respect API limits
DELAY_BETWEEN_REQUESTS = 0.2  # seconds

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

def fetch_set_parts(set_num):
    """
    Fetch all parts for a specific set.
    Returns a list of part-detail dictionaries.
    """
    headers = {"Authorization": f"key {api_key}"}
    url = SET_PARTS_URL.format(set_num=set_num)
    params = {
        "page_size": 1000,
        "inc_part_details": 1,
        "inc_color_details": 1
    }
    parts = []

    while url:
        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()
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

def build_inventory_from_api():
    """
    Fetch user sets, then fetch parts for each set, and return a DataFrame.
    """
    user_sets = fetch_user_sets()
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

def export_inventory():
    """
    Generate the inventory DataFrame and write it to CSV.
    """
    df = build_inventory_from_api()
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    export_inventory()