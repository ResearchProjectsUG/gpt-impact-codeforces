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


def process_contest_data(client: CodeforcesClient, contest_id: int):
    """Process and save all relevant contest data."""
    base_path = "data"

    # Fetch contest standings
    contest_standings_params = {
        "contestId": contest_id,
        "asManager": False,
        "from": 1,
        "count": 5,
        "showUnofficial": False,
    }
    json_data = client.fetch_data(
        "contest.standings",
        contest_standings_params,
    )
    contest_info = json_data["result"]["contest"]
    problems = json_data["result"]["problems"]

    # Fetch user rated list
    user_rated_list_params = {
        "activeOnly": False,
        "includeRetired": True,
        "contestId": contest_id,
    }
    json_data = client.fetch_data("user.ratedList", user_rated_list_params)
    users = json_data["result"]

    # Fetch contest submissions
    contest_submissions_params = {
        "contestId": contest_id,
        "asManager": False,
        "from": 1,
        "count": 10000000,
        "lang": Language.ENGLISH,
    }
    json_data = client.fetch_data("contest.status", contest_submissions_params)
    submissions = json_data["result"]
    filtered_submissions = utils.filter_submissions(submissions)

    # Save data to CSV
    slug = utils.create_slug(contest_info["name"])
    slug_folder = os.path.join(base_path, slug)
    os.makedirs(slug_folder, exist_ok=True)  # Ensure the directory exists

    utils.save_contest_data(slug_folder, contest_info)
    utils.save_problems_data(slug_folder, problems)
    utils.save_user_data(slug_folder, users)
    utils.save_submissions_data(slug_folder, filtered_submissions)

    print(f"Data has been saved in folder: {slug_folder}")


# Usage
client = CodeforcesClient()
CONTEST_ID = 1968  # ID of the Codeforces Round 943 (Div. 3)
process_contest_data(client, CONTEST_ID)
