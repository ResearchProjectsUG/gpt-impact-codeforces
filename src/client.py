import os
import requests
import utils
from config import settings
from enums import Language
from typing import Dict, Any


class CodeforcesClient:
    def __init__(self):
        self.base_url = settings.CODEFORCES_BASE_URL

    def build_url(self, resource: str) -> str:
        """Construct the full API endpoint URL."""
        return f"{self.base_url}/{resource}"

    def fetch_data(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """Generic method to fetch data from a given Codeforces API endpoint."""  # noqa
        url = self.build_url(endpoint)
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raises a HTTPError for bad responses
            return response.json()  # Assuming the API returns JSON data
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None


# ID of the Codeforces Round 943 (Div. 3)
CONTEST_ID = 1968

client = CodeforcesClient()

contest_submissions_params = {
    "contestId": CONTEST_ID,
    "asManager": False,
    "from": 1,
    "count": 10000000,
    "lang": Language.ENGLISH,
}

contest_participants_params = {
    "contestId": CONTEST_ID,
    "activeOnly": False,
    "includeRetired": False,
    "lang": Language.ENGLISH,
}

contest_standings_params = {
    "contestId": CONTEST_ID,
    "asManager": False,
    "from": 1,
    "count": 5,
    "showUnofficial": False,
}


# Process the data
json_data = client.fetch_data("contest.standings", contest_standings_params)
contest_info = json_data["result"]["contest"]
problems = json_data["result"]["problems"]

base_path = "data"
slug = utils.create_slug(contest_info["name"])
slug_folder = os.path.join(base_path, slug)

# Create directory and save data to CSV
utils.save_contest_data(slug, contest_info)
utils.save_problems_data(slug, problems)
print(f"Data has been saved in folder: {slug}")

# TODO(Manuel): Analyze this with users
# content = response.content.decode("utf-8")
