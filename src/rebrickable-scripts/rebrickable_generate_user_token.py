import requests
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import common functions from utils
from utils.common_functions import load_rebrickable_environment

api_key, user_token, username, password = load_rebrickable_environment()
payload = {"username": username,
           "password": password}
headers = {"Authorization": f"key {api_key}"}
r = requests.post("https://rebrickable.com/api/v3/users/_token/", data=payload, headers=headers)
print(r.status_code, r.text)